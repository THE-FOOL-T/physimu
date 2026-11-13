# Mechanics scene v1

M2 is a fixture-driven simulator. No image is recognized at this milestone. The
Python model is `backend/domains/mechanics/scene.py`; its canonical serialization
schema is [schema.json](schema.json). The TS types and runtime validator live in
`frontend/src/domains/mechanics/{types,validate}.ts`. The client validates against
that generated schema, then checks the same units, ids, references and bindings.

Python authoring accepts omitted defaults. Serialize with
`scene.model_dump(mode="json", by_alias=True)` before sending/importing a scene
in the browser: canonical JSON includes all defaults and nullable fields. The
browser requires this complete representation. Both validators reject extra
fields, nonfinite/coerced numeric inputs, invalid units, duplicate object ids,
unresolved references, non-Value binding targets and inconsistent controls.
Unknown object **types** are retained with `unknown_type`; they are never silently
discarded. The solver refuses that unsupported interpretation and preserves the
source image. An explicitly null number remains unresolved, even when a prior
exists. The schema records shape; the solvers additionally check physical validity.

## Coordinates and Values

All geometry (image dimensions, bbox `[x0,y0,x1,y1]`, polygon masks, anchors,
polylines, pulley centres/radii, arrow endpoints and annotation boxes) is in
native image pixels. Bboxes are axis-aligned and have positive area. An inclined
block's mask follows its rotated outline. Image +x is right, +y is down; default
gravity is `[0,1]`. The M2 solvers explicitly reject other gravity orientations.
No geometry extraction, OCR or recognition assigns these coordinates.

Physical inputs are `Value` objects:

```json
{"number": 5.0, "unit": "kg", "status": "given", "source": "user", "confidence": 1.0}
```

Units are SI: `kg`, `m`, `m/s`, `m/s^2`, `N`, `N/m`, `kg/s`, dimensionless `1`.
Angles use `deg`; angular velocity uses `rad/s`, pendulum damping uses `1/s`.
Scale uses `px/m`. Degrees are used in the document and readouts; RK4 converts
pendulum angles to radians internally. Pendulum angle is from straight down,
positive toward +x. Incline angle is above its horizontal base; launch angle is
above horizontal. Height is positive above ground. Generated world positions
and velocities use SI +x/right, +y/down. Trajectory samples, measured stroke
dimensions and UI range bounds are numerical data rather than authored Values.

Statuses: `given` is supplied, `solved` is derived, `assumed` is a declared prior,
`user` is an intentional control/editor override. Sources: `ocr`, `vlm`,
`geometry`, `constraint`, `prior`, `user`. Confidence is finite in `[0,1]`; it is
metadata, not a measured accuracy score. Synthetic authoring uses `user` for
specified physical quantities and `prior` for assumed scale/gravity.

`body.initial` stores the source calibration (SI position/velocity). Native
anchors stay immutable while parameter overrides control a new initial state.
This separates the source picture from a modified simulation. The projectile
symbol is drawn with its bottom touching the ground when physical launch height
is zero; its centre is one symbol radius above the contact line.

## Graph and references

The top-level document has version/domain/image/archetype/frame, bodies,
surfaces, links, pulleys, forces, annotations, repairs, constants, params,
bindings, constraints, warnings and meta. All defaults appear in canonical JSON.
Object ids are globally unique across those six drawable collections. Binding
ids have their own unique namespace. Body `on_surface` references a surface;
body `label_ids` reference annotations. Links have endpoints `{ref, point}`,
where `point` is the native attachment coordinate. Forces reference bodies.
Repairs reference a surface or line object and contain native polyline segments.
Constraint and warning refs resolve too.

Annotations carry typed geometry (points, optional bbox/text/radius/arc angles).
M5 recognizes `ground_hatch` as a static annotation, matching the fixed detector
class list. Annotation.type remains an open string; no version/schema shape
changed. Other unknown types retain their warning and simulation guard.
`text_id` references another label annotation, not a separate unlisted OCR store.
`bound_to` is an existing document path. Optional collision `after_velocity`
constraints carry body ids in refs and a body-id-to-Value map (`m/s`); the solver
compares those printed velocities with the calculated outgoing velocities and
emits `after_panel_mismatch` on disagreement.

Meta language is `en` or `bn`; style is printed/handwritten/photo/unknown.
Provenance is extracted/partial/authored/unsupported/demo_fallback. Every M2
fixture is **authored synthetic**, never extracted, gold or a real benchmark.

## Bindings and defaults

Paths address array entries by id, e.g. `bodies.B1.mass`,
`surfaces.S1.angle_deg`, `links.L1.length_m`, `params.launch_speed`. Controls
contain min/max/positive step/unit/locked, labels reference annotations, and
optional handles write to the same Value as the controls.

```json
{"id":"theta","path":"surfaces.S1.angle_deg","class":"geometry",
 "control":{"min":5,"max":75,"step":1,"unit":"deg","locked":true},
 "labels":["param_theta"],"handle":"incline_tip",
 "drives":["layout","solver","label"]}
```

- Physics changes affect the calculation and bound labels, preserving background.
- Initial changes move sprites/annotations; ranges respect the authored scene.
- Geometry starts locked. Unlock permits matched static redraws and marks
  Modified. Back to original restores the source Values, locks and pixels.

Changes create `user`/`user`/confidence=1 Values and recompute the full run in the
browser. Playing restarts at zero and keeps playing. RK4 edits first prepare a
0.25 s preview, then complete the run on the next animation frame; newer edits
invalidate the pending completion. Drag updates are coalesced per frame.

[decisions.md](decisions.md) records numerical priors, calibration, event choices,
render thresholds and bounded resource limits. Defaults only fill absent keys;
they do not replace explicit unresolved or user values.
