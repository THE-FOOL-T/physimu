import test from "node:test";
import assert from "node:assert/strict";
import en from "../src/i18n/en.json";
import bn from "../src/i18n/bn.json";
test("English and Bangla keys and named placeholders match", () => {
  assert.deepEqual(Object.keys(en).sort(), Object.keys(bn).sort());
  for (const k of Object.keys(en) as (keyof typeof en)[])
    assert.deepEqual(
      (en[k].match(/\{\w+\}/g) || []).sort(),
      (bn[k].match(/\{\w+\}/g) || []).sort(),
      k,
    );
});
