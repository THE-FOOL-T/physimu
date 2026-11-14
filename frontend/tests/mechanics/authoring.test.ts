import test from "node:test";
import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import { parseScene, valueAt } from "../../src/domains/mechanics/validate";
import {
  stencil,
  emptyScene,
  handles,
  moveHandle,
  setBox,
  attach,
  addLine,
  assignValue,
  userValue,
  rename,
  nameOf,
  SceneHistory,
  switchArchetype,
  valuePaths,
  removeObject,
  type EditState,
} from "../../src/domains/mechanics/authoring";
import { BindingEngine } from "../../src/domains/mechanics/bindings";
import {
  parseProject,
  project,
  restoreEngine,
} from "../../src/domains/mechanics/project";
import { archetypes } from "../../src/domains/mechanics/archetypes";
import { repairMissingLength } from "../../src/domains/mechanics/parameter-repair";
const fixture = (name: string) =>
  parseScene(
    JSON.parse(
      readFileSync(
        new URL(`../../../fixtures/mechanics/${name}.json`, import.meta.url),
        "utf8",
      ),
    ),
  );
const image = "data:image/png;base64,aW1hZ2U="; // Pure contract test; browser must decode before installation.

test("first length repair calibrates the detected source and preserves an explicit release angle", () => {
  const scene = fixture("pendulum"),
    before = structuredClone(scene);
  scene.links[0].length_m!.number = null;
  scene.params.release_angle = userValue(15, "deg");
  const pixels = Math.hypot(
    scene.bodies[0].anchor[0] - scene.links[0].a.point[0],
    scene.bodies[0].anchor[1] - scene.links[0].a.point[1],
  );
  repairMissingLength(scene, `links.${scene.links[0].id}.length_m`, 2.4);
  assert.equal(scene.links[0].length_m!.number, 2.4);
  assert.equal(scene.frame.px_per_m.number, pixels / 2.4);
  assert.equal(scene.params.release_angle.number, 15);
  if (before.bodies[0].radius_m?.number)
    assert.equal(
      scene.bodies[0].radius_m!.number,
      (before.bodies[0].radius_m.number * before.frame.px_per_m.number!) /
        scene.frame.px_per_m.number!,
    );
  assert.deepEqual(scene.bodies[0].anchor, before.bodies[0].anchor);
  assert.deepEqual(scene.links[0].polyline, before.links[0].polyline);
  assert.equal(new BindingEngine(parseScene(scene)).trajectory.supported, true);
  assert.throws(() =>
    repairMissingLength(scene, `links.${scene.links[0].id}.length_m`, -1),
  );
});

