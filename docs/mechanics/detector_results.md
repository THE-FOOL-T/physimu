# M4 detector tooling and measured CPU smoke (2026-11-13)

M4 supplies data/training tools and a completed CPU smoke run. It does not supply
a useful mechanics detector. Both one-epoch candidates scored zero on every
supported synthetic class. Neither candidate was installed at `models/mechanics.pt`.
Real printed/handwritten detector and end-to-end metrics remain **null** because
no independently HUMAN-reviewed frozen set exists. Mechanics analysis is still
the M1 unsupported backend; perception/API integration is M5 work.

## Actual dataset

The final fresh output is ignored `data/generated_mechanics/m4-r1-20261113-v4/`.
It contains 600 images, labels, auxiliary scenes, visible indexed masks,
object-to-mask/amodal-box mappings, manifests, split lists, source notice and an
actual inspected `contact-sheet.jpg`. Manifest SHA-256:
`65107a668df0f07330a654b9de0f11cfd033c9292a7a82b6fc882550dcdc0d46`.

Seed 42 generated 75 images for each of projectile, incline_block, pendulum,
spring_mass, atwood, table_pulley, incline_pulley and collision_1d. Style counts:
180 printed, 120 scan, 180 simulated handwritten, 120 simulated photo. Split:
480 train / 120 validation. Mirrored: 300; without numeric values: 150;
Bengali-digit variants: 60. Every class has at least 75 instances, above the
40-instance requirement. Generation, duplicate grouping and contact sheet took
**220.98 seconds** wall time on this machine (the earlier v3 run took 230.05 s).

The contact sheet was opened and inspected. Earlier fresh trial datasets exposed
backwards mirrored glyphs and coarse text/body supervision. The final painter
keeps reflected text readable and uses the actual transformed object masks for
boxes; spring supports no longer masquerade as pendulum pivots. Body resizing
keeps surface contact and attachment points. Final inspection found no clipped
objects in the sheet. This is screenshot QA of synthetic material, not human
annotation approval or recognition correctness. Auxiliary projective/mirrored
scene geometry is not a calibrated solver benchmark; see [labeling.md](labeling.md).

The final v4 run also corrects visible ownership inside pulley disks, where the
white fill erases rope pixels. Its 225 pulley-containing masks differ from v3;
all 600 images, all labels, scenes, object maps and manifest bytes are identical.
That comparison is recorded in `.cache/m4-final/v4-input-comparison.json`. The
actual smoke command below used v3's identical image/label training inputs;
the mask-only correction does not change the measured detector experiment.
Use v4 for future geometry/mask work. The final v4 contact sheet was opened too.

The exact/near-duplicate and source-group audit passed with zero cross-split
collisions. Frozen real count is zero, so `real_frozen_protection` is null; this
does not establish separation from an absent real set. Shared primitives still
limit the independence of synthetic train and validation examples.

## Actual paired smoke

Environment: Windows, Python 3.12.10, Torch 2.13.0+cpu, Torchvision 0.28.0,
Ultralytics 8.4.193, two Torch inference threads. `torch.cuda.is_available()` is
false. No dependency pin changed, no GPU run or full training occurred, and no
checkpoint was downloaded. The existing local general 80-class `yolo26n.pt` was
copied to ignored `models/`; its SHA-256 is
`9b09cc8bf347f0fc8a5f7657480587f25db09b34bf33b0652110fb03a8ad4fef`.
Checkpoint/source/licence limits are recorded in [dataset_sources.md](dataset_sources.md).

Executed from the workspace root (the fresh output now exists; use a new path to
repeat). Process-level Python network guards and `YOLO_OFFLINE=true` were active:

```powershell
$env:PYTHONUTF8 = '1'
$env:AUGPHYS_OFFLINE = '1'
$env:YOLO_OFFLINE = 'true'
$env:PYTHONPATH = "$PWD\tools\offline;$PWD"
$env:AUGPHYS_OFFLINE_LOG = "$PWD\.cache\m4-final\network-smoke.jsonl"
.\.venv\Scripts\python.exe -m backend.tools.mechanics.train --data "$PWD\data\generated_mechanics\m4-r1-20261113-v3" --pretrained "$PWD\models\yolo26n.pt" --out "$PWD\.cache\m4-cpu-smoke-v1" --smoke --execute --device cpu --imgsz 192 --seed 42
```

Each arm trained **one epoch on 16 images**, two per archetype, and validated on
**eight images**, one per archetype, with 108 labeled objects across all 21
classes. Both R1 arms start from the same general checkpoint, so this is a
plumbing check, not evidence that fine-tuning beats a control. A later round can
pass `--finetune` with its prior mechanics checkpoint; the control still starts
from the general checkpoint. Source datasets are copied into the run before the
SDK writes caches; input images/labels/manifests stay unchanged.

| Arm | Training wall seconds | Validation inference total / median / p95 seconds |
| --- | ---: | --- |
| fine_tune | 21.14 | 0.6061 / 0.0579 / 0.1723 |
| pretrained_control | 6.63 | 0.6101 / 0.0568 / 0.1765 |

