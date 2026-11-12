# Round three release status

The requested OCR, tracing, mouse editor, layout, flow and robustness changes
are implemented. Automatic extraction remains experimental: **four of the five
recorded difficult cases still need manual repair**, and some printed values
are unread. The exact 3.0 V picture was not identified; the owner explicitly
accepted alternate failing examples. No recognition accuracy is claimed.

|Package|Result and evidence|Remaining limitation|
|---|---|---|
|A|OCR evidence/crop correction, tolerant units and contextual matching; five recorded cases. Given-value coverage 7/34 to 14/30 at A checkpoint.|Coverage is not accuracy; changed detection denominator; tiny/rotated text and missing part types remain weak.|
|B|Directional leads, wire preservation/repairs and partial circuits; recorded 24 V case has seven parts, five nodes, six Given values and nonzero current in final check.|Other four cases still need repairs; no reviewed topology gold.|
|C|Mouse/touch wire and part editing, frozen draft and explicit Run, undo/redo, geometric topology and checklist.|Automated student-style scenario is not a human novice study.|
|D|Top/right controls, import collapse, full-image Fit, friendly titles, quick source/part sliders, badge placement and phone tabs.|Wide diagrams need zoom on a phone; unrecognized printing can overlap captions.|
|E|Outlined amber flow, tails/styles/colors/size, fair allocation, smoothing, reduced motion and distinct shorts.|The outline meets paper contrast; exact yellow fill alone does not meet 3:1 on white.|
|F|Formatted/enforced checks, UI modules, configurable threads, image-free solve/resolve, bounded/cancellable jobs, budgets, grouped warnings, typed errors and neutral snapshots.|Deadlines are cooperative; a native model call cannot be interrupted. Linux/macOS unverified.|
|G|20-image HTTP median/p95 **9.649/12.258 s**; cold readiness **22.572 s**; phone pinch/Fit and both-model warmup status tested.|6/10 s latency targets fail. No GPU, no paired training; v2 retained. Optional WebM/GIF not done.|
|H|286 Python / 82 TypeScript pass; 67 browser scenarios verified across reruns, 12 strict layouts and axe reports pass; QA guide updated.|Human Bangla, owner-device and independent recognition review remain open.|

One headless file-chooser wait timed out in the full run; the strict 13-case
rerun and five keyboard repeats passed. This is recorded in verification.md.

All Bangla remains unreviewed. Owner images/weights/data are ignored and uploads
remain in memory unless corrections are explicitly saved. Case evidence and
manual-qa.md explain how to inspect and repair a partial result.

The sections below preserve earlier round-two/round-three checkpoints; their
test counts and timings are historical, not the final release totals.

# Round 2 implementation status

The round-two code and local verification are complete except for the explicit
owner dependencies below. This is an experimental application; independent
printed/handwritten end-to-end accuracy remains **null**. A produced simulation
can still have the wrong topology, component type, polarity or values.

## Work packages

|WP|Implemented and verified|Limits / remaining evidence|
|---|---|---|
|0|Arbitrary checkout-name imports, editable package mapping, relative example config, ignored local overrides and environment variables, cross-platform README, check runner.|Executed on Windows; Linux/macOS execution unverified. Final clean-checkout check is recorded in verification.md.|
|1|Validated async memory jobs, real stage callbacks/history, partial boxes, cancel/TTL/caps, warm-up health, instant receipt/preview, paste/drop/PDF pages, retry, summary and explicit extracted/partial/demo provenance.|Polling can skip short stages. Cooperative cancellation takes effect between pipeline stages. HEIC/PDF preview depends on server decoding.|
|2|Desktop three-zone/tablet two-column/mobile tabbed workspace, themes, 44px targets, edit dock, advanced JSON, parameter icons/confidence/status, collision-aware badges, tooltips and keyboard selection.|12 EN/BN light/dark screenshots inspected; real device and human Bangla review pending. Dense labels may need zoom.|
|3|Native overlapping OCR tiles, component-near word proposals, duplicate merge, crop enlargement and coordinate mapping; bounded ambiguous Bengali recognition.|Tiny-label exact normalized recall is only 5/18 (27.8%), versus 0/18 at 640px. Units, subscripts and Bangla still fail. No accuracy-qualified OCR claim.|
|4|Audits/class maps, licensed AITEE remap, all-22-class synthesis, frozen99 exclusion and near-duplicate checks, real/synthetic exposure cap, executable paired training/evaluation and promotion gate, orientation prototype.|No CUDA GPU. Only paired one-epoch CPU plumbing runs completed. Full label-completeness review and GPU training pending; rare-class recall did not improve, so v2 remains selected. Real orientation accuracy null, classifier disabled.|
|5|Dashed/dotted annotations excluded with real-wire protection; Hungarian name/value association; 44 EN/BN parsing cases; both resolvers support total current/power, equivalent R and node-pair voltage; live Explain reductions; visible unknown blocks.|Version-1 netlist shape unchanged. General textbook prose and non-reducible circuits are not given invented series/parallel reductions.|
|6|Untrained printed/photo/handwritten statistics estimate plus override; faint monochrome ruling/shadow/perspective cleanup; pen smoothing/gaps/junction uncertainty; provider-agnostic crop-only opt-in reader with Gemini implementation.|Style confidence is policy, not measured accuracy. Same-contrast black grids remain ambiguous. No real handwritten corpus or real provider/key test; transport tests are mocked.|
|7|Prepared skeleton/masks/adjacency reused across snap retries; four bounded detector recovery crops; OCR atlas and bounded BN retries; real stage timers and 20-image performance report.|Warm-up passes 30s target. HTTP median/p95 narrowly miss 6s/10s targets; see measurements below.|
|8|Original tests preserved; new backend/unit/browser coverage, fresh snapshots/axe checks, manual owner checklist, current docs, explicit UTF-8 reads and PDF error cleanup, Vite security patch.|Clean-checkout verification details and final counts are in verification.md. Human approvals and independent accuracy are not fabricated.|

