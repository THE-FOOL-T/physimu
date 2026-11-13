# Mechanics reconstruction implementation report — 2026-11-14

Implementation started on clean `main` at
`b0e94bfc7f3e6fbb77986a5c994448b92898d71d`. This report distinguishes working
simulation/authoring integration from **unvalidated automatic real recognition**.
The production mechanics checkpoint remains absent. No model was downloaded,
trained, promoted or substituted for a real upload.

## Verified problems and fixes

| Reproduced problem                             | Cause                                                             | Result                                                                                    |
| ---------------------------------------------- | ----------------------------------------------------------------- | ----------------------------------------------------------------------------------------- |
| Normal canvas did not drag physics             | Pointer handling returned unless geometry authoring was active    | Separate captured-pointer interaction controller in Explore                               |
| Only four physical handles existed             | Pulley/collision initial controls were missing                    | All eight archetypes have constrained interactions; ten fixture cases                     |
| OCR speed/labels disagreed with solver         | Association wrote body velocity while scalar solvers read params  | Canonical compilation remaps values and label ownership together                          |
| Collision drag could not affect timing         | Solver read source x instead of overrides                         | Bounded x controls reach the existing collision equations                                 |
| Pulley dragging had no initial-state parameter | Solver always started its generalized coordinate at zero          | Shared initial displacement reaches the existing coupled solver                           |
| Corrected blocking values could remain blocked | Original unsupported provenance suppressed every solve            | Valid corrections unlock physics; source recognition remains immutable                    |
| Partial recognition exposed all geometry tools | One editing flag owned repair and authoring UI                    | Explicit Explore / Fix interpretation / Advanced authoring                                |
| Parameter changes rebuilt image layers         | Every transaction loaded/extracted sprites again                  | Renderer layers cached for the same source scene                                          |
| Arbitrary backgrounds could tear               | Paper-color erasure assumed a uniform background                  | Texture/mask risk selects an approximate moving outline on intact source                  |
| Conflicting OCR could become a given value     | Highest-ranked candidate won without mechanics conflict rejection | Conflicts/ambiguous owners stay unplaced; raw candidates and engines retained             |
| Connections could be fabricated by proximity   | Nearest bodies chosen before checking endpoint reach              | Measured trace-to-mask reach gates assembly; inferred wraps stay assumed                  |
| Reanalysis could replace user state            | No persistent recognition snapshot or correction matching         | v2 snapshot, bounded overrides, unique native matching and retained manual interpretation |

## Architecture and reused implementation

The canonical **scene schema stays v1**. Existing Pydantic/TypeScript validation,
geometry fits, masks, repair segments, source cut-outs, analytic and RK4 equations,
sampling, playback clock, graph rendering, jobs, cancellation and local model/OCR
execution are reused. Projectile, incline, pendulum and spring equations were not
rewritten. Pulley and collision equations only gained authoritative initial-state
inputs. Existing circuit implementation/core files and shared analysis coordinator
remain unchanged. `backend/app/main.py` accepts a mechanics-only panel option;
its exact new structure is pinned in the M7 audit with the prior fingerprint kept.

Reused files without substantive changes include mechanics `geometry.py`,
`sprites.py`, `detect.py`, `scene.py`'s existing schema contract, frontend
`archetypes/projectile.ts`, `incline_block.ts`, `pendulum.ts`, `spring_mass.ts`,
`sampling.ts`, and the ten fixture JSON/raster pairs. `scene.py` only
adds the unit rule for initial displacement; its generated schema is unchanged.
`backend/app/analysis.py`, `backend/core/`, `backend/domains/circuit/` and
`frontend/src/domains/circuit/` have no changes from the implementation baseline.

New backend modules:

- `understanding.py`: coarse native figure proposals and validated region choice.
- `relationships.py`: measured link-to-body endpoint candidates.
- `parameters.py`: observed quantity ownership after topology resolution.
- `ocr.py`: mechanics candidate fusion over shared engines' raw readings.
- `evidence.py`: typed objects, OCR, graph edges, hypotheses, assumptions and issues.
- `readiness.py`: structural validity versus physics support and evidence review.
- `options.py`: request-local mechanics options without global registry mutation.

