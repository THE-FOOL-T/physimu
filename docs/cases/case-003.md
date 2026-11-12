# Case 003: Screenshot 2026-10-30 234003.png

SHA-256: `5cf90536ee0df0f09ba2c19705ac579ca2fae4016f98b7ae3646189afec8ed51`. Read-only configured owner input; raster excluded from Git.

The 230 V source and 5 ohm resistor are read. Rotated labels remain weak, and two resistors are misclassified as switches by v2. The circuit still has no conducting loop.

Inspected annotated image: `.cache/round3/case-003.png` (local only).

Both engine paths were requested. Tesseract is not installed on this machine; there are no real Tesseract readings to report. EasyOCR EN/BN uses installed local models. Dual-engine selection is tested with mocks, not claimed as a local Tesseract benchmark.

## Frozen round-two evidence

The trace below records actual Hungarian selections (including recovery attempts). A selected candidate does not necessarily survive the final netlist. The old API did not retain every rejected pair; unselected candidates are reported as such rather than inventing a rejection distance.

|Raw text|Native box|Old parse|Actual selection (role, part, cost / dummy)|
|---|---|---|---|
|"P_t"|[298.0,0.0,365.0,12.999999999999998]|null|"not parseable"|
|"PdrtidLd"|[357.0,0.0,459.0,10.0]|null|"not parseable"|
|"5 52"|[198.0,9.0,242.0,35.0]|null|"not parseable"|
|"230 V"|[27.0,123.0,91.0,149.0]|{"label":null,"number":230.0,"unit":"V","confidence":0.85,"internal":false,"unknown":false}|[{"role":"value","component":"V1","cost":30.039542739622426,"dummy_cost":169.4593276977539},{"role":"value","component":"V1","cost":30.039542739622426,"dummy_cost":305.0267898559571}]|
|"4 9"|[201.0,130.0,246.0,156.0]|null|"not parseable"|
|"(a)"|[175.0,172.0,211.0,200.0]|null|"not parseable"|

## Current raw engine readings

|Engine / rotation|Raw text|Native box|Current parse in anchored context|
|---|---|---|---|
|"easyocr / 0"|"_t"|[298.0,0.0,365.0,12.999999999999998]|null|
|"easyocr / 0"|"5 52"|[198.0,9.0,242.0,35.0]|{"label":null,"number":5.0,"unit":"ohm","internal":false,"unknown":false,"has_prefix":false,"unit_inferred":true,"confidence":0.6,"emf_symbol":false,"normalized":"5 Ω","normalizations":["contextual_unit_lookalike"]}|
|"easyocr-crop / 0"|"M"|[180.0,34.0,248.0,62.0]|null|
|"easyocr / 0"|"L"|[244.0,37.0,255.0,54.0]|null|
|"easyocr / 0"|"32"|[323.0,56.0,353.0,82.0]|{"label":null,"number":32.0,"unit":"ohm","internal":false,"unknown":false,"has_prefix":false,"unit_inferred":true,"confidence":0.6,"emf_symbol":false,"normalized":"32","normalizations":["component_unit"]}|
|"easyocr / 0"|"6% N"|[198.0,58.0,282.0,116.0]|null|
|"easyocr / 0"|">"|[279.0,58.0,302.0,85.0]|null|
|"easyocr-crop / 0"|"3"|[294.0,59.0,327.0,95.0]|{"label":null,"number":3.0,"unit":"ohm","internal":false,"unknown":false,"has_prefix":false,"unit_inferred":true,"confidence":0.6,"emf_symbol":false,"normalized":"3","normalizations":["component_unit"]}|
|"easyocr / 0"|"{102"|[132.0,80.0,211.0,116.0]|null|
|"easyocr / 0"|"8"|[138.0,83.0,164.0,136.0]|{"label":null,"number":8.0,"unit":"ohm","internal":false,"unknown":false,"has_prefix":false,"unit_inferred":true,"confidence":0.6,"emf_symbol":false,"normalized":"8","normalizations":["component_unit"]}|
|"easyocr / 0"|"S"|[323.0,86.0,347.0,113.0]|null|
|"easyocr / 0"|"4"|[64.0,100.0,75.0,115.0]|{"label":null,"number":4.0,"unit":"V","internal":false,"unknown":false,"has_prefix":false,"unit_inferred":true,"confidence":0.6,"emf_symbol":false,"normalized":"4","normalizations":["component_unit"]}|
|"easyocr-crop / 0"|"~"|[95.0,100.0,120.0,115.0]|null|
|"easyocr-crop / 0"|"7"|[71.0,104.0,112.0,115.0]|{"label":null,"number":7.0,"unit":"V","internal":false,"unknown":false,"has_prefix":false,"unit_inferred":true,"confidence":0.6,"emf_symbol":false,"normalized":"7","normalizations":["component_unit"]}|
|"easyocr / 0"|"4"|[132.0,104.0,148.0,123.0]|{"label":null,"number":4.0,"unit":"V","internal":false,"unknown":false,"has_prefix":false,"unit_inferred":true,"confidence":0.6,"emf_symbol":false,"normalized":"4","normalizations":["component_unit"]}|
|"easyocr / 0"|"'"|[160.0,111.0,171.0,127.0]|null|
|"easyocr / 0"|"ST "|[71.0,116.0,114.0,127.0]|null|
|"easyocr-crop / 0"|"1"|[246.0,118.0,272.0,146.0]|{"label":null,"number":1.0,"unit":null,"internal":false,"unknown":false,"has_prefix":false,"unit_inferred":false,"confidence":0.55,"emf_symbol":false,"normalized":"1","normalizations":[]}|
|"easyocr / 0"|"230 V"|[35.0,123.0,91.0,149.0]|{"label":null,"number":230.0,"unit":"V","internal":false,"unknown":false,"has_prefix":false,"unit_inferred":false,"confidence":0.85,"emf_symbol":false,"normalized":"230 V","normalizations":[]}|
|"easyocr / 0"|"'"|[160.0,123.0,171.0,139.0]|null|
|"easyocr-crop / 0"|"45"|[201.0,130.0,246.0,156.0]|{"label":null,"number":45.0,"unit":null,"internal":false,"unknown":false,"has_prefix":false,"unit_inferred":false,"confidence":0.55,"emf_symbol":false,"normalized":"45","normalizations":[]}|
|"easyocr / 0"|"1"|[84.0,133.0,103.0,156.0]|{"label":null,"number":1.0,"unit":"V","internal":false,"unknown":false,"has_prefix":false,"unit_inferred":true,"confidence":0.6,"emf_symbol":false,"normalized":"1","normalizations":["component_unit"]}|
|"easyocr / 0"|"2"|[338.0,134.0,357.0,160.0]|{"label":null,"number":2.0,"unit":null,"internal":false,"unknown":false,"has_prefix":false,"unit_inferred":false,"confidence":0.55,"emf_symbol":false,"normalized":"2","normalizations":[]}|
|"easyocr-crop / 0"|"3v ."|[313.0,150.0,335.0,160.0]|{"label":null,"number":3.0,"unit":"V","internal":false,"unknown":false,"has_prefix":false,"unit_inferred":false,"confidence":0.85,"emf_symbol":false,"normalized":"3v .","normalizations":[]}|
|"easyocr / 0"|"od"|[326.0,150.0,357.0,160.0]|null|
|"easyocr-crop / 0"|"_"|[208.0,158.0,251.0,174.0]|null|
|"easyocr / 0"|"(a)"|[175.0,172.0,211.0,200.0]|null|