## Measured results

- Local checks: **203 Python passed**, one opt-in real-OCR test skipped in the
  ordinary suite; **46 TypeScript passed**, focused Ruff, type check and build.
  The real OCR benchmark was separately executed using installed local models.
- Browser: **30 passed** in headless installed Edge, including the original four,
  receipt and decoded PNG preview under 200ms, replacement/cancel, real stage
  polling, fallback separation, both-language errors/retry, timeout, paste/PDF,
  privacy, live explanations, keyboard and 12 layout snapshots. Axe reports are
  in ui/accessibility; all 12 tested default states have zero violations.
- Owner seen-image HTTP regression: **20/20 simulations**, **15 degraded**,
  **15 extracted / 5 partial / 0 demo fallback**. This is not accuracy.
- Warm-up **17.216s**; HTTP median **6.407s**, p95 **10.406s**, maximum **14.061s**;
  two requests over 10s. HTTP latency targets were **not met**. Pipeline-only
  median/p95 **5.688/9.843s** do not replace the HTTP measurements.
- Tiny-label OCR exact normalized recall: **0/18 -> 5/18**; new OCR time
  **3.582-4.349s/page**, versus **7.843-8.727s** for the 640px baseline.
- Frozen99 baseline recall: resistor **88.1%**, source **74.6%**, capacitor **0%**,
  switch **20%**, meters **0%**. One-epoch fine-tune smoke: **93.2/82.6/0/20/0%**
  respectively; no rare-class improvement, no promotion. Control smoke has zero
  recall for those present classes. Full training metrics remain null.

Raw data and reproducible commands: performance.md, smoke.json,
smoke_summary.json, ocr_benchmark.md/json, detector_results.md,
detector_smoke_*.json and reference_99_metrics.json. Source weights are excluded
from Git. All confidence estimates and electrical residuals apply to the
extracted circuit and do not certify its match to the source image.

## HUMAN dependencies

1. Approve source exports/licenses, ambiguous class maps, label completeness and
   unreviewed pseudo-labels before full training. AITEE Apache-2.0 is recorded;
   unavailable/metadata-only public exports are listed in dataset_sources.md.
2. Label independent gold sets: 30-50 printed and 30-50 handwritten images with
   boxes and gold electrical netlists, including Bangla and phone photos. Until
   then, independent electrical correctness remains null.
3. Provide real handwritten training/notebook photos and real orientation crops.
4. Review all Bangla controls, privacy text, warnings and explanation templates;
   key/placeholder parity is tested, linguistic approval is not.
5. Supply a server-side key/model and consent if the optional reader is wanted.
   It is off by default and never sends the full uploaded image.
6. Run full GPU fine-tuning and control using the exact preparation/training/
   evaluation commands in detector_results.md. GPU duration is unmeasured;
   measure a smoke epoch on that GPU before estimating the full run.
7. Review the redesigned UI on a real phone and laptop using manual-qa.md.

## Other known limits

Dense multi-figure pages without broad gutters, very small labels, ambiguous
crossings, missing extended detector classes and arbitrary prose remain weak.
Transient previews have a finite step budget; widely separated time constants
can warn. PNG/netlist export works; WebM/GIF export is not implemented.

## Original-project incident

An initial relative Ultralytics output path inherited an old runs_dir and
created new smoke folders under D:/AugmentedPhysics/runs/detect/models/v3.
Generated files were moved into this repository's ignored models/v3 recovery
folders. Training now enforces absolute workspace-contained output paths.
Original and copied v2 SHA-256 match; no existing checkpoint was overwritten.
Automatic approval review rejected removal of the newly created, now-empty
parent directories with "blocked by policy". Those empty directories remain;
cleanup was not retried through another mechanism.

## Round three progress

WP-A implements tolerant/contextual parsing, conservative unit inference,
source-only EMF symbols, shared rotated/native OCR proposals, local dual-engine
selection, stage diagnostics, text-box assignment/ignore, bounded crop-only
reading and opt-in text corrections. Five recorded cases and CLI/evaluation
tools are included. Coverage is 7/34 → 14/30, not accuracy; no reviewed gold is
available. The 24 V source is read, but tiny/rotated labels remain weak and v2
still misclassifies some parts. Tesseract is unavailable locally. The exact
3.0 V example was not identified; the owner explicitly accepted other examples.

