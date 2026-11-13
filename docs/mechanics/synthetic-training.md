# Synthetic detector bootstrap (2026-11-13)

The owner requested multi-epoch detector training on the existing 600 annotated
synthetic images before continuing M6. This explicitly authorizes a local CPU
experiment beyond M4's one-epoch subset smoke. M6 proceeded separately while
this run kept its original M4 dataset. No independently
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

## Measured result ? completed

Training completed **50/50 epochs**, finishing at **21:03:56 Bangladesh time**
on 2026-11-13. Final independent evaluation and code checks completed at
**21:07:52**. The wrapper recorded **17,859.17 s** (4 h 57 min 39 s), including
input work, interruptions/recovery gaps and final evaluation. This is not an
uninterrupted training duration or a GPU measurement. Initial training used four
Torch threads; recovery used two. The two memory failures below remain part of
the record. No fresh run or changed training split was substituted.

The experimental candidate is `models/mechanics-synthetic-20261113.pt`, SHA-256
`148ae88339fd607f6aa08456a7135f2a5e44e60260372426563161b846dfc8cd`.
It remains ignored and separate from the unchanged default mechanics path and
circuit checkpoint. The [measured result JSON](synthetic-training-result.json)
contains aggregate/per-class metrics, protocol, timing scope and provenance.

These are **synthetic validation results, not real accuracy**. Protocol:
512 pixels, confidence 0.25, matching IoU 0.50, NMS IoU 0.70; AP uses confidence
floor 0.001, IoU 0.50:0.05:0.95 and 101-point interpolation. The first epoch SDK
scores were AP50 0.21687/AP50:95 0.13553; those historical values are not the
final independent evaluator. The 120 validation images were withheld from
gradient updates but use the same generator family. There was no independent
real held-out evaluation.

| Synthetic style | Images | Micro precision | Micro recall | Macro AP50 | Macro AP50:95 |
| --- | ---: | ---: | ---: | ---: | ---: |
| all | 120 | 0.8685 | 0.7681 | 0.7583 | 0.5899 |
| printed | 40 | 0.8964 | 0.7654 | 0.7527 | 0.6081 |
| handwritten | 42 | 0.8684 | 0.7730 | 0.7646 | 0.5897 |
| scan | 14 | 0.8177 | 0.7629 | 0.7727 | 0.5808 |
| photo | 24 | 0.8576 | 0.7671 | 0.7714 | 0.5941 |

| Class | Support | Precision | Recall | AP50 | AP50:95 |
| --- | ---: | ---: | ---: | ---: | ---: |
| block | 126 | 1.0000 | 0.9921 | 0.9995 | 0.8480 |
| ball | 13 | 0.9231 | 0.9231 | 0.9208 | 0.6198 |
| bob | 16 | 1.0000 | 0.9375 | 1.0000 | 0.9138 |
| cart | 24 | 1.0000 | 1.0000 | 1.0000 | 0.8359 |
| incline | 30 | 1.0000 | 1.0000 | 1.0000 | 0.9875 |
| floor | 108 | 0.5556 | 0.1389 | 0.1852 | 0.0519 |
| wall | 23 | 0.0000 | 0.0000 | 0.0124 | 0.0022 |
| ceiling | 29 | 0.6667 | 0.3448 | 0.3171 | 0.1303 |
| pivot | 16 | 0.0000 | 0.0000 | 0.0000 | 0.0000 |
| ground_hatch | 190 | 0.8100 | 0.9421 | 0.9482 | 0.6412 |
| pulley | 47 | 1.0000 | 1.0000 | 1.0000 | 0.9409 |
| rope | 47 | 1.0000 | 1.0000 | 1.0000 | 0.9430 |
| rod | 16 | 1.0000 | 1.0000 | 1.0000 | 0.9611 |
| spring | 19 | 0.9048 | 1.0000 | 0.9917 | 0.6323 |
| arrow_force | 120 | 0.8968 | 0.9417 | 0.9723 | 0.6642 |
| arrow_velocity | 133 | 0.8421 | 0.8421 | 0.9064 | 0.5789 |
| angle_mark | 59 | 0.0000 | 0.0000 | 0.0000 | 0.0000 |
| axis | 79 | 0.9405 | 1.0000 | 0.9964 | 0.7598 |
| trajectory_arc | 13 | 1.0000 | 1.0000 | 1.0000 | 0.9433 |
| dimension_line | 120 | 0.8054 | 1.0000 | 0.9700 | 0.5307 |
| text_label | 363 | 0.8255 | 0.6777 | 0.7043 | 0.4042 |

Weak classes remain explicit: wall, pivot and angle_mark have zero recall at
confidence 0.25 on this synthetic split; floor recall is 0.1389 and ceiling
0.3448. Synthetic text-label recall is 0.6777. The overall score does not establish
reliable scene extraction or physical correctness.

The finalizer generated 15 unreviewed qualitative overlays (eight synthetic and
seven public-source previews, including previously quarantined/manual-QA images
used only as previews). No preview entered training or frozen gold. Inspection
of the public Atwood and spring examples shows missing pulley/rope/body boxes
and a missing spring, with a coil region labelled as velocity. These are visual
observations, not reviewed labels or numeric real-image accuracy. They support
keeping the candidate experimental rather than installing it as the default.

