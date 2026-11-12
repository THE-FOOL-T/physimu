# Ten-minute owner QA (round three)

Use an owner diagram whose values and wires you can read, with the v2 weights
installed and the optional AI reader left off. The exact 3.0 V picture is not
required: the owner approved other failing examples. Case 002 is the recorded
24 V / six-resistor example; its 8 kOhm R5 label still needs manual entry.
This checklist is a procedure, not a record of human approval.

1. **Start (1 minute).** Run `python manage.py serve`, open localhost:8000, and
   watch the model chip. It must remain warming while either detector or OCR
   is warming. Missing weights/text reader must be explicit. Cold readiness
   measured locally is in startup-round3.json; a different machine may differ.
2. **Upload and Fit (1 minute).** Drop/paste the owner diagram. Check the immediate
   receipt, readable filename, stage progress and complete paper at Fit. After
   analysis Import should collapse. Open Show original to distinguish a cropped
   original from a view problem. On a phone, use pinch, Pan and Fit.
3. **Check values and evidence (1 minute).** Open Show text found. Hover a label
   and inspect its raw text, parse and assignment reason. If the drawing says
   3.0 V, confirm V1 is Given 3.0 V; for the recorded 24 V case confirm 24 V.
   Compare every visible resistor label. Missing labels must say value not found;
   a bare E must never name a resistor. Click an OCR box to assign or ignore it.
   Draw Read this area around one label; choose/type its actual value.
4. **Read the checklist (1 minute).** Enter Fix circuit. The Editing / not simulated
   banner must stay visible and animation freeze. Read the short Parts / Wires /
   Values assistant and the grouped checklist. Technical warnings stay collapsed.
   A partial extraction must remain clearly partial, with all found parts visible.
5. **Repair a loose wire (1 minute).** Click Fix beside a loose end. Click the two
   real endpoints, adding a bend if needed; Enter finishes the wire. The pre-check
   should change as the connection closes. Undo/Redo must reverse and restore it.
   Readouts remain frozen until Run, unless you explicitly enable auto-run.
6. **Add a missed part (1 minute).** Choose Add part and its type; draw a rectangle
   over the missed symbol. Enter its visible value (use 220 only for a 220-ohm
   practice part). Check snapped ends, type and polarity. Run, or Ctrl+Enter,
   should simulate the edited circuit; a failing Run should keep the draft.
   Compare with automatic result, then return to the edited circuit.
7. **Explore parameters (1 minute).** Check nonzero current on the repaired closed
   loop. Change a slider on the right, then the pinned source slider on top.
   Readouts and speeds should respond. Click a part to use its value slider;
   toggle a switch at its symbol. In a draft these changes wait for Run.
8. **Inspect flow and Explain (1 minute).** Try Dots, Dashes, Arrows and Glow,
   color and size. Amber/yellow must stand out in light/dark themes. Zero voltage
   should give no-current text and grey dashes; reduced motion uses static arrows.
   Check Explain formulas/statuses and a distinct magenta short demonstration.
9. **Bangla and touch (1 minute).** Switch language and Bangla digits. Check tool
   hints, notices, popovers and wrapped controls at 390px. The wide circuit needs
   zoom for small printing. Human electrical terminology review is still needed.
10. **Export and privacy (1 minute).** Export PNG and inspect the downloaded image.
    Download/reopen the netlist: image and user values must survive. Cancel/retry
    an upload and confirm the prior circuit remains usable. Corrections persist
    only after explicit Save corrections opt-in. AI reading is separate opt-in
    and sends label crops only. Leave it off for this test.

Record device/browser, diagram, language, each failed step and reproduction
steps. Automated mouse/touch checks establish regression behavior; they do not
establish novice-student usability, correct OCR/topology, or human Bangla review.
