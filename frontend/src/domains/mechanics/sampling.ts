import { bracket } from "../../shell";
import type { Trajectory, State, XY } from "./types";

export function sample(run: Trajectory, t: number): State {
  if (!run.states.length) throw new Error("Unsupported trajectory");
  const { a, b, alpha } = bracket(
    run.times,
    t,
    run.events.map((e) => e.time),
  );
  const left = run.states[a],
    right = run.states[b],
    mix = (x: number, y: number) => x + (y - x) * alpha;
  const vectors = (key: "positions" | "velocities") =>
    Object.fromEntries(
      Object.keys(left[key]).map((id) => {
        const l = left[key][id],
          r = right[key][id];
        return [id, { x: mix(l.x, r.x), y: mix(l.y, r.y) }];
      }),
    );
  return {
    t,
    positions: vectors("positions"),
    velocities: vectors("velocities"),
    kinetic: mix(left.kinetic, right.kinetic),
    potential: mix(left.potential, right.potential),
    momentum: {
      x: mix(left.momentum.x, right.momentum.x),
      y: mix(left.momentum.y, right.momentum.y),
    } as XY,
    scalars: Object.fromEntries(
      Object.keys(left.scalars).map((k) => [
        k,
        mix(left.scalars[k], right.scalars[k]),
      ]),
    ),
  };
}
