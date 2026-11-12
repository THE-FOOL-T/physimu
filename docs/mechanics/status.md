# Mechanics milestone status

## M0 — standalone source import (2026-11-12)

M0 is complete with the baseline's documented intermittent keyboard chooser
failure disclosed below. M1 has not started. No mechanics product code, detector,
scene, solver, gold annotation, or training data was added.

### Implemented

- Copied 346 tracked baseline files from clean main at
  `97702f2bbfd42f15f434b0acffdc1fc4bc678400`; excluded all five tracked model
  weights. The independent repository has no remote or submodule. Exact origin,
  source path, source comparison, exceptions, and commands are in
  [IMPORT.md](../IMPORT.md).
- Retained circuit implementation, original tests, fixtures, generated demos,
  visual baselines, fonts, example configuration, and dependency pins. No circuit
  files were moved. Imported backend/frontend implementation and original tests
  match the source hash inventory; text verification respects Git's LF policy,
  and binary assets are checked byte-for-byte.
- Installed `augphys` locally with a root editable mapping and a local
  `circuit_sim` compatibility import. Both package names resolve inside this
  checkout, including imports from an unrelated working directory. The baseline
  direct backend runner remains unchanged.
- Removed the source's weight-tracking exception/LFS filters and ignored weight
  formats at every depth. Private configuration remains ignored. Source-only
  Windows setup/start no longer require the strict model doctor to succeed.
- Kept current hybrid OCR, relative local model paths, two inference threads,
  OpenCV full/headless `4.10.0.84`, and Torch/Torchvision `2.13.0`/`0.28.0`.
  No analysis algorithm or API key was changed.
- Preserved historical documents and consolidated actual upstream checkout/URL
  references in IMPORT.md. Updated current setup/model notices and appended the
  repository-import decision. Historical measurements were not replaced with
  new results.
- Added eight backend independence checks and a reproducible verification tool
  with Python/Node network guards, checked temporary source isolation, live
  missing-model HTTP verification, and guaranteed source restoration.

### Environment and setup commands

Executed on Windows with Python **3.12.10**, Node **26.4.0**, npm **11.17.0**,
and installed headless Edge through Playwright 1.56.1. Node satisfies the source's
22+ requirement. Node emitted deprecation/color warnings; these did not fail
unit/build gates. The backend emits one existing multipart deprecation warning.

Commands from the destination root:

```powershell
python -m venv --system-site-packages .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
# From frontend: npm.cmd ci --no-audit --no-fund
.\.venv\Scripts\python.exe -m pip install -e .
```

The fresh local environment reuses compatible system Python packages and installs
missing pinned packages into this workspace. It does not use the source
checkout's environment or dependencies. This is not a pristine operating-system
installation. Dependencies were installed explicitly during setup; no models
were downloaded. PowerShell setup/start scripts each parsed with zero errors;
the manual setup commands above were executed rather than rerunning setup.ps1.

### Gates and measured output

| Command/check | Actual result |
| --- | --- |
| Copied baseline, before package changes: `python manage.py test` using the local environment | **397 Python passed, 1 skipped; 82 TypeScript passed; type check and build passed.** Backend duration 38.45 seconds. |
| Final guarded/source-absent `python manage.py test` | **405 Python passed, 1 skipped; 82 TypeScript passed; type check and build passed.** Backend duration 32.02 seconds. |
| Final guarded/source-absent `python manage.py check` | Ruff lint/format and Prettier passed; **405 Python passed, 1 skipped; 82 TypeScript passed; type check and build passed.** Backend duration 30.74 seconds. |
| New independence tests | **8 passed**; all 397 imported Python tests retained. |
| Full guarded/source-absent `python manage.py browser` | **71 collected: 68 passed, 1 failed, 2 skipped**, 3.3 minutes. The failure is the existing keyboard file-chooser timeout; details below. |
| Focused unchanged keyboard scenario, `--repeat-each 5` | **5 passed**, 20.9 seconds, with source absent and guards enabled. Across full/focused runs, all **69 available unique scenarios** passed; two private-asset cases remain skipped. This is not a clean single-run 69/69 claim. |
| Strict layout comparisons | **12/12 passed at zero pixel tolerance**; no baselines regenerated. |
| Generated default-state accessibility reports | **12 reports, zero violations** in their recorded violation lists. |
| Live app, source absent | Root HTTP **200** at `http://127.0.0.1:8000`; health explicitly reported `missing_weights`, OCR `unavailable`, backend `hybrid`, storage memory-only unless corrections opt in. |
| Actual missing-model upload through `/api/analyze` | HTTP success with preserved circuit `demo_fallback` provenance, explicit `detector_unavailable`, and source image. Existing netlist/solution/envelope keys remain present. This is degradation evidence, not image recognition. |
| Python and Node guard probes | Each intentionally attempted external connection was blocked before connecting. |
| Guarded runtime logs | **Zero blocked external connection attempts** recorded during final test/check/serve/upload and focused browser verification. |
| Original source isolation | Source absent during the gates, restored afterwards; the original source tracked tree remains clean. |
| `python manage.py doctor` | Expected exit **1**, explicitly listing five missing model files. Setup/start no longer depend on this optional strict inventory. |

