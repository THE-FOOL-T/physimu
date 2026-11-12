# M2 authored synthetic fixtures

These ten diagrams are deterministic printed examples, authored together with
their scene graphs. They are **synthetic, not real accuracy data**, not a frozen
gold set, and not detector training/validation output. No perception generated
their geometry, masks, repairs or physical inputs. The source labels say so.

Rebuild from the repository root:

```powershell
.\.venv\Scripts\python.exe -m backend.tools.mechanics.build_fixtures
```

The generator also writes the canonical serialization schema. The painter can
render one JSON with `python -m backend.tools.mechanics.paint_scene input.json
output.png`. Pillow's bundled default font needs no system font or download.
Byte reproduction is tested on the recorded Windows/Pillow environment; other
Pillow versions/platforms have not been measured.

Ground/cliff projectile and horizontal/vertical spring variants make ten scenes
covering all eight archetypes. The rod pendulum does not test slack-string
dynamics. Collision's optional after-panel constraint is exercised by solver
tests. The fixtures exercise masks, static line repairs, source labels, rope
arcs, springs, bodies, hatching and explicit parameter bindings.
