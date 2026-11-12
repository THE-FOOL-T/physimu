# Bangla release review — HUMAN task

All strings in `frontend/src/i18n/bn.json` are unreviewed drafts, including the
electrical explanation templates, warnings and controls. The interface shows
this notice when Bangla is selected. They are not owner-approved translations.

Review technical terms, grammar, named placeholders, numerals and font shaping
on canvas and in tables. Confirm switch terminology (open/closed), electrical
power sign explanations, source short and assumption notices. Record the owner,
date and approved keys here before release. Key and placeholder parity are
automatically tested, but semantic quality requires human review.
# Round 2 additions — unreviewed

All `upload.*`, `provenance.*`, `error.*` and `stage.*` translations added for
receipt, progress, cancellation, result summaries and errors are draft Bangla.
An owner review is required; no linguistic approval is claimed.

WP2 `ui.*` and `model.*` text (theme, editor badge, advanced controls, keyboard
help, confidence, tooltips and model readiness) is also unreviewed.

WP5 `ui.explain`, unknown-block strings, `explain.scope/complex/reduction/kind.*/
using/charge` and `constraint.*` are unreviewed, along with the pre-existing
explanation templates now exercised by the Explain tab.

WP6 `style.*`, `reader.*`, ruling/perspective/junction and label-reader warnings
are draft Bangla, including the privacy disclosure. They need human review.


WP8 coordinate labels and accessible names (`ui.x/y/number/switch_language/
first_node/second_node/analysis_mode/direction`) are also unreviewed. Final
browser checks cover receipt, validation, server/network errors and retry in
both languages; these checks establish wiring and parity, not translation quality.

WP8 short tab labels (`ui.tab_readouts/tab_selected/tab_graph`) are draft Bangla
and require the same human terminology review.

Round-three WP-A `ocr.*`, `error.crop_too_large` and the `unit_inferred`,
`value_not_found`, OCR stage/recovery/time-budget warnings are draft Bangla.
EN/BN key and placeholder parity passes; both text correction dialogs were
opened and visually inspected. No linguistic approval is claimed.

WP-B `trace.fix` and source-open-loop, not-connected, off-axis, same-group,
bypass, missing-part and solve-failed notices are also unreviewed Bangla.

WP-C `edit.*`, `type.ground`, the Fix circuit/Finish editing/checklist wording,
tool instructions, assistant, pre-check, popover and live announcements are
unreviewed Bangla. Sixteen EN/BN tool/popover states were visually inspected;
parity passes. This does not establish terminology or linguistic approval.

WP-D `layout.*`, `warn.image_edge_cut` and `edit.ready_draft` are unreviewed
Bangla. The import strip, four tabs, label modes, zoom hint and possible-cropping
notice are wired in both languages; matching keys/placeholders are tested.


WP-E `flow.*` labels, presets and state descriptions are unreviewed Bangla.
Parity passes and both-language layouts were visually inspected. The color
names and charge/current terminology still need a human language review.


WP-F queued-analysis, rate-limit/invalid-request errors and grouped-warning count
strings are draft Bangla. Matching keys/placeholders pass; no human approval.


WP-G model-ready/warming/text-reader-unavailable text is unreviewed Bangla.
The chip now describes both local models; EN/BN parity remains required.


WP-H preserves literal UTF-8 micro-unit symbols and Bangla digits, with regression
checks. Both-language screenshots were visually rechecked after that repair.
All translations remain drafts; font rendering and key parity do not establish
linguistic or electrical terminology approval.
