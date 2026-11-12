import type {
  ArchetypeModule,
  State,
  Scene,
  Params,
  Trajectory,
} from "../types";
import { guarded, gravity, mass, read, RAD, DT, state, info } from "./common";
import { layout } from "../layout";

export const pendulum: ArchetypeModule = {
  id: "pendulum",
  defaultBindings: (s) => structuredClone(s.bindings),
  layout,
  solve: (s, p) => integrate(s, p),
  forces(s, p, st) {
    const id = s.bodies[0].id,
      a = st.scalars.angle_deg * RAD,
      T = st.scalars.tension;
    return [
      {
        body: id,
        label: "weight",
        vector: { x: 0, y: mass(s, p) * gravity(s, p) },
      },
      {
        body: id,
        label: "tension",
        vector: { x: -T * Math.sin(a), y: -T * Math.cos(a) },
      },
      {
        body: id,
        label: "damping",
        vector: {
          x:
            -mass(s, p) *
            read(s, p, `links.${s.links[0].id}.length_m`) *
            read(s, p, `links.${s.links[0].id}.damping`) *
            st.scalars.omega_rad_s *
            Math.cos(a),
          y:
            mass(s, p) *
            read(s, p, `links.${s.links[0].id}.length_m`) *
            read(s, p, `links.${s.links[0].id}.damping`) *
            st.scalars.omega_rad_s *
            Math.sin(a),
        },
      },
    ];
  },
  regime: (s) =>
    info(
      "taut",
      "Taut rod/string; mass does not affect its angular motion.",
      s,
    ),
};

function integrate(s: Scene, p: Params, preview = false): Trajectory {
  return guarded(s, p, () => {
    const b = s.bodies[0],
      link = s.links.find((l) => l.type === "rod" || l.type === "rope")!,
      prefix = `links.${link.id}`;
    const L = read(s, p, `${prefix}.length_m`),
      c = read(s, p, `${prefix}.damping`),
      g = gravity(s, p),
      m = mass(s, p);
    if (!(L > 0) || c < 0) throw new Error("invalid_pendulum");
    let theta = read(s, p, "params.release_angle") * RAD,
      omega = read(s, p, "params.angular_speed", 0);
    const states: State[] = [],
      times: number[] = [],
      crossings: number[] = [],
      warnings: string[] = [];
    const events: { time: number; type: string; refs: string[] }[] = [];
    const acceleration = (a: number, w: number) =>
      (-g / L) * Math.sin(a) - c * w;
    const horizon = preview
      ? 0.25
      : Math.min(30, Math.max(8, 4 * 2 * Math.PI * Math.sqrt(L / g)));
    let previous = theta;
    for (let i = 0; i <= Math.ceil(horizon / DT); i++) {
      const t = i * DT,
        x = L * Math.sin(theta),
        y = L * Math.cos(theta);
      const T = m * (g * Math.cos(theta) + L * omega * omega);
      times.push(t);
      states.push(
        state(
          t,
          { [b.id]: { x, y } },
          {
            [b.id]: {
              x: L * Math.cos(theta) * omega,
              y: -L * Math.sin(theta) * omega,
            },
          },
          0.5 * m * L * L * omega * omega,
          m * g * L * (1 - Math.cos(theta)),
          { [b.id]: m },
          { angle_deg: theta / RAD, omega_rad_s: omega, tension: T },
        ),
      );
      if (link.type === "rope" && T < 0) {
        warnings.push("rope_slack");
        events.push({ time: t, type: "rope_slack", refs: [link.id] });
        break;
      }
      if (i > 0 && theta * previous < 0)
        crossings.push(
          t -
            DT +
            (DT * Math.abs(previous)) / (Math.abs(previous) + Math.abs(theta)),
        );
      previous = theta;
      const k1a = omega,
        k1w = acceleration(theta, omega);
      const k2a = omega + (DT * k1w) / 2,
        k2w = acceleration(theta + (DT * k1a) / 2, omega + (DT * k1w) / 2);
      const k3a = omega + (DT * k2w) / 2,
        k3w = acceleration(theta + (DT * k2a) / 2, omega + (DT * k2w) / 2);
      const k4a = omega + DT * k3w,
        k4w = acceleration(theta + DT * k3a, omega + DT * k3w);
      theta += (DT * (k1a + 2 * k2a + 2 * k3a + k4a)) / 6;
      omega += (DT * (k1w + 2 * k2w + 2 * k3w + k4w)) / 6;
    }
    const metrics: Record<string, number> = {
      small_angle_period: 2 * Math.PI * Math.sqrt(L / g),
    };
    if (crossings.length >= 2)
      metrics.measured_period = 2 * (crossings[1] - crossings[0]);
    return {
      dt: DT,
      times,
      states,
      events,
      duration: times.at(-1)!,
      metrics,
      warnings,
      supported: true,
    };
  });
}

export const pendulumPreview = (s: Scene, p: Params) => integrate(s, p, true);
