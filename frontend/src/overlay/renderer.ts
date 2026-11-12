import type { Netlist, Solution, Component, OCRText } from "../types";
import { drawTextEvidence, textAt } from "./text-evidence";
import { fitView } from "./view";
import { drawFlow, readFlow, smoothReference, flowing } from "./flow";
import {
  drawTraceIssues,
  type TraceIssue,
  type GhostPart,
} from "../ui/trace-issues";
import { format, t } from "../i18n";
import { placeBadge, placePartBadge, type Rect } from "./labels";
import { supported } from "../solver/mna";
export const imageToCanvas = (
  p: number[],
  width: number,
  imageWidth: number,
): [number, number] => [
  (p[0] * width) / imageWidth,
  (p[1] * width) / imageWidth,
];
export const canvasToImage = (
  p: number[],
  width: number,
  imageWidth: number,
): [number, number] => [
  (p[0] * imageWidth) / width,
  (p[1] * imageWidth) / width,
];
export class Renderer {
  image = new Image();
  imageReady = false;
  flow = readFlow();
  phase = 0;
  last = 0;
  selected = "";
  electron = false;
  paused = false;
  showImage = true;
  edit = false;
  texts: OCRText[] = [];
  showText = false;
  issues: TraceIssue[] = [];
  ghosts: GhostPart[] = [];
  highlightedIssue = "";
  selectedWire = "";
  compareNet?: Netlist;
  preview?: {
    line?: [number, number][];
    box?: [number, number, number, number];
    snap?: [number, number];
  };
  zoom = 1;
  labelMode: "compact" | "full" | "off" = "compact";
  currentReference: number | null = null;
  offsets = new Map<string, number>();
  reduced = matchMedia("(prefers-reduced-motion: reduce)").matches;
  constructor(public canvas: HTMLCanvasElement) {
    matchMedia("(prefers-reduced-motion: reduce)").addEventListener(
      "change",
      (e) => (this.reduced = e.matches),
    );
  }
  setImage(url: string) {
    this.imageReady = false;
    this.canvas.dataset.imageReady = "false";
    this.currentReference = null;
    this.offsets.clear();
    this.issues = [];
    this.ghosts = [];
    this.highlightedIssue = "";
    this.selectedWire = "";
    this.preview = undefined;
    this.compareNet = undefined;
    this.zoom = 1;
    const shell = this.canvas.parentElement;
    if (shell) shell.style.width = "100%";
    this.image.onload = () => {
      this.imageReady = true;
      this.canvas.dataset.imageReady = "true";
    };
    this.image.onerror = () => {
      this.imageReady = false;
      this.canvas.dataset.imageReady = "false";
    };
    this.image.src = url;
  }
  hit(x: number, y: number, net: Netlist): Component | undefined {
    return [...net.components]
      .reverse()
      .find(
        (c) =>
          x >= c.bbox[0] - 8 &&
          x <= c.bbox[2] + 8 &&
          y >= c.bbox[1] - 15 &&
          y <= c.bbox[3] + 8,
      );
  }
  view(net: Netlist) {
    const mobile = innerWidth < 768;
    const base = fitView(
      this.canvas.clientWidth / this.zoom,
      net.image.width,
      net.image.height,
      mobile ? 420 : 400,
      Math.max(
        mobile ? 420 : 400,
        Math.min(
          mobile ? 620 : 720,
          innerHeight * (innerWidth < 900 ? 0.68 : 0.76),
        ),
      ),
    );
    return {
      ...base,
      width: base.width * this.zoom,
      height: base.height * this.zoom,
      scale: base.scale * this.zoom,
      x: base.x * this.zoom,
      y: base.y * this.zoom,
    };
  }
  clientToImage(x: number, y: number, net: Netlist): [number, number] {
    const rect = this.canvas.getBoundingClientRect(),
      view = this.view(net);
    return [
      (x - rect.left - view.x) / view.scale,
      (y - rect.top - view.y) / view.scale,
    ];
  }
  imageToScreen(xy: number[], net: Netlist): [number, number] {
    const rect = this.canvas.getBoundingClientRect(),
      view = this.view(net);
    return [
      rect.left + view.x + xy[0] * view.scale,
      rect.top + view.y + xy[1] * view.scale,
    ];
  }
  render(net: Netlist, solution: Solution, now: number) {
    const elapsed = this.last ? Math.min(0.1, (now - this.last) / 1000) : 0;
    if (!this.paused) this.phase += elapsed;
    this.last = now;
    const canvas = this.canvas,
      dpr = Math.min(devicePixelRatio || 1, 2),
      width = canvas.clientWidth,
      view = this.view(net),
      height = view.height;
    if (
      canvas.width !== Math.round(width * dpr) ||
      canvas.height !== Math.round(height * dpr)
    ) {
      canvas.width = Math.round(width * dpr);
      canvas.height = Math.round(height * dpr);
      canvas.style.height = height + "px";
    }
    const ctx = canvas.getContext("2d")!,
      scale = view.scale;
    Object.assign(canvas.dataset, {
      viewScale: String(scale),
      viewX: String(view.x),
      viewY: String(view.y),
      viewWidth: String(width),
    });
    ctx.setTransform(1, 0, 0, 1, 0, 0);
    ctx.clearRect(0, 0, canvas.width, canvas.height);
    ctx.fillStyle = "#fff";
    ctx.fillRect(0, 0, canvas.width, canvas.height);
    ctx.setTransform(
      dpr * scale,
      0,
      0,
      dpr * scale,
      dpr * view.x,
      dpr * view.y,
    );
    if (this.imageReady && this.showImage) {
      ctx.globalAlpha = 0.82;
      ctx.drawImage(this.image, 0, 0, net.image.width, net.image.height);
      ctx.globalAlpha = 1;
    }
    this.currentReference = smoothReference(
      this.currentReference,
      Object.values(solution.segment_currents),
      elapsed,
    );
    const hi = Math.max(1, ...Object.values(solution.node_voltages)),
      lo = Math.min(0, ...Object.values(solution.node_voltages));
    const count = drawFlow(ctx, net, solution, {
      scale,
      zoom: this.zoom,
      elapsed,
      now,
      reference: this.currentReference,
      settings: this.flow,
      offsets: this.offsets,
      paused: this.paused,
      reduced: this.reduced,
      electron: this.electron,
      editing: this.edit,
      dark: document.documentElement.dataset.theme === "dark",
    });
    const hasCurrent = Object.values(solution.segment_currents).some(flowing);
    canvas.dataset.flowParticles = String(count);
    canvas.dataset.flowState = hasCurrent ? "flowing" : "no-current";
    canvas.dataset.flowReference = String(this.currentReference);
    const flowState = document.querySelector<HTMLElement>(
      "[data-testid=flow-state]",
    );
    if (flowState) {
      const key = hasCurrent ? "flow.active" : "flow.zero";
      if (flowState.dataset.i18n !== key || flowState.textContent !== t(key)) {
        flowState.dataset.i18n = key;
        flowState.textContent = t(key);
      }
    }
    ctx.globalAlpha = 1;
    const fontSize = Math.max(10, 11 / scale);
    for (const warning of net.warnings) {
      if (warning.ref?.startsWith("xy:")) {
        const [x, y] = warning.ref.slice(3).split(",").map(Number);
        ctx.strokeStyle = "#c15b00";
        ctx.lineWidth = 2 / scale;
        ctx.beginPath();
        ctx.arc(x, y, 9 / scale, 0, Math.PI * 2);
        ctx.stroke();
      }
    }
    ctx.font = `500 ${fontSize}px 'Noto Sans Bengali', sans-serif`;
    const occupied: Rect[] = net.components.map((c) => [
      c.bbox[0] - 3,
      c.bbox[1] - 3,
      c.bbox[2] + 3,
      c.bbox[3] + 3,
    ]);
    occupied.push(...this.texts.map((item) => item.bbox as Rect));
    // Printed values in the bundled example have no OCR evidence: protect the
    // usual above-body label zone too, rather than hiding them with readings.
    for (const c of net.components) {
      const [x, y, r, b] = c.bbox;
      occupied.push(
        r - x >= b - y ? [x - 8, y - 25, r + 8, y] : [r, y - 5, r + 70, b + 5],
      );
    }
    for (const s of net.wire_graph.segments)
      for (let k = 1; k < s.polyline.length; k++) {
        const a = s.polyline[k - 1],
          b = s.polyline[k];
        occupied.push([
          Math.min(a[0], b[0]) - 2,
          Math.min(a[1], b[1]) - 2,
          Math.max(a[0], b[0]) + 2,
          Math.max(a[1], b[1]) + 2,
        ]);
      }
    for (const c of net.components) {
      const [x1, y1, x2, y2] = c.bbox,
        reading = solution.components[c.id],
        selected = c.id === this.selected,
        bypass = solution.short_circuit.bypassed.includes(c.id);
      if (bypass || c.disabled) {
        ctx.fillStyle = "#ffffffb0";
        ctx.fillRect(x1 - 3, y1 - 3, x2 - x1 + 6, y2 - y1 + 6);
      }
      const uncertain = c.confidence < 0.65 || c.value.confidence < 0.65;
      if (!supported.has(c.type)) {
        ctx.fillStyle = "#fff1cc";
        ctx.fillRect(x1 - 4, y1 - 4, x2 - x1 + 8, y2 - y1 + 8);
        ctx.save();
        ctx.setLineDash([5, 3]);
        ctx.strokeStyle = "#9b391b";
        ctx.lineWidth = 2 / scale;
        ctx.strokeRect(x1 - 4, y1 - 4, x2 - x1 + 8, y2 - y1 + 8);
        ctx.restore();
        ctx.fillStyle = "#672309";
        ctx.fillText(t("ui.unknown_short"), x1 + 2, (y1 + y2) / 2);
      }
      ctx.save();
      ctx.setLineDash(uncertain ? [4, 4] : []);
      ctx.strokeStyle = selected
        ? "#e15c30"
        : uncertain
          ? "#b48b32"
          : "#7d9e9633";
      ctx.lineWidth = selected ? 2 / scale : 1 / scale;
      ctx.strokeRect(x1 - 3, y1 - 3, x2 - x1 + 6, y2 - y1 + 6);
      ctx.restore();
      if (
        supported.has(c.type) &&
        (!this.imageReady ||
          c.virtual ||
          (c.value.status === "user" && this.edit))
      ) {
        this.symbol(ctx, c);
      }
      if (this.labelMode !== "off") {
        const current = !supported.has(c.type)
          ? t("ui.unknown_short")
          : reading
            ? format(reading.current, "A")
            : "—";
        let text = `${c.label || c.id}${uncertain ? " ?" : ""} · ${current}`;
        if (this.labelMode === "full" && reading)
          text += ` · ${format(reading.v_drop, "V")} · ${format(reading.power, "W")}`;
        const placement = placePartBadge(
          c.bbox,
          [
            [ctx.measureText(text).width + 12, fontSize + 8],
            [ctx.measureText(current).width + 12, fontSize + 8],
          ],
          occupied,
          net.image.width,
          net.image.height,
        );
        if (placement.compact) text = current;
        const textWidth = ctx.measureText(text).width + 12,
          placed = placement.rect;
        occupied.push(placed);
        const bx = placed[0],
          by = placed[1] + fontSize + 3;
        ctx.fillStyle = selected
          ? "#203e3b"
          : c.value.status === "assumed"
            ? "#fff3d4"
            : c.value.status === "solved"
              ? "#def1e5"
              : "#f0f5f3";
        ctx.beginPath();
        ctx.roundRect(bx, by - fontSize - 3, textWidth, fontSize + 8, 4);
        ctx.fill();
        ctx.fillStyle = selected
          ? "white"
          : c.value.status === "assumed"
            ? "#775f26"
            : "#23433d";
        ctx.fillText(text, bx + 6, by);
      }
      if (c.type === "capacitor" && reading) {
        const ratio = Math.min(
          1,
          Math.abs(reading.v_drop) / Math.max(1, hi - lo),
        );
        ctx.fillStyle = "#318b89";
        ctx.fillRect(x1, y2 + 4, (x2 - x1) * ratio, 3);
      }
      if (c.type === "switch") {
        const [a, b] = c.terminals.map((t) => t.xy);
        ctx.strokeStyle = "#e15c30";
        ctx.lineWidth = 2 / scale;
        ctx.beginPath();
        ctx.moveTo(...a);
        ctx.lineTo(b[0], c.switch_closed ? b[1] : b[1] - 12);
        ctx.stroke();
      }
      if (this.edit) {
        ctx.fillStyle = "#d45f30";
        for (const terminal of c.terminals) {
          ctx.beginPath();
          ctx.arc(...terminal.xy, 3 / scale, 0, Math.PI * 2);
          ctx.fill();
        }
      }
    }
    const shown = new Set<string>();
    for (const p of net.wire_graph.points.filter(
      (p) => p.kind === "junction",
    )) {
      if (this.labelMode === "off") break;
      if (shown.has(p.node)) continue;
      shown.add(p.node);
      ctx.beginPath();
      ctx.arc(...p.xy, 3, 0, Math.PI * 2);
      ctx.fillStyle = "#214c4a";
      ctx.fill();
      const label = `${net.nodes.find((n) => n.id === p.node)?.label || p.node}: ${format(solution.node_voltages[p.node] || 0, "V")}`;
      ctx.fillStyle = "#fff";
      const w = ctx.measureText(label).width;
      let tx = Math.max(2, Math.min(net.image.width - w - 6, p.xy[0] + 5)),
        ty =
          p.xy[1] + fontSize + 10 > net.image.height
            ? p.xy[1] - fontSize - 8
            : p.xy[1] + 4;
      const placed = placeBadge(
        [tx, ty, tx + w + 5, ty + fontSize + 5],
        [1, 0],
        occupied,
        net.image.width,
        net.image.height,
      );
      occupied.push(placed);
      tx = placed[0];
      ty = placed[1];
      ctx.fillRect(tx, ty, w + 5, fontSize + 5);
      ctx.fillStyle = "#425950";
      ctx.fillText(label, tx + 2, ty + fontSize);
    }
    if (this.showText) drawTextEvidence(ctx, net, this.texts, scale);
    drawTraceIssues(
      ctx,
      this.issues,
      scale,
      this.highlightedIssue,
      this.reduced ? 0 : now / 1000,
    );
    if (this.compareNet) {
      ctx.save();
      ctx.globalAlpha = 0.3;
      ctx.strokeStyle = "#763DD5";
      ctx.lineWidth = 3 / scale;
      for (const segment of this.compareNet.wire_graph.segments) {
        ctx.beginPath();
        ctx.moveTo(...segment.polyline[0]);
        for (const p of segment.polyline.slice(1)) ctx.lineTo(...p);
        ctx.stroke();
      }
      for (const c of this.compareNet.components)
        ctx.strokeRect(
          c.bbox[0],
          c.bbox[1],
          c.bbox[2] - c.bbox[0],
          c.bbox[3] - c.bbox[1],
        );
      ctx.restore();
    }
    const selectedWire = net.wire_graph.segments.find(
      (s) => s.id === this.selectedWire,
    );
    ctx.save();
    ctx.strokeStyle = "#00689D";
    ctx.lineWidth = 3 / scale;
    if (selectedWire) {
      ctx.beginPath();
      ctx.moveTo(...selectedWire.polyline[0]);
      for (const p of selectedWire.polyline.slice(1)) ctx.lineTo(...p);
      ctx.stroke();
    }
    if (this.preview) {
      ctx.setLineDash([6 / scale, 4 / scale]);
      if (this.preview.line) {
        ctx.beginPath();
        ctx.moveTo(...this.preview.line[0]);
        for (const p of this.preview.line.slice(1)) ctx.lineTo(...p);
        ctx.stroke();
      }
      if (this.preview.box) {
        const [x, y, right, bottom] = this.preview.box;
        ctx.strokeRect(x, y, right - x, bottom - y);
      }
      if (this.preview.snap) {
        ctx.setLineDash([]);
        ctx.beginPath();
        ctx.arc(...this.preview.snap, 12 / scale, 0, Math.PI * 2);
        ctx.stroke();
      }
    }
    ctx.restore();
  }
  textHit(x: number, y: number) {
    return this.showText ? textAt(this.texts, x, y) : undefined;
  }
  symbol(ctx: CanvasRenderingContext2D, c: Component) {
    const [a, b] = c.terminals.map((t) => t.xy),
      mx = (a[0] + b[0]) / 2,
      my = (a[1] + b[1]) / 2;
    ctx.save();
    ctx.translate(mx, my);
    ctx.rotate(Math.atan2(b[1] - a[1], b[0] - a[0]));
    const length = Math.hypot(b[0] - a[0], b[1] - a[1]);
    ctx.strokeStyle = c.virtual ? "#e15c30" : "#31534f";
    ctx.fillStyle = "#fff";
    ctx.lineWidth = 2;
    ctx.beginPath();
    if (c.type === "capacitor") {
      ctx.moveTo(-length / 2, 0);
      ctx.lineTo(-4, 0);
      ctx.moveTo(-4, -12);
      ctx.lineTo(-4, 12);
      ctx.moveTo(4, -12);
      ctx.lineTo(4, 12);
      ctx.moveTo(4, 0);
      ctx.lineTo(length / 2, 0);
    } else if (
      ["dc_source", "battery", "ac_source", "current_source"].includes(c.type)
    ) {
      ctx.arc(0, 0, Math.max(10, length / 2), 0, Math.PI * 2);
      ctx.fill();
      ctx.fillStyle = "#31534f";
      ctx.fillText("+", -8, 4);
      ctx.fillText("−", 3, 4);
    } else {
      ctx.moveTo(-length / 2, 0);
      for (let i = 1; i < 9; i++)
        ctx.lineTo(-length / 2 + (length * i) / 9, i % 2 ? 7 : -7);
      ctx.lineTo(length / 2, 0);
    }
    ctx.stroke();
    ctx.restore();
  }
  export() {
    const a = document.createElement("a");
    a.download = "circuit-overlay.png";
    a.href = this.canvas.toDataURL("image/png");
    a.click();
  }
}
