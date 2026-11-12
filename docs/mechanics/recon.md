# Mechanics reconnaissance — before M0

Date: 2026-11-12 (Asia/Dhaka).

This is the documentation-only reconnaissance requested in section 2 of the
master brief. M0 has **not** started. No circuit source, models, images,
configuration, dependencies, or Git history were copied into this workspace.
No product code was written or changed. No tests, browser scenarios, model
inference, training, or server were run.

## Source inspected and reproducible evidence

The destination, `D:/Physimu-Interactive Augmented simulation`, was empty and
was not a Git repository at the start. A local baseline was discovered at
`D:/Circuit Simu/circuit_sim` and inspected read-only. No source path was
explicitly supplied in the request; discovering this checkout does not select
it over the prescribed GitHub source for M0.

| Observation | Result from this reconnaissance |
| --- | --- |
| Local source branch | `main` |
| `git rev-parse HEAD` | `97702f2bbfd42f15f434b0acffdc1fc4bc678400` |
| Latest subject | `Bundle working inference models and portable hybrid setup` |
| `git status --short --branch` | `## main...origin/main`, with no working-tree entries |
| Configured origin | `https://github.com/THE-FOOL-T/circuit-sim.git` |
| `git log --oneline 516e232..HEAD` | One commit: `97702f2` |
| `git diff --stat 516e232 HEAD` | **30 files changed, 1767 insertions(+), 60 deletions(-)** |
| `git check-ignore config.local.yaml` | `config.local.yaml` is ignored |
| Language JSON inventories | 404 keys in each of `en.json` and `bn.json`; key-name comparison returned no differences |

Git metadata describes the local checkout and its existing remote-tracking
state. No fetch or network lookup was performed, so current remote freshness
is not verified. No local `AGENTS.md` was found in the inspected workspace,
source tree, or their applicable parent locations.

The brief's earlier "233 files changed" is not the result of comparing
`516e232` to this HEAD. It may describe another comparison, whose endpoints
were not supplied. The measured comparison here is the 30-file result above.

## Conflicts requiring resolution before M0

### 1. Current main tracks five inference weights

The brief says weights are not in Git and requires excluding all weights from
the new repository. Current main deliberately does the opposite for portable
distribution. `git ls-files models` includes these five Git LFS paths:

- `models/v2_original.pt`
- `models/ocr/rapidocr/PP-OCRv6_det_small.onnx`
- `models/ocr/rapidocr/PP-OCRv6_rec_small.onnx`
- `models/ocr/rapidocr/ch_ppocr_mobile_v2.0_cls_mobile.onnx`
- `models/ocr/easyocr/bengali.pth`

`.gitignore` now explicitly unignores `models/v2_original.pt`, and
`.gitattributes` assigns LFS filters to all five. `models/manifest.json`,
`models/NOTICE.md`, `models/MODEL_CARD.md`, README, and
`docs/portable_setup.md` describe this intentional distribution exception.
Older `docs/status.md` still says weights are excluded from Git.

Thus "copy everything tracked unchanged" cannot literally coexist with the
brief's weight exclusion and unchanged ignore rules. The brief's stated
no-weights policy is the proposed policy for the destination, but no import
or ignore-rule change has been made. The source/baseline and necessary
documentation/setup exceptions must be settled before M0. No rights or
dataset/model licence approval is inferred from bundled notices.

### 2. Hybrid OCR is now the default, not opt-in

At `516e232`, `config.example.yaml` selected `legacy`, used null hybrid model
paths, and left inference threads null. Current main selects `hybrid`, points
to the four local OCR files above, and sets **two** inference threads.
`requirements.txt` now directly pins `rapidocr==3.10.0` and
`onnxruntime==1.31.1`; the hybrid requirements file is retained for existing
commands rather than being the only installer for these dependencies.

`backend/tests/test_portability.py` explicitly asserts hybrid defaults, two
threads, and model paths contained in `models/`. Returning the example
configuration to the older defaults would change current circuit behaviour
and fail those assertions. The external crop reader remains separately
opt-in and off by default; it must not be confused with local hybrid OCR.

### 3. Portable launch scripts require all five models

New `setup.ps1` checks the model bundle before creating the environment;
`run.ps1` runs `manage.py doctor` before serving. The doctor reports missing
files, LFS pointers, wrong sizes, or wrong hashes and exits unsuccessfully.
Therefore the current README's recommended Windows setup/start path does not
work unchanged in a source-only import with no weights. Direct
`python manage.py serve` has a separate missing-model degradation path.

