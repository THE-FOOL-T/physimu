import type { Scene, Params, State, Point, Drawables } from "./types";
import { read, scale, initial, RAD } from "./archetypes/common";

function rotate(p: Point, angle: number): Point {
  return [
    p[0] * Math.cos(angle) - p[1] * Math.sin(angle),
    p[0] * Math.sin(angle) + p[1] * Math.cos(angle),
  ];
}
const plus = (a: Point, b: Point): Point => [a[0] + b[0], a[1] + b[1]];
const minus = (a: Point, b: Point): Point => [a[0] - b[0], a[1] - b[1]];

/** Native-pixel calibration always uses source geometry; overrides never move the source anchors. */
export function layout(s: Scene, p: Params, st: State): Drawables {
  const S = scale(s),
    sf = s.surfaces.find((v) => v.type === "incline");
  const originalAngle = sf?.angle_deg?.number ?? 0;
  const angle = sf ? read(s, p, `surfaces.${sf.id}.angle_deg`) : 0;
  const delta = -(angle - originalAngle) * RAD;
  const bodies = s.bodies.map((b) => {
    const v = st.positions[b.id] ?? initial(s, b.id, "position"),
      start = initial(s, b.id, "position");
    let anchor: Point = [
        b.anchor[0] + (v.x - start.x) * S,
        b.anchor[1] + (v.y - start.y) * S,
      ],
      rotation = 0;
    if (s.archetype === "pendulum") {
      const pivot = s.links[0].a.point;
      anchor = [pivot[0] + v.x * S, pivot[1] + v.y * S];
    }
    if (s.archetype === "spring_mass") {
      const l = s.links[0],
        vertical = read(s, p, "params.vertical", 0) !== 0;
      const extension = st.scalars.stretch ?? 0,
        rest = read(s, p, `links.${l.id}.rest_length_m`);
      const half = vertical
        ? (b.bbox[3] - b.bbox[1]) / 2
        : (b.bbox[2] - b.bbox[0]) / 2;
      anchor = vertical
        ? [l.a.point[0], l.a.point[1] + (rest + extension) * S + half]
        : [l.a.point[0] + (rest + extension) * S + half, l.a.point[1]];
    }
    if (sf && b.on_surface === sf.id) {
      const foot = sf.polyline[0],
        u: Point = [Math.cos(angle * RAD), -Math.sin(angle * RAD)];
      if (s.archetype === "incline_block") {
        const sourceQ = read(s, {}, "params.start_position"),
          q = st.scalars.q;
        const originalU: Point = [
          Math.cos(originalAngle * RAD),
          -Math.sin(originalAngle * RAD),
        ];
        const offset: Point = [
          b.anchor[0] - foot[0] - sourceQ * S * originalU[0],
          b.anchor[1] - foot[1] - sourceQ * S * originalU[1],
        ];
        anchor = plus(
          plus(foot, [q * S * u[0], q * S * u[1]]),
          rotate(offset, delta),
        );
      } else {
        anchor = plus(foot, rotate(minus(b.anchor, foot), delta));
        anchor = plus(anchor, [
          (st.scalars.q ?? 0) * S * u[0],
          (st.scalars.q ?? 0) * S * u[1],
        ]);
      }
      rotation = delta;
    }
    return { id: b.id, anchor, rotation };
  });
  const surfaces = s.surfaces.map((surface) => {
    let points = surface.polyline.map((p) => [...p] as Point);
    if (surface === sf) {
      const length = read(s, p, `surfaces.${sf.id}.length_m`),
        base = sf.polyline[0];
      points = [
        base,
        [
          base[0] + length * S * Math.cos(angle * RAD),
          base[1] - length * S * Math.sin(angle * RAD),
        ],
      ];
    }
    if (
      s.archetype === "projectile" &&
      surface.id !== "S1" &&
      s.surfaces.some((v) => v.type === "wall")
    ) {
      const h = read(s, p, "params.launch_height"),
        sourceH = read(s, {}, "params.launch_height");
      points = surface.polyline.map((v) => [
        v[0],
        v[1] < s.surfaces[0].polyline[0][1] ? v[1] - (h - sourceH) * S : v[1],
      ]);
    }
    return { id: surface.id, points };
  });
  const pulleys = s.pulleys.map((pulley) => {
    let center = pulley.center;
    if (sf && s.archetype === "incline_pulley") {
      const sourceTip = sf.polyline.at(-1)!,
        tip = surfaces.find((v) => v.id === sf.id)!.points.at(-1)!;
      center = plus(tip, rotate(minus(pulley.center, sourceTip), delta));
    }
    return {
      id: pulley.id,
      center,
      radius: pulley.radius_px,
      rotation: ((st.scalars.q ?? 0) * S) / pulley.radius_px,
    };
  });
  const bodyPoint = (ref: string, point: Point) => {
    const source = s.bodies.find((b) => b.id === ref),
      target = bodies.find((b) => b.id === ref);
    return source && target
      ? plus(
          target.anchor,
          rotate(minus(point, source.anchor), target.rotation),
        )
      : point;
  };
  const links = s.links.map((link) => {
    let points = link.polyline.map((p) => [...p] as Point);
    points[0] = bodyPoint(link.a.ref, link.a.point);
    points[points.length - 1] = bodyPoint(link.b.ref, link.b.point);
    if (link.type === "spring")
      points = [link.a.point, bodyPoint(link.b.ref, link.b.point)];
    if (sf && s.archetype === "incline_pulley" && pulleys.length) {
      const pulley = pulleys[0],
        startAngle = Math.atan2(-Math.cos(angle * RAD), -Math.sin(angle * RAD));
      const arc: Point[] = Array.from({ length: 41 }, (_, i) => {
        const a = startAngle + ((0 - startAngle) * i) / 40;
        return [
          pulley.center[0] + pulley.radius * Math.cos(a),
          pulley.center[1] + pulley.radius * Math.sin(a),
        ];
      });
      points = [points[0], ...arc, points.at(-1)!];
    }
    return { id: link.id, points };
  });
  const handles: Drawables["handles"] = [];
  for (const b of s.bindings)
    if (b.handle && !handles.some((v) => v.id === b.handle)) {
      let point = bodies[0]?.anchor ?? ([0, 0] as Point);
      if (b.handle === "incline_tip")
        point = surfaces.find((v) => v.id === sf?.id)!.points.at(-1)!;
      if (b.handle === "spring_end") point = links[0].points.at(-1)!;
      if (b.handle === "launch") {
        const speed = read(s, p, "params.launch_speed"),
          a = read(s, p, "params.launch_angle") * RAD;
        point = [
          bodies[0].anchor[0] + speed * 2.5 * Math.cos(a),
          bodies[0].anchor[1] - speed * 2.5 * Math.sin(a),
        ];
      }
      handles.push({ id: b.handle, point });
    }
  return { bodies, links, pulleys, surfaces, handles };
}
