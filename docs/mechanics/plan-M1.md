# M1 plan — domain layer and facades

M0 is complete. This continue authorizes M1 only. No circuit file moves,
pipeline/solver changes, mechanics perception, scene contract, or simulation.

## Implementation

- Add the backend Domain protocol and deterministic registry in `backend/domains/`.
  Circuit calls the existing `analyze_page` in process and adds only `domain`.
  Mechanics returns an unsupported envelope with `reason: not_implemented`,
  the source image, and no solution or demo fallback.
- Add `backend/core/__init__.py` re-exports for config, preprocessing, style,
  regions, text reading, image encoding, and job helpers. Mechanics imports
  shared functionality through this facade exclusively.
- Adapt `backend/app/jobs.py` to retain an immutable stage tuple per job;
  preserve STAGES as the default. Add domain forms and `/api/domains` in main.
  Keep the analysis service's existing circuit warmup, hybrid lock, cancellation,
  fallback, and evidence normalization. Its compatibility entry point must
  continue supporting the imported tests' patched `analysis.analyze_page`.
- Add frontend shell re-exports, a domain registry and mount/unmount interfaces,
  a circuit adapter retaining the existing workspace, and a mechanics placeholder.
  Read all 1,125 lines of main.ts before editing (completed). Add an accessible
  top-bar selector. Pause circuit animation and cancel in-flight uploads when
  inactive; preserve its document/edit state on return, suppress inactive global
  editor shortcuts, and do not create duplicate loops or listeners.
- Add matching `mech.*` EN/BN strings; Bangla remains pending HUMAN review.
  Circuit uploads explicitly send `domain=circuit`; the mechanics placeholder
  does not offer analysis/authoring controls before their scheduled milestones.
- Extend both editable Python package namespace lists for the added subpackages.
  Use the existing TS runner with an additional mechanics test glob.

## Preservation and verification

New Python tests go under `backend/tests/mechanics/`, TS tests under
`frontend/tests/mechanics/`, and browser tests use the existing Playwright setup.
Cover registry replacement/unknown names, direct circuit key preservation,
mechanics unsupported output, API defaults/unknown domains/dispatch, independent
job stages and cancellation, facades, and frontend lifecycle/default selection.

The M0 source-hash guard intentionally froze shared files too. Replace that
blanket policy with an explicit M1 shared-file allowlist; keep every original
test, circuit pipeline/solver, fixture and unrelated asset hash checked. Any
snapshot update must be limited to the 12 existing workspace layout images and
reviewed for the required selector; never change thresholds/assertions. Record
the exact changed shared files and diff sizes in the milestone report.

Run `python manage.py test` before each shared-code commit and at milestone end;
also run `check`, the full browser suite, and focused new domain tests. Retain
raw logs under ignored `.cache/m1-*`. If browser timing summaries overwrite
historical docs, keep the measured copies locally and restore historical files.
Record real counts and failures, review desktop/phone EN/BN screenshots, and
verify the app and actual mechanics API locally without model downloads.

## Assumptions and limits

- The current copied baseline and M0 packaging decisions remain authoritative.
- `GET /api/domains` returns names and stage lists; automatic routing stays
  unimplemented and `auto` receives `unknown_domain`.
- Stage lists contain at least `received` and `done`; other domain stages may
  be skipped by a placeholder, without claiming work was done.
- The additive domain selector requires reviewed visual baseline updates if
  pixels change. Original test source and strict zero tolerance stay intact.
- A retained, hidden/inert circuit workspace is the minimal M1 adapter; actual
  implementation moves wait until M7. Public unmount deactivates it without
  destroying the loaded circuit, images, history or handlers.
- No real-model, mechanics accuracy, physical-device, or Bangla review claim.
  No HUMAN gold scenes, licence decisions, data or weights are created.

Append measured results/assumptions to status.md and stop before M2.
