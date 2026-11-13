# Synthetic detector bootstrap (2026-11-13)

The owner requested multi-epoch detector training on the existing 600 annotated
synthetic images before continuing M6. This explicitly authorizes a local CPU
experiment beyond M4's one-epoch subset smoke. M6 has not started. No independently
reviewed real frozen set exists, so this experiment cannot establish real-image
accuracy or qualify a model for production promotion.

## Dataset and experiment

Use the final M4 dataset, `data/generated_mechanics/m4-r1-20261113-v4/`, rather
than the earlier v1 trial visible in the editor. It contains 600 programmatically
annotated diagrams across eight archetypes and 21 ordered classes. The existing
source-group split is preserved: 480 train, 120 validation. No validation image
is used for gradient updates. Shared generator primitives limit independence;
validation scores describe this synthetic distribution only.

Manifest SHA-256:
`65107a668df0f07330a654b9de0f11cfd033c9292a7a82b6fc882550dcdc0d46`.
Initial local general checkpoint: `models/yolo26n.pt`, SHA-256
`9b09cc8bf347f0fc8a5f7657480587f25db09b34bf33b0652110fb03a8ad4fef`.
Circuit weights are never used for mechanics training.

The new `--synthetic-bootstrap` mode requires a synthetic manifest and an explicit
synthetic flag on every image. It permits multi-epoch training without real gold,
trains one candidate, copies the full split into the run, and records
`promotion_eligible: false`. The ordinary training mode still requires at least
20 printed and 20 handwritten frozen HUMAN scenes. Smoke remains a separate,
one-epoch subset mode. Human review and promotion checks are unchanged.

Hardware is an AMD Ryzen 5 PRO 5675U, six cores/twelve logical processors,
7.31 GiB physical RAM, Windows, Torch 2.13.0+cpu and Ultralytics 8.4.193.
CUDA is unavailable. The run uses at most 50 epochs, image size 512, batch two,
four Torch training threads, seed 42, AdamW with initial learning rate 0.001,
zero bias-learning-rate warmup, and patience 12. Generated styles already include
mirroring, distortion and lighting; extra SDK geometric/colour augmentation is
disabled to retain readable text and the generator's supervision.

The local pinned SDK and its [training documentation](https://docs.ultralytics.com/modes/train/)
support these explicit training arguments. No package pin changes, model
downloads, cloud uploads or paid compute are part of this run.

## Reproduction

From the repository root in PowerShell, choose a **new** output directory:

```powershell
$env:PYTHONUTF8 = '1'
$env:AUGPHYS_OFFLINE = '1'
$env:YOLO_OFFLINE = 'true'
$env:PYTHONPATH = "$PWD\tools\offline;$PWD"
$env:AUGPHYS_OFFLINE_LOG = "$PWD\.cache\synthetic-training-20261113-v1\network.jsonl"
.\.venv\Scripts\python.exe -u -m backend.tools.mechanics.train --data "$PWD\data\generated_mechanics\m4-r1-20261113-v4" --pretrained "$PWD\models\yolo26n.pt" --out "$PWD\.cache\synthetic-training-20261113-v1\run" --synthetic-bootstrap --epochs 50 --imgsz 512 --batch 2 --threads 4 --patience 12 --device cpu --execute
```

Omit `--execute` to validate the input hashes, labels, split audit and plan without
training. Output paths must be absolute and contained in this checkout; source
data is immutable and SDK caches are written only in the run's copy.

The actual invocation runs through the ignored local `runner.py` in the same
cache folder. It preserves stdout/stderr, a status/exit-code record and the child
PID. `run/progress.json` records each completed epoch; `run/fine_tune/results.csv`
contains the SDK curve. Best/last checkpoints and the independent common-protocol
synthetic evaluation are saved in the run. None are committed to Git.

## Measured result

Training is in progress. The first epoch completed, saved best/last checkpoints
and recorded preliminary SDK synthetic mAP50 **0.21687** and mAP50:95 **0.13553**.
These are first-epoch SDK scores, not the final fixed-confidence evaluation.
The live `.cache/synthetic-training-20261113-v1/report.md` is updated while the
background finalizer runs and is replaced with final measured results after
training/evaluation finish. `status.json` and `finalizer-status.json` distinguish
running, failed and completed processes. Keep the computer running for the job.

Final completed-epoch count, duration, per-class validation scores and checkpoint
hash will be recorded after the process actually finishes.
Printed and handwritten **real** precision, recall and AP remain null because
independently reviewed frozen images/labels are absent. Synthetic handwritten
style is simulated handwriting, not a real handwritten benchmark.

This experiment does not change the application's default mechanics checkpoint.
The candidate must be identified as experimental in any later manual trial.

## Verification at launch

The complete mechanics data-tool suite passed **24 tests** in **9.13 s**.
`python manage.py test` passed **552 Python tests, one skipped** in **128.30 s**,
then **116 TypeScript tests**, the type check and build (**4.46 s**). The added
test covers complete split preservation, explicit synthetic provenance, refusal
of real/mixed data, and retention of the normal frozen-gold gate. Ruff lint and
format checks passed. Raw output is in the run's `focused-tests.log` and
`regression-now.log`; the latter's recorded exit code is zero. Process-level
Python guards recorded no external connection attempts during these commands
or training so far. Training is still in progress; these gates do not claim a
completed detector run or a final accuracy result.
