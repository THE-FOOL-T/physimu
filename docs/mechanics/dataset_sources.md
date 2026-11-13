# Mechanics data and checkpoint sources

No public training dataset was downloaded or imported in M4. No source or dataset
licence has been approved for the owner. Public datasets remain optional; before
use, HUMAN records their source/version, terms/attribution decision, exact export
hashes and explicit class map (unsupported classes are dropped, never guessed).

| Source | Use and evidence | Owner decision |
| --- | --- | --- |
| Local M2 scene primitives and M4 seeded drawing code | 600 synthetic R1 images, with exact programmatic boxes/masks and augmentation metadata. Source notice explicitly says synthetic, not a real benchmark. No external image dataset is incorporated. | Decide distribution/licensing for generated training material; no real gold approval is implied. |
| Existing local `yolo26n.pt` general checkpoint | Copied to ignored `models/yolo26n.pt`; SHA-256 `9b09cc8bf347f0fc8a5f7657480587f25db09b34bf33b0652110fb03a8ad4fef`. The loaded model reports 80 general classes. Both first-round smoke arms initialize here. Never initialized from circuit v2. Original upstream artifact authenticity was not independently re-established. | Review the applicable code/checkpoint terms before distribution, full training or production decisions. |
| Local Pillow bundled font and repository Noto Sans Bengali | Used to rasterize synthetic labels; no font files downloaded or added to generated datasets. Local Arial, or a local Noto compatibility alias, satisfies the training SDK's font-cache check without a download. | Existing font notices apply; review redistribution terms as needed. |
| M3 public pendulum QA download | Provenance/stated rights in [real-qa-sources.md](real-qa-sources.md). Used only for manual M3 QA and unreviewed M4 prelabel plumbing, not R1 training, reviewed real quotas or gold. | HUMAN must decide any later dataset use and independently review annotations. |
| Public starter pack requested during M4 | [public-candidates.md](public-candidates.md) records seven local PNGs, original/rendered hashes, author credit, stated rights, one quarantined inconsistent diagram and one reused M3 QA image. Five fresh candidates and seven null-scene scaffolds remain ignored. No training/gold import. | Independently author/review suitable scenes, decide source terms and preserve source groups. No verified real handwritten collection yet. |
| Frozen real evaluation and real training pool | Empty except HUMAN-task READMEs. No real label, gold scene or review was supplied by Codex. | HUMAN supplies sources/licences, source-separated reviewed images/labels and frozen gold. |

Ultralytics' [official licence page](https://www.ultralytics.com/license) describes
AGPL-3.0 and Enterprise options for its software/models. The repository already
contains the Ultralytics licence notice. This records the vendor's stated terms;
it does not select a licence or approve the owner's intended use. No model or
dataset licence is inferred from the fact that a file can be downloaded.

All weights, generated images/labels/scenes/masks, reviewed real data and frozen
gold stay outside Git. Only class schema, tools and documentation are tracked.
Training outputs must be new, explicitly absolute, within the current checkout;
runtime analysis does not download models. The mechanics model config remains
independent from circuit configuration and the smoke model is not installed as
the production mechanics detector.
