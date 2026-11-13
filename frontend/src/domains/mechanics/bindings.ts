import type { Scene, Params, Point, Binding, Trajectory } from "./types";
import { archetypes } from "./archetypes";
import { read, scale, RAD } from "./archetypes/common";
import { valueAt } from "./validate";
import { pendulumPreview } from "./archetypes/pendulum";
import type { ParameterRow } from "../../shell";
import { interactionBindings } from "./interaction-bindings";
import { pulleyBounds } from "./archetypes/pulley";
import { topologyIssue } from "./readiness";

/** Original pixels/geometry stay immutable; user overrides are a separate document. */
export class BindingEngine {
  readonly original: Scene;
  readonly recognition: Scene;
  document: Scene;
  params: Params = {};
  unlocked = new Set<string>();
  trajectory: Trajectory;
  preview = false;
  constructor(scene: Scene, recognition = scene) {
    this.recognition = structuredClone(recognition);
    this.original = interactionBindings(scene);
    this.document = structuredClone(this.original);
    this.trajectory = this.solve();
  }
  get modified() {
    return this.original.bindings.some(
      (b) =>
        b.class === "geometry" &&
        b.path in this.params &&
        this.params[b.path] !== valueAt(this.original, b.path).number,
    );
  }
  solve() {
    const issue = topologyIssue(this.original);
    if (issue)
      return {
        ...archetypes.unsupported.solve(this.original, {}),
        reason: issue,
        warnings: [issue],
      };
    if (this.original.forces.some((f) => f.magnitude?.number !== 0))
      return {
        ...archetypes.unsupported.solve(this.original, {}),
        reason: "unsupported_applied_force",
        warnings: ["unsupported_applied_force"],
      };
    if (
      this.original.meta.provenance === "unsupported" &&
      !Object.keys(this.params).length
    )
      return archetypes.unsupported.solve(this.original, {});
    const run = archetypes[this.original.archetype].solve(
      this.original,
      this.solverParameters(),
    );
    if (run.supported) {
      if (this.original.meta.provenance === "unsupported")
        this.document.meta.provenance = "authored";
      this.document.warnings = this.document.warnings.filter(
        (w) =>
          ![
            "invalid_mass",
            "invalid_gravity",
            "invalid_friction",
            "invalid_link_value",
            "invalid_restitution",
            "invalid_launch",
            "unresolved_parameter",
          ].includes(w.code),
      );
    }
    return run;
  }
  /** A recognized tangential speed is converted through the calibrated length.
   * Editing omega explicitly takes ownership; otherwise changing length retains
   * the observed linear speed. Derived Values are reproducible, not saved overrides. */
  solverParameters(): Params {
    const s = this.original,
      p = { ...this.params };
    if (
      s.archetype === "pendulum" &&
      s.params.angular_speed?.source === "constraint" &&
      s.warnings.some((w) => w.code === "pendulum_speed_converted") &&
      !("params.angular_speed" in p)
    ) {
      const link = s.links[0],
        sourceL = link?.length_m?.number;
      if (sourceL && sourceL > 0 && s.params.angular_speed.number !== null) {
        const length = p[`links.${link.id}.length_m`] ?? sourceL;
        if (length > 0) {
          p["params.angular_speed"] =
            (s.params.angular_speed.number * sourceL) / length;
          Object.assign(this.document.params.angular_speed, {
            ...s.params.angular_speed,
            number: p["params.angular_speed"],
          });
        }
      }
    }
    return p;
  }
  binding(id: string) {
    const b = this.original.bindings.find((b) => b.id === id);
    if (!b) throw new Error(`Unknown binding ${id}`);
    return b;
  }
  limits(binding: Binding): [number, number] {
    const s = this.original,
      S = scale(s),
      c = binding.control;
    let min = c.min,
      max = c.max;
    if (
      s.archetype === "pendulum" &&
      binding.path === "params.angular_speed" &&
      s.params.angular_speed.source === "constraint"
    ) {
      const current = this.document.params.angular_speed.number;
      if (current !== null) {
        min = Math.min(min, current);
        max = Math.max(max, current);
      }
    }
    if (binding.path === "params.initial_displacement") {
      const bounds = pulleyBounds(s, this.params);
      min = Math.max(min, bounds.low);
      max = Math.min(max, bounds.high);
    }
    if (
      s.archetype === "collision_1d" &&
      binding.path.endsWith(".initial.position.x")
    ) {
      const index = s.bodies.findIndex(
        (b) => binding.path === `bodies.${b.id}.initial.position.x`,
      );
      const body = s.bodies[index],
        other = s.bodies[1 - index];
      const half = (body.bbox[2] - body.bbox[0]) / (2 * S);
      const gap = half + (other.bbox[2] - other.bbox[0]) / (2 * S);
      const x = read(s, this.params, `bodies.${other.id}.initial.position.x`);
      min = Math.max(min, half);
      max = Math.min(max, s.image.width / S - half);
      if (index === 0) max = Math.min(max, x - gap - 1e-8);
      else min = Math.max(min, x + gap + 1e-8);
    }
    const sf = s.surfaces.find((v) => v.type === "incline");
    if (binding.path === "params.start_position" && sf) {
      const L = read(s, this.params, `surfaces.${sf.id}.length_m`);
      const half =
        Math.hypot(
          s.bodies[0].mask[1][0] - s.bodies[0].mask[0][0],
          s.bodies[0].mask[1][1] - s.bodies[0].mask[0][1],
        ) /
        (2 * S);
      min = Math.max(min, half);
      max = Math.min(max, L - half);
    }
    if (s.archetype === "pendulum" && binding.path.endsWith("length_m")) {
      const pivot = s.links[0].a.point,
        b = s.bodies[0],
        radius = (b.bbox[2] - b.bbox[0]) / 2 + 8;
      max = Math.min(
        max,
        (Math.min(
          pivot[0],
          s.image.width - pivot[0],
          s.image.height - pivot[1],
        ) -
          radius) /
          S,
      );
      // A manually authored portrait diagram can contain a long, small-angle rod.
      // Preserve its validated source length when an unrelated physics Value changes.
      max = Math.max(max, valueAt(s, binding.path).number ?? min);
    }
    if (binding.path === "params.initial_stretch")
      min = Math.max(
        min,
        0.08 - read(s, this.params, `links.${s.links[0].id}.rest_length_m`),
      );
    if (binding.path === "params.initial_stretch") {
      const l = s.links[0],
        b = s.bodies[0],
        vertical = read(s, this.params, "params.vertical", 0) !== 0;
      const available = vertical
        ? s.image.height - l.a.point[1] - (b.bbox[3] - b.bbox[1])
        : s.image.width - l.a.point[0] - (b.bbox[2] - b.bbox[0]);
      max = Math.min(
        max,
        available / S - read(s, this.params, `links.${l.id}.rest_length_m`),
      );
    }
    if (binding.path.endsWith(".mu_k"))
      max = Math.min(
        max,
        read(s, this.params, binding.path.replace(/mu_k$/, "mu_s")),
      );
    if (binding.path.endsWith(".mu_s"))
      min = Math.max(
        min,
        read(s, this.params, binding.path.replace(/mu_s$/, "mu_k")),
      );
    if (sf && binding.path === `surfaces.${sf.id}.length_m`) {
      const a = read(s, this.params, `surfaces.${sf.id}.angle_deg`) * RAD,
        foot = sf.polyline[0];
      max = Math.min(
        max,
        (s.image.width - 24 - foot[0]) / (S * Math.cos(a)),
        (foot[1] - 55) / (S * Math.sin(a)),
      );
    }
    if (sf && binding.path === `surfaces.${sf.id}.angle_deg`) {
      const L = read(s, this.params, `surfaces.${sf.id}.length_m`) * S,
        foot = sf.polyline[0];
      if (L > foot[1] - 55)
        max = Math.min(max, Math.asin((foot[1] - 55) / L) / RAD);
      if (L > s.image.width - 24 - foot[0])
        min = Math.max(
          min,
          Math.acos((s.image.width - 24 - foot[0]) / L) / RAD,
        );
    }
    return [min, Math.max(min, max)];
  }
  unlock(id: string) {
    if (this.binding(id).class !== "geometry")
      throw new Error("Only geometry has locks");
    this.unlocked.add(id);
  }
  set(id: string, number: number, preview = false) {
    return this.setMany({ [id]: number }, preview);
  }
  setMany(values: Record<string, number>, preview = false) {
    // Validate before mutation, then resolve dependent limits against the whole
    // proposed transaction. Friction pairs and restored projects are order independent.
    for (const [id, number] of Object.entries(values)) {
      const b = this.binding(id);
      if (!Number.isFinite(number)) throw new Error("Nonfinite parameter");
      if (b.class === "geometry" && !this.unlocked.has(id))
        throw new Error("Geometry is locked");
    }
    for (const [id, number] of Object.entries(values))
      this.params[this.binding(id).path] = number;
    for (const [id, number] of Object.entries(values)) {
      const b = this.binding(id);
      if (!Number.isFinite(number)) throw new Error("Nonfinite parameter");
      if (b.class === "geometry" && !this.unlocked.has(id))
        throw new Error("Geometry is locked");
      const [min, max] = this.limits(b),
        n = Math.max(min, Math.min(max, number));
      this.params[b.path] = n;
      Object.assign(valueAt(this.document, b.path), {
        number: n,
        status: "user",
        source: "user",
        confidence: 1,
      });
    }
    // Geometry can shorten the range available to an initial-state handle.
    for (const b of this.original.bindings.filter(
      (b) => b.class === "initial",
    )) {
      const [min, max] = this.limits(b),
        v = valueAt(this.document, b.path);
      if (v.number !== null && (v.number < min || v.number > max)) {
        const n = Math.max(min, Math.min(max, v.number));
        this.params[b.path] = n;
        Object.assign(v, {
          number: n,
          status: "user",
          source: "user",
          confidence: 1,
        });
      }
    }
    this.preview = preview && this.original.archetype === "pendulum";
    this.trajectory = this.preview
      ? pendulumPreview(this.original, this.solverParameters())
      : this.solve();
    return this.trajectory;
  }
  complete() {
    this.preview = false;
    this.trajectory = this.solve();
    return this.trajectory;
  }
  backToOriginal() {
    this.params = {};
    this.unlocked.clear();
    this.document = structuredClone(this.original);
    this.preview = false;
    this.trajectory = this.solve();
  }
  rows(): ParameterRow[] {
    return this.original.bindings.map((b) => {
      const value = valueAt(this.document, b.path),
        [min, max] = this.limits(b);
      return {
        id: b.id,
        label: b.id.replaceAll("_", " "),
        kind: b.class,
        value: value.number,
        unit: value.unit,
        min,
        max,
        step: b.control.step,
        locked: b.class === "geometry" && !this.unlocked.has(b.id),
        status: value.status,
        confidence: value.confidence,
      };
    });
  }
  drag(handle: string, point: Point, preview = false) {
    const s = this.original,
      S = scale(s),
      binding = s.bindings.find(
        (b) =>
          b.handle === handle ||
          (handle.startsWith("pulley_") &&
            b.path === "params.initial_displacement"),
      );
    if (!binding) throw new Error("Unknown handle");
    if (handle.startsWith("pulley_")) {
      const i = Number(handle.slice(7)),
        b = s.bodies[i];
      const sf = s.surfaces.find((v) => v.type === "incline");
      const a = sf
        ? read(s, this.params, `surfaces.${sf.id}.angle_deg`) * RAD
        : 0;
      let q = (point[1] - b.anchor[1]) / S;
      if (i === 0)
        q =
          s.archetype === "atwood"
            ? -q
            : ((point[0] - b.anchor[0]) * Math.cos(a) -
                (point[1] - b.anchor[1]) * Math.sin(a)) /
              S;
      return this.set(binding.id, q, preview);
    }
    if (handle.startsWith("collision_")) {
      const b = s.bodies.find((b) => handle === `collision_${b.id}`)!;
      return this.set(
        binding.id,
        read(s, {}, `bodies.${b.id}.initial.position.x`) +
          (point[0] - b.anchor[0]) / S,
        preview,
      );
    }
    if (handle === "block" || handle === "incline_tip") {
      const sf = s.surfaces.find((v) => v.type === "incline")!,
        foot = sf.polyline[0];
      if (handle === "incline_tip")
        return this.set(
          binding.id,
          Math.atan2(foot[1] - point[1], point[0] - foot[0]) / RAD,
          preview,
        );
      const angle = read(s, this.params, `surfaces.${sf.id}.angle_deg`) * RAD;
      return this.set(
        binding.id,
        ((point[0] - foot[0]) * Math.cos(angle) -
          (point[1] - foot[1]) * Math.sin(angle)) /
          S,
        preview,
      );
    }
    if (handle === "bob") {
      const pivot = s.links[0].a.point;
      return this.set(
        binding.id,
        Math.atan2(point[0] - pivot[0], point[1] - pivot[1]) / RAD,
        preview,
      );
    }
    if (handle === "spring_end") {
      const start = s.links[0].a.point,
        vertical = read(s, this.params, "params.vertical", 0) !== 0;
      return this.set(
        binding.id,
        (vertical ? point[1] - start[1] : point[0] - start[0]) / S -
          read(s, this.params, `links.${s.links[0].id}.rest_length_m`),
        preview,
      );
    }
    if (handle === "launch") {
      const h = read(s, this.params, "params.launch_height"),
        sourceH = read(s, {}, "params.launch_height");
      const anchor = s.bodies[0].anchor,
        dx = point[0] - anchor[0],
        dy = anchor[1] - (h - sourceH) * S - point[1];
      const speed = s.bindings.find((b) => b.path === "params.launch_speed")!,
        angle = s.bindings.find((b) => b.path === "params.launch_angle")!;
      return this.setMany(
        {
          [speed.id]: Math.hypot(dx, dy) / 2.5,
          [angle.id]: Math.atan2(dy, dx) / RAD,
        },
        preview,
      );
    }
    throw new Error("Unsupported handle");
  }
}
