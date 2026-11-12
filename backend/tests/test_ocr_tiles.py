import numpy as np
import pytest
from circuit_sim.backend.pipeline.ocr_tiles import windows, merge, easy_tiles


def test_native_word_proposals_keep_small_text_and_drop_long_wire():
    import cv2
    from circuit_sim.backend.pipeline.ocr_tiles import candidate_regions

    image = np.full((1800, 1800, 3), 255, np.uint8)
    cv2.putText(image, "12 V", (100, 110), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (0, 0, 0), 1)
    cv2.line(image, (0, 500), (1700, 500), (0, 0, 0), 2)
    regions = candidate_regions(image)
    assert any(x <= 100 and y < 110 and x2 > 120 for x, y, x2, y2 in regions)
    assert not any(y <= 500 <= y2 and x2 - x > 1000 for x, y, x2, y2 in regions)


@pytest.mark.skipif(
    __import__("os").getenv("CIRCUIT_REAL_OCR_TEST") != "1",
    reason="Explicit local-model OCR benchmark; ~1 minute CPU",
)
def test_real_small_label_recall_before_after():
    from circuit_sim.backend.tools.ocr_benchmark import main

    result = main()
    if result.get("after_recall") is None:
        pytest.skip("Local EasyOCR models are not installed")
    assert result["samples"] == 18
    assert result["after_recall"] > result["before_recall"]


def test_native_tiles_cover_full_page_with_overlap():
    boxes = windows(np.zeros((1800, 1800, 3), np.uint8))
    assert len(boxes) == 4
    coverage = np.zeros((1800, 1800), np.uint8)
    for x, y, x2, y2 in boxes:
        coverage[y:y2, x:x2] += 1
    assert coverage.min() == 1
    assert coverage.max() == 4


def test_component_region_filter_and_nms():
    from types import SimpleNamespace

    boxes = windows(np.zeros((1800, 1800, 3), np.uint8), [SimpleNamespace(bbox=(50, 50, 100, 100))])
    assert boxes == [(0, 0, 1024, 1024)]
    items = [
        {"text": "12 V", "bbox": [10, 10, 50, 24], "confidence": 0.9},
        {"text": "12V", "bbox": [11, 10, 51, 24], "confidence": 0.5},
        {"text": "4Ω", "bbox": [80, 10, 110, 24], "confidence": 0.8},
    ]
    assert len(merge(items)) == 2
    assert merge(items)[0]["text"] == "12 V"


def test_native_box_mapping_and_small_crop_upsampling(monkeypatch):
    from circuit_sim.backend.pipeline import ocr_tiles

    monkeypatch.setattr(ocr_tiles, "candidate_regions", lambda tile: [(0, 0, 1024, 1024)])

    class Reader:
        calls = 0
        heights = []

        def recognize(self, image, **kwargs):
            self.calls += 1
            self.heights.extend(box[3] - box[2] for box in kwargs["horizontal_list"])
            return [
                (
                    [
                        [a + 100, y + 100],
                        [a + 150, y + 100],
                        [a + 150, y + 110],
                        [a + 100, y + 110],
                    ],
                    "12 V",
                    0.95,
                )
                for a, b, y, y2 in kwargs["horizontal_list"]
            ]

    reader = Reader()
    result = easy_tiles(np.full((1800, 1800, 3), 255, np.uint8), reader, lambda: reader)
    assert reader.calls == 1
    assert all(h >= 32 for h in reader.heights)
    assert [r["bbox"] for r in result] == [
        [100, 100, 150, 110],
        [876, 100, 926, 110],
        [100, 876, 150, 886],
        [876, 876, 926, 886],
    ]


def test_batched_small_crop_is_upsampled_and_maps_back_exactly(monkeypatch):
    from circuit_sim.backend.pipeline import ocr_tiles

    monkeypatch.setattr(ocr_tiles, "candidate_regions", lambda tile: [(100, 100, 150, 110)])

    class Reader:
        def recognize(self, image, **kwargs):
            assert all(box[3] - box[2] >= 32 for box in kwargs["horizontal_list"])
            return [
                ([[a, y], [b, y], [b, y2], [a, y2]], "12 V", 0.95)
                for a, b, y, y2 in kwargs["horizontal_list"]
            ]

    result = easy_tiles(np.full((300, 300, 3), 255, np.uint8), Reader(), lambda: Reader())
    assert result[0]["bbox"] == [100, 100, 150, 110]


def test_no_download_and_no_remote_reader_without_optin(monkeypatch):
    monkeypatch.setenv("CIRCUIT_OCR_BACKEND", "legacy")
    from circuit_sim.backend.pipeline import text

    class Remote:
        def read_labels(self, image):
            raise AssertionError("Privacy: unconsented network reader invoked")

    monkeypatch.setattr(text, "_vlm", Remote())
    monkeypatch.setattr(text.shutil, "which", lambda _: None)
    monkeypatch.setattr(
        text, "easy_reader", lambda *a, **k: (_ for _ in ()).throw(FileNotFoundError())
    )
    items, warnings = text.read_text(np.full((100, 100, 3), 255, np.uint8), handwritten=True)
    assert items == []
    assert ("ocr_unavailable", None) in warnings
