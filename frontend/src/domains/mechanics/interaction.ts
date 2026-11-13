import type { Point, State } from "./types";
import { BindingEngine } from "./bindings";
import { archetypes } from "./archetypes";
import { sample } from "./sampling";
import type { EditState } from "./authoring";

export interface PhysicsHandle {
  id: string;
  object: string;
  point: Point;
  axis: "launch" | "slope" | "arc" | "horizontal" | "vertical";
}

/** Physical handles are independent of editable source geometry handles. */
export function physicsHandles(
  engine: BindingEngine,
  state?: State,
): PhysicsHandle[] {
  const s = engine.original,
    run = engine.trajectory;
  if (!run.supported || !run.states.length) return [];
  const draw = archetypes[s.archetype].layout(
    s,
    engine.params,
    state ?? run.states[0],
  );
  const body = (
    i: number,
    id: string,
    axis: PhysicsHandle["axis"],
  ): PhysicsHandle => ({
    id,
    object: s.bodies[i].id,
    point: draw.bodies[i].anchor,
    axis,
  });
  switch (s.archetype) {
    case "projectile": {
      const launch = draw.handles.find((h) => h.id === "launch");
      return launch
        ? [{ ...launch, object: s.bodies[0].id, axis: "launch" }]
        : [];
    }
    case "incline_block":
      return [body(0, "block", "slope")];
    case "pendulum":
      return [body(0, "bob", "arc")];
    case "spring_mass":
      return [
        body(
          0,
          "spring_end",
          s.params.vertical?.number ? "vertical" : "horizontal",
        ),
      ];
    case "atwood":
      return [body(0, "pulley_0", "vertical"), body(1, "pulley_1", "vertical")];
    case "table_pulley":
      return [
        body(0, "pulley_0", "horizontal"),
        body(1, "pulley_1", "vertical"),
      ];
    case "incline_pulley":
      return [body(0, "pulley_0", "slope"), body(1, "pulley_1", "vertical")];
    case "collision_1d":
      return s.bodies.map((b, i) => body(i, `collision_${b.id}`, "horizontal"));
    default:
      return [];
  }
}

export interface InteractionHost {
  canvas: HTMLCanvasElement;
  viewport: HTMLElement;
  engine(): BindingEngine | null;
  enabled(): boolean;
  point(event: PointerEvent): Point;
  radius(): number;
  time(): number;
  pause(): void;
  selected(): string;
  select(id: string): void;
  snapshot(): EditState;
  restore(state: EditState): void;
  preview(): void;
  commit(before: EditState): void;
  error(error: unknown): void;
}

/** Pointer capture, constrained BindingEngine updates and one history transaction.
 * The source scene never moves. A grabbed body retains its pointer offset while
 * playback resets to initial conditions, preventing a jump to an arbitrary state. */
