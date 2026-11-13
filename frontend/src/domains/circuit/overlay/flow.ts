import type { Netlist, Solution } from "../types";

export type FlowStyle = "dots" | "dashes" | "arrows" | "glow";
export type FlowColor = "amber" | "cyan" | "lime" | "magenta";
export type FlowSettings = { style: FlowStyle; color: FlowColor; size: number };
export const defaultFlow: FlowSettings = {
  style: "dots",
  color: "amber",
  size: 1,
};
export const flowing = (current: number) =>
  Number.isFinite(current) && Math.abs(current) > 1e-15;
export const flowColors = {
  amber: ["#FFB300", "#FFD54F"],
  cyan: ["#00B8D4", "#80DEEA"],
  lime: ["#B3CF00", "#D4E157"],
  magenta: ["#E4007C", "#FF80AB"],
} as const;

export function readFlow(): FlowSettings {
  try {
    const saved = JSON.parse(localStorage.getItem("circuit-flow") || "null");
    return {
      style: ["dots", "dashes", "arrows", "glow"].includes(saved?.style)
        ? saved.style
        : "dots",
      color: saved?.color in flowColors ? saved.color : "amber",
      size: [0.8, 1, 1.25].includes(saved?.size) ? saved.size : 1,
    };
  } catch {
    return { ...defaultFlow };
  }
}
export function saveFlow(settings: FlowSettings) {
  try {
    localStorage.setItem("circuit-flow", JSON.stringify(settings));
  } catch {
    /* Preferences are optional. */
  }
}
export function smoothReference(
  previous: number | null,
  currents: number[],
  elapsed: number,
): number {
  const sorted = currents
    .map(Math.abs)
    .filter(flowing)
    .sort((a, b) => a - b);
  const median = sorted[Math.floor(sorted.length / 2)];
  if (!median) return previous ?? 0;
  if (!previous) return median;
  return (
    previous + (median - previous) * (1 - Math.exp(-Math.max(0, elapsed) * 5))
  );
}
type FlowSegment = { id: string; length: number; current: number };
/** Largest-remainder allocation is independent of input order and never starves a live wire.
 * If there are more live wires than the soft cap, one per wire takes precedence. */
export function particleBudget(
  segments: FlowSegment[],
  reference: number,
  cap = 500,
): Map<string, number> {
  const active = segments
    .filter((s) => s.length > 0 && flowing(s.current))
    .sort((a, b) => a.id.localeCompare(b.id));
  const weights = active.map(
    (s) =>
      Math.max(1, s.length) *
      Math.max(
        0.25,
        Math.min(
          4,
          Math.log1p(Math.abs(s.current) / Math.max(reference, 1e-15)),
        ),
      ),
  );
  const desired = active.reduce(
      (sum, s) => sum + Math.max(1, Math.ceil(s.length / 42)),
      0,
    ),
    extra = Math.max(
      0,
      Math.min(desired, Math.max(cap, active.length)) - active.length,
    ),
    total = weights.reduce((a, b) => a + b, 0);
  const rows = active.map((s, i) => {
    const share = (extra * weights[i]) / total;
    return {
      id: s.id,
      count: 1 + Math.floor(share),
      fraction: share - Math.floor(share),
    };
  });
  let left = extra - rows.reduce((sum, r) => sum + r.count - 1, 0);
  for (const row of [...rows].sort(
    (a, b) => b.fraction - a.fraction || a.id.localeCompare(b.id),
  ))
    if (left-- > 0) row.count++;
  return new Map(rows.map((r) => [r.id, r.count]));
}
export function contrast(a: string, b: string): number {
  const luminance = (hex: string) => {
    const rgb = [1, 3, 5]
      .map((i) => parseInt(hex.slice(i, i + 2), 16) / 255)
      .map((v) => (v <= 0.04045 ? v / 12.92 : ((v + 0.055) / 1.055) ** 2.4));
    return rgb[0] * 0.2126 + rgb[1] * 0.7152 + rgb[2] * 0.0722;
  };
  const x = luminance(a),
    y = luminance(b);
  return (Math.max(x, y) + 0.05) / (Math.min(x, y) + 0.05);
}
export function voltageTint(v: number, lo: number, hi: number): string {
  const f = hi > lo ? Math.max(0, Math.min(1, (v - lo) / (hi - lo))) : 0.5;
  const a = [95, 125, 142],
    b = [155, 113, 91];
  return (
    "#" +
    a
      .map((n, i) =>
        Math.round(n + (b[i] - n) * f)
          .toString(16)
          .padStart(2, "0"),
      )
      .join("")
  );
}
export const blendWhite = (hex: string) =>
  "#" +
  [1, 3, 5]
    .map((i) =>
      Math.round((255 + parseInt(hex.slice(i, i + 2), 16)) / 2)
        .toString(16)
        .padStart(2, "0"),
    )
    .join("");
