import { test } from "node:test";
import assert from "node:assert/strict";
import { createAppState } from "../src/ui/state";
import { stored, store } from "../src/ui/storage";
import { withoutImage, ImageStore } from "../src/ui/image-store";
import { groupWarnings } from "../src/ui/warnings";
import fixture from "../../fixtures/editor_loop.json";
import type { Netlist } from "../src/types";

test("workspace states do not share history or time state", () => {
  const a = createAppState(),
    b = createAppState();
  a.graphHistory.push({ time: 1, v: 2, i: 3 });
  a.state.R1 = 4;
  assert.equal(b.graphHistory.length, 0);
  assert.deepEqual(b.state, {});
});
test("payload strips image without mutating the displayed circuit", () => {
  const net = structuredClone(fixture.netlist) as unknown as Netlist;
  net.image.path = "data:image/png;base64," + "A".repeat(2_000_000);
  const payload = withoutImage(net);
  assert.equal(payload.image.path, "");
  assert.ok(JSON.stringify(payload).length < 5000);
  assert.ok(net.image.path.length > 2_000_000);
});
test("image store revokes its blobs and keeps ordinary demo URLs", () => {
  const images = new ImageStore(),
    url = images.fromData("data:image/png;base64,AA==");
  assert.ok(url.startsWith("blob:"));
  assert.equal(images.fromData("/demos/example.png"), "/demos/example.png");
  images.clear();
  images.clear();
});
test("image store preserves percent-encoded SVG and commas in data URLs", async () => {
  const images = new ImageStore(),
    svg = '<svg xmlns="http://www.w3.org/2000/svg"><text>x,y</text></svg>';
  try {
    for (const value of [encodeURIComponent(svg), svg]) {
      const url = images.fromData("data:image/svg+xml," + value);
      assert.equal(await (await fetch(url)).text(), svg);
    }
  } finally {
    images.clear();
  }
});
test("blocked storage is optional for all preferences", () => {
  const descriptor = Object.getOwnPropertyDescriptor(
    globalThis,
    "localStorage",
  );
  Object.defineProperty(globalThis, "localStorage", {
    configurable: true,
    get() {
      throw Error("blocked");
    },
  });
  try {
    assert.equal(stored("circuit-language"), null);
    assert.doesNotThrow(() => store("circuit-language", "bn"));
  } finally {
    if (descriptor)
      Object.defineProperty(globalThis, "localStorage", descriptor);
    else delete (globalThis as Record<string, unknown>).localStorage;
  }
});
test("warning groups have distinct affected refs and stable priorities", () => {
  const warnings = [
    { code: "value_not_found", ref: "R1", message_key: "warn.value_not_found" },
    {
      code: "source_open_loop",
      ref: "V1",
      message_key: "warn.source_open_loop",
    },
    { code: "value_not_found", ref: "R2", message_key: "warn.value_not_found" },
  ];
  const result = groupWarnings([...warnings, warnings[0]]);
  assert.equal(result.length, 2);
  assert.equal(result[0].warning.code, "source_open_loop");
  assert.equal(result[1].refs.size, 2);
});
