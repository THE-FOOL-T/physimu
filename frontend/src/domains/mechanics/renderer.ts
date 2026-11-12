import { canvasDpr } from "../../shell";
import type {
  Scene,
  Params,
  Drawables,
  Point,
  State,
  Trajectory,
  Body,
} from "./types";
import { archetypes } from "./archetypes";
import { read, RAD } from "./archetypes/common";
import { valueAt } from "./validate";

export const FRAME0_LIMITS = {
  meanAbsolute: 2,
  fractionOver16: 0.005,
  anchorErrorPx: 1,
};
export interface Frame0Report {
  mean_absolute_channel: number | null;
  fraction_over_16: number | null;
  max_anchor_error_px: number | null;
  passed: boolean;
}
export interface RenderOptions {
  forces: boolean;
  components: boolean;
  trail: boolean;
  original: boolean;
  marker: boolean;
  handles: boolean;
}
interface Sprite {
  canvas: HTMLCanvasElement;
  x: number;
  y: number;
}
function canvas(w: number, h: number) {
  const c = document.createElement("canvas");
  c.width = Math.ceil(w);
  c.height = Math.ceil(h);
  return c;
}
function path(ctx: CanvasRenderingContext2D, points: Point[]) {
  ctx.beginPath();
  points.forEach((p, i) => (i ? ctx.lineTo(...p) : ctx.moveTo(...p)));
}
function line(
  ctx: CanvasRenderingContext2D,
  points: Point[],
  color: string,
  width: number,
) {
  if (points.length < 2) return;
  ctx.strokeStyle = color;
  ctx.lineWidth = width;
  ctx.lineCap = "round";
  ctx.lineJoin = "round";
  path(ctx, points);
  ctx.stroke();
}
function hatched(
  ctx: CanvasRenderingContext2D,
  points: Point[],
  color: string,
  width: number,
) {
  line(ctx, points, color, width);
  const a = points[0],
    b = points.at(-1)!,
    len = Math.hypot(b[0] - a[0], b[1] - a[1]);
  const ux = (b[0] - a[0]) / len,
    uy = (b[1] - a[1]) / len;
  for (let d = 12; d < len; d += 15)
    line(
      ctx,
      [
        [a[0] + ux * d - uy * 3, a[1] + uy * d + ux * 3],
        [a[0] + ux * d - uy * 11 - ux * 7, a[1] + uy * d + ux * 11 - uy * 7],
      ],
      color,
      1,
    );
}
function arrow(
  ctx: CanvasRenderingContext2D,
  a: Point,
  b: Point,
  color: string,
  label?: string,
  dashed = false,
) {
  ctx.setLineDash(dashed ? [5, 3] : []);
  line(ctx, [a, b], color, 2);
  ctx.setLineDash([]);
  const angle = Math.atan2(b[1] - a[1], b[0] - a[0]);
  ctx.fillStyle = color;
  path(ctx, [
    b,
    [b[0] - 10 * Math.cos(angle - 0.45), b[1] - 10 * Math.sin(angle - 0.45)],
    [b[0] - 10 * Math.cos(angle + 0.45), b[1] - 10 * Math.sin(angle + 0.45)],
  ]);
  ctx.closePath();
  ctx.fill();
  if (label) {
    ctx.font = "bold 14px sans-serif";
    ctx.lineWidth = 4;
    ctx.strokeStyle = "#fffef7";
    ctx.strokeText(label, b[0] + 4, b[1] - 4);
    ctx.fillText(label, b[0] + 4, b[1] - 4);
  }
}
function maskPoints(body: Body): Point[] {
  return body.mask.map((p) => {
    const dx = p[0] - body.anchor[0],
      dy = p[1] - body.anchor[1],
      r = Math.hypot(dx, dy) || 1;
    return [p[0] + (4 * dx) / r, p[1] + (4 * dy) / r];
  });
}
function bounds(
  points: Point[],
  padding = 0,
): [number, number, number, number] {
  return [
    Math.floor(Math.min(...points.map((p) => p[0])) - padding),
    Math.floor(Math.min(...points.map((p) => p[1])) - padding),
    Math.ceil(Math.max(...points.map((p) => p[0])) + padding),
    Math.ceil(Math.max(...points.map((p) => p[1])) + padding),
  ];
}
/** All lifted layers are cut from source pixels; no model, API, or image synthesis. */
export class MechanicsRenderer {
  background: HTMLCanvasElement;
  frame0: Frame0Report = {
    mean_absolute_channel: null,
    fraction_over_16: null,
    max_anchor_error_px: null,
    passed: false,
  };
  degraded = false;
  warnings: string[] = [];
  confidence = 1;
  padding = { left: 32, top: 32, right: 32, bottom: 32 };
  dpr = canvasDpr(globalThis.devicePixelRatio);
  private bodySprites = new Map<string, Sprite>();
  private labelSprites = new Map<string, Sprite>();
  private pulleySprites = new Map<string, Sprite>();
  private springSprites = new Map<string, HTMLCanvasElement>();
  private predictedPaths = new Map<string, Point[]>();
  private source: HTMLCanvasElement;
  constructor(
    readonly scene: Scene,
    readonly image: HTMLImageElement,
  ) {
    this.source = canvas(scene.image.width, scene.image.height);
    this.source.getContext("2d")!.drawImage(image, 0, 0);
    this.background = canvas(scene.image.width, scene.image.height);
    this.buildLayers();
  }
  static async load(scene: Scene, url: string) {
    const img = new Image();
    img.src = url;
    await img.decode();
    if (
      img.naturalWidth !== scene.image.width ||
      img.naturalHeight !== scene.image.height
    )
      throw new Error("Source dimensions differ from scene");
    return new MechanicsRenderer(scene, img);
  }
  private cut(points: Point[]): Sprite {
    const [x, y, x1, y1] = bounds(points, 2),
      result = canvas(x1 - x, y1 - y),
      ctx = result.getContext("2d")!;
    ctx.translate(-x, -y);
    path(ctx, points);
    ctx.closePath();
    ctx.clip();
    ctx.drawImage(this.source, 0, 0);
    return { canvas: result, x, y };
  }
  private buildLayers() {
    const s = this.scene,
      ctx = this.background.getContext("2d")!;
    ctx.drawImage(this.source, 0, 0);
    ctx.fillStyle = s.frame.paper_color;
    for (const b of s.bodies) {
      const points = maskPoints(b);
      this.bodySprites.set(b.id, this.cut(points));
      path(ctx, points);
      ctx.closePath();
      ctx.fill();
    }
    for (const b of s.bodies)
      for (const id of b.label_ids) {
        const a = s.annotations.find((a) => a.id === id),
          box = a?.geometry.bbox;
        if (!box) continue;
        // Interior labels already belong to the mask sprite.
        if (
          box[0] >= b.bbox[0] &&
          box[1] >= b.bbox[1] &&
          box[2] <= b.bbox[2] &&
          box[3] <= b.bbox[3]
        )
          continue;
        const [x, y, x1, y1] = box,
          points: Point[] = [
            [x - 2, y - 2],
            [x1 + 2, y - 2],
            [x1 + 2, y1 + 2],
            [x - 2, y1 + 2],
          ];
        this.labelSprites.set(id, this.cut(points));
        ctx.fillRect(x - 2, y - 2, x1 - x + 4, y1 - y + 4);
      }
    for (const link of s.links) {
      line(
        ctx,
        link.polyline,
        s.frame.paper_color,
        link.type === "spring" ? 30 : s.frame.stroke_px + 6,
      );
      if (link.type === "spring") {
        const a = link.a.point,
          b = link.b.point,
          len = Math.hypot(b[0] - a[0], b[1] - a[1]);
        const sprite = canvas(len, 28),
          c = sprite.getContext("2d")!;
        c.translate(0, 14);
        c.rotate(-Math.atan2(b[1] - a[1], b[0] - a[0]));
        c.drawImage(this.source, -a[0], -a[1]);
        this.springSprites.set(link.id, sprite);
      }
    }
    for (const pulley of s.pulleys) {
      const [x, y] = pulley.center,
        r = pulley.radius_px + 3,
        points: Point[] = Array.from({ length: 128 }, (_, i) => [
          x + r * Math.cos((i * Math.PI) / 64),
          y + r * Math.sin((i * Math.PI) / 64),
        ]);
      this.pulleySprites.set(pulley.id, this.cut(points));
      ctx.beginPath();
      ctx.arc(x, y, r, 0, 2 * Math.PI);
      ctx.fillStyle = s.frame.paper_color;
      ctx.fill();
    }
    for (const a of s.annotations.filter((a) => a.id === "launch")) {
      const [x, y, x1, y1] = bounds(a.geometry.points, 12);
      ctx.fillStyle = s.frame.paper_color;
      ctx.fillRect(x, y, x1 - x, y1 - y);
    }
    for (const repair of s.repairs)
      for (const segment of repair.segments)
        line(ctx, segment, s.frame.ink_color, s.frame.stroke_px);
  }
  backgroundHash(params: Params = {}, st?: State) {
    let background = this.background;
    if (st) {
      background = canvas(this.scene.image.width, this.scene.image.height);
      this.staticBackground(
        background.getContext("2d")!,
        params,
        archetypes[this.scene.archetype].layout(this.scene, params, st),
      );
    }
    const data = background
      .getContext("2d")!
      .getImageData(0, 0, background.width, background.height).data;
    let h = 2166136261;
    for (const value of data) h = Math.imul(h ^ value, 16777619);
    return (h >>> 0).toString(16);
  }
  private staticBackground(
    ctx: CanvasRenderingContext2D,
    params: Params,
    draw: Drawables,
  ) {
    const s = this.scene;
    ctx.drawImage(this.background, 0, 0);
    // Only an unlocked geometry change can replace static source strokes.
    const changed = s.bindings.filter(
      (b) =>
        b.class === "geometry" &&
        b.path in params &&
        params[b.path] !== valueAt(s, b.path).number,
    );
    if (!changed.length) return;
    const edited = s.surfaces.filter(
      (surface) =>
        JSON.stringify(surface.polyline) !==
        JSON.stringify(draw.surfaces.find((v) => v.id === surface.id)!.points),
    );
    for (const surface of edited)
      line(ctx, surface.polyline, s.frame.paper_color, 28);
    for (const surface of edited) {
      const target = draw.surfaces.find((v) => v.id === surface.id)!;
      hatched(ctx, target.points, s.frame.ink_color, s.frame.stroke_px);
      // Repair intersections cleared with the old surface, within that affected area.
      const [x, y, x1, y1] = bounds(surface.polyline, 16);
      ctx.save();
      ctx.beginPath();
      ctx.rect(x, y, x1 - x, y1 - y);
      ctx.clip();
      for (const other of draw.surfaces.filter(
        (v) => !edited.some((e) => e.id === v.id),
      ))
        hatched(ctx, other.points, s.frame.ink_color, s.frame.stroke_px);
      ctx.restore();
    }
    for (const a of s.annotations.filter(
      (a) => a.type === "angle_arc" && a.geometry.bbox,
    )) {
      const b = a.geometry.bbox!;
      ctx.fillStyle = s.frame.paper_color;
      ctx.fillRect(b[0] - 3, b[1] - 3, b[2] - b[0] + 6, b[3] - b[1] + 6);
      ctx.save();
      ctx.beginPath();
      ctx.rect(b[0] - 3, b[1] - 3, b[2] - b[0] + 6, b[3] - b[1] + 6);
      ctx.clip();
      for (const surface of draw.surfaces)
        hatched(ctx, surface.points, s.frame.ink_color, s.frame.stroke_px);
      ctx.restore();
      const sf = s.surfaces.find((v) => v.type === "incline");
      if (!sf) continue;
      ctx.beginPath();
      ctx.arc(
        (b[0] + b[2]) / 2,
        (b[1] + b[3]) / 2,
        (b[2] - b[0]) / 2,
        -read(s, params, `surfaces.${sf.id}.angle_deg`) * RAD,
        0,
      );
      ctx.strokeStyle = s.frame.ink_color;
      ctx.lineWidth = s.frame.stroke_px;
      ctx.stroke();
    }
  }
  private moving(
    ctx: CanvasRenderingContext2D,
    draw: Drawables,
    params: Params,
  ) {
    ctx.save(); // Live label typography must not leak into overlays or later frames.
    const s = this.scene;
    for (const l of draw.links) {
      const source = s.links.find((v) => v.id === l.id)!;
      if (source.type === "spring") {
        const sprite = this.springSprites.get(l.id)!,
          a = l.points[0],
          b = l.points.at(-1)!,
          length = Math.hypot(b[0] - a[0], b[1] - a[1]);
        const lead = 12,
          coil = Math.max(1, sprite.width - 2 * lead),
          target = Math.max(1, length - 2 * lead);
        ctx.save();
        ctx.translate(...a);
        ctx.rotate(Math.atan2(b[1] - a[1], b[0] - a[0]));
        ctx.drawImage(sprite, 0, 0, lead, 28, 0, -14, lead, 28);
        ctx.drawImage(sprite, lead, 0, coil, 28, lead, -14, target, 28);
        ctx.drawImage(
          sprite,
          sprite.width - lead,
          0,
          lead,
          28,
          length - lead,
          -14,
          lead,
          28,
        );
        ctx.restore();
      } else line(ctx, l.points, s.frame.ink_color, s.frame.stroke_px);
    }
    for (const pulley of draw.pulleys) {
      const source = s.pulleys.find((v) => v.id === pulley.id)!,
        sprite = this.pulleySprites.get(pulley.id)!;
      ctx.save();
      ctx.translate(...pulley.center);
      ctx.rotate(pulley.rotation);
      ctx.drawImage(
        sprite.canvas,
        sprite.x - source.center[0],
        sprite.y - source.center[1],
      );
      ctx.restore();
    }
    const launch = s.annotations.find((a) => a.id === "launch");
    if (launch) {
      const source = s.bodies[0],
        h = read(s, params, "params.launch_height"),
        sourceH = read(s, {}, "params.launch_height"),
        S = s.frame.px_per_m.number!;
      const anchor: Point = [
          source.anchor[0],
          source.anchor[1] - (h - sourceH) * S,
        ],
        a = read(s, params, "params.launch_angle") * RAD,
        v = read(s, params, "params.launch_speed");
      arrow(
        ctx,
        anchor,
        [anchor[0] + 2.5 * v * Math.cos(a), anchor[1] - 2.5 * v * Math.sin(a)],
        s.frame.ink_color,
      );
    }
    for (const b of draw.bodies) {
      const source = s.bodies.find((v) => v.id === b.id)!,
        sprite = this.bodySprites.get(b.id)!;
      ctx.save();
      ctx.translate(...b.anchor);
      ctx.rotate(b.rotation);
      ctx.drawImage(
        sprite.canvas,
        sprite.x - source.anchor[0],
        sprite.y - source.anchor[1],
      );
      for (const id of source.label_ids) {
        const label = this.labelSprites.get(id);
        if (label)
          ctx.drawImage(
            label.canvas,
            label.x - source.anchor[0],
            label.y - source.anchor[1],
          );
      }
      for (const binding of s.bindings.filter((binding) =>
        binding.labels.some((id) => source.label_ids.includes(id)),
      )) {
        if (
          !(binding.path in params) ||
          params[binding.path] === valueAt(s, binding.path).number
        )
          continue;
        for (const id of binding.labels) {
          const box = s.annotations.find((a) => a.id === id)?.geometry.bbox;
          if (!box) continue;
          ctx.fillStyle = s.frame.paper_color;
          ctx.fillRect(
            box[0] - source.anchor[0] - 1,
            box[1] - source.anchor[1] - 1,
            box[2] - box[0] + 2,
            box[3] - box[1] + 2,
          );
          ctx.fillStyle = s.frame.ink_color;
          ctx.font = "16px sans-serif";
          ctx.textBaseline = "top";
          ctx.fillText(
            `${params[binding.path].toFixed(1)} ${binding.control.unit}`,
            box[0] - source.anchor[0],
            box[1] - source.anchor[1],
          );
        }
      }
      ctx.restore();
    }
    // Bound labels outside body masks follow the same Value overrides.
    for (const binding of s.bindings.filter(
      (b) => b.path in params && params[b.path] !== valueAt(s, b.path).number,
    ))
      for (const id of binding.labels) {
        if (s.bodies.some((b) => b.label_ids.includes(id))) continue;
        const a = s.annotations.find((a) => a.id === id),
          box = a?.geometry.bbox;
        if (!box) continue;
        ctx.fillStyle = s.frame.paper_color;
        ctx.fillRect(
          ...([
            box[0] - 2,
            box[1] - 2,
            box[2] - box[0] + 4,
            box[3] - box[1] + 4,
          ] as [number, number, number, number]),
        );
        ctx.fillStyle = s.frame.ink_color;
        ctx.font = "16px sans-serif";
        ctx.textBaseline = "top";
        ctx.fillText(
          `${params[binding.path]} ${binding.control.unit}`,
          box[0],
          box[1],
        );
      }
    ctx.restore();
  }
  showSource(target: HTMLCanvasElement) {
    const s = this.scene,
      w = s.image.width + 64,
      h = s.image.height + 64;
    target.width = w * this.dpr;
    target.height = h * this.dpr;
    target.style.width = `${w}px`;
    target.style.height = `${h}px`;
    const ctx = target.getContext("2d")!;
    ctx.scale(this.dpr, this.dpr);
    ctx.fillStyle = s.frame.paper_color;
    ctx.fillRect(0, 0, w, h);
    ctx.drawImage(this.source, 32, 32);
  }
  compose(params: Params, st: State) {
    const output = canvas(this.scene.image.width, this.scene.image.height),
      ctx = output.getContext("2d")!;
    const draw = archetypes[this.scene.archetype].layout(
      this.scene,
      params,
      st,
    );
    this.staticBackground(ctx, params, draw);
    this.moving(ctx, draw, params);
    return output;
  }
  renderFrame0Check(st: State): Frame0Report {
    const composed = this.compose({}, st),
      a = this.source
        .getContext("2d")!
        .getImageData(0, 0, composed.width, composed.height).data;
    const b = composed
      .getContext("2d")!
      .getImageData(0, 0, composed.width, composed.height).data;
    let total = 0,
      over = 0;
    for (let i = 0; i < a.length; i += 4) {
      let exceeds = false;
      for (let c = 0; c < 3; c++) {
        const diff = Math.abs(a[i + c] - b[i + c]);
        total += diff;
        exceeds ||= diff > 16;
      }
      if (exceeds) over++;
    }
    const mean = total / (3 * composed.width * composed.height),
      fraction = over / (composed.width * composed.height);
    const layout = archetypes[this.scene.archetype].layout(this.scene, {}, st);
    let anchorError = 0;
    for (const body of this.scene.bodies) {
      const target = layout.bodies.find((b) => b.id === body.id);
      anchorError = Math.max(
        anchorError,
        target
          ? Math.hypot(
              target.anchor[0] - body.anchor[0],
              target.anchor[1] - body.anchor[1],
            )
          : Math.hypot(this.scene.image.width, this.scene.image.height),
      );
    }
    this.frame0 = {
      mean_absolute_channel: mean,
      fraction_over_16: fraction,
      max_anchor_error_px: anchorError,
      passed:
        mean <= FRAME0_LIMITS.meanAbsolute &&
        fraction <= FRAME0_LIMITS.fractionOver16 &&
        anchorError <= FRAME0_LIMITS.anchorErrorPx,
    };
    this.degraded = !this.frame0.passed;
    this.warnings = this.degraded ? ["render_mismatch"] : [];
    this.confidence = this.degraded ? 0.5 : 1;
    return this.frame0;
  }
  fitTrajectory(run: Trajectory, params: Params) {
    let minX = 0,
      minY = 0,
      maxX = this.scene.image.width,
      maxY = this.scene.image.height;
    this.predictedPaths.clear();
    for (let i = 0; i < run.states.length; i += 8) {
      const draw = archetypes[this.scene.archetype].layout(
        this.scene,
        params,
        run.states[i],
      );
      for (const b of draw.bodies) {
        minX = Math.min(minX, b.anchor[0] - 60);
        minY = Math.min(minY, b.anchor[1] - 60);
        maxX = Math.max(maxX, b.anchor[0] + 60);
        maxY = Math.max(maxY, b.anchor[1] + 60);
        const points = this.predictedPaths.get(b.id) ?? [];
        points.push(b.anchor);
        this.predictedPaths.set(b.id, points);
      }
    }
    this.padding = {
      left: Math.ceil(32 - minX),
      top: Math.ceil(32 - minY),
      right: Math.ceil(maxX - this.scene.image.width + 32),
      bottom: Math.ceil(maxY - this.scene.image.height + 32),
    };
    const w = this.scene.image.width + this.padding.left + this.padding.right,
      h = this.scene.image.height + this.padding.top + this.padding.bottom;
    const checked = this.frame0.mean_absolute_channel !== null;
    this.warnings = checked && !this.frame0.passed ? ["render_mismatch"] : [];
    this.degraded = checked && !this.frame0.passed;
    this.confidence = checked ? (this.degraded ? 0.5 : 1) : 0;
    if (
      w * this.dpr > 16000 ||
      h * this.dpr > 16000 ||
      w * h * this.dpr ** 2 > 32000000
    ) {
      this.padding = { left: 32, top: 32, right: 32, bottom: 32 };
      this.warnings.push("trajectory_extent_limit");
      this.degraded = true;
      this.confidence = 0.5;
    }
  }
  render(
    target: HTMLCanvasElement,
    params: Params,
    st: State,
    run: Trajectory,
    options: RenderOptions,
  ) {
    const s = this.scene,
      pad = this.padding,
      w = s.image.width + pad.left + pad.right,
      h = s.image.height + pad.top + pad.bottom;
    if (target.width !== w * this.dpr || target.height !== h * this.dpr) {
      target.width = w * this.dpr;
      target.height = h * this.dpr;
      target.style.width = `${w}px`;
      target.style.height = `${h}px`;
    }
    const ctx = target.getContext("2d")!;
    ctx.setTransform(this.dpr, 0, 0, this.dpr, 0, 0);
    ctx.textBaseline = "alphabetic";
    ctx.fillStyle = s.frame.paper_color;
    ctx.fillRect(0, 0, w, h);
    ctx.translate(pad.left, pad.top);
    const floors = s.surfaces.filter((sf) => sf.type === "floor");
    for (const floor of floors.filter(
      (sf) =>
        sf.polyline[0][1] === Math.max(...floors.map((f) => f.polyline[0][1])),
    )) {
      const y = floor.polyline[0][1];
      line(
        ctx,
        [
          [-pad.left, y],
          [0, y],
        ],
        s.frame.ink_color,
        s.frame.stroke_px,
      );
      line(
        ctx,
        [
          [s.image.width, y],
          [w - pad.left, y],
        ],
        s.frame.ink_color,
        s.frame.stroke_px,
      );
    }
    const draw = archetypes[s.archetype].layout(s, params, st);
    if (options.original || this.degraded) ctx.drawImage(this.source, 0, 0);
    else {
      this.staticBackground(ctx, params, draw);
      this.moving(ctx, draw, params);
    }
    if (options.original) return;
    if (options.trail) {
      ctx.setLineDash([7, 5]);
      for (const points of this.predictedPaths.values())
        line(ctx, points, "#165f9e", 2);
      ctx.setLineDash([]);
      ctx.font = "14px sans-serif";
      ctx.fillStyle = "#165f9e";
      ctx.fillText("- - predicted path", 20, 60);
    }
    if (options.forces)
      for (const force of archetypes[s.archetype].forces(s, params, st)) {
        if (force.component && !options.components) continue;
        const body = draw.bodies.find((b) => b.id === force.body);
        if (!body) continue;
        const mag = Math.hypot(force.vector.x, force.vector.y);
        if (mag < 1e-8) continue;
        const length = Math.min(110, Math.max(22, mag * 2)),
          end: Point = [
            body.anchor[0] + (length * force.vector.x) / mag,
            body.anchor[1] + (length * force.vector.y) / mag,
          ];
        arrow(
          ctx,
          body.anchor,
          end,
          force.component ? "#6b318c" : "#a82e18",
          `${force.label} ${mag.toFixed(1)} N`,
          !!force.component,
        );
      }
    for (const b of draw.bodies) {
      const v = st.velocities[b.id],
        mag = Math.hypot(v.x, v.y);
      if (mag > 1e-6)
        arrow(
          ctx,
          b.anchor,
          [b.anchor[0] + v.x * 15, b.anchor[1] + v.y * 15],
          "#005b42",
          `v ${mag.toFixed(2)} m/s`,
          true,
        );
      if (options.components) {
        if (Math.abs(v.x) > 1e-6)
          arrow(
            ctx,
            b.anchor,
            [b.anchor[0] + v.x * 15, b.anchor[1]],
            "#005b42",
            `vx ${v.x.toFixed(2)}`,
            true,
          );
        if (Math.abs(v.y) > 1e-6)
          arrow(
            ctx,
            b.anchor,
            [b.anchor[0], b.anchor[1] + v.y * 15],
            "#005b42",
            `vy ${v.y.toFixed(2)}`,
            true,
          );
      }
    }
    if (options.marker)
      for (const p of draw.pulleys) {
        ctx.globalAlpha = 0.3;
        line(
          ctx,
          [
            p.center,
            [
              p.center[0] + p.radius * Math.cos(p.rotation),
              p.center[1] + p.radius * Math.sin(p.rotation),
            ],
          ],
          "#005b42",
          4,
        );
        ctx.globalAlpha = 1;
      }
    if (options.handles)
      for (const handle of draw.handles) {
        ctx.fillStyle = "#fff";
        ctx.strokeStyle = "#003d70";
        ctx.lineWidth = 3;
        ctx.beginPath();
        ctx.rect(handle.point[0] - 7, handle.point[1] - 7, 14, 14);
        ctx.fill();
        ctx.stroke();
        ctx.fillStyle = "#003d70";
        ctx.font = "14px sans-serif";
        ctx.fillText(
          `drag ${handle.id}`,
          handle.point[0] + 12,
          handle.point[1] - 10,
        );
      }
  }
}
