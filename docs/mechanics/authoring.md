# Mechanics scene authoring

Choose **Mechanics** in the main app. This workspace runs locally in browser
memory. Upload a PNG/JPEG/WebP for local analysis. In **Explore**, select a body
and drag its physical handle, or edit the contextual numerical controls. Dragging
pauses playback and edits initial conditions; it does not move source geometry.
Arrow keys adjust the selected body; Shift increases the step. Drag empty canvas
space to pan, choose a zoom level, or use Reset view. Reset rewinds playback;
Back to original parameters clears simulation overrides.

Use **Fix interpretation** for OCR text/units, label ownership, contact and endpoint
corrections, and alternative figure/physics interpretations. Confident conflicting
OCR readings stay unplaced. Explicit Confirm this value buttons mark accepted
assumptions as user values. A valid schema alone does not establish supported
physics or accurate recognition; readiness and warning panels distinguish these.

Use **Advanced authoring** to choose an archetype and **Place authoring template**,
draw missing objects/links and repair masks. Templates propose editable handles
and assumed Values; they do not inspect the image. Synthetic fixtures are labelled.

Position each body box/mask, pivot, pulley centre, incline base/tip and link end
over its actual source pixels. Select objects from the list or click their
handles. Drag a handle, enter native-pixel coordinates, or focus the canvas and
use arrow keys (two pixels per key). A pointer drag is one undo transaction.
Delete template objects absent from the source. Deleted attachment targets leave
explicit fixed anchors so references remain valid. Undo/Redo retains 80 actions;
it keeps scene/parameter state, with the source image stored once outside history.

Use Rope/Spring/Incline/Floor for two-click lines. Attach rope/spring ends with
their A/B selectors. A mask requires at least three clicks and **Finish shape**;
the polygon field also accepts native coordinate pairs. Select a surface/link to
draw repair segments or edit its segment array. Set paper/ink colours and stroke
width from the source. These tools change the authored graph; the original image
remains available. Escape cancels an unfinished shape.

Enter mass, length, gravity, damping, friction and initial conditions in SI units
(angles in degrees). No number is inferred from the diagram. Scale is a physical
Value in px/m. Manual pendulum/incline/spring handle changes recalibrate the source
initial coordinates against that scale; they do not measure a real length from
pixels. Added unplaced Values are visible chips: set their number/unit, then
assign a matching typed target. Source edits mark provenance **authored**.

**Run** validates the canonical scene and references using the same `parseScene`
validator used by tests, then prepares the existing TypeScript solver/renderer.
A valid schema can still describe unsupported physics: that distinction appears
in validation and warnings. Unknown types and incomplete/invalid physical inputs
retain the source and editing controls. Choosing Unsupported retains the graph.
Frame-zero composition is measured against the actual image. A mismatch keeps
the original with motion overlays and an explicit warning; it is not a claim of
successful extraction. Edit masks/repairs/style to improve it.

Simulation controls use the shared fixed-step clock. Physics and initial sliders
preserve source calibration; geometry sliders start locked and show Modified
after unlocking/changing. Lock again to prevent further slider changes. **Back to
original parameters** restores the current authored source, including its original
Values and locks. Source edits use Undo/Redo. No state autoplays, including under
reduced motion; explicit Play remains available, alongside Step and the path.

## Portable scene and image JSON

Export produces a version-2 `augphys-mechanics-project` envelope. Canonical scenes
remain version 1; the project wrapper records an additional immutable snapshot:

- `scene`: canonical source scene with native geometry and source calibration.
- `current_scene`: canonical typed Values after simulation parameter changes.
- `recognition_scene`: first recognition/authored-load snapshot, retained through
  geometry corrections, history, replay and reanalysis. Restore first interpretation
  explicitly returns to it; ordinary Reset does not discard corrections.
- `source_image`: embedded PNG/JPEG/WebP data URL; no remote image dependency.
- `parameter_overrides`: SI numbers addressed by existing binding paths.
- `unlocked_geometry`: geometry binding ids; version and format identify the file.

Import validates both scenes against the generated M2 schema plus semantic
references/units, replays bounded overrides, compares the resulting typed scene,
and decodes/checks the embedded image dimensions before installation. Invalid
imports leave the current document intact. This separation prevents saved geometry
overrides from accidentally becoming a new source calibration. JSON key ordering
does not matter. Direct raw scene JSON must first be packaged with its matching
image and replayed state; arbitrary remote paths are not fetched.

Version-1 projects are accepted and explicitly migrated: their source scene becomes
the initial recognition snapshot. Missing pulley displacement, collision position
and pendulum angular-speed controls are added consistently to both snapshots.
Old scalar-system velocity bindings, labels and saved overrides migrate to the
solver parameter path. Conflicting saved corrections stay unplaced for review.
Native geometry remains unchanged. New exports require a version-2-capable reader.

A pendulum speed observed in m/s derives angular speed through the calibrated
length. This conversion is assumed until reviewed. Editing length retains that
observed linear speed; explicitly editing angular speed, or correcting its bound
label, takes ownership of the angular Value instead.
Bound linear-speed labels continue to display m/s using the current length.
An explicit angular reading takes priority over a conflicting linear reading;
the conflicting observation remains unplaced.

Reanalyze image reuses the embedded local image and never runs during a parameter
drag. User Values follow unique native object matches, not incidental detector IDs;
unmatched corrections remain unplaced for reassignment. A manually authored/repaired
interpretation is retained intact and the new alternatives are available for review.
Reanalysis retains history and cannot overwrite edits made after its request began.

Images are limited to 32 MB, 8000 px per side and 16 megapixels. PNG export is the
current composed canvas (including enabled overlays/edit handles). No video export,
server upload, persistent corrections or automatic annotation is added in M3.
Switching domains pauses Mechanics and retains both documents; reload requires
importing the exported project.

## Human gold authoring

HUMAN: obtain/approve the source and its licence, record origin and image hash,
author every object/mask/attachment/Value with evidence, and independently review
the graph, frame-zero composition and physical answer before designating gold.
Keep unreviewed templates marked assumed; a browser-valid document is not gold.
The public-diagram QA projects made by Codex stay in ignored cache and are never
used as frozen gold, train/validation data or recognition-accuracy evidence.
Have a Bengali-speaking reviewer check translations and a person test touch and
keyboard interactions on physical devices. See [manual-qa.md](manual-qa.md).
