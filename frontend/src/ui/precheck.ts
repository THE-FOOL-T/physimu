import type { Netlist, Warning } from "../types";
import { supported } from "../solver/mna";
import { traceIssues, type TraceIssue, type GhostPart } from "./trace-issues";

export type CheckItem = {
  id: string;
  kind: "wire" | "value" | "polarity" | "crossing" | "part" | "unsupported";
  part?: string;
  issue?: TraceIssue;
  count: number;
};
export function precheck(net: Netlist, ghosts: GhostPart[] = []) {
  const sources = net.components.filter(
    (c) =>
      !c.disabled &&
      ["dc_source", "battery", "ac_source", "current_source"].includes(c.type),
  );
  const closed = sources.filter((source) => {
    const [a, b] = source.terminals.map((t) => t.node);
    if (a === b) return true;
    const adj = new Map(net.nodes.map((n) => [n.id, new Set<string>()]));
    for (const c of net.components) {
      if (
        c.disabled ||
        !supported.has(c.type) ||
        c.id === source.id ||
        (c.type === "switch" && !c.switch_closed)
      )
        continue;
      const [x, y] = c.terminals.map((t) => t.node);
      adj.get(x)?.add(y);
      adj.get(y)?.add(x);
    }
    const seen = new Set<string>(),
      queue = [a];
    while (queue.length) {
      const p = queue.pop()!;
      if (seen.has(p)) continue;
      seen.add(p);
      queue.push(...(adj.get(p) || []));
    }
    return seen.has(b);
  });
  const missing = net.components.filter(
    (c) =>
      !c.disabled &&
      (!Number.isFinite(c.value.number) ||
        c.value.number === null ||
        c.value.status === "assumed") &&
      !["switch", "ground", "ammeter", "voltmeter", "galvanometer"].includes(
        c.type,
      ),
  );
  const issues = traceIssues(net, net.warnings, ghosts).filter(
    (i) => i.code !== "source_open_loop" || !closed.some((c) => c.id === i.ref),
  );
  const items: CheckItem[] = [];
  for (const c of net.components.filter(
    (c) => !supported.has(c.type) && !c.disabled,
  ))
    items.push({
      id: "type-" + c.id,
      kind: "unsupported",
      part: c.id,
      count: 1,
    });
  const loose = issues.filter((i) =>
    ["dangling_wire", "uncertain_topology"].includes(i.code),
  );
  if (loose.length)
    items.push({
      id: "loose",
      kind: "wire",
      issue: loose[0],
      count: loose.length,
    });
  if (!closed.length && sources.length && !loose.length)
    items.push({
      id: "source",
      kind: "wire",
      part: sources[0].id,
      count: 1,
      issue: {
        id: "source",
        code: "source_open_loop",
        ref: sources[0].id,
        xy: sources[0].terminals[0].xy,
      },
    });
  for (const issue of issues.filter(
    (i) => i.code.includes("crossing") || i.code.includes("junction"),
  ))
    items.push({ id: issue.id, kind: "crossing", issue, count: 1 });
  for (const issue of issues.filter((i) => i.code === "missing_part"))
    items.push({ id: issue.id, kind: "part", issue, count: 1 });
  missing.forEach((c) =>
    items.push({ id: "value-" + c.id, kind: "value", part: c.id, count: 1 }),
  );
  const polarity = [
    ...new Set(
      net.warnings
        .filter((w) => w.code === "polarity_uncertain" && w.ref)
        .map((w) => w.ref!),
    ),
  ];
  polarity
    .filter((id) => net.components.some((c) => c.id === id))
    .forEach((id) =>
      items.push({
        id: "polarity-" + id,
        kind: "polarity",
        part: id,
        count: 1,
      }),
    );
  return {
    items,
    issues,
    missing,
    parts: net.components.length,
    sources: sources.length,
    closed: closed.length > 0,
    ready: closed.length > 0 && items.length === 0,
  };
}
export function draftWarnings(net: Netlist): Warning[] {
  const stale = new Set([
    "uncertain_topology",
    "source_open_loop",
    "not_connected",
    "no_closed_loop",
    "dangling_wire",
    "partial_circuit",
    "value_not_found",
    "assumed_value",
    "floating_node",
    "wire_imbalance",
  ]);
  const warnings = net.warnings.filter((w) => !stale.has(w.code));
  const check = precheck({ ...net, warnings });
  if (!check.closed)
    warnings.push({
      code: "no_closed_loop",
      ref: null,
      message_key: "warn.no_closed_loop",
    });
  for (const c of check.missing)
    warnings.push({
      code: "value_not_found",
      ref: c.id,
      message_key: "warn.value_not_found",
    });
  return warnings;
}
