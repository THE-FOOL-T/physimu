# Real mechanics recognition and progressive workspace — 2026-11-14

The user's exact failed pendulum raster now produces an interactive simulation
through real local image analysis with the default mechanics checkpoint absent.
This is a verified regression case, not a real-world recognition accuracy score.
General recognition across all eight families remains dependent on compatible,
validated model evidence; the limited classical fallback supports a single pendulum.
Implementation commit: `e2d2307`, on `main`, starting from clean `0ff6c8c`.

## Failure and repair

The retained failed job returned directly from Detect after `WeightsUnavailable`.
OCR, geometry, association, archetype identification and validation did not execute;
their timings were null and no body existed. `manual_body_1` could only have been
created later by authoring. Upload also failed to clear the previous fixture choice.

Missing weights now remain an explicit detector warning while OCR and geometry
continue. A limited classical recognizer measures support/pivot intersections,
radial ink continuity, circle outlines and interior fill. It distinguishes one
physical bob from dashed alternate depictions, requires sufficient unique evidence
and retains ambiguous hypotheses for explicit user confirmation. It does not use
filenames, image hashes, caption matching or expected physical values.

The geometry tracer preserves short observed segments near a measured pivot;
endpoint reach checks remain in force. Parameter ownership uses the reconstructed
pendulum topology, including alternate radial routes. OCR preserves raw readings,
engine provenance and rotated alternatives. Strong orientation classification can
exclude a contradictory rotated alternative from binding; actual competing upright
physical readings still require review. Figure captions do not become quantities.

The scene schema remains v1, project format v2. Native image pixels, immutable
recognition, editable interpretation/overrides and trajectory remain separate.
No solver family or physics equations were added. The observed release angle is
authoritative even when the diagram depicts the equilibrium pose; an angle mismatch
warning stays visible. Missing mass/length remain null, with direct Fix interpretation
controls and no default silently substituted as an observation.

## Actual source and local execution

Input: `backend/tests/mechanics/assets/user-pendulum.png`, 1024 × 765, recovered
from retained job `7637486f50b445169434568016ad867d`. It is the supplied failure
image, not the unrelated public pendulum or a fixture. See its asset README for
regression provenance and redistribution limitations.
Raster SHA-256: `d5d34495e081c363fc9ab5d258c17bf43a081493bfa3c3e45dfbd690ba0bfdaa`.

Actual OCR observations from the first guarded runtime probe:

| Reading | Confidence | Native bounding box |
| --- | ---: | --- |
| `15°` | 0.99646 | 515, 228, 591, 284 |
| `L = 1.2 m` | 0.94335 | 628, 245, 803, 292 |
| `m = 0.5 kg` | 0.98034 | 403, 598, 599, 657 |
| `Fig. 1 Simple Pendulum` | 0.99647 | retained in raw evidence |

These engine scores are not calibrated accuracy. Actual configured hybrid execution
can report partial/time-budget warnings, particularly on cold start; these warnings
remain in the result and UI. A duplicate OCR-pool probe encountered worker memory
pressure and is retained as a partial run, not reported as complete OCR. No external
label reader, training, download or checkpoint promotion was used.

Classical measurements on the supplied raster include pivot about (511.5, 69), bob
center about (511.5, 568.2), radius about 28.8 px, continuous support and an observed
radial rope trace. Four proposals have explicit `classical_vision` provenance;
confidence is capped at 0.92. Two alternate positions remain attached evidence.
The compiler binds mass 0.5 kg to the bob, length 1.2 m to the rope and angle 15°
to `params.release_angle`, with raw label annotations linked to those same paths.

The mounted solver starts at (0.3105828541, 1.1591109915) m relative to the pivot,
whose radius is 1.2 m, with zero assumed initial angular speed. Its small-angle
period is 2.1975359458 s and the measured nonlinear period is 2.2069866340 s.
Playback changes position while preserving the arc to interpolation tolerance;
dragging changes the release-angle override and trajectory. Raising mass changes
tension through the existing solver. These checks are assertions on actual solver
states, not animation displacement. `visual/pendulum-physics.json` records states,
metrics, overrides and replay; `visual/pendulum-scene.json` is the compiled scene.

Default `models/mechanics.pt` remains absent. The existing experimental
`mechanics-synthetic-20261113.pt` has the required 21 classes and can run real
inference, but synthetic training alone does not establish general recognition.
`python -m backend.tools.mechanics.check_model` reports the exact configured path,
presence, compatibility and class contract, and loads an available file to verify
its names and compute its hash. The default missing file returns exit 2; the
explicit experimental file returns exit 0. Compatibility is not recognition accuracy.

## Progressive workspace

