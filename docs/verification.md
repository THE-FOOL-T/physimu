# Round 2 verification

Verified on Windows with Python 3.12, Node and installed Edge. Runtime package
versions and CPU are recorded in environment_round2.json. Linux/macOS setup is
documented but was not executed on this host.

## Automated checks

- `python manage.py check`: 203 Python passed, one opt-in local-model OCR test
  skipped; 46 TypeScript passed; focused Ruff, TypeScript and Vite build passed.
  Original coverage (92 Python, 28 TypeScript, four browser tests) was preserved.
- `python manage.py browser`: 30 passed in headless Edge. Includes EN/BN errors,
  valid PNG receipt/decoded preview under 200ms, delayed cancellation/replacement,
  real job stages/boxes, missing weights/fallback separation, preserved previous
  circuit, server/network retry, 120-second timeout, clipboard and PDF selection.
- Layout snapshots: 1440x900, 1024x768, 390x844, English/Bangla, light/dark.
  All 12 opened and inspected; no page horizontal overflow. Axe default-state
  reports contain zero violations. Keyboard upload, playback, selection and
  value editing pass. Images and limits are described in ui-review.md.
- `python -m backend.tools.ocr_benchmark`: separately executed against installed
  local EasyOCR models. Exact normalized tiny-label recall improved 0/18 to
  5/18 (27.8%). Raw recognized strings/timings retained; errors remain substantial.
- `npm audit`: zero reported vulnerabilities after the Vite 6.4.5 update.
- Optional AI reader tests use mocked transport only. No real provider key or
  request was used, and no uploaded diagram left the server.

## Fresh checkout

Verified a local Git clone of committed source at `.cache/round2-clean-any-name`,
with no detector weights or config.local.yaml. Created a separate venv using
`--system-site-packages` to reuse the host's already installed pinned Python
packages, then ran `pip install -e .` with normal dependency resolution,
`npm ci` and `python manage.py check`: **203 Python passed, one skipped, 46 TS
passed, focused lint/type check/build passed**. This checks checkout isolation
and installation; it is not a pristine operating-system or Linux/macOS test.

The first full dependency install exposed a real failure: Ultralytics pulled
OpenCV 5 alongside the pinned headless OpenCV 4 package, changing Hough line
array shape and breaking nine tests. Both distributions are now pinned to
4.10.0.84; the line consumers also normalize either array layout, with two
regression cases. The final checkout check passed after this fix. No existing
test was weakened or skipped to obtain that result.

## Real HTTP regression and latency

`python manage.py smoke` ran on 20 owner seen textbook images after model health
reported ready, one request at a time, local CPU, no external label reader.
20/20 returned populated simulations; 15 degraded. Provenance: 15 extracted,
5 partial, zero demo fallback. These seen examples are regression coverage,
not independent recognition accuracy. Small solver residuals validate the
extracted circuit, not correspondence to the uploaded diagram.

Warm-up: 17.216s (30s target passed). HTTP median 6.407s, p95 10.406s, maximum
14.061s; two requests exceeded 10s. Median/p95 HTTP targets were not met.
Pipeline-only median/p95 were 5.688/9.843s. Complete per-image/stage timings,
scope, reproduction and raw samples are in performance.md and smoke*.json.
Browser event-to-readout timings are in performance.json; paint is excluded.

## Detector and unresolved accuracy

No CUDA GPU available. Paired one-epoch CPU smoke runs and frozen99 evaluations
completed; no smoke model passed the promotion gate. v2 remains selected.
Per-class precision/recall/AP and confusion matrices are in detector_results.md
and detector_smoke_*.json. Full training/evaluation commands are provided there.
Independent printed/handwritten gold netlists, real orientation labels, full
GPU runs, real device QA and Bangla review remain HUMAN tasks. Their unmeasured
accuracy/duration values stay null.

## Reproduce

After README setup:

```sh
python manage.py check
python manage.py serve
# In another activated terminal, after /api/health is ready:
python manage.py browser
python manage.py smoke
python -m backend.tools.ocr_benchmark
```

Smoke needs CIRCUIT_IMAGES plus owner weights/local OCR models. The OCR benchmark
needs explicitly installed local EasyOCR EN/BN models and makes no downloads.
`CIRCUIT_REAL_OCR_TEST=1 python -m pytest backend/tests/test_ocr_tiles.py -q`
enables the normally skipped long local-model regression. In PowerShell set
`$env:CIRCUIT_REAL_OCR_TEST='1'` before invoking pytest.

## Round three WP-A checkpoint

- Python: **258 passed, 1 skipped** (the opt-in real OCR suite). Added tolerant
  Unicode/context parsing, false-label/body/arrow/conflicting-reading guards,
  10/12/14 px touching-label proposals, rotation mapping, dual-engine selection,
  logged partial failures, crop-only API privacy and one-to-one gold matching.
