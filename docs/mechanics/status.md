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

## M1 follow-up — local models and original-app comparison

At the owner's request, copied the five manifest-listed model files from the
original checkout recorded in IMPORT.md into this repository's `models/`:
`v2_original.pt`, the three RapidOCR ONNX files, and `ocr/easyocr/bengali.pth`.
Source and destination sizes/SHA-256 hashes match the manifest. All five paths
are ignored by Git; no weights, private images or dataset files were committed.
No application code or dependency pins changed.

- `python manage.py doctor`: **passed**, all five models OK.
- `python manage.py test`, with models present: **428 Python passed, 1 skipped**
  in **38.18 s**; **84 TypeScript passed**; type check and production build passed.
- Both apps reached detector **ready**, OCR **ready**, with both RapidOCR and
  Bengali OCR workers ready. Library versions and inference/budget settings
  agree; each app uses its own copy of the model files and its own environment.
- Sent the same real image bytes sequentially through `/api/analyze` in each
  app, with `lang=en`, `style=auto`, AI reader off and unchanged default budgets.
  Case: `Screenshot 2026-10-30 232522.png`, SHA-256
  `167ebff80d00595c8f56ec3352ccc73165205c1ba2849a758e071247c0e7b6ec`.
  Both returned `partial` with eight components. Netlist, solution, warnings
  and source image are exactly equal. HTTP durations were 18.641 s (new) and
  18.343 s (original); this is one comparison, not a latency benchmark.

Full response parity **did not pass**. After excluding the intentional new
`domain` field and timing measurements, three diagnostic differences remain:

| Field | New app | Original app |
| --- | ---: | ---: |
| `diagnostics.engine_readings.length` | 24 | 25 |
| `diagnostics.stages[1].readings` (Bengali OCR) | 9 | 10 |
| `diagnostics.texts[6].alternatives.length` | 0 | 1 |

Stopped the remaining image comparisons at this first mismatch, as requested,
and reported it to the owner. The cause is **unverified**; no repeated run,
budget adjustment, pipeline fix or M2 work was performed. Identical netlists on
this case do not establish correct recognition or full response equivalence.

The requested fresh visual Circuit/Mechanics switch check **was not completed**.
Computer Use stopped browser input because it could not determine the current
Windows browser URL confidently enough to enforce policy. No further UI input
was attempted. Earlier M1 browser results remain historical evidence only.

Raw responses, exact differences, copy hashes, environment/readiness records and
test logs remain local under ignored `.cache/model-verification/`. The temporary
original-app server was stopped and the original checkout remains clean. The
new app remains running at `http://127.0.0.1:8000` for the owner's inspection.

M2 remains on hold pending review of the diagnostic mismatch and completion of
the fresh UI check. No source or model fix was made during this verification.

## M1 follow-up resolution — inherited OCR work limits

The owner's next continue resumed the investigation above, without starting M2.
The computed circuit results match across three real images. The diagnostic
count difference reproduces inside the original app itself and is explained by
its existing wall-clock OCR work limit. No circuit implementation, model,
configuration, dependency pin or deadline was changed to obtain these results.

### Cause and evidence

- Compared all **36 pipeline/solver Python files** with the original checkout,
  normalizing CRLF/LF only: **zero content differences**.
- Both saved first-case responses report Bengali OCR `limited` and
  `engine_limits: [easyocr-bn]`. The new app's original nine Bengali readings
  are an exact prefix of the original app's ten. The extra original reading is
  a quotation mark with confidence approximately **0.00448**.
- The unchanged `bangla_adapter.py` stops before another recognition call when
  `time.monotonic() + call_reserve_seconds >= run.deadline`; its default reserve
  is three seconds. `router.py` allocates engines from the remaining OCR time.
  The worker preserves the partial readings and records the work limit. Thus
  elapsed inference time determines how many proposal readings are returned.
- Two fresh requests in the **original app alone** returned **8 then 11**
  Bengali readings for the same first image, versus **10** in its earlier saved
  response. Netlist, solver result, warnings and all other compared circuit
  envelope fields stayed exactly equal. Its own full diagnostic JSON differed
  on those repeats, even after removing timing measurements.
