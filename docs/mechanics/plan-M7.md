# M7 plan — shared core and circuit ownership (2026-11-13)

The owner explicitly requested M7 after reviewing the copied circuit source and
model locations. Start at `22fc49b`. This is a structural refactor, not a claim
that mechanics recognition is production ready. Reviewed real mechanics data,
real accuracy and model promotion remain unverified. The running synthetic-only
training experiment, its inputs, weights and finalizer must remain usable.

## Scope and assumptions

- Move the existing backend preprocessing, style, OCR infrastructure, config,
  inference settings, jobs and duplicate checking behind `backend/core/`.
  Extract the existing image encoder and bbox matching helpers without changing
  their statements. Preserve inherited OCR vocabulary/filtering; do not attempt
  to improve recognition during this move.
- Move circuit contracts, detector, tracing, value association/resolution,
  validation, analysis and solver implementations into `backend/domains/circuit/`.
  Preserve direct in-process analysis, API response keys and netlist version 1.
- Move circuit frontend solver, renderer, types and circuit editor/controllers
  into `frontend/src/domains/circuit/`; shared DOM, language, upload/workspace,
  storage and image helpers live behind the existing shell facade. Existing
  shell functions that expose circuit types retain those signatures.
- Preserve old Python module paths as aliases to the actual moved module object,
  including private attributes and monkeypatch targets. Frontend compatibility
  modules re-export the moved implementations. There is one implementation of
  each algorithm. Existing tests and cached training scripts keep their paths.
- Mechanics product source and the facade's public exports remain unchanged.
  Keep configuration, environment variables, API credentials, model defaults,
  dependency pins, weights, datasets, fixtures and visual baselines unchanged.
- The brief's stability prerequisite is interpreted as requiring verified
  regression stability for this refactor. The owner's explicit start does not
  establish real-image accuracy. Report the actual gate failures and remaining
  real-data limitations rather than marking recognition stable.

## Move proof and integration

Record every source/destination pair, baseline hash and structural exceptions in
`docs/mechanics/m7-moves.json` and a readable architecture guide. Update package
discovery, API/adapter imports and the independence guard to follow those exact
mappings. The guard must continue protecting imported algorithm statements,
original tests, fixtures and binary assets; no blanket path exemptions.

Use mechanical import rewrites and adjust file-relative resource roots to resolve
the same repository assets. Extracted helpers must retain their original bodies.
Review all differences beyond imports, resource roots and compatibility modules.
Update README and append the architectural decision and milestone status.

## Verification and resource scheduling

Before committing shared changes, run `python manage.py test` successfully.
Measure the same 598 Python passes/one optional skip, 117 TS passes and 124 browser
scenarios collected at M6; any new tests must be separately counted. Retain every
original assertion, timeout, skip policy and the 12 zero-tolerance circuit images.
Run lint/format, type check/build, full browser, doctor, legacy/new package import
identity and source-absent guarded app/test checks. Review actual EN/BN circuit
and mechanics captures. Keep historical timing JSON unchanged.

Do not run memory-heavy Python/model/browser gates concurrently with training.
Use low-memory static verification while it runs and coordinate final gates with
the existing training finalizer/app-restoration watchers. Do not restart training,
install its candidate as the default or interrupt a checkpoint write for this
refactor. If resource scheduling prevents a gate, report it as pending and do not
claim the milestone complete. Record actual commands, counts and limits in status.

Circuit/domain moves and shared integration receive separate small commits;
documentation is separate. Stop after M7 with changed/gates/open-questions report.
