# Hybrid OCR integration — 2026-11-10

**This checkout now uses hybrid OCR**, selected persistently by `ocr.backend: hybrid`
in its private `config.local.yaml`, at the owner's request. Startup warms RapidOCR
and Bengali EasyOCR; `/api/health` reports the active `ocr_backend`. The portable
example configuration now selects hybrid with bundled, relative model paths.
The supplied parallel-circuit image is now electrically verified through the live
hybrid pipeline; see the runtime repair record below. Broad real-image and
handwritten electrical accuracy remain unmeasured. The historical replay and
timing tables below describe the original integration, before this repair.

## Architecture and inspected source

The AugmentedPhysics `rapidocr.py`, `bangla.py`, `router.py`, `greek_symbols.py`
and base provider contract were read directly. Its installed RapidOCR 3.10.0
implementation, enum parameters, ONNX loading, embedded character dictionary,
classifier output and native coordinate transforms were also inspected. The
three named ONNX files and cached `craft_mlt_25k.pth`/`bengali.pth` exist. No source
or checkpoints in that project were edited or copied over.

The original providers are not safe drop-ins: default constructors can download
models, their schemas belong to another application, classifier angles are hidden
by the unified final output, and their router's broad overlap rules can merge
adjacent labels. This integration adapts their working provider patterns, NFC
handling, independent engine execution, spatial fusion and candidate preservation
into Circuit Atelier's existing dictionary contract.

`read_text()` keeps its public signature. The configured backend, with an optional
environment override, selects the new package before entering the legacy body.
Hybrid uses a shared OCR lock,
cached CPU worker processes and native tiles. RapidOCR detects text, then classifies and
recognizes explicit crops; known clockwise rotations are recorded. A bounded
opposite-direction retry handles ambiguous or reversed crops. Bengali EasyOCR
runs independently using bounded pixel-based text proposals around components,
followed by its Bengali recognizer. It does not depend on RapidOCR detections or
run another full-image CRAFT pass. Original Unicode text is preserved alongside
the normalized interpretation. No component values are set by adapters or router.

Fusion requires close centers and strong overlap or identical-text containment;
complete-link groups prevent overlap chains. Different designators stay separate.
Explicit numeric-unit readings outrank invalid strings. Across engines, semantic
rank and fixed provider order select a representative; raw confidence is not an
inter-engine vote. Every alternative retains its own engine, box, confidence and
rotation. Alternatives must meet the existing 0.65 acceptance-confidence floor
to veto another reading; extremely weak noise remains visible without becoming
a conflict vote. Conflicting plausible quantities force review, including `10 Ω` versus
`100`. Circuit symbol confusables become evidence-bearing review proposals. They
never change a raw number into a different number or silently supply a unit.

## Association and connectivity

The existing SciPy Hungarian assignment remains responsible for matching text to
components. Its costs retain body-box distance, lead-axis direction, label side,
nearer-component competition, scale-relative limits, unit/type compatibility and
OCR confidence. Candidate costs and rejection reasons remain in diagnostics.

Separate names are assigned first and inform the value pass. For hybrid readings,
a combined `R3 = 4.7 kΩ` is assigned atomically in the value pass and updates both
the label and 4700-ohm value on that component. An established label cannot be
overwritten or duplicated on another component. Distinct name/value boxes can
refer to one component, while each reading has at most one value assignment.
Detector-generated IDs alone are not treated as verified printed designators.

Hybrid rejects wrong units, bare numbers, prose/measurements, low-confidence
readings, OCR conflicts and unsupported symbol guesses. Existing near-tie ambiguity
rejection stays active. Hybrid never uses the legacy local rescue after a global
rejection. Existing `source=user` or `status=user` values survive, as do confirmed
or ignored text corrections. Repeated assignment clears stale diagnostic links.

