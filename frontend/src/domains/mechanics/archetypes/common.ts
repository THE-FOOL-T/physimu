import type {
  Scene,
  Params,
  State,
  Trajectory,
  Event,
  XY,
  RegimeInfo,
} from "../types";
import { valueAt } from "../validate";

export const DT = 1 / 240;
export const RAD = Math.PI / 180;
export function read(
  scene: Scene,
  params: Params,
  path: string,
  fallback?: number,
): number {
  if (path in params) {
    if (!Number.isFinite(params[path])) throw new Error(`Nonfinite ${path}`);
    return params[path];
  }
  try {
    const value = valueAt(scene, path);
    if (value.number === null) throw new Error(`Unresolved ${path}`);
    return value.number;
  } catch (error) {
    // An explicitly unresolved Value must never be replaced by a default.
    if (
      fallback !== undefined &&
      !(path.split(".")[1] in (scene.params ?? {})) &&
      path.startsWith("params.")
    )
      return fallback;
    throw error;
  }
}
export function positive(n: number, name: string): number {
  if (!(n > 0)) throw new Error(`${name} must be positive`);
  return n;
}
export const scale = (s: Scene, p: Params = {}) =>
  positive(read(s, p, "frame.px_per_m"), "scale");
export const gravity = (s: Scene, p: Params) =>
  positive(read(s, p, "constants.g"), "gravity");
export const mass = (s: Scene, p: Params, id = s.bodies[0]?.id) =>
  positive(read(s, p, `bodies.${id}.mass`), "mass");
export function initial(
  s: Scene,
  id: string,
  kind: "position" | "velocity",
): XY {
  const b = s.bodies.find((b) => b.id === id)!;
  const v = b.initial[kind];
  if (v.x.number === null || v.y.number === null)
    throw new Error("Unresolved initial state");
  return { x: v.x.number, y: v.y.number };
}
export function state(
  t: number,
  positions: Record<string, XY>,
  velocities: Record<string, XY>,
  kinetic: number,
  potential: number,
  masses: Record<string, number>,
  scalars: Record<string, number> = {},
): State {
  const momentum = { x: 0, y: 0 };
  for (const [id, v] of Object.entries(velocities)) {
    momentum.x += masses[id] * v.x;
    momentum.y += masses[id] * v.y;
  }
  return { t, positions, velocities, kinetic, potential, momentum, scalars };
}
export function sampleTimes(duration: number, events: Event[] = []): number[] {
  if (!Number.isFinite(duration) || duration < 0 || duration > 120)
    throw new Error("trajectory_budget_exceeded");
  const times = [0];
  for (let i = 1; i * DT < duration - 1e-10; i++) times.push(i * DT);
  times.push(duration, ...events.map((e) => e.time));
  return [...new Set(times.map((t) => Math.round(t * 1e12) / 1e12))].sort(
    (a, b) => a - b,
  );
}
export function trajectory(
  duration: number,
  evaluate: (t: number) => State,
  events: Event[] = [],
  metrics: Record<string, number> = {},
  warnings: string[] = [],
): Trajectory {
  const times = sampleTimes(duration, events);
  const states = times.map(evaluate);
  if (
    !states.every(
      (s) =>
        Object.values(s.positions).every(
          (p) => Number.isFinite(p.x) && Number.isFinite(p.y),
        ) && Number.isFinite(s.kinetic + s.potential),
    )
  )
    throw new Error("Nonfinite trajectory");
  return {
    dt: DT,
    times,
    states,
    events,
    duration,
    metrics,
    warnings,
    supported: true,
  };
}
export function unsupported(reason: string): Trajectory {
  return {
    dt: DT,
    times: [],
    states: [],
    events: [],
    duration: 0,
    metrics: {},
    warnings: [reason],
    supported: false,
    reason,
  };
}
export function guarded(
  s: Scene,
  p: Params,
  solve: () => Trajectory,
): Trajectory {
  try {
    if (s.frame.gravity[0] !== 0 || s.frame.gravity[1] !== 1)
      return unsupported("unsupported_gravity");
    if (s.warnings.some((w) => w.code === "unknown_type"))
      return unsupported("unknown_type");
    scale(s, p);
    gravity(s, p);
    s.bodies.forEach((b) => mass(s, p, b.id));
    return solve();
  } catch (error) {
    return unsupported(
      error instanceof Error ? error.message : "invalid_scene",
    );
  }
}
export function info(code: string, message: string, scene: Scene): RegimeInfo {
  const assumed = scene.bindings.some(
    (b) => valueAt(scene, b.path).status === "assumed",
  );
  return { code, message, warnings: assumed ? ["assumed_regime"] : [] };
}

