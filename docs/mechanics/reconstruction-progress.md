# Mechanics reconstruction — 2026-11-14

Starting branch: `main`; starting commit: `b0e94bfc7f3e6fbb77986a5c994448b92898d71d`.
The working tree was clean. Existing fixture assets, solvers, circuit APIs and v1
scene/project formats are retained.

## Architecture and verified defects

| Area                                           | Existing responsibility                                                        | Change needed                                                                                |
| ---------------------------------------------- | ------------------------------------------------------------------------------ | -------------------------------------------------------------------------------------------- |
| `engine.py`                                    | Local model lease, staged progress, detection/OCR/measurement orchestration    | Retain stage/job contract; expose typed evidence and readiness                               |
| `detect.py`, `config.py`                       | Independent 21-class local checkpoint validation                               | Retain missing/incompatible-model behavior; no download or promotion                         |
| `geometry.py`, `sprites.py`, `perception.py`   | Native geometry, masks, attachment guesses, calibration and binding generation | Keep measurements; make relationship uncertainty explicit; compile canonical parameter paths |
| `labels.py`, `label_reader.py`, `associate.py` | Mechanics grammar, consented fallback, global typed ownership                  | Keep circuit OCR untouched; resolve conflicting readings and solver ownership                |
| `archetypes.py`, `validate.py`                 | Topology rules, attachment alternatives, plausibility                          | Rank evidence/contradictions, expose ambiguity and repair requirements                       |
| `scene.py`, `defaults.py`, `corrections.py`    | Pydantic v1 contract, defaults, opt-in storage                                 | Keep public schema and compatibility                                                         |
| `archetypes/*.ts`                              | Existing analytic/RK4 solvers                                                  | Preserve equations; accept bounded initial displacement/position overrides                   |
| `bindings.ts`, `layout.ts`                     | Value overrides, constraints, native source-to-state projection                | Complete physical handles; fix authoritative parameter propagation                           |
| `authoring.ts`, `project.ts`, `validate.ts`    | Explicit geometry editing, history, strict portable v1 validation              | Preserve authoring and transaction semantics; migrate legacy controls explicitly             |
| `workspace.ts`                                 | Upload/jobs, all UI, playback, geometry pointer events                         | Extract physics interaction, inspector/mode composition and transaction handling             |
| `renderer.ts`, `sampling.ts`                   | Source layers, first-frame checks, state sampling                              | Cache source layers; approximate moving outlines when extraction is unreliable               |
| shared core/shell/circuit                      | OCR execution, image/model/jobs; shared clock/graphs/tokens; circuit UI        | Use existing interfaces and regression tests                                                 |

Reproduced from code and tests: normal canvas pointer-down returns unless authoring
is active; drag support stops at four archetypes; collision ignores position
overrides; pulley motion always starts at zero displacement. OCR speed is initially
owned by body velocity while projectile uses a copied launch speed; its label stays
on the unused path. Incline/spring/pulley initial speed does not consume that body
velocity. Renderer layers are rebuilt on every parameter transaction. Partial
recognition automatically opens the full geometry editor.

## Baseline

- `npm test`: **117 passed**.
- Initial `manage.py test` exited during optional OCR/parser initialization with
  `Error importing generated parsers`; a second full run is being recorded in
  `.cache/mechanics-baseline-test.log`. Collection succeeds: 608 tests.
- Mounted ten-fixture browser baseline is being recorded in
  `.cache/mechanics-baseline-browser.log`.
- Existing local app responds on port 8000; circuit detector and hybrid OCR ready.
  The configured production mechanics checkpoint remains absent. Experimental
  synthetic weights are not selected or promoted.

## Sequence

1. Canonical parameter ownership and regression tests.
2. Constrained Explore interactions and transaction/cancellation tests.
3. Explore / Fix Interpretation / Advanced Authoring composition and inspector.
4. Source-layer caching, fallback and link/label validation.
5. Typed recognition evidence, relationships, hypotheses and readiness.
6. Upload/review/project integration and stale-response protection.
7. Full Python/TypeScript/build/browser gates and inspected screenshots.

Results and remaining limitations will be updated as each gate runs. Controlled
detections and OCR test pipeline integration; they are not real recognition scores.

## Implemented increments

- Phase 1: canonical OCR speed ownership and linked annotations; launch-angle and
  pendulum damping extraction; signed velocity handling; conflict/ambiguous-owner
  rejection; unitless dimensional values remain unplaced. Pulley initial
  displacement and collision initial positions now reach existing solvers.
- Phase 2: a separate physics interaction controller handles selection, native
  transforms, pointer capture, constrained previews, cancellation and keyboard
  changes. Ten mounted-fixture interaction cases plus cancellation/zoom passed.
- Phase 3: Explore, Fix interpretation and Advanced authoring; canvas-first panels,
  contextual component parameters/labels, shared design tokens, accessible controls,
  retained geometry tools and project lifecycle. Authoring fields, DOM helpers,
  mode composition, interaction and readouts are separate modules.