- The fresh new-app first-case response returned **11** Bengali readings and
  matched the original app's second fresh response completely after excluding
  timing fields and the intentional additional `domain` field.

This establishes inherited deadline-dependent diagnostic variability on the
tested case, rather than a new domain-adapter difference. No enlarged-budget
diagnostic was needed or run. All live comparisons used unchanged default
25-second page/16-second text settings, the ten-second hybrid reserve, two CPU
threads, identical image bytes, `lang=en`, `style=auto`, and AI reading off.

### Three-image comparison

All three pairs have exactly equal **netlists, solutions, warnings, source
images, observed netlists, provenance, style estimates and regions**. Full
payload comparison excludes only `domain` and timing keys (`timings`, `seconds`,
`elapsed_seconds`); it retains every diagnostic field.

| Real image | Parts / provenance | Bengali readings: new / original | Circuit fields exact | Full payload exact, excluding domain/timing |
| --- | --- | --- | --- | --- |
| `Screenshot 2026-10-30 232522.png` | 8 / partial | 11 / 11 | Yes | Yes |
| `Screenshot 2026-10-30 232632.png` | 5 / partial | 10 / 12 | Yes | No: OCR diagnostics only |
| `Screenshot 2026-10-30 232905.png` | 7 / extracted | 9 / 11 | Yes | No: OCR diagnostics only |

For every pair, the shorter complete raw-engine reading list is an **exact
prefix** of the longer list. The second pair has 49 structural difference paths
because two extra readings also change the length/order of the fused diagnostic
text list; this is not 49 independent recognition differences. The third pair
has four structural differences in reading counts and text-alternative lengths.

Input SHA-256 hashes, in table order:

1. `167ebff80d00595c8f56ec3352ccc73165205c1ba2849a758e071247c0e7b6ec`
2. `21e520de9e4b8ae0d00c44579c2f2c158d9066ebb402eda2c3f3babd90a12775`
3. `de5707fd01baa68a1d593cca8b37cda8d11fa53952fd1394bb2184877b12734a`

These are regression comparisons on three existing owner images, not a frozen
gold evaluation, recognition-accuracy measurement or latency benchmark. Equal
outputs can share the original app's recognition errors. Full diagnostic
determinism under the default wall-clock limit is **not** claimed.

### Fresh UI check and tests

The browser access host remained unavailable. Using the computer-use workflow
with native Edge, brought the browser into view and observed its current URL
before navigating to `http://127.0.0.1:8000/`. Confirmed:

- Circuit is selected by default; the mixed-network example loads with seven
  components, 24 V, 12 kΩ, and the **Models ready** notice.
- Selecting Mechanics shows its heading and the explicit not-implemented/no
  simulation panel, including the pending Bangla-review notice.

The attempted return to Circuit encountered a non-target legacy-window error,
then a cached-element-unavailable error after refreshing. Stopped UI input and
left the browser on Mechanics. This completes the requested quick look at both
states, but **does not verify a fresh native round trip**. The earlier automated
round-trip tests remain separately recorded historical evidence.

Ran `python manage.py test` again with the copied models present: **428 Python
passed, 1 skipped** in **42.69 s**; **84 TypeScript passed**; type check and build
passed. No test source, threshold or expected result was changed.

Commands from this checkout, using `.venv/Scripts/python.exe`:

```powershell
python .cache/model-verification/followup.py start
python .cache/model-verification/followup.py compare
python manage.py test
```

Local evidence is under ignored `.cache/model-verification/followup/`: raw
responses, exact difference files, original self-repeats, `summary.json`,
`case-summary.json`, readiness/server logs and `test.log`. The file-content and
initial prefix audit is `.cache/model-verification/code-and-prefix-audit.json`.
The source checkout remains clean and its temporary server was stopped. The
new app remains available on loopback port 8000. Weights and private data remain
ignored and no pipeline fix was made.

