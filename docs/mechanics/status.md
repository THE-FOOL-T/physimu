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

## M1 — domain layer, facades, circuit adapter (2026-11-12)

The M1 domain layer is implemented. The full browser run retains the known M0
keyboard file-chooser timeout described below. M2 has not started.

### Implemented and preserved

- Added the backend Domain protocol and register/get/names registry with
  deterministic circuit/mechanics ordering and duplicate-registration errors.
  The circuit adapter directly calls the existing `analyze_page` in process and
  preserves all existing result keys while adding `domain: circuit`.
- Kept the circuit service's warmup wait, hybrid analysis lock, cooperative
  cancellation, failure fallback, warning ordering and legacy analysis hook.
  Mechanics bypasses that circuit service path and returns `unsupported` with
  `reason: not_implemented`, an empty scene, source image, warning and empty
  timing/style records. It returns no netlist, solution or demonstration.
- Added the backend core facade, re-exporting existing config, preprocessing,
  decoding, style, figure regions, OCR, image encoding and job helpers. Mechanics
  shared imports use the facade; no implementations moved.
- JobStore retains an immutable stage tuple per job. The existing nine circuit
  stages remain the default. The mechanics placeholder has only `received` and
  `done`, because it performs no perception stages. Counts, indices and percent
  use the individual job's stages; capacity, cancellation and TTL stay intact.
- Both analysis routes accept `domain` with default `circuit`. Unknown names,
  including `auto` and an explicitly empty value, return typed HTTP 400
  `unknown_domain`. `GET /api/domains` lists names/stages. Start responses add
  domain/stages while keeping job id, dimensions and page count.
- Added the frontend shell facade, domain registry/interfaces, retained-workspace
  circuit adapter and mechanics placeholder. The top-bar selector defaults to
  Circuit. Unmount hides/inerts circuit content and popovers, pauses its frame
  work, cancels pending uploads and blocks inactive paste/shortcuts; returning
  restores the document, values, edit history and prior visibility. There is
  one existing animation loop and no duplicate workspace initialization.
- Circuit upload explicitly sends its domain, uses returned job-stage metadata,
  and rejects stale poll responses after cancellation. Mechanics has no upload,
  editor or simulation controls at this milestone.
- Added six matching `mech.*` EN/BN keys. The placeholder explicitly marks
  Bangla as pending human review. Extended the editable package lists for both
  local namespaces, and the existing TS runner with the mechanics test glob.
- No circuit pipeline, solver, renderer, netlist format, original test source or
  fixture changed. The M0 hash guard now has an explicit nine-file shared-boundary
  allowance plus the 12 reviewed layout images. Other imported code/tests/assets
  remain hash-protected; the transport audit now also covers core/domains.

### Commands and measured gates

All commands use the workspace `.venv` on the Windows/Python/Node/Edge environment
recorded under M0. No dependency pins changed and no models were downloaded.

```powershell
.\.venv\Scripts\python.exe -m pip install -e . --no-deps --no-build-isolation
.\.venv\Scripts\python.exe -m pytest backend/tests/mechanics -q
# From frontend:
npm.cmd test
npm.cmd run build
npx.cmd playwright test browser-tests/domains.spec.ts
npx.cmd playwright test browser-tests/layout.spec.ts --grep 'workspace.[0-9]' --update-snapshots
# From the repository root; sourcePath is the source checkout recorded in IMPORT.md:
.\.venv\Scripts\python.exe manage.py test
.\.venv\Scripts\python.exe tools/verify_independence.py --source $sourcePath --browser --out .cache/m1-final
.\.venv\Scripts\python.exe tools/verify_independence.py --source $sourcePath --browser --browser-only --browser-filter 'keyboard operation reaches' --browser-repeat 5 --out .cache/m1-keyboard
```

