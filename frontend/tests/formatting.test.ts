import { test } from "node:test";
import assert from "node:assert/strict";
import { format, digits, setDigits } from "../src/i18n";
test("micro units, unknown values and Bangla numerals keep their Unicode spelling", () => {
  setDigits(false);
  assert.equal(format(0.0001, "A"), "100 µA");
  assert.equal(format(NaN), "—");
  try {
    setDigits(true);
    assert.equal(digits("0123456789"), "০১২৩৪৫৬৭৮৯");
  } finally {
    setDigits(false);
  }
});
