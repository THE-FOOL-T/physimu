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

## M3 — mounted image authoring and editing workspace (2026-11-12)

M3 is implemented and the full browser suite passes. M4 has not started.
The main-app Mechanics selector now opens the image workspace; the mechanics
analysis API remains the explicit M1 unsupported placeholder. There is no
mechanics perception, OCR, detector, training, gold data or automatic routing.

### Implemented

- Retained Mechanics workspace with local image upload/preview, diagram,
  Parameters/Warnings/Readouts/Graphs tabs, provenance/regime/validation notices,
  playback/speed/step/reset/scrub, geometry locks/Modified/reset and overlay PNG.
  Parameters are right of the diagram on desktop and above it on phones, with
  scrollable panels. Domain switching pauses animation, cancels pending file
  work and retains both circuit and mechanics documents. No scene/image is
  persisted to browser storage or sent to a server.
- Explicit blank-image authoring: choose an archetype and place an assumed
  template, then position native-pixel body/pivot/pulley/surface/link handles and
  enter physical Values. Templates use the existing synthetic geometry and
  label every physical prior assumed/prior/confidence zero before user edits.
  They do not inspect uploaded pixels. The synthetic fixture menu is explicit.
- Source editor covers object names/types/Values/boxes, mask polygons,
  incline base/tip/angle, pivot and pulley centres, rope/spring end positions
  and attachment targets, drawing missing rope/spring/incline/floor segments,
  repair-line segments, unplaced typed Value assignment and archetype/unsupported
  selection. Added deletion removes absent template objects while preserving
  explicit fixed anchors for retained link endpoints. Paper/ink/stroke are
  editable for real source composition. Unsupported and invalid physical inputs
  retain the original and editor; they never invoke circuit demonstration data.
- Read the circuit editor, geometry and history patterns. Mechanics uses a
  separate bounded 80-action before/after history because the original class
  is netlist-specific. A drag previews then commits once on pointer-up. Undo/redo
  restores scene, parameter overrides and locks; image bytes remain outside
  history. No original editor or geometry module changed.
- Versioned portable JSON embeds the image, canonical source scene, current
  typed scene, bounded parameter overrides and lock state. Import uses M2's
  generated-schema/semantic validator for both scenes, replays overrides,
  verifies consistency and decodes/checks the actual image before replacement.
  Invalid imports preserve the current document. Source calibration remains
  distinct from simulation overrides, including modified-but-relocked geometry.
- Matching `mech.*` EN/BN strings, Bengali font, optional graph digit/font
  formatting, localized overlays/statuses/readouts, native numeric fields,
  keyboard object selection/movement, 44px controls and no autoplay. Reduced
  motion retains explicit Play/Step and predicted paths. Source-image text and
  technical ids/units retain their original spelling. Human Bangla review is
  still pending. Authoring and human QA instructions are in
  [authoring.md](authoring.md) and [manual-qa.md](manual-qa.md).

### Commands and gates

Same local Windows/Python/Node/Edge environment as M2; no dependency or model pin
changed. The original source was present. Python and Node runners used the
existing process-level external-network guards (`AUGPHYS_OFFLINE=1`,
`PYTHONPATH=tools/offline` plus this root, `NODE_OPTIONS` requiring
`tools/offline/network.cjs`, and npm offline mode). Loopback remained allowed;
this is not a new source-absent or host/browser kernel-firewall proof. The
existing port-8000 app was retained, rather than replaced by a guarded server.

Executed from the root, except the frontend commands:

```powershell
# From frontend during implementation:
npm.cmd test
npm.cmd run build
npx.cmd playwright test browser-tests/mechanics-workspace.spec.ts browser-tests/domains.spec.ts
npx.cmd playwright test browser-tests/mechanics-workspace.spec.ts
npx.cmd playwright test browser-tests/mechanics-workspace.spec.ts --grep 'optional downloaded|visual/accessibility'
# From root with the local environment:
.\.venv\Scripts\python.exe manage.py doctor
.\.venv\Scripts\python.exe manage.py test
.\.venv\Scripts\python.exe manage.py check
.\.venv\Scripts\python.exe manage.py browser
.\.venv\Scripts\python.exe manage.py test # final tracked-code completion run
```

| Gate | Actual result |
| --- | --- |
| New mechanics unit cases | **11 passed** through the final full runner. Native templates/calibration, edits/references/units, history, unsupported switching, portable validation/tampering, dependent override order and relocked geometry. |
| Pre-commit guarded `manage.py test` | **461 Python passed, 1 skipped** in **68.57 s**; **109 TS passed**, type check/build passed. |
| Guarded `manage.py check` | Ruff lint/format, full Prettier, **461 Python passed, 1 skipped** in **49.06 s**; **109 TS passed**, type check/build passed. |
| New Mechanics browser file, focused | **24 passed**, **52.9 s**; subsequent real-image/visual focused check **3 passed**, **13.8 s**. Final formatter/lock changes are also covered by the full run below. |
| Full guarded browser runner | **118 collected: 116 passed, 2 skipped**, **5.4 min**. All 24 M3 cases, 20 M2 cases, three M1 cases and 71 imported scenarios retained. |
| Circuit layout regressions | **12/12 passed at zero pixel tolerance**, no snapshot updates. Unchanged keyboard file chooser passed in **2.1 s**; the historical flake did not recur in this run. |
| Accessibility | Both M1 EN/BN switch checks, M3 empty/loaded defaults, EN/BN authored unsupported states and desktop/phone BN checks passed their zero-violation assertions. All 12 generated circuit accessibility reports have zero recorded violations. |
| `manage.py doctor` | **Exit 0**, all five local model files match. Weights remain ignored; no model download, recopy or Git weight change was needed in M3. |
| Runtime network guards | No blocked external attempts recorded by the guarded test/check/browser/completion runners. Public-diagram search/download happened separately at the owner's explicit request. |
| Final tracked-code `manage.py test` | **461 Python passed, 1 skipped** in **45.66 s**; **109 TS passed**, type check/build passed. |

