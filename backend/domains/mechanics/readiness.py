"""Structural validity, supported physics and evidence completeness are distinct."""

from .validate import violations


MESSAGES = {
    "weights_unavailable": (
        "Install a compatible local 21-class mechanics checkpoint, or use Advanced authoring.",
        "supply_model",
    ),
    "attachment_unreached": (
        "A measured link endpoint does not reach its object. Reconnect the endpoint in Fix interpretation.",
        "reconnect",
    ),
    "attachment_invalid": (
        "A link has incompatible endpoints. Select the link and correct its connections.",
        "reconnect",
    ),
    "rope_route_assumed": (
        "The rope wrap is inferred. Check both endpoints and the pulley route.",
        "review_rope",
    ),
    "multiple_figures": (
        "Several figure regions were found. Choose the intended panel before interpreting the scene.",
        "choose_figure",
    ),
    "invalid_mass": ("Enter a positive mass for this body.", "edit_parameter"),
    "ambiguous_interpretation": (
        "Several physical interpretations remain plausible. Review contacts and connections.",
        "choose_interpretation",
    ),
    "detector_failed": (
        "Local object detection failed. The original image is retained for manual authoring.",
        "author_scene",
    ),
    "ocr_failed": (
        "Local OCR failed. Enter the missing physical values and units.",
        "edit_parameter",
    ),
}


def assess(scene, evidence):
    errors = violations(scene)
    issues = []
    blocking = {code for code, _ in errors}
    for w in scene["warnings"]:
        code = w["code"]
        message, action = MESSAGES.get(
            code, ("Review this retained observation in Fix interpretation.", "review")
        )
        issues.append(
            dict(
                code=code,
                ref=w.get("ref"),
                path=None,
                severity="error"
                if code in blocking or code == "weights_unavailable"
                else "warning",
                message=message,
                action=action,
            )
        )
    for row in evidence.unassigned_labels:
        issues.append(
            dict(
                code="unassigned_label",
                ref=row.get("ref"),
                path=row.get("unplaced_path"),
                severity="warning",
                message=f"Assign the label {row['text']!r} to a physical quantity, including its unit.",
                action="assign_label",
            )
        )
    for row in evidence.assumptions:
        if row["path"] in {b["path"] for b in scene["bindings"]} or row["path"] == "frame.px_per_m":
            issues.append(
                dict(
                    code="assumed_parameter",
                    ref=None,
                    path=row["path"],
                    severity="warning",
                    message=f"{row['path']} is assumed; confirm its value and unit.",
                    action="confirm_parameter",
                )
            )
    status = "ready"
    if any(w["code"] == "weights_unavailable" for w in scene["warnings"]):
        status = "needs_model"
    elif scene["archetype"] == "unsupported" or scene["meta"]["provenance"] == "unsupported":
        status = "unsupported"
    elif issues:
        status = "needs_review"
    return dict(
        status=status,
        structurally_valid=True,
        physics_supported=scene["archetype"] != "unsupported" and not errors,
        issues=issues,
    )
