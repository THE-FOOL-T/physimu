import test from "node:test";
import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import type { Netlist } from "../src/types";
import {
  History,
  addComponent,
  attachTerminal,
  mergeNodes,
  splitTerminal,
  addWire,
  cutWire,
  assertNetlist,
} from "../src/ui/editor";
import { solve } from "../src/solver/mna";
import { resolveLocal } from "../src/solver/resolve";
const load = () =>
  JSON.parse(
    readFileSync(
      new URL("../../fixtures/series.json", import.meta.url),
      "utf8",
    ),
  ).netlist as Netlist;
test("wrong component, missed component and wrong connection are reversible", () => {
  let n = load();
  const history = new History();
  history.push(n);
  n.components[1].type = "lamp";
  addComponent(n, "resistor", [300, 200]);
  attachTerminal(n, n.components[1], 1, "g");
  assertNetlist(n);
  assert.ok(solve(n).components.R1);
  n = history.undo(n)!;
  assert.equal(n.components[1].type, "resistor");
  assert.equal(n.components.length, 3);
  assert.equal(n.components[1].terminals[1].node, "m");
  n = history.redo(n)!;
  assert.equal(n.components.length, 4);
});
test("split/merge and wire routing preserve schema", () => {
  const n = load();
  const c = n.components[1];
  splitTerminal(n, c, 0);
  assertNetlist(n);
  mergeNodes(n, "p", c.terminals[0].node);
  assertNetlist(n);
  const ps = n.wire_graph.points;
  const s = addWire(n, ps[0].id, ps.at(-1)!.id);
  s.polyline.splice(1, 0, [40, 40]);
  assertNetlist(n);
  assert.equal(s.polyline.length, 3);
});
test("offline constraints keep derived resistance when a fixed value changes", () => {
  let n = load();
  n.constraints = [
    {
      type: "current",
      target: "R1",
      value: 1,
      unit: "A",
      source: "problem_text",
    },
  ];
  n.components[2].value.number = null;
  n = resolveLocal(n);
  assert.ok(Math.abs(n.components[2].value.number! - 8) < 1e-6);
  assert.equal(n.components[2].value.status, "solved");
  n.components[1].value.number = 6;
  n.components[1].value.status = "user";
  n = resolveLocal(n);
  assert.ok(Math.abs(n.components[2].value.number! - 6) < 1e-6);
  assert.equal(n.components[1].value.number, 6);
});
test("cutting a wire changes electrical connectivity", () => {
  const n = load();
  const wire = n.wire_graph.segments.find(
    (s) => s.from === "R1.a" || s.to === "R1.a",
  )!;
  cutWire(n, wire.id);
  assertNetlist(n);
  assert.ok(Math.abs(solve(n).components.R1.current) < 1e-8);
});
