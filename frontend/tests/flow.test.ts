import { test } from "node:test";
import assert from "node:assert/strict";
import {
  particleBudget,
  smoothReference,
  contrast,
  flowColors,
  flowOutline,
  voltageTint,
  blendWhite,
  readFlow,
  saveFlow,
} from "../src/overlay/flow";

test("particle budget is fair, bounded and independent of segment order", () => {
  const segments = Array.from({ length: 120 }, (_, i) => ({
    id: "wire" + i,
    length: 30 + i * 200,
    current: i % 2 ? 1e-14 : 100,
  }));
  const counts = particleBudget(segments, 1);
  assert.equal(counts.size, 120);
  assert.ok([...counts.values()].every((c) => c >= 1));
  assert.equal(
    [...counts.values()].reduce((a, b) => a + b, 0),
    500,
  );
  assert.deepEqual(counts, particleBudget([...segments].reverse(), 1));
  const many = particleBudget(
    Array.from({ length: 600 }, (_, i) => ({
      id: String(i),
      length: 10,
      current: 1,
    })),
    1,
  );
  assert.equal(many.size, 600);
  assert.ok([...many.values()].every((c) => c === 1));
  assert.equal(
    particleBudget([{ id: "zero", length: 100, current: 0 }], 1).size,
    0,
  );
});
test("reference follows a large parameter change smoothly and resets on a new circuit", () => {
  let value = smoothReference(null, [0.01, 0.02, 0.03], 0);
  assert.equal(value, 0.02);
  const first = smoothReference(value, [10, 20, 30], 0.016);
  assert.ok(first > value && first < 20);
  for (let i = 0; i < 180; i++)
    value = smoothReference(value, [10, 20, 30], 1 / 60);
  assert.ok(Math.abs(value - 20) < 0.001);
  assert.equal(smoothReference(null, [1e-14], 0), 1e-14);
});
test("outlined bright flow has a 3:1 boundary against paper and the subtle wire tint in both themes", () => {
  // Exact requested amber fill is only ~1.8:1 on white. Its dark boundary,
  // not a false claim about that fill alone, supplies the paper contrast.
  assert.ok(contrast(flowColors.amber[0], "#ffffff") < 3);
  for (const colors of Object.values(flowColors))
    for (const color of colors) {
      assert.ok(contrast(color, flowOutline) >= 3);
      assert.ok(contrast(flowOutline, "#ffffff") >= 3);
      for (const fraction of [0, 0.25, 0.5, 0.75, 1])
        assert.ok(
          contrast(flowOutline, blendWhite(voltageTint(fraction, 0, 1))) >= 3,
        );
    }
  for (const colors of Object.values(flowColors))
    assert.ok(contrast(colors[1], "#192a3b") >= 3);
  assert.ok(contrast("#E4007C", "#ffffff") >= 3);
});
test("flow preferences tolerate unavailable storage", () => {
  const descriptor = Object.getOwnPropertyDescriptor(
    globalThis,
    "localStorage",
  );
  Object.defineProperty(globalThis, "localStorage", {
    configurable: true,
    get() {
      throw new Error("storage blocked");
    },
  });
  try {
    assert.deepEqual(readFlow(), { style: "dots", color: "amber", size: 1 });
    assert.doesNotThrow(() => saveFlow(readFlow()));
  } finally {
    if (descriptor)
      Object.defineProperty(globalThis, "localStorage", descriptor);
    else delete (globalThis as Record<string, unknown>).localStorage;
  }
});
