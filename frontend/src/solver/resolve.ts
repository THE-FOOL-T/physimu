import type { Netlist } from "../types";
import { solve } from "./mna";
const priors: Record<string, number> = {
  resistor: 10,
  rheostat: 10,
  potentiometer: 10,
  capacitor: 1e-5,
  inductor: 0.1,
  dc_source: 12,
  battery: 12,
  current_source: 1,
};
function linear(A: number[][], b: number[]) {
  const n = b.length,
    a = A.map((r, i) => [...r, b[i]]);
  for (let k = 0; k < n; k++) {
    let pivot = k;
    for (let i = k + 1; i < n; i++)
      if (Math.abs(a[i][k]) > Math.abs(a[pivot][k])) pivot = i;
    [a[k], a[pivot]] = [a[pivot], a[k]];
    if (Math.abs(a[k][k]) < 1e-25) return Array(n).fill(0);
    for (let i = k + 1; i < n; i++) {
      const f = a[i][k] / a[k][k];
      for (let j = k; j <= n; j++) a[i][j] -= f * a[k][j];
    }
  }
  const x = Array(n).fill(0);
  for (let i = n - 1; i >= 0; i--) {
    x[i] =
      (a[i][n] -
        a[i].slice(i + 1, n).reduce((s, v, j) => s + v * x[j + i + 1], 0)) /
      a[i][i];
  }
  return x;
}
export function resolveLocal(input: Netlist, keep = true): Netlist {
  const net = structuredClone(input),
    unknown = net.components.filter(
      (c) =>
        !c.disabled &&
        c.value.status !== "user" &&
        (c.value.number === null || (keep && c.value.status === "solved")),
    );
  const prior = unknown.map((c) =>
    Math.log(Math.max(c.value.number ?? priors[c.type] ?? 10, 1e-12)),
  );
  let x = [...prior];
  function residual(x: number[]) {
    unknown.forEach(
      (c, j) => (c.value.number = Math.exp(Math.max(-30, Math.min(30, x[j])))),
    );
    const out = solve(net),
      byid = new Map(
        net.components.flatMap(
          (c) =>
            [
              [c.id, c],
              [c.label || c.id, c],
            ] as const,
        ),
      );
    return net.constraints.map((con) => {
      const c = byid.get(con.target),
        r = c && out.components[c.id];
      let value = 0;
      if (con.target === "total" && con.type === "power")
        value = out.total_power_consumed;
      else if (con.target === "total" && con.type === "current")
        value = net.components
          .filter(
            (c) =>
              ["dc_source", "battery", "ac_source"].includes(c.type) &&
              !c.disabled,
          )
          .reduce(
            (s, c) => s + Math.abs(out.components[c.id]?.current || 0),
            0,
          );
      else if (r && ["current", "voltage", "power"].includes(con.type)) {
        value =
          con.type === "current"
            ? r.current
            : con.type === "voltage"
              ? r.v_drop
              : r.power;
        if (con.value >= 0) value = Math.abs(value);
      } else if (con.type === "equivalent_resistance")
        value = out.equivalent_resistance || 0;
      else if (con.type === "ratio") {
        const [a, b] = con.target.split("/");
        value =
          (byid.get(a)?.value.number || 0) /
          Math.max(byid.get(b)?.value.number || 1e-30, 1e-30);
      } else if (con.type === "voltage") {
        const [a, b] = con.target.split("-");
        const node = (label: string) =>
          net.nodes.find((n) => n.label === label)?.id || label;
        value =
          (out.node_voltages[node(a)] || 0) - (out.node_voltages[node(b)] || 0);
      }
      return (value - con.value) / Math.max(1, Math.abs(con.value));
    });
  }
  if (!unknown.length) {
    if (
      residual([]).some((v) => Math.abs(v) > 1e-4) &&
      !net.warnings.some((w) => w.code === "inconsistent_constraints")
    )
      net.warnings.push({
        code: "inconsistent_constraints",
        ref: null,
        message_key: "warn.inconsistent_constraints",
      });
    return net;
  }
  let J: number[][] = [];
  let damping = 1e-4;
  if (net.constraints.length) {
    for (let iter = 0; iter < 50; iter++) {
      const r = residual(x),
        norm = r.reduce((s, v) => s + v * v, 0);
      J = r.map(() => Array(x.length).fill(0));
      for (let j = 0; j < x.length; j++) {
        const shifted = [...x];
        shifted[j] += 1e-5;
        const b = residual(shifted);
        for (let i = 0; i < r.length; i++) J[i][j] = (b[i] - r[i]) / 1e-5;
      }
      if (norm < 1e-20) break;
      const A = x.map((_, j) =>
          x.map(
            (_, k) =>
              J.reduce((s, row) => s + row[j] * row[k], 0) +
              (j === k ? damping : 0),
          ),
        ),
        b = x.map((_, j) => -J.reduce((s, row, i) => s + row[j] * r[i], 0));
      const step = linear(A, b),
        next = x.map((v, j) =>
          Math.max(-30, Math.min(30, v + Math.max(-2, Math.min(2, step[j])))),
        );
      if (residual(next).reduce((s, v) => s + v * v, 0) < norm) {
        x = next;
        damping = Math.max(1e-12, damping / 3);
      } else damping *= 10;
    }
  }
  const r = residual(x),
    inconsistent = r.some((v) => Math.abs(v) > 1e-4);
  // RREF identifies whether each parameter appears in any Jacobian null direction.
  const matrix = J.map((row) => [...row]),
    pivots: number[] = [];
  let row = 0;
  for (let col = 0; col < x.length && row < matrix.length; col++) {
    let p = row;
    for (let i = row + 1; i < matrix.length; i++)
      if (Math.abs(matrix[i][col]) > Math.abs(matrix[p][col])) p = i;
    if (Math.abs(matrix[p][col]) < 1e-7) continue;
    [matrix[row], matrix[p]] = [matrix[p], matrix[row]];
    const scale = matrix[row][col];
    matrix[row] = matrix[row].map((v) => v / scale);
    for (let i = 0; i < matrix.length; i++)
      if (i !== row) {
        const f = matrix[i][col];
        matrix[i] = matrix[i].map((v, j) => v - f * matrix[row][j]);
      }
    pivots.push(col);
    row++;
  }
  const free = x.map((_, i) => i).filter((i) => !pivots.includes(i));
  unknown.forEach((c, j) => {
    const pr = pivots.indexOf(j),
      determined =
        pr >= 0 &&
        free.every((k) => Math.abs(matrix[pr][k]) < 1e-6) &&
        !inconsistent;
    c.value.status = determined ? "solved" : "assumed";
    c.value.source = determined ? "constraint" : "prior";
    c.value.confidence = determined ? 0.9 : 0.2;
  });
  if (
    inconsistent &&
    !net.warnings.some((w) => w.code === "inconsistent_constraints")
  )
    net.warnings.push({
      code: "inconsistent_constraints",
      ref: null,
      message_key: "warn.inconsistent_constraints",
    });
  return net;
}