Refactored backend orchestration retains the original progress stage names and
model lease. `archetypes.py` ranks supporting topology and explicit contradictions;
moving-body counts remain solver capability limits, not sufficient identification.
`associate.py`, `labels.py`, `perception.py` and `validate.py` now compile and check
the same physical paths. The shared circuit OCR grammar/fusion is unchanged.

New frontend responsibilities:

- `interaction.ts`: physical hit-testing, capture/release/cancel, previews, keyboard
  alternatives, constrained handles and one transaction per drag.
- `interaction-bindings.ts`: missing controls and scalar velocity ownership
  migration for legacy v1 scenes.
- `session.ts`: image/project IO, analysis generation, cancellation, reanalysis and
  explicit correction saving.
- `authoring-panel.ts`: recognition repair and advanced source geometry fields.
- `panels.ts`, `workspace-dom.ts`: mode composition, contextual inspector and UI
  construction helpers using the existing DOM/Vite architecture and design tokens.
- `readiness.ts`, `reanalysis.ts`, `labels.ts`, `readouts.ts`: local readiness,
  correction retention, explicit label corrections and reusable playback readouts.

`workspace.ts` coordinates these modules, the existing solver registry and renderer.
It contains no separate physics equations. No framework or dependency was added.

## State, provenance and project compatibility

The engine retains source calibration, an editable document/validated overrides and
a separate trajectory. The project wrapper is **v2**, with `recognition_scene`
recording the first interpretation. Source edits/history retain that snapshot.
Old v1 project files migrate explicitly; both their source/current snapshots get
the same missing interaction controls before consistency checking. Old velocity
labels, controls and overrides migrate together to the solver's scalar path;
conflicting user observations remain unplaced. Malformed units,
references, embedded images, inconsistent current state and invalid overrides are
rejected before replacing the loaded document.

Physics/initial edits preserve native source geometry. Numeric fields and handles
use the same BindingEngine paths, units and bounds. OCR labels keep raw text and
link to those paths. Corrected labels redraw from the authoritative Value. Generic
friction interpretation, assumed scale and authoring defaults remain disclosed.
Explicit confirmation marks a Value user-supplied. Reanalysis retains user values
only through unique native object matches; unmatched values stay available for
reassignment. An authored interpretation is retained intact while new alternatives
are offered. Late async responses cannot overwrite subsequent edits or uploads.

Pendulum linear-speed observations derive angular speed through calibrated length,
with assumed constraint provenance. Length edits preserve observed linear speed
until an explicit angular-speed or bound-label correction takes ownership. Labels retain their observed
units and derive their displayed value from the current solver input. Conflicting
explicit angular and linear observations remain available for review.

## Rendering and interaction evidence

All ten fixture paths exercise the mounted production workspace: load, initial
composition, selection, constrained pointer drag, actual parameter/trajectory
change, coupled links where applicable, playback, reset, one-step undo/redo and
portable replay. The interaction suite also covers cancellation, keyboard changes,
zoom/scroll and a blocking-value repair. Current pointer acceptance uses DPR 2.
Existing mechanics/circuit accessibility, language, responsive, reduced-motion and
source-preservation tests remain in place; circuit layout baselines were not reset.

The uploaded native raster is retained. Mechanics does not apply shared perspective
warps or ruling erasure without an inverse transform contract. Static layers,
source sprites, physical overlays and interaction handles are distinct. Existing
strict frame-zero thresholds remain unchanged. Incomplete extraction uses an
explicit approximate outline driven by the same trajectory, preserving all source
pixels. Body-owned labels move with their objects; other bound labels stay readable
at their diagram positions and reflect parameter changes.

Screenshots are retained under `.cache/mechanics-reconstruction/visual/`, with
desktop/mobile Bengali captures in `.cache/m3-visual/` and upload captures under
`.cache/m5-final/`. Desktop pendulum/Atwood and phone Bengali incline screenshots
were opened and inspected. This is browser/screenshot review, not human Bengali
approval or physical-device testing.

## Execution record

Raw logs use `.cache/mechanics-*.log`; failed intermediate attempts are retained.
The implementation remains on `main`, with implementation/test head `4109f4a`
(application code `252a7b7`). This report is
recorded in the following documentation commit. Implementation commits:

