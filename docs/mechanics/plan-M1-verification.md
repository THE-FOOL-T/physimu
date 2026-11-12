# M1 follow-up plan — real-model parity and switch check

The owner's continue resumes the held M1 verification. It does not start M2.
Preserve the current status-file follow-up and all historical measurements.

- Inspect the exact response difference and unchanged OCR implementation.
  Check model/pipeline hashes and whether the Bengali readings form identical
  prefixes when its existing wall-clock work limit stops a request.
- Repeat the first image in the original app to test its own reproducibility;
  compare three real images sequentially through both local APIs. Keep raw
  responses/differences and distinguish full-response parity from netlist,
  solver, warning and source-image parity. Timing fields and the new domain
  field are the only exclusions for full-response comparison.
- If default limits prevent a reproducible diagnosis, run a clearly labelled
  controlled diagnostic with identical, generous in-memory budgets in separate
  processes. Do not change either checkout's config, deadlines, OCR algorithm,
  model, source files or expected results to force a match.
- Retry the Circuit/Mechanics switch using available computer-use/browser tools.
  Observe both states and return to Circuit. If the safety/browser capability
  still blocks input, stop UI actions and report the exact limitation.
- Run the existing test suite if code changes become necessary; do not change
  circuit pipeline logic as part of this verification. Record actual commands,
  counts, limitations and any unresolved parity issue in status.md.

New evidence/harnesses and private real images/results stay under ignored
`.cache/model-verification/`. No weights or datasets enter Git. The original
checkout stays clean. Temporary source-server processes are stopped afterwards;
the new app may remain available on loopback for the owner.

Assumption: bounded diagnostic repetition is authorized by continue after the
first mismatch was explicitly reported. Repetition must explain variability,
not hide a failing default comparison. Stop before M2 and wait for the next
instruction after reporting this follow-up.
