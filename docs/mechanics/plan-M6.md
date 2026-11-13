# M6 plan — repeatable rounds and handwriting (2026-11-13)

The owner authorized M6 implementation while the synthetic-only 600-image CPU
training continues. Start at `3a85da8`. Preserve that process, its v4 dataset,
checkpoints and finalizer. Do not start another training job or select its
unfinished candidate as the app default. M7 is outside this milestone.

## Real-data loop

- Add round.py with init/prelabel/merge/evaluate phases, immutable declared target
  classes and one protocol for both model versions. Reuse proposals, the HUMAN
  review importer, frozen integrity/leakage checks and per-class promotion rules.
- Merge only reviewed real labels with explicitly synthetic records. Bound the
  synthetic/real image exposure ratio separately in train/validation, retain
  source groups, original hashes and per-image provenance. No resampling or
  copying frozen scenes. Teach dataset validation about this explicit mixed
  origin; it never treats a mixed score as independent real accuracy.
- Print the exact fine-tune command; execution retains the existing real-gold
  training gate. Evaluate old/new frozen printed and handwritten partitions at
  identical size/confidence and reject common-class regressions. Decisions do
  not install weights. Persist stage state and docs/mechanics/rounds/round-<n>.md
  with measured values or null/HUMAN notes. Actual reviewed real data is absent.

## Handwriting and label fallback

- Add an explicit stronger synthetic handwriting profile without changing the
  baseline painter defaults or any existing generated dataset. Include variable
  strokes/wobble, drawn digits/symbols, elastic warping, ruling, shadows and photo
  perspective. Apply identical spatial transforms to raster, masks and scene
  geometry; derive detector boxes from transformed object masks. Record transforms.
- Keep printed measurement thresholds unchanged. Pass the effective handwritten
  style into line/circle/spring fitting and body mask closing, with bounded gap
  repair and fit evidence. Reuse core preprocessing/style for photos.
- Add a generic cropped-label transport behind the core facade and a mechanics
  crop/vocabulary gate. Off by default; require request consent and separate
  mechanics environment credentials. Only ambiguous bounded label crops leave
  the server; no whole diagram, problem text or scene. Validate provider text,
  ignore provider coordinates, cap confidence and preserve local/user evidence.
  Mock provider tests only; no real external request is authorized here.
- Add matching EN/BN consent disclosure, style override and handwriting editing
  notice to the mechanics workspace. Circuit controllers/layout remain unchanged.

## Verification and stop point

Test round provenance/caps/leakage and rejected promotions on TEST fixtures;
generator determinism and pixel/annotation alignment; jittered fits with actual
pixel/degree errors; masks with small/large gaps; consent/crop/grammar/failure/
cancellation behavior. Run a synthetic handwritten detector-stub end-to-end set
and retain M5 printed failures as disclosed regression evidence, not real accuracy.
Exercise the new UI/browser paths, full manage.py test/check, independence and
unchanged circuit snapshots. Avoid concurrent heavy gates where host memory is
tight. Record actual timings with training contention disclosed. Shared facade
and translation changes get a separate commit after a passing full test.

Real printed/handwritten accuracy, useful production detector quality, HUMAN
review, licences, GPU retraining and native Bangla/device approval remain
unverified unless evidence is actually supplied. Document null round results and
the HUMAN tasks; never author or approve real gold. Stop before M7.
