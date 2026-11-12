import test from "node:test";
import assert from "node:assert/strict";
import { placeBadge, overlap } from "../src/overlay/labels";
test("badges nudge perpendicular to leads and avoid adjacent labels/wires", () => {
  const wire: [number, number, number, number] = [0, 49, 200, 52];
  const first = placeBadge([60, 45, 110, 60], [0, 1], [wire], 200, 100);
  assert.equal(overlap(first, wire), false);
  const next = placeBadge([65, 45, 115, 60], [0, 1], [wire, first], 200, 100);
  assert.equal(overlap(next, wire), false);
  assert.equal(overlap(next, first), false);
  assert.ok(next[0] >= 0 && next[2] <= 200 && next[1] >= 0 && next[3] <= 100);
});
