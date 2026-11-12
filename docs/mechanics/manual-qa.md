# Mechanics manual QA

Automated results and exact counts are recorded in [status.md](status.md). This
checklist is for a person; screenshots and browser automation do not constitute
human language approval, novice testing or physical-device QA.

1. Open Circuit, change a resistor, switch to Mechanics and back. The edited
   resistor/document must remain. Inactive circuit shortcuts/paste must stay off.
2. In Mechanics upload a real diagram, choose and place a template. Verify every
   assumption, delete absent objects, position native handles, set boxes/masks,
   attach ends, draw a missing line, and repair lines revealed under moving bodies.
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

Public-source manual QA provenance is in [real-qa-sources.md](real-qa-sources.md).
No model inference, gold review or recognition score follows from these checks.
