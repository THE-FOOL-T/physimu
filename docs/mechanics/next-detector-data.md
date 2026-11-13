# Next detector data: opt-in textbook appearance

The completed synthetic checkpoint missed essential objects in the three public
pipeline trials recorded in [synthetic-training.md](synthetic-training.md).
Printed letters were also proposed as bodies. These are unreviewed development
observations. They are not detector ground truth or independent real accuracy.

The new `textbook` generator profile addresses plausible input weaknesses:
more diagram coverage, larger bodies, varied filled bodies and spoked/rimmed
pulleys, curved/zigzag springs, larger pivot dots/angle arcs, stronger strokes,
separated labels inside and outside bodies, and four standalone letter text targets per
diagram. Letter placement avoids existing object regions and varies by seed.
Some scenes omit extra force/velocity arrows. Atwood masses stay separated;
spring coil count is limited by its length/stroke so the coil gaps remain visible.
None of these changes establishes improved recognition without training/testing.

Masks and YOLO boxes still describe actual drawn extents. Thin lines are never
padded to improve a size statistic. The profile is explicit; the original
generator's default output remains reproducible. The separate strong-handwriting
profile adds simulated pen distortion/ruling/photo effects. This corpus uses
the lighter baseline handwriting option to separate appearance/label changes
from severe pen distortion. Simulated handwriting
and photos do not establish performance on real handwritten/photographed diagrams.

## Reproduce the data and audit

Use a new, absolute output folder each time. The completed corpus location and
measured reports are recorded below. No generated image, scene, label, mask or
checkpoint belongs in Git.

```powershell
.\.venv\Scripts\python.exe -m backend.tools.mechanics.make_synthetic --out "$PWD\data\generated_mechanics\post-m7-textbook-20261113-v3" --count 600 --seed 73 --handwriting baseline --appearance textbook
.\.venv\Scripts\python.exe -m backend.tools.mechanics.audit_sizes data/generated_mechanics/post-m7-textbook-20261113-v3 --imgsz 512 --out "$PWD\.cache\post-m7-data\textbook-sizes.json"
.\.venv\Scripts\python.exe -m backend.tools.mechanics.leakage data/generated_mechanics/post-m7-textbook-20261113-v3 --out "$PWD\.cache\post-m7-data\leakage.json"
.\.venv\Scripts\python.exe -m backend.tools.mechanics.eval_detector --dataset data/generated_mechanics/post-m7-textbook-20261113-v3 --weights "$PWD\models\mechanics-synthetic-20261113.pt" --imgsz 512 --confidence 0.25 --out "$PWD\.cache\post-m7-data\challenge-baseline.json"
```

The size audit measures the box's shorter side after aspect-preserving inference
resize: `min(box_width, box_height) × imgsz / max(native_width, native_height)`.
Padding does not alter that size. Its p10/p50/p90 and under-4/under-8 counts
describe geometry, not recall or a proven cause of a detection failure. Manifests,
image/label hashes, bounds and class order are checked before measurement.

## Prepared fine-tune command

This command is prepared, **not executed** by this data-preparation follow-up.
It starts from the completed mechanics candidate, with a fresh immutable run
copy and two CPU threads. The existing training tool writes epoch progress,
checkpoints and a final evaluation. It remains a synthetic-only experiment and
is never eligible for production promotion.

```powershell
.\.venv\Scripts\python.exe -m backend.tools.mechanics.train --data "$PWD\data\generated_mechanics\post-m7-textbook-20261113-v3" --pretrained "$PWD\models\yolo26n.pt" --finetune "$PWD\models\mechanics-synthetic-20261113.pt" --out "$PWD\.cache\textbook-finetune-20261113-v1" --synthetic-bootstrap --epochs 30 --imgsz 512 --batch 2 --threads 2 --patience 8 --seed 73 --device cpu --execute
```

Use the same new validation split/protocol to compare the current checkpoint and
any future fine-tune. Comparing scores on the old corpus and this new corpus
does not measure a model improvement. Both corpora share authored template
families, so split isolation does not make them independent real data. Keep
the old checkpoint, inputs and evaluations unchanged. Schedule heavy verification
separately from training on this small-memory CPU host.

Real training-label review, independent frozen printed/handwritten scenes,
source/model/data licence decisions, native Bangla review and device QA remain
HUMAN tasks. Public previews were not added to training. Real metrics remain
null and the default mechanics model is unchanged.
Keep previews already inspected for development out of any future independent
frozen test set; source groups must record that prior use.

## Measured preparation result

Final corpus: **600 images, 480 train / 120 validation**, seed 73; generation completed in **372.11 s**, exit 0. All eight archetypes have 75 images. Styles are 180 printed, 180 simulated handwritten, 120 scan and 120 simulated photo. There are 300 mirrored diagrams, 150 without numeric values and 60 with Bengali digit text. All 21 classes occur at least 75 times. The corpus contains 4,200 text targets, including 2,400 standalone letter targets.

