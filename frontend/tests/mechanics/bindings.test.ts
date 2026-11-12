import test from "node:test";
import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import { parseScene } from "../../src/domains/mechanics/validate";
import { BindingEngine } from "../../src/domains/mechanics/bindings";
import {
  SimulationClock,
  SIM_DT,
  bracket,
  nativeToCss,
  cssToNative,
  canvasDpr,
} from "../../src/shared/sim";

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
const near = (a: number, b: number) =>
  assert.ok(Math.abs(a - b) < 1e-9, `${a} != ${b}`);
test("fixed clock uses capped deltas, accumulator interpolation, speed, step, seek and terminal pause", () => {
  const clock = new SimulationClock(3);
  clock.play();
  clock.tick(0);
  clock.tick(10);
  near(clock.time, 2 * SIM_DT);
  near(clock.displayTime, 0.01);
  near(clock.alpha, 0.4);
  clock.tick(1010);
  near(clock.displayTime, 0.11);
  clock.setSpeed(4);
  clock.tick(1110);
  near(clock.displayTime, 0.51);
  clock.pause();
  clock.tick(9000);
  near(clock.displayTime, 0.51);
  clock.step();
  near(clock.displayTime, 0.51 + SIM_DT);
  assert.equal(clock.playing, false);
  clock.seek(2.99);
  clock.play();
  clock.tick(10000);
  clock.tick(10100);
  near(clock.displayTime, 3);
  assert.equal(clock.playing, false);
  clock.play();
  near(clock.displayTime, 0);
  clock.reset();
  near(clock.displayTime, 0);
  assert.equal(clock.playing, false);
  assert.throws(() => clock.setSpeed(8));
  assert.throws(() => clock.seek(NaN));
  assert.deepEqual(bracket([0, 0.5, 1], 0.75), { a: 1, b: 2, alpha: 0.5 });
  assert.deepEqual(bracket([0, 0.5, 1], 0.75, [1]), { a: 1, b: 1, alpha: 0.5 });
  assert.equal(bracket([0, 0.5, 1], 1, [1]).a, 2);
});
test("native/CSS transforms round-trip with padding, zoom and capped DPR", () => {
  const view = { x: 143, y: 32, zoom: 1.5 },
    p: [number, number] = [123.75, 42.25];
  assert.deepEqual(cssToNative(nativeToCss(p, view), view), p);
  assert.equal(canvasDpr(4), 2);
  assert.equal(canvasDpr(1.5), 1.5);
  assert.throws(() => cssToNative(p, { ...view, zoom: 0 }));
});
test("binding classes, explicit user metadata, source immutability and original restoration", () => {
  const e = engine("incline"),
    source = JSON.stringify(e.original),
    before = structuredClone(e.document);
  assert.throws(() => e.set("theta", 40), /locked/);
  e.set("mass_B1", 6);
  e.set("position", 2.2);
  assert.equal(e.document.bodies[0].mass.status, "user");
  assert.equal(e.document.bodies[0].mass.source, "user");
  assert.equal(e.document.bodies[0].mass.confidence, 1);
  assert.equal(e.modified, false);
  e.unlock("theta");
  e.set("theta", 40);
  assert.equal(e.modified, true);
  assert.ok(e.trajectory.supported, e.trajectory.reason);
  assert.equal(JSON.stringify(e.original), source);
  e.backToOriginal();
  assert.deepEqual(e.document, before);
  assert.deepEqual(e.params, {});
  assert.equal(e.unlocked.size, 0);
});
test("controls clamp to drawn scene and geometry changes constrain initial position", () => {
  const e = engine("incline");
  e.set("position", 1e6);
  assert.ok(e.params["params.start_position"] <= 2.8);
  e.unlock("length");
  e.set("length", 1);
  assert.ok(e.params["params.start_position"] < 1);
  assert.ok(e.trajectory.supported, e.trajectory.reason);
  e.unlock("theta");
  e.set("theta", 1e6);
  assert.ok(e.params["surfaces.S1.angle_deg"] <= 75);
  assert.ok(e.trajectory.supported, e.trajectory.reason);
  const pend = engine("pendulum");
  pend.set("length", 10);
  assert.ok(pend.params["links.L1.length_m"] <= 1.352);
  const spring = engine("spring_horizontal");
  spring.set("stretch", -10);
  assert.ok(spring.params["params.initial_stretch"] >= -0.35);
  assert.throws(() => e.set("position", NaN));
});
test("four drag types write the same bounded Values as sliders", () => {
  for (const [name, handle, point] of [
    ["incline", "block", [450, 200]],
    ["pendulum", "bob", [500, 300]],
    ["spring_horizontal", "spring_end", [360, 330]],
    ["projectile_ground", "launch", [180, 380]],
  ] as const) {
    const e = engine(name);
    e.drag(handle, [...point]);
    assert.ok(Object.keys(e.params).length > 0);
    assert.ok(e.trajectory.supported, e.trajectory.reason);
    for (const row of e.rows())
      if (row.status === "user")
        assert.ok(row.value! >= row.min && row.value! <= row.max);
  }
  const incline = engine("incline");
  assert.throws(() => incline.drag("incline_tip", [500, 100]), /locked/);
  incline.unlock("theta");
  incline.drag("incline_tip", [500, 200]);
  assert.equal(incline.modified, true);
});

test("RK4 changes prepare a short preview before completing the same deterministic run", () => {
  const e = engine("pendulum");
  e.set("angle", 30, true);
  assert.equal(e.preview, true);
  const preview = structuredClone(e.trajectory);
  assert.equal(preview.duration, 0.25);
  const full = e.complete();
  assert.equal(e.preview, false);
  assert.ok(full.duration >= 8);
  assert.deepEqual(full.states.slice(0, preview.states.length), preview.states);
});