`shell/analysis-ui.ts` extracts genuinely shared preview markup and stepper behavior.
Circuit keeps its existing DOM order, classes, stage-index semantics and actions.
Mechanics reuses the existing three-column layout, cards, design tokens, playback,
parameter controls and graph infrastructure. Its upload column provides drag/drop,
receipt, dimensions, thumbnail, diagram style, actual stage states, elapsed progress,
cancel/retry and retained OCR/geometry evidence. The central canvas becomes the
actual augmented simulation; the inspector uses component names and linked labels.

Receive, Prepare, Understand, Detect Components, Read Parameters, Reconstruct
Geometry, Associate Objects and Parameters, Identify Physics System and Validate
come from real backend events and an explicit execution ledger. Build Simulation
and Ready are client stages set only after actual solver/renderer preparation.
Skipped, partial, blocked and failed work is represented separately. Original backend
failures remain recorded when a user correction subsequently enables simulation.
New uploads clear prior sample state immediately and retain source identity. A sample
or imported project is labeled separately. Explore, Fix interpretation and Advanced
authoring retain distinct roles; raw geometry/mask tools stay in Advanced authoring.

## Verification record

`manage.py check` passed 657 Python tests (one optional Circuit real-OCR benchmark
skipped), 131 TypeScript tests, lint, formatting and production build. The conditional
checkpoint case was enabled with `MECHANICS_TEST_MODEL` pointing to the existing
experimental file; the application default was not changed. A subsequent small
binding correction clears resolved missing-parameter messages from the editable
document; the final 131-test TS run and production rebuild also passed. Evidence:
`full-check.log`, `frontend-final-tests.log`, `frontend-final-build.log`.
The conditional checkpoint test requires actual inference and correct compiler
output; it permits recorded classical recovery when model topology is rejected.
It is not evidence that the experimental detector alone recognized the right topology.

The initial broad check failed three contracts: the domain's public stage tuple
omitted the newly executed Understand stage, and the earlier Circuit keyboard-test
commit had not been recorded in the independence manifest. A single lightweight
stage definition now owns both the job contract and pipeline. M7 pins the exact
shared-preview/stepper extraction and request option, retaining earlier fingerprints.
The existing `4109f4a` file-chooser change is now pinned with the original import hash
preserved; no keyboard action/assertion or Circuit snapshot was removed or reset.
The focused routing/independence run passed 31 tests. Its shutdown log contains an
OCR restart-thread logging error after passing tests; that diagnostic is retained.

The seven focused HTTP/browser tests pass, including retained corrections, consent,
cancellation and English/Bengali accessibility. Earlier failures recorded the intended
automatic transition to Explore and a low-contrast drop-zone subtitle; tests now
enter Fix explicitly for corrections, and the subtitle inherits the button foreground.
Missing-model checks await the actual completed analysis rather than its POST receipt.
No accessibility assertion was removed.

**Final complete browser gate: 139 passed, 2 skipped, zero failures, 8.4 minutes.**
`full-browser.log` records exit 0. All three unmocked image-pipeline scenarios passed
in this same run, together with the ten physical interaction and ten fixture-playback
cases. Circuit's twelve unchanged desktop/tablet/phone, English/Bengali, light/dark
layout snapshots and keyboard chooser/playback/editing test passed. The two skips
are existing optional Circuit owner-analysis captures absent from the private cache.
No Circuit screenshot baseline was reset. Generated Circuit timing JSON was copied
to this evidence directory and restored to its tracked baseline.

Additional unmocked browser checks have verified both recovery paths: an occluded
copy with unread mass/length keeps a detected pendulum and needs two parameter
entries before automatically entering Explore; an ambiguous two-bob raster remains
blocked until the user chooses a measured interpretation. The former initially
timed out on a test-only fixture binding name; it now uses the accessible Length
control. The check also exposed a readiness sentence that implied simulation was
available despite missing values; it now explicitly reports the blocked state.
Initial length correction recalibrates SI geometry without moving native pixels
or discarding the recognized angle. Recognition remains immutable after correction.

The first unmocked browser vertical slice passed all upload/physics/drag/replay
assertions in 23.4 s; the complete final run's same case passed in 21.9 s.
Early browser assertions were corrected for the shared human-friendly filename
display and interpolated playback tolerance (about 2.7e-8 m radius difference).
Source correspondence is checked by decoded pixel identity and actual backend
scene/source equality, not browser multipart byte representation.

Evidence is retained under `.cache/real-mechanics-v2/`. `visual/pendulum-analysis.json`
contains the actual scene, bindings, OCR, measurements, stage ledger and warnings;
`visual/pendulum-ready.png` and `pendulum-playing.png` show the mounted real result.
Both ready and playing desktop screenshots were opened and inspected. A portable
`visual/user-pendulum-project.json` was serialized with the production project
function from the actual result and validated with the production import contract.
Controlled-perception tests and synthetic fixture playback do not count as real
recognition evidence. No human Bengali approval, physical-device QA or independently
reviewed real gold set is claimed.