interface Segment {
  t: number;
  q: number;
  v: number;
  a: number;
  end: number;
}
export interface Motion {
  duration: number;
  events: Event[];
  initialAcceleration: number;
  at(t: number): { q: number; v: number; a: number };
}
function root(q: number, v: number, a: number, target: number): number {
  if (Math.abs(a) < 1e-12)
    return Math.abs(v) < 1e-12
      ? Infinity
      : (target - q) / v > 1e-9
        ? (target - q) / v
        : Infinity;
  const disc = v * v + 2 * a * (target - q);
  if (disc < 0) return Infinity;
  return Math.min(
    ...[(-v - Math.sqrt(disc)) / a, (-v + Math.sqrt(disc)) / a].filter(
      (t) => t > 1e-9,
    ),
    Infinity,
  );
}
/** Piecewise exact Coulomb motion: reverse/stick at v=0, never friction in a guessed direction. */
export function motion(
  q0: number,
  v0: number,
  drive: number,
  kinetic: number,
  staticLimit: number,
  inertia: number,
  low: number,
  high: number,
  refs: string[],
  horizon = 8,
  lowEvent = "bottom_contact",
  highEvent = "top_contact",
): Motion {
  if (
    kinetic < 0 ||
    staticLimit < 0 ||
    kinetic > staticLimit + 1e-10 ||
    !(low < high) ||
    q0 < low - 1e-8 ||
    q0 > high + 1e-8
  )
    throw new Error("invalid_motion_bounds_or_friction");
  const segments: Segment[] = [];
  const events: Event[] = [];
  let t = 0,
    q = q0,
    v = v0,
    terminal = false;
  while (t < horizon - 1e-9 && segments.length < 8) {
    const sign =
      Math.abs(v) > 1e-10
        ? Math.sign(v)
        : Math.abs(drive) <= staticLimit + 1e-10
          ? 0
          : Math.sign(drive);
    const a = sign ? (drive - sign * kinetic) / inertia : 0;
    if (
      (q <= low + 1e-9 && (v < 0 || (v === 0 && a < 0))) ||
      (q >= high - 1e-9 && (v > 0 || (v === 0 && a > 0)))
    ) {
      events.push({
        time: t,
        type: q <= low + 1e-9 ? lowEvent : highEvent,
        refs,
      });
      terminal = true;
      break;
    }
    const stop = a * v < -1e-12 ? -v / a : Infinity;
    const hitLow = root(q, v, a, low),
      hitHigh = root(q, v, a, high);
    const delta = Math.min(horizon - t, stop, hitLow, hitHigh);
    segments.push({ t, q, v, a, end: t + delta });
    q += v * delta + 0.5 * a * delta * delta;
    v += a * delta;
    t += delta;
    if (delta === hitLow || delta === hitHigh) {
      q = delta === hitLow ? low : high;
      events.push({
        time: t,
        type: delta === hitLow ? lowEvent : highEvent,
        refs,
      });
      v = 0;
      terminal = true;
      break;
    }
    if (delta === stop) {
      v = 0;
      events.push({ time: t, type: "turn_or_stick", refs });
    }
  }
  const duration = terminal ? t : horizon;
  const finalQ = q;
  return {
    duration,
    events,
    initialAcceleration: segments[0]?.a ?? 0,
    at(time) {
      if (terminal && time >= duration - 1e-10)
        return { q: finalQ, v: 0, a: 0 };
      const seg =
        [...segments].reverse().find((s) => s.t <= time + 1e-10) ?? segments[0];
      if (!seg) return { q: q0, v: 0, a: 0 };
      const dt = Math.max(0, Math.min(time, seg.end) - seg.t);
      return {
        q: seg.q + seg.v * dt + 0.5 * seg.a * dt * dt,
        v: seg.v + seg.a * dt,
        a: seg.a,
      };
    },
  };
}
