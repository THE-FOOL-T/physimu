import type { ArchetypeModule, Scene, Params } from "../types";
import {
  guarded,
  gravity,
  mass,
  read,
  RAD,
  scale,
  initial,
  state,
  trajectory,
  motion,
  info,
} from "./common";
import { layout } from "../layout";

function setup(s: Scene, p: Params) {
  const [b1, b2] = s.bodies,
    pulley = s.pulleys[0],
    g = gravity(s, p),
    S = scale(s, p);
  if (
    s.bodies.length !== 2 ||
    !pulley ||
    !s.links.some((l) => l.type === "rope")
  )
    throw new Error("missing_pulley_objects");
  const m1 = mass(s, p, b1.id),
    m2 = mass(s, p, b2.id);
  const M = pulley.mass ? read(s, p, `pulleys.${pulley.id}.mass`) : 0;
  if (M < 0) throw new Error("negative_pulley_mass");
  const sf =
    s.surfaces.find((v) => v.type === "incline") ??
    s.surfaces.find((v) => v.id === b1.on_surface);
  const theta =
    s.archetype === "incline_pulley"
      ? read(s, p, `surfaces.${sf!.id}.angle_deg`) * RAD
      : 0;
  if (theta < 0 || theta >= Math.PI / 2)
    throw new Error("invalid_incline_angle");
  const isAtwood = s.archetype === "atwood",
    N = isAtwood ? 0 : m1 * g * Math.cos(theta);
  const mus = isAtwood ? 0 : read(s, p, `surfaces.${sf!.id}.mu_s`),
    muk = isAtwood ? 0 : read(s, p, `surfaces.${sf!.id}.mu_k`);
  const drive = m2 * g - m1 * g * (isAtwood ? 1 : Math.sin(theta));
  const floorFor = (x: number, y: number) =>
    Math.min(
      ...s.surfaces
        .filter(
          (sf) =>
            sf.type === "floor" &&
            sf.polyline.some((point) => Math.abs(point[1] - y) > 1) &&
            x >= Math.min(...sf.polyline.map((a) => a[0])) &&
            x <= Math.max(...sf.polyline.map((a) => a[0])),
        )
        .map((sf) => sf.polyline[0][1])
        .filter((f) => f > y),
      s.image.height - 10,
    );
  const floor2 = floorFor(b2.anchor[0], b2.anchor[1]);
  let low: number, high: number;
  if (isAtwood) {
    const floor1 = floorFor(b1.anchor[0], b1.anchor[1]);
    low = Math.max(
      -(floor1 - b1.bbox[3]) / S,
      -(b2.bbox[1] - pulley.center[1] - pulley.radius_px) / S,
    );
    high = Math.min(
      (floor2 - b2.bbox[3]) / S,
      (b1.bbox[1] - pulley.center[1] - pulley.radius_px) / S,
    );
  } else {
    const u = { x: Math.cos(theta), y: -Math.sin(theta) };
    high = Math.min(
      (floor2 - b2.bbox[3]) / S,
      ((pulley.center[0] - b1.anchor[0]) * u.x +
        (pulley.center[1] - b1.anchor[1]) * u.y -
        pulley.radius_px -
        (b1.bbox[2] - b1.bbox[0]) / 2) /
        S,
    );
    if (s.archetype === "incline_pulley") {
      const a = sf!.polyline[0],
        sourceAngle = sf!.angle_deg!.number! * RAD;
      low =
        (Math.hypot(
          b1.mask[1][0] - b1.mask[0][0],
          b1.mask[1][1] - b1.mask[0][1],
        ) /
          2 -
          ((b1.anchor[0] - a[0]) * Math.cos(sourceAngle) -
            (b1.anchor[1] - a[1]) * Math.sin(sourceAngle))) /
        S;
    } else low = -(b1.bbox[0] - Math.min(...sf!.polyline.map((a) => a[0]))) / S;
    low = Math.max(
      low,
      -(b2.bbox[1] - pulley.center[1] - pulley.radius_px) / S,
    );
  }
  return {
    b1,
    b2,
    pulley,
    g,
    S,
    m1,
    m2,
    M,
    theta,
    isAtwood,
    N,
    mus,
    muk,
    drive,
    low,
    high,
  };
}
/** The interaction controller and solver share exactly the same travel limits. */
export function pulleyBounds(s: Scene, p: Params) {
  const { low, high } = setup(s, p);
  return { low, high };
}
export function pulleyModule(
  id: "atwood" | "table_pulley" | "incline_pulley",
): ArchetypeModule {
  return {
    id,
    defaultBindings: (s) => structuredClone(s.bindings),
    layout,
    solve(s, p) {
      return guarded(s, p, () => {
        const f = setup(s, p),
          {
            b1,
            b2,
            m1,
            m2,
            M,
            g,
            theta,
            N,
            mus,
            muk,
            drive,
            low,
            high,
            isAtwood,
          } = f;
        const run = motion(
          read(s, p, "params.initial_displacement", 0),
          read(s, p, "params.initial_speed", 0),
          drive,
          muk * N,
          mus * N,
          m1 + m2 + M / 2,
          low,
          high,
          [b1.id, b2.id],
          8,
          "floor_or_pulley_contact",
          "floor_or_pulley_contact",
        );
        const tension = (a: number) => ({
          T1:
            m1 * (g * (isAtwood ? 1 : Math.sin(theta)) + a) +
            (isAtwood ? 0 : drive - (m1 + m2 + M / 2) * a),
          T2: m2 * (g - a),
        });
        const initialT = tension(run.initialAcceleration);
        if (initialT.T1 < -1e-9 || initialT.T2 < -1e-9)
          return trajectory(
            0,
            (t) => {
              const q = initial(s, b1.id, "position"),
                r = initial(s, b2.id, "position");
              return state(
                t,
                { [b1.id]: q, [b2.id]: r },
                { [b1.id]: { x: 0, y: 0 }, [b2.id]: { x: 0, y: 0 } },
                0,
                0,
                { [b1.id]: m1, [b2.id]: m2 },
              );
            },
            [{ time: 0, type: "rope_slack", refs: [s.links[0].id] }],
            {},
            ["rope_slack"],
          );
        const start1 = initial(s, b1.id, "position"),
          start2 = initial(s, b2.id, "position");
        const u = isAtwood
          ? { x: 0, y: -1 }
          : { x: Math.cos(theta), y: -Math.sin(theta) };
        return trajectory(
          run.duration,
          (t) => {
            const { q, v, a } = run.at(t),
              T = tension(a);
            const pos1 = { x: start1.x + q * u.x, y: start1.y + q * u.y },
              pos2 = { x: start2.x, y: start2.y + q };
            return state(
              t,
              { [b1.id]: pos1, [b2.id]: pos2 },
              { [b1.id]: { x: v * u.x, y: v * u.y }, [b2.id]: { x: 0, y: v } },
              0.5 * (m1 + m2 + M / 2) * v * v,
              -g * (m1 * pos1.y + m2 * pos2.y),
              { [b1.id]: m1, [b2.id]: m2 },
              {
                q,
                v,
                a,
                T1: T.T1,
                T2: T.T2,
                normal: N,
                friction: drive - (m1 + m2 + M / 2) * a,
              },
            );
          },
          run.events,
          {
            acceleration: run.initialAcceleration,
            tension: initialT.T1,
            tension_1: initialT.T1,
            tension_2: initialT.T2,
          },
        );
      });
    },
    forces(s, p, st) {
      const f = setup(s, p),
        { b1, b2, m1, m2, g, theta, isAtwood } = f;
      const T1 = st.scalars.T1 ?? 0,
        T2 = st.scalars.T2 ?? 0,
        N = st.scalars.normal ?? 0,
        friction = st.scalars.friction ?? 0;
      const u = isAtwood
        ? { x: 0, y: -1 }
        : { x: Math.cos(theta), y: -Math.sin(theta) };
      return [
        { body: b1.id, label: "weight", vector: { x: 0, y: m1 * g } },
        { body: b2.id, label: "weight", vector: { x: 0, y: m2 * g } },
        { body: b1.id, label: "tension", vector: { x: T1 * u.x, y: T1 * u.y } },
        { body: b2.id, label: "tension", vector: { x: 0, y: -T2 } },
        ...(!isAtwood
          ? [
              {
                body: b1.id,
                label: "normal",
                vector: { x: -N * Math.sin(theta), y: -N * Math.cos(theta) },
              },
              {
                body: b1.id,
                label: "friction",
                vector: { x: -friction * u.x, y: -friction * u.y },
              },
            ]
          : []),
      ];
    },
    regime(s, p) {
      const f = setup(s, p),
        stick = Math.abs(f.drive) <= f.mus * f.N;
      return info(
        stick ? "stick" : f.drive > 0 ? "mass_2_down" : "mass_1_down",
        stick
          ? "Static friction holds the system."
          : "Taut rope; stops at floor or pulley contact.",
        s,
      );
    },
  };
}
