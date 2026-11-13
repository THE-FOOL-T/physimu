# Mechanics real-data rounds

`backend.tools.mechanics.round` coordinates proposals, HUMAN review/import,
bounded mixing, fine-tune commands and independent real evaluation. It never
approves labels, writes gold scenes, runs training automatically or installs a
candidate. The owner's ongoing 600-image synthetic CPU experiment is separate.

## Start and pre-label

From the repository root, choose a new absolute run directory and unused round
number. Declare target classes before viewing candidate scores. The example
uses thin spring/rope objects; choose targets from actual reviewed weaknesses.

```powershell
.\.venv\Scripts\python.exe -m backend.tools.mechanics.round init --out "$PWD\.cache\round-2" --number 2 --targets spring rope --imgsz 640 --confidence 0.25
.\.venv\Scripts\python.exe -m backend.tools.mechanics.round prelabel --run "$PWD\.cache\round-2" --pool "$PWD\data\real_pool\new-images" --weights "$PWD\models\mechanics-baseline.pt"
```

The size/confidence and target classes belong to that round. Pre-labeling rejects
frozen paths and frozen image/near-duplicate content. Proposals, including empty
ones, remain explicitly unreviewed. Import the run's `proposals/` into a YOLO
annotation workflow, independently review every image and export reviewed labels.
Use the [review-manifest contract](labeling.md); never auto-set its review flag.
Reviewers decide and record source/licence terms and source book/page/drafter
groups. Optional external annotation services are the owner's choice.

## Import, merge and print training instructions

```powershell
.\.venv\Scripts\python.exe -m backend.tools.mechanics.round merge --run "$PWD\.cache\round-2" --export YOUR_REVIEWED_EXPORT --review YOUR_REVIEW_JSON --synthetic "$PWD\data\generated_mechanics\m4-r1-20261113-v4" --baseline "$PWD\models\mechanics-baseline.pt" --pretrained "$PWD\models\yolo26n.pt" --ratio 2 --epochs 50 --device 0
```

The importer checks per-image review/source fields, actual image/label hashes,
class order and frozen/source-group/near-duplicate leakage. Noncanonical external
class names need the existing explicit class-map importer first; the round's
proposal/review path uses the fixed mechanics order. No reviewed export is edited.

Both training and validation require reviewed real images. In **each** split,
synthetic image count is at most `floor(ratio × real image count)`. Whole synthetic
source groups are selected deterministically; there is no oversampling. The cap
is per-image exposure per epoch, not a claim of per-class instance balance. Real
class/archetype quota deficits remain visible. Ratios may be zero; negative or
nonfinite ratios are rejected. Dataset validation rechecks the cap before training.

The merged manifest has explicit `mixed` origin, per-image synthetic flags,
original image/label hashes, source groups, human review metadata and input
manifest/path provenance. Failed leakage creates a rejected folder with no
trainable manifest. Mixed validation is never independent real accuracy.

The tool prints and records a quoted fine-tune command with a separate general
pretrained control, local checkpoints and an absolute contained output path. It
does **not** execute it. The ordinary training wrapper still refuses fewer than
20 frozen printed and 20 frozen handwritten HUMAN scenes. A GPU command requires
a provisioned compatible runtime; this CPU host does not establish that runtime.
No data/model uploads or additional training occur through round.py.

## Compare old and new checkpoints

```powershell
.\.venv\Scripts\python.exe -m backend.tools.mechanics.round evaluate --run "$PWD\.cache\round-2" --candidate "$PWD\models\mechanics-candidate.pt"
```

Both models use the round's identical size, confidence, matching/NMS/AP protocol
and unchanged frozen partitions. Frozen hashes are checked before/after. Every
declared target must improve per-class recall, and no common class (at least 25
baseline instances) may lose more than 0.02 recall. Printed and handwritten must
pass separately, each with at least 20 real images. Missing metrics, smoke,
synthetic/mixed origin, differing support/protocol or a checkpoint changed since
pre-labeling prevent promotion. The decision is evidence only, not installation.

Round stages run once. Use a new round for a new comparison rather than replacing
unfavourable results. State/results are in the ignored run and the readable
`docs/mechanics/rounds/round-<n>.md`. Reports owned by another round are not replaced.

The actual [round 1 report](rounds/round-1.md) inventories the current absence of
reviewed data/checkpoints: its real metrics are null and promotion is refused.
It is not a completed real-data training round. HUMAN tasks remain independent
frozen scenes/labels, disjoint real training annotations, source/licence decisions,
adequate retraining, native Bangla review and device QA.