The original wire-aware erasure and tracing algorithms were left unchanged.
Hybrid computes native `wire_overlap` and protects weak, unitless or conflicting
unassigned boxes through that existing contract. Tight detector boxes are not
expanded or unioned during fusion. Dotted/undotted crossings and assigned boxes
over crossings pass regression tests. Three identical real inputs produced
isomorphic component/node topology between backends; this is agreement, not gold
topology accuracy.

The analysis API envelope and schema version 1 are unchanged. `/api/ocr-crop`
reuses the selected parser, preventing its manual preview
from reintroducing legacy digit/unit inference into hybrid readings. Regression
tests cover this. The inspector displays raw engine/rotation evidence and lets
users choose alternatives through the existing correction workflow. User values
still use the existing undo/edit/solve path and correction storage still requires
the original opt-in.

## Configuration and rollback

Install the application's dependencies, then the optional OCR dependencies:

```powershell
python -m pip install -r requirements.txt
python -m pip install -r requirements-ocr-hybrid.txt
$env:CIRCUIT_OCR_BACKEND = "hybrid"
$env:CIRCUIT_RAPIDOCR_DET = "<local-path>/PP-OCRv6_det_small.onnx"
$env:CIRCUIT_RAPIDOCR_REC = "<local-path>/PP-OCRv6_rec_small.onnx"
$env:CIRCUIT_RAPIDOCR_CLS = "<local-path>/ch_ppocr_mobile_v2.0_cls_mobile.onnx"
# Optional: directory containing craft_mlt_25k.pth and bengali.pth.
$env:CIRCUIT_EASYOCR_MODELS = "<local-EasyOCR-model-directory>"
python manage.py serve
```

Paths can also be set under `ocr.rapidocr` and `ocr.bangla` in
`config.local.yaml`; relative paths resolve against the repository. The backend
can be persisted as `ocr.backend: hybrid` in `config.local.yaml`; the environment
variable takes precedence. A recognizer must have embedded characters or
an explicit local `CIRCUIT_RAPIDOCR_KEYS` dictionary. These models were verified
with RapidOCR 3.10.0, ONNX Runtime 1.31.1 and EasyOCR 1.7.2. Arbitrary replacement
ONNX models are not claimed compatible.

Prepare models explicitly before analysis. EasyOCR uses `download_enabled=False`.
RapidOCR receives all three explicit model paths and a dictionary preflight;
missing models/dependencies produce stage diagnostics and partial results. It
does not silently fall back to legacy. The optional external label reader retains
its original explicit per-request opt-in. No global configuration enables it.

**Immediate rollback:** set `$env:CIRCUIT_OCR_BACKEND = "legacy"`, or set
`ocr.backend: legacy` in `config.local.yaml`, and restart the server. Removing the
environment variable restores the configured backend, which is hybrid in this
checkout. No data migration or model replacement is needed. The
feature can also be rolled back by reverting its merge commit on `main`.

The original integration verification found a broken `.venv` launcher and used
the working AugmentedPhysics Python 3.12.11 runtime, with
EasyOCR and its missing support packages installed only under this checkout's
ignored `.cache/hybrid-deps`. That runtime workaround is not a production setup
change and no packages were installed into the older project.

For the subsequent activation, this checkout's restored `.venv` runs Python
3.12.10. RapidOCR 3.10.0 and ONNX Runtime 1.31.1 were installed in that environment;
EasyOCR 1.7.2 and the existing local model files are reused. Normal
`python manage.py serve` startup now follows the persistent local hybrid setting.
Startup warms the selected engines and reports `ocr_backend: hybrid` through
`/api/health`; a missing hybrid model is never disguised as ready legacy OCR.
Activation regression verification: 376 backend tests passed, one gated benchmark
skipped; Ruff lint and formatting passed for the changed Python files.

