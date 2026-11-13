import type { Scene, Trajectory } from "./types";
import { BindingEngine } from "./bindings";
import { sample } from "./sampling";

/** Fixed physical-space protocol. This calls the product solvers, never a second solver. */
export function compareTrajectories(
  prediction: Scene,
  gold: Scene,
  bodyMap: Record<string, string>,
) {
  if (prediction.meta.provenance === "unsupported")
    return {
      simulation_produced: false,
      trajectory_correct: false,
      maximum_displacement_error_m: null,
    };
  let actual: Trajectory;
  try {
    actual = new BindingEngine(prediction).trajectory;
  } catch {
    return {
      simulation_produced: false,
      trajectory_correct: false,
      maximum_displacement_error_m: null,
    };
  }
  if (!actual.supported || !actual.states.length)
    return {
      simulation_produced: false,
      trajectory_correct: false,
      maximum_displacement_error_m: null,
      simulation_reason: actual.reason ?? "no_states",
    };
  let expected: Trajectory;
  try {
    expected = new BindingEngine(gold).trajectory;
  } catch {
    throw new Error("Gold solver failed; repair/review gold before evaluation");
  }
  if (!expected.supported || !expected.states.length)
    throw new Error("Gold solver is unsupported");
  const ids = gold.bodies.map((b) => b.id);
  if (
    prediction.archetype !== gold.archetype ||
    ids.length !== prediction.bodies.length ||
    ids.some((id) => !bodyMap[id])
  )
    return {
      simulation_produced: true,
      trajectory_correct: false,
      maximum_displacement_error_m: null,
    };
  const horizon = Math.min(5, actual.duration, expected.duration);
  let error = 0;
  for (let i = 0; i <= 120; i++) {
    const a = sample(actual, (horizon * i) / 120),
      b = sample(expected, (horizon * i) / 120);
    for (const id of ids) {
      const p = bodyMap[id],
        a0 = actual.states[0].positions[p],
        b0 = expected.states[0].positions[id];
      if (!a.positions[p] || !b.positions[id] || !a0 || !b0)
        throw new Error("Solver body-map mismatch");
      error = Math.max(
        error,
        Math.hypot(
          a.positions[p].x - a0.x - b.positions[id].x + b0.x,
          a.positions[p].y - a0.y - b.positions[id].y + b0.y,
        ),
      );
    }
  }
  const sameEnd =
    Math.abs(Math.min(5, actual.duration) - Math.min(5, expected.duration)) <=
    0.02;
  return {
    simulation_produced: true,
    trajectory_correct: sameEnd && error <= 0.05,
    maximum_displacement_error_m: error,
  };
}
