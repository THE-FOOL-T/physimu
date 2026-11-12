import type { ArchetypeModule } from "../types";
import {
  guarded,
  gravity,
  mass,
  read,
  RAD,
  state,
  trajectory,
  motion,
  info,
  scale,
} from "./common";
import { layout } from "../layout";

export const inclineBlock: ArchetypeModule = {
  id: "incline_block",
  defaultBindings: (s) => structuredClone(s.bindings),
  layout,
  solve(s, p) {
    return guarded(s, p, () => {
      const b = s.bodies[0],
        surface = s.surfaces.find((v) => v.type === "incline")!;
      const prefix = `surfaces.${surface.id}`,
        m = mass(s, p),
        g = gravity(s, p);
      const theta = read(s, p, `${prefix}.angle_deg`) * RAD;
      if (!(theta > 0 && theta < Math.PI / 2))
        throw new Error("invalid_incline_angle");
      const N = m * g * Math.cos(theta),
        F = read(s, p, "params.applied_force", 0);
      const q0 = read(s, p, "params.start_position"),
        v0 = read(s, p, "params.initial_speed", 0);
      const half =
        Math.hypot(b.mask[1][0] - b.mask[0][0], b.mask[1][1] - b.mask[0][1]) /
        (2 * scale(s, p));
      const run = motion(
        q0,
        v0,
        F - m * g * Math.sin(theta),
        read(s, p, `${prefix}.mu_k`) * N,
        read(s, p, `${prefix}.mu_s`) * N,
        m,
        half,
        read(s, p, `${prefix}.length_m`) - half,
        [b.id],
      );
      return trajectory(
        run.duration,
        (t) => {
          const { q, v, a } = run.at(t),
            u = { x: Math.cos(theta), y: -Math.sin(theta) };
          const pos = { x: q * u.x, y: q * u.y },
            vel = { x: v * u.x, y: v * u.y };
          return state(
            t,
            { [b.id]: pos },
            { [b.id]: vel },
            0.5 * m * v * v,
            -m * g * pos.y,
            { [b.id]: m },
            {
              q,
              v,
              a,
              normal: N,
              friction: F - m * g * Math.sin(theta) - m * a,
            },
          );
        },
        run.events,
        { acceleration: -run.initialAcceleration, normal: N },
      );
    });
  },
  forces(s, p, state) {
    const id = s.bodies[0].id,
      sf = s.surfaces.find((v) => v.type === "incline")!;
    const a = read(s, p, `surfaces.${sf.id}.angle_deg`) * RAD,
      N = state.scalars.normal,
      f = state.scalars.friction;
    return [
      {
        body: id,
        label: "weight",
        vector: { x: 0, y: mass(s, p) * gravity(s, p) },
      },
      {
        body: id,
        label: "normal",
        vector: { x: -N * Math.sin(a), y: -N * Math.cos(a) },
      },
      {
        body: id,
        label: "friction",
        vector: { x: -f * Math.cos(a), y: f * Math.sin(a) },
      },
      {
        body: id,
        label: "slope weight",
        component: true,
        vector: {
          x: -mass(s, p) * gravity(s, p) * Math.sin(a) * Math.cos(a),
          y: mass(s, p) * gravity(s, p) * Math.sin(a) ** 2,
        },
      },
      {
        body: id,
        label: "applied",
        vector: {
          x: read(s, p, "params.applied_force", 0) * Math.cos(a),
          y: -read(s, p, "params.applied_force", 0) * Math.sin(a),
        },
      },
    ];
  },
  regime(s, p) {
    const sf = s.surfaces.find((v) => v.type === "incline")!,
      a = read(s, p, `surfaces.${sf.id}.angle_deg`) * RAD;
    const m = mass(s, p),
      g = gravity(s, p),
      drive = read(s, p, "params.applied_force", 0) - m * g * Math.sin(a);
    const stick =
      Math.abs(drive) <=
        read(s, p, `surfaces.${sf.id}.mu_s`) * m * g * Math.cos(a) &&
      read(s, p, "params.initial_speed", 0) === 0;
    return info(
      stick ? "stick" : "slide",
      "Coulomb friction; stops at the drawn slope endpoint.",
      s,
    );
  },
};