Python remains **461 passed** because M3 changes only frontend product code.
TS is **98 M2 + 11 M3 = 109**. Browser is **94 M2 + 24 M3 = 118**. The existing
opt-in real-model OCR Python benchmark and two private owner-analysis browser
assets remain skipped. The public mechanics image was present, so its optional
browser case ran and passed. No imported test was disabled or changed.

The first expanded browser execution had **22 passes and two failures** when
switching a pendulum to Unsupported: the damping unit changed but its control
unit did not. Both now change together; a new unit regression and both EN/BN
browser cases pass. That unsuccessful execution is not counted as a gate pass.
Later review added replay coverage for dependent friction controls and geometry
that has been changed then relocked. No threshold, timeout or test skip was
introduced to hide failures.

### Public real-image authoring evidence and visual review

The owner asked Codex to find internet diagrams rather than supply a local path.
Found five source candidates, with author/stated rights/download outcomes in
[real-qa-sources.md](real-qa-sources.md). One original pendulum SVG downloaded
successfully; four other downloads returned HTTP 429. The successful source was
rasterized unchanged onto white at **744×700** for the PNG upload control.
All downloaded image/project artifacts stay ignored under `.cache/m3-real/`.
No image, scene or licence decision was added to a training/gold pool.

The actual main-app test uploaded that image, placed a pendulum template, deleted
the absent template ceiling, manually positioned pivot **(354,94)** and bob
**(507,545)**, set its box/mask, entered mass and matched paper/ink/stroke. It
validated, ran, played/paused and wrote a portable scene/image QA project. Scale
and physical mass/length remain authored assumptions/entries, not extracted
measurements or independently reviewed truth.

Initial template-style composition failed visibly; the renderer retained the
original with motion overlays. After explicit manual style corrections, the
actual composed source report is **mean absolute channel difference
0.35296594982078855**, **fraction over 16/255 0.003085637480798771**, and **maximum
initial anchor error 0 px**, passing the unchanged **2.0 / 0.005 / 1 px** limits.
This proves a manually authored example can compose and simulate. It is not
image recognition, recognition accuracy, or pixel-perfect reconstruction.

Opened actual desktop BN, phone BN and real-image playback captures. No
horizontal overflow was detected on the phone, the diagram stays available
below the scrollable parameter panel, and Bengali controls/focus/geometry locks
are visible. This is screenshot/automated QA, not human Bengali approval,
novice testing or physical-device QA.

Fresh browser timing documents were copied to `.cache/m3-final/` and the tracked
historical JSON restored. Thirty circuit edited-Run samples: median **27.3 ms**,
p95 **46.6 ms**, maximum **46.9 ms**. One hundred parameter-event samples: median
**5.7 ms**, p95 **8.0 ms**, maximum **10.0 ms**. Both exclude paint. The Run samples
are slower than the earlier M2 session despite unchanged circuit code; these
are session measurements, not a controlled causal performance comparison.
No frame-rate, HTTP model latency or recognition score is claimed.

### Shared audit, artifacts and stop point

Against M2 `9e32839`, shared changes are limited to README's current capability
notice (**6 added / 3 removed**), **202 added / 1 removed** lines in each EN/BN JSON (201 new matching keys),
and **7 added / 4 removed** lines in the new M2 shared graph kit for optional
format/font arguments with existing defaults. M1's `domains.spec.ts` changes
**7/7** lines to assert the mounted workspace instead of the retired placeholder;
its circuit retention/inactive-shortcut/upload-cancellation assertions remain.
All circuit product files, imported tests/assets/snapshots, backend code, model
pins and scene schema are unchanged. There are no renames.

Shared text/graph/plan commit: **589176a**; authoring/project/history/unit cases:
**431408d**; mounted workspace/renderer/browser integration: **54bbd70**. The
full test command passed before the shared commit. Guides/decision/status and
README updates are a separate documentation commit.

Final logs, guard logs, timing JSON, copied M2 reports and circuit accessibility
reports are under ignored `.cache/m3-final/`; M3 desktop/phone captures are in
`.cache/m3-visual/`; the downloaded source, authored QA project, source hash,
composition/handle report and real playback capture are in `.cache/m3-real/`.
The app remains at `http://127.0.0.1:8000`; the prior M2 dev preview remains on
5173. Browser test Vite instances close after use. No training ran.
The original source checkout remains clean. The final tracked-code test includes
the unchanged source-independence/hash/transport checks; its network log and the
check/browser logs contain zero blocked external attempts.