The complete paired CLI took **45.72 seconds**, including audits, copies, both
runs and evaluation. Training timings include model construction/SDK work.
Inference is wall time around `model.predict` per image, including preprocessing
and first-call warmup, excluding input integrity/label audit. The first arm also
pays initialization costs; timings do not compare model speed fairly. This is
eight-image synthetic model inference, not HTTP latency or end-to-end mechanics.

Common protocol: `imgsz=192`, precision/recall confidence **0.25**, matching
IoU **0.50**, AP confidence floor **0.001**, NMS IoU **0.70**, max detections **300**.
AP uses 101-point interpolation and IoU 0.50 through 0.95 in 0.05 steps.
One prediction can match one ground-truth object of its class. An absent ground
truth class has null recall/AP rather than invented success. Every class is
present in this smoke validation. **Synthetic, not real accuracy**: all four
metric columns below are the actual identical results for **each** arm.

| Class | Generated instances | Smoke val support | Precision | Recall | AP50 | AP50:95 |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| block | 600 | 8 | 0 | 0 | 0 | 0 |
| ball | 75 | 1 | 0 | 0 | 0 | 0 |
| bob | 75 | 1 | 0 | 0 | 0 | 0 |
| cart | 150 | 2 | 0 | 0 | 0 | 0 |
| incline | 150 | 2 | 0 | 0 | 0 | 0 |
| floor | 595 | 7 | 0 | 0 | 0 | 0 |
| wall | 145 | 1 | 0 | 0 | 0 | 0 |
| ceiling | 116 | 2 | 0 | 0 | 0 | 0 |
| pivot | 75 | 1 | 0 | 0 | 0 | 0 |
| ground_hatch | 1006 | 12 | 0 | 0 | 0 | 0 |
| pulley | 225 | 3 | 0 | 0 | 0 | 0 |
| rope | 225 | 3 | 0 | 0 | 0 | 0 |
| rod | 75 | 1 | 0 | 0 | 0 | 0 |
| spring | 75 | 1 | 0 | 0 | 0 | 0 |
| arrow_force | 600 | 8 | 0 | 0 | 0 | 0 |
| arrow_velocity | 675 | 9 | 0 | 0 | 0 | 0 |
| angle_mark | 300 | 4 | 0 | 0 | 0 | 0 |
| axis | 456 | 7 | 0 | 0 | 0 | 0 |
| trajectory_arc | 75 | 1 | 0 | 0 | 0 | 0 |
| dimension_line | 600 | 8 | 0 | 0 | 0 | 0 |
| text_label | 1800 | 26 | 0 | 0 | 0 | 0 |

Raw measured results: `.cache/m4-cpu-smoke-v1/summary.json`; each arm contains
`results.csv`, `evaluation.json`, `MODEL_CARD.md` and `weights/{best,last}.pt`.
Fine-tune best SHA-256:
`2031847adf85e114f3904fabef93d7afe8009805d26bf9bfe914602f6e9ee112`;
control best SHA-256:
`4e3dc4e20a7fbb79426431f45578b217766a3dc15ebe5c8508266cc8fb0f7425`.
Smoke artifacts are ignored; their reports are marked ineligible and the
comparison tool rejects reports marked as smoke.

Actual prelabel CLI on the M3 public pendulum image produced one **unreviewed**
YOLO proposal with an empty label at confidence 0.25/imgsz 192. It remains at
`.cache/m4-prelabels-v1/`; no review or real import was invented. An actual
null-scene scaffold was written outside gold at `.cache/m4-human-scaffold-v1/`.
The empty frozen inventory, null style reports and zero real quotas were also
executed and recorded under `.cache/m4-final/`. Python guard logs for smoke and
proposals contain zero external connection attempts. This is process guarding,
not a host-level or browser-kernel firewall claim.

## Real-data status and evaluation commands

Printed: zero frozen images. Handwritten: zero frozen images. For **every one of
the 21 classes**, precision, recall, AP50 and AP50:95 are null in both partitions.
Real archetype_correct, attachment_correct, parameter_correct,
trajectory_correct, simulation_produced and seconds are also null; M4 has no
perception pipeline to measure. Producing a simulation never establishes
correctness. Full-training duration, GPU duration and real model/HTTP latency are
null. HUMAN must provide independently reviewed scenes and optional detector
labels, source separation and source/licence decisions before real evaluation.

Real training pool: zero images and zero instances for every class. Each class
has a minimum deficit of 25 (preferred target 40); each of the eight archetypes
has an image deficit of 10. Synthetic instances do not satisfy those quotas.

Run matching protocols on two later candidates; keep printed and handwritten
reports separate. Outputs below must be new files in an existing ignored folder:

