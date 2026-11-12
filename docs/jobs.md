# Analysis jobs (additive API, netlist version 1 unchanged)

`POST /api/analyze/start` accepts multipart `image`, `page` (zero-based),
`problem_text`, `lang`, `style`, and explicit `use_label_reader` (default false).
Returns job_id, width, height and page_count after decode validation.
`GET /api/analyze/{id}` returns real current stage, zero-based stage_index,
stage_count, stage-boundary percent, elapsed_seconds, partial, result and error.
Percent describes stage boundaries, not estimated remaining time. Short stages
can finish between polls. `history` and accumulated `stage_timings` expose them.

Stages: queued, received, preprocess, detect, text, wires, validate, resolve, solve, done.
Retrying topology may revisit stages. Partial components and their source raster
share pixel coordinates. `DELETE` releases the logical slot immediately. Native inference already
running finishes atomically in its bounded worker and checks cancellation before
further work. New work can wait in queued.
Uploads are never written. Default cap: 2 workers, 32 retained results, 900-second
idle TTL. Expired jobs return 404. A full worker pool returns 429/busy.

HTTP errors carry `detail.code` and `detail.message_key`: unsupported_type (415), too_large (413),
undecodable (415), invalid_page (422), busy (429), expired (404).
Job errors include cancelled/server_error. The browser also handles network and
120-second timeout errors and retains the previous simulation.

Every analysis result has provenance: extracted, partial or demo_fallback;
meta.provenance carries the same value. The canonical enum and legacy aliases are documented in schema.md. A demo has an empty netlist image path;
the uploaded preview is separate. `POST /api/analyze` remains synchronous.

## Round three lifecycle and limits

Jobs enter `queued` before `received`; stage_index remains zero while queued,
and history records both. Cancellation releases the logical admission slot
immediately, clears the result/raster references and cancels queued futures.
A native call already running finishes atomically in its bounded worker, then
observes cancellation before further work. New work may wait in `queued` during
that interval. The two-worker limit is never bypassed by spawning extra threads.
Long tile/crop, trace and recovery loops check cancellation.

The synchronous endpoint starts and awaits the same job implementation. Upload
bodies are bounded to 21 MiB including multipart framing (20 MiB image limit),
with a 30-second body-receive limit. Analysis is cooperative: 25 seconds overall,
16 seconds OCR, 5 seconds wires, 3 seconds recovery by default; component OCR
retries have a 1.5-second allowance. An atomic model call can overrun; subsequent
work stops, retains the best available circuit and returns `time_budget`.
Local job starts/status polling share a configurable 600 requests/minute/client
limit; cancellation is always allowed. HTTP errors have detail.code and
message_key. Request/job IDs and exception types are logged without raster data.

The client sends `X-Include-Image: false` after receiving the partial raster,
so later polls omit it; `?include_image=false` is also supported. Finished jobs
omit partial data. Initial results contain their display image once for client
conversion to Blob URLs. Solving/resolving strips image.path. Results retain the
same TTL and correction storage still requires explicit opt-in.
