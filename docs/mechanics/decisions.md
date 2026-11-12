# M2 decisions and limits

## Assumptions, scale and physics

`defaults.py` declares mass 1 kg, g 9.81 m/s², friction 0, spring damping 0 kg/s,
restitution 1, launch speed 20 m/s, incline length 3 m, pendulum length 1 m and
spring natural length 0.5 m. Missing pendulum damping is 0 /s. These are
`assumed`/`prior` with confidence zero. Measured/authored or explicit null Values
are retained. Other needed inputs (release/launch angles, spring k, etc.) must be
supplied; a solver reports unresolved/unsupported rather than inventing them.

Absent scale uses drawn incline length / 3 m, drawn pivot-to-bob / 1 m, or
projectile width×0.75 / (20²/9.81) so the default ground arc fits. Other scenes
without a dimension use a declared 100 px/m prior. The ten fixtures explicitly
author their scale (14/100/150/160/240/250 px/m as appropriate) but mark it
assumed, because no real printed dimension was read. The UI badges scale-derived
distance/time as assumed. Dynamics use SI, with image/world +y down.

Solvers are deterministic TypeScript only. Constant acceleration, projectile,
collision and all three spring damping regimes use closed forms. Pendulum uses
RK4 at 1/240 s; period is estimated by interpolated zero crossings. A massive
pulley is a solid disc with I=Mr²/2. Coulomb friction is piecewise exact with
turn/stick transitions. Controls maintain 0≤mu_k≤mu_s; invalid direct solver
inputs are unsupported. Static friction supplies the required force within its
limit. The optional slope force is positive up the incline.

The source calibration is immutable. Layout computes displacements from its
anchors and source physical positions; overriding a mass cannot rescale or move
the background. Source masks and repair segments are explicitly authored.

Terminal contacts stop: projectile ground, incline footprint at either endpoint,
hanging body floor, body/pulley clearance, spring length 0.08 m, negative rope
tension. No invented floor continuation, bouncing, post-slack motion or compressed
spring collision law. The pendulum fixture is a rod; a slack string stops with a
warning. Inelastic contact can lose energy; elastic collisions conserve momentum
and kinetic energy. A collision after-panel is a consistency check, not input
used to force agreement. Forces/readouts describe the selected idealized model.

Default precomputation is 8 s (pendulum at least four periods, capped at 30 s),
collision up to two seconds after contact within a 10 s horizon; projectile runs
to ground contact. Closed-form event times are inserted between regular samples.
Right-hand event states prevent interpolation through a velocity impulse.
Direct inputs requiring more than 120 s of precomputation produce
`trajectory_budget_exceeded` and no invented shortened run. Nonvertical gravity,
unknown types, missing required objects or invalid physical inputs are explicitly
unsupported in M2. Real nonuniform photographic backgrounds remain unverified.

## Rendering and controls

The painter uses Pillow's bundled font, supplied paper/ink/stroke style and no
random state. `save_diagram`/the CLI writes the PNG plus canonical scene JSON
containing the exact authored mask polygons and static-line repair segments.
The builder deterministically reproduces all ten pairs and the schema. M4 adds
random seeds/styles/data generation; M2 does not create training data.

Layer 1 lifts native body masks (with a four-pixel antialias guard), external
attached labels, deforming links and pulley pixels; paper fills the holes and
authored static repairs restore lines below them. Layer 2 uses those source
sprites, fixed spring leads with a stretched original coil, routed tangent ropes,
matched rods, and original pulley pixels rotating by displacement/radius. Live
bound numeric labels replace the source labels only while changed. Geometry
edits redraw affected static lines/hatching/intersections and angle arcs.

Frame-0 checking composes layers 1+2 on a fresh native canvas, compares RGB with
the source and measures mean absolute channel difference and the fraction of
pixels with any channel difference >16/255. Config in `renderer.ts` is 2.0 and
0.005; thresholds were not relaxed. An additional source-anchor calibration
check requires at most 1 px error. Sparse ink can otherwise hide a badly shifted
bob inside the RGB average; the pivot-only fault test exercises this case.
This is a measured tolerance check, **not a
claim of zero changed pixels**. Failed checks emit `render_mismatch`, reduce
render confidence to 0.5 and show the untouched source with overlays. Actual
per-fixture measurements are in status.md. Back to original restores the same
canvas RGBA hash, including overlays, in the browser binding test.

Canvas padding covers the precomputed native trajectory; the source stays at
native size with scrolling, blank-paper pointer panning and optional user zoom.
Narrow views initially pan to the first body rather than shrinking the image. Only the lowest
ground line continues into padding. DPR is capped at 2. A backing side above
16,000 px or area above 32 million pixels uses the original/overlay fallback with
`trajectory_extent_limit`, rather than allocating an unbounded bitmap. This is
a disclosed rendering limit, not a changed physical solution.

The shared kit has a 1/240 s accumulator/interpolation clock, caps incoming frame
delta at 0.1 s, supports 0.25–4× speed, pause/reset/step and an exact terminal-time
scrubber. The dev page renders position, signed velocity and energy plots, live
kinetic/potential bars, labelled force/velocity arrows, dashed component vectors
and predicted paths. Checkbox/lock/button labels and 44 px hit targets provide
non-colour cues. Reduced motion defaults to a still predicted-path preview;
explicit play/step/scrub remain available. No fixture autoplays for anyone.

## Standalone development and milestone boundary

```powershell
# From frontend, after npm ci:
npm.cmd run dev -- --config mechanics-dev.config.mjs --configLoader native --port 5173
# Open http://127.0.0.1:5173/mechanics-dev.html
```

This is a separate Vite HTML entry/config. It serves root fixtures as local modules and
makes no API calls; a backend/model server is unnecessary. The normal production
build still builds the circuit shell only. Browser tests start and close their
own Vite instance on loopback port 5175. `?fixture=pendulum&checkFault=1` injects
wrong pivot metadata to exercise degradation, and `?unknownType=1` exercises
retained unsupported objects; both are explicit dev QA cases. The inspection
hook is read-only and tests operate the controls and handles.

The M1 main-app Mechanics placeholder remains intentionally in place until M3.
The dev lab is English; bilingual workspace strings/editor/authoring/export are
M3 work. No circuit file moved or implementation/test/snapshot changed. The only
shared existing edits are a shell export and local package metadata for the new
tool package. Model pins and existing ignored models are unchanged.

HUMAN: begin the frozen real diagram collection (printed/handwritten, source
separation and licence decisions). No gold scene is generated here. Real
mechanics accuracy, model latency, training/GPU duration, human Bangla review,
physical-device testing and Linux/macOS execution remain null/unverified.
