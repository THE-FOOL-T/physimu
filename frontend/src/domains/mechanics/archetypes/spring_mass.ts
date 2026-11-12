import type { ArchetypeModule } from "../types";
import {
  guarded,
  gravity,
  mass,
  read,
  state,
  trajectory,
  info,
  DT,
} from "./common";
import { layout } from "../layout";

/** Analytic solution, including critical and overdamped cases. */
export function oscillator(
  x0: number,
  v0: number,
  k: number,
  m: number,
  c: number,
) {
  const alpha = c / (2 * m),
    w2 = k / m,
    discriminant = alpha * alpha - w2;
  if (Math.abs(discriminant) < 1e-10) {
    const B = v0 + alpha * x0;
    return (t: number) => {
      const e = Math.exp(-alpha * t);
      return { x: (x0 + B * t) * e, v: (B - alpha * (x0 + B * t)) * e };
    };
  }
  if (discriminant < 0) {
    const w = Math.sqrt(-discriminant),
      B = (v0 + alpha * x0) / w;
    return (t: number) => {
      const e = Math.exp(-alpha * t),
        co = Math.cos(w * t),
        si = Math.sin(w * t),
        f = x0 * co + B * si;
      return { x: e * f, v: e * (-alpha * f - x0 * w * si + B * w * co) };
    };
  }
  const d = Math.sqrt(discriminant),
    r1 = -alpha + d,
    r2 = -alpha - d,
    A = (v0 - r2 * x0) / (r1 - r2),
    B = x0 - A;
  return (t: number) => ({
    x: A * Math.exp(r1 * t) + B * Math.exp(r2 * t),
    v: r1 * A * Math.exp(r1 * t) + r2 * B * Math.exp(r2 * t),
  });
}
export const springMass: ArchetypeModule = {
  id: "spring_mass",
  defaultBindings: (s) => structuredClone(s.bindings),
  layout,
  solve(s, p) {
    return guarded(s, p, () => {
      const id = s.bodies[0].id,
        l = s.links.find((l) => l.type === "spring")!,
        prefix = `links.${l.id}`;
      const m = mass(s, p),
        g = gravity(s, p),
        k = read(s, p, `${prefix}.k`),
        c = read(s, p, `${prefix}.damping`);
      const rest = read(s, p, `${prefix}.rest_length_m`),
        vertical = read(s, p, "params.vertical", 0) !== 0;
      if (!(k > 0) || c < 0 || !(rest > 0)) throw new Error("invalid_spring");
      const eq = vertical ? (m * g) / k : 0,
        run = oscillator(
          read(s, p, "params.initial_stretch") - eq,
          read(s, p, "params.initial_speed", 0),
          k,
          m,
          c,
        );
      const minLength = 0.08;
      let duration = 8;
      const events: { time: number; type: string; refs: string[] }[] = [],
        warnings: string[] = [];
      if (rest + run(0).x + eq < minLength)
        throw new Error("initial_spring_compression");
      for (let t = DT; t <= 8; t += DT)
        if (rest + run(t).x + eq < minLength) {
          let a = t - DT,
            b = t;
          for (let i = 0; i < 45; i++) {
            const mid = (a + b) / 2;
            if (rest + run(mid).x + eq < minLength) b = mid;
            else a = mid;
          }
          duration = (a + b) / 2;
          events.push({
            time: duration,
            type: "compression_limit",
            refs: [l.id],
          });
          warnings.push("compression_limit");
          break;
        }
      return trajectory(
        duration,
        (t) => {
          const f = run(t),
            x = f.x + eq,
            v = t >= duration - 1e-10 && events.length ? 0 : f.v;
          const pos = vertical ? { x: 0, y: x } : { x, y: 0 },
            vel = vertical ? { x: 0, y: v } : { x: v, y: 0 };
          return state(
            t,
            { [id]: pos },
            { [id]: vel },
            0.5 * m * v * v,
            0.5 * k * x * x - (vertical ? m * g * x : 0),
            { [id]: m },
            {
              stretch: x,
              speed: v,
              spring_force: -k * x - c * v,
              equilibrium: eq,
            },
          );
        },
        events,
        {
          angular_frequency: Math.sqrt(k / m),
          period: 2 * Math.PI * Math.sqrt(m / k),
          equilibrium: eq,
        },
        warnings,
      );
    });
  },
  forces(s, p, st) {
    const id = s.bodies[0].id,
      vertical = read(s, p, "params.vertical", 0) !== 0;
    return [
      {
        body: id,
        label: "weight",
        vector: { x: 0, y: mass(s, p) * gravity(s, p) },
      },
      {
        body: id,
        label:
          read(s, p, `links.${s.links[0].id}.damping`) > 0
            ? "spring + damping"
            : "spring",
        vector: vertical
          ? { x: 0, y: st.scalars.spring_force }
          : { x: st.scalars.spring_force, y: 0 },
      },
      ...(!vertical
        ? [
            {
              body: id,
              label: "normal",
              vector: { x: 0, y: -mass(s, p) * gravity(s, p) },
            },
          ]
        : []),
    ];
  },
  regime: (s) =>
    info("oscillation", "Damped spring; compression limit stops the run.", s),
};
