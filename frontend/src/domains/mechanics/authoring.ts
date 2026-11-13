import type { Scene, Point, BBox, Value, ArchetypeId } from "./types";
import { parseScene, valueAt } from "./validate";

export const userValue = (number: number | null, unit: string): Value => ({
  number,
  unit,
  status: "user",
  source: "user",
  confidence: 1,
});
const assumedValue = (number: number, unit: string): Value => ({
  number,
  unit,
  status: "assumed",
  source: "prior",
  confidence: 0,
});

/** An explicit authoring action, never an automatic detector substitute. */
export function addBody(s: Scene) {
  const ids = new Set(objects(s).map((o) => o.id));
  let n = 1;
  while (ids.has(`manual_body_${n}`)) n++;
  const id = `manual_body_${n}`,
    size = Math.min(40, s.image.width / 4, s.image.height / 4);
  const x = size,
    y = size,
    S = s.frame.px_per_m.number ?? 100;
  s.bodies.push({
    id,
    type: "block",
    bbox: [x, y, x + size, y + size],
    mask: [
      [x, y],
      [x + size, y],
      [x + size, y + size],
      [x, y + size],
    ],
    anchor: [x + size / 2, y + size / 2],
    label_ids: [],
    mass: assumedValue(1, "kg"),
    radius_m: null,
    on_surface: null,
    initial: {
      position: {
        x: assumedValue((x + size / 2) / S, "m"),
        y: assumedValue((y + size / 2) / S, "m"),
      },
      velocity: { x: assumedValue(0, "m/s"), y: assumedValue(0, "m/s") },
    },
  });
  s.bindings.push({
    id: `mass_${id}`,
    path: `bodies.${id}.mass`,
    class: "physics",
    control: { min: 0.01, max: 100, step: 0.01, unit: "kg", locked: false },
    labels: [],
    handle: null,
    drives: ["layout", "solver", "label"],
  });
  return id;
}
const set = (v: Value, n: number) => Object.assign(v, userValue(n, v.unit));
const move = (p: Point, d: Point): Point => [p[0] + d[0], p[1] + d[1]];
export function objects(s: Scene) {
  return [
    ...s.bodies,
    ...s.surfaces,
    ...s.links,
    ...s.pulleys,
    ...s.annotations,
  ];
}
export function nameOf(s: Scene, id: string) {
  return s.annotations.find((a) => a.id === `name_${id}`)?.geometry.text ?? id;
}
export function rename(s: Scene, id: string, text: string) {
  let a = s.annotations.find((a) => a.id === `name_${id}`);
  if (!a) {
    a = {
      id: `name_${id}`,
      type: "label",
      geometry: {
        points: [],
        bbox: null,
        text: null,
        radius_px: null,
        start_deg: null,
        end_deg: null,
      },
      text_id: null,
      bound_to: null,
    };
    s.annotations.push(a);
  }
  a.geometry.text = text.slice(0, 120);
}
/** Explicit manual template, never image extraction. Physical priors remain assumed. */
export function stencil(template: Scene, image: Scene["image"]): Scene {
  const s = structuredClone(template),
    factor = Math.min(
      image.width / s.image.width,
      image.height / s.image.height,
    );
  const dx = (image.width - s.image.width * factor) / 2,
    dy = (image.height - s.image.height * factor) / 2;
  const point = (p: Point): Point => [p[0] * factor + dx, p[1] * factor + dy];
  const box = (b: BBox): BBox => [
    ...point([b[0], b[1]]),
    ...point([b[2], b[3]]),
  ];
  s.bodies.forEach((b) => {
    b.anchor = point(b.anchor);
    b.bbox = box(b.bbox);
    b.mask = b.mask.map(point);
    b.label_ids = [];
  });
  s.surfaces.forEach((v) => (v.polyline = v.polyline.map(point)));
  s.links.forEach((l) => {
    l.a.point = point(l.a.point);
    l.b.point = point(l.b.point);
    l.polyline = l.polyline.map(point);
  });
  s.pulleys.forEach((p) => {
    p.center = point(p.center);
    p.radius_px *= factor;
  });
  s.forces = [];
  // Preserve only reference anchors, no synthetic printed labels/repairs.
  s.annotations = s.annotations.filter((a) => a.type === "axis");
  s.annotations.forEach((a) => {
    a.geometry.points = a.geometry.points.map(point);
    if (a.geometry.bbox) a.geometry.bbox = box(a.geometry.bbox);
  });
  s.bindings.forEach((b) => (b.labels = []));
  s.repairs = [];
  s.warnings = [];
  s.image = structuredClone(image);
  s.frame.px_per_m.number! *= factor;
  function priors(v: unknown) {
    if (!v || typeof v !== "object") return;
    if ("number" in v && "unit" in v)
      Object.assign(v, { status: "assumed", source: "prior", confidence: 0 });
    else Object.values(v).forEach(priors);
  }
  priors(s);
  s.meta = {
    language: "en",
    style: "unknown",
    provenance: "authored",
    region: null,
  };
  return parseScene(s);
}
export function emptyScene(image: Scene["image"]): Scene {
  const prior = (n: number, u: string): Value => ({
    number: n,
    unit: u,
    status: "assumed",
    source: "prior",
    confidence: 0,
  });
  return parseScene({
    version: 1,
    domain: "mechanics",
    image,
    archetype: "unsupported",
    frame: {
      gravity: [0, 1],
      px_per_m: prior(100, "px/m"),
      paper_color: "#ffffff",
      ink_color: "#202c3a",
      stroke_px: 2,
    },
    bodies: [],
    surfaces: [],
    links: [],
    pulleys: [],
    forces: [],
    annotations: [],
    repairs: [],
    constants: { g: prior(9.81, "m/s^2") },
    params: {},
    bindings: [],
    constraints: [],
    warnings: [],
    meta: {
      language: "en",
      style: "unknown",
      provenance: "unsupported",
      region: null,
    },
  });
}
export interface Handle {
  id: string;
  object: string;
  point: Point;
  kind: "body" | "surface" | "endpoint" | "pulley" | "pivot";
  index?: number;
  end?: "a" | "b";
}
export function handles(s: Scene): Handle[] {
  return [
    ...s.bodies.map((b) => ({
      id: b.id,
      object: b.id,
      point: b.anchor,
      kind: "body" as const,
    })),
    ...s.surfaces.flatMap((v) =>
      v.polyline.map((p, i) => ({
        id: `${v.id}:${i}`,
        object: v.id,
        point: p,
        kind: "surface" as const,
        index: i,
      })),
    ),
    ...s.pulleys.map((p) => ({
      id: p.id,
      object: p.id,
      point: p.center,
      kind: "pulley" as const,
    })),
    ...s.links.flatMap((l) =>
      (["a", "b"] as const).map((end) => ({
        id: `${l.id}:${end}`,
        object: l.id,
        point: l[end].point,
        kind: "endpoint" as const,
        end,
      })),
    ),
    ...s.annotations
      .filter((a) => a.type === "axis" && a.geometry.points.length)
      .map((a) => ({
        id: a.id,
        object: a.id,
        point: a.geometry.points[0],
        kind: "pivot" as const,
      })),
  ];
}
function moveBody(s: Scene, id: string, point: Point) {
  const b = s.bodies.find((b) => b.id === id)!;
  const d: Point = [point[0] - b.anchor[0], point[1] - b.anchor[1]];
  b.anchor = point;
  b.mask = b.mask.map((p) => move(p, d));
  b.bbox = [
    b.bbox[0] + d[0],
    b.bbox[1] + d[1],
    b.bbox[2] + d[0],
    b.bbox[3] + d[1],
  ];
  for (const l of s.links)
    for (const end of ["a", "b"] as const)
      if (l[end].ref === id) {
        l[end].point = move(l[end].point, d);
        l.polyline[end === "a" ? 0 : l.polyline.length - 1] = l[end].point;
      }
}
/** Source calibration is changed only by a deliberate authoring edit, never a slider. */
export function calibrate(s: Scene) {
  const S = s.frame.px_per_m.number;
  if (!S || S <= 0) return;
  const b = s.bodies[0],
    l = s.links[0],
    sf = s.surfaces.find((v) => v.type === "incline");
  if (s.archetype === "collision_1d") {
    for (const body of s.bodies) {
      set(body.initial.position.x, body.anchor[0] / S);
      set(body.initial.position.y, body.anchor[1] / S);
    }
  }
  if (sf && sf.polyline.length >= 2) {
    const a = sf.polyline[0],
      z = sf.polyline.at(-1)!,
      dx = z[0] - a[0],
      dy = a[1] - z[1];
    if (sf.angle_deg) set(sf.angle_deg, (Math.atan2(dy, dx) * 180) / Math.PI);
    if (sf.length_m) set(sf.length_m, Math.hypot(dx, dy) / S);
    if (s.archetype === "incline_block" && b && s.params.start_position)
      set(
        s.params.start_position,
        ((b.anchor[0] - a[0]) * dx + (a[1] - b.anchor[1]) * dy) /
          Math.hypot(dx, dy) /
          S,
      );
  }
  if (s.archetype === "pendulum" && b && l) {
    const dx = b.anchor[0] - l.a.point[0],
      dy = b.anchor[1] - l.a.point[1];
    l.b.point = [...b.anchor];
    l.polyline = [l.a.point, l.b.point];
    if (l.length_m) set(l.length_m, Math.hypot(dx, dy) / S);
    set(s.params.release_angle, (Math.atan2(dx, dy) * 180) / Math.PI);
    set(b.initial.position.x, dx / S);
    set(b.initial.position.y, dy / S);
  }
  if (s.archetype === "spring_mass" && b && l) {
    const vertical = !!s.params.vertical?.number;
    const half = (vertical ? b.bbox[3] - b.bbox[1] : b.bbox[2] - b.bbox[0]) / 2;
    const distance =
      (vertical ? b.anchor[1] - l.a.point[1] : b.anchor[0] - l.a.point[0]) -
      half;
    set(
      s.params.initial_stretch,
      distance / S - (l.rest_length_m?.number ?? 0),
    );
    l.b.point = vertical
      ? [b.anchor[0], b.anchor[1] - half]
      : [b.anchor[0] - half, b.anchor[1]];
    l.polyline = [l.a.point, l.b.point];
  }
  // Values outside the old stencil limits remain editable within the drawn scene.
  for (const binding of s.bindings) {
    const v = valueAt(s, binding.path).number;
    if (v !== null) {
      binding.control.min = Math.min(binding.control.min, v);
      binding.control.max = Math.max(binding.control.max, v);
    }
  }
}
export function moveHandle(s: Scene, h: Handle, p: Point) {
  p = [
    Math.max(0, Math.min(s.image.width, p[0])),
    Math.max(0, Math.min(s.image.height, p[1])),
  ];
  if (h.kind === "body") moveBody(s, h.object, p);
  if (h.kind === "surface")
    s.surfaces.find((v) => v.id === h.object)!.polyline[h.index!] = p;
  if (h.kind === "endpoint") {
    const l = s.links.find((l) => l.id === h.object)!;
    l[h.end!].point = p;
    l.polyline[h.end === "a" ? 0 : l.polyline.length - 1] = p;
    const axis = s.annotations.find(
      (a) => a.id === l[h.end!].ref && a.type === "axis",
    );
    if (axis) axis.geometry.points = [p];
  }
  if (h.kind === "pivot") {
    s.annotations.find((a) => a.id === h.object)!.geometry.points = [p];
    s.links.forEach((l) => {
      for (const end of ["a", "b"] as const)
        if (l[end].ref === h.object) {
          l[end].point = p;
          l.polyline[end === "a" ? 0 : l.polyline.length - 1] = p;
        }
    });
  }
  if (h.kind === "pulley") {
    const pulley = s.pulleys.find((v) => v.id === h.object)!,
      d: Point = [p[0] - pulley.center[0], p[1] - pulley.center[1]];
    pulley.center = p;
    s.links.forEach((l) => {
      l.polyline = l.polyline.map((v, i) =>
        i > 0 && i < l.polyline.length - 1 ? move(v, d) : v,
      );
    });
  }
  calibrate(s);
}
export function setBox(s: Scene, id: string, box: BBox) {
  if (
    box.some((n) => !Number.isFinite(n)) ||
    box[0] >= box[2] ||
    box[1] >= box[3]
  )
    throw new Error("mech.invalid_box");
  const b = s.bodies.find((b) => b.id === id)!;
  moveBody(s, id, [(box[0] + box[2]) / 2, (box[1] + box[3]) / 2]);
  b.bbox = box;
  b.mask = [
    [box[0], box[1]],
    [box[2], box[1]],
    [box[2], box[3]],
    [box[0], box[3]],
  ];
  calibrate(s);
}
export function attach(s: Scene, id: string, end: "a" | "b", ref: string) {
  const h = handles(s).find((h) => h.object === ref);
  if (!h) throw new Error("mech.invalid_attachment");
  const l = s.links.find((l) => l.id === id)!;
  l[end] = { ref, point: [...h.point] };
  l.polyline[end === "a" ? 0 : l.polyline.length - 1] = [...h.point];
  calibrate(s);
}
export function addLine(
  s: Scene,
  type: "rope" | "spring" | "incline" | "floor",
  a: Point,
  b: Point,
) {
  const used = new Set(objects(s).map((v) => v.id));
  let n = 1;
  while (used.has(`draw_${n}`)) n++;
  const id = `draw_${n}`;
  if (type === "floor" || type === "incline")
    s.surfaces.push({
      id,
      type,
      polyline: [a, b],
      angle_deg: type === "incline" ? userValue(30, "deg") : null,
      length_m: userValue(
        Math.hypot(b[0] - a[0], b[1] - a[1]) / (s.frame.px_per_m.number ?? 100),
        "m",
      ),
      mu_s: assumedValue(0, "1"),
      mu_k: assumedValue(0, "1"),
    });
  else {
    const refs = ([a, b] as Point[]).map((p, i) => {
      const body = s.bodies.find(
        (v) => Math.hypot(v.anchor[0] - p[0], v.anchor[1] - p[1]) < 50,
      );
      if (body) return body.id;
      const anchor = `${id}_${i}`;
      s.annotations.push({
        id: anchor,
        type: "axis",
        geometry: {
          points: [p],
          bbox: null,
          text: null,
          radius_px: null,
          start_deg: null,
          end_deg: null,
        },
        text_id: null,
        bound_to: null,
      });
      return anchor;
    });
    s.links.push({
      id,
      type,
      a: { ref: refs[0], point: a },
      b: { ref: refs[1], point: b },
      polyline: [a, b],
      length_m: userValue(
        Math.hypot(b[0] - a[0], b[1] - a[1]) / (s.frame.px_per_m.number ?? 100),
        "m",
      ),
      k: type === "spring" ? assumedValue(20, "N/m") : null,
      rest_length_m: type === "spring" ? assumedValue(0.5, "m") : null,
      coils: type === "spring" ? 8 : null,
      damping:
        type === "spring"
          ? assumedValue(0, s.archetype === "pendulum" ? "1/s" : "kg/s")
          : null,
    });
  }
  calibrate(s);
  return id;
}
export function assignValue(s: Scene, key: string, path: string) {
  const chip = s.params[key],
    target = valueAt(s, path);
  if (!key.startsWith("unplaced_") || !chip || target.unit !== chip.unit)
    throw new Error("mech.unit_mismatch");
  Object.assign(target, chip);
  delete s.params[key];
}
export function switchArchetype(s: Scene, id: ArchetypeId) {
  s.archetype = id;
  s.meta.provenance = id === "unsupported" ? "unsupported" : "authored";
  s.links.forEach((l) => {
    if (l.damping) l.damping.unit = id === "pendulum" ? "1/s" : "kg/s";
  });
  for (const binding of s.bindings)
    binding.control.unit = valueAt(s, binding.path).unit;
  s.warnings = s.warnings.filter((w) => w.code !== "unknown_type");
}
/** Every typed Value, including values without a default slider, is editable. */
export function valuePaths(s: Scene): string[] {
  const paths: string[] = [];
  function visit(v: unknown, path: string) {
    if (!v || typeof v !== "object") return;
    if ("number" in v && "unit" in v) paths.push(path);
    else if (Array.isArray(v))
      v.forEach((x) => {
        if (x && typeof x === "object" && "id" in x)
          visit(x, `${path}.${x.id}`);
      });
    else
      Object.entries(v).forEach(([k, x]) =>
        visit(x, path ? `${path}.${k}` : k),
      );
  }
  visit(s, "");
  return paths;
}
export interface EditState {
  scene: Scene;
  recognition?: Scene;
  overrides: Record<string, number>;
  unlocked: string[];
}
export function removeObject(s: Scene, id: string) {
  s.bodies = s.bodies.filter((v) => v.id !== id);
  s.surfaces = s.surfaces.filter((v) => v.id !== id);
  s.links = s.links.filter((v) => v.id !== id);
  s.pulleys = s.pulleys.filter((v) => v.id !== id);
  s.annotations = s.annotations.filter(
    (v) => v.id !== id && v.id !== `name_${id}`,
  );
  s.forces = s.forces.filter((v) => v.id !== id && v.body !== id);
  for (const body of s.bodies) {
    if (body.on_surface === id) body.on_surface = null;
    body.label_ids = body.label_ids.filter((v) =>
      s.annotations.some((a) => a.id === v),
    );
  }
  for (const link of s.links)
    for (const end of ["a", "b"] as const)
      if (link[end].ref === id) {
        const name = `anchor_${link.id}_${end}`;
        link[end].ref = name;
        if (!s.annotations.some((a) => a.id === name))
          s.annotations.push({
            id: name,
            type: "axis",
            geometry: {
              points: [link[end].point],
              bbox: null,
              text: null,
              radius_px: null,
              start_deg: null,
              end_deg: null,
            },
            text_id: null,
            bound_to: null,
          });
      }
  const ids = new Set(objects(s).map((v) => v.id));
  s.repairs = s.repairs.filter((r) => ids.has(r.surface_or_line_id));
  s.constraints = s.constraints.filter((c) =>
    c.refs.every((ref) => ids.has(ref)),
  );
  s.warnings = s.warnings.filter((w) => w.ref === null || ids.has(w.ref));
  s.bindings = s.bindings.filter((b) => {
    try {
      valueAt(s, b.path);
      b.labels = b.labels.filter((v) => ids.has(v));
      return true;
    } catch {
      return false;
    }
  });
  s.annotations.forEach((a) => {
    if (a.text_id && !ids.has(a.text_id)) a.text_id = null;
    if (a.bound_to) {
      try {
        valueAt(s, a.bound_to);
      } catch {
        a.bound_to = null;
      }
    }
  });
}
/** Same bounded before/after transaction pattern as the circuit History; image stays outside. */
export class SceneHistory {
  private past: { before: EditState; after: EditState }[] = [];
  private future: { before: EditState; after: EditState }[] = [];
  push(before: EditState, after: EditState) {
    if (JSON.stringify(before) === JSON.stringify(after)) return;
    this.past.push(structuredClone({ before, after }));
    if (this.past.length > 80) this.past.shift();
    this.future = [];
  }
  undo() {
    const item = this.past.pop();
    if (!item) return null;
    this.future.push(item);
    return structuredClone(item.before);
  }
  redo() {
    const item = this.future.pop();
    if (!item) return null;
    this.past.push(item);
    return structuredClone(item.after);
  }
  get canUndo() {
    return this.past.length > 0;
  }
  get canRedo() {
    return this.future.length > 0;
  }
}
