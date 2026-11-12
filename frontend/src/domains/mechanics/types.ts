/** Canonical v1 documents include every default (Python serialization schema). */
export type Point = [number, number];
export type BBox = [number, number, number, number];
export interface Value {
  number: number | null;
  unit: string;
  status: "given" | "solved" | "assumed" | "user";
  source: "ocr" | "vlm" | "geometry" | "constraint" | "prior" | "user";
  confidence: number;
}
export interface Vector {
  x: Value;
  y: Value;
}
export interface Body {
  id: string;
  type: string;
  bbox: BBox;
  mask: Point[];
  anchor: Point;
  label_ids: string[];
  mass: Value;
  radius_m: Value | null;
  on_surface: string | null;
  initial: { position: Vector; velocity: Vector };
}
export interface Surface {
  id: string;
  type: string;
  polyline: Point[];
  angle_deg: Value | null;
  length_m: Value | null;
  mu_s: Value;
  mu_k: Value;
}
export interface Link {
  id: string;
  type: string;
  a: { ref: string; point: Point };
  b: { ref: string; point: Point };
  polyline: Point[];
  length_m: Value | null;
  k: Value | null;
  rest_length_m: Value | null;
  coils: number | null;
  damping: Value | null;
}
export interface Pulley {
  id: string;
  center: Point;
  radius_px: number;
  mass: Value | null;
}
export interface Annotation {
  id: string;
  type: string;
  geometry: {
    points: Point[];
    bbox: BBox | null;
    text: string | null;
    radius_px: number | null;
    start_deg: number | null;
    end_deg: number | null;
  };
  text_id: string | null;
  bound_to: string | null;
}
export interface Binding {
  id: string;
  path: string;
  class: "physics" | "initial" | "geometry";
  control: {
    min: number;
    max: number;
    step: number;
    unit: string;
    locked: boolean;
  };
  labels: string[];
  handle: string | null;
  drives: ("layout" | "solver" | "label")[];
}
export interface SceneWarning {
  code: string;
  ref: string | null;
  message_key: string;
}
export type ArchetypeId =
  | "projectile"
  | "incline_block"
  | "pendulum"
  | "spring_mass"
  | "atwood"
  | "table_pulley"
  | "incline_pulley"
  | "collision_1d"
  | "unsupported";
export interface Scene {
  version: 1;
  domain: "mechanics";
  image: { path: string; width: number; height: number };
  archetype: ArchetypeId;
  frame: {
    gravity: Point;
    px_per_m: Value;
    paper_color: string;
    ink_color: string;
    stroke_px: number;
  };
  bodies: Body[];
  surfaces: Surface[];
  links: Link[];
  pulleys: Pulley[];
  forces: {
    id: string;
    body: string;
    tail: Point;
    head: Point;
    magnitude: Value | null;
    label: string;
  }[];
  annotations: Annotation[];
  repairs: { surface_or_line_id: string; segments: Point[][] }[];
  constants: { g: Value };
  params: Record<string, Value>;
  bindings: Binding[];
  constraints: {
    type: string;
    refs: string[];
    values: Record<string, Value>;
  }[];
  warnings: SceneWarning[];
  meta: {
    language: "en" | "bn";
    style: "printed" | "handwritten" | "photo" | "unknown";
    provenance:
      | "extracted"
      | "partial"
      | "authored"
      | "unsupported"
      | "demo_fallback";
    region: BBox | null;
  };
}
export type Params = Record<string, number>;
export interface XY {
  x: number;
  y: number;
}
export interface State {
  t: number;
  positions: Record<string, XY>;
  velocities: Record<string, XY>;
  kinetic: number;
  potential: number;
  momentum: XY;
  scalars: Record<string, number>;
}
export interface Event {
  time: number;
  type: string;
  refs: string[];
}
export interface Trajectory {
  dt: number;
  times: number[];
  states: State[];
  events: Event[];
  duration: number;
  metrics: Record<string, number>;
  warnings: string[];
  supported: boolean;
  reason?: string;
}
export interface Drawables {
  bodies: { id: string; anchor: Point; rotation: number }[];
  links: { id: string; points: Point[] }[];
  pulleys: { id: string; center: Point; radius: number; rotation: number }[];
  surfaces: { id: string; points: Point[] }[];
  handles: { id: string; point: Point }[];
}
export interface ForceVector {
  body: string;
  label: string;
  vector: XY;
  component?: boolean;
}
export interface RegimeInfo {
  code: string;
  message: string;
  warnings: string[];
}
export interface ArchetypeModule {
  id: ArchetypeId;
  defaultBindings(scene: Scene): Binding[];
  solve(scene: Scene, params: Params): Trajectory;
  layout(scene: Scene, params: Params, state: State): Drawables;
  forces(scene: Scene, params: Params, state: State): ForceVector[];
  regime(scene: Scene, params: Params): RegimeInfo;
}
