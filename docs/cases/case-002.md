# Case 002: Screenshot 2026-10-30 232905.png

SHA-256: `de5707fd01baa68a1d593cca8b37cda8d11fa53952fd1394bb2184877b12734a`. Read-only configured owner input; raster excluded from Git.

The source visibly says 24 V; it is now assigned 24 V. The visible 5k, 10k, 6k, 3k and 2k labels are assigned. R5 (8k in the drawing) remains unread. Detector order IDs differ from printed R2/R4 labels; use the boxes and label field, not IDs alone.

Inspected annotated image: `.cache/round3/case-002.png` (local only).

Both engine paths were requested. Tesseract is not installed on this machine; there are no real Tesseract readings to report. EasyOCR EN/BN uses installed local models. Dual-engine selection is tested with mocks, not claimed as a local Tesseract benchmark.

## Frozen round-two evidence

The trace below records actual Hungarian selections (including recovery attempts). A selected candidate does not necessarily survive the final netlist. The old API did not retain every rejected pair; unselected candidates are reported as such rather than inventing a rejection distance.

|Raw text|Native box|Old parse|Actual selection (role, part, cost / dummy)|
|---|---|---|---|
|" R1"|[161.0,0.0,194.0,17.0]|{"label":"R1","number":null,"unit":null,"confidence":0.6,"internal":false,"unknown":false}|[{"role":"name","component":"R1","cost":26.055217788884445,"dummy_cost":229.7585105895996}]|
|" 5 kQ"|[154.0,11.0,202.0,34.0]|{"label":null,"number":5000.0,"unit":"ohm","confidence":0.85,"internal":false,"unknown":false}|[{"role":"value","component":"R1","cost":14.638120366615372,"dummy_cost":229.7585105895996}]|
|"W"|[144.0,29.0,213.0,64.0]|null|"not parseable"|
|"7"|[254.0,37.0,279.0,57.0]|{"label":null,"number":7.0,"unit":null,"confidence":0.55,"internal":false,"unknown":false,"has_prefix":false}|"not selected; rejection pairs not retained"|
|"C"|[35.0,40.0,55.0,55.0]|null|"not parseable"|
|"fvs"|[13.0,169.0,98.0,206.0]|null|"not parseable"|
|"28"|[247.0,169.0,331.0,233.0]|{"label":null,"number":28.0,"unit":null,"confidence":0.55,"internal":false,"unknown":false,"has_prefix":false}|[{"role":"value","component":"R4","cost":13.489368296359952,"dummy_cost":231.20013427734375}]|
|"7724v"|[13.0,199.0,110.0,223.0]|null|"not parseable"|
|"~R6"|[161.0,305.0,195.0,327.0]|{"label":"R6","number":null,"unit":null,"confidence":0.6,"internal":false,"unknown":false}|[{"role":"name","component":"R6","cost":32.77721926704868,"dummy_cost":214.88186645507812}]|
|"2ko"|[154.0,321.0,202.0,344.0]|{"label":null,"number":2000.0,"unit":"ohm","confidence":0.85,"internal":false,"unknown":false}|[{"role":"value","component":"R6","cost":14.144249453376077,"dummy_cost":214.88186645507812}]|
|"7"|[254.0,347.0,279.0,366.0]|{"label":null,"number":7.0,"unit":null,"confidence":0.55,"internal":false,"unknown":false,"has_prefix":false}|"not selected; rejection pairs not retained"|
|"AL "|[36.0,349.0,56.0,364.0]|null|"not parseable"|

## Current raw engine readings

|Engine / rotation|Raw text|Native box|Current parse in anchored context|
|---|---|---|---|
|"easyocr-crop / 0"|"R1"|[161.0,0.0,194.0,17.0]|{"label":"R1","number":null,"unit":null,"confidence":0.6,"internal":false,"unknown":false,"emf_symbol":false,"unit_inferred":false,"normalized":"","normalizations":[]}|
|"easyocr / 0"|" 5 kQ"|[154.0,11.0,202.0,34.0]|{"label":null,"number":5000.0,"unit":"ohm","internal":false,"unknown":false,"has_prefix":true,"unit_inferred":false,"confidence":0.85,"emf_symbol":false,"normalized":"5kΩ","normalizations":[]}|
|"easyocr / 0"|"1"|[199.0,30.0,213.0,52.0]|{"label":null,"number":1.0,"unit":"ohm","internal":false,"unknown":false,"has_prefix":false,"unit_inferred":true,"confidence":0.6,"emf_symbol":false,"normalized":"1","normalizations":["component_unit"]}|
|"easyocr / 0"|"M"|[152.0,33.0,203.0,59.0]|null|
|"easyocr / 0"|"T"|[144.0,41.0,156.0,61.0]|null|
|"easyocr / 0"|"CJ"|[405.0,103.0,430.0,113.0]|null|
|"easyocr-crop / -90"|"W"|[519.0,108.0,544.0,160.0]|null|
|"easyocr-crop / -90"|"W"|[408.0,109.0,433.0,160.0]|null|
|"easyocr / 0"|"'R3"|[429.0,115.0,465.0,139.0]|{"label":"R3","number":null,"unit":null,"confidence":0.6,"internal":false,"unknown":false,"emf_symbol":false,"unit_inferred":false,"normalized":"'","normalizations":[]}|
|"easyocr-crop / 0"|"\"R4"|[540.0,115.0,575.0,139.0]|{"label":"R4","number":null,"unit":null,"confidence":0.6,"internal":false,"unknown":false,"emf_symbol":false,"unit_inferred":false,"normalized":"\"","normalizations":[]}|
|"easyocr / 0"|"\"6 ko"|[429.0,132.0,474.0,156.0]|{"label":null,"number":6000.0,"unit":"ohm","internal":false,"unknown":false,"has_prefix":true,"unit_inferred":false,"confidence":0.85,"emf_symbol":false,"normalized":"\"6kΩ","normalizations":[]}|
|"easyocr / 0"|"\"3 ko"|[540.0,132.0,586.0,156.0]|{"label":null,"number":3000.0,"unit":"ohm","internal":false,"unknown":false,"has_prefix":true,"unit_inferred":false,"confidence":0.85,"emf_symbol":false,"normalized":"\"3kΩ","normalizations":[]}|
|"easyocr / 0"|">"|[429.0,148.0,442.0,164.0]|null|
|"easyocr / 0"|">"|[540.0,148.0,552.0,164.0]|null|
|"easyocr / 0"|"3n"|[414.0,156.0,442.0,166.0]|{"label":null,"number":3.0000000000000004e-09,"unit":"ohm","internal":false,"unknown":false,"has_prefix":true,"unit_inferred":true,"confidence":0.6,"emf_symbol":false,"normalized":"3n","normalizations":["component_unit"]}|
|"easyocr / 0"|"S"|[522.0,156.0,552.0,167.0]|null|
|"easyocr-crop / 0"|"+"|[13.0,169.0,91.0,190.0]|null|
|"easyocr-crop / 90"|"A"|[253.0,175.0,279.0,226.0]|null|
|"easyocr / 0"|"\"Vs"|[65.0,181.0,98.0,206.0]|null|
|"easyocr / 0"|"'R2"|[275.0,182.0,310.0,206.0]|{"label":"R2","number":null,"unit":null,"confidence":0.6,"internal":false,"unknown":false,"emf_symbol":false,"unit_inferred":false,"normalized":"'","normalizations":[]}|
|"easyocr / 0"|"2e"|[20.0,186.0,69.0,196.0]|null|
|"easyocr / 0"|"S"|[25.0,190.0,66.0,205.0]|null|
|"easyocr / 0"|"\"10 ko"|[275.0,198.0,320.0,223.0]|{"label":null,"number":10000.0,"unit":"ohm","internal":false,"unknown":false,"has_prefix":true,"unit_inferred":false,"confidence":0.85,"emf_symbol":false,"normalized":"\"10kΩ","normalizations":[]}|
|"easyocr / 0"|"\"24V"|[65.0,199.0,109.0,223.0]|{"label":null,"number":24.0,"unit":"V","internal":false,"unknown":false,"has_prefix":false,"unit_inferred":false,"confidence":0.85,"emf_symbol":false,"normalized":"\"24V","normalizations":[]}|
|"easyocr / 0"|">"|[275.0,215.0,287.0,230.0]|null|
|"easyocr / 0"|"55"|[409.0,216.0,452.0,232.0]|{"label":null,"number":55.0,"unit":null,"internal":false,"unknown":false,"has_prefix":false,"unit_inferred":false,"confidence":0.55,"emf_symbol":false,"normalized":"55","normalizations":[]}|
|"easyocr / 0"|"C"|[260.0,222.0,287.0,233.0]|null|
|"easyocr-crop / 0"|"e"|[401.0,262.0,413.0,277.0]|null|
|"easyocr / 0"|"2"|[409.0,264.0,434.0,316.0]|{"label":null,"number":2.0,"unit":"ohm","internal":false,"unknown":false,"has_prefix":false,"unit_inferred":true,"confidence":0.6,"emf_symbol":false,"normalized":"2","normalizations":["component_unit"]}|
|"easyocr / 0"|"'Rs"|[430.0,270.0,465.0,294.0]|null|
|"easyocr / 0"|"a"|[402.0,279.0,413.0,294.0]|null|
|"easyocr / 0"|"4a"|[402.0,295.0,413.0,310.0]|{"label":null,"number":4.0,"unit":"A","internal":false,"unknown":false,"has_prefix":false,"unit_inferred":false,"confidence":0.85,"emf_symbol":false,"normalized":"4a","normalizations":[]}|
|"easyocr / 0"|">"|[430.0,304.0,442.0,319.0]|null|
|"easyocr-crop / 0"|"R6"|[161.0,305.0,195.0,327.0]|{"label":"R6","number":null,"unit":null,"confidence":0.6,"internal":false,"unknown":false,"emf_symbol":false,"unit_inferred":false,"normalized":"","normalizations":[]}|
|"easyocr / 0"|"2ko"|[154.0,321.0,202.0,344.0]|{"label":null,"number":2000.0,"unit":"ohm","internal":false,"unknown":false,"has_prefix":true,"unit_inferred":false,"confidence":0.85,"emf_symbol":false,"normalized":"2kΩ","normalizations":[]}|
|"easyocr / 0"|"1"|[198.0,340.0,212.0,362.0]|{"label":null,"number":1.0,"unit":"ohm","internal":false,"unknown":false,"has_prefix":false,"unit_inferred":true,"confidence":0.6,"emf_symbol":false,"normalized":"1","normalizations":["component_unit"]}|
|"easyocr / 0"|"AN"|[152.0,344.0,202.0,366.0]|null|
|"easyocr / 0"|"P"|[144.0,353.0,156.0,366.0]|null|

