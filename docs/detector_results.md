# Frozen detector test comparison

99 reviewed images; confidence 0.25, matching IoU 0.5; AP uses IoU .50:.05:.95 and 101-point interpolation. Baseline inference size 640; smoke candidates use the same 640 protocol. Full fine-tuning is not completed: no CUDA GPU is available. These are 1-epoch plumbing runs on four training/two validation images, never a release candidate.

|Model|Class|Precision|Recall|AP50|AP50–95|
|---|---|---:|---:|---:|---:|
|v2|resistor|0.9879|0.8809|0.9345|0.7617|
|v2|voltage_source|0.8583|0.7464|0.8013|0.5704|
|v2|capacitor|0.0000|0.0000|0.0407|0.0204|
|v2|switch|0.3333|0.2000|0.2208|0.1231|
|v2|ammeter|0.0000|0.0000|0.0000|0.0000|
|v2|voltmeter|0.0000|0.0000|0.0000|0.0000|
|fine_tune_smoke|resistor|0.9138|0.9323|0.9492|0.7504|
|fine_tune_smoke|voltage_source|0.8837|0.8261|0.8168|0.5902|
|fine_tune_smoke|capacitor|0.0000|0.0000|0.0160|0.0080|
|fine_tune_smoke|switch|0.1290|0.2000|0.2026|0.1059|
|fine_tune_smoke|ammeter|0.0000|0.0000|0.0006|0.0005|
|fine_tune_smoke|voltmeter|0.0000|0.0000|0.0000|0.0000|
|control_smoke|resistor|0.0000|0.0000|0.0001|0.0000|
|control_smoke|voltage_source|0.0000|0.0000|0.0040|0.0017|
|control_smoke|capacitor|0.0000|0.0000|0.0000|0.0000|
|control_smoke|switch|0.0000|0.0000|0.0005|0.0002|
|control_smoke|ammeter|0.0000|0.0000|0.0000|0.0000|
|control_smoke|voltmeter|0.0000|0.0000|0.0000|0.0000|

Eligible for promotion: **False**. Keep v2 selected. Full-model metrics and independent end-to-end accuracy remain **null**. Raw confusion matrices: `reference_99_metrics.json`, `detector_smoke_finetune.json`, `detector_smoke_control.json`; corresponding PNGs show their matrices.

## Reproduce full preparation/training

1. Install dependencies; place v2 and the standard pretrained control in models. See dataset_sources.md for license/export restrictions.
2. Import original owner training material and licensed public exports; review maps, completeness and all pseudo-labels. Record per-image real/synthetic provenance in kinds.json.
3. `python -m backend.tools.merge_dataset data/raw/owner-training data/raw/aitee/remapped data/generated_round2_oriented --original-training /path/to/original/images/train --out data/merged/reviewed --eval /path/to/frozen99/images --quarantine-frozen`
4. After actual human completeness review, record it in manifest.json.
5. GPU command: `python -m backend.tools.train --data data/merged/reviewed/data.yaml --control models/yolo26n.pt --device 0 --epochs 50 --imgsz 960 --seed 42 --execute`. Add `--resume /absolute/path/to/last.pt` to resume one run.
6. Evaluate both checkpoints with eval_detector at the same input size, frozen images/labels/names, then compare the rare-class improvement and two-point resistor/source rule. Do not select on training fit.

GPU duration: **null**, unmeasured on this host. Estimate it on the owner GPU with `--smoke --execute` first; scale measured epoch time by training batches × epochs, allowing validation overhead. No multi-hour CPU training was run.


Round three host check: Windows, CUDA unavailable, zero CUDA devices. No paired
training was run and no CPU training was substituted. Selected v2_original.pt
SHA-256 remains 95bc8a1f76aaed83ad907e87bdee0255da1837fdb8f9c8405a723779e8ed0c46.
The GPU commands and frozen-99 promotion gate above remain the owner procedure;
no new detector accuracy or GPU duration is claimed.
