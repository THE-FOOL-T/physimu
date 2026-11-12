# M2 plan — fixture-driven mechanics foundation

The owner's "continue next" starts M2 only. The M1 follow-up established matching
circuit documents/solutions on three real images and inherited time-limited OCR
diagnostic variability. Keep that limitation and all historical results.

## Scope and files

1. `backend/domains/mechanics/{scene,defaults}.py`: strict finite Pydantic scene,
   SI physical Values, native-pixel geometry, global ids/references, binding path
   checks, unknown-type retention/warnings and explicit assumed defaults.
   Matching TS types/runtime validation under the mechanics domain. Generate
   `docs/mechanics/schema.json`; document conventions/defaults/decisions.
2. `backend/tools/mechanics/`: deterministic printed diagram painter and fixture
   builder. Exact synthetic masks, anchors and static-line repairs, no perception.
   Ten JSON/PNG pairs under `fixtures/mechanics/`: projectile ground/cliff,
   incline, pendulum, horizontal/vertical spring, Atwood, table pulley, incline
   pulley, collision. These are authored synthetic fixtures, never gold scenes.
3. `frontend/src/shared/sim/`: domain-independent fixed-step clock (1/240 s,
   accumulator/interpolation, 0.1 s cap), controls, scrubber, graphs, parameter
   rows and native/CSS coordinate transforms. Export through the shell facade.
4. `frontend/src/domains/mechanics/archetypes/`: eight pure deterministic modules
   with solve/layout/forces/regime/defaultBindings. Closed forms and RK4 only in
   TypeScript. Exact terminal/contact events, friction directions/static cases,
   massive Atwood pulley, after-panel check and energy/momentum readouts.
5. Mechanics renderer/helpers: native-image background and repairs, clipped body
   and label sprites, spring lead/coil/lead pixels, routed ropes/rods, rotating
   pulley pixels, labelled/dashed overlays, trajectory padding, reduced motion,
   measurable frame-0 check and explicit original-with-overlays degradation.
6. Mechanics binding engine: user Values, physics/initial/locked geometry rules,
   drawn-scene limits, recomputation/restart, initial-condition drag handles,
   Modified tag and Back to original. Dev page `frontend/mechanics-dev.html`
   served by Vite, fully independent of backend/API. M3 mounts the real workspace;
   M1's main-app placeholder stays unchanged during M2.

## Shared boundaries

No circuit main, pipeline, solver, renderer, UI implementations, imported tests,
fixtures or snapshots change. No moves. Expected infrastructure-only changes:
the shell facade exports the new sim kit; pyproject lists the new tools package
for both local namespaces. Tests run before the shared integration commit.
Use a separate Vite HTML entry for the dev page rather than changing the main
entry/router. Browser tests start/close a local Vite instance with the existing
Playwright runner. No production dependency changes are expected.

## Contract decisions/assumptions

- Physical inputs are Values; coordinates, measured stroke dimensions, UI control
  bounds and generated trajectory samples are numeric as the brief's structures
  require. World trajectory axes follow image +x/right, +y/down, in SI; heights
  above ground and textbook launch angles remain positive upward/degrees.
- Link endpoints explicitly store `{ref, point}`. Body label ids and text ids
  reference label annotations, whose geometry includes text and its native box;
  there is no unlisted global OCR collection in M2. All references resolve.
- Parameter overrides are addressed by document paths. Native source geometry
  calibrates layout; no CV measurement or mechanics perception is implemented.
- Inclines stop at their drawn endpoint (the brief allows stop or floor
  continuation). Spring compression-limit contact terminates with a warning.
  Rod pendulum is the authored fixture; unsupported/slack assumptions stop rather
  than invent a different physical regime.
- The standalone dev page is English; full bilingual workspace integration is
  scheduled for M3. Shared badges use the existing facade. No Bangla review claim.
- Frame-0 thresholds begin at mean absolute channel difference 2.0 and fraction
  over 16/255 <= 0.005; retain actual measurements. No original-image shortcut
  may replace the composed-layer check. Rendering failures preserve the source.

## Verification and reporting

- New Python/TS tests in their existing mechanics test folders: strict schema,
  ids/references/finite numbers/unknowns/defaults, deterministic painter and all
  ten fixtures; all textbook answers (1e-6 closed form, 1e-3 RK4), conservation,
  friction/regime transitions, floor/pulley/slack/contact/endpoint events,
  deterministic immutable solves, <=1 px initial layout, binding classes/limits,
  interpolation/accumulator and mapping tests.
- Browser: every fixture composes frame 0, plays/pauses/resets/steps/scrubs; test
  surface constraints, each binding class, geometry locks/reset, drag handles,
  background invariance, reduced motion, degradation and padding. Collect actual
  composition and frame/render times under ignored `.cache/m2-*`.
- Run `python manage.py test` before shared-file commits and at completion;
  `check`, all original browser tests, new browser tests, visual inspection.
  Preserve original test assertions and strict layout assets. Retain/report the
  existing keyboard chooser flake if it recurs, rather than weakening tests.
- Append real results, shared diff sizes, limitations, commands and HUMAN tasks
  to status.md. Real-data accuracy stays null. HUMAN: begin collecting the frozen
  printed/handwritten pool; no gold scenes are written by Codex.

Small commits, with shared edits separate. Stop before M3 and wait for continue.
