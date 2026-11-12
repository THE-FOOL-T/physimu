# Frozen real mechanics — awaiting HUMAN gold

This tree contains no gold scenes or images. A person supplies at least 20
printed and 20 handwritten diagrams, with three or more per archetype where
possible, separated by book/page/drafter source groups. No automatic output or
Codex-authored QA example is ground truth. Dataset/source licences are HUMAN
decisions. See docs/mechanics/labeling.md and the M3 authoring guide.

Each style contains `<id>.gold.json` and its relative `images/<id>.png` source.
The envelope records source image SHA-256, source group/reference/licence note,
canonical manually authored scene and explicit dated human review. Optional
reviewed detector labels may be recorded with their own SHA-256. The freeze
tool records hashes only; it never writes/edits scenes. Frozen data must never
enter train/validation, threshold tuning or prelabel promotion. These private
files and frozen.json are ignored by Git. Real metrics remain null while absent.