Real mechanics recognition accuracy, independent real/gold correctness, model
latency, training/GPU duration, licence approval for a dataset, human Bangla
review, physical-device/novice QA and Linux/macOS execution remain
**null/unverified**. HUMAN: approve sources/licences, independently author and
review frozen gold, review Bangla and test physical devices. Codex's local
manual QA project is never designated gold. M3 stops here; M4 requires the next
explicit continue.

## M4 — data tooling and synthetic bootstrap (2026-11-13)

Mechanics data/training tooling is implemented and paired CPU smoke training
completed. The smoke model has zero scores and is not installed for production.
M5 perception/API/UI integration has not started. Frozen real data and reviewed
training labels remain HUMAN tasks, so all real metrics remain null.

### Implemented and preserved

- Added the fixed 21-class schema, contained/fresh dataset outputs, per-image
  hashes/provenance and strict finite in-image YOLO validation. Generated data,
  models, real pool and frozen gold stay ignored; only their READMEs/schema,
  tools/tests and guides enter Git.
- Added a null-scene unreviewed authoring scaffold, gold-envelope/scene validator
  and exclusive portable freeze-hash metadata. The tools never write a gold
  scene. Actual frozen folders contain only READMEs. Test review attestations are
  explicitly synthetic mocks outside those folders, not actual HUMAN approval.
- Reused existing signature/near-duplicate/grouping helpers through the core
  facade and added mechanics split/source/frozen-integrity checks. Exact/resized
  duplicates and source overlaps are covered. This conservative signature does
  not discover every crop, rotation or redraw; human source grouping is required.
- Extended M2 primitives in separate mechanics-only drawing/generator modules.
  Native layout, scale, reflection, typeface/ink/strokes, labels/hatching and
  printed/scan/simulated handwriting/photo styles share their pixel/annotation
  homography. Outputs include images, YOLO labels, auxiliary scenes, indexed
  visible masks, amodal boxes/object maps, source notice and contact sheet.
  Existing M2 painter/fixtures/schema/solvers and all circuit product code remain
  unchanged. Augmented scenes are geometry supervision, not calibrated solver
  or real-recognition benchmarks.
- Added local-checkpoint paired fine-tune/control, plan/execute/smoke/device
  options, immutable input copies and model cards. Circuit weights are refused.
  Full training requires at least 20 independently frozen scenes per real style;
  smoke is explicitly ineligible for promotion. No full or GPU training ran.
- Added per-class precision/recall/AP50/AP50:95, identical explicit evaluation
  protocols, real quotas, separate printed/handwritten frozen reports, fresh
  unreviewed prelabels and provenance-preserving HUMAN-reviewed export import.
  Import binds image and reviewed-label hashes, maps every noncanonical class
  explicitly (null drops it), and rejects leakage before a trainable manifest.
  The promotion tool refuses smoke/synthetic results and checks improvements
  without more than 0.02 common-class recall regression on matching real data.
- Appended independent mechanics config with local `MECHANICS_MODEL` resolution.
  M0's config guard now hashes the identical original byte prefix and separately
  asserts the exact appended settings. Existing config loader, circuit settings,
  model pins, API keys, analysis algorithms, frontend and original test sources
  or snapshot thresholds were not changed.

The plan preceded implementation. Workflow and source/licence decisions are in
[labeling.md](labeling.md), [detector_results.md](detector_results.md) and
[dataset_sources.md](dataset_sources.md). No public training dataset was used;
the M3 public pendulum is unreviewed proposal QA only. Vendor licence statements
are recorded without approving the owner's use.

The owner subsequently confirmed no HUMAN-reviewed data exists and asked Codex
to find it. [public-candidates.md](public-candidates.md) records the completed
source search and ignored local starter pack: seven PNGs and seven null-scene,
review-false scaffolds, including five fresh candidate diagrams, one prior M3 QA
pendulum and one quarantined inconsistent projectile source. An actual corrected
projectile source was found/rendered instead; the disputed free-body diagram
was excluded. Two rate-limited UBC figures were obtained from their publisher.
Original/PNG hashes, attribution, stated terms and provisional source groups are
recorded. No real image/label entered training or frozen gold. Related annotated
datasets use different semantics; no class map or independent gold was invented.
Source-research downloads were authorized network activity outside guarded gates.

### Commands and actual results

Commands were executed from the Windows workspace using the existing Python
3.12.10/Node 26.4.0/npm 11.17.0/Edge environment. Torch 2.13.0+cpu reports CUDA
unavailable; Ultralytics remains 8.4.193. No dependencies or model pins changed.
The local general `yolo26n.pt` was copied to ignored `models/`; its hash and
80-class inventory are recorded in detector_results.md. No checkpoint download.

Representative executed commands (absolute `$PWD` output paths):

