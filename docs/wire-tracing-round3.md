# WP-B tracing evidence

The five WP-A rasters, detections and OCR readings were replayed unchanged to
isolate wire tracing. `python -m backend.tools.wire_eval` writes the measurements
in `wire_round3.json`, appends the cases, and writes ignored overlays. The old
validator's automatic disabled flags are cleared in the replay, because the new
validator keeps all observed parts. No detector or OCR accuracy claim is made.

|Case|WP-A nodes|WP-B nodes|Floating terminals|Computed current|Result|
|---|---:|---:|---:|---|---|
|001 symbolic parallel|8|5|0|zero|Partial: undetected bottom symbol interrupts return|
|002 24 V mixed|7|5|0|nonzero|Source loop now runs; missing 8 kΩ value still needs entry|
|003 rotated diamond|9|10|7|zero|Partial: rotated/misclassified symbols need editing|
|004 meters + sources|11|11|4|zero|Partial: missed meters and wrong capacitor box|
|005 ammeter annotation|9|9|4|zero|Partial: source/symbol gaps need editing|

The previous nonzero results on 004/005 were not proof of correctness: the old
nearest-pixel leads attached parts to inappropriate groups. Conservatively
leaving these partial is preferable to claiming a working extraction. All
observed parts are retained; no demonstration replaces a solver failure.

|Reviewed risk|Evidence and change|
|---|---|
|Text/arrow masks erase wires|Confirmed by the old full-rectangle mask and reproduced by an arrow plus padded OCR box across a synthetic loop. New masks preserve measured straight continuations; rejected wire-derived OCR is not erased. The regression loop stays closed.|
|Nearest-pixel leads form diagonals|Confirmed in the old unconditional Euclidean search. Replaced by outward axis cones and first hits. Off-axis hits are low confidence and warned. A nearer parallel wire is rejected in a test.|
|Loose detector boxes erase stubs|Ink outside both ends fits a shared axis; perpendicular body profiles refine its bounds. A deliberately loose box recovers its axis and retains lead stubs. Real 24 V terminals now all attach.|
|Same-group terminals|Identical/near-identical hits are rejected and warned. A real ink path around the erased body is retained as a possible bypass, with a warning.|
|4–12 px gaps|All four loop regressions (0/4/8/12 px) yield two nodes and 0.03 A at 3 V/100 Ω. Repairs follow facing tangents or stop at the first ray hit. A second wire beyond the first is never selected.|
|Skeleton spurs|Short endpoint-to-branch spurs are pruned, while nearby component ends are protected; direct graph regression verifies the main stroke remains.|
|Undotted crossings|Adjacent branch centers are clustered before pairing opposite ports. Detected junction boxes take priority, then a width-scaled dot test. Original dotted/X/T tests pass; detector-dot override is tested. Uncertain X crossings carry native clickable coordinates.|
|Fixed threshold|Stroke width sets the adaptive block size; one lower-contrast alternative is scored. The selected threshold/repair rung is recorded per case.|
|Snap-only retries|Replaced by conservative trace → bounded repairs → alternative threshold, keeping the least-violation graph.|
|Missed part looks like a wire gap|Facing symbol-sized gaps become ghost rectangles rather than guessed wires. Ghosts can be clicked to enter part placement. They remain suggestions, including false positives from text.|
|Validator hides islands|No automatic disabling. Dead sources receive `source_open_loop`, `not_connected`, and `partial` provenance. Solver failures preserve the observed circuit and expose `solve_failed`.|
|Wire animation loops|The existing shortest-tree `wire_loop` notice remains visible; a zero non-tree segment does not imply the underlying drawing is open.|

Clickable amber endpoints/crossings and ghost rectangles are in the client.
The WP-C mouse tools provide the actual guided repair actions. These images
are seen owner inputs, not independently labelled electrical gold.

A fresh end-to-end HTTP `/api/analyze` request for case 002 also returned five
nodes, 14/14 snapped terminals, zero off-axis snaps and nonzero current
(`extracted`). Total pipeline time was **17.889 s**, with OCR **13.798 s** and
tracing **3.466 s**. This is one integration check, not the 20-image latency
benchmark; it exceeds the latency targets and motivates WP-F/WP-G work.
