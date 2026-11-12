import test from "node:test";
import assert from "node:assert/strict";
import { readdirSync, readFileSync } from "node:fs";
import { solve, transient } from "../src/solver/mna";
import type { Netlist } from "../src/types";
const dir = new URL("../../fixtures/", import.meta.url);
const close = (a: number, b: number) =>
  assert.ok(
    Math.abs(a - b) <= Math.max(1e-12, Math.abs(b) * 1e-6),
    `${a} != ${b}`,
  );
for (const file of readdirSync(dir).filter((p) => p.endsWith(".json"))) {
  const f = JSON.parse(readFileSync(new URL(file, dir), "utf8"));
  test(f.name, () => {
    const net = f.netlist as Netlist,
      out = solve(net);
    for (const [n, v] of Object.entries(f.expected.node_voltages || {}))
      close(out.node_voltages[n], v as number);
    for (const [c, i] of Object.entries(f.expected.currents || {}))
      close(out.components[c].current, i as number);
    assert.ok(
      out.invariants.max_kcl_error <
        Math.max(
          1e-10,
          Math.max(
            ...Object.values(out.components).map((c) => Math.abs(c.current)),
          ) * 1e-9,
        ),
    );
    assert.ok(out.invariants.relative_power_error < 1e-9);
    if (f.expected.short) assert.ok(out.short_circuit.detected);
    for (const c of f.expected.bypassed || [])
      assert.ok(out.short_circuit.bypassed.includes(c));
    if (f.transient) {
      const t = f.transient;
      close(
        transient(net, t.duration, t.steps).samples.at(-1)!.state[t.component],
        t.final,
      );
    }
  });
}
test("signed wire flow and short decomposition", () => {
  const f = JSON.parse(readFileSync(new URL("source_short.json", dir), "utf8"));
  const out = solve(f.netlist);
  assert.equal(out.short_circuit.short_paths.length, 1);
  assert.deepEqual(out.short_circuit.short_paths[0].components, ["S1"]);
  close(out.short_circuit.short_paths[0].current, 12 / 0.051);
});
