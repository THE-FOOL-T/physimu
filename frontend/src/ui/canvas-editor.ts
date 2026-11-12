import type { Component, Netlist } from "../types";
import { Renderer, canvasToImage, imageToCanvas } from "../overlay/renderer";
import { t } from "../i18n";
import { componentIcon } from "./icons";
import { componentTypes } from "./editor";
import { PartPopover } from "./part-popover";
import { precheck, type CheckItem } from "./precheck";
import { distance } from "./topology";
import {
  drawWire,
  snapPoint,
  wireHit,
  cutWire,
  addBoxComponent,
  moveComponent,
  moveTerminal,
  rotateComponent,
  removeComponent,
  crossing,
} from "./edit-geometry";
import type { TraceIssue } from "./trace-issues";
import { issueAt } from "./trace-issues";

type XY = [number, number];
type Tool = "select" | "wire" | "cut" | "add" | "junction" | "read" | "pan";
type Actions = {
  net: () => Netlist;
  editing: () => boolean;
  setEditing: (value: boolean) => void;
  selected: () => string;
  select: (id: string) => void;
  mutate: (fn: (n: Netlist) => void) => void;
  run: () => boolean;
  undo: () => void;
  redo: () => void;
  reset: () => void;
  automatic: () => Netlist;
  notify: (message: string) => void;
  readArea: () => void;
};
const tools: [Tool, string, string][] = [
  ["select", "↖", "V"],
  ["wire", "└", "W"],
  ["cut", "✂", "X"],
  ["add", "+", "A"],
  ["junction", "●", "J"],
  ["read", "▣", "T"],
  ["pan", "✥", "Space"],
];
const create = <K extends keyof HTMLElementTagNameMap>(
  tag: K,
  parent: HTMLElement,
  key?: string,
) => {
  const n = document.createElement(tag);
  parent.append(n);
  if (key) {
    n.dataset.i18n = key;
    n.textContent = t(key);
  }
  return n;
};
export class CanvasEditor {
  tool: Tool = "select";
  dirty = false;
  step = 0;
  popover: PartPopover;
  private bar = document.createElement("section");
  private state = document.createElement("strong");
  private check = document.createElement("button");
  private rail = document.createElement("nav");
  private hint = document.createElement("p");
  private guide = document.createElement("div");
  private palette = document.createElement("div");
  private valueQueue = document.createElement("div");
  private help = document.createElement("section");
  private checklist: HTMLElement;
  private selectedType = "resistor";
  private autoRun = false;
  private path: XY[] = [];
  private space = false;
  private focusIndex = -1;
  private suppressedClick = false;
  private drag?: {
    start: XY;
    screen: XY;
    part?: string;
    terminal?: number;
    pan?: boolean;
    scroll?: XY;
  };
  private pointers = new Map<number, XY>();
  private pinch?: { length: number; zoom: number };
  private erase = new Set<string>();
  constructor(
    private renderer: Renderer,
    private actions: Actions,
  ) {
    const stage = document.getElementById("stage-area")!;
    this.bar.className = "edit-runbar";
    this.bar.hidden = true;
    this.rail.hidden = true;
    this.hint.hidden = true;
    this.bar.dataset.testid = "edit-runbar";
    stage.before(this.bar);
    const row = create("div", this.bar);
    row.className = "row edit-primary";
    row.append(this.state);
    const run = create("button", row, "edit.run");
    run.className = "primary";
    run.dataset.testid = "run-edited";
    run.onclick = () => this.run();
    const editAgain = create("button", row, "edit.again");
    editAgain.dataset.editAgain = "";
    editAgain.onclick = () => this.enter();
    const compare = create("button", row, "edit.compare");
    compare.dataset.testid = "compare-auto";
    compare.setAttribute("aria-pressed", "false");
    compare.onclick = () => {
      const active = compare.getAttribute("aria-pressed") !== "true";
      compare.setAttribute("aria-pressed", String(active));
      renderer.compareNet = active ? actions.automatic() : undefined;
    };
    const history = create("div", this.bar);
    history.className = "row edit-history";
    for (const id of ["undo", "redo", "reset-auto"])
      history.append(document.getElementById(id)!);
    const automatic = create("label", history);
    automatic.className = "toggle";
    const toggle = create("input", automatic);
    toggle.type = "checkbox";
    toggle.onchange = () => (this.autoRun = toggle.checked);
    create("span", automatic, "edit.auto_run");
    this.check.className = "precheck";
    this.check.dataset.testid = "precheck";
    this.bar.append(this.check);
    this.check.onclick = () =>
      this.fix(precheck(actions.net(), renderer.ghosts).items[0]);
    this.guide.className = "fix-stepper";
    this.bar.append(this.guide);
    ["parts", "wires", "values"].forEach((name, index) => {
      const b = create("button", this.guide);
      b.dataset.fixStep = String(index);
      b.onclick = () => this.setStep(index);
    });
    const next = create("button", this.guide, "edit.next");
    next.onclick = () => this.setStep(Math.min(2, this.step + 1));
    this.palette.className = "part-palette";
    this.bar.append(this.palette);
    this.valueQueue.className = "value-queue";
    this.bar.append(this.valueQueue);
    this.help.className = "panel edit-context-help";
    this.help.hidden = true;
    create("h2", this.help, "edit.help");
    create("p", this.help);
    document.querySelector(".right")!.prepend(this.help);
    for (const type of componentTypes) {
      const b = create("button", this.palette);
      b.dataset.addType = type;
      b.innerHTML = componentIcon(type);
      create("small", b).textContent = t("type." + type);
      b.title = t("type." + type);
      b.setAttribute("aria-label", t("type." + type));
      b.onclick = () => {
        this.selectedType = type;
        this.setTool("add");
      };
    }
    this.rail.className = "canvas-tools";
    this.rail.setAttribute("aria-label", t("edit.tools"));
    stage.prepend(this.rail);
    for (const [tool, icon, key] of tools) {
      const b = create("button", this.rail);
      b.dataset.canvasTool = tool;
      b.innerHTML = `<span aria-hidden="true">${icon}</span><span data-tool-label></span><kbd>${key}</kbd>`;
      b.onclick = () => this.setTool(tool);
    }
    this.hint.className = "canvas-hint";
    this.hint.setAttribute("role", "status");
    this.bar.after(this.hint);
    const fit = create(
      "button",
      document.querySelector<HTMLElement>(".canvas-toolbar")!,
      "edit.fit",
    );
    fit.dataset.testid = "fit";
    fit.onclick = () => this.fit();
    // Keep the former form available for technical users, collapsed by default.
    const dock = document.querySelector<HTMLElement>(".edit-dock")!;
    dock.querySelector(".editing-badge")?.remove();
    this.state.className = "editing-badge";
    const details = document.createElement("details"),
      summary = document.createElement("summary");
    summary.dataset.i18n = "edit.advanced";
    summary.textContent = t("edit.advanced");
    details.append(summary);
    for (const child of [...dock.children]) details.append(child);
    dock.append(details);
    dock.parentElement!.append(dock);
    this.checklist = document.getElementById("notices")!;
    this.popover = new PartPopover({
      net: actions.net,
      mutate: actions.mutate,
      screen: (xy) => this.screen(xy),
      selected: actions.selected,
    });
    const canvas = renderer.canvas;
    canvas.addEventListener("pointerdown", (e) => this.down(e), true);
    canvas.addEventListener("pointermove", (e) => this.move(e), true);
    canvas.addEventListener("pointerup", (e) => this.up(e), true);
    canvas.addEventListener(
      "pointercancel",
      (e) => {
        this.pointers.delete(e.pointerId);
        this.cancel();
      },
      true,
    );
    canvas.addEventListener("click", (e) => this.click(e), true);
    canvas.addEventListener(
      "dblclick",
      (e) => {
        if (actions.editing() && this.tool === "wire") {
          this.consume(e);
          this.finishWire();
        }
      },
      true,
    );
    canvas.addEventListener(
      "wheel",
      (e) => {
        e.preventDefault();
        this.zoom(e.deltaY < 0 ? 1.12 : 1 / 1.12, [e.clientX, e.clientY]);
      },
      { passive: false },
    );
    canvas.addEventListener("keydown", (e) => this.canvasKey(e), true);
    document.addEventListener("keydown", (e) => this.key(e));
    document.addEventListener("circuit:fix", (event) => {
      const ref = (event as CustomEvent<{ ref: string | null }>).detail.ref;
      const items = precheck(actions.net(), renderer.ghosts).items;
      this.fix(
        items.find((i) => i.part === ref || i.issue?.ref === ref) || items[0],
      );
    });
    document.addEventListener("keyup", (e) => {
      if (e.code === "Space") this.space = false;
    });
    document.getElementById("edit")!.onclick = () =>
      actions.editing() ? this.done() : this.enter();
    document.getElementById("undo")!.onclick = () => actions.undo();
    document.getElementById("redo")!.onclick = () => actions.redo();
    document.getElementById("reset-auto")!.onclick = () => actions.reset();
    this.translate();
  }
  private consume(e: Event) {
    e.preventDefault();
    e.stopImmediatePropagation();
  }
  private position(e: PointerEvent | MouseEvent): XY {
    return this.renderer.clientToImage(
      e.clientX,
      e.clientY,
      this.actions.net(),
    );
  }
  screen(xy: number[]): XY {
    return this.renderer.imageToScreen(xy, this.actions.net());
  }
  private radius() {
    return 12 / this.renderer.view(this.actions.net()).scale;
  }
  enter() {
    this.actions.setEditing(true);
    this.dirty = false;
    this.tool = "select";
    this.popover.close();
    this.update();
    this.actions.notify(t("edit.draft"));
  }
  done() {
    this.actions.notify(t("edit.run_first"));
    this.state.textContent = t("edit.run_first");
    document
      .querySelector<HTMLButtonElement>("[data-testid=run-edited]")
      ?.focus();
  }
  changed() {
    this.dirty = true;
    this.renderer.ghosts = this.renderer.ghosts.filter(
      (g) =>
        !this.actions
          .net()
          .components.some(
            (c) =>
              distance(
                [(c.bbox[0] + c.bbox[2]) / 2, (c.bbox[1] + c.bbox[3]) / 2],
                [(g.bbox[0] + g.bbox[2]) / 2, (g.bbox[1] + g.bbox[3]) / 2],
              ) < Math.max(10, (g.bbox[2] - g.bbox[0]) / 2),
          ),
    );
    this.update();
    if (this.autoRun) this.run();
  }
  reset() {
    this.cancel();
    this.popover.close();
    this.dirty = false;
    this.renderer.compareNet = undefined;
    this.update();
  }
  run() {
    this.cancel();
    if (this.actions.run()) {
      this.dirty = false;
      this.popover.close();
      this.update();
    } else {
      this.actions.setEditing(true);
      this.fix(precheck(this.actions.net(), this.renderer.ghosts).items[0]);
      this.update();
    }
  }
  setTool(tool: Tool) {
    document.dispatchEvent(new CustomEvent("circuit:tool", { detail: tool }));
    if (!this.actions.editing()) this.enter();
    this.cancel();
    this.tool = tool;
    this.popover.close();
    if (tool === "read") this.actions.readArea();
    this.update();
  }
  setStep(step: number) {
    this.step = step;
    this.setTool(step === 0 ? "select" : step === 1 ? "wire" : "select");
    if (step === 2) {
      const first = precheck(this.actions.net()).missing[0];
      if (first) {
        this.actions.select(first.id);
        this.popover.open(first.id, true);
      }
    }
    this.update();
  }
  focusIssue(issue: TraceIssue) {
    if (!this.actions.editing()) this.enter();
    this.renderer.highlightedIssue = issue.id;
    this.fix({
      id: issue.id,
      kind:
        issue.code === "missing_part"
          ? "part"
          : issue.code.includes("crossing")
            ? "crossing"
            : "wire",
      issue,
      count: 1,
    });
  }
  private fix(item?: CheckItem) {
    if (!item) return;
    if ((item.kind === "value" || item.kind === "unsupported") && item.part) {
      this.actions.select(item.part);
      this.popover.open(item.part, true);
      return;
    }
    if (item.kind === "polarity" && item.part) {
      this.actions.select(item.part);
      this.popover.open(item.part);
      return;
    }
    if (!this.actions.editing()) this.enter();
    if (item.issue) {
      this.renderer.highlightedIssue = item.issue.id;
      this.renderer.canvas.scrollIntoView({
        block: "center",
        behavior: "smooth",
      });
    }
    if (item.kind === "part") {
      this.setTool("add");
      if (item.issue?.bbox) {
        this.renderer.preview = { box: item.issue.bbox };
      }
      return;
    }
    if (item.kind === "crossing") {
      this.setTool("junction");
      return;
    }
    this.setTool("wire");
    if (item.issue) this.path = [[...item.issue.xy]];
    this.actions.notify(t("edit.hint.wire"));
  }
  update() {
    const net = this.actions.net();
    if (!net) return;
    const editing = this.actions.editing(),
      check = precheck(net, this.renderer.ghosts);
    this.bar.hidden = !editing && net.meta.provenance !== "edited";
    this.rail.hidden = !editing;
    this.hint.hidden = !editing;
    this.bar.classList.toggle("is-draft", editing);
    this.state.textContent = t(editing ? "edit.draft" : "edit.simulated");
    this.bar.querySelector<HTMLElement>(".edit-history")!.hidden = !editing;
    this.bar.querySelector<HTMLElement>("[data-testid=run-edited]")!.hidden =
      !editing;
    this.bar.querySelector<HTMLElement>("[data-edit-again]")!.hidden = editing;
    this.bar.querySelector<HTMLElement>("[data-testid=compare-auto]")!.hidden =
      editing;
    this.check.hidden = !editing;
    this.check.classList.toggle("ready", check.ready);
    const item = check.items[0];
    this.check.textContent = check.ready
      ? t("edit.ready", {
          parts: String(check.parts),
          sources: String(check.sources),
        })
      : t("edit.not_ready", {
          issue: item ? this.itemText(item) : t("edit.no_source"),
        });
    this.guide.hidden = !editing;
    this.palette.hidden = !editing || this.tool !== "add";
    for (const b of this.rail.querySelectorAll<HTMLButtonElement>("button")) {
      const tool = b.dataset.canvasTool!;
      b.setAttribute("aria-pressed", String(tool === this.tool));
      b.querySelector<HTMLElement>("[data-tool-label]")!.textContent = t(
        "edit.tool." + tool,
      );
      b.title = t("edit.hint." + tool);
    }
    for (const b of this.guide.querySelectorAll<HTMLButtonElement>(
      "[data-fix-step]",
    )) {
      const index = Number(b.dataset.fixStep);
      b.textContent = `${index + 1}. ${t("edit.step." + ["parts", "wires", "values"][index])}`;
      b.setAttribute("aria-current", index === this.step ? "step" : "false");
    }
    this.hint.textContent = t("edit.hint." + this.tool);
    this.help.hidden = !editing;
    this.help.querySelector("p")!.textContent = this.hint.textContent;
    this.valueQueue.hidden = !editing || this.step !== 2;
    this.valueQueue.replaceChildren();
    if (this.step === 2)
      for (const c of check.missing) {
        const button = create("button", this.valueQueue);
        button.textContent = c.id + " · " + t("edit.enter_value");
        button.onclick = () =>
          this.fix({ id: c.id, kind: "value", part: c.id, count: 1 });
      }
    this.renderer.canvas.dataset.activeTool = this.tool;
    for (const b of this.palette.querySelectorAll<HTMLButtonElement>("button"))
      b.setAttribute(
        "aria-pressed",
        String(b.dataset.addType === this.selectedType),
      );
    this.renderer.issues = check.issues;
    this.renderChecklist(check.items, check.closed);
    const chip = this.popover.element.querySelector<HTMLElement>(".status"),
      part = net.components.find((c) => c.id === this.popover.part);
    if (chip && part) {
      chip.textContent = t(part.value.status);
      chip.className = "status " + part.value.status;
    }
    if (part) {
      const slider = this.popover.element.querySelector<HTMLInputElement>(
        "[data-testid=part-slider]",
      );
      if (slider && slider !== document.activeElement) {
        slider.max = String(
          Math.max(Number(slider.max), Math.abs(part.value.number || 0) * 2),
        );
        slider.value = String(part.value.number ?? 0);
      }
      const value =
        this.popover.element.querySelector<HTMLInputElement>("#part-value");
      if (value && value !== document.activeElement)
        value.value =
          part.value.number === null ? "" : String(part.value.number);
      const unit = this.popover.element.querySelector<HTMLSelectElement>(
        "[data-testid=part-unit]",
      );
      if (unit && unit !== document.activeElement) unit.value = part.value.unit;
      const name =
        this.popover.element.querySelector<HTMLInputElement>("#part-name");
      if (name && name !== document.activeElement)
        name.value = part.label || part.id;
    }
    if (part)
      for (const button of this.popover.element.querySelectorAll<HTMLButtonElement>(
        "[data-part-type]",
      ))
        button.setAttribute(
          "aria-pressed",
          String(button.dataset.partType === part.type),
        );
    this.popover.place();
  }
  translate() {
    this.rail.setAttribute("aria-label", t("edit.tools"));
    this.update();
  }
  private itemText(item: CheckItem) {
    return t("edit.check." + item.kind, {
      count: String(item.count),
      part: item.part || "",
    });
  }
  private renderChecklist(items: CheckItem[], closed: boolean) {
    this.checklist.replaceChildren();
    document.getElementById("warning-count")!.textContent = String(
      items.length,
    );
    const list = create("div", this.checklist);
    list.className = "fix-checklist";
    list.dataset.testid = "fix-checklist";
    if (!items.length)
      create(
        "p",
        list,
        closed
          ? this.actions.editing()
            ? "edit.ready_draft"
            : "edit.running"
          : "edit.no_source",
      );
    for (const item of items.slice(0, 8)) {
      const row = create("div", list);
      row.className = "checklist-item";
      create("span", row).textContent = this.itemText(item);
      const button = create(
        "button",
        row,
        item.kind === "value" ? "edit.enter_value" : "trace.fix",
      );
      button.dataset.check = item.id;
      button.onclick = () => this.fix(item);
      if (item.kind === "crossing" && item.issue)
        for (const [value, key] of [
          [true, "edit.yes"],
          [false, "edit.no"],
        ] as const) {
          const b = create("button", row, key);
          b.onclick = () =>
            this.actions.mutate((n) => crossing(n, item.issue!.xy, value));
        }
    }
    if (items.length > 8)
      create("p", list).textContent = t("edit.more_issues", {
        count: String(items.length - 8),
      });
    const details = create("details", this.checklist);
    create("summary", details, "edit.details");
    const groups = new Map<
      string,
      { count: number; refs: string[]; key: string }
    >();
    for (const w of this.actions.net().warnings) {
      const g = groups.get(w.code) || {
        count: 0,
        refs: [],
        key: w.message_key,
      };
      g.count++;
      if (w.ref) g.refs.push(w.ref);
      groups.set(w.code, g);
    }
    for (const group of groups.values())
      create("p", details).textContent =
        `${t(group.key)} (${group.count}) ${group.refs.join(", ")}`;
  }
  private down(e: PointerEvent) {
    this.pointers.set(e.pointerId, [e.clientX, e.clientY]);
    if (this.pointers.size === 2) {
      const [a, b] = [...this.pointers.values()];
      this.pinch = { length: distance(a, b), zoom: this.zoomValue() };
      this.drag = undefined;
      this.consume(e);
      this.renderer.canvas.setPointerCapture(e.pointerId);
      return;
    }
    const pan = e.button === 1 || this.space || this.tool === "pan";
    if (!this.actions.editing() && !pan) return;
    if (this.tool === "read" && !pan) return;
    this.consume(e);
    this.renderer.canvas.setPointerCapture(e.pointerId);
    const xy = this.position(e);
    this.drag = { start: xy, screen: [e.clientX, e.clientY], pan };
    if (pan) {
      const stage = document.getElementById("canvas-viewport")!;
      this.drag.scroll = [stage.scrollLeft, stage.scrollTop];
      return;
    }
    if (this.tool === "select") {
      const terminal = this.actions
        .net()
        .components.flatMap((c) => c.terminals.map((t, i) => ({ c, t, i })))
        .find(({ t }) => distance(t.xy, xy) < this.radius());
      if (terminal) {
        this.drag.part = terminal.c.id;
        this.drag.terminal = terminal.i;
        this.actions.select(terminal.c.id);
      } else {
        const part = this.renderer.hit(...xy, this.actions.net());
        if (part) {
          this.drag.part = part.id;
          this.actions.select(part.id);
        } else
          this.renderer.selectedWire =
            wireHit(this.actions.net(), xy, this.radius())?.segment.id || "";
      }
    }
    if (this.tool === "cut") {
      this.erase.clear();
      this.eraseAt(xy);
    }
  }
  private move(e: PointerEvent) {
    if (this.pointers.has(e.pointerId))
      this.pointers.set(e.pointerId, [e.clientX, e.clientY]);
    if (this.pinch && this.pointers.size === 2) {
      const [a, b] = [...this.pointers.values()];
      this.setZoom((this.pinch.zoom * distance(a, b)) / this.pinch.length);
      this.consume(e);
      return;
    }
    const xy = this.position(e),
      snap = snapPoint(
        this.actions.net(),
        xy,
        this.radius(),
        this.drag?.part === this.actions.selected() &&
          this.drag.terminal !== undefined
          ? this.actions.net().components.find((c) => c.id === this.drag!.part)
              ?.terminals[this.drag.terminal].id
          : undefined,
      );
    if (this.actions.editing())
      this.renderer.canvas.style.cursor =
        this.tool === "cut"
          ? "crosshair"
          : this.tool === "pan" || this.space
            ? "grab"
            : this.tool === "select"
              ? "default"
              : "crosshair";
    if (this.drag) {
      this.consume(e);
      if (this.drag.pan) {
        const stage = document.getElementById("canvas-viewport")!;
        stage.scrollLeft =
          this.drag.scroll![0] - (e.clientX - this.drag.screen[0]);
        stage.scrollTop =
          this.drag.scroll![1] - (e.clientY - this.drag.screen[1]);
        return;
      }
      if (this.tool === "add") {
        this.renderer.preview = {
          box: [
            Math.min(xy[0], this.drag.start[0]),
            Math.min(xy[1], this.drag.start[1]),
            Math.max(xy[0], this.drag.start[0]),
            Math.max(xy[1], this.drag.start[1]),
          ],
        };
      } else if (this.tool === "cut") this.eraseAt(xy);
      else if (this.tool === "wire")
        this.renderer.preview = {
          line: this.route(
            this.path.at(-1) || this.drag.start,
            snap.xy,
            e.shiftKey,
          ),
          snap: snap.xy,
        };
      else if (this.tool === "select" && this.drag.part) {
        const c = this.actions
          .net()
          .components.find((c) => c.id === this.drag!.part)!;
        this.renderer.preview =
          this.drag.terminal !== undefined
            ? {
                line: [c.terminals[this.drag.terminal].xy, snap.xy],
                snap: snap.xy,
              }
            : {
                box: c.bbox.map(
                  (v, i) => v + xy[i % 2] - this.drag!.start[i % 2],
                ) as Component["bbox"],
              };
      }
    } else if (this.path.length && this.tool === "wire")
      this.renderer.preview = {
        line: [
          ...this.path,
          ...this.route(this.path.at(-1)!, snap.xy, e.shiftKey).slice(1),
        ],
        snap: snap.xy,
      };
    else if (this.actions.editing() && this.tool === "cut")
      this.renderer.selectedWire =
        wireHit(this.actions.net(), xy, this.radius())?.segment.id || "";
  }
  private up(e: PointerEvent) {
    this.pointers.delete(e.pointerId);
    if (this.pointers.size < 2) this.pinch = undefined;
    if (!this.drag) return;
    this.consume(e);
    const drag = this.drag;
    this.drag = undefined;
    this.renderer.preview = undefined;
    if (this.renderer.canvas.hasPointerCapture(e.pointerId))
      this.renderer.canvas.releasePointerCapture(e.pointerId);
    if (drag.pan) {
      this.suppressClick();
      return;
    }
    const xy = this.position(e),
      moved = distance([e.clientX, e.clientY], drag.screen) > 5;
    if (this.tool === "wire") {
      const target = snapPoint(this.actions.net(), xy, this.radius());
      if (moved) {
        const route = this.route(
          this.path.at(-1) ||
            snapPoint(this.actions.net(), drag.start, this.radius()).xy,
          target.xy,
          e.shiftKey,
        );
        this.path = this.path.length
          ? [...this.path, ...route.slice(1)]
          : route;
        this.finishWire();
      } else if (!this.path.length) this.path = [target.xy];
      else {
        this.path.push(
          ...this.route(this.path.at(-1)!, target.xy, e.shiftKey).slice(1),
        );
        if (target.id || wireHit(this.actions.net(), target.xy, 1))
          this.finishWire();
      }
      this.suppressClick();
      return;
    }
    if (this.tool === "add") {
      const box: Component["bbox"] = moved
        ? [
            Math.min(xy[0], drag.start[0]),
            Math.min(xy[1], drag.start[1]),
            Math.max(xy[0], drag.start[0]),
            Math.max(xy[1], drag.start[1]),
          ]
        : [xy[0] - 25, xy[1] - 12, xy[0] + 25, xy[1] + 12];
      let id = "";
      this.actions.mutate((n) => {
        id = addBoxComponent(n, this.selectedType, box, this.radius()).id;
      });
      this.actions.select(id);
      this.tool = "select";
      this.update();
      this.popover.open(id, true);
      this.actions.notify(t("edit.part_added", { part: id }));
      this.suppressClick();
      return;
    }
    if (this.tool === "select" && drag.part && moved) {
      this.actions.mutate((n) => {
        const c = n.components.find((c) => c.id === drag.part)!;
        if (drag.terminal !== undefined)
          moveTerminal(
            n,
            c,
            drag.terminal,
            snapPoint(n, xy, this.radius(), c.terminals[drag.terminal].id).xy,
          );
        else moveComponent(n, c, xy[0] - drag.start[0], xy[1] - drag.start[1]);
      });
      this.actions.notify(t("edit.moved"));
      this.suppressClick();
    }
    if (this.tool === "cut") {
      this.suppressClick();
      this.actions.notify(t("edit.wire_cut"));
    }
  }
  private click(e: MouseEvent) {
    if (this.suppressedClick) {
      this.consume(e);
      return;
    }
    if (this.tool === "read" && this.actions.editing()) return;
    const xy = this.position(e);
    if (this.actions.editing() && this.tool === "junction") {
      this.consume(e);
      const hit = wireHit(this.actions.net(), xy, this.radius());
      if (hit) this.actions.mutate((n) => crossing(n, hit.xy));
      return;
    }
    const part = this.renderer.hit(...xy, this.actions.net());
    const issue = issueAt(this.renderer.issues, ...xy, this.radius());
    if (issue && !part && this.tool === "select") {
      this.consume(e);
      this.focusIssue(issue);
      return;
    }
    if (part && (!this.actions.editing() || this.tool === "select")) {
      this.consume(e);
      this.actions.select(part.id);
      if (part.type === "switch" && !this.actions.editing())
        this.actions.mutate((n) => {
          const c = n.components.find((c) => c.id === part.id)!;
          c.switch_closed = !c.switch_closed;
        });
      this.popover.open(part.id);
      return;
    }
    if (this.actions.editing()) this.consume(e);
  }
  private route(a: XY, b: XY, free: boolean): XY[] {
    if (free || Math.abs(a[0] - b[0]) < 1 || Math.abs(a[1] - b[1]) < 1)
      return [[...a], [...b]];
    return [[...a], [b[0], a[1]], [...b]];
  }
  private finishWire() {
    if (this.path.length < 2) return;
    const path = this.path;
    this.path = [];
    this.renderer.preview = undefined;
    this.actions.mutate((n) => drawWire(n, path));
    this.actions.notify(t("edit.wire_added"));
  }
  private eraseAt(xy: XY) {
    const hit = wireHit(this.actions.net(), xy, this.radius());
    if (hit && !this.erase.has(hit.segment.id)) {
      this.erase.add(hit.segment.id);
      this.actions.mutate((n) => cutWire(n, hit.segment.id));
    }
  }
  private suppressClick() {
    this.suppressedClick = true;
    setTimeout(() => (this.suppressedClick = false), 0);
  }
  private cancel() {
    this.drag = undefined;
    this.path = [];
    this.renderer.preview = undefined;
    this.erase.clear();
  }
  private canvasKey(e: KeyboardEvent) {
    const net = this.actions.net();
    if (e.key === "Tab") {
      this.consume(e);
      const choices = [
        ...net.components.map((c) => c.id),
        ...net.wire_graph.segments.map((s) => s.id),
      ];
      this.focusIndex =
        (this.focusIndex + (e.shiftKey ? -1 : 1) + choices.length) %
        choices.length;
      const id = choices[this.focusIndex];
      if (net.components.some((c) => c.id === id)) {
        this.renderer.selectedWire = "";
        this.actions.select(id);
      } else {
        this.renderer.selectedWire = id;
        this.actions.notify(t("edit.wire_selected"));
      }
      return;
    }
    if (e.key === "Enter" && this.tool !== "wire" && !e.ctrlKey && !e.metaKey) {
      this.consume(e);
      this.popover.open(this.actions.selected(), true);
      return;
    }
    if (!this.actions.editing()) return;
    if (e.key.startsWith("Arrow")) {
      this.consume(e);
      const c = net.components.find((c) => c.id === this.actions.selected());
      if (c)
        this.actions.mutate((n) =>
          moveComponent(
            n,
            n.components.find((p) => p.id === c.id)!,
            e.key === "ArrowLeft" ? -2 : e.key === "ArrowRight" ? 2 : 0,
            e.key === "ArrowUp" ? -2 : e.key === "ArrowDown" ? 2 : 0,
          ),
        );
    }
    if (e.key === "Delete") {
      this.consume(e);
      this.actions.mutate((n) =>
        this.renderer.selectedWire
          ? cutWire(n, this.renderer.selectedWire)
          : removeComponent(n, this.actions.selected()),
      );
    }
  }
  private key(e: KeyboardEvent) {
    const input =
      e.target instanceof HTMLInputElement ||
      e.target instanceof HTMLTextAreaElement ||
      e.target instanceof HTMLSelectElement;
    if (e.key === "Escape") {
      this.cancel();
      this.popover.close();
      this.tool = "select";
      this.update();
      document.querySelector<HTMLButtonElement>("[data-testid=fit]")?.focus();
      return;
    }
    if ((e.ctrlKey || e.metaKey) && e.key === "Enter") {
      e.preventDefault();
      if (this.actions.editing()) this.run();
      return;
    }
    if (input) return;
    if ((e.ctrlKey || e.metaKey) && ["z", "y"].includes(e.key.toLowerCase())) {
      e.preventDefault();
      if (e.key.toLowerCase() === "y" || e.shiftKey) this.actions.redo();
      else this.actions.undo();
      return;
    }
    if (e.ctrlKey || e.metaKey || e.altKey) return;
    if (e.code === "Space") {
      this.space = true;
      e.preventDefault();
      return;
    }
    const tool = tools.find(
      ([, , key]) => key.toLowerCase() === e.key.toLowerCase(),
    );
    if (tool) {
      e.preventDefault();
      if (tool[0] !== "read") this.setTool(tool[0]);
      return;
    }
    if (e.key.toLowerCase() === "r" && this.actions.editing()) {
      e.preventDefault();
      this.actions.mutate((n) => {
        const c = n.components.find((c) => c.id === this.actions.selected());
        if (c) rotateComponent(n, c);
      });
    }
    if (e.key === "Enter" && this.actions.editing() && this.tool === "wire") {
      e.preventDefault();
      this.finishWire();
    }
  }
  private zoomValue() {
    return (
      parseFloat(document.getElementById("canvas-shell")!.style.width) || 100
    );
  }
  private setZoom(value: number) {
    const zoom = Math.max(100, Math.min(500, value));
    this.renderer.zoom = zoom / 100;
    document.getElementById("canvas-shell")!.style.width = zoom + "%";
    const input = document.getElementById("zoom") as HTMLInputElement;
    input.max = "500";
    input.value = String(zoom);
    this.popover.place();
  }
  private zoom(factor: number, at: XY) {
    const stage = document.getElementById("canvas-viewport")!,
      rect = stage.getBoundingClientRect(),
      x = at[0] - rect.left,
      y = at[1] - rect.top;
    const old = this.zoomValue();
    this.setZoom(old * factor);
    const ratio = this.zoomValue() / old;
    stage.scrollLeft = (stage.scrollLeft + x) * ratio - x;
    stage.scrollTop = (stage.scrollTop + y) * ratio - y;
  }
  fit() {
    this.setZoom(100);
    const stage = document.getElementById("canvas-viewport")!;
    stage.scrollLeft = stage.scrollTop = 0;
    this.actions.notify(t("edit.fit_hint"));
  }
}