At this checkpoint: 258 Python, 47 TypeScript and 32 browser tests pass. New
Bangla is unreviewed. WP-B through WP-H remain in progress; layout, tracing,
editor and animation acceptance are not yet claimed.

WP-B replaces rectangle erasure/Euclidean snapping with wire-preserving masks,
ink-refined bodies, outward lead cones, spur pruning, clustered crossing/dot
decisions, bounded gap/first-hit ray repair, missing-part ghosts and a threshold
repair ladder. All parts stay visible; dead source loops are partial and solver
errors preserve the observed circuit. Amber markers and notices are clickable.
The tracing-only five-case replay is documented in wire-tracing-round3.md:
case 002 now has five nodes/no floating terminals/nonzero current; four cases
remain partial because rotated or missed/misclassified parts still need repair.
No independent topology accuracy or exact 3.0 V acceptance is claimed.

WP-C adds the mouse/touch editor, frozen draft → explicit Run flow, provenance
`edited`, automatic comparison, part popover, Parts/Wires/Values assistant,
grouped checklist, geometric union-find rebuilding and image-free structural
undo. Keyboard/touch and mouse repair scenarios pass. Run p95 is **18.7 ms** on
the seven-part example, excluding paint. **273 Python / 66 TypeScript** tests
pass; all **42 browser scenarios** have passed after focused reruns of corrected
selectors and the added value-undo assertion. No real-phone approval is claimed.
Details and limits are in editor-round3.md. WP-D through WP-H remain.

WP-D moves interactive controls above the diagram and into a default Parameters
tab on the right; tablet/phone use tabs below the canvas. Import collapses after
analysis with Replace/Show-original controls, hash-free titles and full-name
tooltips. A shared Fit transform keeps four native edges and margins visible,
including with the editor rail; possible original-image cropping is warned.
Four-sided badge placement and compact/full/off labels protect printed values.
Part popovers now have value sliders. Details are in layout-round3.md. Wide
diagrams still need zoom on a phone; no real-device approval is claimed.


WP-E adds bright outlined amber particles, tails, four styles/presets, size,
static reduced-motion arrows, magenta shorts and visible dashed zero-current
wires. A smoothed median reference follows slider changes; fair allocation keeps
at least one marker on every live wire (the 500 soft cap yields to that rule).
Settings tolerate blocked storage. Exact yellow fill alone does not meet 3:1
on white; the dark outer boundary supplies contrast. The two-channel contrast
checks pass, with no claim that the fill itself meets the requested ratio.


WP-F formats Python with Ruff (100-column target plus E4/E7/E9/F63/F7/F82)
and enforces Ruff format/Prettier in manage.py check. UI state, shell, parameter,
readout, explanation and translation modules replace the main inline page and
render blocks; upload/workspace/editor remain separate. Reader/recovery/warmup
failures are logged. Inference threads are configurable, defaulting to half the
12 logical CPUs here. Comparison results are in performance.md.

Jobs release cancelled admission slots immediately and expose queued work while
the bounded worker finishes a native call. Crop/tile/trace/recovery loops check
cancellation. Page/stage/component budgets retain partial evidence; atomic model
calls can overrun, so 25 seconds is a cooperative allowance, not a hard promise.
Both analysis endpoints use the same jobs/service implementation. Request bodies,
receive time and per-client rates are bounded, with typed error keys and request
IDs. Warnings are deduplicated, ordered and grouped with affected counts.

Provenance is a synced canonical enum with legacy aliases. Display rasters become
Blob URLs, solve/resolve responses strip them, export remains self contained and
corrections attach the displayed raster separately. Preferences tolerate blocked
storage; replaced previews/crop canvases are released. Snapshots now use neutral
names. Linux/macOS execution and real-device/human Bangla review remain unverified.


WP-G reran the same 20-image HTTP protocol: **9.649 s median / 12.258 s p95**,
maximum 12.737 s, 8 over ten seconds. The 6/10-second targets are not met; this
is slower than round two's less extensive OCR/tracing pipeline. Six extracted
and fourteen partial results produced twenty simulation responses, not twenty
recognition successes. Accuracy stays null. Cold process readiness was 22.572 s,
within thirty seconds. The UI now waits for both detector and OCR before ready.

Phone pinch doubles zoom, Fit restores it, and the four-style/color/size menu
fits in a bottom sheet in both languages. Tall paper/navigation hint were added
in D. Wide diagrams remain small at Fit; real-device approval remains open.
Optional WebM/GIF export is not implemented (PNG and netlist export work).
No CUDA GPU is available; v2's recorded hash is unchanged and no CPU training
was run. Exact GPU commands remain in detector_results.md. Linux/macOS setup
was not executed on this Windows host.

WP-H completed final local checks and screenshot inspection, added PNG export,
SVG data-URL and Unicode spelling regressions, and updated the ten-minute QA
procedure. The phone part sheet now keeps the chosen part visible. Final counts
and the one intermittent browser wait are recorded above and in verification.md.
Known extraction and latency limits still require the owner's attention.