```powershell
.\.venv\Scripts\python.exe -m backend.tools.mechanics.make_synthetic --out "$PWD\data\generated_mechanics\m4-r1-20261113-v3" --count 600 --seed 42
.\.venv\Scripts\python.exe -m backend.tools.mechanics.leakage "$PWD\data\generated_mechanics\m4-r1-20261113-v3" --out "$PWD\.cache\m4-final\leakage.json"
# After the pulley-mask correction, generated and audited fresh final v4:
.\.venv\Scripts\python.exe -m backend.tools.mechanics.make_synthetic --out "$PWD\data\generated_mechanics\m4-r1-20261113-v4" --count 600 --seed 42
.\.venv\Scripts\python.exe -m backend.tools.mechanics.leakage "$PWD\data\generated_mechanics\m4-r1-20261113-v4" --out "$PWD\.cache\m4-final\leakage-v4.json"
.\.venv\Scripts\python.exe -m backend.tools.mechanics.train --data "$PWD\data\generated_mechanics\m4-r1-20261113-v3" --pretrained "$PWD\models\yolo26n.pt" --out "$PWD\.cache\m4-cpu-smoke-v1" --smoke --execute --device cpu --imgsz 192 --seed 42
.\.venv\Scripts\python.exe -m backend.tools.mechanics.prelabel .cache/m4-prelabel-input --weights "$PWD\.cache\m4-cpu-smoke-v1\fine_tune\weights\best.pt" --out "$PWD\.cache\m4-prelabels-v1" --imgsz 192 --device cpu
.\.venv\Scripts\python.exe -m backend.tools.mechanics.make_gold_template .cache/m3-real/simple-pendulum.png --out "$PWD\.cache\m4-human-scaffold-v1"
.\.venv\Scripts\python.exe -m backend.tools.mechanics.gold
.\.venv\Scripts\python.exe -m backend.tools.mechanics.eval_detector --quota data/real_pool --out "$PWD\.cache\m4-final\real-quotas.json"
.\.venv\Scripts\python.exe -m backend.tools.mechanics.eval_detector --frozen data/eval/mechanics --style printed --out "$PWD\.cache\m4-final\printed-null.json"
# Same frozen command with --style handwritten and handwritten-null.json.
.\.venv\Scripts\python.exe manage.py doctor
.\.venv\Scripts\python.exe manage.py test
.\.venv\Scripts\python.exe manage.py check
.\.venv\Scripts\python.exe manage.py browser
```

Full gates use the existing Python/Node process guards, loopback allowed, npm
offline and YOLO offline. Guarded smoke/proposal runs used the Python guard too.
The existing main server and original source checkout remain present; this is
not a fresh source-absent or host/browser firewall proof. No source was moved.

| Gate | Actual measured result |
| --- | --- |
| First new data contracts plus independence | 30 passed in 7.28 s. |
| Initial complete new M4 tests | 28 passed in 20.15 s, before the external-map and pulley-ownership regressions were added. |
| Expanded data contract/review cases | 23 passed in 3.59 s; includes explicit external class drops, reviewed-label tamper and frozen-source import rejection. |
| Corrected full `manage.py test`, before shared commit | **490 Python passed, 1 skipped**, 58.10 s; **109 TS passed**; type check/build passed. |
| `manage.py check` | Ruff lint/format and Prettier passed; **490 Python passed, 1 skipped**, 58.24 s; **109 TS passed**; type check/build passed. |
| Pulley mask regression and generator suite | **7 passed**, 22.58 s; ensures the erased rope interior belongs to the pulley without filling its source image with ink. |
| Post-correction lint and formatting | Full Ruff lint and format check passed; 131 files already formatted. |
| Final tracked-code `manage.py test`, after mask correction | **491 Python passed, 1 skipped**, 65.64 s; **109 TS passed**; type check/build passed. |
| Full browser suite | **118 collected: 115 passed, 1 failed, 2 skipped**, 4.9 min. Only failure: the existing keyboard chooser timeout, below. |
| Unchanged keyboard scenario, isolated five times | **5 passed**, 23.0 s. Across full/focused runs all **116 available unique scenarios** passed; this is not a clean single-run 116/116 claim. |
| Strict circuit snapshots and accessibility | **12/12 at zero pixel tolerance**; no baselines regenerated. Twelve recorded default-layout accessibility reports have zero violations; mounted mechanics accessibility cases also passed. |
| Paired CPU smoke | Both arms completed one epoch, 16 train / 8 validation images, all 21 classes present; **45.72 s** complete CLI wall time. |
| Actual proposal/scaffold/null evaluation CLIs | Exit 0; one unreviewed empty proposal, null source-scene scaffold outside gold, zero real images/quotas, separate all-null real style metrics. |
| `manage.py doctor` | Exit 0; all five existing circuit/OCR model files match. The extra general checkpoint remains separate/ignored. |

The first full test invocation passed all 490 Python tests but stopped at npm
because the verification command quoted a Windows Node preload path with
backslashes. The corrected forward-slash path passed the complete command.
This was a guard-launch command error, not a passing full gate or product fix.
Original test assertions, skips, timeouts and snapshots were not weakened.

The full browser run's only failure is the unchanged imported keyboard upload
scenario at `layout.spec.ts:97`, waiting 30 seconds for the file-chooser event,
as previously disclosed in M0/M1. Five focused repetitions pass unchanged with
the same process guards. No production keyboard delay, test retry, skip, timeout
or assertion change was introduced. The two private owner-analysis cases remain
skipped because their optional cached asset is absent. The optional backend
real-model OCR benchmark remains skipped. No new browser test was needed for
these tooling-only changes; the existing Circuit/Mechanics round trips passed.

