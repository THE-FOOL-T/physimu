# UI review, round 2

## Before (observed, not inferred)

Opened all six screenshots in `ui/before`: 1440×900, 1024×768 and 390×844,
English and Bangla. Full-page images preserve what falls below the viewport.

- At 1024 English, the drop-zone text and input card content run past the narrow
  left column and are clipped. The Bangla card wraps better but becomes taller.
- At 1440, the parameters extend nearly a screen below the canvas. Totals and
  graph are disconnected from the readouts on the right; large unused space
  remains below the canvas while parameters continue.
- At 390, the page is over 3500 pixels tall. Measurements and selected-part
  controls follow seven large parameter blocks, requiring extensive scrolling.
- Tiny buttons, legend text and notices compete with oversized card padding.
  Top-level Edit/Export, lower direction/download, and playback occupy separate
  rows with no clear common toolbar. API and digit controls disappear on mobile.
- Diagram badges sit across source wires/near component labels. There is no
  theme control, panel navigation or persistent editing badge.

## After

Opened the 12 generated layout snapshots (three widths × two languages × two
themes). The 320 px upload column no longer clips its text. Desktop separates
upload/parameters, canvas tools and readouts; tablet puts readouts below the
canvas. Mobile uses one bottom sheet with wrapping tabs and a bounded scrolling
panel, avoiding the former seven-parameter-plus-readouts page stack. A scroll
panel can show part of its next row at its lower edge; scroll to reveal it.

The canvas toolbar groups playback, mode, direction, edit, export and view
toggles. Totals stay with the readout area. Edit has a dock and persistent badge;
JSON remains under Advanced. All control targets have a 44 px minimum; canvas
selection works with arrow keys. Badge placement now tests collisions against
wires, parts and previously placed labels, including node badges.

Axe initially found a serious Live-badge contrast issue; corrected its foreground
and background tokens and reran the audit. The 12 final JSON audit reports in
`ui/accessibility` contain no violations in the tested default workspace. No
horizontal document scroll was measured. Keyboard upload chooser, play/pause,
canvas selection, parameter editing and Edit entry passed. The snapshot masks
the variable solve-duration field (magenta); this mask is not part of the UI.
The README tour image is an unmasked browser screenshot.

These observations cover generated examples at the tested sizes. Dense uploaded
diagrams may still need zoom or manual label edits. No real-phone review or
human Bangla approval is claimed.

## Final WP8 inspection

Regenerated and opened all 12 snapshots after adding Explain, style estimation,
reader privacy settings and parameter symbols. The first English desktop
readout tab was clipped by the longer history label; dedicated short bilingual
tab labels now fit (Readouts / Selected part / Graph / Explain). Added a browser
check for tab text overflow. Inspected the refreshed unmasked README tour too.
Tablet readouts stay below the canvas; mobile tabs wrap into two rows without
page overflow. The scrollable parameter panel deliberately reveals only some
rows at a time. The demo source PNG itself is cropped at its lower edge; the
workspace does not remove additional source geometry. At phone width, zoom is
still useful for dense diagram labels. All 12 final axe reports have zero
violations. Bangla visual inspection is not linguistic approval.

## Round three WP-A inspection

Opened all 12 regenerated 1440/1024/390 × EN/BN × light/dark layout snapshots
and both `.cache/round3/ui/ocr-{en,bn}.png` dialog screenshots. Text controls fit
in the top toolbar; mobile wraps an extra row without horizontal page overflow.
The correction dialog is readable in both languages, has visible focus and
keeps its controls inside the viewport. The existing demo image is cropped at
its own lower edge; dense labels and left-side parameters still need WP-D.
The 12 axe reports have no violations in these tested default states.

Opened all five final annotated OCR case PNGs in `.cache/round3`, plus earlier
iterations and the 59-image contact sheet. Case 001 is symbolic (no numerical
values); arrow/caption digits must not be used. Case 002 shows readable 24 V
and five resistor values, while R5 remains unread. Case 003 shows 230 V/5 Ω,
with rotated labels and two false switch classifications unresolved. Case 004
reads 5 V/3 Ω/2 Ω/10 Ω but mistakes a meter for a capacitor. Case 005 has an
unresolved 3 Ω reading (332/30/39 conflict), and symbolic E remains unassigned.
Annotations are local only; no owner image is committed. These observations
do not establish wire connectivity or independent OCR accuracy.

Also ran the actual `manage.py ocr-debug` entry point on case 002 and opened
`.cache/round3/cli/de5707fd01ba.png`: it shows the same 24 V/five resistor
assignments and unread R5 as the recorded evaluation, with no additional crop.

## Round three WP-B wire overlays

