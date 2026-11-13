# Decisions and boundaries

- The historical build location is recorded in `IMPORT.md`. Original weights and images
  remain unchanged; see the training-output incident below for newly created
  folders in the older project. No production integration.
- Existing source README and handoff were read. Its review-gated production
  policy belongs to that repository; this separate module follows this request's
  automatic, explicitly assumed simulation policy.
- V2 is a YOLO26-family `DetectionModel` (Ultralytics task `detect`), trained at
  960 pixels. A 960-pixel reconnaissance initially exhausted available memory on
  this 8 GB CPU machine. Use 640 and one Torch thread here; 1024 is the training
  recipe. Low-confidence switches are a measured failure at 640.
- Original v2 names and IDs are immutable: 0 resistor, 1 voltage_source,
  2 capacitor, 3 switch. Extended schema is in `data/class_schema.yaml`.
  Do not add a duplicate dc_source detector class; normalize at the netlist edge.
- Uploaded rasters live only in request memory. No temporary upload directory,
  bounded in-memory analysis jobs expire after 15 minutes (cleanup every 30 s).
  Images persist on disk only through
  explicit correction opt-in; saved/downloaded netlists belong to the user.
- For undecodable/oversized/non-image input, return a structured HTTP rejection
  and preserve the existing frontend simulation. For valid images with failed
  recognition, return a labeled, separate assumed demonstration and original
  raster. Do not fabricate wires on an unrelated source image.
- MNA uses finite switch and meter resistance as specified. Conflicting ideal
  sources get an explicit series resistance. Numerical leakage is disclosed.
  A source short with zero/unspecified resistance uses 0.05 Ω; ideal current is
  explained, not represented by JSON Infinity.
- Constraint solving uses numerical residuals and a measurement-only Jacobian
  null space. Tiny prior regularization selects sensible free parameters. Fixed
  given/user values do not move. Browser resolution covers saved constraints
  offline; problem-language extraction remains on the Python side.
- Classical OCR is local. EasyOCR models are not downloaded on request paths.
  English detection/recognition is followed by Bengali recognition for ambiguous
  crops; cached English and Bengali weights are already available on this PC.
  The provider-agnostic `LabelReader` has a Gemini REST client, off by default.
  Server environment credentials and explicit UI opt-in are both required; only
  bounded label crops may leave the server. Transport tests are mocked. No real
  key was used and no uploaded image was sent to a VLM service.
- Photo heuristics are deliberately conservative: correct a large paper quad,
  normalize illumination, remove colored ruling while preserving dark ink.
  Faint periodic monochrome ruling removal and handwriting-specific smoothing/
  gap logic are implemented and synthetically tested; real notebook-photo
  verification remains a human dependency. Same-contrast black grids are ambiguous. Page figures split recursively on broad horizontal
  and vertical gutters; dense layouts without gutters remain uncertain.
- The synthetic generator covers all 22 detector classes, IEC/ANSI styles,
  rotations, mild pen jitter, elastic deformation, erasures and paper/scan noise.
  Intended graph/geometry accompanies generated images. This does not substitute
  for real handwritten training or independently labeled electrical test sets.
