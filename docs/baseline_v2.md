# V2 detector baseline

seen-image regression; NOT held out

59 images; inference size 640. AP uses 101-point interpolated precision over IoU .50:.05:.95. Precision/recall use confidence .25.

|Class|Gold|Precision|Recall|AP50|AP50–95|
|---|---:|---:|---:|---:|---:|
|resistor|203|0.9848|0.9557|0.9696631248490702|0.7493513528115112|
|voltage_source|72|0.9718|0.9583|0.9667641878386543|0.7134596594155818|
|capacitor|4|0.8000|1.0000|1.0|0.4508250825082508|
|switch|3|0.0000|0.0000|0.0|0.0|

Full confusion matrix and metrics: `baseline_v2.json`.

The requested independent printed/handwritten baseline remains blocked on HUMAN-labeled, disjoint held-out sets. These values must not be used for model selection.
