# Detector data inventory

Seen 59 and frozen 99 counts reuse their recorded reviewed annotation audits. Generated and AITEE counts are read from local labels by this script.

|Class|Seen 59|Frozen 99|Synthetic 24|AITEE 828|
|---|---:|---:|---:|---:|
|resistor|203|739|9|2146|
|voltage_source|72|138|34|4583|
|capacitor|4|3|12|0|
|switch|3|20|13|0|
|rheostat|0|0|15|0|
|potentiometer|0|0|15|0|
|inductor|0|0|13|0|
|battery|0|0|14|0|
|ac_source|0|0|15|0|
|current_source|0|0|13|294|
|ground|0|0|24|0|
|diode|0|0|10|0|
|lamp|0|0|8|0|
|fuse|0|0|8|0|
|ammeter|0|12|7|0|
|voltmeter|0|4|7|0|
|galvanometer|0|0|8|0|
|junction|0|0|116|0|
|text_label|0|0|201|3941|
|terminal_marker|0|0|96|0|
|plus_minus_mark|0|0|24|0|
|arrow|0|0|24|1261|

All rare classes remain starved of reviewed real data, especially capacitor, switch and all meters. Synthetic coverage is not evidence of real recall. The frozen 99 test images never enter training or validation. AITEE ambiguous P/V classes are dropped pending taxonomy review; pseudo-label additions are unreviewed and excluded from training.

Run: `python -m backend.tools.data_inventory`. Licenses/access and maps: `dataset_sources.md`.
