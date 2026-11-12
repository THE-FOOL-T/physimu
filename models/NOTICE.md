# Bundled inference models

These are unmodified copies of the five inference files used by the working
hybrid setup. `manifest.json` records their SHA-256 hashes, sizes, roles, and
source projects. They are stored through Git LFS; the complete portable release
ZIP includes their materialized bytes. No training datasets are bundled.

## Circuit detector

`v2_original.pt` is the owner's existing fine-tuned Ultralytics YOLO26 checkpoint.
Training provenance and limitations are in [MODEL_CARD.md](MODEL_CARD.md).
Ultralytics publishes its software/models under AGPL-3.0 with an Enterprise
alternative. Its upstream license is preserved in
`licenses/Ultralytics-AGPL-3.0.txt`.
Source: <https://github.com/ultralytics/ultralytics>.
Terms: <https://www.ultralytics.com/license>.
The existing project code and training tools are in this source repository.
This notice records upstream terms; it does not replace any applicable Enterprise
agreement or establish rights to the original training-image collection.

## RapidOCR / PaddleOCR

The three ONNX files are copied from the installed RapidOCR 3.10.0 model directory.
The PP-OCR models originate with PaddleOCR and are converted for ONNX by RapidAI.
The direction classifier is the existing
`ch_ppocr_mobile_v2.0_cls_mobile.onnx`, also used by RapidOCR.

Copyright (c) 2021 RapidOCR Authors / RapidAI.
Copyright (c) 2016 PaddlePaddle Authors.
Apache License 2.0 texts are preserved in `licenses/RapidOCR-Apache-2.0.txt`
and `licenses/PaddleOCR-Apache-2.0.txt`.
Sources: <https://github.com/RapidAI/RapidOCR>,
<https://modelscope.cn/models/RapidAI/RapidOCR>,
<https://github.com/PaddlePaddle/PaddleOCR>.

## EasyOCR

`bengali.pth` is the existing Bengali recognizer from the local EasyOCR cache.
EasyOCR is maintained by JaidedAI under Apache License 2.0, preserved in
`licenses/EasyOCR-Apache-2.0.txt`.
Sources: <https://github.com/JaidedAI/EasyOCR>,
<https://github.com/JaidedAI/EasyOCR/releases/tag/v1.1.8>.

Models retain their upstream terms and carry no accuracy guarantee.
This inventory makes no project-wide license grant.
