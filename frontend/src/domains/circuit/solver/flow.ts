import type { Netlist, Reading, Warning } from "../types";
const distance = (a: number[], b: number[]) =>
  Math.hypot(a[0] - b[0], a[1] - b[1]);
export function segmentCurrents(
  net: Netlist,
  readings: Record<string, Reading>,
) {
  const result: Record<string, number> = Object.fromEntries(
    net.wire_graph.segments.map((s) => [s.id, 0]),
  );
  const warnings: Warning[] = [];
  for (const node of net.nodes) {
    const ps = net.wire_graph.points.filter((p) => p.node === node.id);
    if (!ps.length) continue;
    const parents = new Map(ps.map((p) => [p.id, p.id]));
    const find = (p: string): string => {
      while (parents.get(p) !== p) {
        parents.set(p, parents.get(parents.get(p)!)!);
        p = parents.get(p)!;
      }
      return p;
    };
    const adj = new Map(
      ps.map((p) => [p.id, [] as { to: string; id: string; sign: number }[]]),
    );
    const length = (s: Netlist["wire_graph"]["segments"][number]) =>
      s.polyline
        .slice(1)
        .reduce((n, p, i) => n + distance(s.polyline[i], p), 0);
    for (const s of net.wire_graph.segments
      .filter((s) => s.node === node.id)
      .sort((a, b) => length(a) - length(b) || a.id.localeCompare(b.id))) {
      const a = find(s.from),
        b = find(s.to);
      if (a === b) {
        warnings.push({
          code: "wire_loop",
          ref: s.id,
          message_key: "warn.wire_loop",
        });
        continue;
      }
      parents.set(a, b);
      adj.get(s.from)!.push({ to: s.to, id: s.id, sign: 1 });
      adj.get(s.to)!.push({ to: s.from, id: s.id, sign: -1 });
    }
    const inject: Record<string, number> = Object.fromEntries(
      ps.map((p) => [p.id, 0]),
    );
    for (const c of net.components) {
      if (!readings[c.id]) continue;
      c.terminals.forEach((t, k) => {
        if (t.node === node.id) {
          const p = ps.reduce((a, b) =>
            distance(a.xy, t.xy) < distance(b.xy, t.xy) ? a : b,
          );
          inject[p.id] += readings[c.id].current * (k === 0 ? -1 : 1);
        }
      });
    }
    const seen = new Set<string>();
    function visit(p: string, prev: string | null): number {
      seen.add(p);
      let sum = inject[p];
      for (const e of adj.get(p)!) {
        if (e.to === prev) continue;
        const sub = visit(e.to, p);
        result[e.id] = -sub * e.sign;
        sum += sub;
      }
      return sum;
    }
    for (const p of ps)
      if (!seen.has(p.id)) {
        if (Math.abs(visit(p.id, null)) > 1e-7)
          warnings.push({
            code: "wire_imbalance",
            ref: node.id,
            message_key: "warn.wire_imbalance",
          });
      }
  }
  return { currents: result, warnings };
}
export function decomposePaths(
  net: Netlist,
  readings: Record<string, Reading>,
  currents: Record<string, number>,
  sources: string[],
) {
  const terminal = (t: Netlist["components"][number]["terminals"][number]) => {
    const ps = net.wire_graph.points.filter((p) => p.node === t.node);
    return ps.length
      ? ps.reduce((a, b) =>
          distance(a.xy, t.xy) < distance(b.xy, t.xy) ? a : b,
        ).id
      : "node:" + t.node;
  };
  const edges: {
    a: string;
    b: string;
    i: number;
    id: string;
    component: boolean;
  }[] = net.wire_graph.segments.map((s) => ({
    a: s.from,
    b: s.to,
    i: currents[s.id],
    id: s.id,
    component: false,
  }));
  for (const c of net.components)
    if (readings[c.id] && !sources.includes(c.id))
      edges.push({
        a: terminal(c.terminals[0]),
        b: terminal(c.terminals[1]),
        i: readings[c.id].current,
        id: c.id,
        component: true,
      });
  const output: {
    source: string;
    current: number;
    segments: string[];
    components: string[];
  }[] = [];
  for (const src of net.components.filter((c) => sources.includes(c.id))) {
    const flip = src.polarity?.positive_terminal === src.terminals[1].id,
      start = terminal(src.terminals[flip ? 1 : 0]),
      end = terminal(src.terminals[flip ? 0 : 1]);
    const residual = edges
      .filter((e) => Math.abs(e.i) > 1e-12)
      .map((e) => ({
        ...e,
        a: e.i < 0 ? e.b : e.a,
        b: e.i < 0 ? e.a : e.b,
        i: Math.abs(e.i),
      }));
    const total = Math.abs(readings[src.id].current);
    for (let iter = 0; iter < 100; iter++) {
      function search(p: string, seen: Set<string>): number[] | null {
        if (p === end) return [];
        for (const j of residual
          .map((_, i) => i)
          .sort((a, b) => residual[b].i - residual[a].i)) {
          const e = residual[j];
          if (
            e.a === p &&
            !seen.has(e.b) &&
            e.i > Math.max(1e-12, total * 0.0001)
          ) {
            const tail = search(e.b, new Set([...seen, e.b]));
            if (tail !== null) return [j, ...tail];
          }
        }
        return null;
      }
      const path = search(start, new Set([start]));
      if (!path?.length) break;
      const amount = Math.min(...path.map((j) => residual[j].i));
      for (const j of path) residual[j].i -= amount;
      output.push({
        source: src.id,
        current: amount,
        segments: path
          .filter((j) => !residual[j].component)
          .map((j) => residual[j].id),
        components: path
          .filter((j) => residual[j].component)
          .map((j) => residual[j].id),
      });
      if (
        output
          .filter((p) => p.source === src.id)
          .reduce((n, p) => n + p.current, 0) >=
        total * 0.99
      )
        break;
    }
  }
  return output;
}