## Current association decisions

Every tested component/role pair includes its measured distance and rejection reason. `weak_context` covers a body/lead overlap, low confidence, contradictory bare readings or insufficient anchored support; it is deliberately conservative.

```json
[
  {
    "text": "R1",
    "bbox": [
      161.0,
      0.0,
      194.0,
      17.0
    ],
    "confidence": 0.9350263065581252,
    "component_id": "R1",
    "context": "resistor",
    "engine": "easyocr-crop",
    "rotation": 0,
    "wire_overlap": false,
    "alternatives": [
      {
        "text": " R1",
        "bbox": [
          161.0,
          0.0,
          194.0,
          17.0
        ],
        "confidence": 0.8905524550253185,
        "engine": "easyocr",
        "rotation": 0
      },
      {
        "text": "~R1",
        "bbox": [
          161.0,
          0.0,
          194.0,
          17.0
        ],
        "confidence": 0.27061673972479977,
        "engine": "easyocr-crop",
        "rotation": 0
      },
      {
        "text": "~R1",
        "bbox": [
          161.0,
          0.0,
          194.0,
          17.0
        ],
        "confidence": 0.1739760383873906,
        "engine": "easyocr-crop",
        "rotation": 0
      }
    ],
    "id": "t1",
    "raw": "R1",
    "parsed": {
      "label": "R1",
      "number": null,
      "unit": null,
      "confidence": 0.6,
      "internal": false,
      "unknown": false,
      "emf_symbol": false,
      "unit_inferred": false,
      "normalized": "",
      "normalizations": []
    },
    "assignments": [
      {
        "component_id": "R1",
        "role": "name",
        "parsed": {
          "label": "R1",
          "number": null,
          "unit": null,
          "confidence": 0.6,
          "internal": false,
          "unknown": false,
          "emf_symbol": false,
          "unit_inferred": false,
          "normalized": "",
          "normalizations": []
        }
      }
    ],
    "outcome": "assigned",
    "reason": "assigned",
    "candidates": [
      {
        "component_id": "R1",
        "role": "name",
        "distance": 25.32,
        "reason": "eligible"
      },
      {
        "component_id": "R2",
        "role": "name",
        "distance": 356.58,
        "reason": "too_far"
      },
      {
        "component_id": "R3",
        "role": "name",
        "distance": 252.46,
        "reason": "too_far"
      },
      {
        "component_id": "R4",
        "role": "name",
        "distance": 183.6,
        "reason": "too_far"
      },
      {
        "component_id": "V1",
        "role": "name",
        "distance": 207.9,
        "reason": "too_far"
      },
      {
        "component_id": "R5",
        "role": "name",
        "distance": 345.02,
        "reason": "too_far"
      },
      {
        "component_id": "R6",
        "role": "name",
        "distance": 335.9,
        "reason": "too_far"
      }
    ],
    "assigned_to": "R1",
    "role": "name"
  },
  {
    "text": " 5 kQ",
    "bbox": [
      154.0,
      11.0,
      202.0,
      34.0
    ],
    "confidence": 0.3572108541263147,
    "component_id": "R1",
    "context": "resistor",
    "engine": "easyocr",
    "rotation": 0,
    "wire_overlap": false,
    "id": "t2",
    "raw": " 5 kQ",
    "parsed": {
      "label": null,
      "number": 5000.0,
      "unit": "ohm",
      "internal": false,
      "unknown": false,
      "has_prefix": true,
      "unit_inferred": false,
      "confidence": 0.85,
      "emf_symbol": false,
      "normalized": "5kΩ",
      "normalizations": []
    },
    "assignments": [
      {
        "component_id": "R1",
        "role": "value",
        "parsed": {
          "label": null,
          "number": 5000.0,
          "unit": "ohm",
          "internal": false,
          "unknown": false,
          "has_prefix": true,
          "unit_inferred": false,
          "confidence": 0.85,
          "emf_symbol": false,
          "normalized": "5kΩ",
          "normalizations": []
        }
      }
    ],
    "outcome": "assigned",
    "reason": "assigned",
    "candidates": [
      {
        "component_id": "R1",
        "role": "value",
        "distance": 11.32,
        "reason": "eligible"
      },
      {
        "component_id": "R2",
        "role": "value",
        "distance": 352.41,
        "reason": "too_far"
      },
      {
        "component_id": "R3",
        "role": "value",
        "distance": 246.73,
        "reason": "too_far"
      },
      {
        "component_id": "R4",
        "role": "value",
        "distance": 170.74,
        "reason": "too_far"
      },
      {
        "component_id": "V1",
        "role": "value",
        "distance": 196.33,
        "reason": "too_far"
      },
      {
        "component_id": "R5",
        "role": "value",
        "distance": 334.43,
        "reason": "too_far"
      },
      {
        "component_id": "R6",
        "role": "value",
        "distance": 321.9,
        "reason": "too_far"
      }
    ],
    "assigned_to": "R1",
    "role": "value"
  },
  {
    "text": "1",
    "bbox": [
      199.0,
      30.0,
      213.0,
      52.0
    ],
    "confidence": 0.15233309409224205,
    "component_id": "R1",
    "context": "resistor",
    "engine": "easyocr",
    "rotation": 0,
    "wire_overlap": true,
    "alternatives": [
      {
        "text": "T",
        "bbox": [
          199.0,
          30.0,
          213.0,
          52.0
        ],
        "confidence": 0.08030142156833708,
        "engine": "easyocr-crop",
        "rotation": 90
      },
      {
        "text": "U",
        "bbox": [
          199.0,
          30.0,
          213.0,
          52.0
        ],
        "confidence": 0.023262723413503217,
        "engine": "easyocr-crop",
        "rotation": -90
      },
      {
        "text": "p",
        "bbox": [
          199.0,
          30.0,
          213.0,
          52.0
        ],
        "confidence": 0.022647832371497367,
        "engine": "easyocr-crop",
        "rotation": 90
      },
      {
        "text": "",
        "bbox": [
          199.0,
          30.0,
          213.0,
          52.0
        ],
        "confidence": 0.0,
        "engine": "easyocr-crop",
        "rotation": 90
      }
    ],
    "id": "t3",
    "raw": "1",
    "parsed": {
      "label": null,
      "number": 1.0,
      "unit": null,
      "internal": false,
      "unknown": false,
      "has_prefix": false,
      "unit_inferred": false,
      "confidence": 0.55,
      "emf_symbol": false,
      "normalized": "1",
      "normalizations": []
    },
    "assignments": [],
    "outcome": "unassigned",
    "reason": "too_far",
    "candidates": [
      {
        "component_id": "R1",
        "role": "value",
        "distance": 2.65,
        "reason": "weak_context"
      },
      {
        "component_id": "R2",
        "role": "value",
        "distance": 320.92,
        "reason": "too_far"
      },
      {
        "component_id": "R3",
        "role": "value",
        "distance": 214.14,
        "reason": "too_far"
      },
      {
        "component_id": "R4",
        "role": "value",
        "distance": 142.73,
        "reason": "too_far"
      },
      {
        "component_id": "V1",
        "role": "value",
        "distance": 199.14,
        "reason": "too_far"
      },
      {
        "component_id": "R5",
        "role": "value",
        "distance": 301.8,
        "reason": "too_far"
      },
      {
        "component_id": "R6",
        "role": "value",
        "distance": 303.41,
        "reason": "too_far"
      }
    ]
  },
  {
    "text": "M",
    "bbox": [
      152.0,
      33.0,
      203.0,
      59.0
    ],
    "confidence": 0.28737953268995753,
    "component_id": "R1",
    "context": "resistor",
    "engine": "easyocr",
    "rotation": 0,
    "wire_overlap": false,
    "id": "t4",
    "raw": "M",
    "parsed": null,
    "assignments": [],
    "outcome": "ignored",
    "reason": "not_parseable",
    "candidates": []
  },
  {
    "text": "T",
    "bbox": [
      144.0,
      41.0,
      156.0,
      61.0
    ],
    "confidence": 0.00899183141177673,
    "component_id": "R1",
    "context": "resistor",
    "engine": "easyocr",
    "rotation": 0,
    "wire_overlap": true,
    "id": "t5",
    "raw": "T",
    "parsed": null,
    "assignments": [],
    "outcome": "ignored",
    "reason": "not_parseable",
    "candidates": []
  },
  {
    "text": "CJ",
    "bbox": [
      405.0,
      103.0,
      430.0,
      113.0
    ],
    "confidence": 0.031018206621944187,
    "component_id": "R3",
    "context": "resistor",
    "engine": "easyocr",
    "rotation": 0,
    "wire_overlap": false,
    "alternatives": [
      {
        "text": "CUJ",
        "bbox": [
          405.0,
          103.0,
          430.0,
          113.0
        ],
        "confidence": 0.010162920167004767,
        "engine": "easyocr-crop",
        "rotation": 0
      },
      {
        "text": "C",
        "bbox": [
          405.0,
          103.0,
          430.0,
          113.0
        ],
        "confidence": 0.005358739920603206,
        "engine": "easyocr-crop",
        "rotation": 0
      },
      {
        "text": "C",
        "bbox": [
          405.0,
          103.0,
          430.0,
          113.0
        ],
        "confidence": 0.005358739920603206,
        "engine": "easyocr-crop",
        "rotation": 0
      }
    ],
    "id": "t6",
    "raw": "CJ",
    "parsed": null,
    "assignments": [],
    "outcome": "ignored",
    "reason": "not_parseable",
    "candidates": []
  },
  {
    "text": "W",
    "bbox": [
      519.0,
      108.0,
      544.0,
      160.0
    ],
    "confidence": 0.9821202150625972,
    "component_id": "R2",
    "context": "resistor",
    "engine": "easyocr-crop",
    "rotation": -90,
    "wire_overlap": false,
    "alternatives": [
      {
        "text": "M",
        "bbox": [
          519.0,
          108.0,
          544.0,
          160.0
        ],
        "confidence": 0.44997396000897893,
        "engine": "easyocr-crop",
        "rotation": 90
      },
      {
        "text": "<",
        "bbox": [
          519.0,
          108.0,
          544.0,
          160.0
        ],
        "confidence": 0.40635015174632727,
        "engine": "easyocr",
        "rotation": 0
      },
      {
        "text": "W",
        "bbox": [
          519.0,
          108.0,
          544.0,
          160.0
        ],
        "confidence": 0.36637836001672497,
        "engine": "easyocr-crop",
        "rotation": 90
      },
      {
        "text": "W",
        "bbox": [
          519.0,
          108.0,
          544.0,
          160.0
        ],
        "confidence": 0.2917777197696445,
        "engine": "easyocr-crop",
        "rotation": 90
      }
    ],
    "id": "t7",
    "raw": "W",
    "parsed": null,
    "assignments": [],
    "outcome": "ignored",
    "reason": "not_parseable",
    "candidates": []
  },
  {
    "text": "W",
    "bbox": [
      408.0,
      109.0,
      433.0,
      160.0
    ],
    "confidence": 0.8975812796619529,
    "component_id": "R3",
    "context": "resistor",
    "engine": "easyocr-crop",
    "rotation": -90,
    "wire_overlap": false,
    "alternatives": [
      {
        "text": "<",
        "bbox": [
          408.0,
          109.0,
          433.0,
          160.0
        ],
        "confidence": 0.5126208641770269,
        "engine": "easyocr",
        "rotation": 0
      },
      {
        "text": "M",
        "bbox": [
          408.0,
          109.0,
          433.0,
          160.0
        ],
        "confidence": 0.4599626059700803,
        "engine": "easyocr-crop",
        "rotation": 90
      },
      {
        "text": "M",
        "bbox": [
          408.0,
          109.0,
          433.0,
          160.0
        ],
        "confidence": 0.31226721231911725,
        "engine": "easyocr-crop",
        "rotation": 90
      },
      {
        "text": "M",
        "bbox": [
          408.0,
          109.0,
          433.0,
          160.0
        ],
        "confidence": 0.3096181059888501,
        "engine": "easyocr-crop",
        "rotation": 90
      }
    ],
    "id": "t8",
    "raw": "W",
    "parsed": null,
    "assignments": [],
    "outcome": "ignored",
    "reason": "not_parseable",
    "candidates": []
  },
  {
    "text": "'R3",
    "bbox": [
      429.0,
      115.0,
      465.0,
      139.0
    ],
    "confidence": 0.4511451458478658,
    "component_id": "R3",
    "context": "resistor",
    "engine": "easyocr",
    "rotation": 0,
    "wire_overlap": false,
    "id": "t9",
    "raw": "'R3",
    "parsed": {
      "label": "R3",
      "number": null,
      "unit": null,
      "confidence": 0.6,
      "internal": false,
      "unknown": false,
      "emf_symbol": false,
      "unit_inferred": false,
      "normalized": "'",
      "normalizations": []
    },
    "assignments": [
      {
        "component_id": "R3",
        "role": "name",
        "parsed": {
          "label": "R3",
          "number": null,
          "unit": null,
          "confidence": 0.6,
          "internal": false,
          "unknown": false,
          "emf_symbol": false,
          "unit_inferred": false,
          "normalized": "'",
          "normalizations": []
        }
      }
    ],
    "outcome": "assigned",
    "reason": "assigned",
    "candidates": [
      {
        "component_id": "R1",
        "role": "name",
        "distance": 252.89,
        "reason": "too_far"
      },
      {
        "component_id": "R2",
        "role": "name",
        "distance": 72.66,
        "reason": "eligible"
      },
      {
        "component_id": "R3",
        "role": "name",
        "distance": 13.46,
        "reason": "eligible"
      },
      {
        "component_id": "R4",
        "role": "name",
        "distance": 174.32,
        "reason": "too_far"
      },
      {
        "component_id": "V1",
        "role": "name",
        "distance": 381.71,
        "reason": "too_far"
      },
      {
        "component_id": "R5",
        "role": "name",
        "distance": 137.75,
        "reason": "too_far"
      },
      {
        "component_id": "R6",
        "role": "name",
        "distance": 326.98,
        "reason": "too_far"
      }
    ],
    "assigned_to": "R3",
    "role": "name"
  },
  {
    "text": "\"R4",
    "bbox": [
      540.0,
      115.0,
      575.0,
      139.0
    ],
    "confidence": 0.41071015248513126,
    "component_id": "R2",
    "context": "resistor",
    "engine": "easyocr-crop",
    "rotation": 0,
    "wire_overlap": false,
    "alternatives": [
      {
        "text": "\"R4",
        "bbox": [
          540.0,
          115.0,
          575.0,
          139.0
        ],
        "confidence": 0.13754077570600204,
        "engine": "easyocr-crop",
        "rotation": 0
      },
      {
        "text": "\"Ra",
        "bbox": [
          540.0,
          115.0,
          575.0,
          139.0
        ],
        "confidence": 0.21915535993551943,
        "engine": "easyocr-crop",
        "rotation": 0
      },
      {
        "text": "\"Ra",
        "bbox": [
          540.0,
          115.0,
          575.0,
          139.0
        ],
        "confidence": 0.11933123042388298,
        "engine": "easyocr",
        "rotation": 0
      }
    ],
    "id": "t10",
    "raw": "\"R4",
    "parsed": {
      "label": "R4",
      "number": null,
      "unit": null,
      "confidence": 0.6,
      "internal": false,
      "unknown": false,
      "emf_symbol": false,
      "unit_inferred": false,
      "normalized": "\"",
      "normalizations": []
    },
    "assignments": [
      {
        "component_id": "R2",
        "role": "name",
        "parsed": {
          "label": "R4",
          "number": null,
          "unit": null,
          "confidence": 0.6,
          "internal": false,
          "unknown": false,
          "emf_symbol": false,
          "unit_inferred": false,
          "normalized": "\"",
          "normalizations": []
        }
      }
    ],
    "outcome": "assigned",
    "reason": "assigned",
    "candidates": [
      {
        "component_id": "R1",
        "role": "name",
        "distance": 360.57,
        "reason": "too_far"
      },
      {
        "component_id": "R2",
        "role": "name",
        "distance": 13.18,
        "reason": "eligible"
      },
      {
        "component_id": "R3",
        "role": "name",
        "distance": 123.96,
        "reason": "too_far"
      },
      {
        "component_id": "R4",
        "role": "name",
        "distance": 282.15,
        "reason": "too_far"
      },
      {
        "component_id": "V1",
        "role": "name",
        "distance": 491.16,
        "reason": "too_far"
      },
      {
        "component_id": "R5",
        "role": "name",
        "distance": 184.34,
        "reason": "too_far"
      },
      {
        "component_id": "R6",
        "role": "name",
        "distance": 416.06,
        "reason": "too_far"
      }
    ],
    "assigned_to": "R2",
    "role": "name"
  },
  {
    "text": "\"6 ko",
    "bbox": [
      429.0,
      132.0,
      474.0,
      156.0
    ],
    "confidence": 0.594481121502953,
    "component_id": "R3",
    "context": "resistor",
    "engine": "easyocr",
    "rotation": 0,
    "wire_overlap": false,
    "id": "t11",
    "raw": "\"6 ko",
    "parsed": {
      "label": null,
      "number": 6000.0,
      "unit": "ohm",
      "internal": false,
      "unknown": false,
      "has_prefix": true,
      "unit_inferred": false,
      "confidence": 0.85,
      "emf_symbol": false,
      "normalized": "\"6kΩ",
      "normalizations": []
    },
    "assignments": [
      {
        "component_id": "R3",
        "role": "value",
        "parsed": {
          "label": null,
          "number": 6000.0,
          "unit": "ohm",
          "internal": false,
          "unknown": false,
          "has_prefix": true,
          "unit_inferred": false,
          "confidence": 0.85,
          "emf_symbol": false,
          "normalized": "\"6kΩ",
          "normalizations": []
        }
      }
    ],
    "outcome": "assigned",
    "reason": "assigned",
    "candidates": [
      {
        "component_id": "R1",
        "role": "value",
        "distance": 262.22,
        "reason": "too_far"
      },
      {
        "component_id": "R2",
        "role": "value",
        "distance": 68.16,
        "reason": "eligible"
      },
      {
        "component_id": "R3",
        "role": "value",
        "distance": 17.96,
        "reason": "eligible"
      },
      {
        "component_id": "R4",
        "role": "value",
        "distance": 174.81,
        "reason": "too_far"
      },
      {
        "component_id": "V1",
        "role": "value",
        "distance": 383.9,
        "reason": "too_far"
      },
      {
        "component_id": "R5",
        "role": "value",
        "distance": 121.38,
        "reason": "too_far"
      },
      {
        "component_id": "R6",
        "role": "value",
        "distance": 319.43,
        "reason": "too_far"
      }
    ],
    "assigned_to": "R3",
    "role": "value"
  },
  {
    "text": "\"3 ko",
    "bbox": [
      540.0,
      132.0,
      586.0,
      156.0
    ],
    "confidence": 0.5109621419837067,
    "component_id": "R2",
    "context": "resistor",
    "engine": "easyocr",
    "rotation": 0,
    "wire_overlap": false,
    "id": "t12",
    "raw": "\"3 ko",
    "parsed": {
      "label": null,
      "number": 3000.0,
      "unit": "ohm",
      "internal": false,
      "unknown": false,
      "has_prefix": true,
      "unit_inferred": false,
      "confidence": 0.85,
      "emf_symbol": false,
      "normalized": "\"3kΩ",
      "normalizations": []
    },
    "assignments": [
      {
        "component_id": "R2",
        "role": "value",
        "parsed": {
          "label": null,
          "number": 3000.0,
          "unit": "ohm",
          "internal": false,
          "unknown": false,
          "has_prefix": true,
          "unit_inferred": false,
          "confidence": 0.85,
          "emf_symbol": false,
          "normalized": "\"3kΩ",
          "normalizations": []
        }
      }
    ],
    "outcome": "assigned",
    "reason": "assigned",
    "candidates": [
      {
        "component_id": "R1",
        "role": "value",
        "distance": 369.5,
        "reason": "too_far"
      },
      {
        "component_id": "R2",
        "role": "value",
        "distance": 18.68,
        "reason": "eligible"
      },
      {
        "component_id": "R3",
        "role": "value",
        "distance": 129.46,
        "reason": "too_far"
      },
      {
        "component_id": "R4",
        "role": "value",
        "distance": 285.19,
        "reason": "too_far"
      },
      {
        "component_id": "V1",
        "role": "value",
        "distance": 494.87,
        "reason": "too_far"
      },
      {
        "component_id": "R5",
        "role": "value",
        "distance": 176.05,
        "reason": "too_far"
      },
      {
        "component_id": "R6",
        "role": "value",
        "distance": 412.24,
        "reason": "too_far"
      }
    ],
    "assigned_to": "R2",
    "role": "value"
  },
  {
    "text": ">",
    "bbox": [
      429.0,
      148.0,
      442.0,
      164.0
    ],
    "confidence": 0.02549255168056619,
    "component_id": "R3",
    "context": "resistor",
    "engine": "easyocr",
    "rotation": 0,
    "wire_overlap": false,
    "id": "t13",
    "raw": ">",
    "parsed": null,
    "assignments": [],
    "outcome": "ignored",
    "reason": "not_parseable",
    "candidates": []
  },
  {
    "text": ">",
    "bbox": [
      540.0,
      148.0,
      552.0,
      164.0
    ],
    "confidence": 0.02319013416139626,
    "component_id": "R2",
    "context": "resistor",
    "engine": "easyocr",
    "rotation": 0,
    "wire_overlap": false,
    "id": "t14",
    "raw": ">",
    "parsed": null,
    "assignments": [],
    "outcome": "ignored",
    "reason": "not_parseable",
    "candidates": []
  },
  {
    "text": "3n",
    "bbox": [
      414.0,
      156.0,
      442.0,
      166.0
    ],
    "confidence": 0.0012621645302703301,
    "component_id": "R3",
    "context": "resistor",
    "engine": "easyocr",
    "rotation": 0,
    "wire_overlap": true,
    "id": "t15",
    "raw": "3n",
    "parsed": {
      "label": null,
      "number": 3.0000000000000004e-09,
      "unit": null,
      "internal": false,
      "unknown": false,
      "has_prefix": true,
      "unit_inferred": false,
      "confidence": 0.55,
      "emf_symbol": false,
      "normalized": "3n",
      "normalizations": []
    },
    "assignments": [],
    "outcome": "unassigned",
    "reason": "too_far",
    "candidates": [
      {
        "component_id": "R1",
        "role": "value",
        "distance": 246.61,
        "reason": "too_far"
      },
      {
        "component_id": "R2",
        "role": "value",
        "distance": 91.66,
        "reason": "weak_context"
      },
      {
        "component_id": "R3",
        "role": "value",
        "distance": 0.26,
        "reason": "weak_context"
      },
      {
        "component_id": "R4",
        "role": "value",
        "distance": 149.16,
        "reason": "too_far"
      },
      {
        "component_id": "V1",
        "role": "value",
        "distance": 358.95,
        "reason": "too_far"
      },
      {
        "component_id": "R5",
        "role": "value",
        "distance": 103.16,
        "reason": "weak_context"
      },
      {
        "component_id": "R6",
        "role": "value",
        "distance": 290.47,
        "reason": "too_far"
      }
    ]
  },
  {
    "text": "S",
    "bbox": [
      522.0,
      156.0,
      552.0,
      167.0
    ],
    "confidence": 0.004551191444355007,
    "component_id": "R2",
    "context": "resistor",
    "engine": "easyocr",
    "rotation": 0,
    "wire_overlap": false,
    "id": "t16",
    "raw": "S",
    "parsed": null,
    "assignments": [],
    "outcome": "ignored",
    "reason": "not_parseable",
    "candidates": []
  },
  {
    "text": "+",
    "bbox": [
      13.0,
      169.0,
      91.0,
      190.0
    ],
    "confidence": 0.6713283735937381,
    "component_id": "V1",
    "context": "dc_source",
    "engine": "easyocr-crop",
    "rotation": 0,
    "wire_overlap": true,
    "alternatives": [
      {
        "text": "+",
        "bbox": [
          13.0,
          169.0,
          91.0,
          190.0
        ],
        "confidence": 0.3856495033103471,
        "engine": "easyocr-crop",
        "rotation": 0
      },
      {
        "text": "EL",
        "bbox": [
          13.0,
          169.0,
          91.0,
          190.0
        ],
        "confidence": 0.35389370812115634,
        "engine": "easyocr-crop",
        "rotation": 0
      },
      {
        "text": "LL",
        "bbox": [
          13.0,
          169.0,
          91.0,
          190.0
        ],
        "confidence": 0.18887055121226107,
        "engine": "easyocr",
        "rotation": 0
      }
    ],
    "id": "t17",
    "raw": "+",
    "parsed": null,
    "assignments": [],
    "outcome": "assigned",
    "reason": "polarity",
    "candidates": [],
    "assigned_to": "V1",
    "role": "polarity"
  },
  {
    "text": "A",
    "bbox": [
      253.0,
      175.0,
      279.0,
      226.0
    ],
    "confidence": 0.7339039513590393,
    "component_id": "R4",
    "context": "resistor",
    "engine": "easyocr-crop",
    "rotation": 90,
    "wire_overlap": false,
    "alternatives": [
      {
        "text": "W",
        "bbox": [
          253.0,
          175.0,
          279.0,
          226.0
        ],
        "confidence": 0.6187613049352336,
        "engine": "easyocr-crop",
        "rotation": -90
      },
      {
        "text": "M",
        "bbox": [
          253.0,
          175.0,
          279.0,
          226.0
        ],
        "confidence": 0.5980720669015227,
        "engine": "easyocr-crop",
        "rotation": 90
      },
      {
        "text": "W",
        "bbox": [
          253.0,
          175.0,
          279.0,
          226.0
        ],
        "confidence": 0.45642367165670805,
        "engine": "easyocr-crop",
        "rotation": 90
      },
      {
        "text": "<",
        "bbox": [
          253.0,
          175.0,
          279.0,
          226.0
        ],
        "confidence": 0.28932714521943126,
        "engine": "easyocr",
        "rotation": 0
      }
    ],
    "id": "t18",
    "raw": "A",
    "parsed": null,
    "assignments": [],
    "outcome": "ignored",
    "reason": "not_parseable",
    "candidates": []
  },
  {
    "text": "\"Vs",
    "bbox": [
      65.0,
      181.0,
      98.0,
      206.0
    ],
    "confidence": 0.5893370886220547,
    "component_id": "V1",
    "context": "dc_source",
    "engine": "easyocr",
    "rotation": 0,
    "wire_overlap": false,
    "alternatives": [
      {
        "text": "\"Vs",
        "bbox": [
          65.0,
          181.0,
          98.0,
          206.0
        ],
        "confidence": 0.5824855405719914,
        "engine": "easyocr-crop",
        "rotation": 0
      },
      {
        "text": "'Ve",
        "bbox": [
          65.0,
          181.0,
          98.0,
          206.0
        ],
        "confidence": 0.4834653833874555,
        "engine": "easyocr-crop",
        "rotation": 0
      },
      {
        "text": "\"Vs",
        "bbox": [
          65.0,
          181.0,
          98.0,
          206.0
        ],
        "confidence": 0.3570265764974066,
        "engine": "easyocr-crop",
        "rotation": 0
      }
    ],
    "id": "t19",
    "raw": "\"Vs",
    "parsed": null,
    "assignments": [],
    "outcome": "ignored",
    "reason": "not_parseable",
    "candidates": []
  },
  {
    "text": "'R2",
    "bbox": [
      275.0,
      182.0,
      310.0,
      206.0
    ],
    "confidence": 0.24408661877315266,
    "component_id": "R4",
    "context": "resistor",
    "engine": "easyocr",
    "rotation": 0,
    "wire_overlap": false,
    "alternatives": [
      {
        "text": "\"R2",
        "bbox": [
          275.0,
          182.0,
          310.0,
          206.0
        ],
        "confidence": 0.20182198926778583,
        "engine": "easyocr-crop",
        "rotation": 0
      },
      {
        "text": "'R2",
        "bbox": [
          275.0,
          182.0,
          310.0,
          206.0
        ],
        "confidence": 0.1770363507793378,
        "engine": "easyocr-crop",
        "rotation": 0
      },
      {
        "text": "'Rz",
        "bbox": [
          275.0,
          182.0,
          310.0,
          206.0
        ],
        "confidence": 0.39595874336439707,
        "engine": "easyocr-crop",
        "rotation": 0
      }
    ],
    "id": "t20",
    "raw": "'R2",
    "parsed": {
      "label": "R2",
      "number": null,
      "unit": null,
      "confidence": 0.6,
      "internal": false,
      "unknown": false,
      "emf_symbol": false,
      "unit_inferred": false,
      "normalized": "'",
      "normalizations": []
    },
    "assignments": [
      {
        "component_id": "R4",
        "role": "name",
        "parsed": {
          "label": "R2",
          "number": null,
          "unit": null,
          "confidence": 0.6,
          "internal": false,
          "unknown": false,
          "emf_symbol": false,
          "unit_inferred": false,
          "normalized": "'",
          "normalizations": []
        }
      }
    ],
    "outcome": "assigned",
    "reason": "assigned",
    "candidates": [
      {
        "component_id": "R1",
        "role": "name",
        "distance": 161.56,
        "reason": "too_far"
      },
      {
        "component_id": "R2",
        "role": "name",
        "distance": 229.55,
        "reason": "too_far"
      },
      {
        "component_id": "R3",
        "role": "name",
        "distance": 121.09,
        "reason": "too_far"
      },
      {
        "component_id": "R4",
        "role": "name",
        "distance": 12.95,
        "reason": "eligible"
      },
      {
        "component_id": "V1",
        "role": "name",
        "distance": 222.55,
        "reason": "too_far"
      },
      {
        "component_id": "R5",
        "role": "name",
        "distance": 136.15,
        "reason": "too_far"
      },
      {
        "component_id": "R6",
        "role": "name",
        "distance": 175.14,
        "reason": "too_far"
      }
    ],
    "assigned_to": "R4",
    "role": "name"
  },
  {
    "text": "2e",
    "bbox": [
      20.0,
      186.0,
      69.0,
      196.0
    ],
    "confidence": 0.0021153221060011104,
    "component_id": "V1",
    "context": "dc_source",
    "engine": "easyocr",
    "rotation": 0,
    "wire_overlap": false,
    "id": "t21",
    "raw": "2e",
    "parsed": null,
    "assignments": [],
    "outcome": "ignored",
    "reason": "not_parseable",
    "candidates": []
  },
  {
    "text": "S",
    "bbox": [
      25.0,
      190.0,
      66.0,
      205.0
    ],
    "confidence": 0.27696780038519364,
    "component_id": "V1",
    "context": "dc_source",
    "engine": "easyocr",
    "rotation": 0,
    "wire_overlap": false,
    "id": "t22",
    "raw": "S",
    "parsed": null,
    "assignments": [],
    "outcome": "ignored",
    "reason": "not_parseable",
    "candidates": []
  },
  {
    "text": "\"10 ko",
    "bbox": [
      275.0,
      198.0,
      320.0,
      223.0
    ],
    "confidence": 0.39243424268963006,
    "component_id": "R4",
    "context": "resistor",
    "engine": "easyocr",
    "rotation": 0,
    "wire_overlap": false,
    "id": "t23",
    "raw": "\"10 ko",
    "parsed": {
      "label": null,
      "number": 10000.0,
      "unit": "ohm",
      "internal": false,
      "unknown": false,
      "has_prefix": true,
      "unit_inferred": false,
      "confidence": 0.85,
      "emf_symbol": false,
      "normalized": "\"10kΩ",
      "normalizations": []
    },
    "assignments": [
      {
        "component_id": "R4",
        "role": "value",
        "parsed": {
          "label": null,
          "number": 10000.0,
          "unit": "ohm",
          "internal": false,
          "unknown": false,
          "has_prefix": true,
          "unit_inferred": false,
          "confidence": 0.85,
          "emf_symbol": false,
          "normalized": "\"10kΩ",
          "normalizations": []
        }
      }
    ],
    "outcome": "assigned",
    "reason": "assigned",
    "candidates": [
      {
        "component_id": "R1",
        "role": "value",
        "distance": 178.15,
        "reason": "too_far"
      },
      {
        "component_id": "R2",
        "role": "value",
        "distance": 227.61,
        "reason": "too_far"
      },
      {
        "component_id": "R3",
        "role": "value",
        "distance": 122.04,
        "reason": "too_far"
      },
      {
        "component_id": "R4",
        "role": "value",
        "distance": 17.95,
        "reason": "eligible"
      },
      {
        "component_id": "V1",
        "role": "value",
        "distance": 227.55,
        "reason": "too_far"
      },
      {
        "component_id": "R5",
        "role": "value",
        "distance": 123.9,
        "reason": "too_far"
      },
      {
        "component_id": "R6",
        "role": "value",
        "distance": 164.03,
        "reason": "too_far"
      }
    ],
    "assigned_to": "R4",
    "role": "value"
  },
  {
    "text": "\"24V",
    "bbox": [
      65.0,
      199.0,
      109.0,
      223.0
    ],
    "confidence": 0.6380836963653564,
    "component_id": "V1",
    "context": "dc_source",
    "engine": "easyocr",
    "rotation": 0,
    "wire_overlap": false,
    "id": "t24",
    "raw": "\"24V",
    "parsed": {
      "label": null,
      "number": 24.0,
      "unit": "V",
      "internal": false,
      "unknown": false,
      "has_prefix": false,
      "unit_inferred": false,
      "confidence": 0.85,
      "emf_symbol": false,
      "normalized": "\"24V",
      "normalizations": []
    },
    "assignments": [
      {
        "component_id": "V1",
        "role": "value",
        "parsed": {
          "label": null,
          "number": 24.0,
          "unit": "V",
          "internal": false,
          "unknown": false,
          "has_prefix": false,
          "unit_inferred": false,
          "confidence": 0.85,
          "emf_symbol": false,
          "normalized": "\"24V",
          "normalizations": []
        }
      }
    ],
    "outcome": "assigned",
    "reason": "assigned",
    "candidates": [
      {
        "component_id": "R1",
        "role": "value",
        "distance": 165.15,
        "reason": "too_far"
      },
      {
        "component_id": "R2",
        "role": "value",
        "distance": 435.54,
        "reason": "too_far"
      },
      {
        "component_id": "R3",
        "role": "value",
        "distance": 325.83,
        "reason": "too_far"
      },
      {
        "component_id": "R4",
        "role": "value",
        "distance": 166.87,
        "reason": "too_far"
      },
      {
        "component_id": "V1",
        "role": "value",
        "distance": 17.05,
        "reason": "eligible"
      },
      {
        "component_id": "R5",
        "role": "value",
        "distance": 326.54,
        "reason": "too_far"
      },
      {
        "component_id": "R6",
        "role": "value",
        "distance": 148.71,
        "reason": "too_far"
      }
    ],
    "assigned_to": "V1",
    "role": "value"
  },
  {
    "text": ">",
    "bbox": [
      275.0,
      215.0,
      287.0,
      230.0
    ],
    "confidence": 0.09121619646408874,
    "component_id": "R4",
    "context": "resistor",
    "engine": "easyocr",
    "rotation": 0,
    "wire_overlap": false,
    "id": "t25",
    "raw": ">",
    "parsed": null,
    "assignments": [],
    "outcome": "ignored",
    "reason": "not_parseable",
    "candidates": []
  },
  {
    "text": "55",
    "bbox": [
      409.0,
      216.0,
      452.0,
      232.0
    ],
    "confidence": 0.04566060643555303,
    "engine": "easyocr",
    "rotation": 0,
    "wire_overlap": true,
    "alternatives": [
      {
        "text": "55",
        "bbox": [
          409.0,
          216.0,
          452.0,
          232.0
        ],
        "confidence": 0.0290374486136557,
        "engine": "easyocr-crop",
        "rotation": 0
      },
      {
        "text": "F=",
        "bbox": [
          409.0,
          216.0,
          452.0,
          232.0
        ],
        "confidence": 0.04891746427054274,
        "engine": "easyocr-crop",
        "rotation": 0
      },
      {
        "text": "r",
        "bbox": [
          409.0,
          216.0,
          452.0,
          232.0
        ],
        "confidence": 0.046801927667496024,
        "engine": "easyocr-crop",
        "rotation": 0
      }
    ],
    "id": "t26",
    "raw": "55",
    "parsed": {
      "label": null,
      "number": 55.0,
      "unit": null,
      "internal": false,
      "unknown": false,
      "has_prefix": false,
      "unit_inferred": false,
      "confidence": 0.55,
      "emf_symbol": false,
      "normalized": "55",
      "normalizations": []
    },
    "assignments": [],
    "outcome": "unassigned",
    "reason": "too_far",
    "candidates": [
      {
        "component_id": "R1",
        "role": "value",
        "distance": 280.6,
        "reason": "too_far"
      },
      {
        "component_id": "R2",
        "role": "value",
        "distance": 109.19,
        "reason": "weak_context"
      },
      {
        "component_id": "R3",
        "role": "value",
        "distance": 63.26,
        "reason": "weak_context"
      },
      {
        "component_id": "R4",
        "role": "value",
        "distance": 150.95,
        "reason": "too_far"
      },
      {
        "component_id": "V1",
        "role": "value",
        "distance": 360.62,
        "reason": "too_far"
      },
      {
        "component_id": "R5",
        "role": "value",
        "distance": 40.16,
        "reason": "weak_context"
      },
      {
        "component_id": "R6",
        "role": "value",
        "distance": 257.61,
        "reason": "too_far"
      }
    ]
  },
  {
    "text": "C",
    "bbox": [
      260.0,
      222.0,
      287.0,
      233.0
    ],
    "confidence": 0.005137895569532702,
    "component_id": "R4",
    "context": "resistor",
    "engine": "easyocr",
    "rotation": 0,
    "wire_overlap": true,
    "id": "t27",
    "raw": "C",
    "parsed": null,
    "assignments": [],
    "outcome": "ignored",
    "reason": "not_parseable",
    "candidates": []
  },
  {
    "text": "e",
    "bbox": [
      401.0,
      262.0,
      413.0,
      277.0
    ],
    "confidence": 0.03601281622629049,
    "component_id": "R5",
    "context": "resistor",
    "engine": "easyocr-crop",
    "rotation": 0,
    "wire_overlap": false,
    "alternatives": [
      {
        "text": "4s",
        "bbox": [
          401.0,
          262.0,
          413.0,
          277.0
        ],
        "confidence": 0.0027326817359957763,
        "engine": "easyocr",
        "rotation": 0
      },
      {
        "text": "4s",
        "bbox": [
          401.0,
          262.0,
          413.0,
          277.0
        ],
        "confidence": 0.0022354714156484516,
        "engine": "easyocr-crop",
        "rotation": 0
      },
      {
        "text": "An=",
        "bbox": [
          401.0,
          262.0,
          413.0,
          277.0
        ],
        "confidence": 0.0015213038332178074,
        "engine": "easyocr-crop",
        "rotation": 0
      }
    ],
    "id": "t28",
    "raw": "e",
    "parsed": null,
    "assignments": [],
    "outcome": "ignored",
    "reason": "not_parseable",
    "candidates": []
  },
  {
    "text": "2",
    "bbox": [
      409.0,
      264.0,
      434.0,
      316.0
    ],
    "confidence": 0.26783127977916266,
    "component_id": "R5",
    "context": "resistor",
    "engine": "easyocr",
    "rotation": 0,
    "wire_overlap": false,
    "alternatives": [
      {
        "text": "W",
        "bbox": [
          409.0,
          264.0,
          434.0,
          316.0
        ],
        "confidence": 0.8750227990561008,
        "engine": "easyocr-crop",
        "rotation": 90
      },
      {
        "text": "W",
        "bbox": [
          409.0,
          264.0,
          434.0,
          316.0
        ],
        "confidence": 0.7724977798404922,
        "engine": "easyocr-crop",
        "rotation": 90
      },
      {
        "text": "M",
        "bbox": [
          409.0,
          264.0,
          434.0,
          316.0
        ],
        "confidence": 0.6892769993960748,
        "engine": "easyocr-crop",
        "rotation": 90
      },
      {
        "text": "W",
        "bbox": [
          409.0,
          264.0,
          434.0,
          316.0
        ],
        "confidence": 0.24603819495094914,
        "engine": "easyocr-crop",
        "rotation": -90
      }
    ],
    "id": "t29",
    "raw": "2",
    "parsed": {
      "label": null,
      "number": 2.0,
      "unit": null,
      "internal": false,
      "unknown": false,
      "has_prefix": false,
      "unit_inferred": false,
      "confidence": 0.55,
      "emf_symbol": false,
      "normalized": "2",
      "normalizations": []
    },
    "assignments": [],
    "outcome": "unassigned",
    "reason": "too_far",
    "candidates": [
      {
        "component_id": "R1",
        "role": "value",
        "distance": 317.53,
        "reason": "too_far"
      },
      {
        "component_id": "R2",
        "role": "value",
        "distance": 162.12,
        "reason": "too_far"
      },
      {
        "component_id": "R3",
        "role": "value",
        "distance": 129.26,
        "reason": "too_far"
      },
      {
        "component_id": "R4",
        "role": "value",
        "distance": 155.37,
        "reason": "too_far"
      },
      {
        "component_id": "V1",
        "role": "value",
        "distance": 359.07,
        "reason": "too_far"
      },
      {
        "component_id": "R5",
        "role": "value",
        "distance": 0.0,
        "reason": "weak_context"
      },
      {
        "component_id": "R6",
        "role": "value",
        "distance": 225.41,
        "reason": "too_far"
      }
    ]
  },
  {
    "text": "'Rs",
    "bbox": [
      430.0,
      270.0,
      465.0,
      294.0
    ],
    "confidence": 0.21691687216454503,
    "component_id": "R5",
    "context": "resistor",
    "engine": "easyocr",
    "rotation": 0,
    "wire_overlap": false,
    "id": "t30",
    "raw": "'Rs",
    "parsed": null,
    "assignments": [],
    "outcome": "ignored",
    "reason": "not_parseable",
    "candidates": []
  },
  {
    "text": "a",
    "bbox": [
      402.0,
      279.0,
      413.0,
      294.0
    ],
    "confidence": 0.07880523851174193,
    "component_id": "R5",
    "context": "resistor",
    "engine": "easyocr",
    "rotation": 0,
    "wire_overlap": false,
    "id": "t31",
    "raw": "a",
    "parsed": null,
    "assignments": [],
    "outcome": "ignored",
    "reason": "not_parseable",
    "candidates": []
  },
  {
    "text": "4a",
    "bbox": [
      402.0,
      295.0,
      413.0,
      310.0
    ],
    "confidence": 0.004071198034820394,
    "component_id": "R5",
    "context": "resistor",
    "engine": "easyocr",
    "rotation": 0,
    "wire_overlap": false,
    "id": "t32",
    "raw": "4a",
    "parsed": {
      "label": null,
      "number": 4.0,
      "unit": "A",
      "internal": false,
      "unknown": false,
      "has_prefix": false,
      "unit_inferred": false,
      "confidence": 0.85,
      "emf_symbol": false,
      "normalized": "4a",
      "normalizations": []
    },
    "assignments": [],
    "outcome": "unassigned",
    "reason": "too_far",
    "candidates": [
      {
        "component_id": "R1",
        "role": "value",
        "distance": 317.55,
        "reason": "too_far"
      },
      {
        "component_id": "R2",
        "role": "value",
        "distance": 180.58,
        "reason": "too_far"
      },
      {
        "component_id": "R3",
        "role": "value",
        "distance": 141.77,
        "reason": "too_far"
      },
      {
        "component_id": "R4",
        "role": "value",
        "distance": 148.64,
        "reason": "too_far"
      },
      {
        "component_id": "V1",
        "role": "value",
        "distance": 348.23,
        "reason": "too_far"
      },
      {
        "component_id": "R5",
        "role": "value",
        "distance": 1.68,
        "reason": "unit_mismatch"
      },
      {
        "component_id": "R6",
        "role": "value",
        "distance": 208.99,
        "reason": "too_far"
      }
    ]
  },
  {
    "text": ">",
    "bbox": [
      430.0,
      304.0,
      442.0,
      319.0
    ],
    "confidence": 0.28751387768014425,
    "component_id": "R5",
    "context": "resistor",
    "engine": "easyocr",
    "rotation": 0,
    "wire_overlap": false,
    "id": "t33",
    "raw": ">",
    "parsed": null,
    "assignments": [],
    "outcome": "ignored",
    "reason": "not_parseable",
    "candidates": []
  },
  {
    "text": "R6",
    "bbox": [
      161.0,
      305.0,
      195.0,
      327.0
    ],
    "confidence": 0.994742528856212,
    "component_id": "R6",
    "context": "resistor",
    "engine": "easyocr-crop",
    "rotation": 0,
    "wire_overlap": false,
    "alternatives": [
      {
        "text": "R6",
        "bbox": [
          161.0,
          305.0,
          195.0,
          327.0
        ],
        "confidence": 0.7840100170005475,
        "engine": "easyocr",
        "rotation": 0
      },
      {
        "text": "~R6",
        "bbox": [
          161.0,
          305.0,
          195.0,
          327.0
        ],
        "confidence": 0.39886178675538486,
        "engine": "easyocr-crop",
        "rotation": 0
      },
      {
        "text": "~R6",
        "bbox": [
          161.0,
          305.0,
          195.0,
          327.0
        ],
        "confidence": 0.14537046080388621,
        "engine": "easyocr-crop",
        "rotation": 0
      }
    ],
    "id": "t34",
    "raw": "R6",
    "parsed": {
      "label": "R6",
      "number": null,
      "unit": null,
      "confidence": 0.6,
      "internal": false,
      "unknown": false,
      "emf_symbol": false,
      "unit_inferred": false,
      "normalized": "",
      "normalizations": []
    },
    "assignments": [
      {
        "component_id": "R6",
        "role": "name",
        "parsed": {
          "label": "R6",
          "number": null,
          "unit": null,
          "confidence": 0.6,
          "internal": false,
          "unknown": false,
          "emf_symbol": false,
          "unit_inferred": false,
          "normalized": "",
          "normalizations": []
        }
      }
    ],
    "outcome": "assigned",
    "reason": "assigned",
    "candidates": [
      {
        "component_id": "R1",
        "role": "name",
        "distance": 256.73,
        "reason": "too_far"
      },
      {
        "component_id": "R2",
        "role": "name",
        "distance": 375.19,
        "reason": "too_far"
      },
      {
        "component_id": "R3",
        "role": "name",
        "distance": 278.27,
        "reason": "too_far"
      },
      {
        "component_id": "R4",
        "role": "name",
        "distance": 117.06,
        "reason": "too_far"
      },
      {
        "component_id": "V1",
        "role": "name",
        "distance": 146.61,
        "reason": "too_far"
      },
      {
        "component_id": "R5",
        "role": "name",
        "distance": 231.18,
        "reason": "too_far"
      },
      {
        "component_id": "R6",
        "role": "name",
        "distance": 28.4,
        "reason": "eligible"
      }
    ],
    "assigned_to": "R6",
    "role": "name"
  },
  {
    "text": "2ko",
    "bbox": [
      154.0,
      321.0,
      202.0,
      344.0
    ],
    "confidence": 0.5322496350230894,
    "component_id": "R6",
    "context": "resistor",
    "engine": "easyocr",
    "rotation": 0,
    "wire_overlap": false,
    "id": "t35",
    "raw": "2ko",
    "parsed": {
      "label": null,
      "number": 2000.0,
      "unit": "ohm",
      "internal": false,
      "unknown": false,
      "has_prefix": true,
      "unit_inferred": false,
      "confidence": 0.85,
      "emf_symbol": false,
      "normalized": "2kΩ",
      "normalizations": []
    },
    "assignments": [
      {
        "component_id": "R6",
        "role": "value",
        "parsed": {
          "label": null,
          "number": 2000.0,
          "unit": "ohm",
          "internal": false,
          "unknown": false,
          "has_prefix": true,
          "unit_inferred": false,
          "confidence": 0.85,
          "emf_symbol": false,
          "normalized": "2kΩ",
          "normalizations": []
        }
      }
    ],
    "outcome": "assigned",
    "reason": "assigned",
    "candidates": [
      {
        "component_id": "R1",
        "role": "value",
        "distance": 273.23,
        "reason": "too_far"
      },
      {
        "component_id": "R2",
        "role": "value",
        "distance": 382.3,
        "reason": "too_far"
      },
      {
        "component_id": "R3",
        "role": "value",
        "distance": 287.81,
        "reason": "too_far"
      },
      {
        "component_id": "R4",
        "role": "value",
        "distance": 130.07,
        "reason": "too_far"
      },
      {
        "component_id": "V1",
        "role": "value",
        "distance": 158.23,
        "reason": "too_far"
      },
      {
        "component_id": "R5",
        "role": "value",
        "distance": 231.74,
        "reason": "too_far"
      },
      {
        "component_id": "R6",
        "role": "value",
        "distance": 11.9,
        "reason": "eligible"
      }
    ],
    "assigned_to": "R6",
    "role": "value"
  },
  {
    "text": "1",
    "bbox": [
      198.0,
      340.0,
      212.0,
      362.0
    ],
    "confidence": 0.9237560263455293,
    "component_id": "R6",
    "context": "resistor",
    "engine": "easyocr",
    "rotation": 0,
    "wire_overlap": true,
    "alternatives": [
      {
        "text": "4",
        "bbox": [
          198.0,
          340.0,
          212.0,
          362.0
        ],
        "confidence": 0.0047517742621858705,
        "engine": "easyocr-crop",
        "rotation": 90
      },
      {
        "text": "P",
        "bbox": [
          198.0,
          340.0,
          212.0,
          362.0
        ],
        "confidence": 0.0045576234213220435,
        "engine": "easyocr-crop",
        "rotation": 90
      },
      {
        "text": "U",
        "bbox": [
          198.0,
          340.0,
          212.0,
          362.0
        ],
        "confidence": 0.004204081171565122,
        "engine": "easyocr-crop",
        "rotation": -90
      },
      {
        "text": "A",
        "bbox": [
          198.0,
          340.0,
          212.0,
          362.0
        ],
        "confidence": 0.002930649686790923,
        "engine": "easyocr-crop",
        "rotation": 90
      }
    ],
    "id": "t36",
    "raw": "1",
    "parsed": {
      "label": null,
      "number": 1.0,
      "unit": null,
      "internal": false,
      "unknown": false,
      "has_prefix": false,
      "unit_inferred": false,
      "confidence": 0.55,
      "emf_symbol": false,
      "normalized": "1",
      "normalizations": []
    },
    "assignments": [],
    "outcome": "unassigned",
    "reason": "weak_context",
    "candidates": [
      {
        "component_id": "R1",
        "role": "value",
        "distance": 291.74,
        "reason": "too_far"
      },
      {
        "component_id": "R2",
        "role": "value",
        "distance": 367.59,
        "reason": "too_far"
      },
      {
        "component_id": "R3",
        "role": "value",
        "distance": 278.91,
        "reason": "too_far"
      },
      {
        "component_id": "R4",
        "role": "value",
        "distance": 133.42,
        "reason": "too_far"
      },
      {
        "component_id": "V1",
        "role": "value",
        "distance": 190.31,
        "reason": "too_far"
      },
      {
        "component_id": "R5",
        "role": "value",
        "distance": 207.08,
        "reason": "too_far"
      },
      {
        "component_id": "R6",
        "role": "value",
        "distance": 2.25,
        "reason": "weak_context"
      }
    ]
  },
  {
    "text": "AN",
    "bbox": [
      152.0,
      344.0,
      202.0,
      366.0
    ],
    "confidence": 0.7418565375311941,
    "component_id": "R6",
    "context": "resistor",
    "engine": "easyocr",
    "rotation": 0,
    "wire_overlap": false,
    "id": "t37",
    "raw": "AN",
    "parsed": null,
    "assignments": [],
    "outcome": "ignored",
    "reason": "not_parseable",
    "candidates": []
  },
  {
    "text": "P",
    "bbox": [
      144.0,
      353.0,
      156.0,
      366.0
    ],
    "confidence": 0.0036349026777435928,
    "component_id": "R6",
    "context": "resistor",
    "engine": "easyocr",
    "rotation": 0,
    "wire_overlap": true,
    "id": "t38",
    "raw": "P",
    "parsed": null,
    "assignments": [],
    "outcome": "ignored",
    "reason": "not_parseable",
    "candidates": []
  }
]
```

