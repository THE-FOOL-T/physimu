import test from "node:test";
import assert from "node:assert/strict";
import { imageToCanvas, canvasToImage } from "../src/overlay/renderer";
test("image-space coordinates round trip at desktop and mobile sizes", () => {
  for (const width of [320, 600, 1280])
    for (const p of [
      [0, 0],
      [606, 366],
      [267, 179],
    ]) {
      const out = canvasToImage(imageToCanvas(p, width, 606), width, 606);
      assert.ok(out.every((v, i) => Math.abs(v - p[i]) < 1e-10));
    }
});
