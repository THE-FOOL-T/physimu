# V2 detector baseline

Frozen 99 detector test; 1-epoch control plumbing smoke only, not a selected model

99 images; inference size 640. AP uses 101-point interpolated precision over IoU .50:.05:.95. Precision/recall use confidence .25.

|Class|Gold|Precision|Recall|AP50|AP50–95|
|---|---:|---:|---:|---:|---:|
|resistor|739|0.0000|0.0000|5.3809728798966854e-05|1.6142918639690056e-05|
|voltage_source|138|0.0000|0.0000|0.004005557276904437|0.0016563351125755646|
|capacitor|3|0.0000|0.0000|0.0|0.0|
|switch|20|0.0000|0.0000|0.0004645228956762759|0.00015467039429126523|
|ammeter|12|0.0000|0.0000|0.0|0.0|
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

Full confusion matrix and metrics: `detector_smoke_control.json`.
