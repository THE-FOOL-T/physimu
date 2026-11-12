import type { Component, Netlist, Segment, WirePoint } from "../types";
import { distance, project, rebuildTopology } from "./topology";

type XY = [number, number];
export function uniqueId(items: { id: string }[], prefix: string) {
  let i = 1;
  while (items.some((x) => x.id === prefix + i)) i++;
  return prefix + i;
}
export function wireHit(net: Netlist, xy: XY, radius: number) {
  let best:
    | { segment: Segment; xy: XY; distance: number; index: number }
    | undefined;
  for (const segment of net.wire_graph.segments)
    for (let i = 1; i < segment.polyline.length; i++) {
      const point = project(xy, segment.polyline[i - 1], segment.polyline[i]),
        d = distance(point, xy);
      if (d <= radius && (!best || d < best.distance))
        best = { segment, xy: point, distance: d, index: i };
    }
  return best;
}
export function snapPoint(
  net: Netlist,
  xy: XY,
  radius: number,
  exclude?: string,
) {
  const points = [
    ...net.wire_graph.points.filter((p) => p.id !== exclude),
    ...net.components.flatMap((c) =>
      c.terminals
        .filter((t) => t.id !== exclude)
        .map((t) => ({ ...t, kind: "terminal" })),
    ),
  ];
  const nearest = points.sort(
    (a, b) => distance(a.xy, xy) - distance(b.xy, xy),
  )[0];
  if (nearest && distance(nearest.xy, xy) <= radius)
    return { xy: [...nearest.xy] as XY, id: nearest.id };
  const hit = wireHit(net, xy, radius);
  return hit ? { xy: hit.xy, id: undefined } : { xy, id: undefined };
}
function pointAt(net: Netlist, xy: XY, split = true): WirePoint {
  let point = net.wire_graph.points.find((p) => distance(p.xy, xy) < 0.5);
  if (!point) {
    point = {
      id: uniqueId(net.wire_graph.points, "p"),
      xy: [...xy],
      node: "pending",
      kind: "bend",
    };
    net.wire_graph.points.push(point);
  }
  if (split)
    for (const segment of [...net.wire_graph.segments]) {
      if (segment.from === point.id || segment.to === point.id) continue;
      const i = segment.polyline
        .slice(1)
        .findIndex(
          (b, i) => distance(project(xy, segment.polyline[i], b), xy) < 0.75,
        );
      if (i < 0) continue;
      const oldTo = segment.to,
        right = segment.polyline.slice(i + 1);
      segment.to = point.id;
      segment.polyline = [...segment.polyline.slice(0, i + 1), [...xy]];
      net.wire_graph.segments.push({
        ...segment,
        id: uniqueId(net.wire_graph.segments, "w"),
        from: point.id,
        to: oldTo,
        polyline: [[...xy], ...right],
      });
      point.kind = "junction";
    }
  return point;
}
export function addWire(net: Netlist, a: string, b: string) {
  const p = net.wire_graph.points.find((p) => p.id === a),
    q = net.wire_graph.points.find((p) => p.id === b);
  if (!p || !q || a === b) throw Error("Select distinct points");
  const segment: Segment = {
    id: uniqueId(net.wire_graph.segments, "w"),
    from: a,
    to: b,
    node: "pending",
    polyline: [[...p.xy], [...q.xy]],
    confidence: 1,
  };
  net.wire_graph.segments.push(segment);
  rebuildTopology(net);
  return segment;
}
export function drawWire(net: Netlist, polyline: XY[]) {
  const ids: string[] = [];
  for (let i = 1; i < polyline.length; i++) {
    if (distance(polyline[i - 1], polyline[i]) < 0.5) continue;
    const a = pointAt(net, polyline[i - 1]),
      b = pointAt(net, polyline[i]);
    const s: Segment = {
      id: uniqueId(net.wire_graph.segments, "w"),
      from: a.id,
      to: b.id,
      node: "pending",
      polyline: [[...a.xy], [...b.xy]],
      confidence: 1,
    };
    net.wire_graph.segments.push(s);
    ids.push(s.id);
  }
  rebuildTopology(net);
  return ids;
}
export function cutWire(net: Netlist, id: string) {
  net.wire_graph.segments = net.wire_graph.segments.filter((s) => s.id !== id);
  rebuildTopology(net);
}
export function mergeNodes(
  net: Netlist,
  a: string,
  b: string,
  _connect = true,
) {
  if (a === b) return;
  const left = net.wire_graph.points.filter((p) => p.node === a),
    right = net.wire_graph.points.filter((p) => p.node === b);
  const pairs = left
    .flatMap((p) => right.map((q) => ({ p, q, d: distance(p.xy, q.xy) })))
    .sort((a, b) => a.d - b.d);
  if (pairs[0]) addWire(net, pairs[0].p.id, pairs[0].q.id);
}
function detachEnd(net: Netlist, terminal: Component["terminals"][number]) {
  const old = net.wire_graph.points.find((p) => p.id === terminal.id);
  if (old) {
    const id = uniqueId(net.wire_graph.points, "end");
    old.id = id;
    old.kind = "bend";
    for (const s of net.wire_graph.segments) {
      if (s.from === terminal.id) s.from = id;
      if (s.to === terminal.id) s.to = id;
    }
  }
}
export function moveTerminal(net: Netlist, c: Component, k: number, xy: XY) {
  const terminal = c.terminals[k];
  detachEnd(net, terminal);
  terminal.xy = [...xy];
  rebuildTopology(net);
}
export function attachTerminal(
  net: Netlist,
  c: Component,
  k: number,
  node: string,
  pointId?: string,
) {
  const target =
    net.wire_graph.points.find((p) => p.id === pointId && p.node === node) ||
    net.wire_graph.points.find(
      (p) => p.node === node && p.id !== c.terminals[k].id,
    );
  if (target) moveTerminal(net, c, k, target.xy);
  else splitTerminal(net, c, k);
}
export function splitTerminal(net: Netlist, c: Component, k: number) {
  const a = c.terminals[0].xy,
    b = c.terminals[1].xy,
    l = distance(a, b) || 1;
  const t = c.terminals[k];
  moveTerminal(net, c, k, [
    t.xy[0] - ((b[1] - a[1]) / l) * 12,
    t.xy[1] + ((b[0] - a[0]) / l) * 12,
  ]);
}
export function moveComponent(
  net: Netlist,
  c: Component,
  dx: number,
  dy: number,
) {
  c.bbox = c.bbox.map((v, i) => v + (i % 2 ? dy : dx)) as Component["bbox"];
  c.terminals.forEach((t) => (t.xy = [t.xy[0] + dx, t.xy[1] + dy]));
  rebuildTopology(net);
}
export function removeComponent(net: Netlist, id: string) {
  const c = net.components.find((c) => c.id === id);
  if (!c) return;
  c.terminals.forEach((t) => detachEnd(net, t));
  net.components = net.components.filter((c) => c.id !== id);
  rebuildTopology(net);
}
export function rotateComponent(net: Netlist, c: Component) {
  const x = (c.bbox[0] + c.bbox[2]) / 2,
    y = (c.bbox[1] + c.bbox[3]) / 2,
    w = c.bbox[2] - c.bbox[0],
    h = c.bbox[3] - c.bbox[1];
  c.bbox = [x - h / 2, y - w / 2, x + h / 2, y + w / 2];
  c.terminals.forEach((t) => (t.xy = [x - (t.xy[1] - y), y + (t.xy[0] - x)]));
  c.orientation_deg = (c.orientation_deg + 90) % 360;
  rebuildTopology(net);
}
export function unitFor(type: string) {
  return ["dc_source", "battery", "ac_source", "voltmeter"].includes(type)
    ? "V"
    : type === "current_source" || type === "ammeter" || type === "galvanometer"
      ? "A"
      : type === "capacitor"
        ? "F"
        : type === "inductor"
          ? "H"
          : "ohm";
}
export function addComponent(net: Netlist, type: string, xy: XY): Component {
  const id = uniqueId(
    net.components,
    ["dc_source", "battery", "ac_source"].includes(type)
      ? "V"
      : type === "capacitor"
        ? "C"
        : type === "inductor"
          ? "L"
          : type === "switch"
            ? "S"
            : "R",
  );
  const unit = unitFor(type),
    number =
      unit === "F"
        ? 1e-4
        : unit === "H"
          ? 0.1
          : unit === "V"
            ? 12
            : unit === "A"
              ? 1
              : 100;
  const c: Component = {
    id,
    type,
    label: id,
    bbox: [xy[0] - 25, xy[1] - 12, xy[0] + 25, xy[1] + 12],
    orientation_deg: 0,
    terminals: [
      { id: id + ".a", node: "pending", xy: [xy[0] - 30, xy[1]] },
      { id: id + ".b", node: "pending", xy: [xy[0] + 30, xy[1]] },
    ],
    value: { number, unit, status: "user", source: "user", confidence: 1 },
    polarity: ["dc_source", "battery", "ac_source", "current_source"].includes(
      type,
    )
      ? { positive_terminal: id + ".a" }
      : null,
    switch_closed: true,
    internal_resistance: null,
    initial_voltage: 0,
    initial_current: 0,
    virtual: false,
    confidence: 1,
    disabled: false,
  };
  net.components.push(c);
  rebuildTopology(net);
  return c;
}
export function addBoxComponent(
  net: Netlist,
  type: string,
  box: Component["bbox"],
  radius: number,
) {
  const [x, y, right, bottom] = box,
    c = addComponent(net, type, [(x + right) / 2, (y + bottom) / 2]);
  const vertical = bottom - y > right - x;
  c.bbox = [...box];
  c.orientation_deg = vertical ? 90 : 0;
  const ends: XY[] = vertical
    ? [
        [(x + right) / 2, y],
        [(x + right) / 2, bottom],
      ]
    : [
        [x, (y + bottom) / 2],
        [right, (y + bottom) / 2],
      ];
  c.terminals.forEach(
    (t, i) => (t.xy = snapPoint(net, ends[i], radius, t.id).xy),
  );
  rebuildTopology(net);
  return c;
}
export function crossing(net: Netlist, xy: XY, connect?: boolean) {
  const existing = net.wire_graph.points.find(
    (p) => p.kind === "junction" && distance(p.xy, xy) < 8,
  );
  if (existing && connect !== true) {
    const incident = net.wire_graph.segments.filter(
      (s) => s.from === existing.id || s.to === existing.id,
    );
    const remaining = new Set(incident);
    while (remaining.size) {
      const first = remaining.values().next().value!;
      remaining.delete(first);
      const vector = (s: Segment) => {
        const end = s.from === existing.id ? s.polyline[1] : s.polyline.at(-2)!;
        return [end[0] - existing.xy[0], end[1] - existing.xy[1]];
      };
      const a = vector(first),
        opposite = [...remaining].sort((s, t) => {
          const b = vector(s),
            c = vector(t);
          return (
            (a[0] * b[0] + a[1] * b[1]) / (Math.hypot(...b) || 1) -
            (a[0] * c[0] + a[1] * c[1]) / (Math.hypot(...c) || 1)
          );
        })[0];
      const id = uniqueId(net.wire_graph.points, "cross");
      net.wire_graph.points.push({ ...existing, id, kind: "bend" });
      for (const s of [first, ...(opposite ? [opposite] : [])]) {
        remaining.delete(s);
        if (s.from === existing.id) s.from = id;
        if (s.to === existing.id) s.to = id;
      }
    }
    net.wire_graph.points = net.wire_graph.points.filter(
      (p) => p.id !== existing.id,
    );
  } else if (connect !== false) pointAt(net, xy).kind = "junction";
  net.warnings = net.warnings.filter(
    (w) =>
      !w.ref?.startsWith("xy:") ||
      distance(w.ref.slice(3).split(",").map(Number), xy) > 10,
  );
  rebuildTopology(net);
}