M0 needs an agreed source-only setup/documentation treatment while preserving
circuit analysis behaviour. No script has been changed or executed here.

### 4. M0's blanket image exclusion conflicts with preserving the app/tests

Tracked images include five generated demo PNGs in `frontend/public/demos/`,
Playwright layout baselines, and documentation images. The initial UI fetches
`/demos/mixed-network.json` and uses its local demo raster; browser layout
checks use the committed snapshots. These are distinct from private owner
uploads/datasets. Excluding every image literally would remove baseline assets
needed to preserve behaviour and visual checks. Proposed interpretation:
retain baseline demo/test/documentation assets; exclude private datasets,
uploads, and model weights. This interpretation has not been applied.

### 5. Independence wording needs to distinguish execution from history

M0 allows documentation mentions only in `docs/IMPORT.md` while also requiring
all existing documentation be retained. README and `docs/portable_setup.md`
currently contain upstream clone/release URLs; `docs/decisions.md` records the
local source checkout and the older-project training-output incident.
Preserving these texts verbatim cannot pass that literal search rule.

The new app can be self-contained without an upstream runtime dependency,
but the archival-documentation exception or documentation edits need to be
explicit. Internal `circuit_sim` package identifiers also need to be
distinguished from imports of an external circuit-sim checkout. No destination
remote, dependency, alias, link, or submodule has been created.

## A2 baseline audit

Paths and line counts below refer to the inspected source commit. Line counts
are file-read observations, not test counts.