At initial activation, the original parallel-circuit JPEG was uploaded through the live application.
Its diagnostics confirm RapidOCR (14 readings, 3.719 s) and Bengali EasyOCR
(7 readings, 14.469 s), with no legacy engine stage. The 24.969-second request
retained the correct two-node topology and recognized both 10/15-ohm values,
giving 6 ohm equivalent resistance. The source-label parser issue remains:
`V=6V` was not accepted, so the source was assumed to be 12 V and the simulated
2 A supply current was wrong for the image. This initial activation record is
superseded by the runtime repair below.
Local evidence: `.cache/hybrid-activation/summary.json`, `result.json`,
`health-final.json` and `hybrid-result.png`.

## Runtime repair — 2026-11-10

The failure was reproduced on the original JPEG: RapidOCR took 3.625 s and Bengali
OCR 21.359 s against a 25-second page budget. Wire tracing never completed,
leaving six isolated terminals and zero current. Switching the backend alone did
not make this execution path reliable.

The repaired path keeps the 25-second page budget, reserves 10 seconds after OCR
for tracing/solving, and allows up to 8 seconds for tracing. Each engine owns its
models in a cached spawned process. The parent polls for cancellation/deadline,
retains completed reading snapshots, and terminates a native call that overruns.
A worker yields between text crops when fewer than three seconds remain for
another Bengali recognition call. This reports `limited` and keeps the model
loaded, rather than repeatedly killing/reloading a functioning model.
A stopped process is replaced in the background; health reports whether its
models are ready or warming. API shutdown cancels jobs and releases workers.
Startup and concurrent hybrid uploads queue before starting the per-image clock.
The two-job admission limit and explicit legacy rollback remain available.

Bengali OCR uses independent native pixel proposals inside component-adjacent
regions, split into tiles no larger than 640 pixels per side. These proposals
feed the local EasyOCR recognizer directly. This avoids repeatedly running CRAFT
over large circuit/heading regions. This machine uses two inference threads to
limit CPU contention. These are execution limits, not a general recognition
accuracy claim.

The strict parser now accepts `V=6V` and `V = 6 V` only as complete explicit
voltage expressions. Bare `V` is not a printed component identity. A compatible
source context is required during assignment; missing/wrong units, measurements
such as `V(R1)=6 V`, and prose are still rejected. No numerical prior or guessed
unit is introduced. EN/BN result banners now identify incomplete tracing,
text-reading time limits, and assumed values separately from model readiness.

See [runtime repair verification](hybrid_ocr_fix_verification.json) for the final
measured run record. Raw images, HTTP results, screenshots, logs and reproduction
scripts remain in ignored `.cache/hybrid-fix/`. The earlier PDF report is a
historical failure investigation; it is not a report of the repaired version.

| Repair check | Measured result |
|---|---|
| Backend suite with this checkout's hybrid selection | 395 passed, 1 skipped |
| Frontend unit tests / type check and production build | 82 passed / passed |
| Changed Python lint/format and frontend formatting | Passed |
| Supplied diagram, real HTTP reference runs | 7/7 correct physical values, topology, currents and power |
| Immediate upload during cold startup | Queued correctly; 48.250 s including startup, 20.152 s in the pipeline |
| Two warmed requests | 20.329 s and 19.625 s |
| Two CPU load processes | 21.703 s; correct 6-ohm, 1-A circuit |
| Concurrent uploads | Both correct; 20.281 s / 39.844 s including queue time |
| EN/BN OCR timeout and cooperative-limit banners | 4 passed; correction workflows also passed |
| Full browser regression run | 68 passed; one keyboard-filechooser timeout passed on isolated rerun |

All seven reference runs read 6 V, left printed R1 = 10 ohm, and right printed
R2 = 15 ohm from OCR, with no assumed component values. They connect to two
electrical nodes and yield 1 A supplied, 0.6/0.4 A branches and 6 W load power.
These are repeated measurements of one reference image, not seven independent
accuracy samples. Bengali OCR may legitimately report `limited`; completed
readings and the traced circuit remain available, and its loaded model is reused.

