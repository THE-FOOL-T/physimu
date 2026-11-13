"""Controlled evidence is integration proof, not a detector accuracy benchmark."""

import copy

import numpy as np
import pytest

from circuit_sim.backend.domains.mechanics.engine import analyze_mechanics_page
from circuit_sim.backend.domains.mechanics.labels import read_tokens, parse
from circuit_sim.backend.domains.mechanics.associate import associate
from circuit_sim.backend.domains.mechanics.evidence import Evidence
from circuit_sim.backend.domains.mechanics.archetypes import hypotheses, match
from circuit_sim.backend.domains.mechanics.relationships import body_endpoints
from circuit_sim.backend.domains.mechanics.understanding import select_region
from circuit_sim.backend.domains.mechanics.detect import WeightsUnavailable, Detection
from circuit_sim.backend.tests.mechanics.perception_fixtures import case
from circuit_sim.backend.tools.mechanics.build_fixtures import fixtures


@pytest.mark.parametrize("name", list(fixtures()))
def test_all_fixture_pipelines_publish_owning_graph_and_readiness(name):
    image, truth, detector, reader = case(name)
    result = analyze_mechanics_page(
        image, {"style": "printed"}, detector=detector, text_reader=reader
    )
    evidence = Evidence.model_validate(result["diagnostics"]["evidence"])
    s = result["scene"]
    assert result["readiness"]["status"] == "needs_review"
    assert result["readiness"]["physics_supported"]
    assert s["archetype"] == truth.archetype
    assert all(o.detection_id for o in evidence.objects)
    assert evidence.coordinate_system == "native_image_pixels_x_right_y_down"
    assert any(h.archetype == truth.archetype and not h.contradictions for h in evidence.hypotheses)
    assert all(
        r.source in {a["id"] for a in s["annotations"]}
        for r in evidence.relationships
        if r.type == "LABEL_OF"
    )
    assert all(
        r.target.startswith(("params.", "bodies.", "links.", "surfaces.", "constants."))
        for r in evidence.relationships
        if r.type == "LABEL_OF"
    )
    if s["pulleys"]:
        assert any(r.type == "PASSES_OVER" and r.state == "assumed" for r in evidence.relationships)


@pytest.mark.parametrize("name", list(fixtures()))
def test_topology_ranking_preserves_existing_supported_fixture_classification(name):
    s = fixtures()[name].model_dump(mode="json", by_alias=True)
    assert match(s)[0] == s["archetype"]
    best = next(r for r in hypotheses(s) if r["archetype"] == s["archetype"])
    assert not best["contradictions"] and best["supporting"]


def test_extra_annotation_does_not_change_topology_and_unsupported_link_is_not_forced():
    s = fixtures()["pendulum"].model_dump(mode="json", by_alias=True)
    s["annotations"].append(dict(id="noise", type="label", geometry=dict(text="note")))
    assert match(s)[0] == "pendulum"
    s["links"].append(copy.deepcopy(s["links"][0]))
    s["links"][-1]["id"] = "extra_constraint"
    assert match(s)[0] == "unsupported"
    row = next(r for r in hypotheses(s) if r["archetype"] == "pendulum")
    assert row["contradictions"]


def test_conflicting_ocr_keeps_value_unplaced_and_equally_close_owners_need_review():
    rows = [
        dict(
            text="m1=2 kg",
            bbox=[100.0, 100.0, 140.0, 120.0],
            confidence=0.9,
            alternatives=[dict(text="m1=7 kg", confidence=0.92)],
        )
    ]
    token = read_tokens(rows)[0]
    assert token.conflict
    s = fixtures()["collision"].model_dump(mode="json", by_alias=True)
    before = copy.deepcopy(s["bodies"])
    report = associate(s, [token])
    assert report[0]["reason"] == "conflicting_readings" and not report[0]["accepted"]
    assert s["bodies"] == before
    for b in s["bodies"]:
        b["mass"].update(status="assumed", source="prior")
    a, b = s["bodies"]
    x = (a["anchor"][0] + b["anchor"][0]) / 2
    y = (a["anchor"][1] + b["anchor"][1]) / 2
    report = associate(s, parse("3 kg", [x - 5, y - 5, x + 5, y + 5]))
    assert not report[0]["accepted"] and report[0]["reason"] in {
        "ambiguous_owner",
        "no_plausible_owner",
    }
    assert parse("a=3 m/s²")[0].kind == "acceleration"


def test_missing_rope_end_is_unresolved_not_connected_to_the_nearest_distant_body():
    s = fixtures()["atwood"].model_dump(mode="json", by_alias=True)
    points = [[1.0, 1.0], [10.0, 10.0], [20.0, 20.0]]
    assert body_endpoints(points, s["bodies"]) == []
    image, _, detector, reader = case("atwood")

    def missing(im, check):
        rows = detector(im, check)
        return [r for r in rows if r.type != "rope"]

    result = analyze_mechanics_page(image, detector=missing, text_reader=reader)
    assert result["scene"]["archetype"] == "unsupported"
    assert not result["readiness"]["physics_supported"]
    assert result["scene"]["links"] == []


def test_missing_weights_and_detector_failure_have_specific_honest_states():
    image = np.full((100, 200, 3), 255, np.uint8)

    def missing(*a, **k):
        raise WeightsUnavailable("TEST absent local model")

    result = analyze_mechanics_page(image, detector=missing)
    assert result["readiness"]["status"] == "needs_model"
    assert not result["diagnostics"]["evidence"]["detections"]

    def failed(*a, **k):
        raise RuntimeError("TEST detector failure")

    result = analyze_mechanics_page(image, detector=failed)
    assert result["readiness"]["status"] == "unsupported"
    assert any(i["code"] == "detector_failed" for i in result["readiness"]["issues"])


def test_ocr_failure_retains_geometry_and_native_pixels_without_fabricated_readings():
    image, truth, detector, _ = case("pendulum")
    frozen = image.copy()

    def failed(*a, **k):
        raise RuntimeError("TEST OCR failure")

    result = analyze_mechanics_page(
        image, {"style": "handwritten"}, detector=detector, text_reader=failed
    )
    assert np.array_equal(image, frozen)
    assert result["scene"]["image"]["width"] == truth.image.width
    assert result["scene"]["bodies"]
    assert not result["diagnostics"]["evidence"]["ocr"]
    assert any(i["code"] == "ocr_failed" for i in result["readiness"]["issues"])


def test_region_selection_is_native_and_rejects_nonfinite_or_outside_requests():
    assert select_region([[0, 0, 40, 80], [50, 0, 100, 80]], [50, 0, 100, 80], 100, 80) == [
        50.0,
        0.0,
        100.0,
        80.0,
    ]
    for region in ([0, 0, float("nan"), 80], [-1, 0, 40, 80], [40, 0, 20, 80]):
        with pytest.raises(ValueError, match="invalid_figure_region"):
            select_region([], region, 100, 80)