| Brief item | What the current source actually contains | Consequence |
| --- | --- | --- |
| Python/FastAPI and TypeScript/Vite | `pyproject.toml` requires Python `>=3.12,<3.13`; README specifies Node 22+; frontend uses Vite 6.4.5 and TypeScript 5.9.2. | Reuse the pinned toolchain. Installed runtimes were not verified in this pass. |
| Runner commands | `manage.py` is 150 lines and supports `dev`, `serve`, `test`, `check`, `eval`, `smoke`, `browser`, `build`, `ocr-debug`, and the new `doctor`. | The six commands named in A2 are a subset. `test` runs pytest, frontend unit tests, then `npm run build`; build includes type checking. `check` additionally enforces Ruff lint/format and Prettier. |
| Package-relative imports | Production backend modules use package-relative imports. Root `__init__.py`, `bootstrap.py`, and explicit setuptools package mapping exist. Tests commonly import `circuit_sim.backend...`; test conftest calls `ensure_package()`. | Renaming to default `augphys` is not merely a folder rename. Preserve an internal compatibility import for unchanged circuit tests or explicitly resolve this naming change; never import external source. |
| Netlist contract | `backend/pipeline/netlist.py` is 173 lines. Pydantic v2 base config forbids extras and nonfinite floats; components have exactly two terminals. `Value` has the listed fields **plus `unit_inferred`**. Its source enum does not include `geometry`. `Meta.provenance` also supports **`edited`**, with legacy aliases. | Preserve the circuit version-1 shape. Mechanics needs its own contract with geometry provenance and authored/unsupported results. |
| Page/image engine | `backend/pipeline/engine.py` is 426 lines. `analyze_page` preprocesses, estimates style, detects once, splits figures, transforms boxes/terminals into region-local native coordinates, and calls `analyze_image`. Responses include diagnostics, source image, style estimate, provenance, warnings, timings, and optional observed netlist/regions. | Reuse entry points in-process. Coordinates belong to the actual decoded/preprocessed/cropped analysis raster. |
| Retry strategy | `analyze_image` tries `(alternative, repair)` settings `(False, False)`, `(False, True)`, `(True, True)` under budgets and chooses by validation score; bounded recovery can replace the result if its score improves. | A2's older "several snap scales" description is no longer the actual retry loop. Preserve the current threshold/repair behaviour. |
| Detector | `backend/pipeline/detect.py` is 221 lines. It still uses a size-one `lru_cache`, inference lock, config/`CIRCUIT_MODEL`, and explicit missing-file error. It supports tiled windows, same-class NMS, source orientation/polarity heuristics, and switch-gap inference. | Not every box becomes a two-terminal component: junction, text-label, terminal-marker, plus/minus-mark, and arrow boxes become annotations. Mechanics must not use the circuit detection-to-component conversion. |
| Jobs | `backend/app/jobs.py` is 169 lines. STAGES is still the nine-item circuit tuple; `get()` uses that global tuple. Defaults remain two workers and 900 seconds, plus **32 retained jobs**, initial **queued** state, stage history/timers, optional image omission, immediate cancellation admission release, and removal of captured runner rasters. | M1 must add per-job stages without losing these newer behaviours. Cancellation exception inherits `BaseException`. |
| API execution | `backend/app/main.py` is 430 lines. All listed routes exist, plus `/api/health` and `/api/ocr-crop`. Synchronous `/api/analyze` now calls `/api/analyze/start` internally and polls the same JobStore. Worker execution calls `backend/app/analysis.py:run_analysis`. | A circuit adapter must preserve the service path, not bypass warmup/queuing/error normalization when adding domain dispatch. |
| Shared analysis service | `run_analysis` waits for model warmup, serializes concurrent hybrid analyses before starting the page budget, calls `analyze_page` directly, orders warnings, and catches ordinary errors into the existing circuit demo fallback. | These responsibilities extend beyond the older engine-only account. Mechanics must never inherit that demo fallback. |
| API limits and storage | Request middleware/rate limiting, typed error keys/request IDs, PDF resource cleanup, image-free solve/resolve payloads, and opt-in text corrections are implemented. | Preserve routes and response keys. Current corrections validate **Netlist**, not an arbitrary domain document. A future mechanics correction extension needs explicit domain validation. |
| Frontend composition | `frontend/src/main.ts` is **1125 lines**, not approximately 1080. It imports a raw HTML shell, state, parameters, readouts, explanation, translation, upload, workspace, canvas editor, text inspector, image store, and local solvers. | The brief correctly warns its older layout may be stale. Main was read in full before any proposed adapter design. |
| Editor/history | `ui/editor.ts` is 120 lines and **re-exports** `History`; implementation is in `ui/edit-history.ts`. It stores structural before/after changes, excludes raster paths, and caps undo entries at 80. Canvas editor, popover, edit geometry, and topology rebuilding are separate. | Reuse the pattern rather than passing a mechanics scene into Netlist-specific edit functions. |
| Rendering | `overlay/renderer.ts` is 503 lines; 0.1 s frame cap, DPR cap 2, reduced-motion handling, and image alpha **0.82** are present. Fit/letterboxing is in `overlay/view.ts`; actual hit mapping uses `clientToImage`/`imageToScreen`. | Copy the full offset-aware transform approach for mechanics. The small exported image/canvas helpers alone do not handle Fit offsets. Keep circuit rendering unchanged. |
| Flow and simulation loop | Current particle rendering is in `overlay/flow.ts` with settings, contrast, smoothing, and fair allocation. The circuit physical-time loop and graph remain in main. | There is no reusable fixed-1/240 mechanics loop, trajectory scrubber, or scene sprite compositor yet. |
| Internationalization | EN/BN JSON each contains 404 keys. The existing unit test checks both key sets **and named placeholders**. Font is self-hosted `NotoSansBengali.ttf` with OFL text; CSS includes 44px targets and reduced-motion rules. | Extend `mech.*` later with both parity checks intact. Matching keys do not establish native-speaker approval. |
| Optional local hybrid OCR | `text.py` dispatches legacy/hybrid behind one public `read_text` signature; hybrid adapters, router, normalization, symbols, and spawned worker lifecycle exist. | Hybrid is currently the default, as described in conflict 2; public API reuse needs to account for circuit semantics inside OCR. |
| Hard cases | Five case reports exist. Their prose records symbolic-label false positives, a manually repairable 24 V circuit, rotated/misclassified resistors, a misclassified meter, and conflicting bare readings. | The brief's caution about four cases still needing repair is supported by historical status. No cases were rerun or independently reviewed here. |

## Reuse, adaptation, and new code boundaries

### Preserve and reuse through facades

Backend facade candidates for M1 are `load_config`/`resolve_path`,
`decode`/`preprocess`/`figure_regions`, `estimate_style`, `read_text`, relevant
OCR proposal/crop primitives, and `JobStore`/`Cancelled` helpers. The first
facade should re-export existing implementations without moving circuit files
or introducing circular imports through the application module.

`decode` applies EXIF orientation and bounds the long side to 1800 pixels;
preprocessing can rectify perspective and crop/split figures. Native pixels
therefore mean pixels of the returned analysis raster, not necessarily the
camera original. Store/display that exact raster with its scene coordinates.
The existing image-free solve payload and Blob URL ownership patterns are
useful for keeping editor history and requests small.

Frontend facade candidates are language/digit/formatting helpers, safe
preference storage, image ownership, and existing shell/workspace entry points.
Circuit MNA, local constraint resolution, current-path solving, and explanation
modules remain entirely circuit-owned. They are not mechanics solver helpers.

