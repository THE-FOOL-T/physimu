import type { Netlist, Component, Segment } from "../types";
export { History } from "./edit-history";
export function normalizeNetlist(input: Netlist): Netlist {
  const net = structuredClone(input);
  net.constraints ??= [];
  net.warnings ??= [];
  net.wire_graph ??= { points: [], segments: [] };
  net.meta = Object.assign(
    {
      problem_text: null,
      language: "en",
      degraded: false,
      style: "unknown",
      region: null,
      provenance: "extracted" as const,
    },
    net.meta,
  );
  if (
    ["automatic", "saved", "example", "synthetic exact geometry"].includes(
      net.meta.provenance,
    )
  )
    net.meta.provenance = "extracted";
  for (const n of net.nodes) n.is_ground ??= false;
  for (const c of net.components) {
    c.label ??= null;
    c.orientation_deg ??= 0;
    c.polarity ??= null;
    c.switch_closed ??= true;
    c.internal_resistance ??= null;
    c.initial_voltage ??= 0;
    c.initial_current ??= 0;
    c.virtual ??= false;
    c.confidence ??= 0;
    c.disabled ??= false;
    c.value ??= {
      number: null,
      unit: "ohm",
      status: "assumed",
      source: "prior",
      confidence: 0,
    };
    c.value.status ??= "assumed";
    c.value.source ??= "prior";
    c.value.confidence ??= 0;
  }
  return net;
}
export const componentTypes = [
  "resistor",
  "rheostat",
  "potentiometer",
  "capacitor",
  "inductor",
  "dc_source",
  "battery",
  "current_source",
  "switch",
  "lamp",
  "ammeter",
  "voltmeter",
  "galvanometer",
  "diode",
  "ac_source",
  "ground",
];
export function assertNetlist(net: Netlist) {
  if (
    net.version !== 1 ||
    !Number.isFinite(net.image?.width) ||
    net.image.width <= 0 ||
    !Number.isFinite(net.image.height) ||
    net.image.height <= 0 ||
    !Array.isArray(net.components) ||
    !net.nodes.length
  )
    throw Error("Invalid netlist");
  const nodes = new Set(net.nodes.map((n) => n.id)),
    points = new Map(net.wire_graph.points.map((p) => [p.id, p]));
  if (
    nodes.size !== net.nodes.length ||
    points.size !== net.wire_graph.points.length ||
    new Set(net.components.map((c) => c.id)).size !== net.components.length
  )
    throw Error("Duplicate ids");
  for (const c of net.components) {
    if (
      c.terminals.length !== 2 ||
      c.terminals.some(
        (t) => !nodes.has(t.node) || t.xy.some((v) => !Number.isFinite(v)),
      ) ||
      (c.value.number !== null && !Number.isFinite(c.value.number))
    )
      throw Error("Invalid component");
  }
  for (const p of points.values())
    if (!nodes.has(p.node) || p.xy.some((v) => !Number.isFinite(v)))
      throw Error("Invalid point");
  for (const s of net.wire_graph.segments)
    if (
      !nodes.has(s.node) ||
      points.get(s.from)?.node !== s.node ||
      points.get(s.to)?.node !== s.node ||
      s.polyline.length < 2 ||
      s.polyline.some((p) => p.some((v) => !Number.isFinite(v)))
    )
      throw Error("Invalid segment");
}

export {
  uniqueId,
  mergeNodes,
  attachTerminal,
  splitTerminal,
  addComponent,
  addWire,
  cutWire,
} from "./edit-geometry";
export { rebuildTopology } from "./topology";
