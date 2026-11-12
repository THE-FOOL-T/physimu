import { test } from "node:test";
import assert from "node:assert/strict";
import { readiness } from "../src/ui/readiness";
test("ready status waits for both detector and OCR", () => {
  assert.equal(readiness({ detector: "ready", ocr: "warming" }), "warming");
  assert.equal(readiness({ detector: "warming", ocr: "ready" }), "warming");
  assert.equal(readiness({ detector: "ready", ocr: "ready" }), "ready");
});
test("missing models remain explicit", () => {
  assert.equal(
    readiness({ detector: "missing_weights", ocr: "ready" }),
    "missing_weights",
  );
  assert.equal(
    readiness({ detector: "ready", ocr: "unavailable" }),
    "ocr_unavailable",
  );
});