## Current association decisions

Every tested component/role pair includes its measured distance and rejection reason. `weak_context` covers a body/lead overlap, low confidence, contradictory bare readings or insufficient anchored support; it is deliberately conservative.

```json
[
  {
    "text": "_t",
    "bbox": [
      298.0,
      0.0,
      365.0,
      12.999999999999998
    ],
    "confidence": 0.0029008024544022707,
    "engine": "easyocr",
    "rotation": 0,
    "wire_overlap": false,
    "alternatives": [
      {
        "text": "F_Ii 1",
        "bbox": [
          298.0,
          0.0,
          365.0,
          12.999999999999998
        ],
        "confidence": 0.0007134225200705444,
        "engine": "easyocr-crop",
        "rotation": 0
      },
      {
        "text": "Al=e",
        "bbox": [
          298.0,
          0.0,
          365.0,
          12.999999999999998
        ],
        "confidence": 0.0005336062167771161,
        "engine": "easyocr-crop",
        "rotation": 0
      },
      {
        "text": "A~Sat4",
        "bbox": [
          298.0,
          0.0,
          365.0,
          12.999999999999998
        ],
        "confidence": 5.7561000590534234e-05,
        "engine": "easyocr-crop",
        "rotation": 0
      }
    ],
    "id": "t1",
    "raw": "_t",
    "parsed": null,
    "assignments": [],
    "outcome": "ignored",
    "reason": "not_parseable",
    "candidates": []
  },
  {
    "text": "5 52",
    "bbox": [
      198.0,
      9.0,
      242.0,
      35.0
    ],
    "confidence": 0.8988319039344788,
    "component_id": "R1",
    "context": "resistor",
    "engine": "easyocr",
    "rotation": 0,
    "wire_overlap": false,
    "alternatives": [
      {
        "text": "5 52",
        "bbox": [
          198.0,
          9.0,
          242.0,
          35.0
        ],
        "confidence": 0.7875956892967224,
        "engine": "easyocr-crop",
        "rotation": 0
      },
      {
        "text": "59",
        "bbox": [
          198.0,
          9.0,
          242.0,
          35.0
        ],
        "confidence": 0.91054210491467,
        "engine": "easyocr-crop",
        "rotation": 0
      },
      {
        "text": "59",
        "bbox": [
          198.0,
          9.0,
          242.0,
          35.0
        ],
        "confidence": 0.32575245309073153,
        "engine": "easyocr-crop",
        "rotation": 0
      }
    ],
    "id": "t2",
    "raw": "5 52",
    "parsed": {
      "label": null,
      "number": 5.0,
      "unit": "ohm",
      "internal": false,
      "unknown": false,
      "has_prefix": false,
      "unit_inferred": true,
      "confidence": 0.6,
      "emf_symbol": false,
      "normalized": "5 Ω",
      "normalizations": [
        "contextual_unit_lookalike"
      ]
    },
    "assignments": [
      {
        "component_id": "R1",
        "role": "value",
        "parsed": {
          "label": null,
          "number": 5.0,
          "unit": "ohm",
          "internal": false,
          "unknown": false,
          "has_prefix": false,
          "unit_inferred": true,
          "confidence": 0.6,
          "emf_symbol": false,
          "normalized": "5 Ω",
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
        "component_id": "R1",
        "role": "value",
        "distance": 12.71,
        "reason": "eligible"
      },
      {
        "component_id": "R2",
        "role": "value",
        "distance": 83.2,
        "reason": "weak_context"
      },
      {
        "component_id": "S1",
        "role": "value",
        "distance": 53.53,
        "reason": "unit_mismatch"
      },
      {
        "component_id": "R3",
        "role": "value",
        "distance": 82.94,
        "reason": "weak_context"
      },
      {
        "component_id": "S2",
        "role": "value",
        "distance": 96.66,
        "reason": "unit_mismatch"
      },
      {
        "component_id": "V1",
        "role": "value",
        "distance": 135.91,
        "reason": "too_far"
      }
    ],
    "assigned_to": "R1",
    "role": "value"
  },
  {
    "text": "M",
    "bbox": [
      180.0,
      34.0,
      248.0,
      62.0
    ],
    "confidence": 0.9705685154461072,
    "component_id": "R1",
    "context": "resistor",
    "engine": "easyocr-crop",
    "rotation": 0,
    "wire_overlap": false,
    "alternatives": [
      {
        "text": "M",
        "bbox": [
          180.0,
          34.0,
          248.0,
          62.0
        ],
        "confidence": 0.9480556819320363,
        "engine": "easyocr-crop",
        "rotation": 0
      },
      {
        "text": "M",
        "bbox": [
          180.0,
          34.0,
          248.0,
          62.0
        ],
        "confidence": 0.17595149080338857,
        "engine": "easyocr-crop",
        "rotation": 0
      },
      {
        "text": "M",
        "bbox": [
          180.0,
          34.0,
          248.0,
          62.0
        ],
        "confidence": 0.15037409944479752,
        "engine": "easyocr",
        "rotation": 0
      }
    ],
    "id": "t3",
    "raw": "M",
    "parsed": null,
    "assignments": [],
    "outcome": "ignored",
    "reason": "not_parseable",
    "candidates": []
  },
  {
    "text": "L",
    "bbox": [
      244.0,
      37.0,
      255.0,
      54.0
    ],
    "confidence": 0.7593817952331392,
    "component_id": "R1",
    "context": "resistor",
    "engine": "easyocr",
    "rotation": 0,
    "wire_overlap": false,
    "id": "t4",
    "raw": "L",
    "parsed": null,
    "assignments": [],
    "outcome": "ignored",
    "reason": "not_parseable",
    "candidates": []
  },
  {
    "text": "32",
    "bbox": [
      323.0,
      56.0,
      353.0,
      82.0
    ],
    "confidence": 0.5162119447983207,
    "component_id": "R2",
    "context": "resistor",
    "engine": "easyocr",
    "rotation": 0,
    "wire_overlap": false,
    "alternatives": [
      {
        "text": "152",
        "bbox": [
          323.0,
          56.0,
          353.0,
          82.0
        ],
        "confidence": 0.182973587232454,
        "engine": "easyocr-crop",
        "rotation": 0
      },
      {
        "text": "'2",
        "bbox": [
          323.0,
          56.0,
          353.0,
          82.0
        ],
        "confidence": 0.1328638880646333,
        "engine": "easyocr-crop",
        "rotation": 0
      },
      {
        "text": "'9",
        "bbox": [
          323.0,
          56.0,
          353.0,
          82.0
        ],
        "confidence": 0.11892947632060191,
        "engine": "easyocr-crop",
        "rotation": 0
      }
    ],
    "id": "t5",
    "raw": "32",
    "parsed": {
      "label": null,
      "number": 32.0,
      "unit": null,
      "internal": false,
      "unknown": false,
      "has_prefix": false,
      "unit_inferred": false,
      "confidence": 0.55,
      "emf_symbol": false,
      "normalized": "32",
      "normalizations": []
    },
    "assignments": [],
    "outcome": "unassigned",
    "reason": "too_far",
    "candidates": [
      {
        "component_id": "R1",
        "role": "value",
        "distance": 89.85,
        "reason": "weak_context"
      },
      {
        "component_id": "R2",
        "role": "value",
        "distance": 10.88,
        "reason": "weak_context"
      },
      {
        "component_id": "S1",
        "role": "value",
        "distance": 87.46,
        "reason": "unit_mismatch"
      },
      {
        "component_id": "R3",
        "role": "value",
        "distance": 174.57,
        "reason": "too_far"
      },
      {
        "component_id": "S2",
        "role": "value",
        "distance": 14.58,
        "reason": "unit_mismatch"
      },
      {
        "component_id": "V1",
        "role": "value",
        "distance": 228.55,
        "reason": "too_far"
      }
    ]
  },
  {
    "text": "6% N",
    "bbox": [
      198.0,
      58.0,
      282.0,
      116.0
    ],
    "confidence": 0.1141461580991745,
    "component_id": "R1",
    "context": "resistor",
    "engine": "easyocr",
    "rotation": 0,
    "wire_overlap": false,
    "id": "t6",
    "raw": "6% N",
    "parsed": null,
    "assignments": [],
    "outcome": "ignored",
    "reason": "not_parseable",
    "candidates": []
  },
  {
    "text": ">",
    "bbox": [
      279.0,
      58.0,
      302.0,
      85.0
    ],
    "confidence": 0.20243513865183616,
    "component_id": "R1",
    "context": "resistor",
    "engine": "easyocr",
    "rotation": 0,
    "wire_overlap": false,
    "id": "t7",
    "raw": ">",
    "parsed": null,
    "assignments": [],
    "outcome": "ignored",
    "reason": "not_parseable",
    "candidates": []
  },
  {
    "text": "3",
    "bbox": [
      294.0,
      59.0,
      327.0,
      95.0
    ],
    "confidence": 0.8326540091648873,
    "component_id": "R2",
    "context": "resistor",
    "engine": "easyocr-crop",
    "rotation": 0,
    "wire_overlap": false,
    "alternatives": [
      {
        "text": "13",
        "bbox": [
          294.0,
          59.0,
          327.0,
          95.0
        ],
        "confidence": 0.2920788270270934,
        "engine": "easyocr-crop",
        "rotation": 0
      },
      {
        "text": "3",
        "bbox": [
          294.0,
          59.0,
          327.0,
          95.0
        ],
        "confidence": 0.21980217377023692,
        "engine": "easyocr",
        "rotation": 0
      },
      {
        "text": "i",
        "bbox": [
          294.0,
          59.0,
          327.0,
          95.0
        ],
        "confidence": 0.14589037161614726,
        "engine": "easyocr-crop",
        "rotation": 0
      }
    ],
    "id": "t8",
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
        "component_id": "R1",
        "role": "value",
        "distance": 63.77,
        "reason": "weak_context"
      },
      {
        "component_id": "R2",
        "role": "value",
        "distance": 0.0,
        "reason": "weak_context"
      },
      {
        "component_id": "S1",
        "role": "value",
        "distance": 59.71,
        "reason": "unit_mismatch"
      },
      {
        "component_id": "R3",
        "role": "value",
        "distance": 146.62,
        "reason": "too_far"
      },
      {
        "component_id": "S2",
        "role": "value",
        "distance": 6.58,
        "reason": "unit_mismatch"
      },
      {
        "component_id": "V1",
        "role": "value",
        "distance": 200.17,
        "reason": "too_far"
      }
    ]
  },
  {
    "text": "{102",
    "bbox": [
      132.0,
      80.0,
      211.0,
      116.0
    ],
    "confidence": 0.4334700405597687,
    "component_id": "R1",
    "context": "resistor",
    "engine": "easyocr",
    "rotation": 0,
    "wire_overlap": false,
    "id": "t9",
    "raw": "{102",
    "parsed": null,
    "assignments": [],
    "outcome": "ignored",
    "reason": "not_parseable",
    "candidates": []
  },
  {
    "text": "8",
    "bbox": [
      138.0,
      83.0,
      164.0,
      136.0
    ],
    "confidence": 0.11418356856154688,
    "component_id": "R3",
    "context": "resistor",
    "engine": "easyocr",
    "rotation": 0,
    "wire_overlap": false,
    "alternatives": [
      {
        "text": "M",
        "bbox": [
          138.0,
          83.0,
          164.0,
          136.0
        ],
        "confidence": 0.23977753437265736,
        "engine": "easyocr-crop",
        "rotation": 90
      },
      {
        "text": "Mm",
        "bbox": [
          138.0,
          83.0,
          164.0,
          136.0
        ],
        "confidence": 0.19786849904545428,
        "engine": "easyocr-crop",
        "rotation": -90
      },
      {
        "text": "Wmm",
        "bbox": [
          138.0,
          83.0,
          164.0,
          136.0
        ],
        "confidence": 0.08383368610094627,
        "engine": "easyocr-crop",
        "rotation": 90
      },
      {
        "text": "Wt",
        "bbox": [
          138.0,
          83.0,
          164.0,
          136.0
        ],
        "confidence": 0.08279822448803563,
        "engine": "easyocr-crop",
        "rotation": 90
      }
    ],
    "id": "t10",
    "raw": "8",
    "parsed": {
      "label": null,
      "number": 8.0,
      "unit": null,
      "internal": false,
      "unknown": false,
      "has_prefix": false,
      "unit_inferred": false,
      "confidence": 0.55,
      "emf_symbol": false,
      "normalized": "8",
      "normalizations": []
    },
    "assignments": [],
    "outcome": "unassigned",
    "reason": "weak_context",
    "candidates": [
      {
        "component_id": "R1",
        "role": "value",
        "distance": 55.37,
        "reason": "weak_context"
      },
      {
        "component_id": "R2",
        "role": "value",
        "distance": 143.77,
        "reason": "too_far"
      },
      {
        "component_id": "S1",
        "role": "value",
        "distance": 68.21,
        "reason": "unit_mismatch"
      },
      {
        "component_id": "R3",
        "role": "value",
        "distance": 0.0,
        "reason": "weak_context"
      },
      {
        "component_id": "S2",
        "role": "value",
        "distance": 143.5,
        "reason": "unit_mismatch"
      },
      {
        "component_id": "V1",
        "role": "value",
        "distance": 38.71,
        "reason": "weak_context"
      }
    ]
  },
  {
    "text": "S",
    "bbox": [
      323.0,
      86.0,
      347.0,
      113.0
    ],
    "confidence": 0.15451874822961376,
    "component_id": "R2",
    "context": "resistor",
    "engine": "easyocr",
    "rotation": 0,
    "wire_overlap": false,
    "id": "t11",
    "raw": "S",
    "parsed": null,
    "assignments": [],
    "outcome": "ignored",
    "reason": "not_parseable",
    "candidates": []
  },
  {
    "text": "4",
    "bbox": [
      64.0,
      100.0,
      75.0,
      115.0
    ],
    "confidence": 0.005942274621450139,
    "component_id": "V1",
    "context": "dc_source",
    "engine": "easyocr",
    "rotation": 0,
    "wire_overlap": false,
    "alternatives": [
      {
        "text": "d",
        "bbox": [
          64.0,
          100.0,
          75.0,
          115.0
        ],
        "confidence": 0.078240015286557,
        "engine": "easyocr-crop",
        "rotation": -90
      },
      {
        "text": "U",
        "bbox": [
          64.0,
          100.0,
          75.0,
          115.0
        ],
        "confidence": 0.0060984910100896905,
        "engine": "easyocr-crop",
        "rotation": 90
      },
      {
        "text": "U",
        "bbox": [
          64.0,
          100.0,
          75.0,
          115.0
        ],
        "confidence": 0.005143703412643141,
        "engine": "easyocr-crop",
        "rotation": 90
      },
      {
        "text": "",
        "bbox": [
          64.0,
          100.0,
          75.0,
          115.0
        ],
        "confidence": 0.0,
        "engine": "easyocr-crop",
        "rotation": 90
      }
    ],
    "id": "t12",
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
        "component_id": "R1",
        "role": "value",
        "distance": 119.62,
        "reason": "weak_context"
      },
      {
        "component_id": "R2",
        "role": "value",
        "distance": 224.91,
        "reason": "too_far"
      },
      {
        "component_id": "S1",
        "role": "value",
        "distance": 149.71,
        "reason": "too_far"
      },
      {
        "component_id": "R3",
        "role": "value",
        "distance": 68.8,
        "reason": "weak_context"
      },
      {
        "component_id": "S2",
        "role": "value",
        "distance": 225.0,
        "reason": "too_far"
      },
      {
        "component_id": "V1",
        "role": "value",
        "distance": 2.1,
        "reason": "weak_context"
      }
    ]
  },
  {
    "text": "~",
    "bbox": [
      95.0,
      100.0,
      120.0,
      115.0
    ],
    "confidence": 0.6084043255882854,
    "component_id": "R3",
    "context": "resistor",
    "engine": "easyocr-crop",
    "rotation": 0,
    "wire_overlap": false,
    "alternatives": [
      {
        "text": "~",
        "bbox": [
          95.0,
          100.0,
          120.0,
          115.0
        ],
        "confidence": 0.6037246621648507,
        "engine": "easyocr-crop",
        "rotation": 0
      },
      {
        "text": "~",
        "bbox": [
          95.0,
          100.0,
          120.0,
          115.0
        ],
        "confidence": 0.10468133421309833,
        "engine": "easyocr-crop",
        "rotation": 0
      },
      {
        "text": "~",
        "bbox": [
          95.0,
          100.0,
          120.0,
          115.0
        ],
        "confidence": 0.09181252365250714,
        "engine": "easyocr",
        "rotation": 0
      }
    ],
    "id": "t13",
    "raw": "~",
    "parsed": null,
    "assignments": [],
    "outcome": "ignored",
    "reason": "not_parseable",
    "candidates": []
  },
  {
    "text": "7",
    "bbox": [
      71.0,
      104.0,
      112.0,
      115.0
    ],
    "confidence": 0.5818405282525987,
    "component_id": "V1",
    "context": "dc_source",
    "engine": "easyocr-crop",
    "rotation": 0,
    "wire_overlap": false,
    "alternatives": [
      {
        "text": "~T",
        "bbox": [
          71.0,
          104.0,
          112.0,
          115.0
        ],
        "confidence": 0.030739623583837847,
        "engine": "easyocr-crop",
        "rotation": 0
      },
      {
        "text": "~lt",
        "bbox": [
          71.0,
          104.0,
          112.0,
          115.0
        ],
        "confidence": 0.004519652992478211,
        "engine": "easyocr",
        "rotation": 0
      },
      {
        "text": "~lt",
        "bbox": [
          71.0,
          104.0,
          112.0,
          115.0
        ],
        "confidence": 0.0038597038094721646,
        "engine": "easyocr-crop",
        "rotation": 0
      }
    ],
    "id": "t14",
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
        "component_id": "R1",
        "role": "value",
        "distance": 100.49,
        "reason": "weak_context"
      },
      {
        "component_id": "R2",
        "role": "value",
        "distance": 203.07,
        "reason": "too_far"
      },
      {
        "component_id": "S1",
        "role": "value",
        "distance": 127.71,
        "reason": "too_far"
      },
      {
        "component_id": "R3",
        "role": "value",
        "distance": 46.8,
        "reason": "weak_context"
      },
      {
        "component_id": "S2",
        "role": "value",
        "distance": 203.0,
        "reason": "too_far"
      },
      {
        "component_id": "V1",
        "role": "value",
        "distance": 0.0,
        "reason": "weak_context"
      }
    ]
  },
  {
    "text": "4",
    "bbox": [
      132.0,
      104.0,
      148.0,
      123.0
    ],
    "confidence": 0.024792948992345742,
    "component_id": "V1",
    "context": "dc_source",
    "engine": "easyocr",
    "rotation": 0,
    "wire_overlap": false,
    "id": "t15",
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
        "component_id": "R1",
        "role": "value",
        "distance": 64.99,
        "reason": "weak_context"
      },
      {
        "component_id": "R2",
        "role": "value",
        "distance": 155.14,
        "reason": "too_far"
      },
      {
        "component_id": "S1",
        "role": "value",
        "distance": 79.21,
        "reason": "unit_mismatch"
      },
      {
        "component_id": "R3",
        "role": "value",
        "distance": 0.0,
        "reason": "weak_context"
      },
      {
        "component_id": "S2",
        "role": "value",
        "distance": 154.5,
        "reason": "unit_mismatch"
      },
      {
        "component_id": "V1",
        "role": "value",
        "distance": 27.71,
        "reason": "weak_context"
      }
    ]
  },
  {
    "text": "'",
    "bbox": [
      160.0,
      111.0,
      171.0,
      127.0
    ],
    "confidence": 0.32742293571545034,
    "component_id": "R3",
    "context": "resistor",
    "engine": "easyocr",
    "rotation": 0,
    "wire_overlap": false,
    "id": "t16",
    "raw": "'",
    "parsed": null,
    "assignments": [],
    "outcome": "ignored",
    "reason": "not_parseable",
    "candidates": []
  },
  {
    "text": "ST ",
    "bbox": [
      71.0,
      116.0,
      114.0,
      127.0
    ],
    "confidence": 0.0038250472367710965,
    "component_id": "V1",
    "context": "dc_source",
    "engine": "easyocr",
    "rotation": 0,
    "wire_overlap": false,
    "id": "t17",
    "raw": "ST ",
    "parsed": null,
    "assignments": [],
    "outcome": "ignored",
    "reason": "not_parseable",
    "candidates": []
  },
  {
    "text": "1",
    "bbox": [
      246.0,
      118.0,
      272.0,
      146.0
    ],
    "confidence": 0.5566364947532207,
    "component_id": "S1",
    "context": "switch",
    "engine": "easyocr-crop",
    "rotation": 0,
    "wire_overlap": false,
    "alternatives": [
      {
        "text": "1",
        "bbox": [
          246.0,
          118.0,
          272.0,
          146.0
        ],
        "confidence": 0.4266900581961295,
        "engine": "easyocr-crop",
        "rotation": 0
      },
      {
        "text": "1",
        "bbox": [
          246.0,
          118.0,
          272.0,
          146.0
        ],
        "confidence": 0.41436880190576986,
        "engine": "easyocr",
        "rotation": 0
      },
      {
        "text": "1",
        "bbox": [
          246.0,
          118.0,
          272.0,
          146.0
        ],
        "confidence": 0.34333958776813134,
        "engine": "easyocr-crop",
        "rotation": 0
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
        "component_id": "R1",
        "role": "value",
        "distance": 70.26,
        "reason": "weak_context"
      },
      {
        "component_id": "R2",
        "role": "value",
        "distance": 50.68,
        "reason": "weak_context"
      },
      {
        "component_id": "S1",
        "role": "value",
        "distance": 10.21,
        "reason": "unit_mismatch"
      },
      {
        "component_id": "R3",
        "role": "value",
        "distance": 94.99,
        "reason": "weak_context"
      },
      {
        "component_id": "S2",
        "role": "value",
        "distance": 35.5,
        "reason": "unit_mismatch"
      },
      {
        "component_id": "V1",
        "role": "value",
        "distance": 147.15,
        "reason": "too_far"
      }
    ]
  },
  {
    "text": "230 V",
    "bbox": [
      35.0,
      123.0,
      91.0,
      149.0
    ],
    "confidence": 0.8868075429879207,
    "component_id": "V1",
    "context": "dc_source",
    "engine": "easyocr",
    "rotation": 0,
    "wire_overlap": false,
    "id": "t19",
    "raw": "230 V",
    "parsed": {
      "label": null,
      "number": 230.0,
      "unit": "V",
      "internal": false,
      "unknown": false,
      "has_prefix": false,
      "unit_inferred": false,
      "confidence": 0.85,
      "emf_symbol": false,
      "normalized": "230 V",
      "normalizations": []
    },
    "assignments": [
      {
        "component_id": "V1",
        "role": "value",
        "parsed": {
          "label": null,
          "number": 230.0,
          "unit": "V",
          "internal": false,
          "unknown": false,
          "has_prefix": false,
          "unit_inferred": false,
          "confidence": 0.85,
          "emf_symbol": false,
          "normalized": "230 V",
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
        "distance": 138.44,
        "reason": "unit_mismatch"
      },
      {
        "component_id": "R2",
        "role": "value",
        "distance": 234.62,
        "reason": "too_far"
      },
      {
        "component_id": "S1",
        "role": "value",
        "distance": 156.54,
        "reason": "too_far"
      },
      {
        "component_id": "R3",
        "role": "value",
        "distance": 75.3,
        "reason": "unit_mismatch"
      },
      {
        "component_id": "S2",
        "role": "value",
        "distance": 231.5,
        "reason": "too_far"
      },
      {
        "component_id": "V1",
        "role": "value",
        "distance": 17.57,
        "reason": "eligible"
      }
    ],
    "assigned_to": "V1",
    "role": "value"
  },
  {
    "text": "'",
    "bbox": [
      160.0,
      123.0,
      171.0,
      139.0
    ],
    "confidence": 0.14018753718370025,
    "component_id": "R3",
    "context": "resistor",
    "engine": "easyocr",
    "rotation": 0,
    "wire_overlap": false,
    "id": "t20",
    "raw": "'",
    "parsed": null,
    "assignments": [],
    "outcome": "ignored",
    "reason": "not_parseable",
    "candidates": []
  },
  {
    "text": "45",
    "bbox": [
      201.0,
      130.0,
      246.0,
      156.0
    ],
    "confidence": 0.8093616625594537,
    "component_id": "S1",
    "context": "switch",
    "engine": "easyocr-crop",
    "rotation": 0,
    "wire_overlap": false,
    "alternatives": [
      {
        "text": "4 9",
        "bbox": [
          201.0,
          130.0,
          246.0,
          156.0
        ],
        "confidence": 0.5423205494880676,
        "engine": "easyocr",
        "rotation": 0
      },
      {
        "text": "4 9",
        "bbox": [
          201.0,
          130.0,
          246.0,
          156.0
        ],
        "confidence": 0.40279051661491394,
        "engine": "easyocr-crop",
        "rotation": 0
      },
      {
        "text": "45.\"",
        "bbox": [
          201.0,
          130.0,
          246.0,
          156.0
        ],
        "confidence": 0.40149966659811176,
        "engine": "easyocr-crop",
        "rotation": 0
      }
    ],
    "id": "t21",
    "raw": "45",
    "parsed": {
      "label": null,
      "number": 45.0,
      "unit": null,
      "internal": false,
      "unknown": false,
      "has_prefix": false,
      "unit_inferred": false,
      "confidence": 0.55,
      "emf_symbol": false,
      "normalized": "45",
      "normalizations": []
    },
    "assignments": [],
    "outcome": "unassigned",
    "reason": "too_far",
    "candidates": [
      {
        "component_id": "R1",
        "role": "value",
        "distance": 80.45,
        "reason": "weak_context"
      },
      {
        "component_id": "R2",
        "role": "value",
        "distance": 85.12,
        "reason": "weak_context"
      },
      {
        "component_id": "S1",
        "role": "value",
        "distance": 17.07,
        "reason": "unit_mismatch"
      },
      {
        "component_id": "R3",
        "role": "value",
        "distance": 59.85,
        "reason": "weak_context"
      },
      {
        "component_id": "S2",
        "role": "value",
        "distance": 71.0,
        "reason": "unit_mismatch"
      },
      {
        "component_id": "V1",
        "role": "value",
        "distance": 113.43,
        "reason": "too_far"
      }
    ]
  },
  {
    "text": "1",
    "bbox": [
      84.0,
      133.0,
      103.0,
      156.0
    ],
    "confidence": 0.12794484839857034,
    "component_id": "V1",
    "context": "dc_source",
    "engine": "easyocr",
    "rotation": 0,
    "wire_overlap": false,
    "id": "t22",
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
        "distance": 119.41,
        "reason": "weak_context"
      },
      {
        "component_id": "R2",
        "role": "value",
        "distance": 206.5,
        "reason": "too_far"
      },
      {
        "component_id": "S1",
        "role": "value",
        "distance": 127.08,
        "reason": "too_far"
      },
      {
        "component_id": "R3",
        "role": "value",
        "distance": 45.52,
        "reason": "weak_context"
      },
      {
        "component_id": "S2",
        "role": "value",
        "distance": 201.0,
        "reason": "too_far"
      },
      {
        "component_id": "V1",
        "role": "value",
        "distance": 23.82,
        "reason": "weak_context"
      }
    ]
  },
  {
    "text": "2",
    "bbox": [
      338.0,
      134.0,
      357.0,
      160.0
    ],
    "confidence": 0.8514694614040456,
    "component_id": "S2",
    "context": "switch",
    "engine": "easyocr",
    "rotation": 0,
    "wire_overlap": false,
    "alternatives": [
      {
        "text": "0",
        "bbox": [
          338.0,
          134.0,
          357.0,
          160.0
        ],
        "confidence": 0.5091446304942657,
        "engine": "easyocr-crop",
        "rotation": 90
      },
      {
        "text": "0",
        "bbox": [
          338.0,
          134.0,
          357.0,
          160.0
        ],
        "confidence": 0.4688580207045021,
        "engine": "easyocr-crop",
        "rotation": 90
      },
      {
        "text": "~",
        "bbox": [
          338.0,
          134.0,
          357.0,
          160.0
        ],
        "confidence": 0.1975655188276102,
        "engine": "easyocr-crop",
        "rotation": -90
      },
      {
        "text": "D",
        "bbox": [
          338.0,
          134.0,
          357.0,
          160.0
        ],
        "confidence": 0.15153856365205698,
        "engine": "easyocr-crop",
        "rotation": 90
      }
    ],
    "id": "t23",
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
        "distance": 130.22,
        "reason": "weak_context"
      },
      {
        "component_id": "R2",
        "role": "value",
        "distance": 55.46,
        "reason": "weak_context"
      },
      {
        "component_id": "S1",
        "role": "value",
        "distance": 98.98,
        "reason": "unit_mismatch"
      },
      {
        "component_id": "R3",
        "role": "value",
        "distance": 183.8,
        "reason": "too_far"
      },
      {
        "component_id": "S2",
        "role": "value",
        "distance": 4.71,
        "reason": "unit_mismatch"
      },
      {
        "component_id": "V1",
        "role": "value",
        "distance": 236.68,
        "reason": "too_far"
      }
    ]
  },
  {
    "text": "3v .",
    "bbox": [
      313.0,
      150.0,
      335.0,
      160.0
    ],
    "confidence": 0.012383486144244671,
    "component_id": "S2",
    "context": "switch",
    "engine": "easyocr-crop",
    "rotation": 0,
    "wire_overlap": false,
    "alternatives": [
      {
        "text": "Pv .",
        "bbox": [
          313.0,
          150.0,
          335.0,
          160.0
        ],
        "confidence": 0.017022352665662766,
        "engine": "easyocr",
        "rotation": 0
      }
    ],
    "id": "t24",
    "raw": "3v .",
    "parsed": {
      "label": null,
      "number": 3.0,
      "unit": "V",
      "internal": false,
      "unknown": false,
      "has_prefix": false,
      "unit_inferred": false,
      "confidence": 0.85,
      "emf_symbol": false,
      "normalized": "3v .",
      "normalizations": []
    },
    "assignments": [],
    "outcome": "unassigned",
    "reason": "too_far",
    "candidates": [
      {
        "component_id": "R1",
        "role": "value",
        "distance": 119.44,
        "reason": "unit_mismatch"
      },
      {
        "component_id": "R2",
        "role": "value",
        "distance": 59.58,
        "reason": "unit_mismatch"
      },
      {
        "component_id": "S1",
        "role": "value",
        "distance": 78.77,
        "reason": "unit_mismatch"
      },
      {
        "component_id": "R3",
        "role": "value",
        "distance": 161.06,
        "reason": "too_far"
      },
      {
        "component_id": "S2",
        "role": "value",
        "distance": 0.63,
        "reason": "unit_mismatch"
      },
      {
        "component_id": "V1",
        "role": "value",
        "distance": 214.48,
        "reason": "too_far"
      }
    ]
  },
  {
    "text": "od",
    "bbox": [
      326.0,
      150.0,
      357.0,
      160.0
    ],
    "confidence": 0.024702170370250867,
    "component_id": "S2",
    "context": "switch",
    "engine": "easyocr",
    "rotation": 0,
    "wire_overlap": false,
    "id": "t25",
    "raw": "od",
    "parsed": null,
    "assignments": [],
    "outcome": "ignored",
    "reason": "not_parseable",
    "candidates": []
  },
  {
    "text": "_",
    "bbox": [
      208.0,
      158.0,
      251.0,
      174.0
    ],
    "confidence": 0.32413451880259814,
    "engine": "easyocr-crop",
    "rotation": 0,
    "wire_overlap": true,
    "alternatives": [
      {
        "text": "5T7",
        "bbox": [
          208.0,
          158.0,
          251.0,
          174.0
        ],
        "confidence": 0.1269296258244985,
        "engine": "easyocr-crop",
        "rotation": 0
      },
      {
        "text": "\"S",
        "bbox": [
          208.0,
          158.0,
          251.0,
          174.0
        ],
        "confidence": 0.12568132568333407,
        "engine": "easyocr-crop",
        "rotation": 0
      },
      {
        "text": "z_",
        "bbox": [
          208.0,
          158.0,
          251.0,
          174.0
        ],
        "confidence": 0.05991832126404883,
        "engine": "easyocr",
        "rotation": 0
      }
    ],
    "id": "t26",
    "raw": "_",
    "parsed": null,
    "assignments": [],
    "outcome": "ignored",
    "reason": "not_parseable",
    "candidates": []
  },
  {
    "text": "(a)",
    "bbox": [
      175.0,
      172.0,
      211.0,
      200.0
    ],
    "confidence": 0.921283307924828,
    "engine": "easyocr",
    "rotation": 0,
    "wire_overlap": false,
    "id": "t27",
    "raw": "(a)",
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
|"before"|"R1"|"resistor"|null|{"number":10.0,"unit":"ohm","status":"assumed","source":"prior","confidence":0.0}|
|"before"|"R2"|"resistor"|null|{"number":10.0,"unit":"ohm","status":"assumed","source":"prior","confidence":0.0}|
|"before"|"S1"|"switch"|null|{"number":null,"unit":"ohm","status":"assumed","source":"prior","confidence":0.0}|
|"before"|"R3"|"resistor"|null|{"number":10.0,"unit":"ohm","status":"assumed","source":"prior","confidence":0.0}|
|"before"|"S2"|"switch"|null|{"number":null,"unit":"ohm","status":"assumed","source":"prior","confidence":0.0}|
|"before"|"V1"|"dc_source"|null|{"number":230.0,"unit":"V","status":"given","source":"ocr","confidence":0.5589479492961089}|
|"WP-A"|"R1"|"resistor"|null|{"number":5.0,"unit":"ohm","status":"given","source":"ocr","confidence":0.6,"unit_inferred":true}|
|"WP-A"|"R2"|"resistor"|null|{"number":4.7,"unit":"ohm","status":"assumed","source":"prior","confidence":0.0,"unit_inferred":false}|
|"WP-A"|"S1"|"switch"|null|{"number":1.0,"unit":"ohm","status":"assumed","source":"prior","confidence":0.0,"unit_inferred":false}|
|"WP-A"|"R3"|"resistor"|null|{"number":4.7,"unit":"ohm","status":"assumed","source":"prior","confidence":0.0,"unit_inferred":false}|
|"WP-A"|"S2"|"switch"|null|{"number":1.0,"unit":"ohm","status":"assumed","source":"prior","confidence":0.0,"unit_inferred":false}|
|"WP-A"|"V1"|"dc_source"|null|{"number":230.0,"unit":"V","status":"given","source":"ocr","confidence":0.85,"unit_inferred":false}|

WP-A graph: **9 nodes**; any computed nonzero current: **false**. This is not a topology accuracy score.

The OCR annotation shows components and text, not wire connectivity. WP-B adds wire overlays and records whether repairs improve the graph.

## WP-B tracing replay

Same WP-A detections and OCR; no detector/OCR rerun or gold topology claim. Wire overlay: `.cache/round3/wires/case-003.png` (local only).

```json
{
  "image": "Screenshot 2026-10-30 234003.png",
  "before": {
    "nodes": 9,
    "parts": 6,
    "disabled": 0,
    "provenance": "extracted",
    "nonzero_current": false,
    "score": 35,
    "warnings": [
      {
        "code": "unit_inferred",
        "ref": "R1",
        "message_key": "warn.unit_inferred"
      },
      {
        "code": "gap_bridged",
        "ref": null,
        "message_key": "warn.gap_bridged"
      },
      {
        "code": "uncertain_topology",
        "ref": "R2",
        "message_key": "warn.uncertain_topology"
      },
      {
        "code": "uncertain_topology",
        "ref": "S2",
        "message_key": "warn.uncertain_topology"
      },
      {
        "code": "no_closed_loop",
        "ref": null,
        "message_key": "warn.no_closed_loop"
      },
      {
        "code": "polarity_uncertain",
        "ref": "V1",
        "message_key": "warn.polarity_uncertain"
      },
      {
        "code": "no_closed_loop",
        "ref": "isolated.R2.b",
        "message_key": "warn.no_closed_loop"
      },
      {
        "code": "no_closed_loop",
        "ref": "isolated.S2.a",
        "message_key": "warn.no_closed_loop"
      },
      {
        "code": "no_closed_loop",
        "ref": "isolated.S2.b",
        "message_key": "warn.no_closed_loop"
      },
      {
        "code": "no_closed_loop",
        "ref": "n1",
        "message_key": "warn.no_closed_loop"
      },
      {
        "code": "no_closed_loop",
        "ref": "n8",
        "message_key": "warn.no_closed_loop"
      },
      {
        "code": "no_closed_loop",
        "ref": "n17",
        "message_key": "warn.no_closed_loop"
      },
      {
        "code": "no_closed_loop",
        "ref": "n23",
        "message_key": "warn.no_closed_loop"
      },
      {
        "code": "dangling_wire",
        "ref": "p4",
        "message_key": "warn.dangling_wire"
      },
      {
        "code": "dangling_wire",
        "ref": "p7",
        "message_key": "warn.dangling_wire"
      },
      {
        "code": "dangling_wire",
        "ref": "p9",
        "message_key": "warn.dangling_wire"
      },
      {
        "code": "dangling_wire",
        "ref": "p22",
        "message_key": "warn.dangling_wire"
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
        "ref": "p30",
        "message_key": "warn.dangling_wire"
      },
      {
        "code": "assumed_value",
        "ref": "R2",
        "message_key": "warn.assumed_value"
      },
      {
        "code": "assumed_value",
        "ref": "S1",
        "message_key": "warn.assumed_value"
      },
      {
        "code": "assumed_value",
        "ref": "R3",
        "message_key": "warn.assumed_value"
      },
      {
        "code": "assumed_value",
        "ref": "S2",
        "message_key": "warn.assumed_value"
      },
      {
        "code": "value_not_found",
        "ref": "R2",
        "message_key": "warn.value_not_found"
      },
      {
        "code": "value_not_found",
        "ref": "S1",
        "message_key": "warn.value_not_found"
      },
      {
        "code": "value_not_found",
        "ref": "R3",
        "message_key": "warn.value_not_found"
      },
      {
        "code": "value_not_found",
        "ref": "S2",
        "message_key": "warn.value_not_found"
      }
    ]
  },
  "after": {
    "nodes": 10,
    "parts": 6,
    "disabled": 0,
    "provenance": "partial",
    "nonzero_current": false,
    "score": 40,
    "warnings": [
      {
        "code": "gap_bridged",
        "ref": null,
        "message_key": "warn.gap_bridged"
      },
      {
        "code": "uncertain_topology",
        "ref": "R2",
        "message_key": "warn.uncertain_topology"
      },
      {
        "code": "uncertain_topology",
        "ref": "S1",
        "message_key": "warn.uncertain_topology"
      },
      {
        "code": "uncertain_topology",
        "ref": "S2",
        "message_key": "warn.uncertain_topology"
      },
      {
        "code": "uncertain_topology",
        "ref": "V1",
        "message_key": "warn.uncertain_topology"
      },
      {
        "code": "source_open_loop",
        "ref": "V1",
        "message_key": "warn.source_open_loop"
      },
      {
        "code": "no_closed_loop",
        "ref": null,
        "message_key": "warn.no_closed_loop"
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
        "ref": "S1",
        "message_key": "warn.not_connected"
      },
      {
        "code": "not_connected",
        "ref": "R3",
        "message_key": "warn.not_connected"
      },
      {
        "code": "not_connected",
        "ref": "S2",
        "message_key": "warn.not_connected"
      },
      {
        "code": "not_connected",
        "ref": "V1",
        "message_key": "warn.not_connected"
      },
      {
        "code": "polarity_uncertain",
        "ref": "V1",
        "message_key": "warn.polarity_uncertain"
      },
      {
        "code": "no_closed_loop",
        "ref": "isolated.R2.a",
        "message_key": "warn.no_closed_loop"
      },
      {
        "code": "no_closed_loop",
        "ref": "isolated.R2.b",
        "message_key": "warn.no_closed_loop"
      },
      {
        "code": "no_closed_loop",
        "ref": "isolated.S1.a",
        "message_key": "warn.no_closed_loop"
      },
      {
        "code": "no_closed_loop",
        "ref": "isolated.S1.b",
        "message_key": "warn.no_closed_loop"
      },
      {
        "code": "no_closed_loop",
        "ref": "isolated.S2.a",
        "message_key": "warn.no_closed_loop"
      },
      {
        "code": "no_closed_loop",
        "ref": "isolated.S2.b",
        "message_key": "warn.no_closed_loop"
      },
      {
        "code": "no_closed_loop",
        "ref": "isolated.V1.a",
        "message_key": "warn.no_closed_loop"
      },
      {
        "code": "no_closed_loop",
        "ref": "n16",
        "message_key": "warn.no_closed_loop"
      },
      {
        "code": "dangling_wire",
        "ref": "p8",
        "message_key": "warn.dangling_wire"
      },
      {
        "code": "dangling_wire",
        "ref": "p14",
        "message_key": "warn.dangling_wire"
      },
      {
        "code": "dangling_wire",
        "ref": "p18",
        "message_key": "warn.dangling_wire"
      },
      {
        "code": "dangling_wire",
        "ref": "p20",
        "message_key": "warn.dangling_wire"
      },
      {
        "code": "dangling_wire",
        "ref": "p24",
        "message_key": "warn.dangling_wire"
      }
    ]
  },
  "trace": {
    "alternative_threshold": false,
    "repair": false,
    "terminals_snapped": 5,
    "terminals_floating": 7,
    "off_axis_snaps": 0,
    "gaps_bridged": 1,
    "stroke_width": 1.0,
    "ghosts": []
  },
  "seconds": 2.0603134999983013,
  "scope": "Tracing-only replay on identical WP-A detections/texts; no gold topology accuracy."
}
```
