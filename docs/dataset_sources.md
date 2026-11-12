# Public-source preparation (2026-11-08)

No owner upload was sent to a service. Only public metadata/archive retrieval was
used. License records were written under ignored `data/raw/<name>/SOURCE.md`
before retrieving assets. Those records are evidence checks, **not fabricated
owner approvals**. Maps are committed under `data/maps`.

|Source|Primary license evidence|Local result|
|---|---|---|
|[AITEE](https://github.com/CKnievel/aitee-dataset)|[Apache-2.0 LICENSE](https://raw.githubusercontent.com/CKnievel/aitee-dataset/main/LICENSE)|32,763,230-byte archive; 828 flat images remapped. Archive SHA-256 e243ce75d0bb77e77fb2b2504d2e59b1a6cf881976463818a237458247301812. P/V semantics need review; dropped rather than guessed.|
|[JonathanApps Circuit Component Detection](https://universe.roboflow.com/jonathanapps/circuit-component-detection)|Project lists CC BY 4.0|Map prepared; authenticated/versioned export unavailable. HUMAN: provide export and retain its license/attribution.|
|[v3qwe](https://universe.roboflow.com/project-gtqqq/v3qwe)|Project lists CC BY 4.0|This is the 12-class source cited as reference 28 in the [Masala-CHAI paper](https://arxiv.org/html/2411.14299v2). Map prepared; export unavailable. BJT/MOSFET are unsupported and explicitly dropped.|
|[CGHD](https://github.com/DFKI/cghd)|[CC0-1.0 LICENSE](https://raw.githubusercontent.com/DFKI/cghd/main/LICENSE)|Map prepared. The current main-branch tree exposes README/license/classes, with no image/XML assets. HUMAN: provide the corresponding published release. Keep drafter/circuit photo groups together.|

The AITEE archive includes its own split; flat images/labels were remapped and
content-grouped again for this task. The 828 count is the measured flat asset
count, not an invented match to a number in its README. All 828 v2 pseudo-label
proposals are marked **human_reviewed:false**, stored locally and excluded from
the training mix pending review. A remap does not establish label completeness.

`kinds.json` explicitly marks known real images. Unclassified public/original
material is conservatively counted as synthetic for the 50% cap. Only the 59
owner seen textbook images, identified by exact content hash, are currently
marked real; real training entries are oversampled. This does not turn them
into held-out accuracy data.

Full training remains gated on human label-completeness review in the merge
manifest. Do not set `human_completeness_review` until an actual review is done.
The short smoke path is explicitly exempt for plumbing checks and cannot qualify
a model for release. Frozen-test byte hashes are committed in `data/eval/frozen99.json`.