export class PhysicsInteractionController {
  private gesture: {
    pointer: number;
    start: Point;
    origin: Point;
    handle: PhysicsHandle;
    before: EditState;
    moved: boolean;
  } | null = null;
  private pan: {
    pointer: number;
    x: number;
    y: number;
    left: number;
    top: number;
  } | null = null;
  constructor(private host: InteractionHost) {}
  get dragging() {
    return this.gesture !== null;
  }
  down(e: PointerEvent) {
    const h = this.host,
      engine = h.engine();
    if (
      !h.enabled() ||
      !engine ||
      this.gesture ||
      this.pan ||
      ![0, 1].includes(e.button)
    )
      return false;
    const p = h.point(e),
      radius = h.radius();
    const state = engine.trajectory.supported
      ? sample(engine.trajectory, h.time())
      : undefined;
    const targets = physicsHandles(engine, state);
    let hit = targets
      .map((target) => ({
        target,
        d: Math.hypot(target.point[0] - p[0], target.point[1] - p[1]),
      }))
      .sort((a, b) => a.d - b.d)
      .find((v) => v.d <= radius)?.target;
    if (!hit && state) {
      const draw = archetypes[engine.original.archetype].layout(
        engine.original,
        engine.params,
        state,
      );
      const b = draw.bodies.find((b) => {
        const source = engine.original.bodies.find((s) => s.id === b.id)!;
        return (
          Math.abs(p[0] - b.anchor[0]) <=
            (source.bbox[2] - source.bbox[0]) / 2 + radius / 3 &&
          Math.abs(p[1] - b.anchor[1]) <=
            (source.bbox[3] - source.bbox[1]) / 2 + radius / 3
        );
      });
      hit = b ? targets.find((v) => v.object === b.id) : undefined;
    }
    h.canvas.setPointerCapture(e.pointerId);
    if (!hit || e.button === 1) {
      this.pan = {
        pointer: e.pointerId,
        x: e.clientX,
        y: e.clientY,
        left: h.viewport.scrollLeft,
        top: h.viewport.scrollTop,
      };
    } else {
      const initial = physicsHandles(engine).find((v) => v.id === hit!.id)!;
      let origin = initial.point;
      if (hit.id === "spring_end") {
        origin = archetypes.spring_mass
          .layout(engine.original, engine.params, engine.trajectory.states[0])
          .links[0].points.at(-1)!;
      }
      this.gesture = {
        pointer: e.pointerId,
        start: p,
        origin,
        handle: hit,
        before: h.snapshot(),
        moved: false,
      };
      h.pause();
      h.select(hit.object);
    }
    e.preventDefault();
    return true;
  }
  move(e: PointerEvent) {
    const h = this.host,
      g = this.gesture;
    if (this.pan?.pointer === e.pointerId) {
      h.viewport.scrollLeft = this.pan.left + this.pan.x - e.clientX;
      h.viewport.scrollTop = this.pan.top + this.pan.y - e.clientY;
      return true;
    }
    if (!g || g.pointer !== e.pointerId) return false;
    const p = h.point(e),
      dx = p[0] - g.start[0],
      dy = p[1] - g.start[1];
    if (!g.moved && Math.hypot(dx, dy) < h.radius() / 8) return true;
    try {
      g.moved = true;
      h.engine()!.drag(g.handle.id, [g.origin[0] + dx, g.origin[1] + dy], true);
      h.preview();
    } catch (error) {
      this.cancel();
      h.error(error);
    }
    return true;
  }
  up(e: PointerEvent) {
    if (!this.gesture && !this.pan) return false;
    this.move(e);
    const g = this.gesture;
    if (g && g.pointer !== e.pointerId) return false;
    this.gesture = null;
    this.pan = null;
    if (this.host.canvas.hasPointerCapture(e.pointerId))
      this.host.canvas.releasePointerCapture(e.pointerId);
    if (g?.moved) {
      this.host.engine()!.complete();
      this.host.commit(g.before);
    }
    return true;
  }
  cancel() {
    const g = this.gesture,
      pointer = g?.pointer ?? this.pan?.pointer;
    this.gesture = null;
    this.pan = null;
    if (pointer !== undefined && this.host.canvas.hasPointerCapture(pointer))
      this.host.canvas.releasePointerCapture(pointer);
    if (g) {
      this.host.restore(g.before);
      this.host.preview();
    }
  }
  key(e: KeyboardEvent) {
    if (e.key === "Escape" && (this.gesture || this.pan)) {
      this.cancel();
      return true;
    }
    const h = this.host,
      engine = h.engine();
    if (!h.enabled() || !engine || !e.key.startsWith("Arrow")) return false;
    const handle = physicsHandles(engine).find(
      (v) => v.object === h.selected(),
    );
    if (!handle) return false;
    const before = h.snapshot(),
      step = e.shiftKey ? 12 : 4;
    let origin = handle.point;
    if (handle.id === "spring_end")
      origin = archetypes.spring_mass
        .layout(engine.original, engine.params, engine.trajectory.states[0])
        .links[0].points.at(-1)!;
    try {
      h.pause();
      engine.drag(handle.id, [
        origin[0] +
          (e.key === "ArrowRight" ? step : e.key === "ArrowLeft" ? -step : 0),
        origin[1] +
          (e.key === "ArrowDown" ? step : e.key === "ArrowUp" ? -step : 0),
      ]);
      h.commit(before);
    } catch (error) {
      h.restore(before);
      h.error(error);
    }
    e.preventDefault();
    return true;
  }
}

/** Draw above physics overlays; coordinates share the renderer's native frame. */
export function drawPhysicsInteraction(
  ctx: CanvasRenderingContext2D,
  engine: BindingEngine,
  state: State,
  selected: string,
  radius: number,
  label: string,
) {
  const targets = physicsHandles(engine, state);
  ctx.save();
  ctx.lineWidth = 2;
  for (const handle of targets) {
    const [x, y] = handle.point;
    ctx.strokeStyle = "#00689d";
    ctx.fillStyle = handle.object === selected ? "#d8f0ff" : "#fff";
    ctx.beginPath();
    ctx.arc(x, y, radius, 0, Math.PI * 2);
    ctx.fill();
    ctx.stroke();
    ctx.setLineDash([4, 4]);
    if (["horizontal", "slope", "vertical"].includes(handle.axis)) {
      let dx = 1,
        dy = 0;
      if (handle.axis === "vertical") {
        dx = 0;
        dy = 1;
      }
      if (handle.axis === "slope") {
        const sf = engine.original.surfaces.find((s) => s.type === "incline")!;
        const a =
          ((engine.params[`surfaces.${sf.id}.angle_deg`] ??
            sf.angle_deg!.number!) *
            Math.PI) /
          180;
        dx = Math.cos(a);
        dy = -Math.sin(a);
      }
      ctx.beginPath();
      ctx.moveTo(x - dx * 45, y - dy * 45);
      ctx.lineTo(x + dx * 45, y + dy * 45);
      ctx.stroke();
    }
    if (handle.axis === "arc") {
      const pivot = engine.original.links[0].a.point;
      const r = Math.hypot(x - pivot[0], y - pivot[1]),
        angle = Math.atan2(y - pivot[1], x - pivot[0]);
      ctx.beginPath();
      ctx.arc(...pivot, r, angle - 0.25, angle + 0.25);
      ctx.stroke();
    }
    ctx.setLineDash([]);
    if (handle.object === selected) {
      ctx.font = '14px "Noto Sans Bengali", sans-serif';
      ctx.strokeStyle = "#fff";
      ctx.lineWidth = 4;
      ctx.strokeText(label, x + radius + 5, y - radius - 5);
      ctx.fillStyle = "#005789";
      ctx.fillText(label, x + radius + 5, y - radius - 5);
      ctx.lineWidth = 2;
    }
  }
  ctx.restore();
}
