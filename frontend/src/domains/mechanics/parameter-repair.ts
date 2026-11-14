import type { Scene } from "./types";
import { valueAt } from "./validate";
import { userValue } from "./authoring";

/** First measured length calibrates native pixels. Later length edits are overrides. */
export function repairMissingLength(
  scene: Scene,
  path: string,
  number: number,
) {
  const link = scene.links.find((l) => path === `links.${l.id}.length_m`);
  if (
    scene.archetype !== "pendulum" ||
    !link ||
    valueAt(scene, path).number !== null
  )
    throw new Error("mech.invalid_parameter_repair");
  if (!Number.isFinite(number) || number <= 0)
    throw new Error("mech.invalid_parameter_repair");
  const body = scene.bodies.find((b) =>
    [link.a.ref, link.b.ref].includes(b.id),
  )!;
  const pivot = link.a.ref === body.id ? link.b.point : link.a.point;
  const pixels = Math.hypot(
    body.anchor[0] - pivot[0],
    body.anchor[1] - pivot[1],
  );
  const oldScale = scene.frame.px_per_m.number!;
  const newScale = pixels / number;
  if (!pixels || !oldScale) throw new Error("mech.invalid_parameter_repair");
  Object.assign(valueAt(scene, path), userValue(number, "m"));
  Object.assign(scene.frame.px_per_m, userValue(newScale, "px/m"));
  for (const axis of ["x", "y"] as const)
    body.initial.position[axis].number =
      (body.initial.position[axis].number! * oldScale) / newScale;
  if (
    body.radius_m?.number !== null &&
    body.radius_m &&
    !["user", "ocr", "vlm"].includes(body.radius_m.source)
  )
    body.radius_m.number = (body.radius_m.number! * oldScale) / newScale;
  const binding = scene.bindings.find((b) => b.path === path)!;
  binding.control.min = Math.min(binding.control.min, number);
  binding.control.max = Math.max(binding.control.max, number);
  scene.warnings = scene.warnings.filter((w) => w.code !== "missing_length");
}
