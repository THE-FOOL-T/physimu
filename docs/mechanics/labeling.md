# Mechanics data and human review

The class order is fixed in [mechanics_class_schema.yaml](../../data/mechanics_class_schema.yaml):
block, ball, bob, cart, incline, floor, wall, ceiling, pivot, ground_hatch, pulley,
rope, rod, spring, arrow_force, arrow_velocity, angle_mark, axis, trajectory_arc,
dimension_line, text_label. Detector boxes locate symbols; they do not replace
thin-line geometry, attachments, Values or masks. No circuit class id is reused.

## R0: HUMAN frozen gold first

Supply at least 20 printed and 20 handwritten real diagrams, with three or more
per archetype where possible. Keep books/pages/drafters separate from train and
validation. The source group is the identity of that source, not an arbitrary
screenshot filename. Decide source licences yourself and record the decision.
Codex never authors, edits, auto-generates or approves these frozen scenes.

For the owner's requested public starting material, see
[public-candidates.md](public-candidates.md). Its images/scaffolds are unreviewed,
outside gold/training, and include explicit quality/source exclusions.

Create a null-scene scaffold **outside** the frozen tree:

```powershell
.\.venv\Scripts\python.exe -m backend.tools.mechanics.make_gold_template YOUR_IMAGE --out 'D:\Physimu-Interactive Augmented simulation\.cache\human-authoring-001'
```

The output says NOT GOLD, copies the image unchanged, records its hash and leaves
`scene: null`, review false, reviewer/source fields incomplete. Use the M3
[authoring guide](authoring.md) to author the source scene yourself. A portable
project's `scene` is the canonical source geometry; `current_scene` and simulation
overrides must not accidentally become source calibration. Independently review
every object, attachment, mask, physical Value and intended regime. Unknown or
assumed numbers remain explicit; a produced simulation is not correctness.

Only a person can fill the following envelope and designate it gold:

```json
{
  "kind": "mechanics-human-gold",
  "version": 1,
  "source": {
    "image": "images/owner-example.png",
    "sha256": "HUMAN records exact source SHA-256",
    "group": "HUMAN book/page/drafter group",
    "reference": "HUMAN source reference",
    "licence_note": "HUMAN decision and attribution"
  },
  "review": {
    "human_reviewed": false,
    "reviewer": "",
    "reviewed_at": "",
    "notes": "Set reviewed only after your actual independent review."
  },
  "scene": null
}
```

Put actual reviewed files at `data/eval/mechanics/{printed,handwritten}/<id>.gold.json`,
with images relative to that style directory. `scene.meta.style` identifies the
printed/handwritten source and provenance is authored. Optional per-class
detector evaluation also needs reviewed YOLO labels: add relative `labels` and
`labels_sha256` to `source`. Gold validation checks those labels when present.
Neither annotations nor labels are supplied by this milestone.

Validate one scene, then freeze **hash metadata only**:

```powershell
.\.venv\Scripts\python.exe -m backend.tools.mechanics.gold --scene YOUR_REVIEWED_GOLD_JSON
.\.venv\Scripts\python.exe -m backend.tools.mechanics.gold --freeze-out 'D:\Physimu-Interactive Augmented simulation\data\eval\mechanics\frozen.json'
```

The tool refuses absent/unreviewed scenes, mismatched actual image dimensions,
bad scene references/units, changed hashes and an existing freeze manifest. It
never writes a scene. The manifest uses portable relative paths and records
image, scene and optional detector-label hashes plus source groups. Later audits
refuse changed frozen content. A small partial collection can be inventoried,
but full training refuses fewer than 20 images in either style partition.

## R1: synthetic bootstrap

```powershell
.\.venv\Scripts\python.exe -m backend.tools.mechanics.make_synthetic --out 'D:\Physimu-Interactive Augmented simulation\data\generated_mechanics\r1-new' --count 600 --seed 42
.\.venv\Scripts\python.exe -m backend.tools.mechanics.leakage 'D:\Physimu-Interactive Augmented simulation\data\generated_mechanics\r1-new' --out 'D:\Physimu-Interactive Augmented simulation\.cache\r1-leakage.json'
```