The mismatch's cause is now explained and three circuit-result comparisons are
complete. Inherited OCR diagnostic variability and the unconfirmed native
reverse selection remain disclosed limitations. This follow-up stops here;
M2 has not started and awaits the next explicit continue.

## M2 — contract, authored fixtures and simulation foundation (2026-11-12)

M2 is complete. The simulator is available in the standalone fixture lab;
the main app retains the M1 Mechanics placeholder until M3. No mechanics
perception, detector, OCR, real/gold annotation, training or automatic routing
was implemented. No circuit implementation, original test, fixture or snapshot
changed or moved.

### Implemented

- Strict finite Pydantic scenes, explicit SI Value metadata/defaults, generated
  canonical serialization schema, matching TS types/schema interpreter, units,
  ids/references and binding validation. Unknown types remain in the document
  with warnings and the original image; unresolved inputs are not replaced.
- Deterministic printed painter and ten authored JSON/PNG pairs covering all
  eight archetypes, including ground/cliff and horizontal/vertical variants.
  Masks and static repairs are authored and serialized with the PNG. Every image
  explicitly says synthetic/authored. These are not real accuracy or gold data.
- Eight pure TS solve/layout/forces/regime/defaultBindings modules: closed forms,
  RK4 pendulum, three spring damping regimes, static/kinetic friction and reversal,
  massive pulley, collision restitution/after-panel checking, conservation and
  endpoint/floor/pulley/slack/compression/contact events.
- Shared accumulator/interpolation clock at 1/240 s, 0.1 s frame-delta cap,
  0.25–4× transport, exact-event scrubber, step, graphs, energy bars, parameter
  badges/locks and native/CSS mapping. No circuit renderer was changed.
- Source-pixel background lifting/repairs, clipped bodies and attached labels,
  original spring lead/coil/lead stretching, tangent ropes, rods, rotating pulley
  pixels, labelled vectors/components, dashed paths, native-size padding/panning,
  user zoom, DPR ≤2 and reduced-motion still previews. Failed checks retain the
  untouched source with overlays and reduce render confidence.
- Physics/initial/locked-geometry binding rules, source-constrained ranges,
  explicit user Values, Modified/Back to original, play-preserving restart and
  four initial-condition drag handles. RK4 edits render a short preview before
  completion; drag updates coalesce per frame. Blank-paper dragging pans the
  native image; narrow views initially centre the first body.
- A separate Vite entry/config at `/mechanics-dev.html`, with no backend/API
  dependency. English dev lab only; M3 owns the bilingual workspace/editor.

Contracts, assumptions, equations/events, resource bounds and reproduction are
documented in [schema.md](schema.md), [decisions.md](decisions.md) and
[plan-M2.md](plan-M2.md). Precomputation over 120 s is explicitly unsupported;
canvas backing dimensions over 16,000 px or 32 million pixels use the source/
overlay fallback. Those limits do not invent shortened physical trajectories.

### Commands and measured gates

Used the existing Windows/Python 3.12.10/Node 26.4.0/Edge environment and local
models. Dependency pins and circuit configuration did not change. No model or
dependency download was needed. The editable mapping was reinstalled for the
new local tools package.

```powershell
.\.venv\Scripts\python.exe -m pip install -e . --no-deps --no-build-isolation
.\.venv\Scripts\python.exe -m backend.tools.mechanics.build_fixtures
.\.venv\Scripts\python.exe -m pytest backend/tests/mechanics/test_scene.py -q
.\.venv\Scripts\python.exe manage.py doctor
.\.venv\Scripts\python.exe manage.py test
.\.venv\Scripts\python.exe manage.py check
.\.venv\Scripts\python.exe manage.py browser
# From frontend; final mechanics suite and standalone lab:
npx.cmd playwright test browser-tests/mechanics.spec.ts
npm.cmd run dev -- --config mechanics-dev.config.mjs --configLoader native --port 5173
```

