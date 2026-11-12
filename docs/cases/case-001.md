# Case 001: Screenshot 2026-10-30 232522.png

SHA-256: `167ebff80d00595c8f56ec3352ccc73165205c1ba2849a758e071247c0e7b6ec`. Read-only configured owner input; raster excluded from Git.

The image is symbolic: R1/R2/R3 and current arrows have no numerical part values. Baseline numbers from arrows and the caption were false readings. Leaving all four values missing is the correct conservative outcome. All parts remain disconnected here.

Inspected annotated image: `.cache/round3/case-001.png` (local only).

Both engine paths were requested. Tesseract is not installed on this machine; there are no real Tesseract readings to report. EasyOCR EN/BN uses installed local models. Dual-engine selection is tested with mocks, not claimed as a local Tesseract benchmark.

## Frozen round-two evidence

The trace below records actual Hungarian selections (including recovery attempts). A selected candidate does not necessarily survive the final netlist. The old API did not retain every rejected pair; unselected candidates are reported as such rather than inventing a rejection distance.

|Raw text|Native box|Old parse|Actual selection (role, part, cost / dummy)|
|---|---|---|---|
|"R,"|[256.0,10.0,301.0,56.0]|null|"not parseable"|
|"4"|[137.0,44.0,171.0,90.0]|{"label":null,"number":4.0,"unit":null,"confidence":0.55,"internal":false,"unknown":false,"has_prefix":false}|[{"role":"value","component":"R1","cost":117.4201014219089,"dummy_cost":518.4305877685547},{"role":"value","component":"R1","cost":117.4201014219089,"dummy_cost":933.1750579833983}]|
|"M"|[218.0,118.0,384.0,161.0]|null|"not parseable"|
|"D"|[137.0,121.0,176.0,144.0]|null|"not parseable"|
|"7"|[138.0,137.0,173.0,158.0]|{"label":null,"number":7.0,"unit":null,"confidence":0.55,"internal":false,"unknown":false,"has_prefix":false}|[{"role":"value","component":"R2","cost":113.65837047905214,"dummy_cost":537.8296966552734},{"role":"value","component":"retry.6.R3","cost":0.5649739986653657,"dummy_cost":247.3305633544922}]|
|"1"|[143.0,188.0,179.0,234.0]|{"label":null,"number":1.0,"unit":null,"confidence":0.55,"internal":false,"unknown":false,"has_prefix":false}|[{"role":"value","component":"R3","cost":107.45826654177424,"dummy_cost":512.6642761230469},{"role":"value","component":"R2","cost":132.11821867947123,"dummy_cost":968.0934539794921}]|
|"R;"|[252.0,227.0,297.0,273.0]|null|"not parseable"|
|"J"|[468.0,283.0,549.0,325.0]|null|"not parseable"|
|"H"|[239.0,287.0,293.0,327.0]|null|"not parseable"|
|"C"|[321.0,294.0,408.0,326.0]|null|"not parseable"|
|")"|[406.0,294.0,445.0,345.0]|null|"not parseable"|
|"F"|[288.0,296.0,338.0,348.0]|null|"not parseable"|
|"7"|[381.0,318.0,408.0,345.0]|{"label":null,"number":7.0,"unit":null,"confidence":0.55,"internal":false,"unknown":false,"has_prefix":false}|[{"role":"value","component":"retry.4.V2","cost":0.0635558274478143,"dummy_cost":462.7477661132813}]|
|"7"|[270.0,319.0,293.0,358.0]|{"label":null,"number":7.0,"unit":null,"confidence":0.55,"internal":false,"unknown":false,"has_prefix":false}|[{"role":"value","component":"V1","cost":0.07639151416638512,"dummy_cost":259.97076416015625},{"role":"value","component":"R3","cost":106.85527372984765,"dummy_cost":922.7956970214844}]|
|"664"|[219.0,352.0,283.0,396.0]|{"label":null,"number":664.0,"unit":null,"confidence":0.55,"internal":false,"unknown":false,"has_prefix":false}|[{"role":"value","component":"V1","cost":51.73557127362822,"dummy_cost":467.9473754882813}]|
|"৩৬"|[294.0,361.0,364.0,396.0]|{"label":null,"number":36.0,"unit":null,"confidence":0.55,"internal":false,"unknown":false,"has_prefix":false}|[{"role":"value","component":"retry.5.S1","cost":96.49704242538937,"dummy_cost":463.7718841552735}]|
|":"|[276.0,366.0,300.0,393.0]|null|"not parseable"|

## Current raw engine readings