### Adapt carefully; existing pieces are not domain-neutral

- **OCR objects need more than bbox on some paths.** `ocr_tiles.windows` and
  the Bengali hybrid adapter can use boxes, but `ocr_regions.anchored_regions`
  also accesses `id` and `type`. Circuit association additionally requires
  terminal geometry, polarity, values, and electrical-unit families. Reuse a
  small read-object adapter where appropriate; do not fabricate two-terminal
  mechanics bodies to satisfy circuit functions.
- **OCR already applies circuit semantics before association.** Legacy crop
  quality/retries import `value_tokens.parse_value`; hybrid `router.rank`,
  `same_region`, `fuse`, conflict detection, and rotation retries use the strict
  circuit parser. `clean_strokes` also removes long lines that mechanics may
  need for surfaces, ropes, or dimensions. Preserve original evidence and
  keep the geometry image separate from text-proposal cleanup. A facade
  re-export alone does not make the current reader grammar-neutral.
- **Unicode reuse must be selective.** Bengali/subscript digit maps and NFC
  handling are useful. The entire legacy normalizer is inappropriate for
  mechanics because it contains resistor designator/ohm repairs and electrical
  unit inference. The strict hybrid normalizer is also electrical vocabulary.
- **Crop-reader transport is reusable, vocabulary is not.** `label_reader.py`
  has a circuit-specific prompt, `valid_label`, and circuit parser. Reusing it
  unchanged would reject mechanics units. Preserve consent, server-only
  credentials, crop bounds, no-default-network policy, and mocked transport
  testing; add mechanics vocabulary through the allowed facade boundary later.
- **Wire tracing supplies ideas, not mechanics topology.** `prepare_trace`
  refines electrical terminals, erases certain labels/annotations, skeletonizes,
  and handles electrical crossings/gaps. Rope attachment, pulley tangency,
  body masks, and static-line repairs need mechanics implementations.
- **Upload UI assumes circuit results.** `UploadWorkspace` has its own hard-coded
  circuit stages, `AnalysisResult.netlist`/`solution`, component previews, summary,
  and imported-event component count. A backend-only domain field cannot make
  it accept mechanics envelopes. Preserve its circuit behaviour while adding a
  separate domain-aware boundary and mechanics presenter.
- **Frontend lifecycle is currently global.** Main installs document/canvas
  listeners, a perpetual animation frame, a five-second health interval, and
  eagerly starts the default circuit demo. Workspace/editor/popover code queries
  global IDs and appends elements outside a supplied container. No complete
  DomainHandle-style teardown exists. Mount/unmount work must prevent duplicate
  listeners/loops and hidden circuit controls handling mechanics actions.
- **History is Netlist-typed.** Mechanics can implement the same structural
  history pattern for Scene without editing circuit history/editor modules.
  Circuit editing deliberately freezes simulation until Run; mechanics live
  edit/re-solve behaviour must remain separate.
- **Data tooling has circuit-specific gates.** `train.py` requires original
  circuit training data, fixed first four circuit classes, a frozen-test audit,
  and real/synthetic exposure constraints. `compare_detectors.eligible` hard-codes
  99 images and named circuit classes. Leakage signatures/grouping are reusable
  ideas; mechanics schema, quotas, promotion policy, synthetic bootstrap, and
  round tooling need their own wrappers. Training resolves output paths to
  absolute workspace-contained locations before executing; preserve this guard.

The OCR coupling is a future integration risk against the "do not edit circuit
pipeline" rule. No shared-module refactor or alternative OCR behaviour is
authorized or implemented by this report. Any needed extension beyond facade
wrappers must be identified explicitly in the relevant milestone plan.

### Write new in the later milestones

- Domain registries/adapters and facades, followed by the mechanics scene schema,
  defaults, validation, unsupported envelope, and generated schema documentation.
- Deterministic diagram painter and non-gold synthetic fixtures for all eight
  archetypes and specified projectile/spring variants.
- A browser-only mechanics solver set, fixed-step trajectory/playback kit,
  layout/forces/events, native-pixel sprite rendering, frame-0 checks/degradation,
  parameter bindings/classes, and geometry restoration.
- Mechanics workspace, blank-image authoring, mask/repair/link editing,
  import/export, accessibility, PNG export, and EN/BN text pending human review.
- Gold **templates and tools only**, leakage/quota/provenance tools, synthetic
  generation, bounded CPU smoke-training wrappers, and honest evaluation reports.
- Mechanics detection/model residency management, geometry, label grammar,
  association, archetype matching, sprite extraction, and perception engine.