Opened both iterations of all five `.cache/round3/wires/case-*.png` overlays.
The initial conservative cones exposed cut leads on case 002; preserving
rejected wire-derived OCR and scaling the outward search to symbol size fixes
those attachments. The final case 002 follows the visible five-node mixed
network with no arbitrary diagonal lead. Case 001 now follows the slanted
parallel branches, but the undetected bottom symbol leaves the return open.
Case 003 still misses rotated ends; 004/005 still have meter/source gaps.
These are partial results, with no hidden/disabled observed components. Short
off-axis connections remain low confidence and warned. The overlays were
inspected at native size; owner rasters remain excluded from Git.

Opened `.cache/round3/ui/trace-en.png` and `trace-bn.png` from actual browser
clicks: the amber loose-end ring is visible, the Fix button enters editing and
scrolls to the canvas. The old technical form is still prominent and Bangla
buttons approach its lower boundary; replacing that form is WP-C, not claimed
fixed here. Also reopened the two OCR-dialog screenshots after the regression
run; they remain readable. All 12 unchanged layout comparisons pass.

## Round three WP-C inspection

Opened every generated editor state, including iterations: select, wire, cut,
add, crossing, crop reading, pan and part popover in EN and BN (16 final PNGs in
`.cache/round3/ui/editor`). Tool labels/shortcuts and active borders are visible;
the large Run/pre-check/stepper precede the canvas. The technical form initially
used too much height and was moved into a collapsed section below the canvas.
The icon-only add palette was hard to identify; visible names and larger grid
cells now keep words readable. It scrolls to its final row. The popover sits
beside R1 and keeps value/name/type/delete controls in the viewport. The right
panel shows a short contextual help card. Bangla hints wrap naturally.

Opened all 12 refreshed default layouts at 1440/1024/390 in both themes and
languages. Fit wraps onto another toolbar row at 1024. Phone controls wrap
without document overflow, but the diagram is still too small; WP-D/G address
that. Parameters remain left at this checkpoint. Default axe reports have no
violations. The magenta solve-time mask belongs only to snapshot comparison.

Reopened both OCR dialogs, both clickable trace captures and all three
`docs/browser-{desktop,bangla,mobile}.png` tour captures after the regression
run. The frozen draft and loose-end ring are visible. The left tool rail can
obscure an image edge after focusing a large diagram; this is recorded for the
WP-D Fit/layout change, not claimed fixed here. The public demo's source PNG
also ends at its bottom resistor. No owner raster is committed, no real-phone
or linguistic review is claimed.

## Round three WP-D inspection

Opened all 66 final `.cache/round3/ui/layout-state/{1440,1024,390}-{en,bn}-*.png`
captures: idle, analyzing, result, select, wire, cut, add, crossing, text crop,
pan and part popover, including the earlier iterations before replacement.
Desktop now has only Import on the left, a top toolbar, and Parameters selected
in the right panel. The successful upload collapses Import to a short filename,
part count and Replace/Show-original/Expand controls. The 90-character test hash
is not displayed; the full name is retained in its tooltip. Progress receipts
wrap inside their card, the nine stages are readable, and the cropping notice
stays visible in the compact result summary.

The first tablet layout separated the problem label from its input. Import
fields were grouped, and tablet controls now sit below the canvas. A second
inspection at 1024 × 768 exposed the bottom resistor clipped by the canvas scroll
height. Fit now uses the actual viewport-height limit; final baselines show the
complete bottom resistor and paper margin. Shared pointer transforms preserve
the left edge beside the tool rail. R1's 5 kΩ and R6's 2 kΩ labels are clear;
vertical resistor readings were moved away from their printed values as well.
An arbitrary source caption can still overlap unrecognized printing; the Labels
Off mode and inspector remain available. This is not claimed universally solved.

Every tool has a visible active outline, hint and 44px target. Add shows its
scrolling named palette; Read shows its rectangle instruction; Pan/Fit remain
available. The all-tool test caught text-crop mode intercepting later Select
clicks; changing tools now cancels that interception. The checklist says to Run
a closed draft, rather than calling a frozen draft "running". Opened all six
`.cache/round3/ui/quick/*.png` captures: the new part slider, number field and
Undo value agree; the popover fits the viewport in both languages.

Opened every regenerated baseline in both themes, including repeated passes.
The final 12 baselines show the full circuit and correct panel placement;
magenta over solve-time is Playwright's deliberate dynamic-value mask. Strict
comparison now catches small badge changes. Reopened all 16 editor captures,
both OCR assignment dialogs, both trace issue captures and the three public
tour PNGs generated by regression checks: text actions remain readable and the
amber loose-end ring remains visible beside the wire tool.

