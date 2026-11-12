# Round three layout

Desktop parameters, readouts, explanations and checklist share one 360px right
panel. Parameters opens by default. Selected-part details and the graph are
collapsible Readouts sections. Playback, speed, direction, editor, exports,
source voltage, labels, OCR evidence, detections and Fit are above the canvas;
only voltage legend and time remain below it. Clicking a part opens its value
slider/number popover; switches also toggle directly. Draft changes stay frozen.

Import collapses after analysis to a filename/part-count/Replace/Show-original
strip. Expand restores its settings. Hash-only titles become Uploaded diagram;
full filenames remain in tooltips. Ordinary upload receipts retain extensions.
Import controls stay together on tablet, and tabs move below the canvas below
1200px. Phone controls wrap with 44px minimum targets and no document overflow.

Fit uses one native-image transform for rendering, editing and text selection,
with a 24px margin on each side, and respects the visible canvas height. The
editor rail has its own width, so it no longer covers the left image edge.
Zoom, wheel/pinch and pan share this transform. A conservative original-border
ink check reports possible source cropping; it cannot reconstruct missing ink.

Part badges try four sides, then greater separation and current-only text.
Actual OCR boxes and common printed-value zones are obstacles. Labels can be
compact, full V/I/P, or off. Arbitrary unrecognized printed labels can still
collide; full readings remain available on hover or in the part inspector.

The wide example still fits small on a 390px phone. Taller paper preserves all
edges and provides room for editing; it cannot enlarge a wide image while also
showing its full width. Pinch/wheel zoom, pan, Fit and the visible hint address
navigation. No real-phone or human Bangla approval is claimed.

Validation adds a border notice regression, three Fit/title/label unit tests,
six bilingual viewport/state scenarios, an edge-pixel/320px wrapping scenario,
and six quick-slider/frozen-draft/undo scenarios. Browser coordinate helpers use
the actual rendered transform rather than assuming a width-only scale.
