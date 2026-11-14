import test from "node:test";
import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import { BindingEngine } from "../../src/domains/mechanics/bindings";
import { parseScene } from "../../src/domains/mechanics/validate";
import { pulleyBounds } from "../../src/domains/mechanics/archetypes/pulley";
import { parseProject, project } from "../../src/domains/mechanics/project";
import { preserveCorrections } from "../../src/domains/mechanics/reanalysis";
import { correctedQuantity } from "../../src/domains/mechanics/labels";
import {
  labelQuantity,
  labelCorrection,
} from "../../src/domains/mechanics/labels";
import { restoreEngine } from "../../src/domains/mechanics/project";
import { addBody, removeObject } from "../../src/domains/mechanics/authoring";

const engine = (name: string) =>
  new BindingEngine(
    parseScene(
      JSON.parse(
        readFileSync(
          new URL(`../../../fixtures/mechanics/${name}.json`, import.meta.url),
          "utf8",
        ),
      ),
    ),
  );

for (const name of ["atwood", "table_pulley", "incline_pulley"]) {
  test(`${name}: coupled initial displacement reaches solver without changing native geometry`, () => {
    const e = engine(name),
      before = structuredClone(e.original),
      start = e.trajectory.states[0];
    const { low, high } = pulleyBounds(e.original, {});
    const q = low + (high - low) * 0.65;
    const b = e.original.bindings.find(
      (b) => b.path === "params.initial_displacement",
    )!;
    e.set(b.id, q);
    assert.ok(e.trajectory.supported, e.trajectory.reason);
    const next = e.trajectory.states[0];
    assert.ok(Math.abs(next.positions.B2.y - start.positions.B2.y - q) < 1e-8);
    const first = Math.hypot(
      next.positions.B1.x - start.positions.B1.x,
      next.positions.B1.y - start.positions.B1.y,
    );
    assert.ok(Math.abs(first - Math.abs(q)) < 1e-8);
    assert.deepEqual(e.original, before);
    e.set(b.id, 1000);
    assert.ok(e.params[b.path] <= high);
    assert.ok(e.trajectory.supported, e.trajectory.reason);
  });
}
test("collision position overrides change contact time, preserve separation and source geometry", () => {
  const e = engine("collision"),
    before = structuredClone(e.original),
    time = e.trajectory.metrics.contact_time;
  const b = e.original.bindings.find(
    (b) => b.path === "bodies.B1.initial.position.x",
  )!;
  e.set(b.id, e.document.bodies[0].initial.position.x.number! + 0.2);
  assert.ok(e.trajectory.metrics.contact_time < time);
  assert.equal(e.trajectory.states[0].positions.B1.x, e.params[b.path]);
  e.drag("collision_B1", [10000, 0]);
  assert.ok(e.trajectory.supported, e.trajectory.reason);
  assert.deepEqual(e.original, before);
});
test("dependent bounds are order independent and invalid batches leave no partial mutation", () => {
  const a = engine("incline"),
    b = engine("incline");
  a.setMany({ mu_static: 0.6, mu: 0.5 });
  b.setMany({ mu: 0.5, mu_static: 0.6 });
  assert.deepEqual(a.document, b.document);
  const before = structuredClone(a.document),
    overrides = { ...a.params };
  assert.throws(() => a.setMany({ mass_B1: 7, missing: 8 }));
  assert.deepEqual(a.document, before);
  assert.deepEqual(a.params, overrides);
});
test("legacy v1 projects migrate initial controls on both snapshots and retain edits", () => {
  const e = engine("collision");
  const p = project(e, "data:image/png;base64,AAAA");
  const legacy = p as any;
  legacy.version = 1;
  delete legacy.recognition_scene;
  p.scene.bindings = p.scene.bindings.filter(
    (b) => !b.handle?.startsWith("collision_"),
  );
  p.current_scene = structuredClone(p.scene);
  const restored = parseProject(p);
  assert.equal(
    restored.scene.bindings.filter((b) => b.handle?.startsWith("collision_"))
      .length,
    2,
  );
  assert.deepEqual(restored.current_scene, restored.scene);
});