|Engine / rotation|Raw text|Native box|Current parse in anchored context|
|---|---|---|---|
|"easyocr-crop / 0"|"R,"|[256.0,10.0,301.0,51.0]|null|
|"easyocr / 0"|"4"|[137.0,44.0,171.0,90.0]|{"label":null,"number":4.0,"unit":null,"internal":false,"unknown":false,"has_prefix":false,"unit_inferred":false,"confidence":0.55,"emf_symbol":false,"normalized":"4","normalizations":[]}|
|"easyocr / 0"|"3_"|[344.0,58.0,398.0,88.0]|{"label":null,"number":3.0,"unit":"ohm","internal":false,"unknown":false,"has_prefix":false,"unit_inferred":true,"confidence":0.6,"emf_symbol":false,"normalized":"3","normalizations":["component_unit"]}|
|"easyocr / 0"|"7"|[191.0,71.0,220.0,88.0]|{"label":null,"number":7.0,"unit":"ohm","internal":false,"unknown":false,"has_prefix":false,"unit_inferred":true,"confidence":0.6,"emf_symbol":false,"normalized":"7","normalizations":["component_unit"]}|
|"easyocr / 0"|"Ae"|[134.0,83.0,170.0,102.0]|null|
|"easyocr / 0"|"8"|[264.0,83.0,284.0,98.0]|{"label":null,"number":8.0,"unit":"ohm","internal":false,"unknown":false,"has_prefix":false,"unit_inferred":true,"confidence":0.6,"emf_symbol":false,"normalized":"8","normalizations":["component_unit"]}|
|"easyocr / 0"|"Rz"|[292.0,89.0,339.0,126.0]|null|
|"easyocr / 0"|"76"|[144.0,91.0,196.0,140.0]|{"label":null,"number":76.0,"unit":null,"internal":false,"unknown":false,"has_prefix":false,"unit_inferred":false,"confidence":0.55,"emf_symbol":false,"normalized":"76","normalizations":[]}|
|"easyocr / 0"|"B"|[536.0,116.0,570.0,153.0]|null|
|"easyocr / 0"|"4"|[9.0,118.0,50.0,158.0]|{"label":null,"number":4.0,"unit":null,"internal":false,"unknown":false,"has_prefix":false,"unit_inferred":false,"confidence":0.55,"emf_symbol":false,"normalized":"4","normalizations":[]}|
|"easyocr / 0"|""|[218.0,118.0,365.0,161.0]|null|
|"easyocr / 0"|"2"|[53.0,126.0,80.0,142.0]|{"label":null,"number":2.0,"unit":null,"internal":false,"unknown":false,"has_prefix":false,"unit_inferred":false,"confidence":0.55,"emf_symbol":false,"normalized":"2","normalizations":[]}|
|"easyocr / 0"|"77"|[138.0,137.0,173.0,158.0]|{"label":null,"number":77.0,"unit":null,"internal":false,"unknown":false,"has_prefix":false,"unit_inferred":false,"confidence":0.55,"emf_symbol":false,"normalized":"77","normalizations":[]}|
|"easyocr / 0"|"3"|[134.0,161.0,169.0,189.0]|{"label":null,"number":3.0,"unit":null,"internal":false,"unknown":false,"has_prefix":false,"unit_inferred":false,"confidence":0.55,"emf_symbol":false,"normalized":"3","normalizations":[]}|
|"easyocr / 0"|"T4"|[128.0,177.0,161.0,196.0]|null|
|"easyocr / 0"|"1"|[143.0,188.0,179.0,234.0]|{"label":null,"number":1.0,"unit":null,"internal":false,"unknown":false,"has_prefix":false,"unit_inferred":false,"confidence":0.55,"emf_symbol":false,"normalized":"1","normalizations":[]}|
|"easyocr / 0"|"M-"|[218.0,191.0,373.0,234.0]|null|
|"easyocr / 0"|"V\|"|[516.0,216.0,570.0,254.0]|null|
|"easyocr / 0"|"\""|[21.0,225.0,74.0,261.0]|null|
|"easyocr / 0"|"Rz"|[252.0,230.0,297.0,273.0]|null|
|"easyocr / 0"|"+"|[239.0,287.0,293.0,327.0]|null|
|"easyocr / 0"|"("|[381.0,294.0,408.0,324.0]|null|
|"easyocr / 0"|"L"|[406.0,294.0,449.0,326.0]|null|
|"easyocr / 0"|"L"|[288.0,296.0,338.0,326.0]|null|
|"easyocr / 0"|"1"|[32.0,301.0,51.0,328.0]|{"label":null,"number":1.0,"unit":null,"internal":false,"unknown":false,"has_prefix":false,"unit_inferred":false,"confidence":0.55,"emf_symbol":false,"normalized":"1","normalizations":[]}|
|"easyocr / 0"|"37"|[338.0,317.0,408.0,345.0]|{"label":null,"number":37.0,"unit":null,"internal":false,"unknown":false,"has_prefix":false,"unit_inferred":false,"confidence":0.55,"emf_symbol":false,"normalized":"37","normalizations":[]}|
|"easyocr / 0"|"1"|[289.0,318.0,304.0,348.0]|{"label":null,"number":1.0,"unit":"V","internal":false,"unknown":false,"has_prefix":false,"unit_inferred":true,"confidence":0.6,"emf_symbol":false,"normalized":"1","normalizations":["component_unit"]}|
|"easyocr / 0"|")"|[300.0,318.0,336.0,348.0]|null|
|"easyocr / 0"|"1"|[406.0,318.0,434.0,345.0]|{"label":null,"number":1.0,"unit":null,"internal":false,"unknown":false,"has_prefix":false,"unit_inferred":false,"confidence":0.55,"emf_symbol":false,"normalized":"1","normalizations":[]}|
|"easyocr / 0"|"1"|[277.0,320.0,293.0,353.0]|{"label":null,"number":1.0,"unit":"V","internal":false,"unknown":false,"has_prefix":false,"unit_inferred":true,"confidence":0.6,"emf_symbol":false,"normalized":"1","normalizations":["component_unit"]}|
|"easyocr / 0"|"664"|[219.0,352.0,283.0,396.0]|{"label":null,"number":664.0,"unit":null,"internal":false,"unknown":false,"has_prefix":false,"unit_inferred":false,"confidence":0.55,"emf_symbol":false,"normalized":"664","normalizations":[]}|
|"easyocr / 0"|"0.6"|[294.0,361.0,364.0,396.0]|{"label":null,"number":0.6,"unit":null,"internal":false,"unknown":false,"has_prefix":false,"unit_inferred":false,"confidence":0.55,"emf_symbol":false,"normalized":"0.6","normalizations":[]}|
|"easyocr / 0"|":"|[276.0,366.0,300.0,393.0]|null|

