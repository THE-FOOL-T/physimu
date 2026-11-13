# Application source layout

Circuit and mechanics are local source plugins in one Python backend and one
frontend bundle. Circuit analysis is a direct function call. The browser calls
this application's own API; no original-project server or checkout is required.

```text
backend/
  app/                       HTTP routes, warmup, limits, service orchestration
  core/                      config, preprocessing, style, OCR, jobs, matching
    ocr_hybrid/              existing local OCR engines and worker lifecycle
  domains/
    circuit/                 detector, netlist v1, engine, wires, resolve, validate
      solver/                existing MNA and flow implementation
    mechanics/               scene, perception, labels, validation, regimes
  tools/                     existing circuit/shared CLIs and mechanics tools
frontend/src/
  main.ts                    existing application initialization and integration
  shell/                     upload, workspace, DOM, language, storage and styles
  shared/sim/                clock, graphs, parameters and coordinate helpers
  domains/
    circuit/
      types.ts               existing circuit document and result types
      solver/                existing browser solver and explanations
      overlay/               existing circuit renderer, labels and flow
      ui/                    circuit editor, state, parameters and inspectors
    mechanics/               archetypes, solvers, renderer, editing and upload
```

Start with `backend/domains/circuit/adapter.py` for circuit dispatch,
`backend/domains/circuit/engine.py` for image analysis,
`backend/domains/circuit/detect.py` for the YOLO wrapper, and
`backend/domains/circuit/solver/mna.py` for the circuit solver. The circuit model
remains the ignored `models/v2_original.pt`; configuration and credentials retain
their previous names and values. Mechanics has a separate model setting and
does not train from or overwrite the circuit checkpoint.

Mechanics continues importing shared backend functionality through
`backend/core/__init__.py` and frontend functionality through
`frontend/src/shell/index.ts` (or the pure simulation facade). These public
exports are unchanged. Shared bbox matching and image encoding were extracted
with their existing function bodies. The inherited shared OCR still contains
electrical vocabulary and filtering for circuit compatibility; moving it does
not broaden its recognition capability. Mechanics retains its separate grammar
and opt-in crop policy. Generalizing the inherited OCR policy is outside M7.

The shell's existing upload/workspace/image helpers retain their circuit-facing
types and behavior; this move does not redesign their API. The application's
existing initialization remains in `main.ts`. Translation JSON, fonts, demos,
fixtures, data and models retain their paths, preserving bookmarks, tests,
configuration and the running synthetic training experiment.

## Compatibility and review

Old Python paths such as `backend.pipeline.detect`, `backend.config`,
`backend.app.jobs` and `backend.solver.mna` are small compatibility aliases to the
actual moved modules. Attributes, caches and monkeypatches share the same module
object within each package namespace. Compatibility package directories retain
their own namespaces so their submodule aliases load correctly. `augphys` and
the existing local `circuit_sim` compatibility namespace both work from this
checkout. No external package or source path is consulted.

Old TypeScript module paths re-export their moved implementation. These exports
preserve live language bindings and let original tests keep their imports. HTML
and CSS moved directly into the shell, with application imports updated.

The [complete move manifest](mechanics/m7-moves.json) lists every source and
destination, before-move hash and implementation fingerprint. Run
`python tools/check_m7_moves.py` to check implementation structure, unchanged
extracted helper bodies and repository resource roots without loading a model.
The independence suite follows these mappings; original tests and assets retain
their exact hash checks. Fingerprints tolerate imports, formatting and the
recorded resource depth adjustments, not changed algorithm statements.

M7's [plan](mechanics/plan-M7.md) and [status](mechanics/status.md) distinguish
executed gates from queued checks. File organization does not establish real
mechanics accuracy, HUMAN review or model promotion.

## Complete M7 implementation move list

Old Python/TypeScript paths below retain compatibility modules. These are logical
implementation moves; Git may display an added implementation and a shortened old
module instead of a rename because the alias is retained.