Two additional real-image smoke requests completed in 18.531/16.140 s, but both
remained partial and used assumed values. Their wiring/recognition accuracy is
not established. This repair does not claim every diagram is now electrically
correct. Existing printed/handwritten heuristics and decorative-stroke warnings
were not changed. Tests that mock legacy-specific readers now explicitly select
legacy; ordinary tests no longer depend on the owner's private backend choice.

## Original integration verification and measured limits

See [machine-readable results](hybrid_ocr_verification.json). Raw local outputs
are in `.cache/hybrid-final-evaluation.json`, `.cache/hybrid-synthetic.json`,
`.cache/hybrid-pytest.log`, `.cache/hybrid-browser.log` and `.cache/hybrid-http/`.
They are deliberately not committed because real-image results embed rasters.

| Check | Result |
|---|---|
| Relevant baseline tests before implementation | 227 passed, 1 skipped |
| Final complete backend suite | 371 passed, 1 skipped |
| Frontend unit tests | 82 passed |
| Production type check/build | Passed |
| Full browser suite, including EN/BN correction and alternatives | 67 passed |
| Ruff lint / frontend Prettier | Passed / passed |
| `python manage.py check` | Stops on 3 pre-existing format violations |
| Live RapidOCR and Bengali OCR | Both executed with local models |
| Live `6 Ω` at 0°, 90°, 180°, 270° | Correct reading found in all 4 crops |
| Existing HTTP smoke tool, identical 3 images | 3/3 HTTP 200 with simulation in each mode |

The format violations are in unchanged `backend/pipeline/associate.py`,
`backend/tests/test_associate.py` and `backend/tools/eval_association.py`.
They match `HEAD`; assertions/checks were not weakened or unrelated files
reformatted. Tests and build were run separately after this gate stopped.
The skipped test is the explicitly gated original 18-label real-model benchmark.

The six generated 24px labels use exact component geometry and one-to-one gold
text matching at IoU >= 0.5. This is **synthetic**, not the earlier 18-label tiny
font measurement. Numeric SI micro aliases are normalized only in a unit position.
Precision also credits correctly assigned name subspans inside combined labels;
such subspans do not increase full-label coverage or value accuracy.

| Synthetic measurement | Legacy | Hybrid |
|---|---:|---:|
| Exact normalized complete text | 0/6 | 6/6 |
| Complete-region association coverage/recall | 0/6 | 6/6 |
| Precision among assigned evidence | 100% (name subspans) | 100% |
| Correct component-value assignment | 0/6 | 6/6 |
| False component assignments | 0 | 0 |
| SI value absolute error where matched | unavailable | 0 Ω, 0 V, 0 F |
| OCR + association, warmed models | 12.924 s | 16.217 s |

Legacy split many labels into separate word boxes and hit component crop budgets;
the normalized full-string score must not be generalized to ordinary diagrams.
Model warmup took 30.672 s / 28.406 s respectively. Both measured OCR runs reported
time-budget warnings. Native inference is atomic and can exceed a cooperative
deadline. This is not a latency improvement claim.

On the three **recorded real-image OCR association** records, current original
`HEAD` and feature legacy both give 21/24 correct, 100% precision and 87.5%
coverage. The task's historical reference was 20/24, so no improvement is claimed.
Replaying those same old strings through hybrid's strict rules gives **7/24**,
100% precision and 29.2% coverage, with zero false assignments. This compares
association policy, not the new engines' real-image recognition accuracy.

The separate three-image HTTP run measured median/p95 **11.788/16.706 s** for
legacy and **9.856/20.629 s** for hybrid. Hybrid's first request incurred additional
cold loading. Both modes produced two partial and one extracted result. One
legacy/hybrid HTTP extraction used different recovered component counts; those
requests were not electrically verified. Three samples and overlapping CPU work
are insufficient to replace the historical 20-image performance reference.