## Current association decisions

Every tested component/role pair includes its measured distance and rejection reason. `weak_context` covers a body/lead overlap, low confidence, contradictory bare readings or insufficient anchored support; it is deliberately conservative.

```json
[
  {
    "text": "R,",
    "bbox": [
      256.0,
      10.0,
      301.0,
      51.0
    ],
    "confidence": 0.9755780310487849,
    "component_id": "R1",
    "context": "resistor",
    "engine": "easyocr-crop",
    "rotation": 0,
    "wire_overlap": false,
    "alternatives": [
      {
        "text": "R,",
        "bbox": [
          256.0,
          10.0,
          301.0,
          51.0
        ],
        "confidence": 0.7114602041813595,
        "engine": "easyocr-crop",
        "rotation": 0
      },
      {
        "text": "R,",
        "bbox": [
          256.0,
          10.0,
          301.0,
          51.0
        ],
        "confidence": 0.6289019583130803,
        "engine": "easyocr",
        "rotation": 0
      },
      {
        "text": "R,",
        "bbox": [
          256.0,
          10.0,
          301.0,
          51.0
        ],
        "confidence": 0.5394249686114633,
        "engine": "easyocr-crop",
        "rotation": 0
      }
    ],
    "id": "t1",
    "raw": "R,",
    "parsed": null,
    "assignments": [],
    "outcome": "ignored",
    "reason": "not_parseable",
    "candidates": []
  },
  {
    "text": "4",
    "bbox": [
      137.0,
      44.0,
      171.0,
      90.0
    ],
    "confidence": 0.6821797602967514,
    "engine": "easyocr",
    "rotation": 0,
    "wire_overlap": false,
    "alternatives": [
      {
        "text": "2",
        "bbox": [
          137.0,
          44.0,
          171.0,
          90.0
        ],
        "confidence": 0.45063007775292263,
        "engine": "easyocr-crop",
        "rotation": 90
      },
      {
        "text": "2",
        "bbox": [
          137.0,
          44.0,
          171.0,
          90.0
        ],
        "confidence": 0.35786530316386234,
        "engine": "easyocr-crop",
        "rotation": 90
      },
      {
        "text": "5E",
        "bbox": [
          137.0,
          44.0,
          171.0,
          90.0
        ],
        "confidence": 0.2527768127802612,
        "engine": "easyocr-crop",
        "rotation": -90
      },
      {
        "text": "5",
        "bbox": [
          137.0,
          44.0,
          171.0,
          90.0
        ],
        "confidence": 0.25109900350868486,
        "engine": "easyocr-crop",
        "rotation": 90
      }
    ],
    "id": "t2",
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
    "reason": "too_far",
    "candidates": [
      {
        "component_id": "R1",
        "role": "value",
        "distance": 68.34,
        "reason": "weak_context"
      },
      {
        "component_id": "R2",
        "role": "value",
        "distance": 84.29,
        "reason": "weak_context"
      },
      {
        "component_id": "R3",
        "role": "value",
        "distance": 141.75,
        "reason": "weak_context"
      },
      {
        "component_id": "V1",
        "role": "value",
        "distance": 257.61,
        "reason": "too_far"
      }
    ]
  },
  {
    "text": "3_",
    "bbox": [
      344.0,
      58.0,
      398.0,
      88.0
    ],
    "confidence": 0.09252959055908258,
    "component_id": "R1",
    "context": "resistor",
    "engine": "easyocr",
    "rotation": 0,
    "wire_overlap": true,
    "id": "t3",
    "raw": "3_",
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
        "distance": 22.47,
        "reason": "weak_context"
      },
      {
        "component_id": "R2",
        "role": "value",
        "distance": 45.35,
        "reason": "weak_context"
      },
      {
        "component_id": "R3",
        "role": "value",
        "distance": 120.07,
        "reason": "weak_context"
      },
      {
        "component_id": "V1",
        "role": "value",
        "distance": 229.76,
        "reason": "too_far"
      }
    ]
  },
  {
    "text": "7",
    "bbox": [
      191.0,
      71.0,
      220.0,
      88.0
    ],
    "confidence": 0.6982293831464546,
    "component_id": "R1",
    "context": "resistor",
    "engine": "easyocr",
    "rotation": 0,
    "wire_overlap": true,
    "id": "t4",
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
        "component_id": "R1",
        "role": "value",
        "distance": 16.84,
        "reason": "weak_context"
      },
      {
        "component_id": "R2",
        "role": "value",
        "distance": 40.71,
        "reason": "weak_context"
      },
      {
        "component_id": "R3",
        "role": "value",
        "distance": 112.97,
        "reason": "weak_context"
      },
      {
        "component_id": "V1",
        "role": "value",
        "distance": 225.31,
        "reason": "too_far"
      }
    ]
  },
  {
    "text": "Ae",
    "bbox": [
      134.0,
      83.0,
      170.0,
      102.0
    ],
    "confidence": 0.0008196845654880837,
    "engine": "easyocr",
    "rotation": 0,
    "wire_overlap": true,
    "id": "t5",
    "raw": "Ae",
    "parsed": null,
    "assignments": [],
    "outcome": "ignored",
    "reason": "not_parseable",
    "candidates": []
  },
  {
    "text": "8",
    "bbox": [
      264.0,
      83.0,
      284.0,
      98.0
    ],
    "confidence": 0.06390578458928076,
    "component_id": "R2",
    "context": "resistor",
    "engine": "easyocr",
    "rotation": 0,
    "wire_overlap": false,
    "alternatives": [
      {
        "text": "M",
        "bbox": [
          222.0,
          48.0,
          348.0,
          93.0
        ],
        "confidence": 0.3991689000123557,
        "engine": "easyocr-crop",
        "rotation": 0
      },
      {
        "text": "m",
        "bbox": [
          222.0,
          48.0,
          348.0,
          93.0
        ],
        "confidence": 0.24387259729412225,
        "engine": "easyocr-crop",
        "rotation": 0
      },
      {
        "text": "m",
        "bbox": [
          222.0,
          48.0,
          348.0,
          93.0
        ],
        "confidence": 0.020680635801248792,
        "engine": "easyocr",
        "rotation": 0
      },
      {
        "text": "m",
        "bbox": [
          222.0,
          48.0,
          348.0,
          93.0
        ],
        "confidence": 0.014809704924553024,
        "engine": "easyocr-crop",
        "rotation": 0
      }
    ],
    "id": "t6",
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
    "reason": "too_far",
    "candidates": [
      {
        "component_id": "R1",
        "role": "value",
        "distance": 0.0,
        "reason": "weak_context"
      },
      {
        "component_id": "R2",
        "role": "value",
        "distance": 26.17,
        "reason": "weak_context"
      },
      {
        "component_id": "R3",
        "role": "value",
        "distance": 100.71,
        "reason": "weak_context"
      },
      {
        "component_id": "V1",
        "role": "value",
        "distance": 202.41,
        "reason": "too_far"
      }
    ]
  },
  {
    "text": "Rz",
    "bbox": [
      292.0,
      89.0,
      339.0,
      126.0
    ],
    "confidence": 0.7508480954344361,
    "component_id": "R1",
    "context": "resistor",
    "engine": "easyocr",
    "rotation": 0,
    "wire_overlap": false,
    "id": "t7",
    "raw": "Rz",
    "parsed": null,
    "assignments": [],
    "outcome": "ignored",
    "reason": "not_parseable",
    "candidates": []
  },
  {
    "text": "76",
    "bbox": [
      144.0,
      91.0,
      196.0,
      140.0
    ],
    "confidence": 0.15160856337786188,
    "engine": "easyocr",
    "rotation": 0,
    "wire_overlap": true,
    "alternatives": [
      {
        "text": "5",
        "bbox": [
          137.0,
          121.0,
          176.0,
          144.0
        ],
        "confidence": 0.007355744568469158,
        "engine": "easyocr",
        "rotation": 0
      }
    ],
    "id": "t8",
    "raw": "76",
    "parsed": {
      "label": null,
      "number": 76.0,
      "unit": null,
      "internal": false,
      "unknown": false,
      "has_prefix": false,
      "unit_inferred": false,
      "confidence": 0.55,
      "emf_symbol": false,
      "normalized": "76",
      "normalizations": []
    },
    "assignments": [],
    "outcome": "unassigned",
    "reason": "too_far",
    "candidates": [
      {
        "component_id": "R1",
        "role": "value",
        "distance": 56.62,
        "reason": "weak_context"
      },
      {
        "component_id": "R2",
        "role": "value",
        "distance": 52.11,
        "reason": "weak_context"
      },
      {
        "component_id": "R3",
        "role": "value",
        "distance": 92.01,
        "reason": "weak_context"
      },
      {
        "component_id": "V1",
        "role": "value",
        "distance": 207.6,
        "reason": "too_far"
      }
    ]
  },
  {
    "text": "B",
    "bbox": [
      536.0,
      116.0,
      570.0,
      153.0
    ],
    "confidence": 0.3504910385921711,
    "engine": "easyocr",
    "rotation": 0,
    "wire_overlap": false,
    "id": "t9",
    "raw": "B",
    "parsed": null,
    "assignments": [],
    "outcome": "ignored",
    "reason": "not_parseable",
    "candidates": []
  },
  {
    "text": "4",
    "bbox": [
      9.0,
      118.0,
      50.0,
      158.0
    ],
    "confidence": 0.6069912387927481,
    "engine": "easyocr",
    "rotation": 0,
    "wire_overlap": true,
    "id": "t10",
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
    "reason": "too_far",
    "candidates": [
      {
        "component_id": "R1",
        "role": "value",
        "distance": 197.82,
        "reason": "weak_context"
      },
      {
        "component_id": "R2",
        "role": "value",
        "distance": 192.59,
        "reason": "weak_context"
      },
      {
        "component_id": "R3",
        "role": "value",
        "distance": 200.0,
        "reason": "weak_context"
      },
      {
        "component_id": "V1",
        "role": "value",
        "distance": 292.7,
        "reason": "too_far"
      }
    ]
  },
  {
    "text": "",
    "bbox": [
      218.0,
      118.0,
      365.0,
      161.0
    ],
    "confidence": 0.0,
    "component_id": "R1",
    "context": "resistor",
    "engine": "easyocr",
    "rotation": 0,
    "wire_overlap": false,
    "id": "t11",
    "raw": "",
    "parsed": null,
    "assignments": [],
    "outcome": "ignored",
    "reason": "not_parseable",
    "candidates": []
  },
  {
    "text": "2",
    "bbox": [
      53.0,
      126.0,
      80.0,
      142.0
    ],
    "confidence": 0.649390522703758,
    "engine": "easyocr",
    "rotation": 0,
    "wire_overlap": true,
    "id": "t12",
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
        "distance": 160.92,
        "reason": "weak_context"
      },
      {
        "component_id": "R2",
        "role": "value",
        "distance": 155.59,
        "reason": "weak_context"
      },
      {
        "component_id": "R3",
        "role": "value",
        "distance": 165.96,
        "reason": "weak_context"
      },
      {
        "component_id": "V1",
        "role": "value",
        "distance": 264.42,
        "reason": "too_far"
      }
    ]
  },
  {
    "text": "77",
    "bbox": [
      138.0,
      137.0,
      173.0,
      158.0
    ],
    "confidence": 0.1486188453489653,
    "engine": "easyocr",
    "rotation": 0,
    "wire_overlap": true,
    "id": "t13",
    "raw": "77",
    "parsed": {
      "label": null,
      "number": 77.0,
      "unit": null,
      "internal": false,
      "unknown": false,
      "has_prefix": false,
      "unit_inferred": false,
      "confidence": 0.55,
      "emf_symbol": false,
      "normalized": "77",
      "normalizations": []
    },
    "assignments": [],
    "outcome": "unassigned",
    "reason": "too_far",
    "candidates": [
      {
        "component_id": "R1",
        "role": "value",
        "distance": 85.68,
        "reason": "weak_context"
      },
      {
        "component_id": "R2",
        "role": "value",
        "distance": 66.59,
        "reason": "weak_context"
      },
      {
        "component_id": "R3",
        "role": "value",
        "distance": 79.82,
        "reason": "weak_context"
      },
      {
        "component_id": "V1",
        "role": "value",
        "distance": 190.02,
        "reason": "too_far"
      }
    ]
  },
  {
    "text": "3",
    "bbox": [
      134.0,
      161.0,
      169.0,
      189.0
    ],
    "confidence": 0.041472065244001266,
    "engine": "easyocr",
    "rotation": 0,
    "wire_overlap": true,
    "id": "t14",
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
        "distance": 107.68,
        "reason": "weak_context"
      },
      {
        "component_id": "R2",
        "role": "value",
        "distance": 72.32,
        "reason": "weak_context"
      },
      {
        "component_id": "R3",
        "role": "value",
        "distance": 72.62,
        "reason": "weak_context"
      },
      {
        "component_id": "V1",
        "role": "value",
        "distance": 172.81,
        "reason": "too_far"
      }
    ]
  },
  {
    "text": "T4",
    "bbox": [
      128.0,
      177.0,
      161.0,
      196.0
    ],
    "confidence": 0.0014967896944250575,
    "engine": "easyocr",
    "rotation": 0,
    "wire_overlap": true,
    "id": "t15",
    "raw": "T4",
    "parsed": null,
    "assignments": [],
    "outcome": "ignored",
    "reason": "not_parseable",
    "candidates": []
  },
  {
    "text": "1",
    "bbox": [
      143.0,
      188.0,
      179.0,
      234.0
    ],
    "confidence": 0.4535733489029248,
    "engine": "easyocr",
    "rotation": 0,
    "wire_overlap": true,
    "id": "t16",
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
        "distance": 132.19,
        "reason": "weak_context"
      },
      {
        "component_id": "R2",
        "role": "value",
        "distance": 80.05,
        "reason": "weak_context"
      },
      {
        "component_id": "R3",
        "role": "value",
        "distance": 61.29,
        "reason": "weak_context"
      },
      {
        "component_id": "V1",
        "role": "value",
        "distance": 142.69,
        "reason": "too_far"
      }
    ]
  },
  {
    "text": "M-",
    "bbox": [
      218.0,
      191.0,
      373.0,
      234.0
    ],
    "confidence": 0.11685278414256417,
    "component_id": "R2",
    "context": "resistor",
    "engine": "easyocr",
    "rotation": 0,
    "wire_overlap": false,
    "id": "t17",
    "raw": "M-",
    "parsed": null,
    "assignments": [],
    "outcome": "ignored",
    "reason": "not_parseable",
    "candidates": []
  },
  {
    "text": "V|",
    "bbox": [
      516.0,
      216.0,
      570.0,
      254.0
    ],
    "confidence": 0.2279772947812979,
    "engine": "easyocr",
    "rotation": 0,
    "wire_overlap": true,
    "id": "t18",
    "raw": "V|",
    "parsed": null,
    "assignments": [],
    "outcome": "ignored",
    "reason": "not_parseable",
    "candidates": []
  },
  {
    "text": "\"",
    "bbox": [
      21.0,
      225.0,
      74.0,
      261.0
    ],
    "confidence": 0.35190607361679227,
    "engine": "easyocr",
    "rotation": 0,
    "wire_overlap": true,
    "id": "t19",
    "raw": "\"",
    "parsed": null,
    "assignments": [],
    "outcome": "ignored",
    "reason": "not_parseable",
    "candidates": []
  },
  {
    "text": "Rz",
    "bbox": [
      252.0,
      230.0,
      297.0,
      273.0
    ],
    "confidence": 0.7655401283027459,
    "component_id": "R3",
    "context": "resistor",
    "engine": "easyocr",
    "rotation": 0,
    "wire_overlap": false,
    "id": "t20",
    "raw": "Rz",
    "parsed": null,
    "assignments": [],
    "outcome": "ignored",
    "reason": "not_parseable",
    "candidates": []
  },
  {
    "text": "+",
    "bbox": [
      239.0,
      287.0,
      293.0,
      327.0
    ],
    "confidence": 0.515675159495462,
    "component_id": "R3",
    "context": "resistor",
    "engine": "easyocr",
    "rotation": 0,
    "wire_overlap": true,
    "id": "t21",
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
    "text": "(",
    "bbox": [
      381.0,
      294.0,
      408.0,
      324.0
    ],
    "confidence": 0.9504759304555286,
    "engine": "easyocr",
    "rotation": 0,
    "wire_overlap": true,
    "id": "t22",
    "raw": "(",
    "parsed": null,
    "assignments": [],
    "outcome": "ignored",
    "reason": "not_parseable",
    "candidates": []
  },
  {
    "text": "L",
    "bbox": [
      406.0,
      294.0,
      449.0,
      326.0
    ],
    "confidence": 0.9794822962152274,
    "engine": "easyocr",
    "rotation": 0,
    "wire_overlap": true,
    "id": "t23",
    "raw": "L",
    "parsed": null,
    "assignments": [],
    "outcome": "ignored",
    "reason": "not_parseable",
    "candidates": []
  },
  {
    "text": "L",
    "bbox": [
      288.0,
      296.0,
      338.0,
      326.0
    ],
    "confidence": 0.6457104276489787,
    "component_id": "R3",
    "context": "resistor",
    "engine": "easyocr",
    "rotation": 0,
    "wire_overlap": true,
    "id": "t24",
    "raw": "L",
    "parsed": null,
    "assignments": [],
    "outcome": "ignored",
    "reason": "not_parseable",
    "candidates": []
  },
  {
    "text": "1",
    "bbox": [
      32.0,
      301.0,
      51.0,
      328.0
    ],
    "confidence": 0.7410693525086778,
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
    "reason": "too_far",
    "candidates": [
      {
        "component_id": "R1",
        "role": "value",
        "distance": 285.25,
        "reason": "too_far"
      },
      {
        "component_id": "R2",
        "role": "value",
        "distance": 238.13,
        "reason": "weak_context"
      },
      {
        "component_id": "R3",
        "role": "value",
        "distance": 197.74,
        "reason": "weak_context"
      },
      {
        "component_id": "V1",
        "role": "value",
        "distance": 236.37,
        "reason": "too_far"
      }
    ]
  },
  {
    "text": "37",
    "bbox": [
      338.0,
      317.0,
      408.0,
      345.0
    ],
    "confidence": 0.038902225481237826,
    "engine": "easyocr",
    "rotation": 0,
    "wire_overlap": true,
    "id": "t26",
    "raw": "37",
    "parsed": {
      "label": null,
      "number": 37.0,
      "unit": null,
      "internal": false,
      "unknown": false,
      "has_prefix": false,
      "unit_inferred": false,
      "confidence": 0.55,
      "emf_symbol": false,
      "normalized": "37",
      "normalizations": []
    },
    "assignments": [],
    "outcome": "unassigned",
    "reason": "weak_context",
    "candidates": [
      {
        "component_id": "R1",
        "role": "value",
        "distance": 238.36,
        "reason": "weak_context"
      },
      {
        "component_id": "R2",
        "role": "value",
        "distance": 172.31,
        "reason": "weak_context"
      },
      {
        "component_id": "R3",
        "role": "value",
        "distance": 99.3,
        "reason": "weak_context"
      },
      {
        "component_id": "V1",
        "role": "value",
        "distance": 68.68,
        "reason": "weak_context"
      }
    ]
  },
  {
    "text": "1",
    "bbox": [
      289.0,
      318.0,
      304.0,
      348.0
    ],
    "confidence": 0.39719692712765564,
    "component_id": "V1",
    "context": "dc_source",
    "engine": "easyocr",
    "rotation": 0,
    "wire_overlap": true,
    "id": "t27",
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
        "distance": 239.1,
        "reason": "weak_context"
      },
      {
        "component_id": "R2",
        "role": "value",
        "distance": 173.72,
        "reason": "weak_context"
      },
      {
        "component_id": "R3",
        "role": "value",
        "distance": 98.59,
        "reason": "weak_context"
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
    "text": ")",
    "bbox": [
      300.0,
      318.0,
      336.0,
      348.0
    ],
    "confidence": 0.0087293245502012,
    "component_id": "V1",
    "context": "dc_source",
    "engine": "easyocr",
    "rotation": 0,
    "wire_overlap": true,
    "id": "t28",
    "raw": ")",
    "parsed": null,
    "assignments": [],
    "outcome": "ignored",
    "reason": "not_parseable",
    "candidates": []
  },
  {
    "text": "1",
    "bbox": [
      406.0,
      318.0,
      434.0,
      345.0
    ],
    "confidence": 0.9957969338722741,
    "engine": "easyocr",
    "rotation": 0,
    "wire_overlap": true,
    "id": "t29",
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
        "distance": 248.12,
        "reason": "weak_context"
      },
      {
        "component_id": "R2",
        "role": "value",
        "distance": 182.78,
        "reason": "weak_context"
      },
      {
        "component_id": "R3",
        "role": "value",
        "distance": 119.71,
        "reason": "weak_context"
      },
      {
        "component_id": "V1",
        "role": "value",
        "distance": 115.68,
        "reason": "weak_context"
      }
    ]
  },
  {
    "text": "1",
    "bbox": [
      277.0,
      320.0,
      293.0,
      353.0
    ],
    "confidence": 0.7026347522139673,
    "component_id": "V1",
    "context": "dc_source",
    "engine": "easyocr",
    "rotation": 0,
    "wire_overlap": true,
    "id": "t30",
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
        "distance": 242.6,
        "reason": "weak_context"
      },
      {
        "component_id": "R2",
        "role": "value",
        "distance": 177.22,
        "reason": "weak_context"
      },
      {
        "component_id": "R3",
        "role": "value",
        "distance": 102.09,
        "reason": "weak_context"
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
    "text": "664",
    "bbox": [
      219.0,
      352.0,
      283.0,
      396.0
    ],
    "confidence": 0.4093804724418225,
    "engine": "easyocr",
    "rotation": 0,
    "wire_overlap": false,
    "id": "t31",
    "raw": "664",
    "parsed": {
      "label": null,
      "number": 664.0,
      "unit": null,
      "internal": false,
      "unknown": false,
      "has_prefix": false,
      "unit_inferred": false,
      "confidence": 0.55,
      "emf_symbol": false,
      "normalized": "664",
      "normalizations": []
    },
    "assignments": [],
    "outcome": "unassigned",
    "reason": "weak_context",
    "candidates": [
      {
        "component_id": "R1",
        "role": "value",
        "distance": 280.1,
        "reason": "too_far"
      },
      {
        "component_id": "R2",
        "role": "value",
        "distance": 214.72,
        "reason": "weak_context"
      },
      {
        "component_id": "R3",
        "role": "value",
        "distance": 139.59,
        "reason": "weak_context"
      },
      {
        "component_id": "V1",
        "role": "value",
        "distance": 34.05,
        "reason": "weak_context"
      }
    ]
  },
  {
    "text": "0.6",
    "bbox": [
      294.0,
      361.0,
      364.0,
      396.0
    ],
    "confidence": 0.34763733219297777,
    "engine": "easyocr",
    "rotation": 0,
    "wire_overlap": false,
    "id": "t32",
    "raw": "0.6",
    "parsed": {
      "label": null,
      "number": 0.6,
      "unit": null,
      "internal": false,
      "unknown": false,
      "has_prefix": false,
      "unit_inferred": false,
      "confidence": 0.55,
      "emf_symbol": false,
      "normalized": "0.6",
      "normalizations": []
    },
    "assignments": [],
    "outcome": "unassigned",
    "reason": "weak_context",
    "candidates": [
      {
        "component_id": "R1",
        "role": "value",
        "distance": 284.6,
        "reason": "too_far"
      },
      {
        "component_id": "R2",
        "role": "value",
        "distance": 219.22,
        "reason": "weak_context"
      },
      {
        "component_id": "R3",
        "role": "value",
        "distance": 144.09,
        "reason": "weak_context"
      },
      {
        "component_id": "V1",
        "role": "value",
        "distance": 35.43,
        "reason": "weak_context"
      }
    ]
  },
  {
    "text": ":",
    "bbox": [
      276.0,
      366.0,
      300.0,
      393.0
    ],
    "confidence": 0.7994735580169277,
    "engine": "easyocr",
    "rotation": 0,
    "wire_overlap": false,
    "id": "t33",
    "raw": ":",
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
|"before"|"R1"|"resistor"|null|{"number":6.8,"unit":"ohm","status":"assumed","source":"prior","confidence":0.0}|
|"before"|"R2"|"resistor"|null|{"number":6.8,"unit":"ohm","status":"assumed","source":"prior","confidence":0.0}|
|"before"|"R3"|"resistor"|null|{"number":null,"unit":"ohm","status":"assumed","source":"prior","confidence":0.0}|
|"before"|"V1"|"dc_source"|null|{"number":7.0,"unit":"V","status":"given","source":"ocr","confidence":0.55}|
|"before"|"retry.4.V2"|"dc_source"|null|{"number":7.0,"unit":"V","status":"given","source":"ocr","confidence":0.55}|
|"before"|"retry.5.S1"|"switch"|null|{"number":null,"unit":"ohm","status":"assumed","source":"prior","confidence":0.0}|
|"before"|"retry.6.R3"|"resistor"|null|{"number":7.0,"unit":"ohm","status":"given","source":"ocr","confidence":0.55}|
|"before"|"retry.7.R5"|"resistor"|null|{"number":6.8,"unit":"ohm","status":"assumed","source":"prior","confidence":0.0}|
|"WP-A"|"R1"|"resistor"|null|{"number":10.0,"unit":"ohm","status":"assumed","source":"prior","confidence":0.0,"unit_inferred":false}|
|"WP-A"|"R2"|"resistor"|null|{"number":10.0,"unit":"ohm","status":"assumed","source":"prior","confidence":0.0,"unit_inferred":false}|
|"WP-A"|"R3"|"resistor"|null|{"number":10.0,"unit":"ohm","status":"assumed","source":"prior","confidence":0.0,"unit_inferred":false}|
|"WP-A"|"V1"|"dc_source"|null|{"number":12.0,"unit":"V","status":"assumed","source":"prior","confidence":0.0,"unit_inferred":false}|

WP-A graph: **8 nodes**; any computed nonzero current: **false**. This is not a topology accuracy score.

The OCR annotation shows components and text, not wire connectivity. WP-B adds wire overlays and records whether repairs improve the graph.

## WP-B tracing replay

Same WP-A detections and OCR; no detector/OCR rerun or gold topology claim. Wire overlay: `.cache/round3/wires/case-001.png` (local only).

```json
{
  "image": "Screenshot 2026-10-30 232522.png",
  "before": {
    "nodes": 8,
    "parts": 4,
    "disabled": 0,
    "provenance": "extracted",
    "nonzero_current": false,
    "score": 42,
    "warnings": [
      {
        "code": "time_budget",
        "ref": null,
        "message_key": "warn.time_budget"
      },
      {
        "code": "uncertain_topology",
        "ref": "R1",
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
        "ref": "isolated.R1.b",
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
        "ref": "n10",
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
        "ref": "n21",
        "message_key": "warn.no_closed_loop"
      },
      {
        "code": "dangling_wire",
        "ref": "p3",
        "message_key": "warn.dangling_wire"
      },
      {
        "code": "dangling_wire",
        "ref": "p4",
        "message_key": "warn.dangling_wire"
      },
      {
        "code": "dangling_wire",
        "ref": "p5",
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
        "ref": "p13",
        "message_key": "warn.dangling_wire"
      },
      {
        "code": "dangling_wire",
        "ref": "p15",
        "message_key": "warn.dangling_wire"
      },
      {
        "code": "dangling_wire",
        "ref": "p19",
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
        "ref": "p31",
        "message_key": "warn.dangling_wire"
      },
      {
        "code": "assumed_value",
        "ref": "R1",
        "message_key": "warn.assumed_value"
      },
      {
        "code": "assumed_value",
        "ref": "R2",
        "message_key": "warn.assumed_value"
      },
      {
        "code": "assumed_value",
        "ref": "R3",
        "message_key": "warn.assumed_value"
      },
      {
        "code": "assumed_value",
        "ref": "V1",
        "message_key": "warn.assumed_value"
      },
      {
        "code": "value_not_found",
        "ref": "R1",
        "message_key": "warn.value_not_found"
      },
      {
        "code": "value_not_found",
        "ref": "R2",
        "message_key": "warn.value_not_found"
      },
      {
        "code": "value_not_found",
        "ref": "R3",
        "message_key": "warn.value_not_found"
      },
      {
        "code": "value_not_found",
        "ref": "V1",
        "message_key": "warn.value_not_found"
      }
    ]
  },
  "after": {
    "nodes": 5,
    "parts": 4,
    "disabled": 0,
    "provenance": "partial",
    "nonzero_current": false,
    "score": 31,
    "warnings": [
      {
        "code": "off_axis_snap",
        "ref": "R1",
        "message_key": "warn.off_axis_snap"
      },
      {
        "code": "off_axis_snap",
        "ref": "R3",
        "message_key": "warn.off_axis_snap"
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
        "ref": "R3",
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
        "ref": "n17",
        "message_key": "warn.no_closed_loop"
      },
      {
        "code": "no_closed_loop",
        "ref": "n21",
        "message_key": "warn.no_closed_loop"
      },
      {
        "code": "no_closed_loop",
        "ref": "n27",
        "message_key": "warn.no_closed_loop"
      },
      {
        "code": "no_closed_loop",
        "ref": "n29",
        "message_key": "warn.no_closed_loop"
      },
      {
        "code": "dangling_wire",
        "ref": "p2",
        "message_key": "warn.dangling_wire"
      },
      {
        "code": "dangling_wire",
        "ref": "p3",
        "message_key": "warn.dangling_wire"
      },
      {
        "code": "dangling_wire",
        "ref": "p5",
        "message_key": "warn.dangling_wire"
      },
      {
        "code": "dangling_wire",
        "ref": "p11",
        "message_key": "warn.dangling_wire"
      },
      {
        "code": "dangling_wire",
        "ref": "p12",
        "message_key": "warn.dangling_wire"
      },
      {
        "code": "dangling_wire",
        "ref": "p13",
        "message_key": "warn.dangling_wire"
      },
      {
        "code": "dangling_wire",
        "ref": "p21",
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
        "ref": "p33",
        "message_key": "warn.dangling_wire"
      },
      {
        "code": "dangling_wire",
        "ref": "p34",
        "message_key": "warn.dangling_wire"
      },
      {
        "code": "dangling_wire",
        "ref": "p35",
        "message_key": "warn.dangling_wire"
      },
      {
        "code": "dangling_wire",
        "ref": "p40",
        "message_key": "warn.dangling_wire"
      }
    ]
  },
  "trace": {
    "alternative_threshold": false,
    "repair": false,
    "terminals_snapped": 8,
    "terminals_floating": 0,
    "off_axis_snaps": 2,
    "gaps_bridged": 0,
    "stroke_width": 3.0,
    "ghosts": [
      {
        "bbox": [
          254,
          247,
          269,
          301
        ],
        "from": [
          260,
          295
        ],
        "to": [
          263,
          253
        ],
        "reason": "missing_part"
      }
    ]
  },
  "seconds": 2.7225356999988435,
  "scope": "Tracing-only replay on identical WP-A detections/texts; no gold topology accuracy."
}
```
