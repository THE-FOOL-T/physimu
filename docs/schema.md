# Netlist contract

`schema.json` is generated from `backend/pipeline/netlist.py`; regenerate with
`python -m circuit_sim.backend.tools.make_fixtures` from the workspace parent.
The TypeScript contract is `frontend/src/types.ts`. Version is currently 1.

Coordinates are pixels in the raster in `image.path`, including after EXIF,
perspective correction, downsampling or figure cropping. Image dimensions are
positive. API raster paths are data URLs, so saved netlists are self-contained.
Manual demo images have relative HTTP paths. For an offline saved relative path,
use **Open matching image**. Never interpret CSS pixels as image coordinates.

Two terminals per component, finite values, unique IDs, valid node references,
and same-node wire endpoints are validated. Unknown component types remain
representable and get `unsupported_component` solver warnings. Disabled
components remain visible. Extra schema fields are rejected to catch typos.

Extensions beyond the original plan: `initial_voltage`, `initial_current`,
`virtual`, `disabled`, node `label`, meta `style`, `region`, `degraded`, and
`provenance`. Unknown values are null until resolved. User values are immutable
to the resolver. The detector's `voltage_source` maps to netlist `dc_source`.

Current is signed terminal a → b. Voltage drop is Va − Vb. Positive terminal
power is consumed; negative power is delivered. Source `internal_power` is
reported separately. Supplied/consumed totals include that internal loss on both
the source EMF and consumption side, and explicit numerical reference leakage.
`state` stores capacitor voltage and inductor current for continuation.

`short_paths` have ordered wire-segment IDs plus component IDs and a current;
they are residual-flow paths through the actual graph. Equipotential wire loops
use a minimum-length spanning tree; non-tree currents are zero and warned.
No unique physical current is claimed for an ideal zero-resistance mesh.

Warnings contain stable `code`, optional `ref` and a bilingual `message_key`.
Numerical invariants and repair warnings accompany every solve. Fallback
demonstrations explicitly say they are assumed, use no uploaded-image geometry,
and return the original raster separately in `source_image`.
# Round 2 additive conventions (version 1)

The JSON shape, required fields, types and enum values remain unchanged; existing
version-1 netlists need no migration. Existing free-text `meta.provenance` now
uses extracted/partial/demo_fallback for API-produced results. Job envelopes are
separate from the netlist (`jobs.md`). Existing constraint types encode total
current/power with target `total`, equivalent resistance with target `total`,
and voltage between node labels with target `A-B` (or P-Q). Node labels resolve
to actual node ids before evaluating a voltage constraint. No new enum or field
has been added. Equivalent resistance is the solver's source-terminal resistance;
the simple series/parallel explanation is limited to a one-source resistor graph.


The analysis envelope also reports `style_estimate` (untrained statistics and an
explicit override flag), `timings` and optional `regions`. These do not alter a
saved netlist. `/api/analyze/start` and synchronous `/api/analyze` return
`invalid_page` for malformed, negative or out-of-range PDF page values. The
preview can be a transformed analysis raster; the upload receipt retains the
original pixel dimensions when the browser can decode them.

## Round 3 optional value evidence

Value.unit_inferred is an optional boolean, default false. A nearby numeric OCR
label can use the component's unit family with status given, source ocr and
confidence capped at 0.6; the unit_inferred warning requests review. Bare
capacitor numbers use microfarads by policy. Explicit pF/nF/uF prefixes remain
distinct and are never silently changed. This additive field preserves version 1.

Analysis diagnostics.texts records raw text, native boxes, engine/confidence,
parsed result, assignment outcome/reason and candidate rejections. This is an
analysis envelope, not a saved-netlist field. Crop rereading accepts only cropped
pixels at /api/ocr-crop, is local by default, and needs explicit per-request
consent for the configured external label reader. Opted-in correction storage
may include confirmed/ignored text labels in texts.json alongside the raster.

## Round three robustness conventions

`meta.provenance` is now one enum: `extracted` (default), `partial`,
`demo_fallback`, or `edited`. Python validation and frontend normalization
accept the legacy `automatic`, `saved`, `example`, and `synthetic exact geometry` aliases as `extracted`.
The generated JSON Schema describes canonical output. Synthetic generation
also uses `extracted`; its exact-geometry origin is recorded by its fixture/tool.
No netlist version bump or required field was added.

The client converts embedded PNGs into owned Blob URLs, releases them on replace,
and exports self-contained data URLs on demand. Solve/resolve accept an empty
image path and always return it empty. Correction requests attach the displayed
raster separately and omit the image path; saved correction JSON references its
separate image.png. Undo records omit raster content.
