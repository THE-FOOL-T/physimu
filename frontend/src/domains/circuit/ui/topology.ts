import type { Netlist, WirePoint } from "../types";

export const distance = (a: number[], b: number[]) =>
  Math.hypot(a[0] - b[0], a[1] - b[1]);
export function project(
  xy: number[],
  a: number[],
  b: number[],
): [number, number] {
  const dx = b[0] - a[0],
    dy = b[1] - a[1];
  const f = Math.max(
    0,
    Math.min(
      1,
      ((xy[0] - a[0]) * dx + (xy[1] - a[1]) * dy) / (dx * dx + dy * dy || 1),
    ),
  );
  return [a[0] + f * dx, a[1] + f * dy];
}
export function rebuildTopology(net: Netlist): Netlist {
  net.wire_graph.segments = net.wire_graph.segments.filter(
    (s) => !s.id.startsWith("contact:"),
  );
  const oldNodes = new Map(net.nodes.map((n) => [n.id, n]));
  const oldMembers = new Map<string, Set<string>>();
  const remember = (id: string, node: string) => {
    if (!oldMembers.has(node)) oldMembers.set(node, new Set());
    oldMembers.get(node)!.add(id);
  };
  net.wire_graph.points.forEach((p) => remember(p.id, p.node));
  net.components.forEach((c) =>
    c.terminals.forEach((t) => remember(t.id, t.node)),
  );
  const terminals = net.components.flatMap((c) => c.terminals);
  const terminalIds = new Set(terminals.map((t) => t.id));
  net.wire_graph.points = net.wire_graph.points.filter(
    (p) => p.kind !== "terminal" || terminalIds.has(p.id),
  );
  const points = new Map(net.wire_graph.points.map((p) => [p.id, p]));
  for (const terminal of terminals) {
    const point = points.get(terminal.id);
    if (point) {
      point.xy = [...terminal.xy];
      point.kind = "terminal";
    } else
      points.set(terminal.id, {
        ...terminal,
        xy: [...terminal.xy],
        kind: "terminal",
      });
  }
  net.wire_graph.segments = net.wire_graph.segments.filter(
    (s) => points.has(s.from) && points.has(s.to),
  );
  const used = new Set(net.wire_graph.segments.flatMap((s) => [s.from, s.to]));
  for (const [id, p] of points)
    if (!used.has(id) && p.kind !== "terminal" && p.kind !== "junction")
      points.delete(id);
  const parent = new Map([...points.keys()].map((id) => [id, id]));
  const find = (id: string): string => {
    let root = id;
    while (parent.get(root) !== root) root = parent.get(root)!;
    while (parent.get(id) !== id) {
      const next = parent.get(id)!;
      parent.set(id, root);
      id = next;
    }
    return root;
  };
  const join = (a: string, b: string) => {
    const x = find(a),
      y = find(b);
    parent.set(x < y ? y : x, x < y ? x : y);
  };
  for (const segment of net.wire_graph.segments) {
    segment.polyline[0] = [...points.get(segment.from)!.xy];
    segment.polyline[segment.polyline.length - 1] = [
      ...points.get(segment.to)!.xy,
    ];
    join(segment.from, segment.to);
  }
  // A crossing has independent channels until a shared endpoint or explicit
  // junction joins them. Terminals and junction dots can touch segment interiors.
  const contacts = [...points.values()].filter(
    (p) => p.kind === "terminal" || p.kind === "junction",
  );
  for (const point of contacts) {
    for (const other of points.values())
      if (
        distance(point.xy, other.xy) < 0.75 &&
        find(point.id) !== find(other.id)
      ) {
        net.wire_graph.segments.push({
          id: "contact:" + [point.id, other.id].sort().join(":"),
          from: point.id,
          to: other.id,
          node: "pending",
          polyline: [[...point.xy], [...other.xy]],
          confidence: 1,
        });
        join(point.id, other.id);
      }
    for (const segment of [...net.wire_graph.segments]) {
      if (segment.from === point.id || segment.to === point.id) continue;
      const i = segment.polyline
        .slice(1)
        .findIndex(
          (b, i) =>
            distance(point.xy, project(point.xy, segment.polyline[i], b)) <
            0.75,
        );
      if (i < 0) continue;
      if (
        distance(point.xy, points.get(segment.from)!.xy) < 0.75 ||
        distance(point.xy, points.get(segment.to)!.xy) < 0.75
      ) {
        join(point.id, segment.from);
        continue;
      }
      const to = segment.to,
        right = segment.polyline.slice(i + 1),
        id = segment.id + "@" + point.id;
      segment.to = point.id;
      segment.polyline = [...segment.polyline.slice(0, i + 1), [...point.xy]];
      net.wire_graph.segments.push({
        ...segment,
        id,
        from: point.id,
        to,
        polyline: [[...point.xy], ...right],
      });
      join(point.id, segment.from);
    }
  }
  const groups = new Map<string, WirePoint[]>();
  for (const point of points.values()) {
    const root = find(point.id);
    if (!groups.has(root)) groups.set(root, []);
    groups.get(root)!.push(point);
  }
  const ordered = [...groups.values()].map((group) =>
    group.sort((a, b) => a.id.localeCompare(b.id)),
  );
  ordered.sort((a, b) => b.length - a.length || a[0].id.localeCompare(b[0].id));
  const claimed = new Set<string>();
  net.nodes = [];
  for (const group of ordered) {
    const counts = new Map<string, number>();
    group.forEach((p) => counts.set(p.node, (counts.get(p.node) || 0) + 1));
    const candidate = [...counts]
      .filter(([id]) => oldNodes.has(id) && !claimed.has(id))
      .sort((a, b) => b[1] - a[1] || a[0].localeCompare(b[0]))[0]?.[0];
    let id = candidate || "n." + encodeURIComponent(group[0].id);
    while (claimed.has(id)) id += "_";
    claimed.add(id);
    const members = oldMembers.get(id);
    const unchanged =
      members?.size === group.length && group.every((p) => members.has(p.id));
    const previous = oldNodes.get(id);
    net.nodes.push({
      id,
      is_ground: unchanged ? previous?.is_ground || false : false,
      label: unchanged ? previous?.label || null : null,
    });
    group.forEach((p) => (p.node = id));
  }
  net.nodes.sort((a, b) => a.id.localeCompare(b.id));
  net.wire_graph.points = [...points.values()].sort((a, b) =>
    a.id.localeCompare(b.id),
  );
  for (const terminal of terminals)
    terminal.node = points.get(terminal.id)!.node;
  for (const segment of net.wire_graph.segments)
    segment.node = points.get(segment.from)!.node;
  net.wire_graph.segments.sort((a, b) => a.id.localeCompare(b.id));
  return net;
}