| Commit    | Responsibility                                                                                    |
| --------- | ------------------------------------------------------------------------------------------------- |
| `d00ee00` | Native pipeline, typed evidence, topology and canonical parameter ownership                       |
| `8c5a937` | Calibrated pendulum speed conversion and conflict retention                                       |
| `07ea711` | Shared interaction Values, project migration and correction state                                 |
| `252a7b7` | Workspace modes, direct manipulation, modular controllers and browser coverage                    |
| `4109f4a` | Register native file-chooser interception before keyboard activation in the existing circuit test |

Baseline: `manage.py test` passed **607 Python / 1 skipped**, **117 TS**, and build;
the ten mounted-fixture baseline plus binding case passed **11 browser tests**.
The first baseline invocation exited in optional parser initialization; collection
and the complete rerun succeeded without a dependency change.

Executed gates include `manage.py check`, `manage.py doctor`, targeted Python
perception/evidence/ownership/API suites, `npm test`, `npm run build`, and Playwright.
The first broad browser integration exposed mode-navigation assumptions in tests;
those scenarios now explicitly open the intended modes without dropping assertions.
M7's exact audit detected the intentional route extension; the coordinator was
restored unchanged and the audit pins the new mechanics-only route, retaining its
old fingerprint. A later browser run hit an HTTP 404 while a concurrent Vite build
replaced served files; final build/browser runs are sequential.

The first real-image probe lacked a Windows multiprocessing entry guard. It was
stopped and its outputs archived as launcher failures. The corrected guarded probe
is the sole real-runtime evidence used below. Intermediate formatting/type errors
were corrected before the final gates; none is reported as a passing check.

The final ownership audit found a missing angular-speed binding in old pendulum
scenes. The first derived-speed TS regression failed at that missing control;
migration now supplies it. Final `manage.py check` passed **649 Python, 1 skipped**
and **130 TypeScript**, including lint, formatting and production build. Python's
single skip is the optional `CIRCUIT_REAL_OCR_TEST=1` CPU benchmark. Evidence:
`.cache/mechanics-final-check.log`. The focused mounted legacy-pendulum case passed
after the final build (`.cache/mechanics-final-pendulum-browser.log`).
The post-commit repository independence audit also passed **8 tests**
(`.cache/mechanics-final-independence.log`); this is not a separate claim of a
fresh machine, absent source checkout or host-level network isolation.

The preceding complete browser gate passed **135, skipped 2**. After the final
pendulum/migration changes, two full runs each passed **135, skipped 2, failed 1**:
the circuit keyboard test timed out awaiting the native file-chooser event. Three
isolated repetitions passed, but the 13-case layout sequence reproduced the failure
(12 passed, 1 failed). Browser capture showed a trusted Enter and upload-input click
with active user activation. Registering the chooser listener **before navigation**
then passed all **13 layout tests**, with every original action/assertion retained.
This points to browser interception timing; no circuit application change was made.
The fix is `4109f4a`. Temporary event logging was removed.

Failed full runs are retained in `.cache/mechanics-final-browser.log` and
`mechanics-final-browser-rerun.log`; event evidence is in
`mechanics-keyboard-layout-events.log` and the passing fix in
`mechanics-keyboard-interception-check.log`. Trace-enabled diagnostics also hit
timeouts, including teardown after completed keyboard actions; the wider traced
run was stopped after three failures. Those resource-heavy attempts are not counted
as passing gates. The two normal skips are optional circuit owner-analysis captures
absent from the ignored private cache. The final full run is recorded below. Normal
app health after restart is detector/OCR **ready/ready**, both hybrid OCR engines
ready, startup **25.572 s**. The mechanics production checkpoint remains absent.

**Final complete browser gate: 136 passed, 2 skipped, zero failed, 5.3 minutes.**
The keyboard upload case passed after the complete layout sequence. Log:
`.cache/mechanics-final-browser-verified.log`, exit 0. All ten physical interaction
and fixture-playback cases, repair/reanalysis, mobile/Bengali/accessibility and
unchanged circuit layout baselines are included. The prior failures above remain
part of the execution record. Generated circuit timing JSON is preserved under
`.cache/mechanics-reconstruction/` and restored to its tracked baseline in Git.