test("manual templates transform native geometry, retain SI scale and label every Value assumed", () => {
  for (const name of [
    "projectile_ground",
    "incline",
    "pendulum",
    "spring_horizontal",
    "atwood",
    "table_pulley",
    "incline_pulley",
    "collision",
  ]) {
    const f = fixture(name),
      s = stencil(f, { path: "owner.png", width: 1200, height: 780 });
    assert.equal(s.meta.provenance, "authored");
    assert.equal(s.image.path, "owner.png");
    assert.equal(s.bodies[0].anchor[0], f.bodies[0].anchor[0] * 1.5);
    for (const p of valuePaths(s)) {
      assert.equal(valueAt(s, p).status, "assumed");
      assert.equal(valueAt(s, p).confidence, 0);
    }
    assert.ok(archetypes[s.archetype].solve(s, {}).supported, name);
    assert.equal(s.repairs.length, 0);
    assert.ok(s.annotations.every((a) => a.type === "axis"));
  }
  const s = emptyScene({ path: "real.png", width: 400, height: 300 });
  assert.equal(s.archetype, "unsupported");
  assert.equal(s.bodies.length, 0);
  assert.equal(archetypes.unsupported.solve(s, {}).supported, false);
});
test("manual pendulum pivot/bob edits calibrate native frame zero, box and mask", () => {
  const s = stencil(fixture("pendulum"), {
    path: "real.png",
    width: 800,
    height: 520,
  });
  moveHandle(s, handles(s).find((h) => h.kind === "pivot")!, [320, 70]);
  moveHandle(s, handles(s).find((h) => h.kind === "body")!, [440, 330]);
  setBox(s, "B1", [420, 310, 460, 350]);
  parseScene(s);
  const run = archetypes.pendulum.solve(s, {}),
    draw = archetypes.pendulum.layout(s, {}, run.states[0]);
  assert.ok(
    Math.hypot(draw.bodies[0].anchor[0] - 440, draw.bodies[0].anchor[1] - 330) <
      1e-9,
  );
  assert.deepEqual(s.links[0].b.point, s.bodies[0].anchor);
  assert.equal(s.params.release_angle.status, "user");
});
test("incline handle edits and pulley/rope attachment preserve references", () => {
  const s = fixture("incline");
  moveHandle(
    s,
    handles(s).find(
      (h) =>
        h.kind === "surface" && h.index === 1 && h.object === s.surfaces[0].id,
    )!,
    [650, 130],
  );
  const run = archetypes.incline_block.solve(s, {});
  assert.ok(run.supported);
  const draw = archetypes.incline_block.layout(s, {}, run.states[0]);
  assert.deepEqual(draw.bodies[0].anchor, s.bodies[0].anchor);
  parseScene(s);
  const pulley = fixture("atwood");
  const h = handles(pulley).find((h) => h.kind === "pulley")!;
  moveHandle(pulley, h, [h.point[0] + 10, h.point[1] + 5]);
  attach(pulley, pulley.links[0].id, "b", pulley.bodies[1].id);
  assert.equal(pulley.links[0].b.ref, pulley.bodies[1].id);
  parseScene(pulley);
});
test("draw missing lines, attach endpoints, assign typed chips and retain names", () => {
  const s = fixture("incline");
  for (const type of ["rope", "spring", "incline", "floor"] as const)
    addLine(s, type, [100, 430], [300, 300]);
  rename(s, "B1", "Owner block");
  assert.equal(nameOf(s, "B1"), "Owner block");
  s.params.unplaced_1 = userValue(4, "kg");
  assignValue(s, "unplaced_1", "bodies.B1.mass");
  assert.equal(s.bodies[0].mass.number, 4);
  assert.equal(s.params.unplaced_1, undefined);
  s.params.unplaced_2 = userValue(3, "m");
  assert.throws(
    () => assignValue(s, "unplaced_2", "bodies.B1.mass"),
    /unit_mismatch/,
  );
  parseScene(s);
  switchArchetype(s, "unsupported");
  assert.equal(archetypes.unsupported.solve(s, {}).supported, false);
  assert.ok(s.bodies.length > 0);
});
test("bounded scene history restores parameter overrides and clears redo on a branch", () => {
  const history = new SceneHistory(),
    state: EditState = {
      scene: fixture("pendulum"),
      overrides: {},
      unlocked: [],
    };
  const after = structuredClone(state);
  after.scene.bodies[0].mass = userValue(7, "kg");
  history.push(state, after);
  assert.deepEqual(history.undo(), state);
  assert.deepEqual(history.redo(), after);
  history.undo();
  history.push(state, { ...after, overrides: { "bodies.B1.mass": 3 } });
  assert.equal(history.canRedo, false);
  for (let i = 0; i < 100; i++) {
    const b = structuredClone(state),
      a = structuredClone(state);
    a.scene.constants.g.number = i;
    history.push(b, a);
  }
  let count = 0;
  while (history.undo()) count++;
  assert.equal(count, 80);
});
test("portable project replays all binding classes without losing calibration", () => {
  const e = new BindingEngine(fixture("incline"));
  for (const b of e.original.bindings.filter((b) => b.class === "geometry"))
    e.unlock(b.id);
  const physics = e.original.bindings.find((b) => b.class === "physics")!,
    initial = e.original.bindings.find((b) => b.class === "initial")!,
    geometry = e.original.bindings.find((b) => b.class === "geometry")!;
  for (const b of [physics, initial, geometry]) {
    const [lo, hi] = e.limits(b);
    e.set(b.id, (lo + hi) / 2);
  }
  const p = parseProject(JSON.parse(JSON.stringify(project(e, image))));
  assert.deepEqual(p.scene, e.original);
  assert.deepEqual(p.current_scene, e.document);
  assert.deepEqual(
    restoreEngine({
      scene: p.scene,
      overrides: p.parameter_overrides,
      unlocked: p.unlocked_geometry,
    }).trajectory,
    e.trajectory,
  );
});
test("portable import rejects invalid refs, nonfinite values, remote images, tampering and bounds", () => {
  const e = new BindingEngine(fixture("pendulum")),
    p = project(e, image);
  for (const mutate of [
    (p: any) => (p.scene.links[0].a.ref = "missing"),
    (p: any) => (p.scene.constants.g.number = NaN),
    (p: any) => (p.source_image = "https://example.com/image.png"),
    (p: any) => (p.current_scene.bodies[0].mass.number = 99),
    (p: any) => (p.parameter_overrides["bodies.B1.mass"] = 1e6),
    (p: any) => (p.parameter_overrides["__proto__.number"] = 2),
    (p: any) => p.unlocked_geometry.push("mass_B1"),
    (p: any) => (p.extra = true),
  ]) {
    const bad = structuredClone(p);
    mutate(bad);
    assert.throws(() => parseProject(bad));
  }
  assert.equal(parseProject(p).scene.image.path, p.scene.image.path);
});

test("switching a damped pendulum to unsupported retains editable values and valid binding units", () => {
  const s = fixture("pendulum");
  switchArchetype(s, "unsupported");
  parseScene(s);
  assert.equal(s.meta.provenance, "unsupported");
  assert.equal(s.bodies.length, 1);
  switchArchetype(s, "spring_mass");
  parseScene(s);
  switchArchetype(s, "pendulum");
  parseScene(s);
  assert.equal(s.links[0].damping!.unit, "1/s");
});
test("removing an object preserves endpoint anchors and drops invalid bindings", () => {
  const s = fixture("pendulum");
  removeObject(s, "B1");
  const checked = parseScene(s);
  assert.equal(checked.bodies.length, 0);
  assert.ok(checked.annotations.some((a) => a.id === checked.links[0].b.ref));
  assert.ok(checked.bindings.every((b) => !b.path.startsWith("bodies.B1.")));
  assert.equal(archetypes.pendulum.solve(checked, {}).supported, false);
});
test("dependent friction overrides restore regardless of saved key order", () => {
  const e = new BindingEngine(fixture("incline"));
  e.set("mu", 0.05);
  e.set("mu_static", 0.08);
  const p = project(e, image);
  p.parameter_overrides = Object.fromEntries(
    Object.entries(p.parameter_overrides).reverse(),
  );
  assert.deepEqual(parseProject(p).current_scene, e.document);
});
test("a modified geometry value can be relocked and roundtripped", () => {
  const e = new BindingEngine(fixture("incline"));
  e.unlock("theta");
  e.set("theta", 35);
  e.unlocked.delete("theta");
  const p = parseProject(project(e, image));
  assert.deepEqual(p.unlocked_geometry, []);
  assert.equal(p.current_scene.surfaces[0].angle_deg!.number, 35);
  const restored = restoreEngine({
    scene: p.scene,
    overrides: p.parameter_overrides,
    unlocked: p.unlocked_geometry,
  });
  assert.throws(() => restored.set("theta", 40), /locked/);
});