- Phase 4: renderer source layers are reused for parameter changes; readout nodes
  are reused during playback. Textured backgrounds/poor masks use visible moving
  outlines on the intact source. Corrected bound labels redraw from their Values.
- Phase 5: typed evidence/relationship graph, topology hypotheses with contradictions,
  readiness issues, native coarse figure proposals and explicit panel selection.
  Mechanics fuses the shared OCR engines' raw readings with its own semantics.
  Endpoint evidence must actually reach body boundaries before a link is assembled.
- Phase 6: upload/reanalysis, correction preservation through unique object matching,
  unmatched user values retained for reassignment, project v2 immutable recognition
  snapshot, strict v1 migration, review selectors and local-only model behavior.

## Gates so far

- Full baseline rerun: **607 Python passed, 1 skipped**, **117 TS passed**, build
  passed. Mounted ten-fixture baseline plus existing binding case: **11 passed**.
- Parameter regression gate: **67 Python passed** including existing perception
  tests; **123 TS passed** after initial-state controls were added.
- Evidence/recognition gate: **93 Python passed**; current frontend **126 passed**.
- First complete integration browser pass: **39 passed, 2 failed** because two old
  authoring scenarios selected the archetype after returning to Explore. Those
  scenarios now explicitly open Fix interpretation. No assertion was removed.
- First full check: lint and formatting passed; **643 Python passed, 1 skipped,
  1 failed**. The failure was the deliberate native-panel API extension tripping
  M7's exact main.py fingerprint. The shared analysis coordinator was restored
  unchanged; a mechanics request adapter isolates the option. The main.py record
  now pins the exact new structure and retains its prior fingerprint/history.
  The unchanged independence assertions subsequently passed **8 tests**.
- Model doctor: all five bundled circuit/OCR hashes pass. Normal app was restarted
  with local configuration and ready circuit/hybrid OCR; no model was downloaded.

Final clean full gates, real local candidate observations and screenshot inspection
will be recorded in the implementation report. Intermediate failed commands are
retained under `.cache/mechanics-*.log` rather than reported as successful gates.

## Completion validation

The latest `manage.py check` completed with **649 Python passed, 1 skipped**,
**130 TS passed**, Ruff/Prettier and production build passed. Log:
`.cache/mechanics-final-check.log`. Backend checkpoints: `d00ee00`, `8c5a937`.
Frontend state/bindings: `07ea711`; workspace integration: `252a7b7` on `main`.
Final browser interception ordering fix: `4109f4a`.
The shared circuit analysis coordinator/core/domain implementations remain unchanged.
The final workspace also extracts image/project/analysis lifecycle into `session.ts`.

A complete browser run passed **135, skipped 2** before the last velocity migration
and pendulum conversion changes. The new mounted legacy-pendulum case also passed;
it verifies the new angular control, linear-speed preservation through length
edits, explicit angular ownership and portable replay. The latest full browser
verification completed sequentially after the final build: **136 passed, 2 skipped,
zero failed**, in **5.3 minutes** (`.cache/mechanics-final-browser-verified.log`). A prior targeted run's
404 was caused by concurrent static-output replacement, not suppressed or relabelled
as a successful test.

The first full browser run on the final code passed **135, skipped 2, failed 1**:
the unchanged circuit keyboard/file-chooser test timed out awaiting its event.
Three isolated repetitions passed, but a second full run and the 13-test layout
sequence reproduced the same failure. Event logging confirmed trusted Enter and
an upload-input click with user activation. Registering file-chooser interception
before navigation then passed **all 13 layout tests**, retaining all original
actions/assertions. No circuit application code changed. The fix is `4109f4a`.
The final full rerun passed **136 tests, 2 skipped**, including keyboard upload
after all layout cases. Failed full/diagnostic logs remain retained
and are not counted as passing gates. Trace-heavy diagnostics were stopped after
timeouts and are also excluded from passing evidence.

The final ownership audit exposed the old pendulum fixture's missing angular-speed
binding. Migration now adds it. The first derived-speed TS test failed at that
missing control; all **130 TS tests** pass after fixing the migration. Explicit
angular/linear conflicts retain unplaced observations; unknown angular values do
not crash conversion. The app was restarted with the final backend and reports
detector/OCR **ready/ready**, both hybrid OCR engines ready, startup **25.572 s**.

The final guarded experimental-model probe executed actual inference and hybrid
OCR on three existing public images: **5 Atwood, 8 spring and 11 incline candidate
detections**; **all three unsupported**. It sent zero external crops. Default
mechanics weights remain absent; automatic real recognition is not complete.
Final observation times were **27.40 / 16.25 / 36.81 s**, including setup and
concurrent verification, not a controlled benchmark. The failed unguarded launcher
attempt is retained separately and excluded from these observations.