## Final values and tracing baseline for WP-B

|Revision|Part|Type|Printed name|Value|
|---|---|---|---|---|
|"before"|"R1"|"resistor"|"R1"|{"number":5000.0,"unit":"ohm","status":"given","source":"ocr","confidence":0.3520235461449072}|
|"before"|"R2"|"resistor"|null|{"number":100.0,"unit":"ohm","status":"assumed","source":"prior","confidence":0.0}|
|"before"|"R3"|"resistor"|null|{"number":100.0,"unit":"ohm","status":"assumed","source":"prior","confidence":0.0}|
|"before"|"R4"|"resistor"|null|{"number":100.0,"unit":"ohm","status":"assumed","source":"prior","confidence":0.0}|
|"before"|"V1"|"dc_source"|null|{"number":12.0,"unit":"V","status":"assumed","source":"prior","confidence":0.0}|
|"before"|"R5"|"resistor"|null|{"number":100.0,"unit":"ohm","status":"assumed","source":"prior","confidence":0.0}|
|"before"|"R6"|"resistor"|"R6"|{"number":2000.0,"unit":"ohm","status":"given","source":"ocr","confidence":0.5696317245096543}|
|"WP-A"|"R1"|"resistor"|"R1"|{"number":5000.0,"unit":"ohm","status":"given","source":"ocr","confidence":0.3572108541263147,"unit_inferred":false}|
|"WP-A"|"R2"|"resistor"|"R4"|{"number":3000.0,"unit":"ohm","status":"given","source":"ocr","confidence":0.5109621419837067,"unit_inferred":false}|
|"WP-A"|"R3"|"resistor"|"R3"|{"number":6000.0,"unit":"ohm","status":"given","source":"ocr","confidence":0.594481121502953,"unit_inferred":false}|
|"WP-A"|"R4"|"resistor"|"R2"|{"number":10000.0,"unit":"ohm","status":"given","source":"ocr","confidence":0.39243424268963006,"unit_inferred":false}|
|"WP-A"|"V1"|"dc_source"|null|{"number":24.0,"unit":"V","status":"given","source":"ocr","confidence":0.6380836963653564,"unit_inferred":false}|
|"WP-A"|"R5"|"resistor"|null|{"number":100.0,"unit":"ohm","status":"assumed","source":"prior","confidence":0.0,"unit_inferred":false}|
|"WP-A"|"R6"|"resistor"|"R6"|{"number":2000.0,"unit":"ohm","status":"given","source":"ocr","confidence":0.5322496350230894,"unit_inferred":false}|

