import type { Netlist, Solution } from "../types";
import { t, format, digits } from "../i18n";
import { solve, voltageTypes, supported } from "./mna";

export type Reduction = {
  type: "series" | "parallel";
  components: string[];
  resistance: number;
  left: number;
  right: number;
};
type Edge = { a: string; b: string; r: number; ids: string[] };
const resistive = new Set(["resistor", "rheostat", "potentiometer", "lamp"]);

export function reduceResistance(net: Netlist) {
  const active = net.components.filter((c) => !c.disabled),
    sources = active.filter((c) => voltageTypes.has(c.type));
  if (
    sources.length !== 1 ||
    active.some((c) => !resistive.has(c.type) && !voltageTypes.has(c.type))
  )
    return { steps: [] as Reduction[], resistance: null, complex: true };
  const [start, end] = sources[0].terminals.map((t) => t.node);
  let edges: Edge[] = active
    .filter((c) => resistive.has(c.type))
    .map((c) => ({
      a: c.terminals[0].node,
      b: c.terminals[1].node,
      r: c.value.number || 0,
      ids: [c.id],
    }));
  if (edges.some((e) => e.r <= 0 || e.a === e.b))
    return { steps: [] as Reduction[], resistance: null, complex: true };
  const steps: Reduction[] = [];
  for (let iteration = 0; iteration < active.length * 2; iteration++) {
    let changed = false;
    for (let i = 0; i < edges.length && !changed; i++)
      for (let j = i + 1; j < edges.length; j++) {
        const a = edges[i],
          b = edges[j];
        if ((a.a === b.a && a.b === b.b) || (a.a === b.b && a.b === b.a)) {
          const r = 1 / (1 / a.r + 1 / b.r),
            ids = [...a.ids, ...b.ids];
          steps.push({
            type: "parallel",
            components: ids,
            resistance: r,
            left: a.r,
            right: b.r,
          });
          edges = edges.filter((_, k) => k !== i && k !== j);
          edges.push({ a: a.a, b: a.b, r, ids });
          changed = true;
          break;
        }
      }
    if (changed) continue;
    for (const node of net.nodes) {
      if ([start, end].includes(node.id)) continue;
      const incident = edges.filter((e) => e.a === node.id || e.b === node.id);
      if (incident.length !== 2) continue;
      const [a, b] = incident,
        otherA = a.a === node.id ? a.b : a.a,
        otherB = b.a === node.id ? b.b : b.a;
      if (otherA === otherB) continue;
      const r = a.r + b.r,
        ids = [...a.ids, ...b.ids];
      steps.push({
        type: "series",
        components: ids,
        resistance: r,
        left: a.r,
        right: b.r,
      });
      edges = edges.filter((e) => e !== a && e !== b);
      edges.push({ a: otherA, b: otherB, r, ids });
      changed = true;
      break;
    }
    if (!changed) break;
  }
  const complete =
    edges.length === 1 &&
    [edges[0].a, edges[0].b].includes(start) &&
    [edges[0].a, edges[0].b].includes(end);
  return {
    steps,
    resistance: complete ? edges[0].r : null,
    complex: !complete,
  };
}

export function explanations(net: Netlist, solution: Solution, time: number) {
  const output: string[] = [t("explain.scope")],
    reduction = reduceResistance(net);
  for (const step of reduction.steps) {
    output.push(
      t("explain." + step.type, { components: step.components.join(", ") }),
    );
    output.push(
      t("explain.reduction", {
        kind: t("explain.kind." + step.type),
        resistance: format(step.resistance, "Ω"),
      }),
    );
    output.push(
      t("explain.formula." + step.type, {
        left: format(step.left, "Ω"),
        right: format(step.right, "Ω"),
        resistance: format(step.resistance, "Ω"),
      }),
    );
  }
  if (reduction.complex) output.push(t("explain.complex"));
  if (reduction.resistance !== null)
    output.push(
      t("explain.equivalent", {
        resistance: format(reduction.resistance, "Ω"),
      }),
    );
  let steady: Solution | undefined;
  for (const c of net.components) {
    if (c.disabled) continue;
    if (!supported.has(c.type)) {
      output.push(t("ui.unknown_block", { type: t("type." + c.type) }));
      continue;
    }
    const r = solution.components[c.id];
    if (!r) continue;
    output.push(
      t("explain.component", {
        id: c.label || c.id,
        current: format(r.current, "A"),
        voltage: format(r.v_drop, "V"),
      }),
    );
    if (c.value.status === "assumed" || c.value.status === "solved") {
      output.push(
        t("explain." + c.value.status, {
          id: c.label || c.id,
          value: format(
            c.value.number || 0,
            c.value.unit === "ohm" ? "Ω" : c.value.unit,
          ),
        }),
      );
      if (c.value.status === "solved")
        output.push(
          t("explain.using", {
            constraints: net.constraints
              .map(
                (con) =>
                  `${t("constraint." + con.type)} ${con.target} = ${format(con.value, con.unit)}`,
              )
              .join("; "),
          }),
        );
    }
    if (c.type === "switch")
      output.push(
        t("explain.switch", {
          id: c.id,
          state: t(c.switch_closed ? "closed" : "open"),
        }),
      );
    if (c.type === "capacitor") {
      output.push(
        t("explain.capacitor", {
          id: c.id,
          voltage: format(r.v_drop, "V"),
          time: format(time, "s"),
        }),
      );
      steady ??= solve(net);
      const final = steady.components[c.id]?.v_drop || 0;
      if (Math.abs(final) > 1e-12)
        output.push(
          t("explain.charge", {
            id: c.id,
            percent: digits(
              String(
                Math.round(Math.min(100, 100 * Math.abs(r.v_drop / final))),
              ),
            ),
          }),
        );
    }
  }
  for (const n of net.nodes)
    output.push(
      t("explain.node", {
        id: n.label || n.id,
        voltage: format(solution.node_voltages[n.id] || 0, "V"),
      }),
    );
  output.push(
    t("explain.power", {
      supplied: format(solution.total_power_supplied, "W"),
      consumed: format(solution.total_power_consumed, "W"),
    }),
  );
  return output;
}