Fresh circuit timing JSON was copied to `.cache/m4-final/`, then the historical
tracked files restored. Thirty synchronous edited-Run samples: median **12.5 ms**,
p95 **15.4 ms**, maximum **16.4 ms**. One hundred parameter-event samples: median
**5.7 ms**, p95 **6.8 ms**, maximum **8.3 ms**. Both exclude paint and are circuit
UI measurements, not mechanics recognition or frame-rate measurements. Opened
the fresh phone BN mechanics workspace capture; its retained controls and image
remain visible without horizontal overflow. This is limited screenshot QA,
not human Bengali review or physical-device testing.

### Synthetic measurements and limits

Final generated counts, native-layout/contact-sheet review and per-class table
are recorded in [detector_results.md](detector_results.md). Seed 42 produced 600
diagrams, **75 per archetype**, styles **180/120/180/120** printed/scan/simulated
handwriting/photo, **480 train / 120 validation**, **300 mirrored**, **150 without
numeric values**, and **60 with actual Bengali digit text**. Every class appears
at least 75 times, exceeding 40. Images, boxes and scene coordinates stay inside
the native canvas; near-duplicate groups remain within one split.

Final output is ignored `data/generated_mechanics/m4-r1-20261113-v4/`, generated
in **220.98 s**, exit 0. The final split audit also passes with no collisions.
It explicitly reports zero frozen real images and null real-frozen protection.
V4 changes 225 pulley-containing masks from v3, while every image, YOLO label,
scene, object map and manifest byte is identical; that actual comparison is in
`.cache/m4-final/v4-input-comparison.json`. Thus the measured v3 smoke uses the
same image/label inputs as final v4; no detector retraining was necessary for
the mask-only correction. Opened the actual final v4 contact sheet as well.

The actual inspected contact sheet led to readable reflected text, drawn text
extents, improved body contact/attachment handling and truthful support symbols.
A later audit added the explicit pulley-interior mask-ownership correction and
regression. These are synthetic authoring fixes, not real recognition results.
Earlier fresh trial directories stay ignored and are not the final dataset.

Both first-round smoke arms start from the same independent general checkpoint.
Fine-tune training wall time: **21.14 s**; control: **6.63 s**, including SDK/model
work and unequal first-call setup overhead. At common `imgsz=192`, confidence
0.25, matching IoU 0.50, AP floor 0.001 and IoU 0.50:0.05:0.95, every class has
**precision 0, recall 0, AP50 0 and AP50:95 0** in both arms on eight synthetic
validation diagrams/108 objects. **Synthetic, not real accuracy.** No useful
detector, improvement, full training or production promotion is claimed.

Median per-image `model.predict` wall time was **57.9 ms** fine-tune and
**56.8 ms** control (p95 **172.3 / 176.5 ms**). The scope includes preprocessing
and first-call warmup and excludes the data audit. Eight synthetic images do not
establish real latency, HTTP timing or fair model-speed comparison.

### Shared changes, HUMAN tasks and stop point

Against M3 `ff73afe`, shared implementation/config changes are exactly:
`.gitignore` **9 added / 0 removed**, core facade **5/0**, example config **7/0**,
and the M0 independence guard **15/1**. The original example-config prefix is
byte-for-byte identical. No frontend/circuit algorithm, imported original test,
fixture, model pin or circuit visual baseline changed; no renames.

Shared integration/plan commit: **5a46afa**; dataset/gold/generator tools:
**012fb2e**; paired training/evaluation/review import: **d8939e7**. Documentation
is separate; the final mask correction/regression is **6f560f7**. All datasets, models,
scaffolds and proposals stay ignored. The actual frozen tree contains exactly
three READMEs, with no agent-authored gold, labels or freeze manifest.

Python count is **461 M3 + 30 M4 = 491 passed**; TS stays **109**, browser stays
**118 collected**. Full test/check/browser, smoke/proposal, generator and focused
keyboard process-guard logs contain zero blocked external attempts. Original
source tracked status remains clean. No source was moved and no existing server
was stopped. Logs, null reports, per-arm metrics/hashes, input comparison,
accessibility reports and fresh timing/capture copies are in `.cache/m4-final/`.
After staging the completed guides/source catalogue, all eight independence
checks passed again in **6.54 s**, and `git diff --cached --check` passed. Public
starter integrity checks confirm seven exact image hashes and seven null-scene,
review-false scaffolds; frozen real folders remain README-only.

HUMAN: decide source/model/data licences; independently author/review and freeze
at least 20 printed and 20 handwritten real scenes; supply reviewed real labels
(25–40 instances per class, 10 images per archetype); run GPU training and review
real evaluation before model promotion. Bangla review and real-device/novice QA
remain HUMAN too. The public manual QA project and synthetic validator mocks do
not count toward these requirements.

Real printed/handwritten recognition and end-to-end correctness, independent
gold physics, real model/HTTP latency, full/GPU training duration, Linux/macOS,
human Bangla approval and physical-device testing remain **null/unverified**.
No smoke weight was installed at `models/mechanics.pt`. M4 stops here; M5 needs
the next explicit continue.

