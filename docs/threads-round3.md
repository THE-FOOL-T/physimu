# Inference thread comparison (round three WP-F)

Windows CPU, 12 logical processors; three warmed runs on the bundled printed
mixed network, sequential processes with the API server stopped. No other
model workload ran during this final comparison. This is a small stage profile,
not a 20-image HTTP latency measurement or proof of general speedup.

|Threads|Model initialization seconds|Detector median seconds|OCR median seconds|
|---|---:|---:|---:|
|1|18.633|0.078|7.553|
|6|16.011|0.086|7.065|

The six-thread default improved OCR slightly in this sample; detector medians
are close. All runs returned 38 readings and a component/retry time-budget
warning. Quality was not hand-scored, and earlier round-two timings used a
different OCR pipeline. Raw rows are threads-one.json and threads-half.json.
The live server warmup observed separately was 18.568 seconds.

Reproduce in separate processes (set CIRCUIT_THREADS in your shell):
`python -m backend.tools.thread_profile --out docs/threads-one.json --count 3`
with CIRCUIT_THREADS=1; repeat with CIRCUIT_THREADS=6 and the other output path.
`inference.threads: null` defaults to max(1, cpu_count // 2); CIRCUIT_THREADS or
an explicit config value overrides it. No model downloads occur on requests.
