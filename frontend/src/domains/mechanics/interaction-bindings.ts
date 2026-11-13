import type { Scene, Binding } from "./types";

export function scalarVelocityPath(s: Scene, path: string) {
  if (!/^bodies\.[^.]+\.initial\.velocity\.x$/.test(path)) return path;
  const name =
    s.archetype === "projectile"
      ? "launch_speed"
      : [
            "incline_block",
            "spring_mass",
            "atwood",
            "table_pulley",
            "incline_pulley",
          ].includes(s.archetype)
        ? "initial_speed"
        : "";
  return name && s.params[name] ? `params.${name}` : path;
}

/** V1 migration: add missing initial controls and map unused velocity ownership.
 * Preserve source geometry and original observations; apply equally to both saved
 * snapshots before validating project consistency. */
export function interactionBindings(scene: Scene): Scene {
  const s = structuredClone(scene);
  for (const body of s.bodies) {
    const path = `bodies.${body.id}.initial.velocity.x`,
      canonical = scalarVelocityPath(s, path);
    if (canonical === path) continue;
    const key = canonical.split(".")[1],
      observed = body.initial.velocity.x;
    if (observed.status === "user" && s.params[key].status !== "user")
      s.params[key] = structuredClone(observed);
    else if (
      observed.status === "user" &&
      observed.number !== s.params[key].number
    ) {
      s.params[`unplaced_legacy_${body.id}`] ??= structuredClone(observed);
      if (
        !s.warnings.some(
          (w) => w.code === "legacy_velocity_conflict" && w.ref === body.id,
        )
      )
        s.warnings.push({
          code: "legacy_velocity_conflict",
          ref: body.id,
          message_key: "mech.legacy_velocity_conflict",
        });
    }
  }
  for (const label of s.annotations)
    if (label.bound_to) label.bound_to = scalarVelocityPath(s, label.bound_to);
  for (const binding of s.bindings) {
    binding.path = scalarVelocityPath(s, binding.path);
    binding.labels = [
      ...new Set([
        ...binding.labels,
        ...s.annotations
          .filter((a) => a.bound_to === binding.path)
          .map((a) => a.id),
      ]),
    ];
  }
  const add = (
    path: string,
    id: string,
    min: number,
    max: number,
    handle: string | null,
    unit = "m",
  ) => {
    if (s.bindings.some((b) => b.path === path)) return;
    while (s.bindings.some((b) => b.id === id)) id += "_initial";
    const binding: Binding = {
      id,
      path,
      class: "initial",
      labels: s.annotations.filter((a) => a.bound_to === path).map((a) => a.id),
      control: { min, max, step: 0.01, unit, locked: false },
      handle,
      drives: ["layout", "solver", "label"],
    };
    s.bindings.push(binding);
  };
  if (s.archetype === "pendulum" && s.params.angular_speed)
    add("params.angular_speed", "angular_speed", -10, 10, null, "rad/s");
  if (["atwood", "table_pulley", "incline_pulley"].includes(s.archetype)) {
    s.params.initial_displacement ??= {
      number: 0,
      unit: "m",
      status: "assumed",
      source: "prior",
      confidence: 0,
    };
    add("params.initial_displacement", "displacement", -50, 50, "pulley_0");
  }
  if (s.archetype === "collision_1d") {
    for (const body of s.bodies)
      add(
        `bodies.${body.id}.initial.position.x`,
        `x_${body.id}`,
        0,
        s.image.width / s.frame.px_per_m.number!,
        `collision_${body.id}`,
      );
  }
  return s;
}