- TypeScript: **47 passed**; native text hit testing added. Build/typecheck passed.
- Browser: **32 passed** in installed headless Edge; new EN/BN real-pointer
  tests assign/ignore text and draw a crop, verify PNG dimensions and reader-off
  consent, then assign its returned value. All original browser tests pass.
- Five real selected owner cases were rerun locally, annotated and opened.
  Coverage **14/30** versus **7/34** frozen baseline; accuracy stays null.
- A concurrent evaluation/test attempt exhausted host memory and was discarded.
  Subsequent runs were sequential with the development server stopped.

WP-B checkpoint: **271 Python passed, 1 skipped**, **48 TypeScript passed**,
typecheck/build and focused Ruff pass. Thirteen added Python regressions cover
0/4/8/12 px loop gaps, arrow/OCR masks, parallel-wire rejection, loose-box axis
refinement, spur pruning, detector dots, retained disconnected parts, failure
geometry, first-hit rays and missing-part ghosts. The added TypeScript check
verifies native clickable issue locations. Original tracing/cache tests pass.

The WP-B focused browser run passed **17 tests**, including all 12 unchanged
layout comparisons, keyboard navigation, EN/BN crop correction, and two new
real-click issue-location tests. No layout baselines needed regeneration.

## Round three WP-C checkpoint

- **273 Python passed, 1 skipped**: the analytic editor fixture and an edited
  `/api/solve` value/provenance regression were added.
- **66 TypeScript passed**, build/typecheck and focused Ruff passed. Seventeen
  topology/history checks include 12 × 35 seeded edit sequences; the new
  analytic fixture also runs through the original cross-language physics test.
- **42 browser scenarios passed across the full and focused runs**. The full
  run exposed three duplicate tool-attribute selectors; the canvas attribute was
  renamed and all eight editor cases passed again. A final missed-part rerun
  also verifies that Undo/Redo updates the open value input. Earlier form-based
  tests now open Advanced or use the popover, retaining their original checks.
- Real mouse tests cover missing wire/part, terminal drag, cutting, type changes,
  undo/redo, frozen draft, failed Run, Ctrl+Enter, edited export, comparison and
  assistant/checklist-only repair. Phone touch drawing passes.
- Run median/p95/max: **11.5/18.7/20.9 ms**, 30 local browser events, excludes
  paint. Parameter-event median/p95: **5.4/6.5 ms**, 100 events, excludes paint.
- All 12 regenerated layouts, 16 EN/BN tool/popover states, repeated OCR/trace
  screenshots and three public-example tour captures were opened and inspected.

## Round three WP-D checkpoint

- `python manage.py check`: **274 Python passed, 1 skipped**, **69 TypeScript
  passed**, typecheck/build and focused Ruff pass. New checks cover native-edge
  margins/round trips, hash filenames, R1/R6 badge clearance and border ink.
- **55 browser scenarios passed across the full and focused reruns**. The first
  full run passed 45/49; receipt-extension expectations and expanding collapsed
  import settings were repaired, and a subpixel corner probe was made tolerant
  of rasterization. Those cases and six new quick-slider cases passed. The final
  seven viewport/state/edge cases and 13 strict layout/keyboard cases pass.
- Six EN/BN × 1440/1024/390 scenarios exercise import collapse/original display,
  hash-title tooltip, source-voltage updates, all seven tools and native Fit
  corners. Six quick-control scenarios verify immediate simulation, frozen draft
  and Undo synchronization. The 320px test samples all four source-image corners.
- All 12 layout baselines were regenerated and then compared successfully at
  zero pixel tolerance. The canvas image is awaited and read back before capture;
  layout snapshots use consistent software canvas rasterization. All 12 axe
  reports have no violations. No real-device or linguistic approval is claimed.
- All 66 final state PNGs, six quick-control captures, 16 repeated editor states,
  both OCR dialogs, both trace captures, three tour captures and every baseline
  iteration generated in this package were opened and inspected; ui-review.md
  records the findings. Owner image files remain ignored.
- Latest local timings: edited Run **13.5/19.4/27.1 ms** median/p95/max (30 events),
  parameter events **5.9/8.7/9.4 ms** (100 events), both exclude paint.


## Round three WP-E checkpoint

- 73 TypeScript tests pass (four new flow tests); typecheck/build pass. Python
  remains 274 passed / one skipped from D, with no Python changes in E.
- Six new browser scenarios pass across the initial run and focused rerun:
  styles in both themes, persistence, smoothing/zero/reduced motion, short and
  owner flow in both themes. The initial short check used the wrong dataset
  name (`active` versus `flowing`); the corrected assertion passes.
- All 13 layout/keyboard cases pass while regenerating the 12 baselines. All
  generated PNGs were opened, including 13 ignored flow captures and repeated
  zero/reduced-motion captures. See ui-review.md for the actual findings.
