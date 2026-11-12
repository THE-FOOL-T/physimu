# Owner-reviewed labeling and frozen evaluation

Create `data/eval/printed/{images,labels,netlists}` and the corresponding
`handwritten` tree. Supply 30–50 independently sourced images per split,
including phone photos and Bangla labels. The existing 59 textbook images are
v2 TRAINING data. The additional 99-image collection has documented user-reviewed
CVAT labels and zero exact matches to 695 recorded prior image hashes. It still
needs source/near-duplicate review, style partitioning and gold netlists for the
requested printed/handwritten electrical benchmark. Existing reviewed boxes can
be reused without inventing new approval; do not re-label them unnecessarily.

Prelabel into a fresh directory (from the workspace parent):

```powershell
python -m circuit_sim.backend.tools.prelabel <images> --out circuit_sim/data/prelabels
```

Import the images and YOLO proposals into Label Studio, Roboflow, or labelImg.
Keep class IDs from `data/class_schema.yaml`, check every missing symbol, polarity
mark, arrow, junction, meter and text region, then export YOLO boxes. Proposals
are unreviewed; `manifest.json` includes a seeded review sample. Do not use its
sample review as a substitute for reviewing the entire frozen test set.

Author gold `netlists/<image-stem>.json` with exact node membership and the wire
graph, preferably through the editor with an independent electrical check.
Mark the values actually printed as given; do not use the automatic result as
ground truth without review. Declare ground, polarity, switch state and initial
conditions. Human annotation and synthetic ground truth are separate sources.

Freeze source hashes and book/page or drafter identities. Split by source page
and drafter, not random screenshots of the same circuit. `merge_dataset` checks
content hashes against all frozen eval images; additionally check near-duplicates
and conceptual overlap yourself. Never train on frozen eval images.

Dataset candidates, searched but not downloaded or approved:

- [AITEE, publisher repository](https://github.com/CKnievel/aitee-dataset):
  educational diagrams, YOLO format; inspect taxonomy and license with the owner.
- [DFKI CGHD, publisher repository](https://github.com/DFKI/cghd): photographed
  hand-drawn diagrams, VOC boxes, segmentation and some netlists.
- [Digitize-HCD, publisher dataset](https://data.mendeley.com/datasets/rngcz5wtv8/2):
  handwritten circuits; verify release terms and annotation compatibility.
- [JUHCCR paper](https://pmc.ncbi.nlm.nih.gov/articles/PMC12586450/): hand-drawn
  component crops; crops alone do not establish full-diagram wire connectivity.
- [Masala-CHAI publisher code](https://github.com/jitendra-bhandari/Masala-CHAI):
  inspect the underlying detection dataset's terms separately from the code.

For each chosen import, create `data/raw/<name>/SOURCE.md` recording source URL,
version, exact license, download date, ownership/attribution requirements and the
owner's verification. No license approval or dataset labels were fabricated.
