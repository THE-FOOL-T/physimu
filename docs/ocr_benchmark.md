# Small-label OCR regression

## Round three assignment evidence (WP-A)

The owner approved using other diagrams instead of the unidentified 3.0 V boxed
diagram. All 59 configured images were run against frozen round-two code; the
five with the most assumed values were selected (ties by original file index).
`ocr_assignment_round3.json` and `cases/case-001.md` through `case-005.md` retain
raw readings, boxes, actual assignment decisions and final values. Owner rasters
and annotated PNGs stay in ignored `.cache/round3`.

Coverage changed from **7/34 (20.6%)** to **14/30 (46.7%)** detected parts marked
`given`. The denominator changed because recovery chose different detections.
This is **not accuracy**: the symbolic example has no numerical values, and its
old arrow/caption readings were false positives. Conflicting bare readings now
stay missing. The 24 V circuit reads its source and five of six resistors; 8 kΩ
remains unread. Rotated diamond labels and meter classifications remain weak.
Bare E is never accepted as a resistor name. Missing values have a notice and
can be entered through the text dialog/crop tool. No human-reviewed text gold
exists, so text and assignment accuracy remain **null**.

Only installed EasyOCR models ran locally. Tesseract is unavailable; the shared
dual-engine path is covered with mocks. No remote label reader was used.

The 10/12/14 px real-model synthetic benchmark was rerun too:
`ocr_benchmark_round3.json` retains all strings/timings. Exact recall is still
**5/18**; the proposal/association improvements do not establish better exact
recognition on this corpus. The round-two JSON below is preserved separately.

```sh
python manage.py ocr-debug path/to/diagram.png
python tools/ocr_eval.py --baseline .cache/round3/before.jsonl --limit 5
python -m backend.tools.case_report
```

The baseline JSONL is local evidence containing owner images and is deliberately
not committed. New baselines require running the old revision in an isolated
checkout. Gold format: `data/eval/text_gold/README.md`.

## Round two tiny-label measurement

Run `python -m backend.tools.ocr_benchmark` after explicitly installing local
EasyOCR English/Bengali models. No network or download occurs in this command.
The command writes `ocr_benchmark.json` with every recognized string and timing.

Corpus: 18 known strings on 1800×1800 canvases, rendered at 10, 12 and 14 px
glyph height: 4 Ω, 12 V, 2.2 kΩ, 100 µF, ২Ω and R₁. Recall means exact normalized
string equality, not electrical accuracy. Baseline is English EasyOCR detection
at 640 px; new path is native 1024 px overlapping tiles, duplicate NMS, crop
recognition upsampling to at least 32 px and ambiguous BN recognition.

Measured local CPU results (`ocr_benchmark.json`): exact recall improved from
**0/18 to 5/18 (27.8%)** after the WP7 crop-atlas optimization. This remains inadequate
label accuracy. Omega, micro, subscripts and Bangla digits
still fail on this deliberately small typography test. Recognized strings are
preserved in the JSON; no missing labels were filled in to improve the score.

|Glyph height|640 px baseline|Native ROI-tiled path|
|---|---:|---:|
|10 px|8.727 s|4.147 s|
|12 px|7.843 s|4.349 s|
|14 px|8.391 s|3.582 s|

The initial full-tile attempt took 81–86 s/page. That run also exposed missing
Omega/micro/subscript glyphs in the Noto Bengali font used by Pillow. Its raw
result is retained as `ocr_benchmark_initial.json`, **not a valid font-complete
accuracy comparison**. The final corpus uses DejaVu Sans for non-Bengali glyphs
and Noto Bengali for Bengali. Native connected-component word proposals now
avoid blank tile margins, then upsample each crop for recognition. CPU batch size is one to avoid
padding every short label to the widest crop; geometry is shared in one atlas.
WP7 packs those crops in an in-memory atlas and reuses geometry for EN/BN
recognition, removing repeated CRAFT passes. The intermediate ROI/CRAFT result
(3/18 recall, 9.9–11.9 s) is retained in `ocr_benchmark_roi_craft.json`.
Detector boxes filter unrelated windows in normal analysis. Full-page OCR still
is below six seconds on these three measured pages, with weak exact recall.
The working raster remains decoder-bounded to
1800 px. These are synthetic typography results, not handwriting accuracy.

Final measurement: Windows CPU, local EN/BN models, no external reader.

Unit checks: tile coverage and overlap, region filtering, duplicate suppression,
exact native coordinate mapping, recognition crop upsampling, and privacy when
remote reading is disabled. The opt-in real-model regression was executed; all 18 labels and raw output
are retained. See verification.md for final suite totals.
