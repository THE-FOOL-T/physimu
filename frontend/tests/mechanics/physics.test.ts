import test from "node:test";
import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import { parseScene } from "../../src/domains/mechanics/validate";
import { archetypes } from "../../src/domains/mechanics/archetypes";
import type { Scene, Params } from "../../src/domains/mechanics/types";

export function fixture(name: string): Scene {
  return parseScene(
    JSON.parse(
      readFileSync(
        new URL(`../../../fixtures/mechanics/${name}.json`, import.meta.url),
        "utf8",
      ),
    ),
  );
}
const near = (actual: number, expected: number, tolerance = 1e-6) =>
  assert.ok(
    Math.abs(actual - expected) <= tolerance * Math.max(1, Math.abs(expected)),
    `${actual} != ${expected}`,
  );
const run = (name: string, p: Params = {}) => {
  const s = fixture(name),
    r = archetypes[s.archetype].solve(s, p);
  assert.ok(r.supported, r.reason);
  return r;
};

test("textbook closed forms: projectile, incline, Atwood, table, collision", () => {
  const g = 9.81,
    projectile = run("projectile_ground");
  near(projectile.metrics.range, 400 / g);
  near(projectile.metrics.peak_height, 100 / g);
  near(projectile.metrics.flight_time, (20 * Math.sqrt(2)) / g);
  near(
    run("incline", { "surfaces.S1.mu_k": 0, "surfaces.S1.mu_s": 0 }).metrics
      .acceleration,
    g / 2,
  );
  near(
    run("incline").metrics.acceleration,
    g * (0.5 - 0.2 * Math.cos(Math.PI / 6)),
  );
  const atwood = run("atwood");
  near(atwood.metrics.acceleration, g / 3);
  near(atwood.metrics.tension, (4 * g) / 3);
  near(run("table_pulley").metrics.acceleration, (g - 0.1 * 2 * g) / 3);
  const collision = run("collision");
  near(collision.metrics.v1_after, -1);
  near(collision.metrics.v2_after, 2);
  near(collision.metrics.contact_time, 0.5);
});
test("RK4 pendulum period and undamped energy; spring frequency and all damping regimes", () => {
  const pend = run("pendulum", { "params.release_angle": 1 });
  near(pend.metrics.small_angle_period, (2 * Math.PI) / Math.sqrt(9.81));
  near(pend.metrics.measured_period, (2 * Math.PI) / Math.sqrt(9.81), 1e-3);
  const e0 = pend.states[0].kinetic + pend.states[0].potential;
  for (const s of pend.states) near(s.kinetic + s.potential, e0, 1e-7);
  const spring = run("spring_horizontal");
  near(spring.metrics.angular_frequency, 10);
  near(spring.metrics.period, Math.PI / 5);
  for (const s of spring.states) near(s.kinetic + s.potential, 2);
  for (const damping of [2, 20, 30]) {
    const r = run("spring_horizontal", { "links.L1.damping": damping });
    for (let i = 1; i < r.states.length; i++)
      assert.ok(
        r.states[i].kinetic + r.states[i].potential <=
          r.states[i - 1].kinetic + r.states[i - 1].potential + 1e-8,
      );
  }
  near(run("spring_vertical").metrics.equilibrium, 9.81 / 100);
});

