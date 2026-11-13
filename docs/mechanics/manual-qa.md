# Mechanics manual QA

Automated results and exact counts are recorded in [status.md](status.md). This
checklist is for a person; screenshots and browser automation do not constitute
human language approval, novice testing or physical-device QA.

The reconstruction workflow has three modes. Explore contains physical selection,
initial-condition dragging and contextual parameters. Fix interpretation contains
OCR/unit/ownership, contact and endpoint repairs. Advanced authoring contains body
creation, source masks, drawing, stencils, calibration and geometry controls.

| Fixture/system             | Explore manipulation                            | Expected authoritative change                    |
| -------------------------- | ----------------------------------------------- | ------------------------------------------------ |
| Projectile ground/cliff    | Launch tip in two directions                    | Launch speed and angle; changed range/flight     |
| Incline                    | Block along slope                               | Bounded start position; source incline unchanged |
| Pendulum                   | Bob around pivot                                | Release angle; constant length                   |
| Horizontal/vertical spring | Body along its spring axis                      | Initial stretch; rest length unchanged           |
| Atwood                     | Either hanging body vertically                  | Shared displacement; opposite movement           |
| Table pulley               | Table body horizontally or hanger vertically    | Same shared rope displacement                    |
| Incline pulley             | Supported body along slope or hanger vertically | Coupled rope displacement                        |
| Collision                  | Either body horizontally                        | Its initial x; no overlap; changed contact time  |

For each, repeat at Fit and zoom 1.5 with a scrolled viewport. Pause/rewind occurs
on grab; release creates one Undo step. Escape/pointer cancellation restores the
whole transaction. Arrow keys provide the same bounded physical operation. Reset
rewinds playback without clearing edits; Back to original parameters clears
overrides. Restore first interpretation is a separate document-level operation.

Check Confirm this value changes only its provenance/value override and survives
project export/import. Correct an invalid mass and verify that valid simulation
unlocks without a new upload. Add/remove a missing body in Advanced authoring and
undo the transaction. Default masses, stiffness, rest length and damping introduced
by authoring must remain marked assumed until confirmed or entered.

1. Open Circuit, change a resistor, switch to Mechanics and back. The edited
   resistor/document must remain. Inactive circuit shortcuts/paste must stay off.
2. In Mechanics upload a real diagram and observe stages/partial boxes/text.
   Missing weights must give an explicit unsupported result and retain the image.
   Partial/unsupported results must open editing. Review an extracted result too.
   If needed, choose and place a template. Verify every assumption, delete absent
   objects, position native handles, set boxes/masks, attach ends, draw a missing
   line, and repair lines revealed under moving bodies.
3. Enter physical Values, assign unplaced chips and check confidence/status badges.
   Run. Compare the trajectory/regime/units and readouts to an independently worked
   physical solution. Check the original toggle and any composition warning.
4. Change each binding class. Physics/initial edits preserve the background;
   geometry requires unlocking and shows Modified. Lock and Back to original work.
   Undo/Redo restores edits once per drag, including after changing tabs/language.
5. Export JSON, reload/import it, compare scene/Values/image and replay. Import an
   invalid reference or wrong image dimension: validation must fail while keeping
   the current project. Export PNG and inspect its actual pixels.
6. Try incomplete/null Values, unknown types and Unsupported: source and editor
   remain, playback is unavailable, warnings distinguish schema validity from
   simulation support. No circuit demo may appear in Mechanics.
7. Test EN/BN and the digit toggle, including labels, badges, warnings, graphs and
   readouts. HUMAN Bengali review is pending. Technical ids/units and editable
   number fields retain machine-readable Latin spelling.
8. On a physical phone/tablet test 44px control targets, tab order/selection,
   pointer capture, scroll/zoom, keyboard arrows, clear focus and cancellation.
   Under reduced motion confirm no autoplay and readable static paths/vectors.
9. Cancel or switch domains during analysis, then edit or load a fixture. A late
   response must not replace it. Correction consent starts off; saving requires
   both checking the box and pressing Save correction. Verify only the native
   image/edited scene are saved locally as unreviewed data, and consent resets.

Public-source manual QA provenance is in [real-qa-sources.md](real-qa-sources.md).
No model inference, gold review or recognition score follows from these checks.