- Ultralytics licensing must be reviewed by the owner BEFORE public hosting or
  redistribution: [official licensing](https://www.ultralytics.com/license)
  describes AGPL-3.0 and Enterprise options. No deployment or redistribution was
  performed. Dataset selection/license verification remain HUMAN tasks.
- Noto Sans Bengali is self-hosted under OFL-1.1; its license ships with the font.
  [Official font source](https://github.com/google/fonts/tree/main/ofl/notosansbengali).
- New local Git repository, phase commits; no commits to AugmentedPhysics.
# Round 2 training and data isolation

Frozen detector-test hashes are recorded under `data/eval/frozen99.json`.
Near-duplicate candidates must be rejected or quarantined before training;
content groups stay together across train/validation. Unclassified image
provenance counts as synthetic for the 50% exposure cap. Only exact hashes of
the known seen textbook set are currently declared real. AITEE label taxonomy
ambiguities and all pseudo-labels require actual human completeness review.

Training uses absolute output paths contained inside this repository. This
guards against inherited Ultralytics `runs_dir` pointing at an older project.
The first relative-path smoke attempt created new run folders there; generated
files were recovered into local ignored models/v3, original weights verified,
and empty parent cleanup was automatically blocked. No old checkpoint was
overwritten. One-epoch smoke models cannot pass the promotion gate, regardless
of apparent fit. Orientation/polarity models remain disabled until a real crop
test demonstrates superiority to the heuristic. Dataset/source references are
in `dataset_sources.md`. The existing Ultralytics licensing note above remains.


## Round 2 runtime and compatibility

The saved netlist stays version 1. New total/node-pair constraints reuse existing
constraint types and target strings; schema.md documents the conventions. Job,
style and timing metadata are response-envelope fields. Unsupported components
remain representable and visibly unknown while supported parts are simulated.

Receipt/cancellation happen before awaiting job deletion. A per-upload abort
controller prevents an old request timeout from aborting a replacement upload.
Original image dimensions remain distinct from a transformed analysis preview.
UTF-8 is explicit for pipeline/tool JSON and YAML reads on Windows. PDF resources
are closed on validation/render failures. Vite was updated within version 6 to
6.4.5 after the registry audit identified development-server advisories; the
subsequent npm audit reported zero vulnerabilities at verification time.

CPU timing retains the HTTP target misses as measured; pipeline-only timing is
reported separately. No confidence statistic is a calibrated accuracy estimate.
Model promotion, independent electrical correctness and real orientation accuracy
require the evidence listed in status.md. No full GPU training was performed.

Normal dependency installation also brings in `opencv-python` through
Ultralytics and `opencv-python-headless` through EasyOCR. Pin both to 4.10.0.84
so their shared cv2 namespace uses one ABI. A clean-checkout install initially
selected full OpenCV 5 and broke nine Hough-array consumers; compatible pins
and explicit line-array normalization fixed this, with regression coverage.

## Repository import

M0 imports the clean current main recorded in [IMPORT.md](IMPORT.md) into this
independent Physimu repository. No source links, upstream remote, model weights,
private configuration, environments, or datasets are imported. Tracked generated
demos, fixtures, visual baselines, fonts, and historical documents are retained.

The Python distribution/public package is `augphys`. Setuptools maps it to the
repository root, independent of the checkout directory name. The existing
`circuit_sim` import is retained as a compatibility name for local copied code,
so original tests/tools remain unchanged. It is not an external dependency.
Both package trees resolve to this checkout. The existing direct `backend.*`
runner entry points continue to work.

Hybrid OCR, relative example model paths, two inference threads, and dependency
pins remain unchanged. The owner supplies detector/OCR weights manually after
licence review. Setup/start permit absent models; doctor is a strict optional
inventory. Circuit API, algorithms, editor, renderer, and original tests are
preserved. Historical upstream checkout references are consolidated in IMPORT.md;
earlier measurements remain explicitly historical. No mechanics code is in M0.

## M5 mechanics perception and detector ownership

Mechanics uses its own local 21-class checkpoint, cache and parser. Shared
preprocessing, OCR and job behavior are reached through the facade; circuit
pipeline implementations stay unchanged. A cancellable application model lease
serializes both domains, waits for startup warmup and clears the other detector
cache before loading. OCR models remain shared. This trades detector reload time
for single-domain detector ownership on CPU; it is a per-process guarantee for
the supported service path, not arbitrary mixed-namespace internal calls.

An analysis scene refers to the actual preprocessed native raster returned with
it. Upload preview coordinates are replaced before partial boxes are drawn.
Object location boxes never substitute for measured line/circle angles. Unread
values remain assumed or unplaced, and uncertain geometry remains editable.
The runtime performs constraint checks, not a second mechanics solver. An
unsupported result retains objects and blocks simulation until an authored
repair; recognized archetypes keep their existing unit conventions.

The broad frontend shell facade loads CSS. A narrow pure simulation facade lets
the evaluation process reuse the existing sampler and TypeScript solvers in
Node without importing browser styles. No numerical solver was replaced.
Collision after-panel readings use the existing after_velocity constraint; the
left-to-right body mapping is explicitly assumed and requires review.

Mechanics correction storage uses the existing corrections endpoint, with an
explicit domain and separate scene/image validation. Saved corrections are
unreviewed local data, never agent-authored gold or training approval. The M4
smoke checkpoint remains unpromoted; real correctness is null without HUMAN gold.
