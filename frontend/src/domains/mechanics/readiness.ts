import type { Scene, Trajectory } from "./types";
import { valueAt } from "./validate";

export type ReadinessStatus =
  | "analyzing"
  | "needs_model"
  | "needs_review"
  | "ready"
  | "unsupported";
export function readiness(
  scene: Scene,
  run: Trajectory,
  analyzing = false,
): ReadinessStatus {
  if (analyzing) return "analyzing";
  if (
    scene.warnings.some((w) => w.code === "weights_unavailable") &&
    scene.archetype === "unsupported"
  )
    return "needs_model";
  if (!run.supported)
    return scene.archetype !== "unsupported" &&
      scene.warnings.some((w) =>
        [
          "missing_mass",
          "missing_length",
          "invalid_mass",
          "unresolved_parameter",
        ].includes(w.code),
      )
      ? "needs_review"
      : "unsupported";
  if (
    scene.bindings.some((b) => valueAt(scene, b.path).status === "assumed") ||
    scene.frame.px_per_m.status === "assumed" ||
    scene.warnings.some(
      (w) => !["regime_stick", "regime_slide"].includes(w.code),
    ) ||
    Object.keys(scene.params).some((k) => k.startsWith("unplaced_"))
  )
    return "needs_review";
  return "ready";
}

/** Structural scene validation alone cannot establish these solver assumptions. */
export function topologyIssue(s: Scene): string | null {
  if (s.archetype === "unsupported") return "unsupported_archetype";
  const pairs = [
    "atwood",
    "table_pulley",
    "incline_pulley",
    "collision_1d",
  ].includes(s.archetype);
  if (s.bodies.length !== (pairs ? 2 : 1)) return "unsupported_body_count";
  for (const link of s.links)
    for (const endpoint of [link.a, link.b]) {
      const body = s.bodies.find((b) => b.id === endpoint.ref);
      if (
        body &&
        Math.hypot(
          endpoint.point[0] - body.anchor[0],
          endpoint.point[1] - body.anchor[1],
        ) >
          Math.hypot(body.bbox[2] - body.bbox[0], body.bbox[3] - body.bbox[1]) *
            0.65 +
            12
      )
        return "attachment_unreached";
    }
  if (["atwood", "table_pulley", "incline_pulley"].includes(s.archetype)) {
    if (s.pulleys.length !== 1) return "missing_pulley_objects";
    if (
      !s.links.some(
        (l) =>
          l.type === "rope" &&
          new Set([l.a.ref, l.b.ref]).size === 2 &&
          s.bodies.every((b) => [l.a.ref, l.b.ref].includes(b.id)),
      )
    )
      return "attachment_invalid";
  }
  if (
    s.archetype === "pendulum" &&
    !s.links.some(
      (l) =>
        ["rope", "rod"].includes(l.type) &&
        [l.a.ref, l.b.ref].includes(s.bodies[0].id) &&
        [l.a.ref, l.b.ref].includes("pivot"),
    )
  )
    return "attachment_invalid";
  if (
    s.archetype === "spring_mass" &&
    !s.links.some(
      (l) => l.type === "spring" && [l.a.ref, l.b.ref].includes(s.bodies[0].id),
    )
  )
    return "attachment_invalid";
  return null;
}