export const flowOutline = "#3B2A00";

export function drawFlow(
  ctx: CanvasRenderingContext2D,
  net: Netlist,
  solution: Solution,
  options: {
    scale: number;
    zoom: number;
    elapsed: number;
    now: number;
    reference: number;
    settings: FlowSettings;
    offsets: Map<string, number>;
    paused: boolean;
    reduced: boolean;
    electron: boolean;
    editing: boolean;
    dark: boolean;
  },
): number {
  const {
    scale,
    zoom,
    elapsed,
    now,
    reference,
    settings,
    offsets,
    paused,
    reduced,
    electron,
    editing,
    dark,
  } = options;
  const voltages = Object.values(solution.node_voltages),
    lo = Math.min(0, ...voltages),
    hi = Math.max(1, ...voltages),
    shorts = new Set(
      solution.short_circuit.short_paths.flatMap((p) => p.segments),
    );
  const paths = net.wire_graph.segments.map((segment) => {
    const lengths = segment.polyline
      .slice(1)
      .map((p, k) =>
        Math.hypot(
          p[0] - segment.polyline[k][0],
          p[1] - segment.polyline[k][1],
        ),
      );
    return {
      segment,
      lengths,
      length: lengths.reduce((a, b) => a + b, 0),
      current: solution.segment_currents[segment.id] || 0,
    };
  });
  const counts = particleBudget(
    paths.map((p) => ({
      id: p.segment.id,
      length: p.length * scale,
      current: p.current,
    })),
    reference,
  );
  const present = new Set(paths.map((p) => p.segment.id));
  for (const id of offsets.keys()) if (!present.has(id)) offsets.delete(id);
  let drawn = 0;
  for (const { segment, lengths, length, current } of paths) {
    if (!length) continue;
    const short = shorts.has(segment.id),
      active = flowing(current),
      color = short ? "#E4007C" : flowColors[settings.color][dark ? 1 : 0],
      sign = Math.sign(current) * (electron ? -1 : 1),
      radius =
        Math.max(2.8, Math.min(6, 4 * settings.size * Math.sqrt(zoom))) / scale;
    const at = (distance: number): [number, number, number] => {
      let n = ((distance % length) + length) % length;
      for (let k = 0; k < lengths.length; k++) {
        if (n <= lengths[k] || k === lengths.length - 1) {
          const a = segment.polyline[k],
            b = segment.polyline[k + 1],
            f = n / (lengths[k] || 1);
          return [
            a[0] + (b[0] - a[0]) * f,
            a[1] + (b[1] - a[1]) * f,
            Math.atan2(b[1] - a[1], b[0] - a[0]),
          ];
        }
        n -= lengths[k];
      }
      return [0, 0, 0];
    };
    ctx.save();
    ctx.beginPath();
    ctx.moveTo(...segment.polyline[0]);
    for (const p of segment.polyline.slice(1)) ctx.lineTo(...p);
    if (!active) {
      // Clear the narrow underlying printed wire so gaps remain visible.
      ctx.strokeStyle = "#FFFFFF";
      ctx.lineWidth = 3.5 / scale;
      ctx.stroke();
    }
    ctx.lineWidth = (short ? 2.5 : 1.6) / scale;
    ctx.strokeStyle = short
      ? "#E4007C"
      : active
        ? voltageTint(solution.node_voltages[segment.node] || 0, lo, hi)
        : "#7D8790";
    ctx.globalAlpha = short ? 0.85 : active ? 0.5 : 0.9;
    ctx.setLineDash(
      !active
        ? [5 / scale, 6 / scale]
        : segment.confidence < 0.6
          ? [5 / scale, 3 / scale]
          : [],
    );
    if (short && !reduced) {
      ctx.shadowColor = "#E4007C";
      ctx.shadowBlur = 5 + 3 * Math.sin(now / 200);
    }
    ctx.stroke();
    ctx.setLineDash([]);
    ctx.shadowBlur = 0;
    if (!active) {
      ctx.restore();
      continue;
    }
    const speed =
        Math.max(
          24,
          Math.min(
            160,
            35 +
              65 * Math.log1p(Math.abs(current) / Math.max(reference, 1e-15)),
          ),
        ) / scale,
      offset =
        ((offsets.get(segment.id) || 0) +
          (paused || reduced ? 0 : elapsed * sign * speed)) %
        length;
    offsets.set(segment.id, offset);
    const allocated = counts.get(segment.id) || 1;
    const count = reduced
      ? Math.min(allocated, Math.max(1, Math.ceil((length * scale) / 110)))
      : allocated;
    for (let k = 0; k < count; k++) {
      const distance = (k * length) / count + offset,
        [x, y, angle] = at(distance),
        arrow = reduced || settings.style === "arrows";
      ctx.globalAlpha = editing ? 0.35 : 1;
      if (!reduced && !arrow) {
        // Tail samples follow bends instead of cutting diagonally across a corner.
        for (let tail = 5; tail >= 1; tail--) {
          const [tx, ty] = at(distance - (sign * tail * 3) / scale);
          ctx.globalAlpha = (editing ? 0.35 : 1) * (0.45 - tail * 0.065);
          ctx.beginPath();
          ctx.arc(tx, ty, radius * (1 - tail * 0.12), 0, Math.PI * 2);
          ctx.fillStyle = color;
          ctx.fill();
        }
        ctx.globalAlpha = editing ? 0.35 : 1;
      }
      ctx.save();
      ctx.translate(x, y);
      ctx.rotate(angle + (sign < 0 ? Math.PI : 0));
      ctx.fillStyle = color;
      ctx.strokeStyle = short ? "#FFFFFF" : flowOutline;
      ctx.lineWidth = (short ? 1.6 : 1.2) / scale;
      ctx.shadowColor = color;
      ctx.shadowBlur = (settings.style === "glow" ? 12 : 5) * settings.size;
      ctx.beginPath();
      if (arrow) {
        ctx.moveTo(radius * 1.7, 0);
        ctx.lineTo(-radius, -radius);
        ctx.lineTo(-radius * 0.4, 0);
        ctx.lineTo(-radius, radius);
        ctx.closePath();
      } else if (settings.style === "dashes") {
        ctx.roundRect(
          -radius * 1.7,
          -radius * 0.65,
          radius * 3.4,
          radius * 1.3,
          radius * 0.5,
        );
      } else ctx.arc(0, 0, radius, 0, Math.PI * 2);
      // A dark outer boundary stays visible on white uploaded paper in either UI theme.
      if (dark && !short) {
        ctx.strokeStyle = flowOutline;
        ctx.lineWidth = 2.8 / scale;
        ctx.stroke();
        ctx.strokeStyle = "#FFF4C4";
        ctx.lineWidth = 0.8 / scale;
      }
      ctx.fill();
      ctx.stroke();
      ctx.restore();
      drawn++;
    }
    ctx.restore();
  }
  return drawn;
}
