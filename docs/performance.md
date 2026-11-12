# CPU performance measurement

Warm local HTTP analysis of 20 owner seen textbook images. Simulation production is regression coverage, not recognition accuracy. Times include HTTP transfer/decode and a fresh client per request; per-stage pipeline timers exclude upload decode. No external AI reader used.

Median: 9.649 s; p95: 12.258 s; max: 12.737 s; requests >10 s: 8. Startup warm-up: 17.935 s. Pipeline-only median: 9.071 s; p95: 11.434 s.

|Stage|Median seconds|p95 seconds|
|---|---:|---:|
|detect|0.1860|0.4645|
|preprocess|0.0506|0.1162|
|resolve|0.0025|0.0043|
|solve|0.0026|0.0052|
|text|6.3263|8.3941|
|validate|0.0217|0.0478|
|wires|1.7912|3.1368|

|Image|HTTP seconds|Pipeline seconds|Provenance|Degraded|
|---|---:|---:|---|---|
|Screenshot 2026-10-30 232522.png|11.758|10.821|partial|True|
|Screenshot 2026-10-30 232632.png|10.529|9.971|partial|True|
|Screenshot 2026-10-30 232905.png|11.783|11.136|extracted|False|
|Screenshot 2026-10-30 232921.png|12.233|11.395|partial|True|
|Screenshot 2026-10-30 234003.png|10.849|10.265|partial|True|
|Screenshot 2026-10-30 234104.png|9.814|9.175|partial|True|
|Screenshot 2026-10-30 234210.png|6.433|5.880|extracted|False|
|Screenshot 2026-10-30 234420.png|7.537|6.976|partial|True|
|Screenshot 2026-10-30 234517.png|9.825|9.310|partial|True|
|Screenshot 2026-10-30 234541.png|7.530|6.927|extracted|False|
|Screenshot 2026-10-30 234621.png|10.346|9.752|partial|True|
|Screenshot 2026-10-30 234647.png|6.889|6.216|partial|True|
|Screenshot 2026-10-30 234712.png|6.399|5.581|extracted|False|
|Screenshot 2026-10-30 234759.png|12.737|12.179|partial|True|
|Screenshot 2026-10-30 234822.png|9.037|8.138|partial|True|
|Screenshot 2026-10-30 234851.png|10.726|10.061|partial|True|
|Screenshot 2026-10-30 234914.png|8.774|8.124|extracted|False|
|Screenshot 2026-10-30 234939.png|9.484|8.968|extracted|False|
|Screenshot 2026-10-30 235008.png|7.893|7.344|partial|True|
|Screenshot 2026-10-30 235028.png|8.049|7.465|partial|True|

Raw samples: smoke.json; summary: smoke_summary.json. Browser event-to-readout timing (excludes paint) is in performance.json. Full-page small-label OCR remains slower; see ocr_benchmark.md. Optional remote-reader latency is unmeasured.

## Round three interpretation

Measured with six CPU threads, the unchanged v2 weights, local EasyOCR and no
external AI reader. These are the same first 20 sorted owner training/seen images
as the earlier run; not a held-out accuracy set. The new OCR/tracing pipeline is
more expensive: **9.649 s median / 12.258 s p95**, versus round-two 6.407/10.406 s.
The 6 s / 10 s targets are **not met**. Maximum was 12.737 s; 8/20 exceeded 10 s.
Six results were extracted and 14 partial; 20 had simulation responses, and
partial/assumed circuits are not valid recognition successes. Independent
end-to-end accuracy stays null. Warnings include bounded component/retry work;
none of these wall times exceeded the 25-second page allowance.

Cold process readiness: first HTTP 5.172 s; detector plus OCR ready at **22.572 s**
from process launch (server model timer 17.935 s). See startup-round3.json.
The earlier live warmup and the isolated one/six-thread stage comparison are in
[threads-round3.md](threads-round3.md); they do not replace this HTTP sample.
Run `python -m backend.tools.smoke --count 20` after /api/health is ready to
reproduce the current HTTP protocol. It includes a new client and upload/decode.
