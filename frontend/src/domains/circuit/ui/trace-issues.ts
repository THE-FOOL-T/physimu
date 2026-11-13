import type { Netlist, Warning } from "../types";

export interface GhostPart {
  bbox: [number, number, number, number];
  from: [number, number];
  to: [number, number];
  reason: string;
}
export interface TraceIssue {
  id: string;
  code: string;
  ref: string | null;
  xy: [number, number];
  bbox?: GhostPart["bbox"];
}
export function traceIssues(
  net: Netlist,
  warnings: Warning[],
  ghosts: GhostPart[] = [],
): TraceIssue[] {
  const result: TraceIssue[] = [];
  const add = (
    code: string,
    ref: string | null,
    xy: [number, number],
    bbox?: GhostPart["bbox"],
  ) => {
    if (
      result.some(
        (i) =>
          i.code === code && Math.hypot(i.xy[0] - xy[0], i.xy[1] - xy[1]) < 5,
      )
    )
      return;
    result.push({ id: `issue-${result.length}`, code, ref, xy, bbox });
  };
  const terminals = new Set(
    net.components.flatMap((c) => c.terminals.map((t) => t.id)),
  );
  const degree = new Map(net.wire_graph.points.map((p) => [p.id, 0]));
  for (const segment of net.wire_graph.segments) {
    degree.set(segment.from, (degree.get(segment.from) || 0) + 1);
    degree.set(segment.to, (degree.get(segment.to) || 0) + 1);
  }
  for (const point of net.wire_graph.points) {
    const touches = net.components.some((c) =>
      c.terminals.some(
        (t) => Math.hypot(t.xy[0] - point.xy[0], t.xy[1] - point.xy[1]) < 2,
      ),
    );
    if ((degree.get(point.id) || 0) <= 1 && !touches)
      add("dangling_wire", point.id, point.xy);
    if (
      terminals.has(point.id) &&
      (point.node.startsWith("isolated.") || !degree.get(point.id))
    )
      add("uncertain_topology", point.id, point.xy);
  }
  for (const warning of warnings) {
    const match = warning.ref?.match(/^xy:([\d.-]+),([\d.-]+)$/);
    if (match)
      add(warning.code, warning.ref, [Number(match[1]), Number(match[2])]);
    else if (warning.code === "source_open_loop") {
      const component = net.components.find((c) => c.id === warning.ref);
      if (component)
        add(warning.code, warning.ref, [
          (component.bbox[0] + component.bbox[2]) / 2,
          (component.bbox[1] + component.bbox[3]) / 2,
        ]);
    }
  }
  for (const ghost of ghosts)
    add(
      "missing_part",
      null,
      [
        (ghost.bbox[0] + ghost.bbox[2]) / 2,
        (ghost.bbox[1] + ghost.bbox[3]) / 2,
      ],
      ghost.bbox,
    );
  return result;
}
export function issueAt(
  issues: TraceIssue[],
  x: number,
  y: number,
  radius: number,
) {
  return issues.find((i) => Math.hypot(x - i.xy[0], y - i.xy[1]) <= radius);
}
export function drawTraceIssues(
  ctx: CanvasRenderingContext2D,
  issues: TraceIssue[],
  scale: number,
  active: string,
  phase = 0,
) {
  ctx.save();
  for (const issue of issues) {
    ctx.strokeStyle = issue.id === active ? "#A63C00" : "#C87000";
    ctx.lineWidth = 2 / scale;
    ctx.setLineDash(issue.bbox ? [5 / scale, 3 / scale] : []);
    if (issue.bbox)
      ctx.strokeRect(
        issue.bbox[0],
        issue.bbox[1],
        issue.bbox[2] - issue.bbox[0],
        issue.bbox[3] - issue.bbox[1],
      );
    ctx.beginPath();
    ctx.arc(
      ...issue.xy,
      (8 + Math.sin(phase * 4) * 1.5) / scale,
      0,
      Math.PI * 2,
    );
    ctx.stroke();
  }
  ctx.restore();
}
