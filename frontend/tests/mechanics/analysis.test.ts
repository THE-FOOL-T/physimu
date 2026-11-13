import { test } from "node:test";
import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import {
  MechanicsAnalysis,
  parseResult,
} from "../../src/domains/mechanics/analysis";
import { compareTrajectories } from "../../src/domains/mechanics/evaluation";
import { BindingEngine } from "../../src/domains/mechanics/bindings";
import { parseScene } from "../../src/domains/mechanics/validate";
const fixture = () =>
  parseScene(
    JSON.parse(
      readFileSync(
        new URL("../../../fixtures/mechanics/pendulum.json", import.meta.url),
        "utf8",
      ),
    ),
  );
function result() {
  const scene = fixture();
  scene.meta.provenance = "partial";
  return {
    domain: "mechanics",
    provenance: "partial",
    reason: null,
    scene,
    source_image: "data:image/png;base64,aGVsbG8=",
    warnings: [],
    timings: { total: 0.1 },
  };
}
const reply = (x: unknown, status = 200) =>
  new Response(JSON.stringify(x), { status });
const file = () =>
  new File([new Uint8Array([1, 2])], "diagram.png", { type: "image/png" });
test("mechanics polling sends explicit domain and receives canonical partial image and scene", async () => {
  const calls: { url: string; options?: RequestInit }[] = [];
  let poll = 0;
  const client = new MechanicsAnalysis((async (url, options) => {
    calls.push({ url: String(url), options });
    if (options?.method === "POST")
      return reply({
        domain: "mechanics",
        job_id: "a/b",
        stages: ["received", "done"],
      });
    return ++poll === 1
      ? reply({
          stage: "geometry",
          percent: 50,
          elapsed_seconds: 0.2,
          partial: {
            source_image: result().source_image,
            width: 800,
            height: 520,
            detections: [],
          },
        })
      : reply({
          stage: "done",
          percent: 100,
          elapsed_seconds: 0.3,
          result: result(),
        });
  }) as typeof fetch);
  const stages: string[] = [];
  const got = await client.start(file(), "bn", (p) => {
    stages.push(p.stage);
  });
  assert.equal(got?.scene.archetype, "pendulum");
  const form = calls[0].options!.body as FormData;
  assert.equal(form.get("domain"), "mechanics");
  assert.equal(form.get("lang"), "bn");
  assert.deepEqual(stages, ["geometry", "done"]);
  assert.match(calls[1].url, /a%2Fb\?include_image=true/);
  assert.match(calls[2].url, /include_image=false/);
});
test("cancelling a pending start deletes its late admitted job", async () => {
  let finish!: (r: Response) => void;
  const deleted: string[] = [];
  const client = new MechanicsAnalysis((async (url, options) => {
    if (options?.method === "POST")
      return new Promise<Response>((resolve) => {
        finish = resolve;
      });
    if (options?.method === "DELETE") deleted.push(String(url));
    return reply({});
  }) as typeof fetch);
  const pending = client.start(file(), "en", () =>
    assert.fail("stale progress"),
  );
  client.cancel();
  finish(reply({ job_id: "late", domain: "mechanics", stages: [] }));
  assert.equal(await pending, null);
  assert.deepEqual(deleted, ["/api/analyze/late"]);
});
test("cancelling a pending poll blocks a late successful result", async () => {
  let finish!: (r: Response) => void;
  let polled!: () => void;
  const ready = new Promise<void>((r) => {
    polled = r;
  });
  const deleted: string[] = [];
  const client = new MechanicsAnalysis((async (url, options) => {
    if (options?.method === "POST")
      return reply({ job_id: "j", domain: "mechanics", stages: [] });
    if (options?.method === "DELETE") {
      deleted.push(String(url));
      return reply({});
    }
    polled();
    return new Promise<Response>((r) => {
      finish = r;
    });
  }) as typeof fetch);
  const pending = client.start(file(), "en", () =>
    assert.fail("stale progress"),
  );
  await ready;
  client.cancel();
  finish(reply({ stage: "done", percent: 100, result: result() }));
  assert.equal(await pending, null);
  assert.deepEqual(deleted, ["/api/analyze/j"]);
});
test("invalid envelopes and failed jobs cannot become scenes", async () => {
  assert.throws(() => parseResult({ ...result(), domain: "circuit" }));
  const invalid = result();
  invalid.scene.meta.provenance = "authored";
  assert.throws(() => parseResult(invalid));
  let count = 0;
  const client = new MechanicsAnalysis((async () =>
    reply(
      ++count === 1
        ? { domain: "mechanics", job_id: "x", stages: [] }
        : { error: { code: "cancelled" } },
    )) as typeof fetch);
  await assert.rejects(
    client.start(file(), "en", () => {}),
    /cancelled/,
  );
});
test("unsupported perception withholds simulation while preserving editable objects", () => {
  const scene = fixture();
  scene.meta.provenance = "unsupported";
  const engine = new BindingEngine(scene);
  assert.equal(engine.trajectory.supported, false);
  assert.equal(engine.original.bodies.length, 1);
});
test("trajectory evaluation distinguishes production from correctness", () => {
  const gold = fixture(),
    prediction = fixture();
  const bodyMap = Object.fromEntries(gold.bodies.map((b) => [b.id, b.id]));
  const same = compareTrajectories(prediction, gold, bodyMap);
  assert.equal(same.trajectory_correct, true);
  assert.ok(same.maximum_displacement_error_m! < 1e-12);
  prediction.constants.g.number = 2;
  const changed = compareTrajectories(prediction, gold, bodyMap);
  assert.equal(changed.simulation_produced, true);
  assert.equal(changed.trajectory_correct, false);
  prediction.meta.provenance = "unsupported";
  assert.equal(
    compareTrajectories(prediction, gold, bodyMap).simulation_produced,
    false,
  );
});

test("an unrelated authored repair cannot silently ignore a retained force", () => {
  const scene = fixture();
  scene.forces.push({
    id: "F1",
    body: scene.bodies[0].id,
    tail: [40, 20],
    head: [80, 20],
    label: "F",
    magnitude: {
      number: 10,
      unit: "N",
      status: "given",
      source: "ocr",
      confidence: 1,
    },
  });
  scene.meta.provenance = "authored";
  scene.bodies[0].mass.number = 2;
  const engine = new BindingEngine(scene);
  assert.equal(engine.trajectory.supported, false);
  assert.equal(engine.trajectory.reason, "unsupported_applied_force");
  scene.forces = [];
  assert.equal(new BindingEngine(scene).trajectory.supported, true);
});