test("recognition snapshot survives authoring, override replay and version-2 project import", () => {
  const first = engine("pendulum"),
    recognized = structuredClone(first.recognition);
  const authored = structuredClone(first.original);
  authored.frame.paper_color = "#ffffff";
  const edited = new BindingEngine(authored, recognized);
  edited.set("mass_B1", 4);
  const p = project(edited, "data:image/png;base64,AAAA");
  assert.equal(p.version, 2);
  assert.deepEqual(p.recognition_scene, recognized);
  assert.notDeepEqual(p.scene, p.recognition_scene);
  assert.deepEqual(parseProject(p), p);
  const restored = restoreEngine({
    scene: p.scene,
    recognition: p.recognition_scene,
    overrides: p.parameter_overrides,
    unlocked: [],
  });
  assert.deepEqual(restored.recognition, recognized);
});

test("reanalysis preserves uniquely matched user values and surfaces unmatched values for repair", () => {
  const old = engine("collision");
  old.set("mass_B1", 8);
  const next = structuredClone(old.original);
  next.bodies[0].id = "new_body";
  next.bindings.forEach((b) => {
    b.path = b.path.replace("bodies.B1.", "bodies.new_body.");
  });
  next.annotations.forEach((a) => {
    a.bound_to = a.bound_to?.replace("bodies.B1.", "bodies.new_body.") ?? null;
  });
  const kept = preserveCorrections(old.document, next);
  assert.equal(kept.overrides["bodies.new_body.mass"], 8);
  assert.equal(kept.unplaced.length, 0);
  next.bodies[0].anchor[0] += 100;
  const unresolved = preserveCorrections(old.document, next);
  assert.ok(unresolved.unplaced.includes("bodies.B1.mass"));
  assert.equal(unresolved.scene.params.unplaced_correction_1.number, 8);
  assert.equal(unresolved.scene.params.unplaced_correction_1.status, "user");
});

test("explicit label corrections normalize SI and reject dimensional values without units", () => {
  assert.deepEqual(correctedQuantity("m₁=300 g"), { number: 0.3, unit: "kg" });
  assert.deepEqual(correctedQuantity("v₀=-২০ m/s"), {
    number: -20,
    unit: "m/s",
  });
  assert.deepEqual(correctedQuantity("θ=30°"), { number: 30, unit: "deg" });
  assert.deepEqual(correctedQuantity("μs=0.4"), { number: 0.4, unit: "1" });
  assert.equal(correctedQuantity("v0=20"), null);
  assert.equal(correctedQuantity("2 bananas"), null);
});

test("explicit missing-body authoring retains provenance, valid bindings and reversible removal", () => {
  const s = structuredClone(engine("atwood").original),
    before = structuredClone(s);
  const id = addBody(s);
  const body = parseScene(s).bodies.find((b) => b.id === id)!;
  assert.equal(body.mass.status, "assumed");
  assert.equal(body.initial.velocity.x.source, "prior");
  assert.ok(s.bindings.some((b) => b.path === `bodies.${id}.mass`));
  removeObject(s, id);
  assert.deepEqual(parseScene(s), before);
});

test("correcting a blocking physical value unlocks simulation without replacing source recognition", () => {
  const s = structuredClone(engine("incline").original);
  s.bodies[0].mass = {
    number: -1,
    unit: "kg",
    status: "given",
    source: "ocr",
    confidence: 0.8,
  };
  s.meta.provenance = "unsupported";
  s.warnings.push({
    code: "invalid_mass",
    ref: "B1",
    message_key: "mech.invalid_mass",
  });
  s.warnings.push({
    code: "missing_mass",
    ref: "B1",
    message_key: "mech.missing_mass",
  });
  const e = new BindingEngine(s),
    original = structuredClone(e.original);
  assert.equal(e.trajectory.supported, false);
  e.set("mass_B1", 2);
  assert.equal(e.trajectory.supported, true, e.trajectory.reason);
  assert.equal(e.document.meta.provenance, "authored");
  assert.ok(!e.document.warnings.some((w) => w.code === "invalid_mass"));
  assert.ok(!e.document.warnings.some((w) => w.code === "missing_mass"));
  assert.deepEqual(e.original, original);
  assert.deepEqual(
    parseProject(project(e, "data:image/png;base64,AAAA")).current_scene,
    e.document,
  );
  e.backToOriginal();
  assert.equal(e.trajectory.supported, false);
});

