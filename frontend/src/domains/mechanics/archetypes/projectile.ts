import type { ArchetypeModule } from "../types";
import {
  guarded,
  gravity,
  mass,
  read,
  RAD,
  state,
  trajectory,
  info,
} from "./common";
import { layout } from "../layout";

export const projectile: ArchetypeModule = {
  id: "projectile",
  defaultBindings: (s) => structuredClone(s.bindings),
  layout,
  solve(s, p) {
    return guarded(s, p, () => {
      const id = s.bodies[0].id,
        m = mass(s, p),
        g = gravity(s, p);
      const v = read(s, p, "params.launch_speed"),
        a = read(s, p, "params.launch_angle") * RAD;
      const h = read(s, p, "params.launch_height");
      if (v < 0 || h < 0 || a < 0 || a > Math.PI / 2)
        throw new Error("invalid_launch");
      const vx = v * Math.cos(a),
        vy = v * Math.sin(a);
      const T = (vy + Math.sqrt(vy * vy + 2 * g * h)) / g;
      return trajectory(
        T,
        (t) => {
          const end = t >= T - 1e-10;
          const pos = { x: vx * t, y: end ? 0 : -h - vy * t + 0.5 * g * t * t };
          const vel = { x: end ? 0 : vx, y: end ? 0 : -vy + g * t };
          return state(
            t,
            { [id]: pos },
            { [id]: vel },
            0.5 * m * (vel.x ** 2 + vel.y ** 2),
            -m * g * pos.y,
            { [id]: m },
          );
        },
        [{ time: T, type: "ground_contact", refs: [id] }],
        { flight_time: T, range: vx * T, peak_height: h + (vy * vy) / (2 * g) },
      );
    });
  },
  forces: (s, p) => [
    {
      body: s.bodies[0].id,
      label: "weight",
      vector: { x: 0, y: mass(s, p) * gravity(s, p) },
    },
  ],
  regime: (s) => info("flight", "Ballistic flight ends at ground contact.", s),
};