| Gate | Measured result |
| --- | --- |
| New backend domain suite | **23 passed** in 6.90 s. Registry, direct adapter/key preservation, unsupported result, both API forms, unknown/empty domains, concurrent stage lists/cancellation, facade imports and installed package paths. |
| Existing TS runner | **84 passed**: 82 imported plus two domain/lifecycle tests. |
| First full `manage.py test` | **428 Python passed, 1 skipped** in 44.63 s; 84 TS passed; type check/build passed. |
| Source-absent guarded `manage.py test` | **428 Python passed, 1 skipped** in 35.21 s; 84 TS passed; type check/build passed. |
| Source-absent guarded `manage.py check` | Ruff lint/format and Prettier passed; **428 Python passed, 1 skipped** in 34.56 s; 84 TS passed; type check/build passed. |
| Final pre-commit/completion `manage.py test` | **428 Python passed, 1 skipped** in 34.26 s; 84 TS passed; type check/build passed. Final Ruff lint/format and full Prettier checks also passed after the facade type export and expanded transport audit; zero external attempts. |
| New browser file | **3 passed** in 9.9 s; also all three passed in the full run. EN/BN round trips retain the changed resistor value, inactive shortcuts stay inactive, language switching works, and upload sends its domain/stages and cancels on unmount. |
| Full guarded/source-absent browser suite | **74 collected: 71 passed, 1 failed, 2 skipped**, 3.3 min. Only failure: unchanged keyboard chooser scenario, below. |
| Unchanged keyboard case, isolated five times | **5 passed** in 21.0 s, with source absent and guards enabled. Across full/focused runs all **72 available unique scenarios** passed; this is **not** a clean single-run 72/72 result. |
| Updated strict layout baselines | **12/12 passed at zero pixel tolerance** in the full run. Update run: 12 passed in 59.5 s. Test source/assertions/thresholds unchanged. |
| Accessibility | 12 default-layout JSON reports contain zero violations; the two new EN/BN mechanics checks also assert zero WCAG 2 A/AA violations. |
| Live local API | Root HTTP 200; domains list circuit's nine stages and mechanics' two. Both mechanics routes return unsupported/not_implemented with source image, no netlist/solution. Async result finishes at stage index 1/count 2/100 percent. `auto` returns HTTP 400. |
| Missing-model circuit route, guarded/source absent | Original explicit `detector_unavailable`/`demo_fallback` remains, with original response keys plus `domain`. |
| Independence | Both network probes blocked their intentional external connections. Zero runtime external attempts in full and focused guarded runs; original source restored after each. This remains process-level Python/Node guarding, not a host/browser kernel firewall claim. |

Python count is **397 imported + 8 M0 + 23 M1 = 428 passed**; the existing optional
real-model OCR benchmark remains skipped. Browser count is **71 imported + 3 M1
= 74**. The two private owner-analysis browser cases remain skipped because the
optional owner asset is absent. Original tests were not disabled or rewritten.

Raw test/check/server/browser output and summary are in `.cache/m1-final/`;
focused repeats are in `.cache/m1-keyboard/`; initial tests, actual mechanics
HTTP output, before/after images, size/diff inventory and placeholder captures
are in `.cache/m1/`. The final completion run used the same offline environment
as the verifier, with the restored source present, and logs named `*-end.log`.
The source checkout remains clean and no verification server was left running.

The first focused backend run had 21 passes and two empty-domain failures:
FastAPI replaced the empty optional form with its default. Validation now uses
the submitted form value when present, and all six unknown-domain cases pass.
A snapshot-update command with an anchored grep selected no tests; the corrected
command above selected exactly 12. A local screenshot helper initially waited
for a hidden readout row to become visible; it now waits for attachment. These
tool/test setup failures are not included as successful gate executions.

### Browser limitation, visual review and timing

The full run's sole failure is the same imported
`layout.spec.ts: keyboard operation reaches upload, playback, part selection and
value editing` file-chooser wait seen in M0. It timed out at 30 seconds and then
passed five isolated repeats unchanged. No production keyboard delay, test retry,
timeout change, skip, relaxed assertion or snapshot threshold was introduced to
hide this limitation.