WP-A graph: **7 nodes**; any computed nonzero current: **true**. This is not a topology accuracy score.

The OCR annotation shows components and text, not wire connectivity. WP-B adds wire overlays and records whether repairs improve the graph.

## WP-B tracing replay

Same WP-A detections and OCR; no detector/OCR rerun or gold topology claim. Wire overlay: `.cache/round3/wires/case-002.png` (local only).

```json
{
  "image": "Screenshot 2026-10-30 232905.png",
  "before": {
    "nodes": 7,
    "parts": 7,
    "disabled": 0,
    "provenance": "extracted",
    "nonzero_current": true,
    "score": 12,
    "warnings": [
      {
        "code": "polarity_uncertain",
        "ref": "V1",
        "message_key": "warn.polarity_uncertain"
      },
      {
        "code": "no_closed_loop",
        "ref": "n6",
        "message_key": "warn.no_closed_loop"
      },
      {
        "code": "no_closed_loop",
        "ref": "n8",
        "message_key": "warn.no_closed_loop"
      },
      {
        "code": "no_closed_loop",
        "ref": "n12",
        "message_key": "warn.no_closed_loop"
      },
      {
        "code": "dangling_wire",
        "ref": "p26",
        "message_key": "warn.dangling_wire"
      },
      {
        "code": "dangling_wire",
        "ref": "p29",
        "message_key": "warn.dangling_wire"
      },
      {
        "code": "dangling_wire",
        "ref": "p33",
        "message_key": "warn.dangling_wire"
      },
      {
        "code": "assumed_value",
        "ref": "R5",
        "message_key": "warn.assumed_value"
      },
      {
        "code": "value_not_found",
        "ref": "R5",
        "message_key": "warn.value_not_found"
      }
    ]
  },
  "after": {
    "nodes": 5,
    "parts": 7,
    "disabled": 0,
    "provenance": "extracted",
    "nonzero_current": true,
    "score": 4,
    "warnings": [
      {
        "code": "ambiguous_crossing",
        "ref": "xy:442,299",
        "message_key": "warn.ambiguous_crossing"
      },
      {
        "code": "polarity_uncertain",
        "ref": "V1",
        "message_key": "warn.polarity_uncertain"
      },
      {
        "code": "dangling_wire",
        "ref": "p1",
        "message_key": "warn.dangling_wire"
      },
      {
        "code": "dangling_wire",
        "ref": "p4",
        "message_key": "warn.dangling_wire"
      },
      {
        "code": "dangling_wire",
        "ref": "p9",
        "message_key": "warn.dangling_wire"
      },
      {
        "code": "dangling_wire",
        "ref": "p33",
        "message_key": "warn.dangling_wire"
      }
    ]
  },
  "trace": {
    "alternative_threshold": false,
    "repair": false,
    "terminals_snapped": 14,
    "terminals_floating": 0,
    "off_axis_snaps": 0,
    "gaps_bridged": 0,
    "stroke_width": 1.7999999523162842,
    "ghosts": []
  },
  "seconds": 2.4327978000001167,
  "scope": "Tracing-only replay on identical WP-A detections/texts; no gold topology accuracy."
}
```


## Final round-three manual-value verification

The final pipeline still reads six of seven values, keeps seven components and
five nodes, and leaves R5 visibly missing/assumed. Entering its printed 8 kOhm
value through the same solve API (status user) produces source current -2 mA
and equivalent resistance 12 kOhm without changing topology or other values.
The sign is current into the positive source terminal. See
case-002-corrected.json for the actual solve response fields/invariants. This
verifies the known manual repair for this case, not automatic OCR accuracy.
