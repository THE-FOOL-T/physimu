import test from "node:test";
import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import type { Netlist } from "../src/types";
import { assertNetlist } from "../src/ui/editor";
import { History, cloneForEdit } from "../src/ui/edit-history";
import { rebuildTopology } from "../src/ui/topology";
import {
  addBoxComponent,
  drawWire,
  cutWire,
  moveTerminal,
  moveComponent,
  removeComponent,
  crossing,
} from "../src/ui/edit-geometry";
import { precheck } from "../src/ui/precheck";
import { solve } from "../src/solver/mna";
const load = () =>
  JSON.parse(
    readFileSync(
      new URL("../../fixtures/editor_loop.json", import.meta.url),
      "utf8",
    ),
  ).netlist as Netlist;

test("two drawn endpoints repair a missing wire and preserve typed values", () => {
  const net = load(),
    wire = structuredClone(net.wire_graph.segments[0]);
  cutWire(net, wire.id);
  assert.equal(precheck(net).closed, false);
  drawWire(net, wire.polyline);
  assert.equal(precheck(net).closed, true);
  net.components.find((c) => c.type === "resistor")!.value = {
    number: 220,
    unit: "ohm",
    status: "user",
    source: "user",
    confidence: 1,
  };
  assertNetlist(net);
  assert.ok(Math.abs(solve(net).components.R1.current) > 0);
});
test("a box over a missed resistor snaps its two ends and closes the loop", () => {
  const net = load(),
    part = net.components.find((c) => c.type === "resistor")!;
  const box: [number, number, number, number] = [
    part.terminals[0].xy[0],
    part.bbox[1],
    part.terminals[1].xy[0],
    part.bbox[3],
  ];
  removeComponent(net, part.id);
  assert.equal(precheck(net).closed, false);
  const added = addBoxComponent(net, "resistor", box, 12);
  added.value.number = 220;
  assertNetlist(net);
  assert.equal(precheck(net).closed, true);
  assert.ok(Math.abs(solve(net).components[added.id].current) > 0);
});
test("joining and separating a crossing changes only the chosen channels", () => {
  const net = load();
  net.components = [];
  net.wire_graph = { points: [], segments: [] };
  net.nodes = [];
  drawWire(net, [
    [10, 50],
    [90, 50],
  ]);
  drawWire(net, [
    [50, 10],
    [50, 90],
  ]);
  assert.equal(net.nodes.length, 2);
  crossing(net, [50, 50], true);
  assert.equal(net.nodes.length, 1);
  crossing(net, [50, 50], false);
  assert.equal(net.nodes.length, 2);
  assertNetlist(net);
  assert.deepEqual(rebuildTopology(cloneForEdit(net)), net);
});
test("history stores field differences and never stores the embedded image", () => {
  const net = load();
  net.image.path = "data:image/png;base64," + "A".repeat(2_000_000);
  const before = cloneForEdit(net),
    history = new History();
  net.components[0].value.number = 7;
  history.push(before, net);
  assert.ok(JSON.stringify(history.undoStack).length < 300);
  assert.equal(history.undo(net)!.image.path, net.image.path);
  assert.equal(history.redo(before)!.components[0].value.number, 7);
});

function equivalence(net: Netlist) {
  return net.wire_graph.points
    .map((p) => [
      p.id,
      net.wire_graph.points
        .filter((q) => q.node === p.node)
        .map((q) => q.id)
        .sort(),
    ])
    .sort((a, b) => String(a[0]).localeCompare(String(b[0])));
}
test("an unsupported model cannot supply the only return path", () => {
  const net = load();
  net.components.find((c) => c.id === "R1")!.type = "diode";
  const result = precheck(net);
  assert.equal(result.closed, false);
  assert.equal(result.items[0].kind, "unsupported");
});
for (let seed = 1; seed <= 12; seed++)
  test(`geometry, topology and undo remain valid through random edits (seed ${seed})`, () => {
    let net = load(),
      state = seed;
    const random = () => {
      state = (Math.imul(state, 1664525) + 1013904223) >>> 0;
      return state / 2 ** 32;
    };
    const history = new History();
    rebuildTopology(net);
    for (let i = 0; i < 35; i++) {
      const before = cloneForEdit(net),
        part = net.components[Math.floor(random() * net.components.length)],
        op = Math.floor(random() * 6);
      if (op === 0)
        drawWire(net, [
          [10 + random() * 700, 20 + random() * 400],
          [10 + random() * 700, 20 + random() * 400],
        ]);
      else if (op === 1 && net.wire_graph.segments.length)
        cutWire(
          net,
          net.wire_graph.segments[
            Math.floor(random() * net.wire_graph.segments.length)
          ].id,
        );
      else if (op === 2)
        moveTerminal(net, part, Math.round(random()), [
          20 + random() * 700,
          20 + random() * 400,
        ]);
      else if (op === 3)
        addBoxComponent(net, "resistor", [50 + i * 3, 70, 80 + i * 3, 90], 8);
      else if (op === 4) moveComponent(net, part, random() * 10, random() * 10);
      else if (net.wire_graph.segments[0])
        crossing(net, net.wire_graph.segments[0].polyline[0]);
      assertNetlist(net);
      assert.deepEqual(rebuildTopology(cloneForEdit(net)), net);
      const fresh = cloneForEdit(net);
      fresh.nodes = [];
      fresh.wire_graph.points.forEach((p) => (p.node = "pending"));
      fresh.components.forEach((c) =>
        c.terminals.forEach((t) => (t.node = "pending")),
      );
      rebuildTopology(fresh);
      assert.deepEqual(equivalence(fresh), equivalence(net));
      history.push(before, net);
      if (history.undoStack.length) {
        const after = cloneForEdit(net);
        net = history.undo(net)!;
        assertNetlist(net);
        net = history.redo(net)!;
        assert.deepEqual(net, after);
      }
    }
  });
