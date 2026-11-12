"""Render recorded OCR evidence without re-running models or embedding owner rasters."""

import json
from pathlib import Path

from ..pipeline.values import parse_value

ROOT = Path(__file__).resolve().parents[2]
FINDINGS = [
    "The image is symbolic: R1/R2/R3 and current arrows have no numerical part values. "
    "Baseline numbers from arrows and the caption were false readings. Leaving all four "
    "values missing is the correct conservative outcome. All parts remain disconnected here.",
    "The source visibly says 24 V; it is now assigned 24 V. The visible 5k, 10k, 6k, 3k "
    "and 2k labels are assigned. R5 (8k in the drawing) remains unread. Detector order IDs "
    "differ from printed R2/R4 labels; use the boxes and label field, not IDs alone.",
    "The 230 V source and 5 ohm resistor are read. Rotated labels remain weak, and two "
    "resistors are misclassified as switches by v2. The circuit still has no conducting loop.",
    "5 V, 3 ohm, 2 ohm and 10 ohm are assigned. E is no longer a resistor name. The "
    "second source is symbolic, and the detector mistakes a meter for a capacitor. A "
    "nonzero computed current does not establish correct tracing or electrical accuracy.",
    "The visible 3 ohm label produces conflicting 332 / 30 / 39 readings; it now needs "
    "confirmation instead of assigning 332 ohm. The 5 V source and 2 ohm resistor are "
    "read. The visible 10 ohm label is in the OCR evidence but may remain unassigned. "
    "E is symbolic, and the ammeter reading must not become a resistance value.",
]


def compact(value):
    return json.dumps(value, ensure_ascii=False, separators=(",", ":")).replace("|", "\\|")


def main():
    report = json.loads((ROOT / "docs/ocr_assignment_round3.json").read_text(encoding="utf-8"))
    selected = set(report["images"])
    before = {}
    with (ROOT / ".cache/round3/before.jsonl").open(encoding="utf-8") as stream:
        for line in stream:
            item = json.loads(line)
            if item["image"] in selected:
                before[item["image"]] = item
    out = ROOT / "docs/cases"
    out.mkdir(parents=True, exist_ok=True)
    for index, current in enumerate(report["reports"]):
        original = before[current["image"]]
        lines = [
            f"# Case {index + 1:03}: {current['image']}",
            "",
            f"SHA-256: `{current['sha256']}`. Read-only configured owner input; raster excluded from Git.",
            "",
            FINDINGS[index],
            "",
            f"Inspected annotated image: `.cache/round3/case-{index + 1:03}.png` (local only).",
            "",
            "Both engine paths were requested. Tesseract is not installed on this machine; "
            "there are no real Tesseract readings to report. EasyOCR EN/BN uses installed local models. "
            "Dual-engine selection is tested with mocks, not claimed as a local Tesseract benchmark.",
            "",
            "## Frozen round-two evidence",
            "",
            "The trace below records actual Hungarian selections (including recovery attempts). "
            "A selected candidate does not necessarily survive the final netlist. The old API did "
            "not retain every rejected pair; unselected candidates are reported as such rather "
            "than inventing a rejection distance.",
            "",
            "|Raw text|Native box|Old parse|Actual selection (role, part, cost / dummy)|",
            "|---|---|---|---|",
        ]
        for item in original["result"].get("diagnostics", {}).get("texts", []):
            selections = [
                t
                for t in original.get("assignment_trace", [])
                if t["text"] == item["text"] and t["bbox"] == item["bbox"]
            ]
            traces = [
                {k: t.get(k) for k in ("role", "component", "cost", "dummy_cost")}
                for t in selections
            ]
            parsed = item.get("baseline_parsed")
            reason = traces or (
                "not parseable" if parsed is None else "not selected; rejection pairs not retained"
            )
            lines.append(
                "|"
                + "|".join(compact(v) for v in (item["text"], item["bbox"], parsed, reason))
                + "|"
            )
        lines += [
            "",
            "## Current raw engine readings",
            "",
            "|Engine / rotation|Raw text|Native box|Current parse in anchored context|",
            "|---|---|---|---|",
        ]
        for item in current["diagnostics"].get("engine_readings", []):
            values = (
                f"{item.get('engine', 'easyocr')} / {item.get('rotation', 0)}",
                item["text"],
                item["bbox"],
                parse_value(item["text"], item.get("context")),
            )
            lines.append("|" + "|".join(compact(v) for v in values) + "|")
        lines += [
            "",
            "## Current association decisions",
            "",
            "Every tested component/role pair includes its measured distance and rejection reason. "
            "`weak_context` covers a body/lead overlap, low confidence, contradictory bare readings "
            "or insufficient anchored support; it is deliberately conservative.",
            "",
            "```json",
            json.dumps(current["diagnostics"].get("texts", []), ensure_ascii=False, indent=2),
            "```",
            "",
            "## Final values and tracing baseline for WP-B",
            "",
            "|Revision|Part|Type|Printed name|Value|",
            "|---|---|---|---|---|",
        ]
        for revision, parts in [
            ("before", original["result"]["netlist"]["components"]),
            ("WP-A", current["components"]),
        ]:
            for c in parts:
                lines.append(
                    "|"
                    + "|".join(
                        compact(v)
                        for v in (
                            revision,
                            c["id"],
                            c["type"],
                            c.get("label"),
                            c["value"],
                        )
                    )
                    + "|"
                )
        lines += [
            "",
            f"WP-A graph: **{current['nodes']} nodes**; any computed nonzero current: "
            f"**{str(current['nonzero_current']).lower()}**. This is not a topology accuracy score.",
            "",
            "The OCR annotation shows components and text, not wire connectivity. WP-B adds "
            "wire overlays and records whether repairs improve the graph.",
            "",
        ]
        (out / f"case-{index + 1:03}.md").write_text("\n".join(lines), encoding="utf-8")


if __name__ == "__main__":
    main()
