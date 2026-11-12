# WP-C mouse editor

Fix circuit opens a frozen draft. The Parts → Wires → Values assistant and
ordered checklist update geometry/checks immediately. Run (Ctrl+Enter) rebuilds
topology, checks the source loop, resolves constraints without changing user
values, solves, then marks the result `edited`. Failed runs stay in edit mode;
the first issue is highlighted. Done prompts for Run. Automatic reruns are off
by default. Edit again, reset, undo/redo and a faint automatic-result comparison
are available. The previous technical form is collapsed below the canvas.

Pointer tools: select/move, terminal drag, orthogonal/free-angle bent wires,
piece/drag cutting, rectangle/click part placement with snapped ends, junction
join/separate, crop reading, Space/middle-button pan, wheel/pinch zoom and Fit.
Part popovers offer type icons, number/unit, presets, name, rotate, polarity,
switch state and deletion. Tab cycles parts/wires; Enter opens a part, arrows
nudge, Delete removes, Esc cancels, and Ctrl+Z/Y undo/redo. Live announcements
describe edits. The right panel becomes contextual help while editing.

`rebuildTopology` is the single union-find path for edits. Geometry/shared
endpoints define connectivity; independent crossing channels stay separate
until a junction is added. Interior contacts split segments so wire-flow
injections have a connected graph. IDs are deterministic; unchanged groups
retain their ground/labels. Empty nodes are dropped. Undo stores field changes;
a value-only command is under 300 bytes even with a 2 MB image URL. The URL is
never copied into undo entries.

The synthetic `editor_loop.json` has an analytic 3 V / 100 Ω = 0.03 A solution.
Real-pointer browser tests remove a wire and repair it, remove a resistor and
draw a new rectangle/type 220, drag an end onto a wire, cut a piece, change type,
undo/redo, exercise failed/successful Run and compare, follow only the assistant
and checklist, and repeat wire drawing with phone touch emulation. The saved
edited netlist retains the typed 220 Ω value. Python tests check the same user
value/provenance through `/api/solve`.

Twelve seeded sequences of 35 edits (420 operations) check schema validity,
idempotence, equivalent connectivity from a fresh rebuild, undo and redo.
Additional unit cases cover crossings, missed parts, missing wires, unsupported
models and image-free history. Existing editor and physics tests remain.

Measured 30 synchronous Runs on the seven-part example: median **11.5 ms**,
p95 **18.7 ms**, max **20.9 ms**, excluding paint (`edit-performance.json`).
Parameter events measured median/p95 **5.4/6.5 ms**, excluding paint
(`performance.json`). These are local browser timings, not HTTP OCR latency.

Known limits: geometry from legacy saved files may disagree with their logical
node IDs; entering editing derives connectivity from the drawing. Diodes have
no simulation model and appear as an explicit checklist issue. Real-phone
ergonomics are not human-reviewed. WP-D still needs to fix the editor rail/fit
interaction at image edges, move parameters right and enlarge mobile content.

All new Bangla strings are drafts. No owner raster is included in these tests.
