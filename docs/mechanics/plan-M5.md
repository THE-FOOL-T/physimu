# M5 plan — perception, jobs and editable results (2026-11-13)

Continue authorizes M5 only. Start from clean M4 `9c9123b`. Circuit pipeline,
solver, imported original tests and visual baselines remain unchanged. The
mechanics production checkpoint is absent; M4 smoke is not promoted. No reviewed
real gold/labels were supplied. Public candidate images remain unreviewed and
outside training/gold. No model/data download, full training or M6 round work.

## Backend and model ownership

- Write mechanics detect.py, geometry.py, labels.py, associate.py, sprites.py,
  archetypes.py, validate.py and engine.py; extend existing defaults only for
  explicit assumed priors. Keep the v1 schema and TypeScript solvers unchanged.
- Add a core model-lease helper and facade exports for existing OCR digit/window/
  crop helpers, thread setup and model release. Mechanics imports shared code
  only through core. No circuit implementation moves or algorithm edits.
- Serialize app-domain model use, wait cooperatively for any circuit startup
  warmup, and evict the other detector before loading a domain model. Startup
  also enters this lease. Preserve circuit warmup/fallback/warning behavior;
  switching back can incur a detector reload. Direct mechanics engine calls use
  the same lease. The scope is the supported application/service path, not
  arbitrary callers bypassing the facade and invoking circuit internals.
- Lazy local mechanics .pt cache keyed by domain/path/file identity, with a
  thread lock, MECHANICS_MODEL, exact class map and typed missing/incompatible
  weights. No automatic model fetch. Never initialize from circuit weights.
- M1's two-stage not_implemented placeholder is deliberately replaced by the
  nine M5 stages. Update only those milestone-owned tests; retain their circuit,
  domain validation, cancellation and fallback-isolation assertions. Mechanics
  can now wait for startup model ownership, but never calls circuit analysis.

## Native image evidence and scene construction

- Reuse preprocessing/style/figure splitting/OCR through the facade. The returned
  source_image is the actual analyzed native raster, including any perspective
  correction, so its scene and preview cannot use stale upload coordinates.
- Detection boxes locate objects only. Fit lines/circles, trace masked rope/rod
  skeletons, estimate pendulum angle/length and spring endpoints/coils, fit
  trajectory arcs/tangents, measure dimension scale and stroke/ink from pixels.
  Return evidence/confidence/failure reasons; unknown/failed objects stay editable.
- Extract body polygons from padded crops with static lines excluded; close/fill
  closed shapes and emit line repairs. Retain original source pixels for sprites.
- Mechanics-specific grammar normalizes Bengali/subscript digits without the
  circuit resistor grammar. Parse SI mass, angle, friction, speed, length, spring
  constant, force and gravity; bare m/M are names, units require adjacent numbers,
  ambiguous bare values stay unplaced. Bengali unit spellings need HUMAN review.
- Typed Hungarian assignment uses owner compatibility, names, distance and OCR
  evidence. Preserve user values. Infer no numeric label from the supplied problem
  text without spatial evidence. Unplaced values become editable chips.
- Match supported archetypes from measured objects/attachments. Search alternate
  surfaces and link endpoints, score violations and retain diagnostic alternatives.
  Validate masses/g/angles/friction, rope reach/tangency and required structures;
  warn when priors choose a regime. Missing values are explicitly assumed. Backend
  checks regimes only; it never duplicates the TypeScript solver.
- Handle figure gutters conservatively, left collision panel as initial state
  and the right as an optional check. Retain image/boxes and explain ambiguity.
- Provenance extracted only when required evidence/values are measured/read;
  partial for supported scenes with priors/disabled parts; unsupported otherwise,
  with a plain reason and editable retained objects. No example or demo fallback.
- Retain a recognized archetype when measured inputs fail validation, so its
  objects and unit conventions stay editable. The mechanics BindingEngine must
  withhold simulation while provenance is unsupported; an authored repair can
  then use the unchanged numerical solver. This is a result-integration guard.
- Keep the guard for unmodelled nonzero/unresolved force arrows after unrelated
  authoring edits too. Changing a mass must not enable a solver that ignores a
  retained force. Remove that arrow or author a supported arrangement explicitly.
- The fixed detector schema includes ground_hatch while the v1 annotation type
  is an open string and its known-type warning list omits this static decoration.
  Recognize ground_hatch as a static annotation in both validators (no schema
  shape/version change); retain genuinely unknown-type warnings and tests.

## Jobs, UI and corrections

- Existing domain routes carry mechanics stages, partial boxes/text and validated
  envelopes; no new analysis route is necessary. Progress callbacks cooperate
  with cancellation before/after model/OCR and between geometry objects.
- Add a mechanics-specific upload/poll controller using the existing shared
  upload patterns. Show real stages/progress and native partial detections, accept
  validated result scenes into the retained M3 workspace, open editing on partial
  or unsupported results, preserve blank authoring when weights are absent.
- Cancel/invalidate pending jobs on unmount, replacement, fixture/import or edits;
  stale responses must never overwrite a user's document/history. Keep one existing
  animation loop and the circuit upload controller unchanged.
- Reuse /api/corrections with an explicit mechanics branch and strict scene/image
  validation. Mechanics consent is off by default, requires a checked box and save
  action, stores unreviewed corrections only when requested. Preserve existing
  circuit correction payloads, validation and file layout. No auto-training/gold.
- All new text has matching mech.* EN/BN keys and human-review notice. Default
  circuit layout/snapshots should not change. No scene/upload browser persistence.

## Gates and reporting

- Geometry/grammar/assignment/model ownership/cancel/API tests under
  backend/tests/mechanics. Known painted geometry supplies exact synthetic truth;
  measure/report native pixel and degree errors, including failures.
- End-to-end synthetic tests inject boxes and raw OCR only, never a completed
  scene/archetype/attachment answer. Exercise each archetype, missing/unrecognized
  objects, assumptions, repairs and alternative scoring. Report measured archetype,
  attachment and parameter correctness explicitly as synthetic, not real accuracy.
- Add eval_end_to_end.py with separate printed/handwritten frozen metrics, all null
  when absent. Reuse the existing TypeScript solver through a local Node/tsx
  evaluator for trajectory comparisons; do not write a Python mechanics solver.
- Add a pure shell simulation re-export for the existing sampling helper. The
  broad browser shell facade imports CSS and cannot be loaded by the Node metric
  process; this narrow facade keeps the same implementation without DOM/CSS work.
- Browser tests start an isolated loopback backend with an explicitly test-owned
  box/OCR stub (no production stub flag/HTTP hook). Upload painted images, observe
  stages/partials, play/pause/edit a partial result, cancel/switch/stale-poll and
  consent behavior; real asset cases skip when absent. Unit/TS checks stay in the
  existing runners. Measure CPU stage timings, not target/recognition claims.
- Run manage.py test before shared commits and at completion, check, full browser
  and unchanged strict circuit snapshots. Disclose the inherited chooser flake
  if it recurs; no relaxed assertions/retries/timeouts/baselines.
- Shared facade/model lease, app integration, translations and any current README
  notice get separate commits after a passing full test. Update decisions, guides
  and status with exact commands/results, null real metrics, shared diff audit and
  HUMAN tasks. No dependency pin changes. Stop before M6; final reply has exactly
  changed / gate evidence / open questions.
