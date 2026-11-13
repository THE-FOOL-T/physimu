import schema from "../../../../docs/mechanics/schema.json";
import type { Scene, Value } from "./types";

type Rule = Record<string, any>;
/** Small, dependency-free interpreter for the generated schema's vocabulary.
 * Reject unsupported assertion keywords rather than silently accepting them. */
export function validateSchema(
  input: unknown,
  rule: Rule = schema,
  path = "scene",
): void {
  if (rule.$ref) {
    const name = rule.$ref.split("/").at(-1)!;
    validateSchema(input, (schema.$defs as Record<string, Rule>)[name], path);
    return;
  }
  const annotations = new Set([
    "title",
    "description",
    "default",
    "$defs",
    "$schema",
  ]);
  const supported = new Set([
    "anyOf",
    "const",
    "enum",
    "type",
    "properties",
    "required",
    "additionalProperties",
    "items",
    "prefixItems",
    "minItems",
    "maxItems",
    "minimum",
    "maximum",
    "exclusiveMinimum",
    "exclusiveMaximum",
    "pattern",
  ]);
  for (const key of Object.keys(rule))
    if (!annotations.has(key) && !supported.has(key))
      throw new Error(`Unsupported schema keyword ${key}`);
  if (rule.anyOf) {
    if (
      !rule.anyOf.some((branch: Rule) => {
        try {
          validateSchema(input, branch, path);
          return true;
        } catch {
          return false;
        }
      })
    )
      throw new Error(`${path}: no matching type`);
    return;
  }
  if ("const" in rule && input !== rule.const)
    throw new Error(`${path}: invalid constant`);
  if (rule.enum && !rule.enum.includes(input))
    throw new Error(`${path}: invalid enum`);
  const type = rule.type;
  const valid =
    type === undefined ||
    (type === "null"
      ? input === null
      : type === "array"
        ? Array.isArray(input)
        : type === "object"
          ? input !== null && typeof input === "object" && !Array.isArray(input)
          : type === "number"
            ? typeof input === "number" && Number.isFinite(input)
            : type === "integer"
              ? typeof input === "number" && Number.isSafeInteger(input)
              : typeof input === type);
  if (!valid) throw new Error(`${path}: expected ${type}`);
  if (typeof input === "number") {
    for (const [key, fails] of [
      ["minimum", input < rule.minimum],
      ["maximum", input > rule.maximum],
      ["exclusiveMinimum", input <= rule.exclusiveMinimum],
      ["exclusiveMaximum", input >= rule.exclusiveMaximum],
    ] as const)
      if (key in rule && fails) throw new Error(`${path}: ${key}`);
  }
  if (
    typeof input === "string" &&
    rule.pattern &&
    !new RegExp(rule.pattern).test(input)
  )
    throw new Error(`${path}: pattern`);
  if (Array.isArray(input)) {
    if (
      input.length < (rule.minItems ?? 0) ||
      input.length > (rule.maxItems ?? Infinity)
    )
      throw new Error(`${path}: array length`);
    input.forEach((item, i) =>
      validateSchema(
        item,
        rule.prefixItems?.[i] ?? rule.items ?? {},
        `${path}[${i}]`,
      ),
    );
  }
  if (input !== null && typeof input === "object" && !Array.isArray(input)) {
    const object = input as Record<string, unknown>;
    for (const key of rule.required ?? [])
      if (!(key in object)) throw new Error(`${path}.${key}: required`);
    for (const [key, item] of Object.entries(object)) {
      if (rule.properties?.[key])
        validateSchema(item, rule.properties[key], `${path}.${key}`);
      else if (rule.additionalProperties === false)
        throw new Error(`${path}.${key}: extra field`);
      else if (typeof rule.additionalProperties === "object")
        validateSchema(item, rule.additionalProperties, `${path}.${key}`);
    }
  }
}

