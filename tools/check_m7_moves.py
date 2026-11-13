"""Verify the recorded M7 moves without importing models or application code."""

import ast
import hashlib
import json
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]


def digest(data):
    return hashlib.sha256(data.encode("utf-8")).hexdigest()


class Structure(ast.NodeTransformer):
    def visit_Import(self, node):
        return None

    def visit_ImportFrom(self, node):
        return None

    def visit_Subscript(self, node):
        self.generic_visit(node)
        # Moving a file changes only the depth needed to reach the same assets.
        if ast.unparse(node.value) == "Path(__file__).resolve().parents":
            node.slice = ast.Constant(value="repository-relative-depth")
        return node


def fingerprint(text, suffix, extracted=()):
    if suffix == ".py":
        tree = ast.parse(text)
        tree.body = [
            node
            for node in tree.body
            if not isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))
            or node.name not in extracted
        ]
        return digest(ast.dump(Structure().visit(tree), include_attributes=False))
    if suffix == ".ts":
        # Import/export module specifiers change, but bindings and code do not.
        text = re.sub(
            r"\b(from\s+|import\s+)([\"'])([^\"']+)\2",
            lambda m: m[1] + '"<module>"',
            text,
        )
        tokens = re.findall(
            r"'(?:\\.|[^'\\])*'|\"(?:\\.|[^\"\\])*\"|`(?:\\.|[^`\\])*`"
            r"|//[^\n]*|/\*[\s\S]*?\*/|[\w$]+|[^\s]",
            text,
        )
        tokens = [t for t in tokens if not t.startswith(("//", "/*"))]
        # Prettier wraps longer imports and inserts optional trailing commas.
        return digest(
            "\n".join(
                token
                for index, token in enumerate(tokens)
                if not (
                    token == ","
                    and index + 1 < len(tokens)
                    and tokens[index + 1] in ("}", "]", ")")
                )
            )
        )
    return digest(text.replace("\r\n", "\n"))


def verify_moves(root=ROOT):
    manifest = json.loads((root / "docs/mechanics/m7-moves.json").read_text(encoding="utf-8"))
    result = {}
    for row in manifest["moves"] + manifest.get("rewrites", []):
        target = root / row["to"]
        text = target.read_text(encoding="utf-8")
        assert (
            fingerprint(text, target.suffix, row.get("extracted", ())) == row["structure_sha256"]
        ), (
            row["from"],
            row["to"],
        )
        if "resource_roots" in row:
            for expression, expected in row["resource_roots"].items():
                assert expression in text, (target, expression)
                depth = int(re.search(r"parents\[(\d+)\]", expression)[1])
                assert target.resolve().parents[depth] == (root / expected).resolve(), target
        result[row["from"]] = target
    for row in manifest["extractions"]:
        tree = ast.parse((root / row["to"]).read_text(encoding="utf-8"))
        node = next(
            n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name == row["name"]
        )
        assert digest(ast.dump(node, include_attributes=False)) == row["structure_sha256"], row
    return result


if __name__ == "__main__":
    checked = verify_moves()
    print(f"Verified {len(checked)} moved/updated implementation paths and extracted helper bodies")