The eight new Python regressions are separate evidence categories:

| Category | Executed cases |
| --- | ---: |
| Controlled boxes/OCR compiling the real raster, including changed physical values | 2 |
| Scaled/padded raster classical geometry invariance | 2 |
| Blank rejection and explicit ambiguous-bob confirmation | 1 |
| Orientation alternative retention and same-orientation conflict protection | 1 |
| Mandatory Test B: actual raster, missing weights, real classical vision and configured OCR | 1 |
| Conditional Test C: actual compatible checkpoint inference plus real OCR/compiler | 1 |

The final `manage.py check` enabled Test C explicitly. Without its local checkpoint
option, Test C remains an explicit skip; Test B is mandatory. `manage.py doctor`
passed all five shared bundled-asset hashes, not mechanics accuracy. A final exact
M7 audit verified 110 implementation paths/helper bodies. The running normal app
reports hybrid OCR ready/ready, startup 30.553 s, with default mechanics weights
still absent. The post-commit independence audit passed all 8 tests
(`final-independence.log`); this does not claim a fresh machine or host-level
network isolation. No checkpoint was downloaded or trained, and the application's
default was not replaced or promoted.

Commands executed include, from the repository root (frontend commands inside
`frontend/`):

```powershell
$env:MECHANICS_TEST_MODEL = (Resolve-Path -LiteralPath 'models/mechanics-synthetic-20261113.pt').Path
$env:AUGPHYS_OFFLINE = '1'
$env:PYTHONPATH = (Resolve-Path -LiteralPath 'tools/offline').Path
.venv\Scripts\python.exe manage.py check
.venv\Scripts\python.exe manage.py doctor
.venv\Scripts\python.exe -m backend.tools.mechanics.check_model
.venv\Scripts\python.exe -m pytest backend/tests/test_independence.py backend/tests/mechanics/test_domains.py -q
.venv\Scripts\python.exe .cache/real-mechanics-v2/probe_families.py
cd frontend
npm.cmd test
npm.cmd run build
npx.cmd playwright test mechanics-analysis.spec.ts
npx.cmd playwright test mechanics-real-upload.spec.ts
npx.cmd playwright test mechanics-real-upload.spec.ts --grep 'unread mass'
npx.cmd playwright test
```

`MECHANICS_TEST_MODEL` enables only the conditional test; it does not configure the
application's `MECHANICS_MODEL`. The probe explicitly selects the experimental file
inside its process. The checkpoint CLI above reports the normal missing default
(expected exit 2); its explicitly selected experimental run reported exit 0.
Retained failing diagnostics include `full-check-initial-failed.log`,
`oracle-browser-initial.log`, `oracle-browser.log` and `real-browser-final.log`;
they are not counted as successful gates. Final succeeding logs are named above.

## Broader systems and remaining recognition limits

The raster-to-measurement/compiler tests cover all ten painted diagrams across all
eight existing solver families using controlled boxes/raw OCR, not finished scenes.
Those tests establish the reusable pipeline/ownership contract, not detector accuracy.
The new stage ledger and independent OCR execution apply to all of these families.
Classical recognition is explicitly limited to single-pendulum hypotheses.

A guarded, real-inference probe additionally ran the experimental checkpoint and
configured OCR on all ten synthetic rasters and five previously retained public
diagrams. Full results, source hashes, OCR, timings and reasons are in
`family-observations/summary.json` and its per-image files. No boxes, text, authored
scenes or external label calls were injected. Observed outcomes:

| Raster group | Actual compiled result |
| --- | --- |
| Synthetic Atwood | Atwood, physics structurally supported |
| Synthetic incline–pulley | Incline–pulley, physics structurally supported |
| Synthetic horizontal spring | **Wrong family: collision**, despite solver support |
| Other seven synthetic rasters | Unsupported reconstructed topology or physical constraints |
| Public Atwood and spring–mass | Unsupported reconstructed topology |
| Public projectile, inclined block and incline–pulley | Unsupported physical/attachment constraints |

The wrong-family observation is an explicit recognition failure, not a successful
reconstruction. Structural solver support cannot certify source interpretation.
Public observations took about 10.9–47.3 seconds; they include setup and local
verification load and are not a performance benchmark. There is no reviewed gold
set, and real accuracy remains null. No new recognition capability for the other
seven families, model training/promotion, handwriting accuracy or production model
readiness is claimed. A validated compatible checkpoint and independently reviewed
examples remain necessary for reliable general recognition.
