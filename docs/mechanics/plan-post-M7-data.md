# Post-M7 plan — detector failure audit and next synthetic corpus

The owner's next continue authorizes this bounded follow-up after M7. The
completed 50-epoch checkpoint remains experimental: all three actual public
pipeline trials returned unsupported. This work prepares and measures better
training inputs before another expensive CPU training run. It does not create
an additional numbered milestone from the original M0–M7 brief.

## Evidence and scope

At input size 512, the 600-image R1 corpus has median minimum box sides of
2.28 px for floor, 2.19 px for wall, 1.83 px for ceiling, 3.78 px for pivot,
2.73 px for angle marks and 5.92 px for text. These are geometric size
measurements, not proof that size caused every miss. Inspected public trials
also show letters mistaken for bodies and missing springs/pulleys. Their
unreviewed visual observations are development feedback, never real gold.

- Add a reproducible mechanics-only dataset size audit at an explicit inference
  size, with per-class/split counts and size quantiles. Validate inputs through
  the existing manifest/hash/label contract; do not alter labels or thresholds.
- Extend the synthetic generator/painter with an explicit opt-in `textbook`
  appearance profile. Keep the baseline profile and RNG sequence unchanged.
  Vary paper/ink, filled bodies, pulley rims/spokes, spring coils, support strokes,
  pivot size, labels inside/outside bodies and standalone letter text. Increase
  diagram occupancy. Every target remains an actual authored object extent,
  with matching transformed masks/boxes and no arbitrary box padding.
- Generate a fresh 600-image corpus, seed 73, retaining all eight archetypes,
  the fixed 21-class order, explicit synthetic provenance and source-group
  train/validation isolation. Old datasets/checkpoints/reports remain intact.
- Measure the completed checkpoint on the new synthetic validation split at
  size 512/confidence 0.25 using the unchanged evaluation protocol. Record it as
  a separate challenge baseline, never compare its score directly to the old
  corpus as a training improvement. Prepare a concrete local fine-tune command;
  do not launch another multi-hour training run in this data-preparation step.

## Files and verification

Only mechanics tools/tests and mechanics documentation change. No circuit,
shared core, app default, numerical solver, schema, dependency, weight, source
fixture, browser snapshot or API change is intended. Add alignment,
reproducibility, invalid-profile, meaningful appearance and audit-size tests.
Verify the old baseline's seeded output against pre-change hashes. Run focused
tool tests, Ruff/format, full `manage.py test`, leakage and model doctor. Open
actual new contact sheet and annotated samples; report limitations plainly.

Use sequential CPU workloads and pause/restore only the owned local app if
memory requires it. Run Python/Node external-network guards for gates and model
evaluation. No downloads, external label reader, real-image training or upload.

## Stop point and remaining human work

Append measured outcomes and reproducible paths/commands to status and a data
report, then stop. No detector improvement or promotion is claimed without new
training/evaluation. Real printed/handwritten metrics remain null. Independent
real labels/gold, licensing decisions, native Bangla and device review remain
HUMAN tasks; no automatic output or public preview is designated reviewed gold.

## Visual-QA refinements during preparation

An early partial generation exposed overlapping enlarged Atwood masses and dense
spring coils. Constrain mass width by neighbour distance and coil count by
length/stroke. A second generation completed but was rejected when actual printed
captures exposed overlapping mass labels. Preserve its original manifest under
`manifest.rejected.json`, so the normal training wrapper cannot accept that
folder. Use conservative separated body-label positions and test both geometry
and actual rendered glyph extents over 24 seeds.

The final fresh v3 corpus uses `--handwriting baseline --appearance textbook`.
The lighter pen profile isolates the new shape/label appearance changes; the
strong profile remains available and is exercised by the new alignment tests.
This choice and the rejected development attempts must be disclosed with actual
counts/timings rather than described as a single successful generation.