| Previous implementation | Current implementation |
| --- | --- |
| `backend/pipeline/annotations.py` | `backend/domains/circuit/annotations.py` |
| `backend/pipeline/associate.py` | `backend/domains/circuit/associate.py` |
| `backend/pipeline/budget.py` | `backend/core/budget.py` |
| `backend/pipeline/detect.py` | `backend/domains/circuit/detect.py` |
| `backend/pipeline/engine.py` | `backend/domains/circuit/engine.py` |
| `backend/pipeline/image_edges.py` | `backend/domains/circuit/image_edges.py` |
| `backend/pipeline/label_assignment.py` | `backend/domains/circuit/label_assignment.py` |
| `backend/pipeline/label_reader.py` | `backend/core/ocr_label_reader.py` |
| `backend/pipeline/netlist.py` | `backend/domains/circuit/netlist.py` |
| `backend/pipeline/ocr_hybrid/__init__.py` | `backend/core/ocr_hybrid/__init__.py` |
| `backend/pipeline/ocr_hybrid/bangla_adapter.py` | `backend/core/ocr_hybrid/bangla_adapter.py` |
| `backend/pipeline/ocr_hybrid/normalize.py` | `backend/core/ocr_hybrid/normalize.py` |
| `backend/pipeline/ocr_hybrid/rapidocr_adapter.py` | `backend/core/ocr_hybrid/rapidocr_adapter.py` |
| `backend/pipeline/ocr_hybrid/router.py` | `backend/core/ocr_hybrid/router.py` |
| `backend/pipeline/ocr_hybrid/symbols.py` | `backend/core/ocr_hybrid/symbols.py` |
| `backend/pipeline/ocr_hybrid/worker.py` | `backend/core/ocr_hybrid/worker.py` |
| `backend/pipeline/ocr_regions.py` | `backend/core/ocr_regions.py` |
| `backend/pipeline/ocr_tiles.py` | `backend/core/ocr_tiles.py` |
| `backend/pipeline/orientation.py` | `backend/domains/circuit/orientation.py` |
| `backend/pipeline/preprocess.py` | `backend/core/preprocess.py` |
| `backend/pipeline/resolve.py` | `backend/domains/circuit/resolve.py` |
| `backend/pipeline/retry.py` | `backend/domains/circuit/retry.py` |
| `backend/pipeline/style.py` | `backend/core/style.py` |
| `backend/pipeline/tesseract_regions.py` | `backend/core/tesseract_regions.py` |
| `backend/pipeline/text.py` | `backend/core/text.py` |
| `backend/pipeline/validate.py` | `backend/domains/circuit/validate.py` |
| `backend/pipeline/value_tokens.py` | `backend/core/value_tokens.py` |
| `backend/pipeline/values.py` | `backend/domains/circuit/values.py` |
| `backend/pipeline/warnings.py` | `backend/domains/circuit/warnings.py` |
| `backend/pipeline/wire_geometry.py` | `backend/domains/circuit/wire_geometry.py` |
| `backend/pipeline/wire_repair.py` | `backend/domains/circuit/wire_repair.py` |
| `backend/pipeline/wires.py` | `backend/domains/circuit/wires.py` |
| `backend/config.py` | `backend/core/config.py` |
| `backend/inference.py` | `backend/core/inference.py` |
| `backend/app/jobs.py` | `backend/core/jobs.py` |
| `backend/tools/leakage.py` | `backend/core/leakage.py` |
| `backend/solver/__init__.py` | `backend/domains/circuit/solver/__init__.py` |
| `backend/solver/flow.py` | `backend/domains/circuit/solver/flow.py` |
| `backend/solver/mna.py` | `backend/domains/circuit/solver/mna.py` |
| `frontend/src/ui/canvas-editor.ts` | `frontend/src/domains/circuit/ui/canvas-editor.ts` |
| `frontend/src/ui/dom.ts` | `frontend/src/shell/dom.ts` |
| `frontend/src/ui/edit-geometry.ts` | `frontend/src/domains/circuit/ui/edit-geometry.ts` |
| `frontend/src/ui/edit-history.ts` | `frontend/src/domains/circuit/ui/edit-history.ts` |
| `frontend/src/ui/editor.ts` | `frontend/src/domains/circuit/ui/editor.ts` |
| `frontend/src/ui/explain.ts` | `frontend/src/domains/circuit/ui/explain.ts` |
| `frontend/src/ui/filenames.ts` | `frontend/src/shell/filenames.ts` |
| `frontend/src/ui/flow-controls.ts` | `frontend/src/domains/circuit/ui/flow-controls.ts` |
| `frontend/src/ui/icons.ts` | `frontend/src/domains/circuit/ui/icons.ts` |
| `frontend/src/ui/image-store.ts` | `frontend/src/shell/image-store.ts` |
| `frontend/src/ui/parameters.ts` | `frontend/src/domains/circuit/ui/parameters.ts` |
| `frontend/src/ui/part-popover.ts` | `frontend/src/domains/circuit/ui/part-popover.ts` |
| `frontend/src/ui/precheck.ts` | `frontend/src/domains/circuit/ui/precheck.ts` |
| `frontend/src/ui/readiness.ts` | `frontend/src/shell/readiness.ts` |
| `frontend/src/ui/readouts.ts` | `frontend/src/domains/circuit/ui/readouts.ts` |
| `frontend/src/ui/shell.html` | `frontend/src/shell/shell.html` |
| `frontend/src/ui/state.ts` | `frontend/src/domains/circuit/ui/state.ts` |
| `frontend/src/ui/storage.ts` | `frontend/src/shell/storage.ts` |
| `frontend/src/ui/text-inspector.ts` | `frontend/src/domains/circuit/ui/text-inspector.ts` |
| `frontend/src/ui/topology.ts` | `frontend/src/domains/circuit/ui/topology.ts` |
| `frontend/src/ui/trace-issues.ts` | `frontend/src/domains/circuit/ui/trace-issues.ts` |
| `frontend/src/ui/translation.ts` | `frontend/src/shell/translation.ts` |
| `frontend/src/ui/upload.ts` | `frontend/src/shell/upload.ts` |
| `frontend/src/ui/warnings.ts` | `frontend/src/domains/circuit/ui/warnings.ts` |
| `frontend/src/ui/workspace.ts` | `frontend/src/shell/workspace.ts` |
| `frontend/src/overlay/flow.ts` | `frontend/src/domains/circuit/overlay/flow.ts` |
| `frontend/src/overlay/labels.ts` | `frontend/src/domains/circuit/overlay/labels.ts` |
| `frontend/src/overlay/renderer.ts` | `frontend/src/domains/circuit/overlay/renderer.ts` |
| `frontend/src/overlay/text-evidence.ts` | `frontend/src/domains/circuit/overlay/text-evidence.ts` |
| `frontend/src/overlay/view.ts` | `frontend/src/domains/circuit/overlay/view.ts` |
| `frontend/src/solver/explain.ts` | `frontend/src/domains/circuit/solver/explain.ts` |
| `frontend/src/solver/flow.ts` | `frontend/src/domains/circuit/solver/flow.ts` |
| `frontend/src/solver/mna.ts` | `frontend/src/domains/circuit/solver/mna.ts` |
| `frontend/src/solver/resolve.ts` | `frontend/src/domains/circuit/solver/resolve.ts` |
| `frontend/src/types.ts` | `frontend/src/domains/circuit/types.ts` |
| `frontend/src/i18n/index.ts` | `frontend/src/shell/language.ts` |
| `frontend/src/style.css` | `frontend/src/shell/style.css` |
| `frontend/src/workspace.css` | `frontend/src/shell/workspace.css` |
