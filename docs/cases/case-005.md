# Case 005: Screenshot 2026-10-31 000946.png

SHA-256: `feb53035e2391b6056c098fedc7ab7fbf85bb19752fa11a58846784db7759ab6`. Read-only configured owner input; raster excluded from Git.

The visible 3 ohm label produces conflicting 332 / 30 / 39 readings; it now needs confirmation instead of assigning 332 ohm. The 5 V source and 2 ohm resistor are read. The visible 10 ohm label is in the OCR evidence but may remain unassigned. E is symbolic, and the ammeter reading must not become a resistance value.

Inspected annotated image: `.cache/round3/case-005.png` (local only).

Both engine paths were requested. Tesseract is not installed on this machine; there are no real Tesseract readings to report. EasyOCR EN/BN uses installed local models. Dual-engine selection is tested with mocks, not claimed as a local Tesseract benchmark.

## Frozen round-two evidence

The trace below records actual Hungarian selections (including recovery attempts). A selected candidate does not necessarily survive the final netlist. The old API did not retain every rejected pair; unselected candidates are reported as such rather than inventing a rejection distance.

|Raw text|Native box|Old parse|Actual selection (role, part, cost / dummy)|
|---|---|---|---|
|"2 9"|[66.0,31.0,109.0,57.0]|null|"not parseable"|
|"R2"|[179.0,54.0,220.0,91.0]|{"label":"R2","number":null,"unit":null,"confidence":0.6,"internal":false,"unknown":false}|[{"role":"name","component":"R3","cost":21.73282162432279,"dummy_cost":196.1268768310547}]|
|"R"|[170.0,61.0,198.0,86.0]|null|"not parseable"|
|"1"|[298.0,90.0,326.0,141.0]|{"label":null,"number":1.0,"unit":null,"confidence":0.55,"internal":false,"unknown":false,"has_prefix":false}|"not selected; rejection pairs not retained"|
|"12"|[211.0,133.0,252.0,170.0]|{"label":null,"number":12.0,"unit":null,"confidence":0.55,"internal":false,"unknown":false,"has_prefix":false}|[{"role":"value","component":"V2","cost":23.385720147128183,"dummy_cost":156.87135314941406}]|
|"(24"|[296.0,134.0,335.0,159.0]|null|"not parseable"|
|"(1)"|[196.0,140.0,232.0,167.0]|null|"not parseable"|
|"4"|[288.0,152.0,307.0,167.0]|{"label":null,"number":4.0,"unit":null,"confidence":0.55,"internal":false,"unknown":false,"has_prefix":false}|"not selected; rejection pairs not retained"|
|"LS J"|[12.0,158.0,308.0,212.0]|null|"not parseable"|
|"10 $2"|[109.0,204.0,160.0,230.0]|null|"not parseable"|
|"E"|[214.0,205.0,241.0,230.0]|{"label":"E","number":null,"unit":null,"confidence":0.6,"internal":false,"unknown":false}|[{"role":"name","component":"R4","cost":115.08962055685592,"dummy_cost":262.5871353149414}]|

## Current raw engine readings

|Engine / rotation|Raw text|Native box|Current parse in anchored context|
|---|---|---|---|
|"easyocr-crop / 0"|"~5V"|[220.0,4.0,268.0,28.0]|{"label":null,"number":5.0,"unit":"V","internal":false,"unknown":false,"has_prefix":false,"unit_inferred":false,"confidence":0.85,"emf_symbol":false,"normalized":"~5V","normalizations":[]}|
|"easyocr / 0"|"332"|[165.0,10.0,210.0,33.0]|{"label":null,"number":332.0,"unit":"ohm","internal":false,"unknown":false,"has_prefix":false,"unit_inferred":true,"confidence":0.6,"emf_symbol":false,"normalized":"332","normalizations":["component_unit"]}|
|"easyocr-crop / 90"|"3"|[220.0,19.0,231.0,45.0]|{"label":null,"number":3.0,"unit":"V","internal":false,"unknown":false,"has_prefix":false,"unit_inferred":true,"confidence":0.6,"emf_symbol":false,"normalized":"3","normalizations":["component_unit"]}|
|"easyocr / 0"|"i["|[227.0,24.0,241.0,54.0]|null|
|"easyocr / 0"|"'"|[211.0,26.0,223.0,45.0]|null|
|"easyocr / 0"|"7"|[237.0,26.0,277.0,72.0]|{"label":null,"number":7.0,"unit":"V","internal":false,"unknown":false,"has_prefix":false,"unit_inferred":true,"confidence":0.6,"emf_symbol":false,"normalized":"7","normalizations":["component_unit"]}|
|"easyocr / 0"|"#t"|[167.0,29.0,215.0,49.0]|null|
|"easyocr-crop / 0"|"2 9"|[66.0,31.0,109.0,57.0]|{"label":null,"number":2.0,"unit":"ohm","internal":false,"unknown":false,"has_prefix":false,"unit_inferred":true,"confidence":0.6,"emf_symbol":false,"normalized":"2 Ω","normalizations":["contextual_unit_lookalike"]}|
|"easyocr / 0"|"4e"|[160.0,35.0,171.0,51.0]|null|
|"easyocr / 0"|"T"|[220.0,36.0,231.0,60.0]|null|
|"easyocr / 0"|"4u"|[220.0,50.0,240.0,60.0]|{"label":null,"number":4e-06,"unit":"V","internal":false,"unknown":false,"has_prefix":true,"unit_inferred":true,"confidence":0.6,"emf_symbol":false,"normalized":"4u","normalizations":["component_unit"]}|
|"easyocr-crop / 0"|"M"|[56.0,53.0,119.0,78.0]|null|
|"easyocr / 0"|"Sa"|[16.0,59.0,60.0,80.0]|null|
|"easyocr / 0"|"R"|[170.0,61.0,198.0,86.0]|null|
|"easyocr-crop / 0"|"41"|[289.0,78.0,308.0,95.0]|{"label":null,"number":41.0,"unit":null,"internal":false,"unknown":false,"has_prefix":false,"unit_inferred":false,"confidence":0.55,"emf_symbol":false,"normalized":"41","normalizations":[]}|
|"easyocr / 0"|"'"|[210.0,83.0,222.0,100.0]|null|
|"easyocr / 0"|"4"|[15.0,90.0,34.0,103.0]|{"label":null,"number":4.0,"unit":"ohm","internal":false,"unknown":false,"has_prefix":false,"unit_inferred":true,"confidence":0.6,"emf_symbol":false,"normalized":"4","normalizations":["component_unit"]}|
|"easyocr / 0"|"1"|[298.0,90.0,326.0,141.0]|{"label":null,"number":1.0,"unit":null,"internal":false,"unknown":false,"has_prefix":false,"unit_inferred":false,"confidence":0.55,"emf_symbol":false,"normalized":"1","normalizations":[]}|
|"easyocr-crop / 90"|" _"|[160.0,92.0,171.0,109.0]|null|
|"easyocr / 0"|"VVV #"|[167.0,92.0,214.0,105.0]|null|
|"easyocr / 0"|"2A"|[296.0,134.0,335.0,159.0]|{"label":null,"number":2.0,"unit":"A","internal":false,"unknown":false,"has_prefix":false,"unit_inferred":false,"confidence":0.85,"emf_symbol":false,"normalized":"2A","normalizations":[]}|
|"easyocr / 0"|"L"|[14.0,151.0,33.0,193.0]|null|
|"easyocr-crop / 0"|"("|[196.0,151.0,211.0,167.0]|null|
|"easyocr / 0"|"2"|[227.0,151.0,252.0,170.0]|{"label":null,"number":2.0,"unit":"V","internal":false,"unknown":false,"has_prefix":false,"unit_inferred":true,"confidence":0.6,"emf_symbol":false,"normalized":"2","normalizations":["component_unit"]}|
|"easyocr / 0"|"4"|[179.0,164.0,219.0,212.0]|{"label":null,"number":4.0,"unit":"V","internal":false,"unknown":false,"has_prefix":false,"unit_inferred":true,"confidence":0.6,"emf_symbol":false,"normalized":"4","normalizations":["component_unit"]}|
|"easyocr / 0"|"}"|[218.0,170.0,231.0,206.0]|null|
|"easyocr / 0"|"{"|[227.0,170.0,239.0,206.0]|null|
|"easyocr-crop / 0"|"L"|[156.0,174.0,211.0,198.0]|null|
|"easyocr / 0"|"M"|[97.0,176.0,160.0,200.0]|null|
|"easyocr / 0"|"7"|[90.0,185.0,101.0,202.0]|{"label":null,"number":7.0,"unit":"ohm","internal":false,"unknown":false,"has_prefix":false,"unit_inferred":true,"confidence":0.6,"emf_symbol":false,"normalized":"7","normalizations":["component_unit"]}|
|"easyocr / 0"|"4u"|[208.0,202.0,228.0,212.0]|{"label":null,"number":4e-06,"unit":"V","internal":false,"unknown":false,"has_prefix":true,"unit_inferred":true,"confidence":0.6,"emf_symbol":false,"normalized":"4u","normalizations":["component_unit"]}|
|"easyocr / 0"|"10 $2"|[109.0,204.0,160.0,230.0]|null|
|"easyocr / 0"|";"|[227.0,205.0,241.0,224.0]|null|