The skipped backend test is the existing opt-in real-model OCR benchmark. The
two skipped browser tests are owner-analysis flow in light/dark themes; their
private cached analysis asset was not copied. No imported test was changed or
disabled to achieve these results.

The initial new independence suite had one failure in its Windows Git stdin
query (404 passed, one failed, one skipped). The query now passes explicit path
arguments and retains its full ignore assertions; the corrected eight tests
and subsequent full gates pass. No circuit change was needed.

### Browser limitation and visual review

The full run's only failure was
`layout.spec.ts: keyboard operation reaches upload, playback, part selection
and value editing`, waiting 30 seconds for the file-chooser event. The imported
verification notes already record this intermittent failure. Its unchanged
scenario passed five isolated repeats with the same source/network isolation.
The failure remains disclosed; tests, timeouts, and snapshots were not weakened.

Actual generated phone EN popover and desktop BN parameter captures were opened
for visual inspection. They retain the baseline layout, font, editing state,
and visible missing-detector notice. This is limited screenshot review, not
human Bangla approval, novice testing, or physical-device verification.

The existing browser tests wrote fresh timing summaries. These were retained
under ignored `.cache/m0-isolation/`, and the original historical documentation
JSON files were restored. Measured synchronous edited-Run events (30 samples):
median **10.9 ms**, p95 **13.5 ms**, maximum **18.2 ms**. Parameter events
(100 samples): median **5.1 ms**, p95 **6.6 ms**, maximum **8.1 ms**. Both exclude
paint; no frame-rate or recognition-accuracy claim is made.

### Independence proof and reproduction

Use `tools/verify_independence.py` with the source path recorded in IMPORT.md.
The exact executed invocations are preserved there. The final complete
test/check/serve proof is in `.cache/m0-final/`; the first full browser run is
in `.cache/m0-isolation/`; five keyboard repeats are in `.cache/m0-keyboard/`.
Logs and summaries remain local, ignored, and reproducible with the tracked
helper. Each completed proof restored the original checkout in a finally block.

The network proof uses process-level Python socket audit hooks and a Node TCP
guard, allowing loopback/local IPC for the app/browser. It does **not** disable
the host network adapters or claim a kernel-level browser firewall. These guards,
the source-absent runs, source-contained import checks, and static transport audit
establish that the exercised circuit path does not depend on an external circuit
server or the original checkout. The optional consent-gated label reader is
retained and was not used against a real provider.

Static checks cover tracked source/URL references, source-contained imports and
files, no upstream dependency/remote/submodule, no tracked model/private state,
unchanged circuit implementation/tests/assets, and circuit transport imports.
Upstream references exist only in IMPORT.md. Internal compatibility package
names are local identifiers, not references to an external installed project.

### Count differences and limits

The brief's historical 286 Python total is stale: the untouched current source
measured **397**, matching its latest portable-setup documentation after hybrid
OCR work. M0 adds exactly eight independence tests, yielding **405**. TypeScript
remains **82**. The current imported browser tree collects **71**, rather than
the old 67-scenario checkpoint; M0 adds no browser scenarios. Counts are measured
above and are not inferred from the number of test functions.

Real-model accuracy, independent real-image circuit correctness, mechanics
accuracy, real HTTP model latency, GPU training duration, Linux/macOS execution,
and real-device/Bangla review are **null/unverified**. HUMAN tasks: supply local
models and reviewed real/gold data, decide any model/data licensing, review
Bangla, and perform device QA. No synthetic measurements are presented as real
accuracy. No training was run.

### Assumptions and stop point

The user's continue was interpreted as authorizing M0 with the explicit
conflict interpretations in plan-M0.md: current clean main; no weights in Git;
retain generated baseline assets; preserve current hybrid defaults; consolidate
historical upstream references; allow source-only setup; retain local legacy
imports while installing augphys. No circuit behaviour change was inferred.

Shared package/setup/ignore changes are committed separately from the unchanged
source import and the verification/documentation additions. M0 ends here.
M1 requires the next explicit continue.