## M5 — perception, jobs and editable results (2026-11-13)

M5 is implemented with the inherited full-run keyboard chooser failure disclosed
below. M6 has not started. Production mechanics weights and reviewed real gold
are still absent. A useful real-image recognizer is not established by this work.

### Implemented

- Added the independent local 21-class lazy detector, file-identity cache,
  MECHANICS_MODEL override and explicit missing/incompatible-weight result.
  A cancellable core lease serializes application-domain detector use, waits for
  startup warmup and evicts the other detector before loading. Circuit analysis,
  hybrid locking, cancellation, fallback keys and warning order are preserved.
- Implemented measured lines/circles, masked skeleton traces, pendulum geometry,
  spring endpoints/coils, trajectory fits, dimension scale, native body masks,
  static-line repairs and ink/paper/stroke estimates. Collinear ink support
  distinguishes an occluded incline from its uninterrupted parallel rope.
- Added EN/BN/subscript digit normalization and mechanics SI grammar, typed
  Hungarian association with confidence/distance, user-value preservation,
  unplaced Values, structural archetype rules, alternate contact/link scoring,
  physical checks and explicit priors/regime warnings. Bare m/M/g are names.
  Bengali unit spellings remain pending HUMAN review.
- Both existing analysis routes now execute the nine mechanics stages and expose
  partial boxes/text. Results contain a validated native-coordinate scene,
  reason, source image, warnings, timings and diagnostics; no circuit netlist,
  solution or demo. Auto routing remains an unimplemented interface/HTTP 400.
- Wired upload/progress/cancel/result loading into the M3 workspace. The actual
  preprocessed raster replaces the upload preview before native partial boxes
  are drawn. Partial/unsupported results open editing; replacement, edits,
  fixture/import and unmount reject stale results. No second animation loop.
- Unsupported provenance withholds simulation while retaining recognized objects
  for repair. Unresolved/nonzero arbitrary force arrows also block after an
  unrelated authoring edit, so changing a mass cannot enable a solver that
  ignores a retained force. Numerical solvers and renderer thresholds are unchanged.
- Reused the corrections endpoint with explicit mechanics domain/scene validation.
  Consent starts off, requires a separate save action and resets after save or
  replacement/unmount. Native image, scene and consent records are local,
  unreviewed corrections, never gold or training approval. Circuit payloads retain
  their existing validation/storage path.
- Added the frozen end-to-end evaluator with separate printed/handwritten metrics,
  ID-independent scene correspondence, required-Value/attachment comparisons and
  the existing TypeScript solvers/sampler for trajectories. A narrow pure shell
  facade avoids loading browser CSS in the Node metric process. The actual null
  baseline is [end_to_end_baseline.json](end_to_end_baseline.json).
- Recognized ground_hatch as a known static annotation in both validators; the
  open-string field, schema shape and version are unchanged. Added matching
  mech.* text, localized automatic binding labels, and replaced ten pre-existing
  Bangla question-mark strings. Native language review remains pending.

No circuit pipeline, solver, original test source, dependency pin, fixture or
visual baseline changed. No data/model was added to Git, no model was downloaded
and no training or promotion was run. M1-owned placeholder tests now assert the
M5 missing-model/stage contract; their circuit/unknown-domain isolation remains.

### Commands and measured gates

The Windows/Python/Node/Edge environment is the one recorded above. Commands used
the workspace .venv and pinned frontend dependencies. The full isolation launcher
in `.cache/m5-final/run_isolated.py` uses the tracked Python/Node process guards,
checks both source rename targets, and restores the source in finally. It allows
loopback/IPC; this is not a kernel-level browser firewall or host network shutdown.
The source path is recorded only in [IMPORT.md](../IMPORT.md).

```powershell
.\.venv\Scripts\python.exe -m pytest backend/tests/mechanics -q
.\.venv\Scripts\python.exe manage.py test
.\.venv\Scripts\python.exe manage.py check
.\.venv\Scripts\python.exe -m circuit_sim.backend.tests.mechanics.perception_probe
.\.venv\Scripts\python.exe -m backend.tools.mechanics.eval_end_to_end --out .cache/m5-final/frozen-end-to-end.json
.\.venv\Scripts\python.exe manage.py doctor
# From frontend, with the local app/server available for the full suite:
npm.cmd test
npm.cmd run build
npx.cmd playwright test
npx.cmd playwright test --grep 'keyboard operation reaches' --repeat-each 5
npx.cmd playwright test browser-tests/mechanics-analysis.spec.ts
```