Manifest SHA-256: `5c3dc8e7449ce6c7295d717f4ea1334a0b422fcfcf291054352c051f5fdb9297`.

The exact/near-duplicate/source-group split audit passed with **zero collisions**. It found zero frozen real images, so real-frozen protection remains null. The split shares authored template families; the audit does not make this an independent real benchmark.

Median minimum target side at size 512, pixels (both complete corpora):

| Class      | Original R1 | Textbook v3 |
| ---------- | ----------: | ----------: |
| floor      |       2.280 |       4.331 |
| wall       |       2.190 |       3.733 |
| ceiling    |       1.833 |       4.028 |
| pivot      |       3.779 |       9.267 |
| angle_mark |       2.730 |       6.793 |
| text_label |       5.923 |      10.196 |
| block      |      20.682 |      38.484 |
| spring     |       9.509 |      20.153 |
| pulley     |      29.587 |      35.348 |

The unchanged experimental checkpoint was evaluated on **120 new synthetic validation images / 1,983 objects** at size 512, confidence 0.25, matching IoU 0.50, AP floor 0.001, NMS IoU 0.70, and AP IoU 0.50:0.05:0.95 with 101-point interpolation. All 21 supported classes are included in the macro means.

Macro precision **0.663588**, recall **0.678523**, AP50 **0.684247**, AP50:95 **0.474520**. These are **synthetic appearance-challenge baseline scores**, not new training results or real accuracy. The different input corpus prevents a direct improvement claim against the old R1 score.

Checkpoint SHA-256: `148ae88339fd607f6aa08456a7135f2a5e44e60260372426563161b846dfc8cd`. No training ran and no weight was installed as the default.

| Class          | Objects | Precision | Recall |   AP50 | AP50:95 |
| -------------- | ------: | --------: | -----: | -----: | ------: |
| block          |     135 |    0.8957 | 0.7630 | 0.8881 |  0.7417 |
| ball           |       7 |    0.4286 | 0.4286 | 0.4313 |  0.2669 |
| bob            |      12 |    0.6667 | 0.5000 | 0.5123 |  0.4542 |
| cart           |      34 |    0.9286 | 0.7647 | 0.9013 |  0.7851 |
| incline        |      33 |    1.0000 | 1.0000 | 1.0000 |  0.9334 |
| floor          |     121 |    0.5455 | 0.3967 | 0.3760 |  0.1267 |
| wall           |      28 |    0.0000 | 0.0000 | 0.0145 |  0.0030 |
| ceiling        |      19 |    0.6667 | 0.6316 | 0.6289 |  0.2367 |
| pivot          |      12 |    0.0000 | 0.0000 | 0.0000 |  0.0000 |
| ground_hatch   |     201 |    0.8364 | 0.8905 | 0.9290 |  0.6354 |
| pulley         |      51 |    0.8519 | 0.9020 | 0.8483 |  0.6166 |
| rope           |      51 |    0.8947 | 1.0000 | 0.9963 |  0.7742 |
| rod            |      12 |    0.6875 | 0.9167 | 0.8223 |  0.5914 |
| spring         |      15 |    0.8333 | 1.0000 | 0.9790 |  0.6344 |
| arrow_force    |      66 |    0.6835 | 0.8182 | 0.7748 |  0.3642 |
| arrow_velocity |      57 |    0.5738 | 0.6140 | 0.5886 |  0.2555 |
| angle_mark     |      52 |    0.0000 | 0.0000 | 0.0000 |  0.0000 |
| axis           |      92 |    0.9375 | 0.9783 | 0.9785 |  0.7024 |
| trajectory_arc |       7 |    1.0000 | 1.0000 | 1.0000 |  0.8760 |
| dimension_line |     120 |    0.7770 | 0.9583 | 0.9489 |  0.5137 |
| text_label     |     858 |    0.7281 | 0.6865 | 0.7510 |  0.4535 |

Wall, pivot and angle-mark recall is still zero on this challenge. Larger examples alone do not make the existing detector recognize those classes; the measured baseline preserves this failure for a future fine-tune comparison.

Per-image `model.predict` wall time: median **222.2 ms**, p95 **768.2 ms**; total prediction time **41.96 s**. It includes preprocessing/first-call warmup, excludes input auditing, OCR, geometry and HTTP. Session/resource conditions differ from earlier runs, so this is not a controlled model-speed comparison.

Opened the actual final contact sheet and full-resolution annotated printed Atwood image. Labels and bodies are separated in that inspected example. This is limited synthetic screenshot QA, not HUMAN label review, exhaustive legibility approval, real-image correctness or Bangla approval.

Development attempts remain disclosed: v1 was interrupted after 195 image files when visual QA found overlapping masses/dense coils. V2 completed 600 images in 619.34 s but was rejected for overlapping body labels; its original manifest is preserved as `manifest.rejected.json`. Only corrected v3 is the prepared training corpus. The original R1 corpus/model/report remain unchanged.

Raw reports, logs, hashes and captures are local/ignored under `.cache/post-m7-data/`. No model, dataset, real scene or reviewed label was added to Git.