- Contrast tests explicitly test the composite outline against paper and muted
  wire tints; requested amber fill alone has less than 3:1 on white paper.


## Round three WP-F checkpoint

- 285 Python tests pass, one optional real-model OCR test skips; 78 TypeScript
  tests pass. Build/typecheck and Ruff checks pass. The added risk tests cover
  three cancel/restart cycles during blocked native inference, queued state,
  request-id failure logging, exhausted page evidence retention, stage deadlines,
  1 MB image-free API responses, body limits, typed errors, rate expiry,
  provenance aliases, thread defaults and cancellation propagation.
- Frontend tests cover independent workspace state, small image-free payloads,
  Blob ownership, blocked storage and distinct warning reference counts.
- 18 focused browser scenarios pass across the initial and corrected rerun:
  editor mouse/touch/Run/undo, privacy, upload recovery, PDF, blocked storage and
  self-contained export. The initial three upload failures came from a query
  string bypassing exact mock routes; the client now sends X-Include-Image
  instead, and all ten upload/privacy/robustness scenarios pass together.
- All 16 editor/tool/popover captures generated by this check were opened.
  The new two robustness browser scenarios generate no screenshots.


## Round three WP-G checkpoint

- All twenty warm HTTP requests returned 200: six extracted, fourteen partial.
  Median/p95/max 9.649/12.258/12.737 s; eight exceeded ten seconds. Targets fail.
  Raw records and stage table are in smoke.json and performance.md.
- Process launch to first HTTP: 5.172 s; both models ready: 22.572 s. Health's
  internal model timer: 17.935 s. The new unit tests prevent early ready while
  OCR is warming and preserve missing-model notices.
- Three new browser checks pass: real emulated two-finger pinch 100 to 200%, Fit
  back to 100%, contained flow controls in EN/BN, and warmup polling through OCR
  readiness. Both generated phone captures were opened and inspected.
- A fresh final case-002 HTTP check retained seven parts / five nodes / six
  Given values and nonzero current. Its 16.666 s pipeline time was a separate
  check alongside frontend build, excluded from the isolated 20-image sample.
- CUDA check: unavailable, zero devices. Selected v2_original.pt SHA-256 matches
  detector_results.md. Training, GPU timings and Linux/macOS execution unverified.


## Final round-three WP-H verification

- Final Python: **286 passed, 1 skipped** (optional real-model OCR check).
  Final TypeScript: **82 passed**. Ruff small-rule checks, Ruff format (100-column
  target), Prettier, TypeScript typecheck and Vite production build pass.
- **67 browser scenarios verified across full and focused reruns.** The final
  full refresh passed 66/67; the keyboard file-chooser wait timed out once.
  A subsequent strict layout/keyboard run passed all 13, and the keyboard case
  passed five consecutive isolated repeats. This is disclosed as an intermittent
  headless file-chooser wait, not described as a clean 67/67 single run.
- The earlier first refresh found percent-encoded SVG loading, corrupted micro
  units/Bangla digits, and a legacy fallback without source_image. Those were
  fixed and their targeted checks pass. New regression tests cover SVG/comma
  preservation and literal Unicode spelling; PNG download checks dimensions.
- Final phone inspection found the popover covering the selected symbol. A
  55vh scrolling bottom sheet now keeps the selected part above it, with sticky
  close controls and focus without page jumps. Nine phone/quick-slider checks
  and both phone all-tool scenarios pass after that change.
- Cancelled queued jobs now release their runner's captured raster immediately;
  a weak-reference regression checks this while another native call is blocked.
  Legacy synthetic provenance aliases remain readable as canonical extracted.
- All 12 visual baselines were regenerated, inspected and compared at zero
  pixel tolerance. All 12 axe reports contain zero violations. All final 125 UI
  captures, including every overwritten inspection iteration, were viewed
  directly or on named review boards, with full-size phone/owner/export probes.
- Thirty edited Run events: median/p95/max **12.1/21.6/22.2 ms**. One hundred
  parameter events: **6.3/12.2/13.4 ms**. Both measure synchronous event through
  solver/readout DOM and exclude paint. Raw JSON files remain committed.
- Final owner case 002: entering only R5=8000 as a user value gives source
  current -0.002 A, equivalent resistance 12000 ohm, max KCL residual
  4.34e-19 A and relative power residual 2.90e-16. See case-002-corrected.json.
  This is a known manual repair, not automatic recognition accuracy.
- The ten-minute owner checklist is current. Human novice usability, real-phone
  approval, Bangla language approval, Linux/macOS setup and paired GPU training
  are not claimed. Four reproduced difficult circuits still need manual repair.
  The 6/10-second HTTP latency targets remain missed (see performance.md).
