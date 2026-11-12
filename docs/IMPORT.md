# Circuit source import — M0

Imported on 2026-11-12 (Asia/Dhaka) into the Physimu workspace.

## Origin and baseline

- Origin: https://github.com/THE-FOOL-T/circuit-sim
- Read-only local source: `D:/Circuit Simu/circuit_sim`.
- Branch: `main`; clean working tree before copying.
- Exact commit: `97702f2bbfd42f15f434b0acffdc1fc4bc678400`.
- Subject: `Bundle working inference models and portable hybrid setup`.
- Compared with the brief's `516e232`: one newer commit, 30 files changed,
  1767 insertions and 60 deletions. The local main and existing origin/main
  agreed; no remote fetch was needed or performed.

This repository contains copied source, never a link to the origin checkout.
There is no source dependency, upstream remote, submodule, subtree, or circuit
HTTP service. Package dependencies are installed separately for this workspace.

## Copy inventory and exclusions

Copied 346 Git-tracked files byte-for-byte before adaptation. Excluded five
Git LFS model paths, as required by the destination's no-weights policy:

1. `models/v2_original.pt`
2. `models/ocr/rapidocr/PP-OCRv6_det_small.onnx`
3. `models/ocr/rapidocr/PP-OCRv6_rec_small.onnx`
4. `models/ocr/rapidocr/ch_ppocr_mobile_v2.0_cls_mobile.onnx`
5. `models/ocr/easyocr/bengali.pth`

The original `.git`, environments, dependencies, builds, private configuration,
owner images/datasets, caches, and generated local evidence were never copied.
Tracked generated demo images, visual baselines, fonts, documentation images,
fixtures, and historical JSON reports are retained to preserve baseline checks.
No model bytes or LFS pointer files are included in this repository.

The source hash inventory is in [import-manifest.json](import-manifest.json).
It records original hashes, not a claim that adapted documentation/packaging is
unchanged. Final changed-file and verification records are appended below.

## Reconnaissance conflicts and M0 interpretations

The user requested continue after the conflicts were reported. M0 follows the
brief's no-weights rule while preserving the actual current circuit defaults:
hybrid OCR, relative local model paths, and two inference threads. It does not
restore older legacy defaults. Existing circuit algorithms, API keys, editor,
rendering, saved netlist schema, fixtures, and tests remain unchanged.

The canonical distribution and public Python package are `augphys`. The internal
`circuit_sim` compatibility import refers to this repository's source and keeps
baseline tests and old CLI invocations working; no origin package is installed.
Model files are supplied manually by the owner and remain ignored. Model/dataset
licence decisions remain with the owner; preserved notices are not an approval.

Setup/start scripts are adapted to permit a source-only checkout. The strict
doctor inventory remains available for explicitly checking manually supplied
models. Historical upstream setup instructions are identified as historical
and replaced with current local setup guidance where necessary.

## Consolidated historical upstream references

The brief permits origin/checkout references only in this import note. Their
former documentation locations now refer here or use a neutral historical
placeholder. These references document provenance; they are not app inputs:

- The former README clone command was
  `git clone https://github.com/THE-FOOL-T/circuit-sim.git any-folder-name`.
- The former portable release was
  `https://github.com/THE-FOOL-T/circuit-sim/releases/tag/portable-2026-11-11`.
- Its former download URL was
  `https://github.com/THE-FOOL-T/circuit-sim/releases/download/portable-2026-11-11/circuit-sim-portable-2026-11-11.zip`.
- `docs/decisions.md` formerly identified the source build directory as
  `D:/Circuit Simu/circuit_sim`.
- `docs/recon.json` and the JSON example in `docs/recon.md` formerly recorded
  the copied model as `D:/Circuit Simu/circuit_sim/models/v2_original.pt`.
- `docs/mechanics/recon.md` originally identified the same source checkout and
  configured Git origin. Its local provenance references now point to this note.

Older data/model paths in historical reports describe earlier experiments;
current configuration uses only local relative paths or explicit owner
overrides. Those historical records are not consulted to import application code.

## Changes since the brief's recorded commit

`git diff --stat 516e232 HEAD` at the source reports changes to attributes/ignore
rules, README, association formatting and tests, new model-bundle preflight/tests,
portability tests, portable packaging, example OCR/thread defaults, five LFS
models and their manifest/notices/licences, hybrid requirements, the doctor
runner command, and Windows setup/start scripts. Circuit engine, detector,
solver, and frontend logic are not changed by that comparison. The old
286-Python count predates the hybrid integration; the latest source documentation
records 397 Python passed plus one skipped and 82 frontend passed.

## Verification record

In progress. Final exact commands, counts, isolation scope, changes, and limits
will be recorded here and in [mechanics/status.md](mechanics/status.md) before
M0 is declared complete. No recognition accuracy follows from passing tests.
