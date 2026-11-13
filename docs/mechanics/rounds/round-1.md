# Mechanics round 1

<!-- mechanics-round b915816f197648c0b2f7fead8de9e598 -->

Real evaluation and human review are required; this tool never installs a candidate.

Protocol: image size 512, confidence 0.25, matching IoU 0.50.
Declared target classes: spring, rope.

Pre-label stage: null — HUMAN: supply a source-separated real pool and a local detector.
Merge stage: null — HUMAN: review every label and provide its immutable export/review manifest.

## Real printed

Images: 0. Promotion eligible: False.

| Class | Old recall | New recall | New precision | New AP50 | New AP50:95 |
| --- | ---: | ---: | ---: | ---: | ---: |
| block | null | null | null | null | null |
| ball | null | null | null | null | null |
| bob | null | null | null | null | null |
| cart | null | null | null | null | null |
| incline | null | null | null | null | null |
| floor | null | null | null | null | null |
| wall | null | null | null | null | null |
| ceiling | null | null | null | null | null |
| pivot | null | null | null | null | null |
| ground_hatch | null | null | null | null | null |
| pulley | null | null | null | null | null |
| rope | null | null | null | null | null |
| rod | null | null | null | null | null |
| spring | null | null | null | null | null |
| arrow_force | null | null | null | null | null |
| arrow_velocity | null | null | null | null | null |
| angle_mark | null | null | null | null | null |
| axis | null | null | null | null | null |
| trajectory_arc | null | null | null | null | null |
| dimension_line | null | null | null | null | null |
| text_label | null | null | null | null | null |

- A frozen partition needs at least 20 real images
- Independent frozen real evaluation required; smoke/synthetic cannot be promoted
- No measured recall improvement: rope
- No measured recall improvement: spring

## Real handwritten

Images: 0. Promotion eligible: False.

| Class | Old recall | New recall | New precision | New AP50 | New AP50:95 |
| --- | ---: | ---: | ---: | ---: | ---: |
| block | null | null | null | null | null |
| ball | null | null | null | null | null |
| bob | null | null | null | null | null |
| cart | null | null | null | null | null |
| incline | null | null | null | null | null |
| floor | null | null | null | null | null |
| wall | null | null | null | null | null |
| ceiling | null | null | null | null | null |
| pivot | null | null | null | null | null |
| ground_hatch | null | null | null | null | null |
| pulley | null | null | null | null | null |
| rope | null | null | null | null | null |
| rod | null | null | null | null | null |
| spring | null | null | null | null | null |
| arrow_force | null | null | null | null | null |
| arrow_velocity | null | null | null | null | null |
| angle_mark | null | null | null | null | null |
| axis | null | null | null | null | null |
| trajectory_arc | null | null | null | null | null |
| dimension_line | null | null | null | null | null |
| text_label | null | null | null | null | null |

- A frozen partition needs at least 20 real images
- Independent frozen real evaluation required; smoke/synthetic cannot be promoted
- No measured recall improvement: rope
- No measured recall improvement: spring

Overall promotion eligible: **False**.

HUMAN: independently author/review frozen real scenes/labels, annotate disjoint training data, decide licences, run adequate retraining and review Bangla/devices. Missing metrics are null; synthetic scores cannot satisfy promotion.
