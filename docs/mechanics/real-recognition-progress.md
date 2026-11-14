# Real mechanics recognition and shared workspace progress

Baseline: clean `main`, `0ff6c8c`. All five implementation commits cited in the
brief are present. The normal `models/mechanics.pt` is absent; the existing
synthetic-only checkpoint is available separately and has not been promoted.

Recovered the exact failed 1024 x 765 pendulum source from the app's retained
mechanics analysis job. It has the 1.2 m, 0.5 kg and 15 degree labels, central
solid bob, two dashed alternative positions and the Simple Pendulum caption.
The recovered raster is a user regression input, not independent evaluation gold.
Its original response is retained in `.cache/real-mechanics-v2/`.

Confirmed root cause: `engine.py` catches unavailable mechanics weights and
returns directly from Detect. OCR, geometry, association, archetype and validation
timings are null. The returned scene has no bodies; later manual authoring can
create `manual_body_1`. The UI also retains the fixture dropdown selection after
upload, although the uploaded document is different.

Verified vertical slice:

- The actual local OCR reads `15°`, `L = 1.2 m`, `m = 0.5 kg` and the caption.
  Strong orientation evidence excludes incompatible rotated readings from binding,
  retaining those raw alternatives for review. Same-orientation conflicts still block.
- Measured support, pivot, radial ink trace and a unique solid bob reconstruct one
  pendulum. Two dashed positions remain alternate-state annotations, not extra bodies.
  Rules and geometry confidence are not calibrated accuracy.
- Actual missing-model analysis produces the supported canonical scene. The existing
  pendulum solver uses the observed mass, length and release angle. An explicit
  angle/pose mismatch warning discloses that the central drawn bob is equilibrium,
  while the printed angle specifies the release state.
- An unmocked Playwright upload of this exact raster passes source pixel identity,
  genuine progress/evidence, scene correspondence, playback, arc radius, dragging,
  mass-to-tension changes, reset and project export/import. Screenshots are retained
  and the ready workspace has been visually inspected.
- Circuit's preview DOM and stepper are shared primitives; Mechanics reuses the
  existing three-column layout and parameter controls. Missing-model/OCR warnings
  remain visible. Upload immediately clears a previous sample selection/document.
- Real runtime Test B and conditional checkpoint Test C passed alongside controlled
  compiler cases (8 tests at that checkpoint). The experimental local 21-class file
  was selected inside the test process only. Normal model configuration is unchanged.

Final verification: 657 Python / one optional skip, 131 TypeScript, lint, formatting
and production build passed. The complete browser gate passed 139 / two optional
skips / zero failures, including all three unmocked upload/recovery/candidate cases
and unchanged Circuit visual/keyboard baselines. The implementation is `e2d2307`.
Broader real-inference probes retain recognition failures, including a wrong-family
synthetic result; the experimental model remains unpromoted. See
[the final report](real-recognition-report.md) for exact evidence, intermediate
failures, commands and remaining recognition limits. Local outputs are retained in
`.cache/real-mechanics-v2/`.