| Gate | Actual result |
| --- | --- |
| New backend contract/painter/fixture tests | **33 passed** in 9.90 s; both installed namespaces checked in isolated interpreters. |
| New TS physics/binding/clock tests | **14 passed**; textbook equations, energy/momentum, friction directions/reversal/static cases, massive pulley, event times, force balance/damping, bounds, immutable deterministic layout and RK4 preview completion. |
| Corrected first full `manage.py test` | **460 Python passed, 1 skipped** in 47.24 s; **97 TS passed**; type check/build passed. Later added one malformed-input and one force-vector test. |
| Full `manage.py check` | Lint/format/Prettier passed; **461 Python passed, 1 skipped** in 54.89 s; **97 TS passed**; type check/build passed. |
| Completion `manage.py check` | **461 Python passed, 1 skipped** in 53.37 s; **98 TS passed**; lint/format/type check/build passed. |
| Final pre-commit `manage.py test` | **461 Python passed, 1 skipped** in **42.62 s**; **98 TS passed**; type check/build passed. Final separate Ruff/Prettier checks also passed. |
| Post-commit tracked-tree `manage.py test` | **461 Python passed, 1 skipped** in **46.41 s**; **98 TS passed**; type check/build passed, including independence checks with all M2 files now tracked. |
| Full browser suite | **94 collected: 92 passed, 2 skipped**, 4.3 min. All 20 M2 scenarios passed. The unchanged keyboard chooser case passed in this run. |
| Final M2 browser suite after calibration/panning refinements | **20/20 passed**, 39.0 s; same documented native config loader, no teardown assertion. |
| Original circuit layout comparisons | **12/12 passed, zero pixel tolerance**; no baselines regenerated. Main production bundle remained `index-BPt3-liY.js` through completion. |
| Accessibility | 12 generated circuit default reports have **zero violations**; the lab's automated WCAG 2 A/AA check also has zero violations. This does not constitute full human/device accessibility review. |
| Model doctor | Exit **0**, all five existing local model files match. Models remain ignored. |
| Standalone lab | CLI started successfully on port 5173; HTML HTTP **200**. Ten browser fixture tests each assert **zero `/api` requests**. |

Totals: **397 imported + 8 M0 + 23 M1 + 33 M2 = 461 Python**;
**82 imported + 2 M1 + 14 M2 = 98 TS**;
**71 imported + 3 M1 + 20 M2 = 94 browser**. The optional real-model OCR benchmark
and two private owner-asset browser cases retain their original skips. Original
test source, assertions, timeouts and snapshot thresholds were not weakened.
The M0/M1 chooser flake remains historical; one passing full run does not prove
it can never recur.

The first full attempt had 455 Python passes and five failures: the new package
path test imported both compatibility trees into pytest's process and polluted
legacy monkeypatch paths. Its checks now run in separate interpreters; no
packaging bootstrap, circuit implementation or original test was changed.
Intermediate lab checks also exposed readout keyboard focus, terminal scrubber
rounding, live-slider replacement and canvas text-baseline leakage; these were
fixed. The initial launch-drag assertion incorrectly expected the ball's origin
to move; the corrected assertion checks its launch handle/vector. One bundled
config-loader run printed a Windows libuv shutdown assertion despite parent exit
0; the explicit native `.mjs` loader completed subsequent suites cleanly, and
test port 5175 closed. No retries/skips were added to hide those failures.

### Solver and frame-0 evidence

Measured idealized fixture outputs: projectile **T=2.8832080782 s**,
**R=40.7747196738 m**, **H=10.1936799185 m**; incline **4.905 m/s²** without
friction and **3.2058581578 m/s²** for 5 kg/mu_k=0.2; Atwood **a=3.27 m/s²**,
**T=13.08 N**; table pulley **a=2.616 m/s²**. Small-amplitude pendulum period:
closed form **2.0060666807 s**, RK4 measured **2.0061048768 s**. Spring:
**omega=10 rad/s**, **period=0.6283185307 s**. Equal-mass elastic collision:
outgoing velocities **-1 and 2 m/s**, contact **0.5 s**. Closed-form assertions
use relative 1e-6 and RK4 assertions 1e-3.

