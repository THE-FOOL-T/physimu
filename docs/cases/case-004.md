# Case 004: Screenshot 2026-10-31 000926.png

SHA-256: `dcd116ab9daf34db3e1e6bc5874d9375a7e4e9732e4a76f9524c6044dbf2aa8d`. Read-only configured owner input; raster excluded from Git.

5 V, 3 ohm, 2 ohm and 10 ohm are assigned. E is no longer a resistor name. The second source is symbolic, and the detector mistakes a meter for a capacitor. A nonzero computed current does not establish correct tracing or electrical accuracy.

Inspected annotated image: `.cache/round3/case-004.png` (local only).

Both engine paths were requested. Tesseract is not installed on this machine; there are no real Tesseract readings to report. EasyOCR EN/BN uses installed local models. Dual-engine selection is tested with mocks, not claimed as a local Tesseract benchmark.

## Frozen round-two evidence

The trace below records actual Hungarian selections (including recovery attempts). A selected candidate does not necessarily survive the final netlist. The old API did not retain every rejected pair; unselected candidates are reported as such rather than inventing a rejection distance.

|Raw text|Native box|Old parse|Actual selection (role, part, cost / dummy)|
|---|---|---|---|
|"5V"|[236.0,4.0,279.0,29.0]|{"label":null,"number":5.0,"unit":"V","confidence":0.85,"internal":false,"unknown":false}|[{"role":"value","component":"V1","cost":14.45909704295411,"dummy_cost":131.7129364013672},{"role":"value","component":"retry.7.V2","cost":116.92627300312218,"dummy_cost":346.50975036621094}]|
|"Cih"|[149.0,14.0,275.0,62.0]|null|"not parseable"|
|"Civ ["|[23.0,28.0,167.0,118.0]|null|"not parseable"|
|"R"|[186.0,50.0,215.0,75.0]|null|"not parseable"|
|"Fw "|[151.0,66.0,273.0,94.0]|null|"not parseable"|
|"L "|[148.0,90.0,273.0,134.0]|null|"not parseable"|
|"a"|[19.0,110.0,47.0,129.0]|null|"not parseable"|
|"10 9"|[110.0,198.0,162.0,223.0]|null|"not parseable"|
|"E"|[224.0,199.0,251.0,225.0]|{"label":"E","number":null,"unit":null,"confidence":0.6,"internal":false,"unknown":false}|[{"role":"name","component":"R4","cost":111.7673650059022,"dummy_cost":264.0044174194336},{"role":"name","component":"R4","cost":111.7673650059022,"dummy_cost":475.2079513549804}]|

## Current raw engine readings

|Engine / rotation|Raw text|Native box|Current parse in anchored context|
|---|---|---|---|
|"easyocr / 0"|"5V"|[236.0,4.0,279.0,29.0]|{"label":null,"number":5.0,"unit":"V","internal":false,"unknown":false,"has_prefix":false,"unit_inferred":false,"confidence":0.85,"emf_symbol":false,"normalized":"5V","normalizations":[]}|
|"easyocr / 0"|"3 Q"|[174.0,14.0,216.0,34.0]|{"label":null,"number":3.0,"unit":"ohm","internal":false,"unknown":false,"has_prefix":false,"unit_inferred":true,"confidence":0.6,"emf_symbol":false,"normalized":"3 Ω","normalizations":["contextual_unit_lookalike"]}|
|"easyocr-crop / 0"|"i"|[202.0,14.0,242.0,62.0]|null|
|"easyocr-crop / 90"|"2"|[238.0,25.0,252.0,55.0]|{"label":null,"number":2.0,"unit":"V","internal":false,"unknown":false,"has_prefix":false,"unit_inferred":true,"confidence":0.6,"emf_symbol":false,"normalized":"2","normalizations":["component_unit"]}|
|"easyocr / 0"|"h"|[248.0,26.0,288.0,73.0]|null|
|"easyocr-crop / 0"|"2 9"|[71.0,28.0,117.0,50.0]|{"label":null,"number":2.0,"unit":"ohm","internal":false,"unknown":false,"has_prefix":false,"unit_inferred":true,"confidence":0.6,"emf_symbol":false,"normalized":"2 Ω","normalizations":["contextual_unit_lookalike"]}|
|"easyocr-crop / 0"|"M"|[174.0,30.0,221.0,50.0]|null|
|"easyocr / 0"|"T"|[136.0,34.0,178.0,69.0]|null|
|"easyocr-crop / 0"|"M"|[66.0,46.0,130.0,71.0]|null|
|"easyocr / 0"|"R"|[186.0,50.0,215.0,75.0]|null|
|"easyocr / 0"|"4u"|[231.0,51.0,251.0,62.0]|{"label":null,"number":4e-06,"unit":"V","internal":false,"unknown":false,"has_prefix":true,"unit_inferred":true,"confidence":0.6,"emf_symbol":false,"normalized":"4u","normalizations":["component_unit"]}|
|"easyocr / 0"|"3"|[26.0,52.0,70.0,71.0]|{"label":null,"number":3.0,"unit":"ohm","internal":false,"unknown":false,"has_prefix":false,"unit_inferred":true,"confidence":0.6,"emf_symbol":false,"normalized":"3","normalizations":["component_unit"]}|
|"easyocr / 0"|"18"|[257.0,55.0,337.0,188.0]|{"label":null,"number":18.0,"unit":null,"internal":false,"unknown":false,"has_prefix":false,"unit_inferred":false,"confidence":0.55,"emf_symbol":false,"normalized":"18","normalizations":[]}|
|"easyocr / 0"|"F"|[151.0,66.0,246.0,88.0]|null|
|"easyocr / 0"|"M "|[202.0,67.0,273.0,91.0]|null|
|"easyocr / 0"|"L@"|[148.0,85.0,258.0,127.0]|null|
|"easyocr / 0"|"49"|[19.0,110.0,47.0,129.0]|{"label":null,"number":49.0,"unit":null,"internal":false,"unknown":false,"has_prefix":false,"unit_inferred":false,"confidence":0.55,"emf_symbol":false,"normalized":"49","normalizations":[]}|
|"easyocr / 0"|"S"|[183.0,119.0,224.0,134.0]|null|
|"easyocr / 0"|"1"|[22.0,156.0,41.0,186.0]|{"label":null,"number":1.0,"unit":null,"internal":false,"unknown":false,"has_prefix":false,"unit_inferred":false,"confidence":0.55,"emf_symbol":false,"normalized":"1","normalizations":[]}|
|"easyocr-crop / 0"|"4"|[193.0,157.0,233.0,205.0]|{"label":null,"number":4.0,"unit":"V","internal":false,"unknown":false,"has_prefix":false,"unit_inferred":true,"confidence":0.6,"emf_symbol":false,"normalized":"4","normalizations":["component_unit"]}|
|"easyocr-crop / 90"|"15"|[229.0,162.0,244.0,199.0]|{"label":null,"number":15.0,"unit":"V","internal":false,"unknown":false,"has_prefix":false,"unit_inferred":true,"confidence":0.6,"emf_symbol":false,"normalized":"15","normalizations":["component_unit"]}|
|"easyocr / 0"|"1"|[240.0,164.0,252.0,188.0]|{"label":null,"number":1.0,"unit":"V","internal":false,"unknown":false,"has_prefix":false,"unit_inferred":true,"confidence":0.6,"emf_symbol":false,"normalized":"1","normalizations":["component_unit"]}|
|"easyocr / 0"|""|[169.0,169.0,224.0,191.0]|null|
|"easyocr / 0"|"M"|[108.0,170.0,173.0,194.0]|null|
|"easyocr / 0"|"1"|[240.0,180.0,252.0,199.0]|{"label":null,"number":1.0,"unit":"V","internal":false,"unknown":false,"has_prefix":false,"unit_inferred":true,"confidence":0.6,"emf_symbol":false,"normalized":"1","normalizations":["component_unit"]}|
|"easyocr / 0"|"Uo"|[221.0,195.0,242.0,205.0]|null|
|"easyocr / 0"|"10 9"|[110.0,198.0,162.0,223.0]|{"label":null,"number":10.0,"unit":"ohm","internal":false,"unknown":false,"has_prefix":false,"unit_inferred":true,"confidence":0.6,"emf_symbol":false,"normalized":"10 Ω","normalizations":["contextual_unit_lookalike"]}|
|"easyocr / 0"|"'"|[240.0,199.0,251.0,214.0]|null|

