import { test } from "node:test";
import assert from "node:assert/strict";
import { textAt } from "../src/overlay/text-evidence";
import type { OCRText } from "../src/types";
test("text hit targets stay in native image coordinates and ignore outside clicks", () => {
  const texts: OCRText[] = [
    {
      text: "40 Q",
      bbox: [150, 15, 200, 35],
      confidence: 0.8,
      outcome: "unassigned",
    },
  ];
  assert.equal(textAt(texts, 175, 25), texts[0]);
  assert.equal(textAt(texts, 250, 25), undefined);
});