Outputs must be explicitly absolute, inside this checkout, new or empty, and
outside frozen folders. Keep output under ignored `data/generated_mechanics/`
or `.cache/`. Production accepts 400–800 images; `--small` is explicitly for tests
and plumbing. All data is synthetic, never frozen gold or real-world accuracy.
The directory contains images, YOLO labels, scene JSON, indexed PNG masks,
object-to-mask mappings with amodal boxes, manifest, counts, data.yaml, source
notice and contact sheet. Mask pixels identify the visible topmost object;
occluded objects retain their amodal box. Fonts come from local Pillow/Noto.

The same homography transforms pixels, masks, boxes and scene coordinates.
Labels are reflected locally before a mirrored image so text remains readable.
Photographic/scan geometry is exported in native pixels with its homography;
these augmented scenes are detector/geometry supervision, not calibrated solver
demos or frame-zero renderer benchmarks. Physical numbers are programmatically
authored; handwritten/photo styles are simulations, not real handwriting/photos.
Shared diagram templates still limit synthetic independence. Near-duplicate
connected components are kept in one split; never use frozen gold for tuning.

## R3: review every real proposal before import

Keep `data/real_pool/` HUMAN supplied and source-separated from frozen gold.
Target about 100 or more real training diagrams, 25–40 instances per class and
10 or more images per archetype. Rare classes need deliberate collection.

```powershell
.\.venv\Scripts\python.exe -m backend.tools.mechanics.prelabel YOUR_REAL_IMAGES --weights YOUR_ABSOLUTE_MECHANICS_PT --out 'D:\Physimu-Interactive Augmented simulation\.cache\proposals-new' --imgsz 640 --confidence 0.25
```

The fresh output includes images, YOLO labels, class list and unreviewed manifest.
Import it into Label Studio, Roboflow or labelImg using a YOLO detection import
workflow. Review every box and class, add missed objects and remove false boxes.
An empty proposal also requires review. This tool makes no external service call;
you choose any annotation service and approve its terms. Proposals are rejected
as training data, and frozen folders cannot be used as a prelabel pool.

Keep the reviewed export immutable. Supply a separate review JSON with kind
`mechanics-human-review`, version 1, its actual ordered `class_names` and one
record per exported image. Each record must contain:

- relative `image` and `label` paths, source image `sha256`, and the exact reviewed
  export's `reviewed_label_sha256`;
- `human_reviewed` set by a person only after actual review, `reviewer`, ISO date
  `reviewed_at`, source/reference `source`, `source_group` and `licence_note`;
- `archetype`, `style` (printed/handwritten/photo) and `split` (train/val/pool).

Do not copy the unreviewed flag or claim model boxes were reviewed automatically.
Canonical class names map identically. Other exports need an explicit YAML
mapping from **every** source class name to a canonical name or `null` to drop
it; case/meaning are not guessed. Record class-map decisions with the source.

```powershell
.\.venv\Scripts\python.exe -m backend.tools.mechanics.import_reviewed YOUR_EXPORT --review YOUR_REVIEW_JSON --out 'D:\Physimu-Interactive Augmented simulation\data\generated_mechanics\reviewed-real-new'
# Add --class-map YOUR_MAPPING_YAML when source classes differ.
.\.venv\Scripts\python.exe -m backend.tools.mechanics.eval_detector --quota 'D:\Physimu-Interactive Augmented simulation\data\generated_mechanics\reviewed-real-new' --out 'D:\Physimu-Interactive Augmented simulation\.cache\real-quotas.json'
```

Importer checks every image/label hash, finite in-image boxes, attestation,
mapping and split/source/frozen leakage. Failed leakage produces a rejected
folder without a trainable manifest. Successful records retain per-image source,
reviewer, dates, original export label hash, review-manifest hash and map. No
original file is edited, no gold is generated, and no label is auto-approved.

The leakage guard reuses the existing exact SHA-256 and conservative image
signature (dHash distance ≤6 plus binary Dice >0.92), extended with source groups,
split checks and frozen-hash integrity. It catches tested exact/resized duplicates;
it is not an exhaustive detector of every crop, rotation or redraw. Correct
human source grouping and manual source review remain necessary. An absent
frozen set is explicitly reported, never called a completed real leakage proof.

Training/evaluation commands and measured limits are in
[detector_results.md](detector_results.md). Source/licence decisions are recorded
in [dataset_sources.md](dataset_sources.md); no public training dataset is used.
