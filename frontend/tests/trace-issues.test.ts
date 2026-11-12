import test from "node:test";
import assert from "node:assert/strict";
import { traceIssues, issueAt } from "../src/ui/trace-issues";
import fixture from "../../fixtures/single_resistor.json";
import type { Netlist } from "../src/types";

test("loose ends, doubtful crossings and missing parts have native clickable locations", () => {
  const net = structuredClone(fixture.netlist) as unknown as Netlist;
  net.wire_graph.points.push({
    id: "loose",
    node: net.nodes[0].id,
    xy: [80, 90],
    kind: "bend",
  });
  const issues = traceIssues(
    net,
    [
      {
        code: "ambiguous_crossing",
        ref: "xy:140,100",
        message_key: "warn.ambiguous_crossing",
      },
    ],
    [
      {
        bbox: [200, 100, 240, 120],
        from: [200, 110],
        to: [240, 110],
        reason: "missing_part",
      },
    ],
  );
  assert.equal(issueAt(issues, 80, 90, 12)?.ref, "loose");
  assert.equal(issueAt(issues, 140, 100, 12)?.code, "ambiguous_crossing");
  assert.equal(issueAt(issues, 220, 110, 12)?.code, "missing_part");
  assert.equal(issueAt(issues, 0, 0, 12), undefined);
});
