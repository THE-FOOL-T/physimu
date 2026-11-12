# V2 detector baseline

Existing user-reviewed 99-image reference; zero exact overlap with 695 recorded prior image hashes; not a style-split gold-netlist benchmark

99 images; inference size 640. AP uses 101-point interpolated precision over IoU .50:.05:.95. Precision/recall use confidence .25.

|Class|Gold|Precision|Recall|AP50|AP50–95|
|---|---:|---:|---:|---:|---:|
|resistor|739|0.9879|0.8809|0.9345472869801448|0.7617114726036369|
|voltage_source|138|0.8583|0.7464|0.8012941485727255|0.5704289816247665|
|capacitor|3|0.0000|0.0000|0.04074638233054075|0.020373191165270376|
|switch|20|0.3333|0.2000|0.22082248278232364|0.1230939382322745|
|ammeter|12|0.0000|0.0000|0.0|0.0|
|voltmeter|4|0.0000|0.0000|0.0|0.0|

Full confusion matrix and metrics: `reference_99_metrics.json`.