Maximum undamped energy drift: small-amplitude pendulum **1.98e-13 J**, spring
**8.88e-16 J**; that collision's momentum/energy drift was zero in the sampled
run. Tests also cover unequal masses and inelastic cases. Maximum initial body
anchor error over all ten fixtures was **5.68e-14 px** (gate ≤1 px). These are
synthetic mathematical checks, not extracted-image correctness measurements.

Actual layers 1+2 were composed and read back at native resolution. Mean is
absolute RGB channel difference on 0–255; fraction counts pixels with any channel
difference >16. Limits remain **mean ≤2.0**, **fraction ≤0.005**, plus the
additional **anchor error ≤1 px** check. No threshold was relaxed.

| Fixture | Mean absolute channel difference | Fraction over 16 |
| --- | ---: | ---: |
| projectile_ground | 0.063659 | 0.00040625 |
| projectile_cliff | 0.063587 | 0.00040385 |
| incline | 0.004127 | 0.00003125 |
| pendulum | 0.126590 | 0.00111538 |
| spring_horizontal | 0.035582 | 0.00018510 |
| spring_vertical | 0.030386 | 0.00015865 |
| atwood | 0.131913 | 0.00064183 |
| table_pulley | 0.320216 | 0.00157933 |
| incline_pulley | 0.132967 | 0.00156010 |
| collision | 0.005625 | 0.00003846 |

All ten pass the configured tolerance; this is **not zero changed pixels**.
An intentional 80 px pivot error yielded mean **0.806114** and fraction
**0.00462740**: sparse ink passed the RGB limits alone. The added calibration
check correctly failed at **80 px**, emitted `render_mismatch`, reduced render
confidence to 0.5 and preserved the source with overlays. Passing these checks
still does not establish real-image physical correctness. Back to original
reproduced the initial composed canvas's **exact RGBA hash**, including overlays.

Final ten-fixture render-handler samples: **213**, median **2.1 ms**, p95
**8.8 ms**, maximum **23.5 ms**. Playing rAF intervals: **133**, median
**16.7 ms**, p95 **16.8 ms**, maximum **16.9 ms**. These are short headless Edge
measurements; handler scope includes sampling, draw submission, graphs and DOM,
and excludes presentation/paint completion. They are not a device-wide 60 fps,
model latency, or recognition-accuracy claim.

### Review, shared audit and stop point

Opened actual desktop incline/spring/cliff, degradation, before/after reset and
phone captures for visual inspection. The final phone view keeps native image
size, initially pans the body into view and supports blank-paper panning. This
is screenshot/emulation QA, not a physical-device or human Bangla approval.

Only two previously tracked shared files changed relative to `d61acdb`:

| File | Added | Removed | Purpose |
| --- | ---: | ---: | --- |
| `frontend/src/shell/index.ts` | 1 | 0 | Export the new shared sim facade. |
| `pyproject.toml` | 1 | 1 | List the new local tools package in both namespaces. |

All other product/test/fixture additions are new M2 files. No guard allowances,
dependency pins, model files, circuit implementation, existing test or snapshot
changed. Shared foundation commit: **1169642**; contract/fixtures: **db9a724**;
client solvers/renderer/lab: **6c3768c**. The full test command passed before the
shared commit. This status is a separate documentation commit.

Raw gates and solver/browser summaries are under ignored `.cache/m2-final/`;
captures and full per-fixture samples are under `.cache/m2-browser/`. Fresh
circuit timing JSON was copied there before restoring the historical tracked
performance documents. The original checkout remains clean. These M2 gates ran
with the source present and do not claim a fresh source-absent/kernel-network
proof; existing independence/hash/transport checks passed unchanged.

The intentional standalone preview remains at
`http://127.0.0.1:5173/mechanics-dev.html`; the prior circuit server remains on
port 8000. Test Vite instances closed. No training was run. Real mechanics
accuracy, real-model mechanics latency, frozen real/gold data, GPU duration,
human Bangla review, real-device QA and Linux/macOS execution are
**null/unverified**. HUMAN: start collecting the source-separated printed and
handwritten R0 diagrams and resolve their licences. Gold authoring tools come
in M3; Codex did not create gold scenes.

M2 stops here. M3 requires the next explicit continue.