The 390px pages wrap without horizontal overflow, with the tab sheet below the
diagram. The wide circuit remains small at Fit; taller white paper does not
increase its width. Zoom/pinch, Pan and the visible navigation hint are needed
for small labels. The mobile pages also remain long while Import is expanded;
successful analysis collapses it. These are observed limits, not a claim of
real-phone usability approval. All added Bangla remains draft/unreviewed.


## Round three WP-E inspected captures

Opened all eight example flow PNGs (light/dark times dots/dashes/arrows/glow),
the two ignored owner-analysis PNGs, reduced-static-arrows, zero-current and
short-circuit. Reopened reduced and zero after improving zero-current wire
visibility. The amber heads and dark edge stand apart from the grey printed
wires; dark-theme yellow has a light inner edge and dark outer edge because
uploaded paper remains white. Dashes are longer, arrows indicate direction,
and Glow has a wider halo. Tails follow bends. The magenta short is visibly
separate, with a white glyph outline. The zero-current capture first looked
solid because the original wire showed through the dash gaps: a narrow white
understroke now makes the grey dashes visible. Reduced motion keeps spaced,
static amber arrowheads. Owner R5 is still marked missing/assumed, and printed
captions can still overlap detections; these captures do not validate extraction.

Opened every one of the 12 regenerated layout baselines. Flow appearance is in
the top toolbar and the slim state legend is below the paper. At 1440 the right
controls remain beside the image; at 1024 they remain below; at 390 controls
wrap without horizontal overflow, but the expanded import page is still long
and the wide circuit needs zoom for small labels. Bangla labels fit their
controls; linguistic correctness is unreviewed. The solve-time magenta block
in baseline captures is an intentional dynamic-value mask.


## Round three WP-F inspected captures

Reopened all 16 EN/BN editor captures after the module split. The seven active
tool states keep their instructions, Run banner, complete paper and amber draft
markers. The Add palette scrolls and all names remain visible. Both part
popovers fit beside R1, with the value/slider agreement and visible close/delete
controls. A transient toast overlaps the lower diagram in these immediate test
captures and disappears after five seconds; no claim that it never covers ink.
The faded particles correctly indicate the frozen draft rather than live flow.
Platform-neutral baseline files were renamed without changing raster bytes.


## Round three WP-G phone captures

Opened mobile-flow-en.png and mobile-flow-bn.png after the two-finger zoom/Fit
checks. The flow menu is contained between the viewport edges at the bottom,
with style/color/size and a visible Close action. The toolbar remains reachable
by scrolling. Magenta arrows are distinct on white paper. Bangla text fits;
this does not establish semantic approval. Fit still makes this wide circuit's
printing small at 390px, so the visible pinch/zoom hint remains necessary.


## Final round-three WP-H inspection

Inspected every image from both full refreshes, using individual views and named
review boards in ignored review-pre/review-final. Final coverage: 66 states
(1440/1024/390 x EN/BN x idle, analyzing, result, seven tools, popover), 16 editor
states, 13 flow captures, six quick sliders, 12 theme/layout baselines, two OCR
and two trace dialogs, three tours, two phone-flow sheets, two phone-part sheets
and one exported PNG: 125 captures. Repeated/overwritten iterations were also
viewed. These private local boards/images are not added to Git.

The first review exposed corrupted micro-unit symbols and Bangla numeral
characters. Correct UTF-8 was restored, literal-spelling regressions were added,
and the complete refresh was repeated. Final full-size owner capture shows
readable microamp units, bright amber heads and the still-unread R5 value. The
exported PNG contains the whole paper and bottom resistor with margins, matching
canvas dimensions. It is a real download, not a mockup.

The first phone popover covered the selected resistor. Its shorter scrolling
sheet now leaves R1 and the complete circuit above the menu in both full-size
mobile-part captures; Close remains visible while lower fields scroll. Both
phone all-tool series and six quick captures were refreshed/reopened after the
fix. The flow sheet remains contained and its magenta arrows stand apart.

Desktop controls remain above/right; tablet/phone controls remain below. Import
collapses after success; the result/cropping notice remains readable. All tools
show the active outline, instructions and frozen-draft banner; a closed draft
asks to Run. OCR assignment dialogs and trace markers remain visible. Zero flow
has grey dashes; reduced motion uses static arrows. In dark UI the paper remains
white, with yellow flow bounded by dark/light edges. The solve-time magenta block
in baselines is an intentional test mask. All twelve strict comparisons pass.

Observed limits remain: small wide diagrams need zoom at 390px, long pages while
Import is expanded, occasional caption/printing collisions, and transient toasts
covering some lower ink. No human language/device/novice approval is implied by
these visual checks. The exact 3.0 V owner picture was not available.
