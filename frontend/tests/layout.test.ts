import { test } from "node:test";
import assert from "node:assert/strict";
import { fitView } from "../src/overlay/view";
import { placePartBadge, overlap, type Rect } from "../src/overlay/labels";
import { friendlyFilename } from "../src/ui/filenames";

test("Fit keeps content at all four native edges inside a 24px paper margin", () => {
  for (const width of [200, 320, 390, 650, 1024, 1440])
    for (const [w, h] of [
      [606, 366],
      [2000, 200],
      [200, 2000],
    ]) {
      const v = fitView(width, w, h);
      assert.ok(v.x >= 24 - 1e-6 && v.y >= 24 - 1e-6);
      assert.ok(v.x + w * v.scale <= v.width - 24 + 1e-6);
      assert.ok(v.y + h * v.scale <= v.height - 24 + 1e-6);
      assert.ok(Math.abs((v.x + 73 * v.scale - v.x) / v.scale - 73) < 1e-6);
    }
});
test("part readings avoid printed R1/R6 values above the body", () => {
  for (const body of [
    [155, 32, 205, 58],
    [210, 310, 260, 336],
  ] as Rect[]) {
    const printed: Rect = [body[0] - 8, body[1] - 25, body[2] + 8, body[1]],
      placed = placePartBadge(
        body,
        [
          [90, 20],
          [40, 20],
        ],
        [body, printed],
        606,
        366,
      );
    assert.ok(!overlap(placed.rect, printed));
    assert.ok(!overlap(placed.rect, body));
  }
});
test("titles discard opaque hashes and keep useful filenames", () => {
  assert.equal(
    friendlyFilename("parallel_" + "a".repeat(90) + ".png"),
    "parallel",
  );
  assert.equal(friendlyFilename("a".repeat(90) + ".png"), "Uploaded diagram");
  assert.equal(friendlyFilename("3.0 V circuit.png"), "3.0 V circuit");
});
