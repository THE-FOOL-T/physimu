# OCR-to-component association

The association stage consumes the component detections and OCR regions already
produced by the pipeline. It does not train a second detector or require an
association checkpoint.

## Matching procedure

`backend/pipeline/associate.py` uses a global, geometry-first assignment:

1. Parse reference designators, values, units, unknown-value marks and source
   internal-resistance labels from each OCR region.
2. Reject physically incompatible candidates. For example, `Ω` values are
   considered for resistor-like parts, `V` for voltage sources, `F` for
   capacitors, and `A` for current sources. Reference prefixes such as `R`,
   `C`, `L`, `V`, `I` and `S` constrain the component class.
3. Score each remaining text/component pair using normalized box-edge distance,
   center distance and the component terminal axis. The score is scale-aware,
   so it does not rely on a single pixel radius.
4. Use the Hungarian assignment algorithm to avoid greedy collisions.
5. Abstain when a text box is almost equally close to two compatible parts or
   when the best score is worse than the unmatched option.
6. Treat a combined OCR region such as `R1 = 100 Ω` as one name/value pair. It
   cannot assign the name to one part and the value to another.
7. Use the side of a component occupied by its reference label as supporting
   evidence when assigning a separate value. Plus/minus marks are matched to
   source terminals.

The function remains compatible with existing calls:
`associate(components, texts, weight=1.0)`. It mutates component labels, values,
internal resistance and polarity as before, and now returns match diagnostics.
Each matched OCR dictionary also receives an `association` field, for example:

```json
{
  "component_id": "R1",
  "role": "value",
  "score": 0.73,
  "confidence": 0.85
}
```

The score is a normalized matching cost, not a probability. The confidence is
the lower of the OCR confidence and the value parser's confidence; it is not
calibrated as a probability either. The pipeline's existing
`diagnostics.texts` output therefore contains the association decision beside
the original OCR text and bounding box.

## Detector checkpoint

The uploaded `last.pt` SHA-256 is
`95bc8a1f76aaed83ad907e87bdee0255da1837fdb8f9c8405a723779e8ed0c46`, matching
the checkpoint recorded in `models/MODEL_CARD.md`. The repository expects this
checkpoint at `models/v2_original.pt` (or via `CIRCUIT_MODEL`). Keep weights out
of Git, as the repository already intends.

The association matcher itself does not use `best.pt` or `last.pt`; those files
are object-detection weights. A new trained association model is not required
for this geometry-first version.

## Tests and measured scope

Run the repository test command:

```bash
python manage.py test
```

The added tests cover combined labels/values, global assignment, reference-prefix
and unit compatibility, ambiguous cases, separate label/value placement,
unitless values, user-value protection, source internal resistance and polarity.
A seeded synthetic-layout test also checks at least 90% assignment coverage and
zero wrong links on generated boxes. Its current run covered 120 generated
layouts and 904 OCR regions: 874 were assigned, all 874 assignments were
correct, and 30 were left unassigned (96.7% coverage and 100% precision among
assigned regions). These are generated horizontal-resistor layouts with
synthetic OCR boxes, not textbook scans or phone photographs.

The repository does not currently contain an independently annotated
text-to-component benchmark. Do not describe the system as having 90% real-image
accuracy until such a benchmark has been run.

## Measuring real association accuracy

Prepare a JSONL file with one diagram per line. Include the detected components
and OCR regions, then manually add `target_component` to each OCR region that
should attach to a component. The value must be the component's `id`. Example:

```json
{
  "components": [
    {
      "id": "R1",
      "type": "resistor",
      "bbox": [100, 80, 150, 110],
      "terminals": [
        {"id": "R1.a", "xy": [100, 95], "node": "n1"},
        {"id": "R1.b", "xy": [150, 95], "node": "n2"}
      ],
      "value": {"unit": "ohm"}
    }
  ],
  "texts": [
    {
      "text": "R1",
      "bbox": [108, 48, 130, 64],
      "confidence": 0.96,
      "target_component": "R1"
    },
    {
      "text": "100 Ω",
      "bbox": [108, 28, 145, 44],
      "confidence": 0.93,
      "target_component": "R1"
    }
  ]
}
```

Run:

```bash
python -m circuit_sim.backend.tools.eval_association \
  --input data/eval/association.jsonl \
  --output docs/association-results.json
```

Read the two primary metrics separately:

- `precision_when_assigned`: fraction of made associations that are correct.
- `assignment_coverage`: fraction of annotated OCR regions that received an
  association.

The target is at least 0.90 for both. `correct_over_all_annotated` is their
combined measure. Include printed diagrams, handwritten diagrams, different
books, varied layouts and phone photos. Split by source book/page before tuning
thresholds; do not tune and report on the same pages.

