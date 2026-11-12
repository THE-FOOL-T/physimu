import type { Solution } from "../types";
type Notice = Solution["warnings"][number];
const priority = [
  "source_open_loop",
  "solve_failed",
  "uncertain_topology",
  "dangling_wire",
  "missed_component",
  "crossing_uncertain",
  "value_not_found",
  "unit_inferred",
  "polarity_assumed",
  "time_budget",
];
export function groupWarnings(warnings: Notice[]) {
  const groups = new Map<
    string,
    { warning: Notice; refs: Set<string | null> }
  >();
  for (const warning of warnings) {
    if (!groups.has(warning.code))
      groups.set(warning.code, { warning, refs: new Set() });
    groups.get(warning.code)!.refs.add(warning.ref);
  }
  const rank = (code: string) =>
    priority.includes(code) ? priority.indexOf(code) : 50;
  return [...groups.values()].sort(
    (a, b) =>
      rank(a.warning.code) - rank(b.warning.code) ||
      a.warning.code.localeCompare(b.warning.code),
  );
}
