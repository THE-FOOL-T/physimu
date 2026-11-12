"""Public association API; implementation records every assignment decision."""

from .label_assignment import associate as _associate, center, search_windows


class AssociationResult(list):
    def __init__(self, warnings=None, matched=None, unmatched=None):
        super().__init__(warnings or [])
        self.matched = matched if matched is not None else []
        self.unmatched = unmatched if unmatched is not None else []

    def __getitem__(self, item):
        if item == "matched":
            return self.matched
        if item == "unmatched":
            return self.unmatched
        if item == "warnings":
            return list(self)
        return super().__getitem__(item)

    def get(self, key, default=None):
        if key == "matched":
            return self.matched
        if key == "unmatched":
            return self.unmatched
        if key == "warnings":
            return list(self)
        return default


def associate(components, texts, weight=1.0):
    warnings = _associate(components, texts, weight=weight)
    matched = []
    unmatched = []
    for item in texts:
        if item.get("outcome") == "assigned" and item.get("assigned_to"):
            assoc = item.get("association") or {
                "component_id": item["assigned_to"],
                "role": item.get("role", "value"),
                "parsed": item.get("parsed"),
            }
            assoc["text"] = item.get("text")
            item["association"] = assoc
            matched.append(assoc)
        else:
            unmatched.append(
                {
                    "item": item,
                    "text": item.get("text"),
                    "reason": item.get("reason", "unassigned"),
                    "role": item.get("role", "unknown"),
                }
            )
    return AssociationResult(warnings, matched=matched, unmatched=unmatched)
