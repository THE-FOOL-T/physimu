# M4 plan — data tooling and synthetic bootstrap (2026-11-13)

Continue authorizes M4 only. No mechanics perception/API work, circuit algorithm
change, full training, real-data annotation or frozen gold creation is included.
There is no human-reviewed mechanics frozen set/real training pool yet; ask for
local paths while building tools. Real metrics remain null in its absence.

## Data contracts and human tooling

- Fix the 21-class order from A5.5 in data/mechanics_class_schema.yaml. Mechanics
  tools use their own class map; never load or initialize from circuit weights.
- Add mechanics dataset/path/provenance helpers. Outputs are explicitly absolute,
  within this workspace, new/empty, and outside frozen-evaluation roots. Reject
  symlink escapes. Images/data/models remain ignored; only schema/README metadata
  is tracked. No dependency/package changes are expected.
- Provide a blank authoring scaffold outside frozen folders, strict scene/gold
  validation, human review/source attestations and freeze-hash manifest tooling.
  Tools never write, edit or auto-generate frozen gold scenes. Human-authored
  scenes and source-separated 20 printed/20 handwritten diagrams remain HUMAN.
- Reuse the existing leakage signatures/near-duplicate ideas behind the core
  facade without editing circuit tools. Mechanics audit covers exact/near image
  duplicates, source groups across train/validation/frozen, and frozen integrity.
  Report absent frozen data explicitly rather than claiming a real leakage proof.

## Synthetic generation

- Extend the M2 painter in mechanics-only modules; keep original fixture pixels
  and painter defaults unchanged. Default 600 images, 400–800 for production R1,
  with an explicit small-test mode. Eight archetypes balanced, styles exactly
  30/20/30/20 printed/scan/handwritten/photo (rounded for arbitrary counts).
- Seeded native geometry/layout variation: canvas 600–1400, scale 0.5–1.6,
  translation/margins, 50% mirror; strokes/ink/fonts/arrowheads/text/hatching;
  25% without numeric values and 10% Bengali digits. Scan rotation/noise/JPEG,
  hand-jitter/wobble/width/blur and photo perspective/lighting/shadow. Transform
  boxes, polygons, anchors and repairs together, including perspective/rotation.
- Export images, YOLO boxes, scene JSON, per-object masks and exact synthetic
  provenance. Include a deterministic source-group split, class/archetype/style
  counts, assert >=40 objects per class, SOURCE.md and a contact sheet. Inspect
  the actual sheet and fix clipping/overlap issues. Synthetic graphs never count
  as gold or as measured real physics/recognition correctness.

## Training, evaluation and review loop

- Separate mechanics config with MECHANICS_MODEL and no runtime model download.
  M4 explicitly requires a new config entry while the M0 guard currently hashes
  the whole example config. Preserve its original byte prefix and extend the
  guard narrowly for the appended mechanics section. Shared config/ignore/facade
  changes are committed separately after manage.py test. Original config loader,
  circuit detector/tools/tests, model pins and API remain unchanged.
- Paired fine-tune/control wrapper: local general pretrained checkpoint for R1,
  optional prior mechanics checkpoint for later fine-tuning; absolute contained
  output, plan unless --execute, explicit --smoke/--device. Refuse circuit weights,
  missing weights/downloads, unreviewed real labels and leaked splits. Smoke is
  one epoch on a small generated subset and can never be promoted. CPU only here.
- Per-class precision/recall/AP50/AP50:95 at explicit common image size/confidence,
  with defined IoU matching, null missing-class metrics and measured inference
  time. Quota reports for real classes (25–40 instances) and archetypes (10 images).
  Record synthetic/real origin from validated provenance, never infer real from
  an arbitrary folder name. Evaluation works identically across model candidates.
- Prelabel local images to fresh, unreviewed YOLO proposals. Import only exports
  accompanied by explicit per-image human review and provenance, class-map
  checks, source hashes and frozen/source-group leakage audit. No auto-review.
- Preserve promotion rules in a mechanics-specific comparison tool: same protocol,
  independent frozen real classes, improvements without >2-point common-class
  regressions; smoke/synthetic cannot qualify. No real promotion is run in M4.

## Verification and report

New Python tests under backend/tests/mechanics cover seeded generator output,
box/mask/pixel transforms, mix/minimums, paths/config, gold validation/freeze hashes,
leakage/source splits, exact tiny-fixture evaluator/AP/quota results, training
plans and proposal/review imports. No original test assertion is weakened.
Run the actual 600-image generator, inspect its contact sheet, run paired local
CPU smoke training and actual synthetic validation at a recorded protocol, and
exercise prelabeling. Measure durations, weights/hashes and counts. No GPU time
or full-training result is invented. Real metrics remain null with HUMAN notes.

Run manage.py test before shared commits and at completion, manage.py check,
existing browser gates as appropriate, and verify unchanged circuit snapshots.
Write labeling.md, detector_results.md with exact local/Colab/Kaggle commands,
dataset_sources.md reporting stated rights without approval, and append actual
gates/limits/assumptions/HUMAN tasks/shared diffs to status.md. Small commits.
Stop before M5; final reply has changed / gates-evidence / open questions only.