| Gate | Actual result |
| --- | --- |
| Focused initial domain/perception suite | **76 passed**, 11.64 s. Later additions cover scale, two collision panels, correction API and evaluation/cache behavior. |
| Expanded mechanics suite before the final three cases | **143 passed**, 58.86 s. Final perception-only suite has **56 passed**, 7.27 s; all cases are also in the full gates below. |
| Corrected full pre-commit manage.py test | **551 Python passed, 1 skipped**, 73.71 s; **115 TS passed**; type check/build passed. |
| Source-absent guarded manage.py test | **551 Python passed, 1 skipped**, 74.76 s; **115 TS passed**; type check/build passed. Full CLI wall time 89.25 s. |
| Source-absent guarded manage.py check | Ruff lint/format and Prettier passed; **551 Python passed, 1 skipped**, 77.33 s; **115 TS passed**; type check/build passed. Full CLI wall time 102.80 s. |
| Completion manage.py test, after force guard and label review | **551 Python passed, 1 skipped**, 79.15 s; **116 TS passed**; type check/build passed. Full CLI wall time 94.92 s. |
| Completion manage.py check | Ruff lint/format and Prettier passed; **551 Python passed, 1 skipped**, 85.48 s; **116 TS passed**; type check/build passed. Full CLI wall time 108.13 s. |
| Full guarded/source-absent browser run | **122 collected: 119 passed, 1 failed, 2 skipped**, 5.4 min. Sole failure: unchanged keyboard file chooser. |
| Unchanged keyboard scenario, isolated repeats | **5 passed**, 26.5 s. Across full/focused runs, all **120 available unique scenarios** pass; this is not a clean single-run 120/120 claim. |
| New mechanics browser cases | All **4 passed** in the full run and again on the final bundle (**24.0 s**): real HTTP oracle upload/progress/text/play/edit, cancellation/switch, missing weights/consent, phone BN layout/accessibility. |
| Strict circuit layouts | **12/12 at zero pixel tolerance**, no snapshot regeneration. Twelve default-layout accessibility reports have zero recorded violations; mechanics accessibility assertions, including the new phone BN case, pass. |
| Actual local API | Root HTTP **200**; mechanics advertises nine stages. Missing mechanics model returns unsupported/weights_unavailable with matching native raster dimensions and no netlist/solution. The negative circuit run preserves detector_unavailable/demo_fallback and its response keys. |
| Real local checkpoint ownership probe | Circuit cache **1/0**, then three mechanics requests **0/1**, then Circuit **1/0**. The second number is mechanics cache size. Only the unpromoted M4 smoke was temporarily selected in that child process. |
| Network/source proof | Both intentional Python/Node external probes blocked. **Zero runtime external attempts** in isolated gates, model probe and completion gates. Original source restored and tracked status clean. |
| Doctor | Exit **0**: all five circuit/OCR files match. This does not approve or inventory a mechanics checkpoint. |

Python is **491 M4 + 56 perception/correction + 4 evaluation/cache = 551 passed**.
TS is **109 M4 + 7 = 116**; the seventh case was added after isolation to prevent
an unrelated authored edit from enabling an unmodelled force. Browser is
**118 M4 + 4 = 122**. The existing opt-in real-model OCR benchmark and two optional
private owner-analysis browser cases retain their original skips.

The full browser failure is the same layout.spec.ts keyboard file-chooser wait
recorded in M0–M4: 30 seconds waiting for the chooser, followed by five unchanged
focused passes. No test retry, timeout, assertion, production keyboard delay,
skip or visual threshold was changed to hide it. The final bundle's focused M5
rerun follows the additional force guard and localized binding labels; no circuit
layout/code was changed after the full browser run.

The first full unit run had **550 passes, one failure, one skip**: immediate
model-lease acquisition emitted a redundant queued stage in an original circuit
job test. The lease now reports queue checks only while waiting; the unchanged
original test and all full gates pass. Initial test-harness import/kwargs/fixture
assumptions, a Node CSS import, and exact-floating-point zero assertion were
corrected. The first browser attempt found an unbound fetch receiver (no upload
reached the API); the default transport now calls fetch through an arrow wrapper.
These failures are retained in logs, not counted as successful gates.

### Synthetic correctness and CPU measurements

The tracked perception_probe uses the ten M2 painted QA fixtures. Providers
supply only their detector boxes and actual printed label strings, never a scene,
archetype or attachment answer. These are known QA fixtures, not a held-out model
benchmark. Every returned supported scene is partial because required Values
remain assumed or unplaced. **Synthetic, not real accuracy.**

| Metric | Measured result |
| --- | --- |
| Archetype correct | **10/10** across all eight archetypes |
| Attachments/contact relationships correct | **20/20**, with geometry-based object correspondence and point support tolerance recorded in the protocol |
| Required parameter Values correct | **21/157 (13.38%)**; missing/assumed Values count wrong even when numerically equal. Includes scale, initial state and physical inputs, not merely detected label precision. |
| Trajectory correct | **2/10**, pendulum and Atwood, at the explicit .05 m displacement/.02 s capped-duration protocol |
| Simulation produced | **10/10**, separate from correctness |
| Independent detector/OCR accuracy | **null** in this oracle probe |
| Frozen printed and handwritten real metrics | **all null**, zero reviewed images/scenes/labels |

Most fixture parameter legends are distant from plausible physical owners and
stay unplaced; they are not silently treated as spatial labels. Defaults and
scale differences therefore make most required Values and trajectories fail.
Correct archetype/attachments and producing an animation do not validate those
Values or trajectories. The UI retains the source, assumptions, warnings and
editor so they can be repaired.

