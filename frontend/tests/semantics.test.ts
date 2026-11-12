import test from "node:test";
import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import type { Netlist } from "../src/types";
import { reduceResistance, explanations } from "../src/solver/explain";
import { resolveLocal } from "../src/solver/resolve";
import { solve } from "../src/solver/mna";
const fixture = (name: string) =>
  JSON.parse(readFileSync(`../fixtures/${name}.json`, "utf8"))
    .netlist as Netlist;
for (const name of ["series", "parallel", "mixed"])
  test(`series/parallel reduction agrees with MNA: ${name}`, () => {
    const net = fixture(name),
      group = reduceResistance(net),
      solution = solve(net);
    assert.equal(group.complex, false);
    assert.ok(
      Math.abs(group.resistance! - solution.equivalent_resistance!) < 1e-6,
    );
    assert.ok(group.steps.length > 0);
  });
test("bridge cannot be explained as a simple series/parallel reduction", () => {
  assert.equal(reduceResistance(fixture("unbalanced_bridge")).complex, true);
});
for (const [type, target, value] of [
  ["equivalent_resistance", "total", 12],
  ["voltage", "A-B", 8],
  ["power", "total", 12],
  ["current", "total", 1],
] as const) {
  for (const state of ["determined", "underdetermined", "inconsistent"])
    test(`${type} resolution: ${state}`, () => {
      const net = fixture("series");
      net.nodes.find((n) => n.id === "m")!.label = "A";
      net.nodes.find((n) => n.id === "g")!.label = "B";
      net.components[1].value.number = null;
      if (state === "underdetermined") net.components[2].value.number = null;
      net.constraints = [
        { type, target, value, unit: "", source: "problem_text" },
      ];
      if (state === "inconsistent")
        net.constraints.push({
          type,
          target,
          value: value * 2,
          unit: "",
          source: "problem_text",
        });
      const result = resolveLocal(net);
      assert.equal(
        result.components[1].value.status,
        state === "determined" ? "solved" : "assumed",
      );
      if (state === "determined")
        assert.ok(Math.abs(result.components[1].value.number! - 4) < 1e-4);
      if (state === "inconsistent")
        assert.ok(
          result.warnings.some((w) => w.code === "inconsistent_constraints"),
        );
    });
}
test("fixed contradictory total measurements warn and explanations update with values", () => {
  const net = fixture("series");
  net.constraints = [
    {
      type: "current",
      target: "total",
      value: 2,
      unit: "A",
      source: "problem_text",
    },
  ];
  assert.ok(
    resolveLocal(net).warnings.some(
      (w) => w.code === "inconsistent_constraints",
    ),
  );
  const before = explanations(net, solve(net), 0).join(" ");
  net.components[1].value.number = 8;
  assert.notEqual(explanations(net, solve(net), 0).join(" "), before);
});