Commands actually executed from the repository root (frontend commands inside
`frontend/`):

```powershell
.venv\Scripts\python.exe manage.py check
.venv\Scripts\python.exe manage.py doctor
.venv\Scripts\python.exe -m pytest backend/tests/test_independence.py -q
.venv\Scripts\python.exe -m pytest backend/tests/mechanics/test_parameter_contract.py backend/tests/mechanics/test_evidence.py backend/tests/mechanics/test_perception.py backend/tests/mechanics/test_region_api.py -q
cd frontend
npm.cmd test
npm.cmd run build
npx.cmd playwright test
npx.cmd playwright test mechanics-interaction.spec.ts --grep 'legacy pendulum'
npx.cmd playwright test layout.spec.ts --grep 'keyboard operation' --repeat-each=3
```

## Real local detector/OCR observation and remaining boundaries

The available synthetic-only experimental checkpoint was selected **only inside a
test process**, with the normal application default left unchanged. Actual inference
and configured local hybrid OCR ran on three previously available public diagrams.
No oracle boxes/text, fixtures, external label calls or downloads were used.
Their hashes, actual results and timings are in
`.cache/mechanics-reconstruction/real-summary.json` and `real-*.json`.

| Real image    | Candidate detections | Observed result                    | Wall time |
| ------------- | -------------------: | ---------------------------------- | --------: |
| Atwood        |                    5 | Unsupported reconstructed topology |   27.40 s |
| Spring mass   |                    8 | Unsupported reconstructed topology |   16.25 s |
| Incline block |                   11 | Unsupported applied-force evidence |   36.81 s |

All three remained unsupported: Atwood and spring lacked a supported reconstructed
topology; incline retained unsupported force evidence. These are useful failure
observations, **not real accuracy scores or successful reconstruction**. OCR budget/
partial warnings remain visible. There is no independently reviewed real gold set
here. Timings include setup and concurrent local verification, not a benchmark.

**Implemented and tested:** fixture simulation, direct manipulation for all eight
archetypes, parameter/label ownership, modes, repair/authoring, source fallback,
typed evidence, native panel selection, project migration and failure handling.

**Blocked by external assets/evidence:** production automatic recognition readiness,
approved compatible mechanics weights, independent real detection/physics gold and
human printed/handwritten/Bengali evaluation. The experimental checkpoint is not
promoted. Arbitrary applied-force systems and configurations outside the eight
existing solvers remain explicitly unsupported. Rope wrapping and missing scale
can still require review; geometry confidence is not calibrated accuracy.

**Not implemented:** new solver families, new model training/promotion, validated
Bengali handwriting/language accuracy, or independent human/device QA. These are
not represented as finished mechanics recognition.

To verify when an approved checkpoint is supplied, set `MECHANICS_MODEL` to its
local `.pt` path, run `python manage.py doctor` for shared assets, start the app and
upload independently reviewed diagrams in Mechanics. Inspect evidence, readiness,
object/parameter ownership, physical trajectories and source overlays. Run the
existing `backend.tools.mechanics.eval_end_to_end` protocol against reviewed frozen
scenes; empty/unreviewed partitions must retain null accuracy metrics.

From the repository root in PowerShell, after supplying the approved local file
and an independently reviewed frozen evaluation root:

```powershell
$env:MECHANICS_MODEL = (Resolve-Path -LiteralPath 'models/mechanics.pt').Path
$env:AUGPHYS_OFFLINE = '1'
$env:PYTHONPATH = (Resolve-Path -LiteralPath 'tools/offline').Path
.venv\Scripts\python.exe manage.py doctor
.venv\Scripts\python.exe manage.py check
.venv\Scripts\python.exe -m backend.tools.mechanics.eval_end_to_end --root 'data/mechanics/frozen' --out '.cache/mechanics-approved-evaluation.json'
.venv\Scripts\python.exe manage.py serve
```

Use the actual reviewed root in place of `data/mechanics/frozen`. In a second
terminal, run `.venv\Scripts\python.exe manage.py browser` against the served build. A passing doctor
checks the shared bundled assets; it does not certify mechanics model accuracy.
Inspect evaluation record counts and human-review provenance before interpreting
any metric. No checkpoint installation, download or gold review is implied here.