Native geometry tests measure six drawn lines (0/15/30/60/90/−30 degrees): maximum
angle error **0.0746 degrees**, length error **2.0 px**. Circle centre error
**0.0123 px**, radius error **0.0924 px**; derived pendulum length error
**0.0117 px**, angle error **0.0010 degrees**. The drawn ten-coil spring yields
**10 coils**, endpoints **6 px** from truth. Parabola launch tangent error is
**0.00193 degrees**, coefficient error **7.08e−8**, median pixel residual
**0.280 px**. Empty geometry raises explicit unmeasured errors. Dimension labels
also calibrate native scale in a separate test. These controlled drawings do not
establish these errors on real diagrams. Some fixture body masks fall back to
boxes, and all pulley wrapping is inferred with a warning.

Ten-image CPU engine timings, median/p95 milliseconds, with oracle detection and
OCR (not real inference/HTTP): received **50.672/61.956**, preprocess
**85.971/95.816**, detect **0.423/0.485**, text **0.114/0.145**, geometry
**21.474/34.787**, associate **0.451/1.019**, archetype **2.793/4.859**, validate
**1.181/2.020**, total **161.830/199.202**. Received includes model-lease/GC work
in this direct-call probe; service queue time is outside engine timing.

A separate guarded runtime probe deliberately selected the existing unpromoted
M4 smoke checkpoint on three public candidates (Atwood, spring–mass, incline).
It used actual local detection/OCR and returned **zero detections**, unsupported
with retained images on all three. Wall times were **22.581 / 17.070 / 14.667 s**,
including cold/cache/OCR-budget work while verification was active. This is a
runtime/cache check, not a useful model, real correctness score, production HTTP
benchmark or target-latency claim. No smoke weight was copied into models/.

Fresh circuit browser timing JSON was copied to `.cache/m5-final/` and historical
tracked files restored. Thirty synchronous edited-Run events: median **13.1 ms**,
p95 **15.5 ms**, max **26.4 ms**. One hundred parameter events: median **5.7 ms**,
p95 **8.0 ms**, max **9.1 ms**. Both exclude paint; neither is mechanics latency.

### Review, shared boundaries and stop point

Opened actual desktop EN uploaded/edited/paused pendulum and phone BN partial
analysis captures. They retain the source diagram, warning/provenance text,
consent-off control and editable assumptions. The phone browser assertion has
no horizontal overflow. Binding labels and shared OCR/preprocess warnings were
localized after review; Bangla text and physical-device usability are not HUMAN
approved. No frame-0 or render comparison threshold was weakened.

Shared imported-file audit against M4 9c9123b (insertions/deletions): README.md
**8/3**, backend/app/analysis.py **24/2**, backend/app/main.py **20/2**, core facade
**12/0**, frontend EN **60/2**, BN **69/11**. New core/model and pure shell facade
files are separate additions. Mechanics workspace/controller/contract changes
are domain-owned; circuit pipeline/frontend controllers and original tests are
unchanged. No config, packaging list, pin, original fixture or layout snapshot
changed and no imported-source hash allowance was added.

Full source-absent logs are in `.cache/m5-final/isolated/`; completion logs and
summary, null real baseline, synthetic metric/geometry records, actual API/model
probe, captures and timing copies are in `.cache/m5-final/`. Guard probes are
logged separately from runtime. Test-owned oracle providers and the synthetic
probe are tracked/reproducible. Verification servers were closed. The verified
workspace app was restarted at http://127.0.0.1:8000 with its normal circuit/OCR
weights; health reports ready/ready/hybrid. Mechanics still reports missing
weights by default. Source restoration and original-source cleanliness hold.

HUMAN: review licences; independently author/review and freeze at least 20 printed
and 20 handwritten scenes; review disjoint real labels and adequate training/
evaluation before any model promotion; review Bangla and physical devices/novices.
Public candidates, manual QA and synthetic test mocks are not gold. No real gold,
licence approval, useful production mechanics weights or training was produced.
Production mechanics accuracy/latency, GPU duration, Linux/macOS, real-device QA
and human Bangla review remain **null/unverified**. M5 ends here. M6 requires the
next explicit continue.

Ownership/facades/plan commit: **d5e6676**; domain perception, tests and evaluation:
**3ebb53b**; shared app/workspace integration, translations and browser cases:
**de0d1bd**. Documentation is separate. Full test passed before the shared commits.
Final evaluator review also covers force correspondence by measured arrow
endpoints with arbitrary ids, and canonicalizes optional gold defaults before
comparison. Its existing four regression tests pass in **13.19 s**; no HUMAN
gold was written. The post-review full test log is
`.cache/m5-final/test-post-review.log`: **551 Python passed, 1 skipped**, 86.73 s;
**116 TS passed**, type check/build passed, zero guarded external attempts.
Full Ruff lint/format also passes after this review. All source/model/transport
boundaries remain the ones audited above.

The final signed after-panel regression (**29a076f**) keeps a negative component
signed and restricts arrow direction to its nearest owning body. The affected
two-panel test passes in **6.21 s**. Final full manage.py test after that change:
**551 Python passed, 1 skipped**, **90.45 s**; **116 TS passed**, type check/build
passed, zero guarded external attempts. Full Ruff lint/format passes too.
Evidence: `.cache/m5-final/signed-after-panel.log` and `test-final-signed.log`.
The after-panel identity mapping remains explicitly assumed, not recognition.