Reviewed old/new header comparisons for desktop EN, tablet BN and phone EN/BN,
the full dark phone BN circuit image, and actual desktop EN/phone BN mechanics
captures. The eight desktop/tablet images retain their original dimensions and
have changed pixels only in the header's selector area (y=14..58). Phone images
gain 52 pixels for the selector row. The placeholder captures have no horizontal
overflow. This is automated/screenshot QA, not human Bangla approval or physical
device/novice testing.

Browser-produced timing summaries were copied to ignored `.cache/m1-final/`,
then the historical `docs/edit-performance.json` and `docs/performance.json`
were restored. Thirty synchronous edited-Run samples: median **10.1 ms**, p95
**12.5 ms**, maximum **13.7 ms**. One hundred parameter-event samples: median
**4.7 ms**, p95 **5.8 ms**, maximum **13.1 ms**. Both scopes exclude paint; these
are circuit UI measurements, not recognition latency or frame-rate measurements.

### Shared-file diff audit against M0

Line counts from `git diff --numstat 172250a` (insertions/deletions):

| Shared file | Added | Removed |
| --- | ---: | ---: |
| `README.md` | 10 | 2 |
| `backend/app/analysis.py` | 18 | 4 |
| `backend/app/jobs.py` | 11 | 4 |
| `backend/app/main.py` | 24 | 1 |
| `backend/tests/test_independence.py` (M0 guard) | 28 | 1 |
| `frontend/package.json` | 1 | 1 |
| `frontend/src/i18n/en.json` | 6 | 0 |
| `frontend/src/i18n/bn.json` | 6 | 0 |
| `frontend/src/main.ts` | 24 | 2 |
| `frontend/src/ui/canvas-editor.ts` | 1 | 0 |
| `frontend/src/ui/text-inspector.ts` | 1 | 0 |
| `frontend/src/ui/upload.ts` | 17 | 0 |
| `pyproject.toml` | 1 | 1 |

Binary replacements under `frontend/browser-tests/layout.spec.ts-snapshots/`:

| File | M0 bytes | M1 bytes |
| --- | ---: | ---: |
| `1024-bn-dark.png` | 220688 | 221912 |
| `1024-bn-light.png` | 213723 | 214984 |
| `1024-en-dark.png` | 186606 | 187303 |
| `1024-en-light.png` | 179804 | 180589 |
| `1440-bn-dark.png` | 192167 | 193445 |
| `1440-bn-light.png` | 187329 | 188619 |
| `1440-en-dark.png` | 158639 | 159362 |
| `1440-en-light.png` | 153488 | 154209 |
| `390-bn-dark.png` | 152967 | 154857 |
| `390-bn-light.png` | 149563 | 151419 |
| `390-en-dark.png` | 119951 | 121333 |
| `390-en-light.png` | 116215 | 117548 |

New domain/facade modules and the plan are committed separately from the shared
integration. Status reporting is a separate documentation update. No renames.
The module/plan commit is `40421b9`; the shared integration and its tests/visual
baselines are `cbe05cb`. `manage.py test` passed before the shared commit.

### Assumptions, limits and stop point

The continued M0 baseline/packaging decisions still apply. An empty domain is an
explicit unknown value; omission retains circuit. Mechanics uses two truthful
placeholder stages and empty unmeasured records. Automatic routing is unimplemented.
The existing circuit receives uploads through its retained legacy controller;
the M1 DomainModule mounts/deactivates that workspace rather than relocating or
reinitializing it. The selector justifies these 12 reviewed visual replacements.

Mechanics accuracy, real-image circuit accuracy, real-model latency, training,
GPU execution, Linux/macOS, real devices and human Bangla review remain
**null/unverified**. No data, weights, gold scenes, licence approval or model
training was produced. HUMAN tasks remain local model/licence provision,
Bangla review and physical-device QA. The known keyboard chooser flake remains
an open browser limitation, not a mechanics recognition result.

M1 stops here. M2 requires the next explicit continue.
