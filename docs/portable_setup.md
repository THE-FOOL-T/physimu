# Source-only setup and historical sharing record

This checkout contains source, fixtures, and generated demo/test assets. Weights,
datasets, uploads, credentials, `.venv`, and `node_modules` are excluded from Git.
The earlier model-bundled distribution is recorded in [IMPORT.md](IMPORT.md).
Its release and clone instructions are historical and do not apply here.

## First run on a friend's Windows laptop

1. Install Python 3.12 with the Windows `py` launcher, and Node.js 22 or newer.
2. Open PowerShell in this writable source checkout.
3. Run `powershell -ExecutionPolicy Bypass -File .\setup.ps1`. Internet is needed
   to install Python and npm packages. Wait for **Setup complete**.
4. Run `powershell -ExecutionPolicy Bypass -File .\run.ps1`.
5. Open <http://127.0.0.1:8000>. Initial model loading can take tens of seconds.
   Check <http://127.0.0.1:8000/api/health>: expect `ocr_backend: hybrid`, detector
   and OCR ready, and both OCR workers ready before comparing uploads.

Missing models do not block setup/start. Examples and editing remain available;
automatic extraction explicitly reports missing detection/OCR models. The owner
supplies local models manually after licence review. The optional strict
`python manage.py doctor` checks the five files against `models/manifest.json`.
Model loading is local; there is no runtime download.
Dependencies still need installation on each laptop. This bundle does not
include the Python interpreter or an offline package installer.

For Linux/macOS, follow the manual commands in [README](../README.md).
Windows is the tested host; other platforms remain unverified.

## If you copy this source folder

Install dependencies per machine using README. Never copy virtual environments
or private configuration. There is no upstream source/model remote, and no LFS
download is required. Model and data paths are local configuration choices.

## If it starts but diagrams do not simulate correctly

| Check | Meaning / action |
| --- | --- |
| `python manage.py doctor` reports missing/pointer/wrong hash | Supply the correct local files manually; see IMPORT.md for provenance. |
| `/api/health` says warming | Wait for startup; loading is outside the image-analysis time budget. |
| Health says missing_weights/unavailable/error | Inspect the server error; verify the five files and dependencies. |
| Health selects legacy | An old `config.local.yaml` or `CIRCUIT_OCR_BACKEND` overrides hybrid. |
| Health is ready but image warnings mention time limits | The same 25-second budget can complete less work on a slower CPU. Close heavy programs and compare the same original image. |
| Values or connections are wrong | Read the warnings and inspect/Edit the result. Ready models do not guarantee correct recognition. |

Use a fresh extracted folder when comparing machines. Do not copy an old private
`config.local.yaml` with absolute paths. Environment variables also override the
bundled paths. Share the health JSON and exact upload warning if a difference remains.

The default uses two CPU threads and no GPU requirement. Hardware/OS differences
can still change runtime and OCR work completed within the budget. The solver
needs no learned model: it solves the extracted electrical netlist. Missing
detection/text models can produce an incomplete netlist before solving begins.

## Model inventory

| File | Purpose |
| --- | --- |
| `models/v2_original.pt` | Find supported circuit symbols. |
| `models/ocr/rapidocr/PP-OCRv6_det_small.onnx` | Find text regions. |
| `models/ocr/rapidocr/ch_ppocr_mobile_v2.0_cls_mobile.onnx` | Check text direction. |
| `models/ocr/rapidocr/PP-OCRv6_rec_small.onnx` | Read numbers and Latin text. |
| `models/ocr/easyocr/bengali.pth` | Read Bengali in component-adjacent crops. |

The Bengali hybrid path uses recognition only (`detector=False`); CRAFT and
English-only EasyOCR models are unnecessary for this default pipeline.
See the [manifest](../models/manifest.json) for hashes and [notices](../models/NOTICE.md).

## Historical baseline verification on 2026-11-11

The following record belongs to the model-bundled baseline. It is not a new
measurement or a claim that this source-only checkout contains model bytes.

A separate folder with an arbitrary name, no private configuration, no copied
virtual environment, and no `CIRCUIT_*` overrides loaded all five models from its
own `models/` directory. It reused the installed Python dependencies on this
Windows host; a second laptop and a fresh dependency installation were not tested.
Warmup took 26.3 seconds. The supplied 6 V / 10-ohm / 15-ohm parallel image then
completed in 20.6 seconds: three components, two nodes, all values read, 6 ohms
equivalent resistance, and 1 A total supply current. OCR/topology review warnings
still appeared; this single checked image is not a general accuracy measurement.

`python manage.py check` passed: 397 backend tests, one optional benchmark skipped,
82 frontend tests, Python/TypeScript formatting checks, type checking, and build.
PowerShell scripts parsed successfully; setup argument forwarding and stopping on
failed commands were checked. Existing formatting discrepancies in three Python
files were normalized without changing their parsed Python syntax trees.
