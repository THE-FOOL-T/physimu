# V2 detector baseline

Frozen 99 detector test; 1-epoch plumbing smoke only, not a selected model

99 images; inference size 640. AP uses 101-point interpolated precision over IoU .50:.05:.95. Precision/recall use confidence .25.

|Class|Gold|Precision|Recall|AP50|AP50–95|
|---|---:|---:|---:|---:|---:|
|resistor|739|0.9138|0.9323|0.9492124431067093|0.7504101142863038|
|voltage_source|138|0.8837|0.8261|0.8167785080360652|0.5902082812361893|
|capacitor|3|0.0000|0.0000|0.01603017444601603|0.008015087223008015|
|switch|20|0.1290|0.2000|0.20259491845706626|0.10591266881388887|
|ammeter|12|0.0000|0.0000|0.000594059405940594|0.00047524752475247524|
|voltmeter|4|0.0000|0.0000|0.0|0.0|
|rheostat|0|0.0000|0.0000|N/A|N/A|
|potentiometer|0|0.0000|0.0000|N/A|N/A|
|inductor|0|0.0000|0.0000|N/A|N/A|
|battery|0|0.0000|0.0000|N/A|N/A|
|ac_source|0|0.0000|0.0000|N/A|N/A|
|current_source|0|0.0000|0.0000|N/A|N/A|
|ground|0|0.0000|0.0000|N/A|N/A|
|diode|0|0.0000|0.0000|N/A|N/A|
|lamp|0|0.0000|0.0000|N/A|N/A|
|fuse|0|0.0000|0.0000|N/A|N/A|
|galvanometer|0|0.0000|0.0000|N/A|N/A|
|junction|0|0.0000|0.0000|N/A|N/A|
|text_label|0|0.0000|0.0000|N/A|N/A|
|terminal_marker|0|0.0000|0.0000|N/A|N/A|
|plus_minus_mark|0|0.0000|0.0000|N/A|N/A|
|arrow|0|0.0000|0.0000|N/A|N/A|

Full confusion matrix and metrics: `detector_smoke_finetune.json`.
