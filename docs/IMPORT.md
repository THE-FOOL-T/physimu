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
It records original raw hashes plus LF-normalized hashes for unchanged UTF-8
text, so Git's line-ending policy works on fresh checkouts. Binary hashes remain
byte-exact. This is not a claim that adapted documentation/packaging is unchanged.

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

## Changes made to run independently

- `pyproject.toml`: install the `augphys` distribution/public package and retain
  a local compatibility package mapping. `bootstrap.py` and root `__init__.py`:
  expose both names from this checkout, independent of its directory name.
- `.gitignore` / `.gitattributes`: remove the tracked-weight exception and LFS
  filters; ignore weight formats globally and Ruff's local cache.
- `setup.ps1` / `run.ps1`: allow setup/start without the strict five-model
  preflight; the doctor implementation itself is unchanged.
- README, portable setup, model notices/card, and decisions: describe this
  source-only checkout, manual model placement, unchanged hybrid defaults,
  package mapping, and preserved historical evidence.
- Historical `docs/recon.md`, `docs/recon.json`, `docs/decisions.md`, and mechanics
  reconnaissance: consolidate actual source-checkout paths/URLs here. The
  historical copied-model path is now repository-relative in the recon records.
- Add `backend/tests/test_independence.py`, `tools/verify_independence.py`,
  `tools/offline/`, the import hash inventory, and mechanics milestone records.

No imported backend implementation, original test, frontend implementation,
fixture, demo, visual baseline, example config, or dependency pin changed. No
file moves or circuit pipeline edits occurred. Internal package/ZIP labels that
name the circuit are identifiers, not imports of a different checkout.

## Verification record

The copied untouched baseline passed 397 Python tests (one optional skipped),
82 frontend tests, type checking, and build. Final source-absent guarded test
and check runs each passed 405 Python tests (397 originals + eight independence
checks, one optional skipped), 82 frontend tests, type checking/build, and
applicable formatting checks.

The full source-absent browser run collected 71: 68 passed, one known keyboard
chooser timeout, two private-asset skips. The unchanged chooser case passed
five isolated repeats. All 69 available unique scenarios were verified across
runs; this is not a clean single-run 69/69 assertion. All 12 zero-tolerance
layouts passed; baselines were not regenerated. Full details and measured
limits are in [mechanics/status.md](mechanics/status.md).

The app served at `http://127.0.0.1:8000` with the origin absent. Health and an
actual upload explicitly reported missing models; the preserved circuit fallback
kept its existing response keys and separate source raster. Python/Node process
guards blocked external probe connections, allowed local app/browser traffic,
and recorded zero external runtime attempts in completed final/focused runs.
Host network adapters were not disabled. Each run restored the original source.
Verification servers were stopped after their checks.

Exact isolation commands, run from the destination root with its local Python:

```powershell
.\.venv\Scripts\python.exe tools/verify_independence.py --source 'D:\Circuit Simu\circuit_sim' --browser
.\.venv\Scripts\python.exe tools/verify_independence.py --source 'D:\Circuit Simu\circuit_sim' --browser --browser-only --browser-filter 'keyboard operation' --browser-repeat 5 --out .cache/m0-keyboard
.\.venv\Scripts\python.exe tools/verify_independence.py --source 'D:\Circuit Simu\circuit_sim' --out .cache/m0-final
```

The first command's nonzero exit is retained with its chooser timeout; the
second and third exited successfully. The initial import commit is `cff4cca`.
Subsequent package/setup and verification/documentation commits separate the
adaptations from that unchanged source import. No recognition accuracy, real
model performance, human review, or licence approval follows from these checks.