export function atPath(scene: Scene, path: string): unknown {
  let current: any = scene;
  for (const part of path.split(".")) {
    current = Array.isArray(current)
      ? current.find((item) => item.id === part)
      : current?.[part];
    if (current === undefined || current === null)
      throw new Error(`Unresolved path: ${path}`);
  }
  return current;
}
export function valueAt(scene: Scene, path: string): Value {
  const value = atPath(scene, path) as Value;
  if (
    !value ||
    typeof value !== "object" ||
    !("number" in value) ||
    !("unit" in value)
  )
    throw new Error(`Not a Value: ${path}`);
  return value;
}
export function parseScene(input: unknown): Scene {
  validateSchema(input);
  const scene = structuredClone(input) as Scene;
  const unit = (value: Value | null, expected: string) => {
    if (value !== null && value.unit !== expected)
      throw new Error(`Expected SI unit ${expected}`);
  };
  unit(scene.frame.px_per_m, "px/m");
  unit(scene.constants.g, "m/s^2");
  for (const b of scene.bodies) {
    unit(b.mass, "kg");
    unit(b.radius_m, "m");
    unit(b.initial.position.x, "m");
    unit(b.initial.position.y, "m");
    unit(b.initial.velocity.x, "m/s");
    unit(b.initial.velocity.y, "m/s");
  }
  for (const s of scene.surfaces) {
    unit(s.angle_deg, "deg");
    unit(s.length_m, "m");
    unit(s.mu_s, "1");
    unit(s.mu_k, "1");
  }
  for (const l of scene.links) {
    unit(l.length_m, "m");
    unit(l.rest_length_m, "m");
    unit(l.k, "N/m");
    unit(l.damping, scene.archetype === "pendulum" ? "1/s" : "kg/s");
  }
  scene.pulleys.forEach((p) => unit(p.mass, "kg"));
  scene.forces.forEach((f) => unit(f.magnitude, "N"));
  const units: Record<string, string> = {
    launch_speed: "m/s",
    launch_angle: "deg",
    launch_height: "m",
    start_position: "m",
    initial_speed: "m/s",
    applied_force: "N",
    release_angle: "deg",
    angular_speed: "rad/s",
    initial_stretch: "m",
    vertical: "1",
    restitution: "1",
  };
  for (const [key, value] of Object.entries(scene.params))
    if (key in units) unit(value, units[key]);
  const groups = [
    scene.bodies,
    scene.surfaces,
    scene.links,
    scene.pulleys,
    scene.forces,
    scene.annotations,
  ];
  const items = groups.flat();
  const ids = new Set(items.map((item) => item.id));
  if (items.some((item) => !item.id) || ids.size !== items.length)
    throw new Error("Nonunique object ids");
  const requireRef = (ref: string | null, allowed = ids) => {
    if (ref !== null && !allowed.has(ref))
      throw new Error(`Unresolved reference: ${ref}`);
  };
  const annotations = new Set(scene.annotations.map((item) => item.id));
  const surfaces = new Set(scene.surfaces.map((item) => item.id));
  for (const body of scene.bodies) {
    requireRef(body.on_surface, surfaces);
    body.label_ids.forEach((id) => requireRef(id, annotations));
    if (body.bbox[0] >= body.bbox[2] || body.bbox[1] >= body.bbox[3])
      throw new Error("Invalid bbox");
  }
  for (const link of scene.links) {
    requireRef(link.a.ref);
    requireRef(link.b.ref);
  }
  for (const force of scene.forces)
    requireRef(force.body, new Set(scene.bodies.map((b) => b.id)));
  for (const annotation of scene.annotations) {
    requireRef(annotation.text_id, annotations);
    if (annotation.bound_to) atPath(scene, annotation.bound_to);
  }
  scene.repairs.forEach((r) => requireRef(r.surface_or_line_id));
  scene.constraints.forEach((c) => c.refs.forEach((ref) => requireRef(ref)));
  for (const c of scene.constraints.filter((c) => c.type === "after_velocity"))
    for (const [ref, value] of Object.entries(c.values)) {
      requireRef(ref, new Set(scene.bodies.map((b) => b.id)));
      unit(value, "m/s");
    }
  scene.warnings.forEach((w) => requireRef(w.ref));
  if (new Set(scene.bindings.map((b) => b.id)).size !== scene.bindings.length)
    throw new Error("Nonunique binding ids");
  for (const b of scene.bindings) {
    const value = valueAt(scene, b.path);
    if (
      b.control.min >= b.control.max ||
      b.control.unit !== value.unit ||
      (b.class === "geometry" && !b.control.locked)
    )
      throw new Error("Invalid binding control");
    b.labels.forEach((ref) => requireRef(ref, annotations));
  }
  if (scene.frame.px_per_m.number !== null && scene.frame.px_per_m.number <= 0)
    throw new Error("Invalid scale");
  const known = [
    new Set(["block", "ball", "bob", "cart"]),
    new Set(["incline", "floor", "wall", "ceiling"]),
    new Set(["rope", "rod", "spring"]),
    new Set(["dimension", "angle_arc", "label", "axis", "ground_hatch"]),
  ];
  [scene.bodies, scene.surfaces, scene.links, scene.annotations].forEach(
    (group, i) =>
      group.forEach((item) => {
        if (
          !known[i].has(item.type) &&
          !scene.warnings.some(
            (w) => w.code === "unknown_type" && w.ref === item.id,
          )
        )
          scene.warnings.push({
            code: "unknown_type",
            ref: item.id,
            message_key: "mech.unknown_type",
          });
      }),
  );
  return scene;
}
