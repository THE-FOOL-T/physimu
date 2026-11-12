# V2 original — preserved local checkpoint

Source: `D:/AugmentedPhysics/runs/augmented_physics/circuits_real_v2_20261031/weights/last.pt`

SHA-256: `95bc8a1f76aaed83ad907e87bdee0255da1837fdb8f9c8405a723779e8ed0c46`

`v2_original.pt` is an unchanged copy, now versioned with Git LFS for the owner's
requested portable distribution. Architecture is an
Ultralytics DetectionModel, YOLO26 family; detection task, four classes recorded
in `docs/recon.json`, original training input 960. CPU inference here uses 640.

Training history comes from the original handoff: synthetic training followed
by real-diagram fine-tuning that included the original 59 textbook diagrams.
They are seen regression data. Fresh measured results are in
`docs/baseline_v2.md`; they are not independent accuracy estimates.

No new trained candidate is claimed. `backend/tools/train.py` implements a
paired v2 fine-tune and standard pretrained control after reviewed licensed
data and independent frozen evaluation sets exist. Select by per-class recall
on those held-out sets, printed and handwritten separately.

License: review Ultralytics AGPL-3.0 / Enterprise terms before hosting or sharing.