## Current association decisions

Every tested component/role pair includes its measured distance and rejection reason. `weak_context` covers a body/lead overlap, low confidence, contradictory bare readings or insufficient anchored support; it is deliberately conservative.

```json
[
  {
    "text": "5V",
    "bbox": [
      236.0,
      4.0,
      279.0,
      29.0
    ],
    "confidence": 0.8586043236469733,
    "component_id": "V1",
    "context": "dc_source",
    "engine": "easyocr",
    "rotation": 0,
    "wire_overlap": false,
    "id": "t1",
    "raw": "5V",
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
      "normalized": "5V",
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
          "normalized": "5V",
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
        "distance": 10.45,
        "reason": "eligible"
      },
      {
        "component_id": "R1",
        "role": "value",
        "distance": 38.96,
        "reason": "unit_mismatch"
      },
      {
        "component_id": "R2",
        "role": "value",
        "distance": 130.57,
        "reason": "unit_mismatch"
      },
      {
        "component_id": "R3",
        "role": "value",
        "distance": 65.02,
        "reason": "unit_mismatch"
      },
      {
        "component_id": "V2",
        "role": "value",
        "distance": 146.31,
        "reason": "too_far"
      },
      {
        "component_id": "C1",
        "role": "value",
        "distance": 147.26,
        "reason": "too_far"
      },
      {
        "component_id": "R4",
        "role": "value",
        "distance": 175.72,
        "reason": "too_far"
      }
    ],
    "assigned_to": "V1",
    "role": "value"
  },
  {
    "text": "3 Q",
    "bbox": [
      174.0,
      14.0,
      216.0,
      34.0
    ],
    "confidence": 0.41846257581284724,
    "component_id": "R1",
    "context": "resistor",
    "engine": "easyocr",
    "rotation": 0,
    "wire_overlap": false,
    "alternatives": [
      {
        "text": "3 Q",
        "bbox": [
          174.0,
          14.0,
          216.0,
          34.0
        ],
        "confidence": 0.361908634223385,
        "engine": "easyocr-crop",
        "rotation": 0
      },
      {
        "text": "39",
        "bbox": [
          174.0,
          14.0,
          216.0,
          34.0
        ],
        "confidence": 0.988943986650017,
        "engine": "easyocr-crop",
        "rotation": 0
      },
      {
        "text": "39",
        "bbox": [
          174.0,
          14.0,
          216.0,
          34.0
        ],
        "confidence": 0.8334620774648767,
        "engine": "easyocr-crop",
        "rotation": 0
      }
    ],
    "id": "t2",
    "raw": "3 Q",
    "parsed": {
      "label": null,
      "number": 3.0,
      "unit": "ohm",
      "internal": false,
      "unknown": false,
      "has_prefix": false,
      "unit_inferred": true,
      "confidence": 0.6,
      "emf_symbol": false,
      "normalized": "3 Ω",
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
          "number": 3.0,
          "unit": "ohm",
          "internal": false,
          "unknown": false,
          "has_prefix": false,
          "unit_inferred": true,
          "confidence": 0.6,
          "emf_symbol": false,
          "normalized": "3 Ω",
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
        "distance": 43.91,
        "reason": "weak_context"
      },
      {
        "component_id": "R1",
        "role": "value",
        "distance": 6.93,
        "reason": "eligible"
      },
      {
        "component_id": "R2",
        "role": "value",
        "distance": 68.37,
        "reason": "weak_context"
      },
      {
        "component_id": "R3",
        "role": "value",
        "distance": 46.27,
        "reason": "weak_context"
      },
      {
        "component_id": "V2",
        "role": "value",
        "distance": 142.43,
        "reason": "too_far"
      },
      {
        "component_id": "C1",
        "role": "value",
        "distance": 143.44,
        "reason": "too_far"
      },
      {
        "component_id": "R4",
        "role": "value",
        "distance": 148.22,
        "reason": "too_far"
      }
    ],
    "assigned_to": "R1",
    "role": "value"
  },
  {
    "text": "i",
    "bbox": [
      202.0,
      14.0,
      242.0,
      62.0
    ],
    "confidence": 0.21706064760407173,
    "component_id": "V1",
    "context": "dc_source",
    "engine": "easyocr-crop",
    "rotation": 0,
    "wire_overlap": false,
    "alternatives": [
      {
        "text": "m",
        "bbox": [
          202.0,
          14.0,
          242.0,
          62.0
        ],
        "confidence": 0.18653930440371003,
        "engine": "easyocr",
        "rotation": 0
      },
      {
        "text": "M",
        "bbox": [
          202.0,
          14.0,
          242.0,
          62.0
        ],
        "confidence": 0.055702506712205,
        "engine": "easyocr-crop",
        "rotation": 0
      },
      {
        "text": "m",
        "bbox": [
          202.0,
          14.0,
          242.0,
          62.0
        ],
        "confidence": 0.03845970300175616,
        "engine": "easyocr-crop",
        "rotation": 0
      }
    ],
    "id": "t3",
    "raw": "i",
    "parsed": null,
    "assignments": [],
    "outcome": "ignored",
    "reason": "not_parseable",
    "candidates": []
  },
  {
    "text": "2",
    "bbox": [
      238.0,
      25.0,
      252.0,
      55.0
    ],
    "confidence": 0.3732598212789675,
    "component_id": "V1",
    "context": "dc_source",
    "engine": "easyocr-crop",
    "rotation": 90,
    "wire_overlap": false,
    "alternatives": [
      {
        "text": "1",
        "bbox": [
          238.0,
          25.0,
          252.0,
          55.0
        ],
        "confidence": 0.09029991298325513,
        "engine": "easyocr-crop",
        "rotation": 90
      },
      {
        "text": "1",
        "bbox": [
          238.0,
          25.0,
          252.0,
          55.0
        ],
        "confidence": 0.07660946668350821,
        "engine": "easyocr-crop",
        "rotation": 90
      },
      {
        "text": "4",
        "bbox": [
          238.0,
          25.0,
          252.0,
          55.0
        ],
        "confidence": 0.04243334183230396,
        "engine": "easyocr-crop",
        "rotation": -90
      },
      {
        "text": "I:",
        "bbox": [
          238.0,
          25.0,
          252.0,
          55.0
        ],
        "confidence": 0.16133785723138094,
        "engine": "easyocr",
        "rotation": 0
      }
    ],
    "id": "t4",
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
        "component_id": "V1",
        "role": "value",
        "distance": 0.0,
        "reason": "weak_context"
      },
      {
        "component_id": "R1",
        "role": "value",
        "distance": 23.69,
        "reason": "weak_context"
      },
      {
        "component_id": "R2",
        "role": "value",
        "distance": 114.77,
        "reason": "weak_context"
      },
      {
        "component_id": "R3",
        "role": "value",
        "distance": 38.67,
        "reason": "weak_context"
      },
      {
        "component_id": "V2",
        "role": "value",
        "distance": 122.19,
        "reason": "too_far"
      },
      {
        "component_id": "C1",
        "role": "value",
        "distance": 123.12,
        "reason": "too_far"
      },
      {
        "component_id": "R4",
        "role": "value",
        "distance": 149.1,
        "reason": "too_far"
      }
    ]
  },
  {
    "text": "h",
    "bbox": [
      248.0,
      26.0,
      288.0,
      73.0
    ],
    "confidence": 0.5142646730851688,
    "component_id": "V1",
    "context": "dc_source",
    "engine": "easyocr",
    "rotation": 0,
    "wire_overlap": false,
    "id": "t5",
    "raw": "h",
    "parsed": null,
    "assignments": [],
    "outcome": "ignored",
    "reason": "not_parseable",
    "candidates": []
  },
  {
    "text": "2 9",
    "bbox": [
      71.0,
      28.0,
      117.0,
      50.0
    ],
    "confidence": 0.6394118252042894,
    "component_id": "R2",
    "context": "resistor",
    "engine": "easyocr-crop",
    "rotation": 0,
    "wire_overlap": false,
    "alternatives": [
      {
        "text": "232",
        "bbox": [
          71.0,
          28.0,
          117.0,
          50.0
        ],
        "confidence": 0.8800390781814172,
        "engine": "easyocr",
        "rotation": 0
      },
      {
        "text": "25",
        "bbox": [
          71.0,
          28.0,
          117.0,
          50.0
        ],
        "confidence": 0.265183068889315,
        "engine": "easyocr-crop",
        "rotation": 0
      },
      {
        "text": "{20",
        "bbox": [
          71.0,
          28.0,
          117.0,
          50.0
        ],
        "confidence": 0.13987097229438517,
        "engine": "easyocr-crop",
        "rotation": 0
      }
    ],
    "id": "t6",
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
        "distance": 144.87,
        "reason": "too_far"
      },
      {
        "component_id": "R1",
        "role": "value",
        "distance": 80.09,
        "reason": "weak_context"
      },
      {
        "component_id": "R2",
        "role": "value",
        "distance": 7.43,
        "reason": "eligible"
      },
      {
        "component_id": "R3",
        "role": "value",
        "distance": 85.4,
        "reason": "weak_context"
      },
      {
        "component_id": "V2",
        "role": "value",
        "distance": 183.11,
        "reason": "too_far"
      },
      {
        "component_id": "C1",
        "role": "value",
        "distance": 184.11,
        "reason": "too_far"
      },
      {
        "component_id": "R4",
        "role": "value",
        "distance": 132.39,
        "reason": "too_far"
      }
    ],
    "assigned_to": "R2",
    "role": "value"
  },
  {
    "text": "M",
    "bbox": [
      174.0,
      30.0,
      221.0,
      50.0
    ],
    "confidence": 0.866177312600712,
    "component_id": "R1",
    "context": "resistor",
    "engine": "easyocr-crop",
    "rotation": 0,
    "wire_overlap": false,
    "alternatives": [
      {
        "text": "M",
        "bbox": [
          174.0,
          30.0,
          221.0,
          50.0
        ],
        "confidence": 0.3029337505563632,
        "engine": "easyocr",
        "rotation": 0
      },
      {
        "text": "M",
        "bbox": [
          174.0,
          30.0,
          221.0,
          50.0
        ],
        "confidence": 0.26873177619393473,
        "engine": "easyocr-crop",
        "rotation": 0
      },
      {
        "text": "M",
        "bbox": [
          174.0,
          30.0,
          221.0,
          50.0
        ],
        "confidence": 0.24532627716054378,
        "engine": "easyocr-crop",
        "rotation": 0
      }
    ],
    "id": "t7",
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
      136.0,
      34.0,
      178.0,
      69.0
    ],
    "confidence": 0.27556320715618554,
    "component_id": "R1",
    "context": "resistor",
    "engine": "easyocr",
    "rotation": 0,
    "wire_overlap": false,
    "id": "t8",
    "raw": "T",
    "parsed": null,
    "assignments": [],
    "outcome": "ignored",
    "reason": "not_parseable",
    "candidates": []
  },
  {
    "text": "M",
    "bbox": [
      66.0,
      46.0,
      130.0,
      71.0
    ],
    "confidence": 0.9086025926549759,
    "component_id": "R2",
    "context": "resistor",
    "engine": "easyocr-crop",
    "rotation": 0,
    "wire_overlap": false,
    "alternatives": [
      {
        "text": "M",
        "bbox": [
          66.0,
          46.0,
          130.0,
          71.0
        ],
        "confidence": 0.744329324001459,
        "engine": "easyocr-crop",
        "rotation": 0
      },
      {
        "text": "M",
        "bbox": [
          66.0,
          46.0,
          130.0,
          71.0
        ],
        "confidence": 0.7228961855746583,
        "engine": "easyocr-crop",
        "rotation": 0
      },
      {
        "text": "M",
        "bbox": [
          66.0,
          46.0,
          130.0,
          71.0
        ],
        "confidence": 0.7002704164959859,
        "engine": "easyocr",
        "rotation": 0
      }
    ],
    "id": "t9",
    "raw": "M",
    "parsed": null,
    "assignments": [],
    "outcome": "ignored",
    "reason": "not_parseable",
    "candidates": []
  },
  {
    "text": "R",
    "bbox": [
      186.0,
      50.0,
      215.0,
      75.0
    ],
    "confidence": 0.999860768396502,
    "component_id": "R1",
    "context": "resistor",
    "engine": "easyocr",
    "rotation": 0,
    "wire_overlap": false,
    "id": "t10",
    "raw": "R",
    "parsed": null,
    "assignments": [],
    "outcome": "ignored",
    "reason": "not_parseable",
    "candidates": []
  },
  {
    "text": "4u",
    "bbox": [
      231.0,
      51.0,
      251.0,
      62.0
    ],
    "confidence": 0.006237039464950679,
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
        "distance": 0.62,
        "reason": "weak_context"
      },
      {
        "component_id": "R1",
        "role": "value",
        "distance": 20.55,
        "reason": "weak_context"
      },
      {
        "component_id": "R2",
        "role": "value",
        "distance": 110.59,
        "reason": "weak_context"
      },
      {
        "component_id": "R3",
        "role": "value",
        "distance": 24.33,
        "reason": "weak_context"
      },
      {
        "component_id": "V2",
        "role": "value",
        "distance": 105.69,
        "reason": "too_far"
      },
      {
        "component_id": "C1",
        "role": "value",
        "distance": 106.61,
        "reason": "too_far"
      },
      {
        "component_id": "R4",
        "role": "value",
        "distance": 132.79,
        "reason": "too_far"
      }
    ]
  },
  {
    "text": "3",
    "bbox": [
      26.0,
      52.0,
      70.0,
      71.0
    ],
    "confidence": 0.026245530645276682,
    "component_id": "R2",
    "context": "resistor",
    "engine": "easyocr",
    "rotation": 0,
    "wire_overlap": true,
    "id": "t12",
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
    "reason": "weak_context",
    "candidates": [
      {
        "component_id": "V1",
        "role": "value",
        "distance": 190.95,
        "reason": "too_far"
      },
      {
        "component_id": "R1",
        "role": "value",
        "distance": 126.56,
        "reason": "too_far"
      },
      {
        "component_id": "R2",
        "role": "value",
        "distance": 18.54,
        "reason": "weak_context"
      },
      {
        "component_id": "R3",
        "role": "value",
        "distance": 125.78,
        "reason": "too_far"
      },
      {
        "component_id": "V2",
        "role": "value",
        "distance": 207.54,
        "reason": "too_far"
      },
      {
        "component_id": "C1",
        "role": "value",
        "distance": 208.44,
        "reason": "too_far"
      },
      {
        "component_id": "R4",
        "role": "value",
        "distance": 124.77,
        "reason": "weak_context"
      }
    ]
  },
  {
    "text": "18",
    "bbox": [
      257.0,
      55.0,
      337.0,
      188.0
    ],
    "confidence": 0.16640616405836656,
    "engine": "easyocr",
    "rotation": 0,
    "wire_overlap": false,
    "alternatives": [
      {
        "text": "L0T",
        "bbox": [
          257.0,
          55.0,
          337.0,
          188.0
        ],
        "confidence": 0.4044375515407054,
        "engine": "easyocr-crop",
        "rotation": 90
      },
      {
        "text": "~0T",
        "bbox": [
          257.0,
          55.0,
          337.0,
          188.0
        ],
        "confidence": 0.3732606656871296,
        "engine": "easyocr-crop",
        "rotation": 90
      },
      {
        "text": "LOT",
        "bbox": [
          257.0,
          55.0,
          337.0,
          188.0
        ],
        "confidence": 0.24614559953263315,
        "engine": "easyocr-crop",
        "rotation": 90
      },
      {
        "text": "Do",
        "bbox": [
          257.0,
          55.0,
          337.0,
          188.0
        ],
        "confidence": 0.16407695583462745,
        "engine": "easyocr-crop",
        "rotation": -90
      }
    ],
    "id": "t13",
    "raw": "18",
    "parsed": {
      "label": null,
      "number": 18.0,
      "unit": null,
      "internal": false,
      "unknown": false,
      "has_prefix": false,
      "unit_inferred": false,
      "confidence": 0.55,
      "emf_symbol": false,
      "normalized": "18",
      "normalizations": []
    },
    "assignments": [],
    "outcome": "unassigned",
    "reason": "too_far",
    "candidates": [
      {
        "component_id": "V1",
        "role": "value",
        "distance": 79.2,
        "reason": "too_far"
      },
      {
        "component_id": "R1",
        "role": "value",
        "distance": 103.71,
        "reason": "too_far"
      },
      {
        "component_id": "R2",
        "role": "value",
        "distance": 173.84,
        "reason": "too_far"
      },
      {
        "component_id": "R3",
        "role": "value",
        "distance": 82.39,
        "reason": "weak_context"
      },
      {
        "component_id": "V2",
        "role": "value",
        "distance": 66.75,
        "reason": "weak_context"
      },
      {
        "component_id": "C1",
        "role": "value",
        "distance": 67.68,
        "reason": "weak_context"
      },
      {
        "component_id": "R4",
        "role": "value",
        "distance": 133.33,
        "reason": "too_far"
      }
    ]
  },
  {
    "text": "F",
    "bbox": [
      151.0,
      66.0,
      246.0,
      88.0
    ],
    "confidence": 0.26204222814132905,
    "component_id": "R1",
    "context": "resistor",
    "engine": "easyocr",
    "rotation": 0,
    "wire_overlap": false,
    "alternatives": [
      {
        "text": "F",
        "bbox": [
          151.0,
          72.0,
          181.0,
          94.0
        ],
        "confidence": 0.12978188492663723,
        "engine": "easyocr",
        "rotation": 0
      }
    ],
    "id": "t14",
    "raw": "F",
    "parsed": null,
    "assignments": [],
    "outcome": "ignored",
    "reason": "not_parseable",
    "candidates": []
  },
  {
    "text": "M ",
    "bbox": [
      202.0,
      67.0,
      273.0,
      91.0
    ],
    "confidence": 0.12317118185542321,
    "component_id": "V1",
    "context": "dc_source",
    "engine": "easyocr",
    "rotation": 0,
    "wire_overlap": false,
    "id": "t15",
    "raw": "M ",
    "parsed": null,
    "assignments": [],
    "outcome": "ignored",
    "reason": "not_parseable",
    "candidates": []
  },
  {
    "text": "L@",
    "bbox": [
      148.0,
      85.0,
      258.0,
      127.0
    ],
    "confidence": 0.9890355693222611,
    "component_id": "R3",
    "context": "resistor",
    "engine": "easyocr",
    "rotation": 0,
    "wire_overlap": false,
    "alternatives": [
      {
        "text": "L@",
        "bbox": [
          148.0,
          85.0,
          258.0,
          127.0
        ],
        "confidence": 0.981879632822634,
        "engine": "easyocr-crop",
        "rotation": 0
      },
      {
        "text": "L@",
        "bbox": [
          148.0,
          85.0,
          258.0,
          127.0
        ],
        "confidence": 0.9499869524188549,
        "engine": "easyocr-crop",
        "rotation": 0
      },
      {
        "text": "L@",
        "bbox": [
          148.0,
          85.0,
          258.0,
          127.0
        ],
        "confidence": 0.7739254640260553,
        "engine": "easyocr-crop",
        "rotation": 0
      }
    ],
    "id": "t16",
    "raw": "L@",
    "parsed": null,
    "assignments": [],
    "outcome": "ignored",
    "reason": "not_parseable",
    "candidates": []
  },
  {
    "text": "49",
    "bbox": [
      19.0,
      110.0,
      47.0,
      129.0
    ],
    "confidence": 0.08144533141438495,
    "engine": "easyocr",
    "rotation": 0,
    "wire_overlap": true,
    "alternatives": [
      {
        "text": "1",
        "bbox": [
          19.0,
          110.0,
          47.0,
          129.0
        ],
        "confidence": 0.06046482653152574,
        "engine": "easyocr-crop",
        "rotation": 0
      },
      {
        "text": "^",
        "bbox": [
          19.0,
          110.0,
          47.0,
          129.0
        ],
        "confidence": 0.22448271558929278,
        "engine": "easyocr-crop",
        "rotation": 0
      },
      {
        "text": "4:",
        "bbox": [
          19.0,
          110.0,
          47.0,
          129.0
        ],
        "confidence": 0.17446774821924546,
        "engine": "easyocr-crop",
        "rotation": 0
      }
    ],
    "id": "t17",
    "raw": "49",
    "parsed": {
      "label": null,
      "number": 49.0,
      "unit": null,
      "internal": false,
      "unknown": false,
      "has_prefix": false,
      "unit_inferred": false,
      "confidence": 0.55,
      "emf_symbol": false,
      "normalized": "49",
      "normalizations": []
    },
    "assignments": [],
    "outcome": "unassigned",
    "reason": "weak_context",
    "candidates": [
      {
        "component_id": "V1",
        "role": "value",
        "distance": 215.48,
        "reason": "too_far"
      },
      {
        "component_id": "R1",
        "role": "value",
        "distance": 157.01,
        "reason": "too_far"
      },
      {
        "component_id": "R2",
        "role": "value",
        "distance": 58.29,
        "reason": "weak_context"
      },
      {
        "component_id": "R3",
        "role": "value",
        "distance": 143.57,
        "reason": "too_far"
      },
      {
        "component_id": "V2",
        "role": "value",
        "distance": 201.07,
        "reason": "too_far"
      },
      {
        "component_id": "C1",
        "role": "value",
        "distance": 201.77,
        "reason": "too_far"
      },
      {
        "component_id": "R4",
        "role": "value",
        "distance": 91.22,
        "reason": "weak_context"
      }
    ]
  },
  {
    "text": "S",
    "bbox": [
      183.0,
      119.0,
      224.0,
      134.0
    ],
    "confidence": 0.009292527656853622,
    "component_id": "R4",
    "context": "resistor",
    "engine": "easyocr",
    "rotation": 0,
    "wire_overlap": false,
    "alternatives": [
      {
        "text": "S",
        "bbox": [
          183.0,
          119.0,
          224.0,
          134.0
        ],
        "confidence": 0.008116856359095204,
        "engine": "easyocr-crop",
        "rotation": 0
      },
      {
        "text": "Ca",
        "bbox": [
          183.0,
          119.0,
          224.0,
          134.0
        ],
        "confidence": 0.0020624409271188114,
        "engine": "easyocr-crop",
        "rotation": 0
      },
      {
        "text": "Ca",
        "bbox": [
          183.0,
          119.0,
          224.0,
          134.0
        ],
        "confidence": 0.0012054777629143807,
        "engine": "easyocr-crop",
        "rotation": 0
      }
    ],
    "id": "t18",
    "raw": "S",
    "parsed": null,
    "assignments": [],
    "outcome": "ignored",
    "reason": "not_parseable",
    "candidates": []
  },
  {
    "text": "1",
    "bbox": [
      22.0,
      156.0,
      41.0,
      186.0
    ],
    "confidence": 0.704720036754626,
    "engine": "easyocr",
    "rotation": 0,
    "wire_overlap": true,
    "id": "t19",
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
        "component_id": "V1",
        "role": "value",
        "distance": 237.18,
        "reason": "too_far"
      },
      {
        "component_id": "R1",
        "role": "value",
        "distance": 186.62,
        "reason": "too_far"
      },
      {
        "component_id": "R2",
        "role": "value",
        "distance": 105.18,
        "reason": "weak_context"
      },
      {
        "component_id": "R3",
        "role": "value",
        "distance": 163.54,
        "reason": "too_far"
      },
      {
        "component_id": "V2",
        "role": "value",
        "distance": 197.98,
        "reason": "too_far"
      },
      {
        "component_id": "C1",
        "role": "value",
        "distance": 198.5,
        "reason": "too_far"
      },
      {
        "component_id": "R4",
        "role": "value",
        "distance": 77.07,
        "reason": "weak_context"
      }
    ]
  },
  {
    "text": "4",
    "bbox": [
      193.0,
      157.0,
      233.0,
      205.0
    ],
    "confidence": 0.4569032329194478,
    "component_id": "V2",
    "context": "dc_source",
    "engine": "easyocr-crop",
    "rotation": 0,
    "wire_overlap": false,
    "alternatives": [
      {
        "text": "4",
        "bbox": [
          193.0,
          157.0,
          233.0,
          205.0
        ],
        "confidence": 0.13309913649411786,
        "engine": "easyocr",
        "rotation": 0
      },
      {
        "text": "X",
        "bbox": [
          193.0,
          157.0,
          233.0,
          205.0
        ],
        "confidence": 0.06006608799253943,
        "engine": "easyocr-crop",
        "rotation": 0
      },
      {
        "text": "H",
        "bbox": [
          193.0,
          157.0,
          233.0,
          205.0
        ],
        "confidence": 0.19220545693912072,
        "engine": "easyocr-crop",
        "rotation": 0
      }
    ],
    "id": "t20",
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
        "distance": 127.76,
        "reason": "too_far"
      },
      {
        "component_id": "R1",
        "role": "value",
        "distance": 130.39,
        "reason": "too_far"
      },
      {
        "component_id": "R2",
        "role": "value",
        "distance": 136.89,
        "reason": "too_far"
      },
      {
        "component_id": "R3",
        "role": "value",
        "distance": 91.18,
        "reason": "weak_context"
      },
      {
        "component_id": "V2",
        "role": "value",
        "distance": 16.48,
        "reason": "weak_context"
      },
      {
        "component_id": "C1",
        "role": "value",
        "distance": 17.0,
        "reason": "weak_context"
      },
      {
        "component_id": "R4",
        "role": "value",
        "distance": 39.96,
        "reason": "weak_context"
      }
    ]
  },
  {
    "text": "15",
    "bbox": [
      229.0,
      162.0,
      244.0,
      199.0
    ],
    "confidence": 0.5090817249082119,
    "component_id": "V2",
    "context": "dc_source",
    "engine": "easyocr-crop",
    "rotation": 90,
    "wire_overlap": false,
    "alternatives": [
      {
        "text": "3S",
        "bbox": [
          229.0,
          162.0,
          244.0,
          199.0
        ],
        "confidence": 0.10527781210914594,
        "engine": "easyocr-crop",
        "rotation": 90
      },
      {
        "text": "5I",
        "bbox": [
          229.0,
          162.0,
          244.0,
          199.0
        ],
        "confidence": 0.05199009014950754,
        "engine": "easyocr-crop",
        "rotation": -90
      },
      {
        "text": "~5",
        "bbox": [
          229.0,
          162.0,
          244.0,
          199.0
        ],
        "confidence": 0.4930462914640746,
        "engine": "easyocr-crop",
        "rotation": 90
      },
      {
        "text": "li",
        "bbox": [
          229.0,
          162.0,
          244.0,
          199.0
        ],
        "confidence": 0.04644126981347613,
        "engine": "easyocr",
        "rotation": 0
      }
    ],
    "id": "t21",
    "raw": "15",
    "parsed": {
      "label": null,
      "number": 15.0,
      "unit": null,
      "internal": false,
      "unknown": false,
      "has_prefix": false,
      "unit_inferred": false,
      "confidence": 0.55,
      "emf_symbol": false,
      "normalized": "15",
      "normalizations": []
    },
    "assignments": [],
    "outcome": "unassigned",
    "reason": "weak_context",
    "candidates": [
      {
        "component_id": "V1",
        "role": "value",
        "distance": 124.64,
        "reason": "too_far"
      },
      {
        "component_id": "R1",
        "role": "value",
        "distance": 130.78,
        "reason": "too_far"
      },
      {
        "component_id": "R2",
        "role": "value",
        "distance": 151.87,
        "reason": "too_far"
      },
      {
        "component_id": "R3",
        "role": "value",
        "distance": 92.01,
        "reason": "weak_context"
      },
      {
        "component_id": "V2",
        "role": "value",
        "distance": 0.0,
        "reason": "weak_context"
      },
      {
        "component_id": "C1",
        "role": "value",
        "distance": 0.0,
        "reason": "weak_context"
      },
      {
        "component_id": "R4",
        "role": "value",
        "distance": 63.46,
        "reason": "weak_context"
      }
    ]
  },
  {
    "text": "1",
    "bbox": [
      240.0,
      164.0,
      252.0,
      188.0
    ],
    "confidence": 0.43749090814380054,
    "component_id": "V2",
    "context": "dc_source",
    "engine": "easyocr",
    "rotation": 0,
    "wire_overlap": true,
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
        "component_id": "V1",
        "role": "value",
        "distance": 120.12,
        "reason": "too_far"
      },
      {
        "component_id": "R1",
        "role": "value",
        "distance": 127.8,
        "reason": "too_far"
      },
      {
        "component_id": "R2",
        "role": "value",
        "distance": 155.61,
        "reason": "too_far"
      },
      {
        "component_id": "R3",
        "role": "value",
        "distance": 89.75,
        "reason": "weak_context"
      },
      {
        "component_id": "V2",
        "role": "value",
        "distance": 1.91,
        "reason": "weak_context"
      },
      {
        "component_id": "C1",
        "role": "value",
        "distance": 2.38,
        "reason": "weak_context"
      },
      {
        "component_id": "R4",
        "role": "value",
        "distance": 72.96,
        "reason": "weak_context"
      }
    ]
  },
  {
    "text": "",
    "bbox": [
      169.0,
      169.0,
      224.0,
      191.0
    ],
    "confidence": 0.0,
    "component_id": "R4",
    "context": "resistor",
    "engine": "easyocr",
    "rotation": 0,
    "wire_overlap": false,
    "alternatives": [
      {
        "text": "",
        "bbox": [
          169.0,
          169.0,
          224.0,
          191.0
        ],
        "confidence": 0.0,
        "engine": "easyocr-crop",
        "rotation": 0
      },
      {
        "text": "",
        "bbox": [
          169.0,
          169.0,
          224.0,
          191.0
        ],
        "confidence": 0.0,
        "engine": "easyocr-crop",
        "rotation": 0
      },
      {
        "text": "",
        "bbox": [
          169.0,
          169.0,
          224.0,
          191.0
        ],
        "confidence": 0.0,
        "engine": "easyocr-crop",
        "rotation": 0
      }
    ],
    "id": "t23",
    "raw": "",
    "parsed": null,
    "assignments": [],
    "outcome": "ignored",
    "reason": "not_parseable",
    "candidates": []
  },
  {
    "text": "M",
    "bbox": [
      108.0,
      170.0,
      173.0,
      194.0
    ],
    "confidence": 0.4903574498469112,
    "component_id": "R4",
    "context": "resistor",
    "engine": "easyocr",
    "rotation": 0,
    "wire_overlap": false,
    "id": "t24",
    "raw": "M",
    "parsed": null,
    "assignments": [],
    "outcome": "ignored",
    "reason": "not_parseable",
    "candidates": []
  },
  {
    "text": "1",
    "bbox": [
      240.0,
      180.0,
      252.0,
      199.0
    ],
    "confidence": 0.20113578963361878,
    "component_id": "V2",
    "context": "dc_source",
    "engine": "easyocr",
    "rotation": 0,
    "wire_overlap": true,
    "id": "t25",
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
        "component_id": "V1",
        "role": "value",
        "distance": 133.62,
        "reason": "too_far"
      },
      {
        "component_id": "R1",
        "role": "value",
        "distance": 141.07,
        "reason": "too_far"
      },
      {
        "component_id": "R2",
        "role": "value",
        "distance": 164.95,
        "reason": "too_far"
      },
      {
        "component_id": "R3",
        "role": "value",
        "distance": 102.78,
        "reason": "too_far"
      },
      {
        "component_id": "V2",
        "role": "value",
        "distance": 1.91,
        "reason": "weak_context"
      },
      {
        "component_id": "C1",
        "role": "value",
        "distance": 2.38,
        "reason": "weak_context"
      },
      {
        "component_id": "R4",
        "role": "value",
        "distance": 72.96,
        "reason": "weak_context"
      }
    ]
  },
  {
    "text": "Uo",
    "bbox": [
      221.0,
      195.0,
      242.0,
      205.0
    ],
    "confidence": 0.004435952930529279,
    "component_id": "V2",
    "context": "dc_source",
    "engine": "easyocr",
    "rotation": 0,
    "wire_overlap": false,
    "id": "t26",
    "raw": "Uo",
    "parsed": null,
    "assignments": [],
    "outcome": "ignored",
    "reason": "not_parseable",
    "candidates": []
  },
  {
    "text": "10 9",
    "bbox": [
      110.0,
      198.0,
      162.0,
      223.0
    ],
    "confidence": 0.41314664483070374,
    "component_id": "R4",
    "context": "resistor",
    "engine": "easyocr",
    "rotation": 0,
    "wire_overlap": false,
    "id": "t27",
    "raw": "10 9",
    "parsed": {
      "label": null,
      "number": 10.0,
      "unit": "ohm",
      "internal": false,
      "unknown": false,
      "has_prefix": false,
      "unit_inferred": true,
      "confidence": 0.6,
      "emf_symbol": false,
      "normalized": "10 Ω",
      "normalizations": [
        "contextual_unit_lookalike"
      ]
    },
    "assignments": [
      {
        "component_id": "R4",
        "role": "value",
        "parsed": {
          "label": null,
          "number": 10.0,
          "unit": "ohm",
          "internal": false,
          "unknown": false,
          "has_prefix": false,
          "unit_inferred": true,
          "confidence": 0.6,
          "emf_symbol": false,
          "normalized": "10 Ω",
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
        "distance": 185.71,
        "reason": "too_far"
      },
      {
        "component_id": "R1",
        "role": "value",
        "distance": 164.37,
        "reason": "too_far"
      },
      {
        "component_id": "R2",
        "role": "value",
        "distance": 138.79,
        "reason": "too_far"
      },
      {
        "component_id": "R3",
        "role": "value",
        "distance": 126.36,
        "reason": "too_far"
      },
      {
        "component_id": "V2",
        "role": "value",
        "distance": 94.09,
        "reason": "too_far"
      },
      {
        "component_id": "C1",
        "role": "value",
        "distance": 94.59,
        "reason": "too_far"
      },
      {
        "component_id": "R4",
        "role": "value",
        "distance": 16.38,
        "reason": "eligible"
      }
    ],
    "assigned_to": "R4",
    "role": "value"
  },
  {
    "text": "'",
    "bbox": [
      240.0,
      199.0,
      251.0,
      214.0
    ],
    "confidence": 0.33572094039755385,
    "component_id": "V2",
    "context": "dc_source",
    "engine": "easyocr",
    "rotation": 0,
    "wire_overlap": false,
    "id": "t28",
    "raw": "'",
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
|"before"|"V1"|"dc_source"|null|{"number":5.0,"unit":"V","status":"given","source":"ocr","confidence":0.8350155506676267}|
|"before"|"R1"|"resistor"|null|{"number":10.0,"unit":"ohm","status":"assumed","source":"prior","confidence":0.0}|
|"before"|"R2"|"resistor"|null|{"number":10.0,"unit":"ohm","status":"assumed","source":"prior","confidence":0.0}|
|"before"|"R3"|"resistor"|null|{"number":10.0,"unit":"ohm","status":"assumed","source":"prior","confidence":0.0}|
|"before"|"V2"|"dc_source"|null|{"number":12.0,"unit":"V","status":"assumed","source":"prior","confidence":0.0}|
|"before"|"C1"|"capacitor"|null|{"number":1e-05,"unit":"F","status":"assumed","source":"prior","confidence":0.0}|
|"before"|"R4"|"resistor"|"E"|{"number":10.0,"unit":"ohm","status":"assumed","source":"prior","confidence":0.0}|
|"WP-A"|"V1"|"dc_source"|null|{"number":5.0,"unit":"V","status":"given","source":"ocr","confidence":0.85,"unit_inferred":false}|
|"WP-A"|"R1"|"resistor"|null|{"number":3.0,"unit":"ohm","status":"given","source":"ocr","confidence":0.41846257581284724,"unit_inferred":true}|
|"WP-A"|"R2"|"resistor"|null|{"number":2.0,"unit":"ohm","status":"given","source":"ocr","confidence":0.6,"unit_inferred":true}|
|"WP-A"|"R3"|"resistor"|null|{"number":null,"unit":"ohm","status":"assumed","source":"prior","confidence":0.0,"unit_inferred":false}|
|"WP-A"|"V2"|"dc_source"|null|{"number":12.0,"unit":"V","status":"assumed","source":"prior","confidence":0.0,"unit_inferred":false}|
|"WP-A"|"C1"|"capacitor"|null|{"number":null,"unit":"F","status":"assumed","source":"prior","confidence":0.0,"unit_inferred":false}|
|"WP-A"|"R4"|"resistor"|null|{"number":10.0,"unit":"ohm","status":"given","source":"ocr","confidence":0.41314664483070374,"unit_inferred":true}|

WP-A graph: **11 nodes**; any computed nonzero current: **true**. This is not a topology accuracy score.

The OCR annotation shows components and text, not wire connectivity. WP-B adds wire overlays and records whether repairs improve the graph.

## WP-B tracing replay

Same WP-A detections and OCR; no detector/OCR rerun or gold topology claim. Wire overlay: `.cache/round3/wires/case-004.png` (local only).

```json
{
  "image": "Screenshot 2026-10-31 000926.png",
  "before": {
    "nodes": 11,
    "parts": 7,
    "disabled": 6,
    "provenance": "partial",
    "nonzero_current": true,
    "score": 47,
    "warnings": [
      {
        "code": "unit_inferred",
        "ref": "R1",
        "message_key": "warn.unit_inferred"
      },
      {
        "code": "unit_inferred",
        "ref": "R2",
        "message_key": "warn.unit_inferred"
      },
      {
        "code": "unit_inferred",
        "ref": "R4",
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
        "code": "uncertain_topology",
        "ref": "R2",
        "message_key": "warn.uncertain_topology"
      },
      {
        "code": "uncertain_topology",
        "ref": "C1",
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
        "ref": "C1",
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
        "ref": "isolated.V1.a",
        "message_key": "warn.no_closed_loop"
      },
      {
        "code": "no_closed_loop",
        "ref": "isolated.R1.b",
        "message_key": "warn.no_closed_loop"
      },
      {
        "code": "no_closed_loop",
        "ref": "isolated.R2.a",
        "message_key": "warn.no_closed_loop"
      },
      {
        "code": "no_closed_loop",
        "ref": "isolated.C1.a",
        "message_key": "warn.no_closed_loop"
      },
      {
        "code": "no_closed_loop",
        "ref": "n1",
        "message_key": "warn.no_closed_loop"
      },
      {
        "code": "no_closed_loop",
        "ref": "n2",
        "message_key": "warn.no_closed_loop"
      },
      {
        "code": "no_closed_loop",
        "ref": "n4",
        "message_key": "warn.no_closed_loop"
      },
      {
        "code": "no_closed_loop",
        "ref": "n6",
        "message_key": "warn.no_closed_loop"
      },
      {
        "code": "no_closed_loop",
        "ref": "n9",
        "message_key": "warn.no_closed_loop"
      },
      {
        "code": "no_closed_loop",
        "ref": "n13",
        "message_key": "warn.no_closed_loop"
      },
      {
        "code": "dangling_wire",
        "ref": "p10",
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
        "ref": "p21",
        "message_key": "warn.dangling_wire"
      },
      {
        "code": "dangling_wire",
        "ref": "p24",
        "message_key": "warn.dangling_wire"
      },
      {
        "code": "dangling_wire",
        "ref": "p30",
        "message_key": "warn.dangling_wire"
      },
      {
        "code": "dangling_wire",
        "ref": "p31",
        "message_key": "warn.dangling_wire"
      },
      {
        "code": "dangling_wire",
        "ref": "p32",
        "message_key": "warn.dangling_wire"
      },
      {
        "code": "dangling_wire",
        "ref": "p35",
        "message_key": "warn.dangling_wire"
      },
      {
        "code": "assumed_value",
        "ref": "V2",
        "message_key": "warn.assumed_value"
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
        "ref": "C1",
        "message_key": "warn.value_not_found"
      }
    ]
  },
  "after": {
    "nodes": 11,
    "parts": 7,
    "disabled": 0,
    "provenance": "partial",
    "nonzero_current": false,
    "score": 46,
    "warnings": [
      {
        "code": "uncertain_topology",
        "ref": "V1",
        "message_key": "warn.uncertain_topology"
      },
      {
        "code": "off_axis_snap",
        "ref": "V1",
        "message_key": "warn.off_axis_snap"
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
        "code": "uncertain_topology",
        "ref": "C1",
        "message_key": "warn.uncertain_topology"
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
        "ref": "C1",
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
        "ref": "isolated.C1.a",
        "message_key": "warn.no_closed_loop"
      },
      {
        "code": "no_closed_loop",
        "ref": "n6",
        "message_key": "warn.no_closed_loop"
      },
      {
        "code": "no_closed_loop",
        "ref": "n13",
        "message_key": "warn.no_closed_loop"
      },
      {
        "code": "no_closed_loop",
        "ref": "n15",
        "message_key": "warn.no_closed_loop"
      },
      {
        "code": "no_closed_loop",
        "ref": "n16",
        "message_key": "warn.no_closed_loop"
      },
      {
        "code": "no_closed_loop",
        "ref": "n18",
        "message_key": "warn.no_closed_loop"
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
        "ref": "p27",
        "message_key": "warn.dangling_wire"
      },
      {
        "code": "dangling_wire",
        "ref": "p28",
        "message_key": "warn.dangling_wire"
      },
      {
        "code": "dangling_wire",
        "ref": "p30",
        "message_key": "warn.dangling_wire"
      },
      {
        "code": "dangling_wire",
        "ref": "p32",
        "message_key": "warn.dangling_wire"
      },
      {
        "code": "dangling_wire",
        "ref": "p35",
        "message_key": "warn.dangling_wire"
      }
    ]
  },
  "trace": {
    "alternative_threshold": false,
    "repair": false,
    "terminals_snapped": 10,
    "terminals_floating": 4,
    "off_axis_snaps": 2,
    "gaps_bridged": 0,
    "stroke_width": 1.0,
    "ghosts": []
  },
  "seconds": 2.1246922999998787,
  "scope": "Tracing-only replay on identical WP-A detections/texts; no gold topology accuracy."
}
```
