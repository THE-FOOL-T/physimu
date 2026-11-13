# Mechanics image analysis (M5)

Choose Mechanics and upload PNG, JPEG or WebP. The job reports received,
preprocess, detect, text, geometry, associate, archetype, validate and done. Native
partial boxes and raw text appear while the job runs. Cancel, replacement,
fixture/import, editing or leaving the domain invalidates pending results.
Circuit remains the default domain. `auto` remains an unimplemented interface;
the routes reject it with the existing `unknown_domain` HTTP 400.

The independent checkpoint must have the exact ordered classes in
`data/mechanics_class_schema.yaml`. Supply an approved local file at
`models/mechanics.pt`, or set `MECHANICS_MODEL` to a local `.pt` path. No model
is downloaded by analysis. Do not use circuit weights or promote the M4 one-epoch
smoke as a useful detector. Missing, incompatible or unreadable weights produce
an explicit `weights_unavailable` unsupported scene with its source image.
Fixtures and manual authoring continue to work. Doctor inventories the five
circuit/OCR files; a passing doctor does not validate mechanics weights.

`POST /api/analyze` and `/api/analyze/start` accept `domain=mechanics`; polling
and deletion reuse the existing job routes. The result contains domain,
provenance, scene, reason, source_image, warnings, diagnostics, style_estimate
and timings. It contains no circuit netlist, solution or demonstration.
Unexecuted timings are null. Engine time excludes service-queue time; job elapsed
time includes it. Model inference is cooperatively cancellable before/after the
native call, not interruptible during it.

The source_image is the actual analyzed raster after shared decoding,
orientation, size limiting and preprocessing. All scene coordinates use that
raster. The controller validates its dimensions and replaces the upload preview
before drawing partial boxes. Complete results are schema-validated in Python
and TypeScript. Partial and unsupported results open in edit mode automatically.

The pipeline measures ink lines, circles, masked skeletons, spring coils,
pendulum geometry, trajectory tangents and dimension scale. It extracts native
body polygons and static-line repairs. The label grammar handles SI units,
English/Bangla/subscript digits and raw OCR alternatives; a bare m/M/g is a
name, and an unowned number stays in Unplaced Values. Hungarian assignment is
typed and distance-limited. OCR confidence and geometric rule scores are not
calibrated accuracy estimates. The Bengali unit table and UI need native review.

Printed angles override geometry with an angle_mismatch warning above five
degrees. Candidate contacts within 12 native pixels and alternative link owners
are scored against physical constraints. A masked incline is fitted from all
collinear ink support, so an uninterrupted parallel rope need not replace its
two visible edge pieces. Every alternative is diagnostic evidence, not certainty.
Body box masks, inferred pulley wrapping and unsupported arrangements remain
explicit. Unknown objects are retained for editing and block simulation.

No-archetype results are unsupported with a reason. A recognized arrangement
with invalid physical inputs also remains unsupported and withholds simulation;
its objects/archetype are retained for repair. Supported scenes with priors or
unresolved parts are partial. Extracted requires all required Values to be read
or measured and no unresolved warning. Producing a simulation never establishes
correctness. Use the [authoring guide](authoring.md) to repair the scene.

Limits include one initial figure, one pulley, right-rising inclines, springs
whose support is above/to the left, and the existing eight scalar solver models.
Spring floors are ideal frictionless guides, not continuing contact constraints;
projectile launch surfaces are not continuing contacts. Arbitrary drawn forces
are retained but currently require manual repair to a supported arrangement.
Rope wrapping is inferred and badged. Default scale, rest states, masses and
friction can substantially change the resulting trajectory. A schema-valid
scene is not independent physical validation. Preview masks may degrade frame-0
matching; the existing strict renderer checks and fallback remain unchanged.

Figure splitting uses the shared gutter helper. For two-panel collisions, only
the left panel supplies initial conditions. Readable right-panel body speeds
become after_velocity checks for the existing browser solver. Body mapping is
assumed left-to-right and must be reviewed; this is not identity recognition.
Missing after labels receive collision_check_unmeasured. All source pixels,
detector boxes and panel bounds remain available in the result diagnostics.

To save a correction, check the consent box and press Save correction. The box
starts unchecked and resets on replacement/unmount/save. The endpoint rejects
requests without explicit opt_in and mismatched scene/image dimensions. It
stores native PNG, scene JSON and consent metadata below ignored
`data/corrections/mechanics/`. These are unreviewed corrections, not HUMAN gold.
Nothing is automatically sent to a provider, put in training or persisted by
ordinary upload. This milestone uses local OCR even if label-reader consent is
submitted; provider fallback is later work.

## Reproduce evaluation

With the workspace environment active:

```powershell
python -m pytest backend/tests/mechanics -q
python -m circuit_sim.backend.tests.mechanics.perception_probe
python -m backend.tools.mechanics.eval_end_to_end --out .cache/frozen-end-to-end.json
# From frontend, after npm ci and npm run build:
npx.cmd playwright test browser-tests/mechanics-analysis.spec.ts
```

The probe supplies only detector boxes and actual printed OCR strings from ten
M2 QA fixtures; geometry, association and archetypes execute normally. It is
synthetic, not real accuracy, not held out, and not an evaluation of the model or
OCR. It reports failures and assumptions along with successes. The browser file
starts an isolated loopback API with the same test-owned providers and deliberate
stage delays; no production environment flag or HTTP endpoint enables a stub.

The frozen evaluator requires the M4 HUMAN review/hash contract. Printed and
handwritten partitions are separate, with all metrics null when empty. It
matches scene objects by compatible type/native geometry; IDs have no semantic
meaning. Detector recall uses reviewed YOLO labels at IoU .5 and confidence .25;
missing label support remains null. Scene correspondence permits IoU .2 for
thin measured geometry; point supports must be within 12 px. Attachment accuracy
includes link endpoints and body contact relationships. Parameter correctness
requires exact SI text numbers/units, or geometry angles within three degrees;
missing/assumed Values count as incorrect even when numerically equal. This
strict metric also covers required scale, initial state and physical inputs.

Trajectory evaluation invokes the unchanged TypeScript solvers through pinned
tsx, with 121 equal-time samples over at most five seconds. Compare physical
displacements from each initial position within .05 m, with capped end times
within .02 s. This explicit protocol is separate from simulation_produced. It
does not compare rendered pixels or provide a perceptual accuracy guarantee.
Install the pinned frontend dependencies before evaluating trajectories. Gold
whose own solver fails causes an evaluation error, not a fabricated score.

Current measured gates and limitations are in [status.md](status.md). No reviewed
real set or useful production mechanics checkpoint was created in M5. HUMAN:
independently author/review and freeze real scenes, review real object labels and
licences, run adequate training/evaluation, and review Bangla and real devices.