test("force vectors agree with static balance, tangential damping and spring acceleration", () => {
  const s = fixture("incline"),
    p = { "surfaces.S1.mu_s": 0.8 },
    st = archetypes.incline_block.solve(s, p).states[0];
  const f = archetypes.incline_block
    .forces(s, p, st)
    .filter((f) => !f.component);
  near(
    f.reduce((a, f) => a + f.vector.x, 0),
    0,
  );
  near(
    f.reduce((a, f) => a + f.vector.y, 0),
    0,
  );
  const pend = fixture("pendulum"),
    params = {
      "params.release_angle": 0,
      "params.angular_speed": 1,
      "links.L1.damping": 0.5,
    };
  const start = archetypes.pendulum.solve(pend, params).states[0],
    forces = archetypes.pendulum.forces(pend, params, start);
  near(
    forces.reduce((a, f) => a + f.vector.x, 0),
    -0.5,
  );
  near(
    forces.reduce((a, f) => a + f.vector.y, 0),
    -1,
  );
  const spring = fixture("spring_horizontal"),
    sp = { "links.L1.damping": 2, "params.initial_speed": 1 };
  const sf = archetypes.spring_mass.forces(
    spring,
    sp,
    archetypes.spring_mass.solve(spring, sp).states[0],
  );
  near(
    sf.reduce((a, f) => a + f.vector.x, 0),
    -22,
  );
  near(
    sf.reduce((a, f) => a + f.vector.y, 0),
    0,
  );
});
test("all ten immutable deterministic solves reproduce native anchors within one pixel", () => {
  for (const name of [
    "projectile_ground",
    "projectile_cliff",
    "incline",
    "pendulum",
    "spring_horizontal",
    "spring_vertical",
    "atwood",
    "table_pulley",
    "incline_pulley",
    "collision",
  ]) {
    const s = fixture(name),
      before = JSON.stringify(s),
      module = archetypes[s.archetype],
      a = module.solve(s, {}),
      b = module.solve(s, {});
    assert.ok(a.supported, `${name}: ${a.reason}`);
    assert.deepEqual(a, b);
    assert.equal(JSON.stringify(s), before);
    const draw = module.layout(s, {}, a.states[0]);
    for (const body of s.bodies) {
      const p = draw.bodies.find((b) => b.id === body.id)!.anchor;
      near(p[0], body.anchor[0], 1e-9);
      near(p[1], body.anchor[1], 1e-9);
    }
  }
});
test("conservation: ballistic flight, pulley energy, collision momentum and e=1 energy", () => {
  for (const name of ["projectile_ground", "projectile_cliff", "atwood"]) {
    const r = run(name),
      e = r.states[0].kinetic + r.states[0].potential;
    for (const s of r.states.slice(0, -1))
      near(s.kinetic + s.potential, e, 1e-7);
  }
  for (const e of [0, 0.4, 1]) {
    const r = run("collision", { "params.restitution": e });
    r.states.forEach((s) => near(s.momentum.x, 1));
    if (e === 1) r.states.forEach((s) => near(s.kinetic, 2.5));
    else assert.ok(r.states.at(-1)!.kinetic < 2.5);
  }
  for (const [m1, m2] of [
    [1, 2],
    [5, 0.5],
    [2, 3],
  ])
    for (const e of [0, 0.4, 1]) {
      const r = run("collision", {
        "bodies.B1.mass": m1,
        "bodies.B2.mass": m2,
        "params.restitution": e,
      });
      r.states.forEach((s) => near(s.momentum.x, m1 * 2 - m2));
      if (e === 1) r.states.forEach((s) => near(s.kinetic, 2 * m1 + 0.5 * m2));
    }
});
test("static friction, both incline pulley directions, reversal and massive pulley", () => {
  const stick = run("incline", {
    "surfaces.S1.mu_s": 0.8,
    "surfaces.S1.mu_k": 0.6,
  });
  near(stick.metrics.acceleration, 0);
  assert.ok(stick.states.every((s) => s.velocities.B1.x === 0));
  const reverse = run("incline", { "params.initial_speed": 1 });
  assert.ok(reverse.events.some((e) => e.type === "turn_or_stick"));
  const table = run("table_pulley", { "surfaces.S1.mu_s": 0.6 });
  near(table.metrics.acceleration, 0);
  const up = run("incline_pulley");
  assert.ok(up.metrics.acceleration > 0);
  const down = run("incline_pulley", { "bodies.B2.mass": 0.2 });
  assert.ok(down.metrics.acceleration < 0);
  const balanced = run("incline_pulley", { "bodies.B2.mass": 1 });
  near(balanced.metrics.acceleration, 0);
  const s = fixture("atwood");
  s.pulleys[0].mass = { ...s.bodies[0].mass, number: 2 };
  const massive = archetypes.atwood.solve(s, {});
  near(massive.metrics.acceleration, 9.81 / 4);
  near(massive.metrics.tension_1, 9.81 * 1.25);
  near(massive.metrics.tension_2, 2 * 9.81 * 0.75);
  const E = massive.states[0].kinetic + massive.states[0].potential;
  massive.states
    .slice(0, -1)
    .forEach((st) => near(st.kinetic + st.potential, E));
});
test("exact events: floor, pulley, slope ends, compression, slack and after-panel mismatch", () => {
  for (const name of ["atwood", "table_pulley", "incline_pulley"]) {
    const r = run(name);
    assert.ok(r.events.some((e) => e.type === "floor_or_pulley_contact"));
    near(r.states.at(-1)!.scalars.v, 0);
  }
  assert.equal(run("incline").events.at(-1)!.type, "bottom_contact");
  assert.equal(
    run("incline", { "params.initial_speed": 20 }).events.at(-1)!.type,
    "top_contact",
  );
  assert.ok(
    run("spring_horizontal", {
      "params.initial_stretch": 0.6,
    }).warnings.includes("compression_limit"),
  );
  const pend = fixture("pendulum");
  pend.links[0].type = "rope";
  assert.ok(
    archetypes.pendulum
      .solve(pend, { "params.release_angle": 120 })
      .warnings.includes("rope_slack"),
  );
  assert.ok(
    run("table_pulley", {
      "surfaces.S1.mu_s": 10,
      "surfaces.S1.mu_k": 10,
      "params.initial_speed": -1,
    }).warnings.includes("rope_slack"),
  );
  const col = fixture("collision");
  col.constraints.push({
    type: "after_velocity",
    refs: ["B1"],
    values: { B1: { ...col.params.restitution, number: 999, unit: "m/s" } },
  });
  assert.ok(
    archetypes.collision_1d
      .solve(col, {})
      .warnings.includes("after_panel_mismatch"),
  );
});
test("unsupported inputs do not fabricate trajectories; schema rejects unsafe documents", () => {
  assert.equal(
    archetypes.projectile.solve(fixture("projectile_ground"), {
      "constants.g": 0.01,
    }).reason,
    "trajectory_budget_exceeded",
  );
  const s = fixture("atwood");
  s.bodies[0].mass.number = null;
  assert.equal(archetypes.atwood.solve(s, {}).supported, false);
  assert.equal(run("collision").supported, true);
  const base = fixture("incline");
  for (const mutate of [
    (s: Scene) => (s.bodies[0].mass.number = NaN),
    (s: Scene) => (s.bodies[0].id = "S1"),
    (s: Scene) => s.links.push({ id: "bad" } as any),
    (s: Scene) => (s.bodies[0].on_surface = "absent"),
  ]) {
    const s = structuredClone(base);
    mutate(s);
    assert.throws(() => parseScene(s));
  }
  const unknown = structuredClone(base);
  unknown.bodies[0].type = "wheelbarrow";
  const parsed = parseScene(unknown);
  assert.equal(parsed.bodies[0].type, "wheelbarrow");
  assert.equal(parsed.warnings.at(-1)!.code, "unknown_type");
  assert.equal(archetypes.incline_block.solve(parsed, {}).supported, false);
});
