# Asset reconnaissance

Existing README and handoff read. Source project: `D:/AugmentedPhysics`. No source files changed.

The original 59-image collection was used to TRAIN v2. Its historical evaluation directory name does not make it held-out data. The additional 99-image set has labels; independence must be checked against training manifests before using it as a frozen benchmark.

Model and image inventory (observed, not assumed):

```json
{
  "weights": "D:\\AugmentedPhysics\\runs\\augmented_physics\\circuits_real_v2_20261031\\weights\\last.pt",
  "copy": "models/v2_original.pt",
  "sha256": "95bc8a1f76aaed83ad907e87bdee0255da1837fdb8f9c8405a723779e8ed0c46",
  "task": "detect",
  "architecture": "DetectionModel",
  "names": {
    "0": "resistor",
    "1": "voltage_source",
    "2": "capacitor",
    "3": "switch"
  },
  "training_imgsz": 960,
  "inference_imgsz": 640,
  "images": [
    {
      "path": "D:/AugmentedPhysics/datasets/circuits_v1/real_v1/evaluation_v1/images",
      "count": 59,
      "sizes": {
        "643x415 PNG": 1,
        "595x367 PNG": 1,
        "606x366 PNG": 1,
        "591x346 PNG": 1,
        "463x208 PNG": 1,
        "334x190 PNG": 1,
        "270x160 PNG": 1,
        "403x168 PNG": 1,
        "340x192 PNG": 1,
        "307x204 PNG": 1,
        "472x193 PNG": 1,
        "361x205 PNG": 1,
        "351x174 PNG": 1,
        "316x211 PNG": 1,
        "333x244 PNG": 1,
        "462x255 PNG": 1,
        "358x193 PNG": 1,
        "360x202 PNG": 1,
        "339x183 PNG": 1,
        "400x211 PNG": 1,
        "394x196 PNG": 1,
        "331x243 PNG": 1,
        "310x258 PNG": 1,
        "375x180 PNG": 1,
        "367x255 PNG": 1,
        "369x267 PNG": 1,
        "366x220 PNG": 1,
        "283x190 PNG": 1,
        "469x234 PNG": 1,
        "409x271 PNG": 1,
        "355x232 PNG": 1,
        "445x241 PNG": 1,
        "516x159 PNG": 1,
        "439x252 PNG": 1,
        "513x333 PNG": 1,
        "336x202 PNG": 1,
        "412x222 PNG": 1,
        "553x267 PNG": 1,
        "447x274 PNG": 1,
        "406x162 PNG": 1,
        "313x190 PNG": 1,
        "373x261 PNG": 1,
        "510x277 PNG": 1,
        "477x193 PNG": 1,
        "451x220 PNG": 1,
        "427x189 PNG": 1,
        "348x148 PNG": 1,
        "318x237 PNG": 1,
        "355x228 PNG": 1,
        "352x234 PNG": 1,
        "315x175 PNG": 1,
        "271x172 PNG": 1,
        "325x210 PNG": 1,
        "253x175 PNG": 1,
        "381x156 PNG": 1,
        "244x174 PNG": 1,
        "294x160 PNG": 1,
        "360x174 PNG": 1,
        "352x202 PNG": 1
      },
      "label_counts": {
        "txt": 59,
        "json": 1,
        "xml": 0
      }
    },
    {
      "path": "D:/AugmentedPhysics/datasets/circuits_v2/user_verified_99_20261105/images",
      "count": 99,
      "sizes": {
        "454x283 WEBP": 1,
        "314x255 WEBP": 1,
        "231x317 WEBP": 1,
        "342x294 WEBP": 1,
        "736x1000 PNG": 1,
        "450x315 JPEG": 1,
        "695x729 PNG": 1,
        "724x733 PNG": 1,
        "465x231 WEBP": 1,
        "586x627 PNG": 1,
        "737x725 PNG": 1,
        "460x435 JPEG": 1,
        "1600x1000 PNG": 40,
        "511x144 PNG": 1,
        "313x166 PNG": 1,
        "315x136 PNG": 1,
        "313x138 PNG": 1,
        "303x112 PNG": 1,
        "222x96 PNG": 1,
        "265x130 PNG": 1,
        "301x118 PNG": 1,
        "352x126 PNG": 1,
        "306x136 PNG": 1,
        "303x142 PNG": 1,
        "223x121 PNG": 1,
        "228x112 PNG": 1,
        "310x165 PNG": 1,
        "403x150 PNG": 1,
        "315x157 PNG": 1,
        "340x99 PNG": 1,
        "307x150 PNG": 1,
        "226x151 PNG": 1,
        "148x118 PNG": 1,
        "223x123 PNG": 1,
        "352x175 PNG": 1,
        "219x202 PNG": 1,
        "466x219 PNG": 1,
        "495x193 PNG": 1,
        "291x163 PNG": 1,
        "319x199 PNG": 1,
        "298x172 PNG": 1,
        "390x184 PNG": 1,
        "396x327 PNG": 1,
        "345x144 PNG": 1,
        "249x142 PNG": 1,
        "315x169 PNG": 1,
        "403x178 PNG": 1,
        "927x652 PNG": 1,
        "634x424 PNG": 1,
        "1197x508 PNG": 1,
        "1000x565 PNG": 1,
        "1000x616 PNG": 1,
        "1427x605 PNG": 1,
        "454x223 WEBP": 1,
        "453x249 WEBP": 1,
        "441x315 JPEG": 1,
        "896x315 WEBP": 1,
        "427x274 WEBP": 1,
        "735x729 PNG": 1,
        "1000x737 PNG": 1
      },
      "label_counts": {
        "txt": 99,
        "json": 1,
        "xml": 1
      }
    }
  ],
  "samples": [
    {
      "image": "Screenshot 2026-10-30 232522.png",
      "detections": 4,
      "classes": {
        "resistor": 3,
        "voltage_source": 1
      }
    },
    {
      "image": "Screenshot 2026-10-30 232632.png",
      "detections": 5,
      "classes": {
        "resistor": 4,
        "voltage_source": 1
      }
    },
    {
      "image": "Screenshot 2026-10-30 232905.png",
      "detections": 7,
      "classes": {
        "resistor": 6,
        "voltage_source": 1
      }
    },
    {
      "image": "Screenshot 2026-10-30 232921.png",
      "detections": 7,
      "classes": {
        "resistor": 6,
        "voltage_source": 1
      }
    },
    {
      "image": "Screenshot 2026-10-30 234003.png",
      "detections": 6,
      "classes": {
        "resistor": 3,
        "voltage_source": 1,
        "switch": 2
      }
    },
    {
      "image": "Screenshot 2026-10-30 234104.png",
      "detections": 5,
      "classes": {
        "resistor": 4,
        "voltage_source": 1
      }
    },
    {
      "image": "Screenshot 2026-10-30 234210.png",
      "detections": 4,
      "classes": {
        "resistor": 3,
        "voltage_source": 1
      }
    },
    {
      "image": "Screenshot 2026-10-30 234420.png",
      "detections": 4,
      "classes": {
        "resistor": 3,
        "voltage_source": 1
      }
    },
    {
      "image": "Screenshot 2026-10-30 234517.png",
      "detections": 6,
      "classes": {
        "resistor": 5,
        "switch": 1
      }
    },
    {
      "image": "Screenshot 2026-10-30 234541.png",
      "detections": 5,
      "classes": {
        "resistor": 4,
        "voltage_source": 1
      }
    }
  ],
  "python": "3.12.11 | packaged by conda-forge | (main, Jun  4 2025, 14:29:09) [MSC v.1943 64 bit (AMD64)]",
  "gpu": false
}
```

Ten annotated predictions are in `recon_samples/`. Geometry/connectivity, source polarity and OCR are not detector outputs. Handwriting accuracy is unmeasured. See status.md for measured limitations.

Visual inspection of the samples found specific failures: the open key in the
three-parallel-branch figure (`232522`) is missed; the two-resistor figure
(`232632`) receives extra resistor predictions; in `234003`, low-confidence
switch boxes overlap diagonal resistor/annotation regions. Battery boxes follow
the plates rather than the lead direction, so terminal orientation cannot be
read directly from box aspect ratio. Labels and arrows remain outside the
four-class detector's vocabulary. The 960-pixel first inference exhausted CPU
memory on this machine; 640 pixels with one Torch thread completed all ten.

Follow-up audit: the 99-image collection's README and manifest explicitly record
the user's CVAT review and its role as a reference not used to retrain v2.
All 99 image hashes match that manifest. None matches the 695 recorded prior
image hashes in v2's input-fingerprint record. This proves exact-byte
disjointness only. It includes synthetic examples, is not split by handwriting
style, and has no gold netlists. See `reference_99_audit.json` and
`reference_99_metrics.md` for the separately labeled detector evaluation.
