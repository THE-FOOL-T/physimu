# Reviewed text gold format

No reviewed owner text labels have been supplied. Accuracy remains null.
Store one JSON file per independently annotated image:

```json
{
  "image": "relative/or/configured/input.png",
  "sha256": "the exact image SHA-256",
  "human_reviewed": true,
  "texts": [
    {"bbox": [10, 20, 70, 40], "text": "3.0 V", "component_id": "V1"}
  ]
}
```

This is a format example, not an annotation or approval. Use image-space boxes.
OCR evaluation reports exact normalized text and assignment correctness only
for entries explicitly reviewed; assignment coverage without gold is not accuracy.
Do not commit owner images. `python -m backend.tools.ocr_eval --help` documents
coverage evaluation; `python manage.py ocr-debug <image>` prints the full trace
and saves the annotated raster in ignored `.cache/ocr-debug`.