## Current association decisions

Every tested component/role pair includes its measured distance and rejection reason. `weak_context` covers a body/lead overlap, low confidence, contradictory bare readings or insufficient anchored support; it is deliberately conservative.

```json
[
  {
    "text": "~5V",
    "bbox": [
      220.0,
      4.0,
      268.0,
      28.0
    ],
    "confidence": 0.2065305096932456,
    "component_id": "V1",
    "context": "dc_source",
    "engine": "easyocr-crop",
    "rotation": 0,
    "wire_overlap": false,
    "alternatives": [
      {
        "text": " 5",
        "bbox": [
          220.0,
          4.0,
          268.0,
          28.0
        ],
        "confidence": 0.3961184172597701,
        "engine": "easyocr",
        "rotation": 0
      }
    ],
    "id": "t1",
    "raw": "~5V",
    "parsed": {
      "label": null,
      "number": 5.0,
      "unit": "V",
      "internal": false,
      "unknown": false,
      "has_prefix": false,
      "unit_inferred": false,
      "confidence": 0.85,
      "emf_symbol": false,
      "normalized": "~5V",
      "normalizations": []
    },
    "assignments": [
      {
        "component_id": "V1",
        "role": "value",
        "parsed": {
          "label": null,
          "number": 5.0,
          "unit": "V",
          "internal": false,
          "unknown": false,
          "has_prefix": false,
          "unit_inferred": false,
          "confidence": 0.85,
          "emf_symbol": false,
          "normalized": "~5V",
          "normalizations": []
        }
      }
    ],
    "outcome": "assigned",
    "reason": "assigned",
    "candidates": [
      {
        "component_id": "V1",
        "role": "value",
        "distance": 9.39,
        "reason": "eligible"
      },
      {
        "component_id": "R1",
        "role": "value",
        "distance": 31.8,
        "reason": "unit_mismatch"
      },
      {
        "component_id": "R2",
        "role": "value",
        "distance": 130.27,
        "reason": "too_far"
      },
      {
        "component_id": "R3",
        "role": "value",
        "distance": 76.4,
        "reason": "unit_mismatch"
      },
      {
        "component_id": "V2",
        "role": "value",
        "distance": 153.67,
        "reason": "too_far"
      },
      {
        "component_id": "R4",
        "role": "value",
        "distance": 181.0,
        "reason": "too_far"
      }
    ],
    "assigned_to": "V1",
    "role": "value"
  },
  {
    "text": "332",
    "bbox": [
      165.0,
      10.0,
      210.0,
      33.0
    ],
    "confidence": 0.7720052156057436,
    "component_id": "R1",
    "context": "resistor",
    "engine": "easyocr",
    "rotation": 0,
    "wire_overlap": false,
    "alternatives": [
      {
        "text": "30",
        "bbox": [
          165.0,
          10.0,
          210.0,
          33.0
        ],
        "confidence": 0.5242351160185201,
        "engine": "easyocr-crop",
        "rotation": 0
      },
      {
        "text": "39",
        "bbox": [
          165.0,
          10.0,
          210.0,
          33.0
        ],
        "confidence": 0.42164975612015404,
        "engine": "easyocr-crop",
        "rotation": 0
      },
      {
        "text": "30 ,",
        "bbox": [
          165.0,
          10.0,
          210.0,
          33.0
        ],
        "confidence": 0.3599426655927716,
        "engine": "easyocr-crop",
        "rotation": 0
      }
    ],
    "id": "t2",
    "raw": "332",
    "parsed": {
      "label": null,
      "number": 332.0,
      "unit": null,
      "internal": false,
      "unknown": false,
      "has_prefix": false,
      "unit_inferred": false,
      "confidence": 0.55,
      "emf_symbol": false,
      "normalized": "332",
      "normalizations": []
    },
    "assignments": [],
    "outcome": "unassigned",
    "reason": "too_far",
    "candidates": [
      {
        "component_id": "V1",
        "role": "value",
        "distance": 40.11,
        "reason": "weak_context"
      },
      {
        "component_id": "R1",
        "role": "value",
        "distance": 7.94,
        "reason": "weak_context"
      },
      {
        "component_id": "R2",
        "role": "value",
        "distance": 75.45,
        "reason": "weak_context"
      },
      {
        "component_id": "R3",
        "role": "value",
        "distance": 64.85,
        "reason": "weak_context"
      },
      {
        "component_id": "V2",
        "role": "value",
        "distance": 150.33,
        "reason": "too_far"
      },
      {
        "component_id": "R4",
        "role": "value",
        "distance": 157.53,
        "reason": "too_far"
      }
    ]
  },
  {
    "text": "3",
    "bbox": [
      220.0,
      19.0,
      231.0,
      45.0
    ],
    "confidence": 0.10501812410756006,
    "component_id": "V1",
    "context": "dc_source",
    "engine": "easyocr-crop",
    "rotation": 90,
    "wire_overlap": true,
    "alternatives": [
      {
        "text": "3",
        "bbox": [
          220.0,
          19.0,
          231.0,
          45.0
        ],
        "confidence": 0.08401384977929638,
        "engine": "easyocr-crop",
        "rotation": 90
      },
      {
        "text": "3",
        "bbox": [
          220.0,
          19.0,
          231.0,
          45.0
        ],
        "confidence": 0.06300534719479689,
        "engine": "easyocr-crop",
        "rotation": 90
      },
      {
        "text": "3",
        "bbox": [
          220.0,
          19.0,
          231.0,
          45.0
        ],
        "confidence": 0.03549089939824146,
        "engine": "easyocr",
        "rotation": 0
      },
      {
        "text": "",
        "bbox": [
          220.0,
          19.0,
          231.0,
          45.0
        ],
        "confidence": 0.0,
        "engine": "easyocr-crop",
        "rotation": -90
      }
    ],
    "id": "t3",
    "raw": "3",
    "parsed": {
      "label": null,
      "number": 3.0,
      "unit": null,
      "internal": false,
      "unknown": false,
      "has_prefix": false,
      "unit_inferred": false,
      "confidence": 0.55,
      "emf_symbol": false,
      "normalized": "3",
      "normalizations": []
    },
    "assignments": [],
    "outcome": "unassigned",
    "reason": "too_far",
    "candidates": [
      {
        "component_id": "V1",
        "role": "value",
        "distance": 1.96,
        "reason": "weak_context"
      },
      {
        "component_id": "R1",
        "role": "value",
        "distance": 10.32,
        "reason": "weak_context"
      },
      {
        "component_id": "R2",
        "role": "value",
        "distance": 108.36,
        "reason": "weak_context"
      },
      {
        "component_id": "R3",
        "role": "value",
        "distance": 55.51,
        "reason": "weak_context"
      },
      {
        "component_id": "V2",
        "role": "value",
        "distance": 137.12,
        "reason": "too_far"
      },
      {
        "component_id": "R4",
        "role": "value",
        "distance": 158.55,
        "reason": "too_far"
      }
    ]
  },
  {
    "text": "i[",
    "bbox": [
      227.0,
      24.0,
      241.0,
      54.0
    ],
    "confidence": 0.2505388565077297,
    "component_id": "V1",
    "context": "dc_source",
    "engine": "easyocr",
    "rotation": 0,
    "wire_overlap": false,
    "id": "t4",
    "raw": "i[",
    "parsed": null,
    "assignments": [],
    "outcome": "ignored",
    "reason": "not_parseable",
    "candidates": []
  },
  {
    "text": "'",
    "bbox": [
      211.0,
      26.0,
      223.0,
      45.0
    ],
    "confidence": 0.21675245824761546,
    "component_id": "R1",
    "context": "resistor",
    "engine": "easyocr",
    "rotation": 0,
    "wire_overlap": true,
    "alternatives": [
      {
        "text": "s",
        "bbox": [
          211.0,
          26.0,
          223.0,
          45.0
        ],
        "confidence": 0.02725260059254797,
        "engine": "easyocr-crop",
        "rotation": -90
      },
      {
        "text": "l",
        "bbox": [
          211.0,
          26.0,
          223.0,
          45.0
        ],
        "confidence": 0.015984968131065536,
        "engine": "easyocr-crop",
        "rotation": 90
      },
      {
        "text": "",
        "bbox": [
          211.0,
          26.0,
          223.0,
          45.0
        ],
        "confidence": 0.0,
        "engine": "easyocr-crop",
        "rotation": 90
      },
      {
        "text": "",
        "bbox": [
          211.0,
          26.0,
          223.0,
          45.0
        ],
        "confidence": 0.0,
        "engine": "easyocr-crop",
        "rotation": 90
      }
    ],
    "id": "t5",
    "raw": "'",
    "parsed": null,
    "assignments": [],
    "outcome": "ignored",
    "reason": "not_parseable",
    "candidates": []
  },
  {
    "text": "7",
    "bbox": [
      237.0,
      26.0,
      277.0,
      72.0
    ],
    "confidence": 0.42941374315900305,
    "component_id": "V1",
    "context": "dc_source",
    "engine": "easyocr",
    "rotation": 0,
    "wire_overlap": false,
    "id": "t6",
    "raw": "7",
    "parsed": {
      "label": null,
      "number": 7.0,
      "unit": null,
      "internal": false,
      "unknown": false,
      "has_prefix": false,
      "unit_inferred": false,
      "confidence": 0.55,
      "emf_symbol": false,
      "normalized": "7",
      "normalizations": []
    },
    "assignments": [],
    "outcome": "unassigned",
    "reason": "too_far",
    "candidates": [
      {
        "component_id": "V1",
        "role": "value",
        "distance": 15.85,
        "reason": "weak_context"
      },
      {
        "component_id": "R1",
        "role": "value",
        "distance": 41.82,
        "reason": "weak_context"
      },
      {
        "component_id": "R2",
        "role": "value",
        "distance": 137.7,
        "reason": "too_far"
      },
      {
        "component_id": "R3",
        "role": "value",
        "distance": 56.81,
        "reason": "weak_context"
      },
      {
        "component_id": "V2",
        "role": "value",
        "distance": 122.89,
        "reason": "too_far"
      },
      {
        "component_id": "R4",
        "role": "value",
        "distance": 159.92,
        "reason": "too_far"
      }
    ]
  },
  {
    "text": "#t",
    "bbox": [
      167.0,
      29.0,
      215.0,
      49.0
    ],
    "confidence": 0.10383744507091784,
    "component_id": "R1",
    "context": "resistor",
    "engine": "easyocr",
    "rotation": 0,
    "wire_overlap": true,
    "id": "t7",
    "raw": "#t",
    "parsed": null,
    "assignments": [],
    "outcome": "ignored",
    "reason": "not_parseable",
    "candidates": []
  },
  {
    "text": "2 9",
    "bbox": [
      66.0,
      31.0,
      109.0,
      57.0
    ],
    "confidence": 0.7281985814032859,
    "component_id": "R2",
    "context": "resistor",
    "engine": "easyocr-crop",
    "rotation": 0,
    "wire_overlap": false,
    "alternatives": [
      {
        "text": "2 9",
        "bbox": [
          66.0,
          31.0,
          109.0,
          57.0
        ],
        "confidence": 0.5573113006017733,
        "engine": "easyocr",
        "rotation": 0
      },
      {
        "text": "22",
        "bbox": [
          66.0,
          31.0,
          109.0,
          57.0
        ],
        "confidence": 0.5706831697232349,
        "engine": "easyocr-crop",
        "rotation": 0
      },
      {
        "text": "20",
        "bbox": [
          66.0,
          31.0,
          109.0,
          57.0
        ],
        "confidence": 0.3212652775847217,
        "engine": "easyocr-crop",
        "rotation": 0
      }
    ],
    "id": "t8",
    "raw": "2 9",
    "parsed": {
      "label": null,
      "number": 2.0,
      "unit": "ohm",
      "internal": false,
      "unknown": false,
      "has_prefix": false,
      "unit_inferred": true,
      "confidence": 0.6,
      "emf_symbol": false,
      "normalized": "2 Ω",
      "normalizations": [
        "contextual_unit_lookalike"
      ]
    },
    "assignments": [
      {
        "component_id": "R2",
        "role": "value",
        "parsed": {
          "label": null,
          "number": 2.0,
          "unit": "ohm",
          "internal": false,
          "unknown": false,
          "has_prefix": false,
          "unit_inferred": true,
          "confidence": 0.6,
          "emf_symbol": false,
          "normalized": "2 Ω",
          "normalizations": [
            "contextual_unit_lookalike"
          ]
        }
      }
    ],
    "outcome": "assigned",
    "reason": "assigned",
    "candidates": [
      {
        "component_id": "V1",
        "role": "value",
        "distance": 139.96,
        "reason": "too_far"
      },
      {
        "component_id": "R1",
        "role": "value",
        "distance": 79.96,
        "reason": "weak_context"
      },
      {
        "component_id": "R2",
        "role": "value",
        "distance": 9.96,
        "reason": "eligible"
      },
      {
        "component_id": "R3",
        "role": "value",
        "distance": 90.8,
        "reason": "weak_context"
      },
      {
        "component_id": "V2",
        "role": "value",
        "distance": 179.27,
        "reason": "too_far"
      },
      {
        "component_id": "R4",
        "role": "value",
        "distance": 133.1,
        "reason": "too_far"
      }
    ],
    "assigned_to": "R2",
    "role": "value"
  },
  {
    "text": "4e",
    "bbox": [
      160.0,
      35.0,
      171.0,
      51.0
    ],
    "confidence": 0.004943037599193785,
    "component_id": "R1",
    "context": "resistor",
    "engine": "easyocr",
    "rotation": 0,
    "wire_overlap": true,
    "id": "t9",
    "raw": "4e",
    "parsed": null,
    "assignments": [],
    "outcome": "ignored",
    "reason": "not_parseable",
    "candidates": []
  },
  {
    "text": "T",
    "bbox": [
      220.0,
      36.0,
      231.0,
      60.0
    ],
    "confidence": 0.010334103877781331,
    "component_id": "V1",
    "context": "dc_source",
    "engine": "easyocr",
    "rotation": 0,
    "wire_overlap": true,
    "id": "t10",
    "raw": "T",
    "parsed": null,
    "assignments": [],
    "outcome": "ignored",
    "reason": "not_parseable",
    "candidates": []
  },
  {
    "text": "4u",
    "bbox": [
      220.0,
      50.0,
      240.0,
      60.0
    ],
    "confidence": 0.0077569094518967555,
    "component_id": "V1",
    "context": "dc_source",
    "engine": "easyocr",
    "rotation": 0,
    "wire_overlap": false,
    "id": "t11",
    "raw": "4u",
    "parsed": {
      "label": null,
      "number": 4e-06,
      "unit": null,
      "internal": false,
      "unknown": false,
      "has_prefix": true,
      "unit_inferred": false,
      "confidence": 0.55,
      "emf_symbol": false,
      "normalized": "4u",
      "normalizations": []
    },
    "assignments": [],
    "outcome": "unassigned",
    "reason": "too_far",
    "candidates": [
      {
        "component_id": "V1",
        "role": "value",
        "distance": 0.45,
        "reason": "weak_context"
      },
      {
        "component_id": "R1",
        "role": "value",
        "distance": 15.92,
        "reason": "weak_context"
      },
      {
        "component_id": "R2",
        "role": "value",
        "distance": 110.61,
        "reason": "weak_context"
      },
      {
        "component_id": "R3",
        "role": "value",
        "distance": 35.11,
        "reason": "weak_context"
      },
      {
        "component_id": "V2",
        "role": "value",
        "distance": 114.12,
        "reason": "too_far"
      },
      {
        "component_id": "R4",
        "role": "value",
        "distance": 140.04,
        "reason": "too_far"
      }
    ]
  },
  {
    "text": "M",
    "bbox": [
      56.0,
      53.0,
      119.0,
      78.0
    ],
    "confidence": 0.9406662600741953,
    "component_id": "R2",
    "context": "resistor",
    "engine": "easyocr-crop",
    "rotation": 0,
    "wire_overlap": false,
    "alternatives": [
      {
        "text": "M",
        "bbox": [
          56.0,
          53.0,
          119.0,
          78.0
        ],
        "confidence": 0.9208316482504983,
        "engine": "easyocr",
        "rotation": 0
      },
      {
        "text": "M",
        "bbox": [
          56.0,
          53.0,
          119.0,
          78.0
        ],
        "confidence": 0.9083158104741393,
        "engine": "easyocr-crop",
        "rotation": 0
      },
      {
        "text": "M",
        "bbox": [
          56.0,
          53.0,
          119.0,
          78.0
        ],
        "confidence": 0.7901002626590667,
        "engine": "easyocr-crop",
        "rotation": 0
      }
    ],
    "id": "t12",
    "raw": "M",
    "parsed": null,
    "assignments": [],
    "outcome": "ignored",
    "reason": "not_parseable",
    "candidates": []
  },
  {
    "text": "Sa",
    "bbox": [
      16.0,
      59.0,
      60.0,
      80.0
    ],
    "confidence": 0.005366396529079325,
    "component_id": "R2",
    "context": "resistor",
    "engine": "easyocr",
    "rotation": 0,
    "wire_overlap": true,
    "id": "t13",
    "raw": "Sa",
    "parsed": null,
    "assignments": [],
    "outcome": "ignored",
    "reason": "not_parseable",
    "candidates": []
  },
  {
    "text": "R",
    "bbox": [
      170.0,
      61.0,
      198.0,
      86.0
    ],
    "confidence": 0.9998365707418522,
    "component_id": "R1",
    "context": "resistor",
    "engine": "easyocr",
    "rotation": 0,
    "wire_overlap": false,
    "alternatives": [
      {
        "text": "R )",
        "bbox": [
          179.0,
          54.0,
          220.0,
          87.0
        ],
        "confidence": 0.4911411849036341,
        "engine": "easyocr",
        "rotation": 0
      }
    ],
    "id": "t14",
    "raw": "R",
    "parsed": null,
    "assignments": [],
    "outcome": "ignored",
    "reason": "not_parseable",
    "candidates": []
  },
  {
    "text": "41",
    "bbox": [
      289.0,
      78.0,
      308.0,
      95.0
    ],
    "confidence": 0.09030935604538412,
    "engine": "easyocr-crop",
    "rotation": 0,
    "wire_overlap": true,
    "alternatives": [
      {
        "text": "71",
        "bbox": [
          289.0,
          78.0,
          308.0,
          95.0
        ],
        "confidence": 0.08655384256470985,
        "engine": "easyocr",
        "rotation": 0
      },
      {
        "text": "i",
        "bbox": [
          289.0,
          78.0,
          308.0,
          95.0
        ],
        "confidence": 0.8795063849194698,
        "engine": "easyocr-crop",
        "rotation": 0
      },
      {
        "text": "4:",
        "bbox": [
          289.0,
          78.0,
          308.0,
          95.0
        ],
        "confidence": 0.05015157157365441,
        "engine": "easyocr-crop",
        "rotation": 0
      }
    ],
    "id": "t15",
    "raw": "41",
    "parsed": {
      "label": null,
      "number": 41.0,
      "unit": null,
      "internal": false,
      "unknown": false,
      "has_prefix": false,
      "unit_inferred": false,
      "confidence": 0.55,
      "emf_symbol": false,
      "normalized": "41",
      "normalizations": []
    },
    "assignments": [],
    "outcome": "unassigned",
    "reason": "too_far",
    "candidates": [
      {
        "component_id": "V1",
        "role": "value",
        "distance": 65.64,
        "reason": "too_far"
      },
      {
        "component_id": "R1",
        "role": "value",
        "distance": 91.29,
        "reason": "weak_context"
      },
      {
        "component_id": "R2",
        "role": "value",
        "distance": 179.31,
        "reason": "too_far"
      },
      {
        "component_id": "R3",
        "role": "value",
        "distance": 84.31,
        "reason": "weak_context"
      },
      {
        "component_id": "V2",
        "role": "value",
        "distance": 106.65,
        "reason": "too_far"
      },
      {
        "component_id": "R4",
        "role": "value",
        "distance": 164.64,
        "reason": "too_far"
      }
    ]
  },
  {
    "text": "'",
    "bbox": [
      210.0,
      83.0,
      222.0,
      100.0
    ],
    "confidence": 0.4321225057979383,
    "component_id": "R3",
    "context": "resistor",
    "engine": "easyocr",
    "rotation": 0,
    "wire_overlap": true,
    "alternatives": [
      {
        "text": "a",
        "bbox": [
          210.0,
          83.0,
          222.0,
          100.0
        ],
        "confidence": 0.05315647282524427,
        "engine": "easyocr-crop",
        "rotation": 90
      },
      {
        "text": "a",
        "bbox": [
          210.0,
          83.0,
          222.0,
          100.0
        ],
        "confidence": 0.018165087303867233,
        "engine": "easyocr-crop",
        "rotation": 90
      },
      {
        "text": "U",
        "bbox": [
          210.0,
          83.0,
          222.0,
          100.0
        ],
        "confidence": 0.005426395087525293,
        "engine": "easyocr-crop",
        "rotation": -90
      },
      {
        "text": "4d",
        "bbox": [
          210.0,
          83.0,
          222.0,
          100.0
        ],
        "confidence": 0.0012040718677917442,
        "engine": "easyocr-crop",
        "rotation": 90
      }
    ],
    "id": "t16",
    "raw": "'",
    "parsed": null,
    "assignments": [],
    "outcome": "ignored",
    "reason": "not_parseable",
    "candidates": []
  },
  {
    "text": "4",
    "bbox": [
      15.0,
      90.0,
      34.0,
      103.0
    ],
    "confidence": 0.06010618670945633,
    "component_id": "R2",
    "context": "resistor",
    "engine": "easyocr",
    "rotation": 0,
    "wire_overlap": true,
    "id": "t17",
    "raw": "4",
    "parsed": {
      "label": null,
      "number": 4.0,
      "unit": null,
      "internal": false,
      "unknown": false,
      "has_prefix": false,
      "unit_inferred": false,
      "confidence": 0.55,
      "emf_symbol": false,
      "normalized": "4",
      "normalizations": []
    },
    "assignments": [],
    "outcome": "unassigned",
    "reason": "weak_context",
    "candidates": [
      {
        "component_id": "V1",
        "role": "value",
        "distance": 207.25,
        "reason": "too_far"
      },
      {
        "component_id": "R1",
        "role": "value",
        "distance": 150.58,
        "reason": "too_far"
      },
      {
        "component_id": "R2",
        "role": "value",
        "distance": 37.09,
        "reason": "weak_context"
      },
      {
        "component_id": "R3",
        "role": "value",
        "distance": 143.32,
        "reason": "too_far"
      },
      {
        "component_id": "V2",
        "role": "value",
        "distance": 204.7,
        "reason": "too_far"
      },
      {
        "component_id": "R4",
        "role": "value",
        "distance": 108.24,
        "reason": "weak_context"
      }
    ]
  },
  {
    "text": "1",
    "bbox": [
      298.0,
      90.0,
      326.0,
      141.0
    ],
    "confidence": 0.8854615649517292,
    "engine": "easyocr",
    "rotation": 0,
    "wire_overlap": true,
    "alternatives": [
      {
        "text": "57",
        "bbox": [
          298.0,
          90.0,
          326.0,
          141.0
        ],
        "confidence": 0.36843949445129054,
        "engine": "easyocr-crop",
        "rotation": -90
      },
      {
        "text": "4=",
        "bbox": [
          298.0,
          90.0,
          326.0,
          141.0
        ],
        "confidence": 0.37493131266960134,
        "engine": "easyocr-crop",
        "rotation": 90
      },
      {
        "text": "+",
        "bbox": [
          298.0,
          90.0,
          326.0,
          141.0
        ],
        "confidence": 0.28726547275006453,
        "engine": "easyocr-crop",
        "rotation": 90
      },
      {
        "text": "+=",
        "bbox": [
          298.0,
          90.0,
          326.0,
          141.0
        ],
        "confidence": 0.14387008884921923,
        "engine": "easyocr-crop",
        "rotation": 90
      }
    ],
    "id": "t18",
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
        "component_id": "V1",
        "role": "value",
        "distance": 93.45,
        "reason": "too_far"
      },
      {
        "component_id": "R1",
        "role": "value",
        "distance": 117.35,
        "reason": "too_far"
      },
      {
        "component_id": "R2",
        "role": "value",
        "distance": 196.2,
        "reason": "too_far"
      },
      {
        "component_id": "R3",
        "role": "value",
        "distance": 98.33,
        "reason": "too_far"
      },
      {
        "component_id": "V2",
        "role": "value",
        "distance": 97.08,
        "reason": "too_far"
      },
      {
        "component_id": "R4",
        "role": "value",
        "distance": 163.13,
        "reason": "too_far"
      }
    ]
  },
  {
    "text": " _",
    "bbox": [
      160.0,
      92.0,
      171.0,
      109.0
    ],
    "confidence": 0.08912506002708272,
    "component_id": "R3",
    "context": "resistor",
    "engine": "easyocr-crop",
    "rotation": 90,
    "wire_overlap": true,
    "alternatives": [
      {
        "text": "e",
        "bbox": [
          160.0,
          92.0,
          171.0,
          109.0
        ],
        "confidence": 0.06715461296666891,
        "engine": "easyocr",
        "rotation": 0
      },
      {
        "text": "le",
        "bbox": [
          160.0,
          92.0,
          171.0,
          109.0
        ],
        "confidence": 0.007186071747301958,
        "engine": "easyocr-crop",
        "rotation": -90
      },
      {
        "text": "",
        "bbox": [
          160.0,
          92.0,
          171.0,
          109.0
        ],
        "confidence": 0.0,
        "engine": "easyocr-crop",
        "rotation": 90
      },
      {
        "text": "",
        "bbox": [
          160.0,
          92.0,
          171.0,
          109.0
        ],
        "confidence": 0.0,
        "engine": "easyocr-crop",
        "rotation": 90
      }
    ],
    "id": "t19",
    "raw": " _",
    "parsed": null,
    "assignments": [],
    "outcome": "ignored",
    "reason": "not_parseable",
    "candidates": []
  },
  {
    "text": "VVV #",
    "bbox": [
      167.0,
      92.0,
      214.0,
      105.0
    ],
    "confidence": 0.05321036005745232,
    "component_id": "R3",
    "context": "resistor",
    "engine": "easyocr",
    "rotation": 0,
    "wire_overlap": true,
    "id": "t20",
    "raw": "VVV #",
    "parsed": null,
    "assignments": [],
    "outcome": "ignored",
    "reason": "not_parseable",
    "candidates": []
  },
  {
    "text": "2A",
    "bbox": [
      296.0,
      134.0,
      335.0,
      159.0
    ],
    "confidence": 0.8887639593629428,
    "engine": "easyocr",
    "rotation": 0,
    "wire_overlap": true,
    "id": "t21",
    "raw": "2A",
    "parsed": {
      "label": null,
      "number": 2.0,
      "unit": "A",
      "internal": false,
      "unknown": false,
      "has_prefix": false,
      "unit_inferred": false,
      "confidence": 0.85,
      "emf_symbol": false,
      "normalized": "2A",
      "normalizations": []
    },
    "assignments": [],
    "outcome": "unassigned",
    "reason": "too_far",
    "candidates": [
      {
        "component_id": "V1",
        "role": "value",
        "distance": 118.24,
        "reason": "too_far"
      },
      {
        "component_id": "R1",
        "role": "value",
        "distance": 139.76,
        "reason": "too_far"
      },
      {
        "component_id": "R2",
        "role": "value",
        "distance": 207.68,
        "reason": "too_far"
      },
      {
        "component_id": "R3",
        "role": "value",
        "distance": 109.34,
        "reason": "too_far"
      },
      {
        "component_id": "V2",
        "role": "value",
        "distance": 87.41,
        "reason": "too_far"
      },
      {
        "component_id": "R4",
        "role": "value",
        "distance": 157.63,
        "reason": "too_far"
      }
    ]
  },
  {
    "text": "L",
    "bbox": [
      14.0,
      151.0,
      33.0,
      193.0
    ],
    "confidence": 0.9733201309629749,
    "engine": "easyocr",
    "rotation": 0,
    "wire_overlap": true,
    "id": "t22",
    "raw": "L",
    "parsed": null,
    "assignments": [],
    "outcome": "ignored",
    "reason": "not_parseable",
    "candidates": []
  },
  {
    "text": "(",
    "bbox": [
      196.0,
      151.0,
      211.0,
      167.0
    ],
    "confidence": 0.12192127018260468,
    "component_id": "R4",
    "context": "resistor",
    "engine": "easyocr-crop",
    "rotation": 0,
    "wire_overlap": false,
    "alternatives": [
      {
        "text": "4(",
        "bbox": [
          196.0,
          151.0,
          211.0,
          167.0
        ],
        "confidence": 0.12120990468144953,
        "engine": "easyocr-crop",
        "rotation": 0
      },
      {
        "text": "4(",
        "bbox": [
          196.0,
          151.0,
          211.0,
          167.0
        ],
        "confidence": 0.10590994912494815,
        "engine": "easyocr",
        "rotation": 0
      },
      {
        "text": "4(",
        "bbox": [
          196.0,
          151.0,
          211.0,
          167.0
        ],
        "confidence": 0.08209639284477742,
        "engine": "easyocr-crop",
        "rotation": 0
      }
    ],
    "id": "t23",
    "raw": "(",
    "parsed": null,
    "assignments": [],
    "outcome": "ignored",
    "reason": "not_parseable",
    "candidates": []
  },
  {
    "text": "2",
    "bbox": [
      227.0,
      151.0,
      252.0,
      170.0
    ],
    "confidence": 0.14835582390334423,
    "component_id": "V2",
    "context": "dc_source",
    "engine": "easyocr",
    "rotation": 0,
    "wire_overlap": false,
    "alternatives": [
      {
        "text": "2",
        "bbox": [
          227.0,
          151.0,
          252.0,
          170.0
        ],
        "confidence": 0.11814412744983205,
        "engine": "easyocr-crop",
        "rotation": 0
      },
      {
        "text": "8",
        "bbox": [
          227.0,
          151.0,
          252.0,
          170.0
        ],
        "confidence": 0.05122953739931635,
        "engine": "easyocr-crop",
        "rotation": 0
      },
      {
        "text": "\"",
        "bbox": [
          227.0,
          151.0,
          252.0,
          170.0
        ],
        "confidence": 0.07179502958283379,
        "engine": "easyocr-crop",
        "rotation": 0
      }
    ],
    "id": "t24",
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
    "reason": "weak_context",
    "candidates": [
      {
        "component_id": "V1",
        "role": "value",
        "distance": 105.95,
        "reason": "too_far"
      },
      {
        "component_id": "R1",
        "role": "value",
        "distance": 113.93,
        "reason": "too_far"
      },
      {
        "component_id": "R2",
        "role": "value",
        "distance": 145.64,
        "reason": "too_far"
      },
      {
        "component_id": "R3",
        "role": "value",
        "distance": 60.68,
        "reason": "weak_context"
      },
      {
        "component_id": "V2",
        "role": "value",
        "distance": 12.06,
        "reason": "weak_context"
      },
      {
        "component_id": "R4",
        "role": "value",
        "distance": 80.36,
        "reason": "weak_context"
      }
    ]
  },
  {
    "text": "4",
    "bbox": [
      179.0,
      164.0,
      219.0,
      212.0
    ],
    "confidence": 0.6731840869381358,
    "component_id": "V2",
    "context": "dc_source",
    "engine": "easyocr",
    "rotation": 0,
    "wire_overlap": false,
    "alternatives": [
      {
        "text": "4",
        "bbox": [
          179.0,
          164.0,
          219.0,
          212.0
        ],
        "confidence": 0.566645902193855,
        "engine": "easyocr-crop",
        "rotation": 0
      },
      {
        "text": "H",
        "bbox": [
          179.0,
          164.0,
          219.0,
          212.0
        ],
        "confidence": 0.33045371367279586,
        "engine": "easyocr-crop",
        "rotation": 0
      },
      {
        "text": "H",
        "bbox": [
          179.0,
          164.0,
          219.0,
          212.0
        ],
        "confidence": 0.26148794174944,
        "engine": "easyocr-crop",
        "rotation": 0
      }
    ],
    "id": "t25",
    "raw": "4",
    "parsed": {
      "label": null,
      "number": 4.0,
      "unit": null,
      "internal": false,
      "unknown": false,
      "has_prefix": false,
      "unit_inferred": false,
      "confidence": 0.55,
      "emf_symbol": false,
      "normalized": "4",
      "normalizations": []
    },
    "assignments": [],
    "outcome": "unassigned",
    "reason": "weak_context",
    "candidates": [
      {
        "component_id": "V1",
        "role": "value",
        "distance": 136.45,
        "reason": "too_far"
      },
      {
        "component_id": "R1",
        "role": "value",
        "distance": 138.81,
        "reason": "too_far"
      },
      {
        "component_id": "R2",
        "role": "value",
        "distance": 135.67,
        "reason": "too_far"
      },
      {
        "component_id": "R3",
        "role": "value",
        "distance": 82.65,
        "reason": "weak_context"
      },
      {
        "component_id": "V2",
        "role": "value",
        "distance": 16.89,
        "reason": "weak_context"
      },
      {
        "component_id": "R4",
        "role": "value",
        "distance": 38.2,
        "reason": "weak_context"
      }
    ]
  },
  {
    "text": "}",
    "bbox": [
      218.0,
      170.0,
      231.0,
      206.0
    ],
    "confidence": 0.07673886262493657,
    "component_id": "V2",
    "context": "dc_source",
    "engine": "easyocr",
    "rotation": 0,
    "wire_overlap": false,
    "id": "t26",
    "raw": "}",
    "parsed": null,
    "assignments": [],
    "outcome": "ignored",
    "reason": "not_parseable",
    "candidates": []
  },
  {
    "text": "{",
    "bbox": [
      227.0,
      170.0,
      239.0,
      206.0
    ],
    "confidence": 0.15235200799976756,
    "component_id": "V2",
    "context": "dc_source",
    "engine": "easyocr",
    "rotation": 0,
    "wire_overlap": true,
    "id": "t27",
    "raw": "{",
    "parsed": null,
    "assignments": [],
    "outcome": "ignored",
    "reason": "not_parseable",
    "candidates": []
  },
  {
    "text": "L",
    "bbox": [
      156.0,
      174.0,
      211.0,
      198.0
    ],
    "confidence": 0.018794488637402518,
    "component_id": "R4",
    "context": "resistor",
    "engine": "easyocr-crop",
    "rotation": 0,
    "wire_overlap": false,
    "alternatives": [
      {
        "text": "",
        "bbox": [
          156.0,
          174.0,
          211.0,
          198.0
        ],
        "confidence": 0.0,
        "engine": "easyocr",
        "rotation": 0
      },
      {
        "text": "",
        "bbox": [
          156.0,
          174.0,
          211.0,
          198.0
        ],
        "confidence": 0.0,
        "engine": "easyocr-crop",
        "rotation": 0
      },
      {
        "text": "",
        "bbox": [
          156.0,
          174.0,
          211.0,
          198.0
        ],
        "confidence": 0.0,
        "engine": "easyocr-crop",
        "rotation": 0
      }
    ],
    "id": "t28",
    "raw": "L",
    "parsed": null,
    "assignments": [],
    "outcome": "ignored",
    "reason": "not_parseable",
    "candidates": []
  },
  {
    "text": "M",
    "bbox": [
      97.0,
      176.0,
      160.0,
      200.0
    ],
    "confidence": 0.9912690599173324,
    "component_id": "R4",
    "context": "resistor",
    "engine": "easyocr",
    "rotation": 0,
    "wire_overlap": false,
    "id": "t29",
    "raw": "M",
    "parsed": null,
    "assignments": [],
    "outcome": "ignored",
    "reason": "not_parseable",
    "candidates": []
  },
  {
    "text": "7",
    "bbox": [
      90.0,
      185.0,
      101.0,
      202.0
    ],
    "confidence": 0.15726161691031226,
    "component_id": "R4",
    "context": "resistor",
    "engine": "easyocr",
    "rotation": 0,
    "wire_overlap": true,
    "id": "t30",
    "raw": "7",
    "parsed": {
      "label": null,
      "number": 7.0,
      "unit": null,
      "internal": false,
      "unknown": false,
      "has_prefix": false,
      "unit_inferred": false,
      "confidence": 0.55,
      "emf_symbol": false,
      "normalized": "7",
      "normalizations": []
    },
    "assignments": [],
    "outcome": "unassigned",
    "reason": "weak_context",
    "candidates": [
      {
        "component_id": "V1",
        "role": "value",
        "distance": 191.62,
        "reason": "too_far"
      },
      {
        "component_id": "R1",
        "role": "value",
        "distance": 161.25,
        "reason": "too_far"
      },
      {
        "component_id": "R2",
        "role": "value",
        "distance": 115.36,
        "reason": "weak_context"
      },
      {
        "component_id": "R3",
        "role": "value",
        "distance": 114.02,
        "reason": "too_far"
      },
      {
        "component_id": "V2",
        "role": "value",
        "distance": 120.39,
        "reason": "too_far"
      },
      {
        "component_id": "R4",
        "role": "value",
        "distance": 1.64,
        "reason": "weak_context"
      }
    ]
  },
  {
    "text": "4u",
    "bbox": [
      208.0,
      202.0,
      228.0,
      212.0
    ],
    "confidence": 0.007889165257051526,
    "component_id": "V2",
    "context": "dc_source",
    "engine": "easyocr",
    "rotation": 0,
    "wire_overlap": false,
    "id": "t31",
    "raw": "4u",
    "parsed": {
      "label": null,
      "number": 4e-06,
      "unit": null,
      "internal": false,
      "unknown": false,
      "has_prefix": true,
      "unit_inferred": false,
      "confidence": 0.55,
      "emf_symbol": false,
      "normalized": "4u",
      "normalizations": []
    },
    "assignments": [],
    "outcome": "unassigned",
    "reason": "weak_context",
    "candidates": [
      {
        "component_id": "V1",
        "role": "value",
        "distance": 152.74,
        "reason": "too_far"
      },
      {
        "component_id": "R1",
        "role": "value",
        "distance": 157.83,
        "reason": "too_far"
      },
      {
        "component_id": "R2",
        "role": "value",
        "distance": 162.26,
        "reason": "too_far"
      },
      {
        "component_id": "R3",
        "role": "value",
        "distance": 101.72,
        "reason": "too_far"
      },
      {
        "component_id": "V2",
        "role": "value",
        "distance": 0.77,
        "reason": "weak_context"
      },
      {
        "component_id": "R4",
        "role": "value",
        "distance": 57.55,
        "reason": "weak_context"
      }
    ]
  },
  {
    "text": "10 $2",
    "bbox": [
      109.0,
      204.0,
      160.0,
      230.0
    ],
    "confidence": 0.6088813762132428,
    "component_id": "R4",
    "context": "resistor",
    "engine": "easyocr",
    "rotation": 0,
    "wire_overlap": false,
    "id": "t32",
    "raw": "10 $2",
    "parsed": null,
    "assignments": [],
    "outcome": "ignored",
    "reason": "not_parseable",
    "candidates": []
  },
  {
    "text": ";",
    "bbox": [
      227.0,
      205.0,
      241.0,
      224.0
    ],
    "confidence": 0.18037322211615336,
    "component_id": "V2",
    "context": "dc_source",
    "engine": "easyocr",
    "rotation": 0,
    "wire_overlap": false,
    "id": "t33",
    "raw": ";",
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
|"before"|"V1"|"dc_source"|null|{"number":12.0,"unit":"V","status":"assumed","source":"prior","confidence":0.0}|
|"before"|"R1"|"resistor"|null|{"number":10.0,"unit":"ohm","status":"assumed","source":"prior","confidence":0.0}|
|"before"|"R2"|"resistor"|null|{"number":10.0,"unit":"ohm","status":"assumed","source":"prior","confidence":0.0}|
|"before"|"R3"|"resistor"|"R2"|{"number":10.0,"unit":"ohm","status":"assumed","source":"prior","confidence":0.0}|
|"before"|"V2"|"dc_source"|null|{"number":12.0,"unit":"V","status":"assumed","source":"prior","confidence":0.0}|
|"before"|"R4"|"resistor"|"E"|{"number":10.0,"unit":"ohm","status":"assumed","source":"prior","confidence":0.0}|
|"WP-A"|"V1"|"dc_source"|null|{"number":5.0,"unit":"V","status":"given","source":"ocr","confidence":0.2065305096932456,"unit_inferred":false}|
|"WP-A"|"R1"|"resistor"|null|{"number":null,"unit":"ohm","status":"assumed","source":"prior","confidence":0.0,"unit_inferred":false}|
|"WP-A"|"R2"|"resistor"|null|{"number":2.0,"unit":"ohm","status":"given","source":"ocr","confidence":0.6,"unit_inferred":true}|
|"WP-A"|"R3"|"resistor"|null|{"number":null,"unit":"ohm","status":"assumed","source":"prior","confidence":0.0,"unit_inferred":false}|
|"WP-A"|"V2"|"dc_source"|null|{"number":12.0,"unit":"V","status":"assumed","source":"prior","confidence":0.0,"unit_inferred":false}|
|"WP-A"|"R4"|"resistor"|null|{"number":null,"unit":"ohm","status":"assumed","source":"prior","confidence":0.0,"unit_inferred":false}|

WP-A graph: **9 nodes**; any computed nonzero current: **true**. This is not a topology accuracy score.

The OCR annotation shows components and text, not wire connectivity. WP-B adds wire overlays and records whether repairs improve the graph.

## WP-B tracing replay

Same WP-A detections and OCR; no detector/OCR rerun or gold topology claim. Wire overlay: `.cache/round3/wires/case-005.png` (local only).

```json
{
  "image": "Screenshot 2026-10-31 000946.png",
  "before": {
    "nodes": 9,
    "parts": 6,
    "disabled": 5,
    "provenance": "partial",
    "nonzero_current": true,
    "score": 35,
    "warnings": [
      {
        "code": "unit_inferred",
        "ref": "R2",
        "message_key": "warn.unit_inferred"
      },
      {
        "code": "uncertain_topology",
        "ref": "V1",
        "message_key": "warn.uncertain_topology"
      },
      {
        "code": "uncertain_topology",
        "ref": "R1",
        "message_key": "warn.uncertain_topology"
      },
      {
        "code": "partial_circuit",
        "ref": "V1",
        "message_key": "warn.partial_circuit"
      },
      {
        "code": "partial_circuit",
        "ref": "R1",
        "message_key": "warn.partial_circuit"
      },
      {
        "code": "partial_circuit",
        "ref": "R2",
        "message_key": "warn.partial_circuit"
      },
      {
        "code": "partial_circuit",
        "ref": "R3",
        "message_key": "warn.partial_circuit"
      },
      {
        "code": "partial_circuit",
        "ref": "R4",
        "message_key": "warn.partial_circuit"
      },
      {
        "code": "polarity_uncertain",
        "ref": "V2",
        "message_key": "warn.polarity_uncertain"
      },
      {
        "code": "no_closed_loop",
        "ref": "isolated.V1.b",
        "message_key": "warn.no_closed_loop"
      },
      {
        "code": "no_closed_loop",
        "ref": "isolated.R1.b",
        "message_key": "warn.no_closed_loop"
      },
      {
        "code": "no_closed_loop",
        "ref": "n1",
        "message_key": "warn.no_closed_loop"
      },
      {
        "code": "no_closed_loop",
        "ref": "n4",
        "message_key": "warn.no_closed_loop"
      },
      {
        "code": "no_closed_loop",
        "ref": "n5",
        "message_key": "warn.no_closed_loop"
      },
      {
        "code": "no_closed_loop",
        "ref": "n7",
        "message_key": "warn.no_closed_loop"
      },
      {
        "code": "no_closed_loop",
        "ref": "n12",
        "message_key": "warn.no_closed_loop"
      },
      {
        "code": "no_closed_loop",
        "ref": "n16",
        "message_key": "warn.no_closed_loop"
      },
      {
        "code": "dangling_wire",
        "ref": "p3",
        "message_key": "warn.dangling_wire"
      },
      {
        "code": "dangling_wire",
        "ref": "p6",
        "message_key": "warn.dangling_wire"
      },
      {
        "code": "dangling_wire",
        "ref": "p14",
        "message_key": "warn.dangling_wire"
      },
      {
        "code": "dangling_wire",
        "ref": "p16",
        "message_key": "warn.dangling_wire"
      },
      {
        "code": "dangling_wire",
        "ref": "p20",
        "message_key": "warn.dangling_wire"
      },
      {
        "code": "dangling_wire",
        "ref": "p23",
        "message_key": "warn.dangling_wire"
      },
      {
        "code": "dangling_wire",
        "ref": "p27",
        "message_key": "warn.dangling_wire"
      },
      {
        "code": "assumed_value",
        "ref": "V2",
        "message_key": "warn.assumed_value"
      },
      {
        "code": "value_not_found",
        "ref": "R1",
        "message_key": "warn.value_not_found"
      },
      {
        "code": "value_not_found",
        "ref": "R3",
        "message_key": "warn.value_not_found"
      },
      {
        "code": "value_not_found",
        "ref": "V2",
        "message_key": "warn.value_not_found"
      },
      {
        "code": "value_not_found",
        "ref": "R4",
        "message_key": "warn.value_not_found"
      }
    ]
  },
  "after": {
    "nodes": 9,
    "parts": 6,
    "disabled": 0,
    "provenance": "partial",
    "nonzero_current": false,
    "score": 35,
    "warnings": [
      {
        "code": "uncertain_topology",
        "ref": "V1",
        "message_key": "warn.uncertain_topology"
      },
      {
        "code": "uncertain_topology",
        "ref": "R1",
        "message_key": "warn.uncertain_topology"
      },
      {
        "code": "uncertain_topology",
        "ref": "V2",
        "message_key": "warn.uncertain_topology"
      },
      {
        "code": "off_axis_snap",
        "ref": "V2",
        "message_key": "warn.off_axis_snap"
      },
      {
        "code": "source_open_loop",
        "ref": "V1",
        "message_key": "warn.source_open_loop"
      },
      {
        "code": "source_open_loop",
        "ref": "V2",
        "message_key": "warn.source_open_loop"
      },
      {
        "code": "no_closed_loop",
        "ref": null,
        "message_key": "warn.no_closed_loop"
      },
      {
        "code": "not_connected",
        "ref": "V1",
        "message_key": "warn.not_connected"
      },
      {
        "code": "not_connected",
        "ref": "R1",
        "message_key": "warn.not_connected"
      },
      {
        "code": "not_connected",
        "ref": "R2",
        "message_key": "warn.not_connected"
      },
      {
        "code": "not_connected",
        "ref": "R3",
        "message_key": "warn.not_connected"
      },
      {
        "code": "not_connected",
        "ref": "V2",
        "message_key": "warn.not_connected"
      },
      {
        "code": "not_connected",
        "ref": "R4",
        "message_key": "warn.not_connected"
      },
      {
        "code": "polarity_uncertain",
        "ref": "V1",
        "message_key": "warn.polarity_uncertain"
      },
      {
        "code": "polarity_uncertain",
        "ref": "V2",
        "message_key": "warn.polarity_uncertain"
      },
      {
        "code": "no_closed_loop",
        "ref": "isolated.V1.a",
        "message_key": "warn.no_closed_loop"
      },
      {
        "code": "no_closed_loop",
        "ref": "isolated.V1.b",
        "message_key": "warn.no_closed_loop"
      },
      {
        "code": "no_closed_loop",
        "ref": "isolated.R1.b",
        "message_key": "warn.no_closed_loop"
      },
      {
        "code": "no_closed_loop",
        "ref": "isolated.V2.a",
        "message_key": "warn.no_closed_loop"
      },
      {
        "code": "no_closed_loop",
        "ref": "n11",
        "message_key": "warn.no_closed_loop"
      },
      {
        "code": "no_closed_loop",
        "ref": "n20",
        "message_key": "warn.no_closed_loop"
      },
      {
        "code": "no_closed_loop",
        "ref": "n26",
        "message_key": "warn.no_closed_loop"
      },
      {
        "code": "dangling_wire",
        "ref": "p7",
        "message_key": "warn.dangling_wire"
      },
      {
        "code": "dangling_wire",
        "ref": "p14",
        "message_key": "warn.dangling_wire"
      },
      {
        "code": "dangling_wire",
        "ref": "p19",
        "message_key": "warn.dangling_wire"
      },
      {
        "code": "dangling_wire",
        "ref": "p22",
        "message_key": "warn.dangling_wire"
      },
      {
        "code": "dangling_wire",
        "ref": "p25",
        "message_key": "warn.dangling_wire"
      }
    ]
  },
  "trace": {
    "alternative_threshold": false,
    "repair": false,
    "terminals_snapped": 8,
    "terminals_floating": 4,
    "off_axis_snaps": 1,
    "gaps_bridged": 0,
    "stroke_width": 1.0,
    "ghosts": [
      {
        "bbox": [
          157,
          123,
          227,
          146
        ],
        "from": [
          163,
          129
        ],
        "to": [
          221,
          140
        ],
        "reason": "missing_part"
      }
    ]
  },
  "seconds": 1.6508915000013076,
  "scope": "Tracing-only replay on identical WP-A detections/texts; no gold topology accuracy."
}
```