The offline OCR and paired real-analysis runs attempted zero socket connections
with connection-denial guards; real analysis used `YOLO_OFFLINE=true` to suppress
the existing detector dependency's online probes. No model downloads occurred.
Independently reviewed full-image text/value/netlist gold was unavailable, so
real OCR accuracy, real value error, and end-to-end electrical accuracy remain
unavailable. Midpoint and disagreement rejection are validated by deterministic
tests. Two separately measured midpoint cases (plain value and combined
designator/value) were both correctly left unassigned. Review-only symbols and
genuine handwritten accuracy need more evaluation.

Reproduce the new local comparison after configuring models:

```powershell
$env:YOLO_OFFLINE = "true"
$env:CIRCUIT_THREADS = "2"
python -m backend.tools.hybrid_ocr_eval --real-count 3 --out .cache/hybrid-evaluation.json
```

## Changed files

| File | Purpose |
|---|---|
| `backend/pipeline/ocr_hybrid/__init__.py` | Isolated optional package |
| `backend/pipeline/ocr_hybrid/rapidocr_adapter.py` | Explicit ONNX loading, classifier evidence and bounded retries |
| `backend/pipeline/ocr_hybrid/bangla_adapter.py` | Cached offline Bengali EasyOCR, native coordinates |
| `backend/pipeline/ocr_hybrid/router.py` | Budgets, serialization lock, fusion, alternatives and wire evidence |
| `backend/pipeline/ocr_hybrid/worker.py` | Cached isolated models, hard native-call limits, partial evidence and cancellation |
| `backend/pipeline/ocr_hybrid/normalize.py` | Strict NFC/SI parsing without numerical priors |
| `backend/pipeline/ocr_hybrid/symbols.py` | Conservative circuit symbol review proposals |
| `backend/pipeline/text.py` | Feature-flag dispatch behind the public entry point |
| `backend/pipeline/label_assignment.py` | Strict hybrid eligibility, identity/coherence and protected corrections |
| `backend/config.py` | Portable environment overrides for local models |
| `backend/app/warmup.py` | Warm the configured OCR engines and report active backend |
| `backend/app/analysis.py`, `backend/pipeline/budget.py` | Queue startup/concurrent work and reserve tracing time |
| `backend/tests/test_ocr_backend_config.py` | Persistent selection, explicit rollback and truthful hybrid readiness |
| `backend/tests/test_ocr_worker.py`, `backend/tests/test_hybrid_queue.py` | Process timeout/restart, cancellation and startup/admission regressions |
| `config.example.yaml` | Optional OCR configuration defaults |
| `backend/app/main.py` | Consistent crop-preview parsing |
| `backend/tests/test_ocr_hybrid.py` | Offline adapter/router/assignment/API/topology regressions |
| `backend/tools/hybrid_ocr_eval.py` | Separate synthetic, frozen-record and paired-image evaluation |
| `frontend/src/types.ts` | Optional diagnostic fields only |
| `frontend/src/ui/text-inspector.ts` | Raw engine/angle evidence and existing alternative-choice workflow |
| `frontend/src/ui/upload.ts`, `frontend/browser-tests/ocr-timeout.spec.ts` | Explain incomplete tracing, limited OCR and assumed values in EN/BN |
| `frontend/src/i18n/en.json`, `frontend/src/i18n/bn.json` | Rejection explanations in both languages |
| `frontend/browser-tests/ocr.spec.ts` | Alternative selection and correction regressions |
| `requirements-ocr-hybrid.txt` | Optional verified RapidOCR/ONNX dependencies |
| `pyproject.toml` | Include the optional package in built distributions |
| `README.md` | Link to setup, verification and rollback |
| `docs/hybrid_ocr_integration.md` | Architecture, risks and delivery record |
| `docs/hybrid_ocr_verification.json` | Measured results without embedded owner images |

Integrated from `feature/hybrid-ocr-association` into `main` on 2026-11-10.
