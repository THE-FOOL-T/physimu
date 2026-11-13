import type { Scene } from "./types";
import { valuePaths, objects } from "./authoring";
import { valueAt } from "./validate";

/** Corrections follow a unique native object match, never an incidental array ID.
 * Unmatched corrections remain named unplaced Values for explicit reassignment. */
export function preserveCorrections(
  previous: Scene,
  next: Scene,
): { scene: Scene; overrides: Record<string, number>; unplaced: string[] } {
  const scene = structuredClone(next),
    mapping = new Map<string, string>();
  const overrides: Record<string, number> = {};
  const candidates = objects(scene);
  const anchor = (o: any): number[] | undefined =>
    o.anchor ?? o.center ?? o.polyline?.[0] ?? o.geometry?.points?.[0];
  for (const old of objects(previous)) {
    const p = anchor(old);
    if (!p) continue;
    const matches = candidates
      .filter((o) => (o as any).type === (old as any).type)
      .map((o) => {
        const q = anchor(o);
        return { o, d: q ? Math.hypot(q[0] - p[0], q[1] - p[1]) : Infinity };
      })
      .sort((a, b) => a.d - b.d);
    if (
      matches[0]?.d <= 20 &&
      (!matches[1] || matches[1].d - matches[0].d > 12) &&
      ![...mapping.values()].includes(matches[0].o.id)
    )
      mapping.set(old.id, matches[0].o.id);
  }
  const unplaced: string[] = [];
  for (const path of valuePaths(previous)) {
    const value = valueAt(previous, path);
    if (value.status !== "user" && value.source !== "user") continue;
    const parts = path.split(".");
    let target: string | null = path;
    if (
      ["bodies", "surfaces", "links", "pulleys", "forces"].includes(parts[0])
    ) {
      target = mapping.has(parts[1])
        ? [parts[0], mapping.get(parts[1]), ...parts.slice(2)].join(".")
        : null;
    } else if (parts[0] === "params" && previous.archetype !== scene.archetype)
      target = null;
    try {
      if (!target) throw new Error("unmatched");
      const destination = valueAt(scene, target);
      if (destination.unit !== value.unit) throw new Error("unit mismatch");
      if (
        scene.bindings.some((b) => b.path === target) &&
        value.number !== null
      )
        overrides[target] = value.number;
      else Object.assign(destination, structuredClone(value));
    } catch {
      let n = 1;
      while (`unplaced_correction_${n}` in scene.params) n++;
      scene.params[`unplaced_correction_${n}`] = structuredClone(value);
      unplaced.push(path);
    }
  }
  // Editable OCR text and label ownership survive when the native label is stable.
  for (const label of previous.annotations.filter(
    (a) => a.type === "label" && a.geometry.text && a.bound_to,
  )) {
    let user = false;
    try {
      user = valueAt(previous, label.bound_to!).status === "user";
    } catch {
      /* Removed target. */
    }
    if (!user || !label.geometry.bbox) continue;
    const box = label.geometry.bbox;
    const match = scene.annotations.find(
      (a) =>
        a.type === "label" &&
        a.geometry.bbox &&
        a.geometry.bbox.every((v, i) => Math.abs(v - box[i]) <= 8),
    );
    if (match) match.geometry.text = label.geometry.text;
  }
  return { scene, overrides, unplaced };
}
