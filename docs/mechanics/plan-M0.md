# M0 plan — import and prove a standalone circuit baseline

Date: 2026-11-12 (Asia/Dhaka). Scope: M0 only; no domain layer or mechanics code.

## Source and decisions

Use the clean local main inspected during reconnaissance, commit
`97702f2bbfd42f15f434b0acffdc1fc4bc678400`. Record the original URL, local source
path, comparison with `516e232`, exclusions, and all changes in `docs/IMPORT.md`.
The user's continue authorizes progressing with the following explicit
interpretations of the reported conflicts:

- The brief's no-weights rule takes precedence over upstream's new Git LFS
  distribution exception. Do not copy the five tracked weights or any ignored
  source state. Ignore all weight formats and private/local configuration.
- Preserve current hybrid OCR, relative example model paths, two inference
  threads, dependency pins, circuit algorithms, fixtures, response keys, and
  saved version-1 documents. Missing models must remain explicit.
- Keep tracked generated demos, visual snapshots, fonts, and documentation
  assets, since excluding these would change the baseline app and checks.
- Keep all historical documentation files. Consolidate upstream checkout URLs
  and absolute source-checkout references in `docs/IMPORT.md`, replacing their
  former locations with local import-note references or neutral historical
  placeholders. Historical results remain historical.
- Use `augphys` as the distribution/public package name, retaining a local
  `circuit_sim` compatibility import for unchanged baseline tests and tools.
  Both resolve to source in this checkout; no upstream package is installed.
- Adapt only setup/package/documentation boundaries so a source-only checkout
  can install and start without weights. Doctor remains a strict optional model
  inventory; setup/start must not require it to pass.

## Work and files

1. Copy the Git-tracked baseline files, excluding weights. Preserve their bytes
   and record a hash inventory. Initialize a new repository with no remote.
2. Create an independent local Python environment and npm installation. Reuse
   installed system Python dependencies where compatible; install missing pinned
   dependencies into this workspace. Do not reuse the source venv/node_modules
   or install/import the source repository.
3. Run the copied baseline tests before package/setup changes and commit the
   import. Package/setup/shared-file changes get a separate tested commit.
4. Adjust `pyproject.toml`, `bootstrap.py`, root package metadata, frontend
   package metadata if needed, `.gitignore`, `.gitattributes`, `setup.ps1`,
   `run.ps1`, README, and relevant setup/import documentation. Do not change
   `backend/pipeline`, `backend/solver`, frontend circuit logic, or imported tests.
5. Add `backend/tests/test_independence.py` for source-contained imports,
   configuration/private-state exclusions, upstream-reference and remote checks,
   and circuit analysis transport boundaries. Add a reproducible offline/isolation
   verification helper if required, outside product execution paths.
6. Temporarily make the original checkout absent for the final gates, using
   checked absolute paths and a finally block to restore it. Apply process-level
   guards against external network connections to Python and Node. Allow only
   loopback where required for the local app/browser checks. Report the guard's
   exact scope, rather than claiming the operating system network was disabled.
7. Run the full test/check/browser gates, serve the built app at
   `http://127.0.0.1:8000`, verify missing-model analysis and health, and audit
   imported file hashes. Never regenerate visual baselines to hide a failure.
8. Write actual commands/counts/failures/limits and assumptions to
   `docs/mechanics/status.md`; update import/decision records; commit and stop.

## Gates and evidence

- `python manage.py test`: pytest, original frontend tests, type checking/build.
  Historical latest expectation is 397 Python passed + 1 skipped and 82 frontend
  passed; measure before/after and attribute added independence tests separately.
- `python manage.py check`: existing Ruff checks/format, Prettier, suite/build.
- `python manage.py browser`: existing Playwright, installed Edge when available;
  report actual totals and strict-layout outcomes, including intermittent failures.
- New independence tests and Git/file audit: no upstream remote, `.gitmodules`,
  outside-source imports, external circuit service, weights/private state in Git.
- Original checkout absent + guarded external network: test/check and app serve;
  missing weights explicitly reported; source restored unchanged afterwards.
- No claim of recognition accuracy, full training, GPU results, Linux/macOS
  verification, native Bangla review, or real-device QA.
