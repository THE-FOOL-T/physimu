import type { ArchetypeModule } from "../types";
import {
  guarded,
  mass,
  read,
  scale,
  initial,
  state,
  trajectory,
  info,
} from "./common";
import { layout } from "../layout";

export const collision1d: ArchetypeModule = {
  id: "collision_1d",
  defaultBindings: (s) => structuredClone(s.bindings),
  layout,
  solve(s, p) {
    return guarded(s, p, () => {
      if (s.bodies.length !== 2)
        throw new Error("collision_requires_two_bodies");
      const [b1, b2] = s.bodies,
        m1 = mass(s, p, b1.id),
        m2 = mass(s, p, b2.id),
        S = scale(s, p);
      const e = read(s, p, "params.restitution");
      if (e < 0 || e > 1) throw new Error("invalid_restitution");
      const x1 = initial(s, b1.id, "position").x,
        x2 = initial(s, b2.id, "position").x;
      const v1 = read(s, p, `bodies.${b1.id}.initial.velocity.x`),
        v2 = read(s, p, `bodies.${b2.id}.initial.velocity.x`);
      const half =
          (b1.bbox[2] - b1.bbox[0] + (b2.bbox[2] - b2.bbox[0])) / (2 * S),
        gap = x2 - x1 - half;
      if (gap < 0) throw new Error("initial_body_overlap");
      const contact = v1 > v2 ? gap / (v1 - v2) : Infinity;
      const w1 = (m1 * v1 + m2 * v2 + m2 * e * (v2 - v1)) / (m1 + m2),
        w2 = (m1 * v1 + m2 * v2 + m1 * e * (v1 - v2)) / (m1 + m2);
      const warnings: string[] = [];
      for (const c of s.constraints.filter(
        (c) => c.type === "after_velocity",
      )) {
        for (const [id, v] of Object.entries(c.values)) {
          const actual = id === b1.id ? w1 : id === b2.id ? w2 : NaN;
          if (
            v.number === null ||
            Math.abs(actual - v.number) > 1e-6 * Math.max(1, Math.abs(actual))
          )
            warnings.push("after_panel_mismatch");
        }
      }
      const duration = Math.max(
        2,
        Number.isFinite(contact) ? Math.min(contact + 2, 10) : 2,
      );
      const event =
        contact <= duration
          ? [{ time: contact, type: "collision", refs: [b1.id, b2.id] }]
          : [];
      return trajectory(
        duration,
        (t) => {
          const after = t >= contact - 1e-10,
            dt = after ? t - contact : 0,
            a = after ? w1 : v1,
            b = after ? w2 : v2;
          const q1 = after ? x1 + v1 * contact + w1 * dt : x1 + v1 * t,
            q2 = after ? x2 + v2 * contact + w2 * dt : x2 + v2 * t;
          return state(
            t,
            { [b1.id]: { x: q1, y: 0 }, [b2.id]: { x: q2, y: 0 } },
            { [b1.id]: { x: a, y: 0 }, [b2.id]: { x: b, y: 0 } },
            0.5 * m1 * a * a + 0.5 * m2 * b * b,
            0,
            { [b1.id]: m1, [b2.id]: m2 },
          );
        },
        event,
        {
          v1_after: w1,
          v2_after: w2,
          ...(Number.isFinite(contact) ? { contact_time: contact } : {}),
        },
        warnings,
      );
    });
  },
  forces(s, p) {
    return s.bodies.flatMap((b) => [
      {
        body: b.id,
        label: "weight",
        vector: { x: 0, y: mass(s, p, b.id) * read(s, p, "constants.g") },
      },
      {
        body: b.id,
        label: "normal",
        vector: { x: 0, y: -mass(s, p, b.id) * read(s, p, "constants.g") },
      },
    ]);
  },
  regime: (s) =>
    info(
      "impulse",
      "Instantaneous one-dimensional contact; momentum is conserved.",
      s,
    ),
};