test("derived pendulum speed, length, labels and project replay share one angular Value", () => {
  const s = structuredClone(engine("pendulum").original);
  s.params.angular_speed = {
    number: 4,
    unit: "rad/s",
    status: "assumed",
    source: "constraint",
    confidence: 0,
  };
  s.warnings.push({
    code: "pendulum_speed_converted",
    ref: "L1",
    message_key: "mech.pendulum_speed_converted",
  });
  const e = new BindingEngine(s);
  e.set("length", 1.2);
  assert.ok(Math.abs(e.document.params.angular_speed.number! - 4 / 1.2) < 1e-9);
  const velocity = e.trajectory.states[0].velocities.B1;
  assert.ok(Math.abs(Math.hypot(velocity.x, velocity.y) - 4) < 1e-9);
  assert.ok(!("params.angular_speed" in e.params));
  assert.deepEqual(
    labelQuantity(
      e.original,
      "params.angular_speed",
      "v0=4 m/s",
      e.solverParameters(),
    ),
    { number: 4, unit: "m/s" },
  );
  assert.deepEqual(
    labelCorrection(e.document, "params.angular_speed", "v0=6 m/s"),
    { number: 5, unit: "rad/s" },
  );
  assert.deepEqual(
    parseProject(project(e, "data:image/png;base64,AAAA")).current_scene,
    e.document,
  );
  const omega = e.original.bindings.find(
    (b) => b.path === "params.angular_speed",
  )!;
  e.set(omega.id, 3);
  e.set("length", 1.1);
  assert.equal(e.document.params.angular_speed.number, 3);
  assert.ok(
    Math.abs(
      labelQuantity(
        e.original,
        "params.angular_speed",
        "v0=4 m/s",
        e.solverParameters(),
      ).number! - 3.3,
    ) < 1e-9,
  );
});

test("v1 velocity bindings and labels migrate to the solver path without losing a saved override", () => {
  const e = engine("projectile_ground"),
    p: any = project(e, "data:image/png;base64,AAAA");
  p.version = 1;
  delete p.recognition_scene;
  const path = "bodies.B1.initial.velocity.x";
  const label = structuredClone(
    p.scene.annotations.find((a: any) => a.type === "label"),
  );
  label.id = "legacy_speed";
  label.bound_to = path;
  label.geometry.text = "v0=20 m/s";
  p.scene.annotations.push(label);
  const binding = structuredClone(
    p.scene.bindings.find((b: any) => b.path === "params.launch_speed"),
  );
  binding.id = "legacy_velocity";
  binding.path = path;
  binding.labels = [label.id];
  binding.handle = null;
  p.scene.bindings.push(binding);
  p.current_scene = structuredClone(p.scene);
  p.current_scene.bodies[0].initial.velocity.x = {
    number: 7,
    unit: "m/s",
    status: "user",
    source: "user",
    confidence: 1,
  };
  p.parameter_overrides = { [path]: 7 };
  const migrated = parseProject(p);
  assert.equal(migrated.parameter_overrides["params.launch_speed"], 7);
  assert.ok(!(path in migrated.parameter_overrides));
  assert.equal(migrated.current_scene.params.launch_speed.number, 7);
  assert.equal(
    migrated.scene.annotations.find((a) => a.id === label.id)!.bound_to,
    "params.launch_speed",
  );
  assert.ok(
    migrated.scene.bindings
      .find((b) => b.path === "params.launch_speed")!
      .labels.includes(label.id),
  );
});