A subsequent child-process trial used the actual mechanics pipeline, local
hybrid OCR, application-default size **640** and confidence **0.25**, with only
its mechanics weight path overridden to the experimental candidate. Consent
was off, zero crops were sent and no external connection attempt was recorded.
All three scenes/envelopes validated and retained source images and editable
objects, with no circuit netlist, solution or demo. All three results were
**unsupported**. This is a failed usability trial on unreviewed public previews,
not a frozen accuracy score. No app default or threshold was changed.

| Public preview | Detections | Result | Whole-call seconds |
| --- | ---: | --- | ---: |
| atwood | 5 | unsupported | 30.91 |
| spring_mass | 8 | unsupported | 14.77 |
| incline_block | 10 | unsupported | 28.81 |

Atwood/spring lacked a supported object/attachment combination. The incline
failed a required physical/attachment constraint, including unmodelled-force
warnings. Whole-call time includes model/OCR setup, budgets and geometry; it is
not a warmed HTTP benchmark or the detector-only timing below. Raw responses
and summaries are ignored under `.cache/m7/experimental-runtime/`.

Independent per-image predict time on the 120 synthetic images: median
**82.13 ms**, p95 **144.14 ms**. Scope includes preprocessing and first-call
warmup, excludes audit/file work, OCR, geometry, simulation and HTTP. It is not
an end-to-end latency claim.

Finalizer checks: Ruff lint/format passed; `manage.py test` passed **598 Python,
one skipped, in 117.46 s**, **117 TypeScript**, type check and build (**1.94 s**).
These used the uncommitted M7 refactor tree and the source checkout present.
The separate M7 source-absent gates are recorded in status.md. Raw logs, weights,
per-style/per-class evaluation, checkpoint and proposal provenance remain in
`.cache/synthetic-training-20261113-v1/`.

Printed/handwritten real metrics and real end-to-end correctness remain **null**.
HUMAN tasks: independent reviewed real scenes/labels, source/model/data licence
decisions, Bangla review and physical-device QA. No model promotion occurred.

## Verification at launch

The complete mechanics data-tool suite passed **24 tests** in **9.13 s**.
`python manage.py test` passed **552 Python tests, one skipped** in **128.30 s**,
then **116 TypeScript tests**, the type check and build (**4.46 s**). The added
test covers complete split preservation, explicit synthetic provenance, refusal
of real/mixed data, and retention of the normal frozen-gold gate. Ruff lint and
format checks passed. Raw output is in the run's `focused-tests.log` and
`regression-now.log`; the latter's recorded exit code is zero. Process-level
Python guards recorded no external connection attempts during these commands
or training so far. At launch, training was still in progress; those gates did not claim a
completed detector run or a final accuracy result.

## Memory interruption and recovery during M6

While M6 checks ran alongside training, the host exhausted memory. The initial
training process failed during epoch 5 at 16:33:19 Bangladesh time; the last
complete checkpoint was epoch 4. The original segment's status and error are
preserved in `failed-segment-1-status.json` and `stderr.log`. This was an actual
failed segment, not uninterrupted training or a completed 50-epoch result.

At 16:43:59 the local `resume.py` helper resumed that checkpoint using the pinned
SDK's `model.train(resume=True, device="cpu", workers=0, batch=2)`. Source and
copied image/label hashes and split identities were revalidated. The checkpoint
retained optimizer state and zero-based epoch 3, so training continued at epoch 5
in its original output folder. Checkpoint hash at recovery:
`ee5fb41ecc6bd7ec0c6102d181b92ab7df9053174236de5e898a66e16c3d46be`.
The verification is recorded in `resume-record.json`. Two training threads are
used after recovery. Best/last checkpoints, curve, stdout and the live report
continue in the original run folder. The finalizer was restarted and now reports
failures explicitly rather than leaving a stale running message.

The TypeScript runner now uses one test-file process at a time, with all existing
assertions/tests retained. Remaining heavy gates run sequentially. The workspace
app server was temporarily stopped to leave memory for training and verification.
No further training run, cloud compute or model download was started. The
recovered run subsequently saved epoch 5; final metrics remain pending.

The later browser workload also exhausted host memory. That recovery segment
failed during epoch 7 at 16:57:38, after epochs 5 and 6 were saved. Browser
verification was then completed separately. The final recovery resumes the
latest intact epoch-6 checkpoint at **17:07:49** with optimizer/data verification and two threads;
`resume-record-2.json` identifies its actual checkpoint hash. Earlier failure
statuses and both tracebacks remain preserved. No further heavy model/browser
checks run alongside training.

During recovery, the normal app server stayed paused to reserve memory. The local
`.cache/m6/restore_app.py` watcher starts it with its normal configuration after
training/final evaluation/checks finish (or restores it after a failed job).
Its state is `.cache/m6/app-restore-status.json`. The training report and
`finalizer-status.json` remain the source of current job state; a running epoch
does not imply completed training or real accuracy.

After training/finalization and the queued M7 browser checks finished, the owned
watcher restored the normal app. Health reported circuit detector/OCR ready with
hybrid OCR. The experimental mechanics candidate is not the default.