- Real-data rounds/handwriting tools; physical circuit/shared implementation
  moves occur only in M7 after both domains are stable.

The frozen real scenes remain a HUMAN task. No gold scene, human-review flag,
licence decision, training-data approval, or substitute real benchmark was
created during reconnaissance.

## Recorded results versus measurements made here

The brief's 286/82/67 totals describe an older release checkpoint, not the
current whole baseline. They should not be used as the expected current count
without rerunning the suite in M0.

| Evidence in the inspected source | Historical result, not rerun here |
| --- | --- |
| `docs/status.md`, final round-three section | 286 Python passed; `docs/verification.md` adds one skipped optional real-OCR test. 82 TypeScript passed; 67 browser scenarios verified across runs, with one full-run chooser timeout and successful focused reruns; 12 strict layouts. |
| `docs/hybrid_ocr_integration.md` / fix JSON | Later runtime repair: 395 backend passed, one skipped; 82 frontend passed. Browser full run: 68 passed, one failed chooser wait; isolated keyboard rerun passed. This is not a clean single-run 69/69 claim. |
| `docs/portable_setup.md`, 2026-11-11 verification | Latest documented `manage.py check`: **397 backend passed, one skipped; 82 frontend passed**, formatting/type check/build passed. These are documentation claims awaiting M0 reproduction. |
| `docs/reference_99_metrics.md` | Existing reviewed 99-image detector set at size 640/confidence .25: recall resistor .8809, voltage source .7464, capacitor 0, switch .2000, ammeter/voltmeter 0. These numbers are not in `data_inventory.md` itself; that file records class counts. |
| `docs/ocr_benchmark.md` | Tiny-label exact recall 5/18, still labelled limited/synthetic benchmark evidence; no independent whole-image OCR accuracy follows. |
| `docs/status.md` / `docs/performance.md` reference | Historical 20-image HTTP median/p95 9.649/12.258 seconds; targets missed. Current hybrid docs also record different, smaller protocols, including seven repeats of one reference image. These cannot replace a fresh comparable 20-image latency result. |
| `docs/results.md` / evaluation inventory | Printed and handwritten independent end-to-end metrics are null, zero examples. `data/eval` is **not entirely empty**: it contains frozen99 hashes, association-record evidence, and READMEs; the independent printed/handwritten image/netlist sets are absent. |

Fresh verification for this reconnaissance is deliberately limited to file
reads, Git metadata/diffs, line counts, ignore status, and JSON key inventories.
The language unit test itself was not executed, nor was placeholder parity
independently rerun.

```json
{
  "phase": "recon_only_before_M0",
  "backend_tests_passed": null,
  "backend_tests_skipped": null,
  "frontend_tests_passed": null,
  "browser_tests_passed": null,
  "strict_layouts_passed": null,
  "build_passed": null,
  "independence_gate_passed": null,
  "current_cpu_latency_seconds": null,
  "current_gpu_availability": null,
  "mechanics_real_accuracy": null,
  "note": "No execution gates were requested for reconnaissance. Re-measure circuit gates in M0 after resolving source/import conflicts; HUMAN-supplied independent mechanics gold is required for real accuracy."
}
```

No current hardware claim is made from the old no-CUDA documentation. No model
bytes or hashes were independently verified here. OpenCV full/headless are
both still pinned to `4.10.0.84`; Torch/Torchvision requirements remain
`2.13.0`/`0.28.0`. README describes the CPU wheel-index installation route.
These are source pins, not an audit of installed binary packages.

## Scope, assumptions, and next step

1. The discovered local checkout is suitable for read-only reconnaissance
   because its origin matches the repository in the brief. Its use for M0 and
   freshness versus GitHub main are not yet confirmed.
2. The supplied section-2 instruction takes precedence over the later milestone
   work: create this report, summarize it, and stop. No M0 plan, repository
   initialization, commit, package rename, source import, or mechanics code is
   included in this turn.
3. Historical metrics are retained as attributed evidence, never presented as
   new measurements. Gold/annotation/language/device/licence review remains
   human work, and unmeasured results remain null.
4. Proposed interpretations for bundled assets, package compatibility, and
   archival references are recommendations only. Conflicting source/import
   rules have not been silently resolved.

Before M0, settle the source revision and the treatment of tracked weights,
hybrid defaults, source-only Windows startup, baseline image assets, and
historical upstream references. Then, on an explicit continue, write
`docs/mechanics/plan-M0.md`, perform only M0, measure its gates, append its status,
and stop again. Reconnaissance ends here.
