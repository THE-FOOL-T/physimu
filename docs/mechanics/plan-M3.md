# M3 plan — image authoring and mounted workspace

The owner's continue starts M3 only. Preserve all circuit implementations,
original tests, fixtures and strict layout baselines. No mechanics perception,
training, gold annotation or backend analysis is added at this milestone.

## Implementation

- Replace the mechanics placeholder with a retained, memory-only workspace.
  Upload/preview an image, explicitly choose an authored stencil or a synthetic
  fixture, edit in native pixels, validate, run the existing TS solvers and render
  over the source. No stencil is described as extraction. Unsupported stays
  editable. Domain switching pauses work and retains both documents.
- Add mechanics-only authoring, portable-project and history modules. Follow the
  existing canvas editor's draft-on-pointer-down/single-history-entry-on-up and
  bounded undo/redo patterns; do not import its circuit-specific geometry/history.
  Editors cover names/types/Values/boxes, anchors/endpoints, new lines, attachments,
  masks, repairs, unplaced Values and archetype choice. Validation uses parseScene,
  the same generated-schema and semantic validator as the M2 tests.
- Preserve source calibration separately from simulation parameter overrides.
  A portable JSON project contains the canonical source scene, embedded image,
  typed current scene, override map and geometry-unlock state. On import validate
  both scenes, replay bounded overrides and check equality before replacing the
  current workspace. Decode/check the embedded image dimensions. Reject remote
  image references; import/export requires no service or persistent upload.
- Manual stencil geometry is explicitly assumed until positioned by the user.
  Recalibrate source SI coordinates/initial controls after native handle edits;
  keep user-entered physical scale and Values. No image measurements or OCR.
- Add Parameters/Warnings/Readouts/Graphs tabs, provenance/regime/Modified notices,
  sliders, geometry locks/reset, playback, overlay toggles and PNG export.
  Localize new text with matching mech.* EN/BN keys, inherited Bengali font,
  digit switching, keyboard selection, 44px controls and reduced-motion support.

## Shared boundaries and checks

Expected shared changes are matching EN/BN keys and small optional localization
hooks/facade exports if required. Keep shared changes in a separate commit after
manage.py test passes. M1 mechanics-placeholder assertions may be updated to the
mounted workspace while retaining their circuit round-trip and inactivity checks;
no imported baseline test is changed. No circuit screenshots should change.

Add mechanics unit tests for authoring/calibration/history/portable validation and
browser tests against the actual main app for all edit actions, each binding class,
playback, unsupported state, lifecycle, JSON/image round trip, PNG, languages,
reduced motion and accessibility. Run manage.py test/check, the full browser suite
and inspect actual captures. Preserve historical performance JSON after browser
runs. Record measured results and any failures rather than weakening assertions.

There is currently no real mechanics image in the checkout. Ask for a local asset
while implementing; mark a real-image check unverified/skip if none is supplied.
Synthetic uploads test authoring but are never counted as real-image evidence.
No licensing decision or gold scene is made for the owner. Add authoring.md and
manual-qa.md with HUMAN tasks for real gold, Bangla and physical-device review.
Append actual commands/counts/limits/shared diffs to status.md and stop before M4.
