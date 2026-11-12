import type { Netlist, Component, Solution, Warning, Reading } from "../types";
import { segmentCurrents, decomposePaths } from "./flow";
type SolvedSolution = Omit<Solution, "invariants"> & {
  invariants: Omit<
    Solution["invariants"],
    "max_kcl_error" | "relative_power_error"
  > & {
    max_kcl_error: number;
    relative_power_error: number;
  };
};
export const voltageTypes = new Set(["dc_source", "battery", "ac_source"]);
const resistive = new Set([
    "resistor",
    "rheostat",
    "potentiometer",
    "lamp",
    "fuse",
  ]),
  meters = new Set(["ammeter", "galvanometer"]);
export const supported = new Set([
  ...voltageTypes,
  ...resistive,
  ...meters,
  "switch",
  "voltmeter",
  "capacitor",
  "inductor",
  "current_source",
  "ground",
]);
function gaussian(A: number[][], rhs: number[]): number[] {
  const a = A.map((r, i) => [...r, rhs[i]]),
    n = a.length;
  for (let k = 0; k < n; k++) {
    let p = k;
    for (let i = k + 1; i < n; i++)
      if (Math.abs(a[i][k]) > Math.abs(a[p][k])) p = i;
    if (Math.abs(a[p][k]) < 1e-20) throw Error("singular");
    [a[k], a[p]] = [a[p], a[k]];
    for (let i = k + 1; i < n; i++) {
      const f = a[i][k] / a[k][k];
      for (let j = k + 1; j <= n; j++) a[i][j] -= f * a[k][j];
      a[i][k] = 0;
    }
  }
  const x = Array(n).fill(0);
  for (let i = n - 1; i >= 0; i--) {
    let y = a[i][n];
    for (let j = i + 1; j < n; j++) y -= a[i][j] * x[j];
    x[i] = y / a[i][i];
  }
  return x;
}
function lowPath(
  net: Netlist,
  a: string,
  b: string,
  exclude: string,
): string[] | null {
  if (a === b) return [];
  const queue: [string, string[]][] = [[a, []]],
    seen = new Set([a]);
  for (const [p, path] of queue)
    for (const c of net.components) {
      if (
        c.disabled ||
        c.id === exclude ||
        !((c.type === "switch" && c.switch_closed) || meters.has(c.type))
      )
        continue;
      const [x, y] = c.terminals.map((t) => t.node),
        q = x === p ? y : y === p ? x : null;
      if (q === null) continue;
      if (q === b) return [...path, c.id];
      if (!seen.has(q)) {
        seen.add(q);
        queue.push([q, [...path, c.id]]);
      }
    }
  return null;
}
export function solve(
  net: Netlist,
  dt?: number,
  state: Record<string, number> = {},
): SolvedSolution {
  const warnings: Warning[] = structuredClone(net.warnings);
  const warn = (code: string, ref: string | null = null) => {
    if (!warnings.some((w) => w.code === code && w.ref === ref))
      warnings.push({ code, ref, message_key: "warn." + code });
  };
  const cs = net.components.filter((c) => !c.disabled),
    source = cs.find((c) => voltageTypes.has(c.type));
  let ground = net.nodes.find((n) => n.is_ground)?.id;
  if (!ground) {
    ground = source
      ? source.terminals[
          source.polarity?.positive_terminal === source.terminals[1].id ? 0 : 1
        ].node
      : net.nodes[0]?.id;
    warn("assumed_ground", ground);
  }
  const ids = net.nodes.filter((n) => n.id !== ground).map((n) => n.id),
    index = new Map(ids.map((n, i) => [n, i]));
  const vs = cs.filter(
    (c) => voltageTypes.has(c.type) || (c.type === "inductor" && dt),
  );
  const branches = new Map(vs.map((c, i) => [c.id, ids.length + i]));
  const size = ids.length + vs.length;
  const A = Array.from({ length: size }, () => Array(size).fill(0)),
    z = Array(size).fill(0),
    conductance: Record<string, number> = {},
    history: Record<string, number> = {},
    internal: Record<string, number> = {};
  const shorts: string[] = [],
    bypassed: string[] = [],
    connectivity = new Map(net.nodes.map((n) => [n.id, new Set<string>()]));
  const add = (r: number | undefined, c: number | undefined, v: number) => {
    if (r !== undefined && c !== undefined) A[r][c] += v;
  };
  const inject = (a: number | undefined, b: number | undefined, i: number) => {
    if (a !== undefined) z[a] -= i;
    if (b !== undefined) z[b] += i;
  };
  for (const c of cs) {
    const [na, nb] = c.terminals.map((t) => t.node),
      a = index.get(na),
      b = index.get(nb),
      value = c.value.number ?? (resistive.has(c.type) ? 10 : 1);
    if (!supported.has(c.type)) {
      warn("unsupported_component", c.id);
      continue;
    }
    const path = lowPath(net, na, nb, c.id);
    if (
      path !== null &&
      !voltageTypes.has(c.type) &&
      !meters.has(c.type) &&
      !["switch", "ground"].includes(c.type)
    )
      bypassed.push(c.id);
    let g = 0,
      h = 0;
    if (resistive.has(c.type)) g = 1 / Math.max(Math.abs(value), 1e-9);
    else if (c.type === "switch") g = 1 / (c.switch_closed ? 0.001 : 1e9);
    else if (meters.has(c.type)) g = 1e6;
    else if (c.type === "voltmeter") g = 1e-9;
    else if (c.type === "inductor" && !dt) g = 1e6;
    else if (c.type === "capacitor" && dt) {
      g = Math.max(value, 1e-15) / dt;
      h = -g * (state[c.id] ?? c.initial_voltage);
    } else if (c.type === "current_source")
      h =
        value * (c.polarity?.positive_terminal === c.terminals[1].id ? -1 : 1);
    if (g) {
      add(a, a, g);
      add(b, b, g);
      add(a, b, -g);
      add(b, a, -g);
    }
    if (h) inject(a, b, h);
    conductance[c.id] = g;
    history[c.id] = h;
    if (g || branches.has(c.id)) {
      connectivity.get(na)!.add(nb);
      connectivity.get(nb)!.add(na);
    }
    if (branches.has(c.id)) {
      const k = branches.get(c.id)!;
      add(a, k, 1);
      add(b, k, -1);
      add(k, a, 1);
      add(k, b, -1);
      if (c.type === "inductor") {
        const r = Math.max(value, 1e-15) / dt!;
        A[k][k] = -r;
        z[k] = -r * (state[c.id] ?? c.initial_current);
      } else {
        let r = c.internal_resistance || 0;
        if (path !== null) {
          if (!r) r = 0.05;
          shorts.push(c.id);
          warn("source_short", c.id);
        }
        const e =
          value *
          (c.polarity?.positive_terminal === c.terminals[1].id ? -1 : 1);
        A[k][k] = -r;
        z[k] = e;
        internal[c.id] = r;
        if (c.type === "ac_source") warn("unsupported_ac", c.id);
      }
    }
  }
  const reached = new Set<string>(),
    leak: Record<string, number> = {};
  function reach(n: string) {
    const stack = [n];
    while (stack.length) {
      const p = stack.pop()!;
      if (reached.has(p)) continue;
      reached.add(p);
      stack.push(...connectivity.get(p)!);
    }
  }
  if (ground) reach(ground);
  for (const n of ids)
    if (!reached.has(n)) {
      A[index.get(n)!][index.get(n)!] += 1e-9;
      leak[n] = 1e-9;
      warn("floating_node", n);
      reach(n);
    }
  let x: number[];
  try {
    x = gaussian(A, z);
  } catch {
    for (const c of vs)
      if (voltageTypes.has(c.type) && !internal[c.id]) {
        A[branches.get(c.id)!][branches.get(c.id)!] = -0.001;
        internal[c.id] = 0.001;
        warn("conflicting_sources", c.id);
      }
    x = gaussian(A, z);
  }
  const voltages: Record<string, number> = Object.fromEntries(
    net.nodes.map((n) => [n.id, n.id === ground ? 0 : x[index.get(n.id)!]]),
  );
  const readings: Record<string, Reading> = {},
    kcl: Record<string, number> = Object.fromEntries(
      net.nodes.map((n) => [n.id, 0]),
    ),
    newState: Record<string, number> = {};
  let consumed = 0,
    supplied = 0,
    losses = 0;
  for (const c of cs) {
    const [na, nb] = c.terminals.map((t) => t.node),
      v = voltages[na] - voltages[nb],
      i = branches.has(c.id)
        ? x[branches.get(c.id)!]
        : (conductance[c.id] || 0) * v + (history[c.id] || 0),
      p = v * i,
      loss = i * i * (internal[c.id] || 0);
    losses += loss;
    readings[c.id] = {
      v_drop: v,
      current: i,
      power: p,
      internal_power: loss,
      internal_resistance: internal[c.id] || 0,
      deflection: Math.sign(i),
    };
    consumed += Math.max(0, p);
    supplied += Math.max(0, -p);
    kcl[na] += i;
    kcl[nb] -= i;
    if (c.type === "capacitor") newState[c.id] = v;
    if (c.type === "inductor") newState[c.id] = i;
  }
  let leakPower = 0;
  for (const [n, g] of Object.entries(leak)) {
    const current = g * voltages[n];
    kcl[n] += current;
    if (ground) kcl[ground] -= current;
    leakPower += g * voltages[n] ** 2;
  }
  consumed += losses + leakPower;
  supplied += losses;
  const flow = segmentCurrents(net, readings);
  warnings.push(...flow.warnings);
  const paths = decomposePaths(
    net,
    readings,
    flow.currents,
    shorts.length || bypassed.length
      ? cs.filter((c) => voltageTypes.has(c.type)).map((c) => c.id)
      : [],
  );
  const kclError = Math.max(0, ...Object.values(kcl).map(Math.abs)),
    powerError =
      Math.abs(consumed - supplied) / Math.max(consumed, supplied, 1e-30);
  if (
    kclError >
    Math.max(
      1e-10,
      Math.max(0, ...Object.values(readings).map((r) => Math.abs(r.current))) *
        1e-9,
    )
  )
    warn("kcl_residual");
  if (powerError > 1e-9) warn("power_residual");
  return {
    node_voltages: voltages,
    components: readings,
    segment_currents: flow.currents,
    total_power_supplied: supplied,
    total_power_consumed: consumed,
    internal_power: losses,
    equivalent_resistance:
      source && Math.abs(readings[source.id].current) > 1e-15
        ? Math.abs(readings[source.id].v_drop / readings[source.id].current)
        : null,
    short_circuit: {
      detected: !!(shorts.length || bypassed.length),
      sources: shorts,
      bypassed,
      short_paths: paths,
      ideal_current_infinite: !!shorts.length,
    },
    state: newState,
    warnings,
    invariants: {
      kcl,
      max_kcl_error: kclError,
      relative_power_error: powerError,
      regularization_power: leakPower,
    },
  };
}
export function transient(
  net: Netlist,
  duration?: number,
  steps?: number,
  state?: Record<string, number>,
) {
  const rs = net.components
    .filter((c) => resistive.has(c.type))
    .map((c) => Math.max(c.value.number || 10, 1e-6));
  const taus = net.components
    .filter((c) => ["capacitor", "inductor"].includes(c.type))
    .map((c) =>
      c.type === "capacitor"
        ? (c.value.number || 1e-6) * (rs.length ? Math.max(...rs) : 10)
        : (c.value.number || 0.001) / (rs.length ? Math.min(...rs) : 10),
    );
  duration = duration || 5 * (taus.length ? Math.max(...taus) : 1);
  const required = Math.ceil(
      duration / Math.max((taus.length ? Math.min(...taus) : 1) / 100, 1e-15),
    ),
    limited = steps === undefined && required > 5000;
  steps = Math.max(2, Math.min(5000, steps ?? required));
  const dt = duration / steps;
  state = {
    ...(state ||
      Object.fromEntries(
        net.components
          .filter((c) => ["capacitor", "inductor"].includes(c.type))
          .map((c) => [
            c.id,
            c.type === "capacitor" ? c.initial_voltage : c.initial_current,
          ]),
      )),
  };
  const samples: {
    time: number;
    state: Record<string, number>;
    components?: Record<string, Reading>;
  }[] = [{ time: 0, state: { ...state } }];
  let solution!: Solution;
  for (let k = 1; k <= steps; k++) {
    solution = solve(net, dt, state);
    state = solution.state;
    samples.push({
      time: k * dt,
      state: { ...state },
      components: solution.components,
    });
  }
  if (limited)
    solution.warnings.push({
      code: "time_step_limited",
      ref: null,
      message_key: "warn.time_step_limited",
    });
  return { duration, dt, samples, solution, steady_state: solve(net) };
}
