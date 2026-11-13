# Mechanics handwriting and photographs

M6 adds bounded handwriting fit settings and a stronger synthetic profile.
Automatic style selection still reuses the untrained shared image-statistics
heuristic, whose 0.55 confidence is a policy value. It is not measured style
accuracy. Use the mechanics style selector for the next upload when Auto chooses
poorly. Handwritten results show a persistent notice that editing is expected.
Real printed/handwritten accuracy remains null without independently reviewed data.

## Perception

Shared preprocessing handles illumination, estimated page perspective and faint
notebook ruling. Its returned raster remains the coordinate/image reference.
Mechanics does not change the circuit preprocessor or style estimator.

Printed geometry keeps its existing thresholds. Handwritten fitting uses a
7-pixel line-support band and 20-pixel line-gap limit instead of 3.5/12; the circle
outlier floor is 4.5 instead of 2.5 pixels. Spring traces close only small gaps
and smooth the transverse profile before coil counting. Fits retain residual
evidence and can still fail. Handwritten body outlines use a size-bounded closing
kernel of at most seven pixels, then the existing contour-area check. Large open
outlines remain unmeasured/editable. Repaired masks have lower policy confidence;
no measured probability or real-image improvement is implied.

## Stronger synthetic profile

Choose a **new** output directory; the active training dataset is immutable:

```powershell
.\.venv\Scripts\python.exe -m backend.tools.mechanics.make_synthetic --out "$PWD\data\generated_mechanics\handwriting-new" --count 600 --seed 73 --handwriting strong
```

The baseline profile remains the default for existing reproducible tools. Strong
handwriting adds stronger pen jitter/wobble and stroke-width variation, explicit
drawn Latin digit/symbol paths, locally jittered/rotated unit/Bangla font glyphs,
smooth elastic deformation, notebook ruling/shadows and optional phone perspective.
Bangla glyph styling uses the local Noto font; it is not genuine handwriting data.

The same homography and smooth displacement deform image pixels, every object
mask and native scene coordinates. Long polylines are densified before warping.
The recorded displacement parameters have an iterative inverse for resampling;
detector boxes come from the transformed amodal object masks, while indexed masks
retain visible topmost ownership. Ruling/shadows are unlabelled backgrounds.
These projective/deformed auxiliary scenes are supervision, not calibrated solver
benchmarks. Real data and frozen gold are never synthesized from them.

An actual 64-image `--small` QA corpus was generated at
`data/generated_mechanics/m6-handwriting-20261113-v1/`, with 51 train/13 validation,
19 printed/13 scan/19 simulated handwritten/13 simulated photo images. Its contact
sheet was opened. This corpus is not another training run or a new production
dataset. The original 600-image v4 training inputs remain unchanged.

## Optional cropped-label fallback

Off by default. The checkbox permits **only ambiguous label crops** to be sent
to **Google Gemini for the next upload**; it resets after that request and on
domain unmount. Selecting Handwritten alone never enables external calls.
Server configuration requires separate `MECHANICS_LABEL_API_KEY` and
`MECHANICS_LABEL_MODEL` environment variables. The model identifier must be
valid for the owner's account. No keys are accepted from or stored in the browser,
and existing circuit credentials/configuration are unchanged.

The generic transport sits behind the core facade and uses Google's documented
[generateContent interface](https://ai.google.dev/api/generate-content), inline
PNG crops and an API-key header. No real provider call was executed for M6.
Transport tests use httpx MockTransport and synthetic crops only.

After local OCR, the gate selects ambiguous text detections/OCR regions, skips
clear valid local readings, deduplicates overlapping crops and considers at most
eight. Crops are at most 640×160 pixels and 20% of the native raster each; whole
diagrams are rejected. No scene, problem text or full image is sent. An additional
eight-second cooperative budget is checked between crops; each request receives
the remaining timeout. [HTTPX timeouts](https://www.python-httpx.org/advanced/timeouts/)
apply to connection/read/write/pool phases rather than a strict total wall clock,
so an in-flight call can exceed that budget. Cancellation is checked between calls.
No real-provider latency bound was verified.

Only a short transcription matching the local mechanics grammar is accepted;
prose, circuit values, nonfinite quantities and untyped bare numbers are rejected.
Provider boxes/source/confidence are ignored. The server maps the crop, marks
source `vlm` and caps confidence at 0.65 (policy, not measured reliability).
Ambiguous local text is retained with the proposal as an alternative. Missing
configuration, failure or rejected text leaves local evidence editable and warns.
Existing generation cancellation prevents late analysis from replacing user edits.

## Synthetic evidence and limits

The ten strongly pen-rendered fixture cases use oracle boxes and raw authored
text, not a finished scene. They measure geometry/association/archetype behavior,
not detector/OCR accuracy or independent generalization. Archetypes and attachments
match in all ten cases; only **20/157 required parameters** and **2/10 trajectories**
match the strict evaluator. The unchanged printed probe remains **21/157** and
**2/10**. Missing/unplaced values and assumed scale/initial conditions still limit
physics correctness. Producing a trajectory is recorded separately.

For six controlled wobbling lines, maximum angle error is **0.07880°**, maximum
length error **2.05446 px**. The wobbled circle has centre error **0.05718 px** and
radius error **0.11376 px**. The test spring has ten measured/true coils and
**6.08277 px** endpoint errors. These are synthetic measurements, not real errors.
Raw reports/protocols are in `.cache/m6/{handwritten,printed}-probe.json`; tests and
the probe are tracked. CPU timings were measured with background training active
and do not establish model/HTTP latency or frame-rate targets.

See [round tooling](rounds.md) for real-data evaluation and promotion. HUMAN tasks:
annotate disjoint real training data, independently author/review frozen printed
and handwritten scenes, decide licences, retrain/evaluate adequately, review
Bangla and test real devices/novices. No automated output is approved as gold.