```powershell
.\.venv\Scripts\python.exe -m backend.tools.mechanics.eval_detector --frozen data/eval/mechanics --weights "$PWD\models\mechanics-candidate.pt" --style printed --imgsz 960 --confidence 0.25 --out "$PWD\.cache\printed-candidate.json"
.\.venv\Scripts\python.exe -m backend.tools.mechanics.eval_detector --frozen data/eval/mechanics --weights "$PWD\models\mechanics-candidate.pt" --style handwritten --imgsz 960 --confidence 0.25 --out "$PWD\.cache\handwritten-candidate.json"
.\.venv\Scripts\python.exe -m backend.tools.mechanics.compare_detectors BASELINE_PRINTED_JSON CANDIDATE_PRINTED_JSON --targets spring rope --out "$PWD\.cache\printed-comparison.json"
# Repeat comparison for the handwritten partition before any promotion.
```

Promotion requires independently frozen real data with at least 20 images per
partition, identical images/class supports/protocol, recall improvements on
predeclared target classes and no common class (at least 25 baseline instances)
regressing more than 0.02. Both partitions must pass separately. The tool refuses
smoke and synthetic results. No actual promotion was attempted or passed.

## GPU commands for the owner (documented, not executed)

Dataset layout in an uploaded checkout is:

```text
data/generated_mechanics/<run>/
  manifest.json, data.yaml, train.txt, val.txt, counts.json, SOURCE.md
  images/, labels/, scenes/, masks/, objects/, contact-sheet.jpg
data/eval/mechanics/{printed,handwritten}/  HUMAN scenes/images/optional labels
data/eval/mechanics/frozen.json           HUMAN-created hash freeze metadata
models/yolo26n.pt                        locally supplied general checkpoint
.cache/<new-training-run>/               copied dataset and both candidate arms
```

Upload this checkout, the local checkpoint, and independently reviewed frozen
data to the runtime. A manifest uses relative image paths; the wrapper recreates
`data.yaml` with the runtime's absolute dataset path. Do not upload a private
dataset to a service until you have decided its terms. Choose a GPU runtime and
verify CUDA; these commands have **not** been tested on Linux/Colab/Kaggle here.
The training wrapper refuses full training without 20 frozen images per style.

Colab cell, assuming your uploaded checkout is `/content/physimu`:

```bash
%%bash
set -eu
cd /content/physimu
python --version
python -m pip install -r requirements.txt
python -m pip install -e . --no-deps --no-build-isolation
python -c "import torch; assert torch.cuda.is_available(), 'Select/install a compatible CUDA runtime first'"
python -m backend.tools.mechanics.gold
python -m backend.tools.mechanics.make_synthetic --out /content/physimu/data/generated_mechanics/r1-gpu-new --count 600 --seed 42
YOLO_OFFLINE=true python -m backend.tools.mechanics.train --data /content/physimu/data/generated_mechanics/r1-gpu-new --pretrained /content/physimu/models/yolo26n.pt --out /content/physimu/.cache/m4-gpu-new --epochs 50 --imgsz 960 --seed 42 --device 0 --execute
```

Kaggle cell, assuming the uploaded checkout/data have been copied to the writable
directory `/kaggle/working/physimu`:

```bash
%%bash
set -eu
cd /kaggle/working/physimu
python --version
python -m pip install -r requirements.txt
python -m pip install -e . --no-deps --no-build-isolation
python -c "import torch; assert torch.cuda.is_available(), 'Select/install a compatible CUDA runtime first'"
python -m backend.tools.mechanics.gold
python -m backend.tools.mechanics.make_synthetic --out /kaggle/working/physimu/data/generated_mechanics/r1-gpu-new --count 600 --seed 42
YOLO_OFFLINE=true python -m backend.tools.mechanics.train --data /kaggle/working/physimu/data/generated_mechanics/r1-gpu-new --pretrained /kaggle/working/physimu/models/yolo26n.pt --out /kaggle/working/physimu/.cache/m4-gpu-new --epochs 50 --imgsz 960 --seed 42 --device 0 --execute
```

Use Python 3.12 and the pinned requirements. Installing dependencies is a setup
step; checkpoints are supplied locally, never fetched by this wrapper. If the
runtime fails the CUDA assertion, fix that runtime before training; this host
does not establish a CUDA wheel/driver combination. The vendor documents
[Colab](https://docs.ultralytics.com/integrations/google-colab/),
[Kaggle](https://docs.ultralytics.com/integrations/kaggle/) and
[training arguments](https://docs.ultralytics.com/modes/train/).

After actual training, download both arm folders with model cards, input hashes,
results, and `weights/best.pt`. Evaluate against the frozen real sets at one
unchanged protocol. Preserve candidates locally under ignored `models/`;
only after the owner's real evaluation and promotion decision copy the selected
candidate to `models/mechanics.pt`, or set `MECHANICS_MODEL` to its local path.
Do not copy the M4 smoke model there. No model is committed to Git. HUMAN tasks:
freeze real gold, annotate the real pool, decide model/data licences, run GPU
training and review real results. M5 is not started by these instructions.
