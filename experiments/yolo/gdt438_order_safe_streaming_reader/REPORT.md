# GDT438 — the prospective reader is now order-safe

## Result

GDT437's repair is now in the actual left-to-right command. The reader still
uses only the visible page, register, owner and ordered component recipe. It
does not accept an event ID or precomputed inherited-state field.

The complete replay gives:

- 4,576/4,576 state transitions identical to GDT436;
- 4,576/4,576 clauses identical to the GDT437 repaired edition;
- exactly 68 reordered event clauses in 59 of 715 statements;
- 245/245 future-card probes matching GDT437;
- both stop types leaving action and argument unchanged.

## What is different in use

After `OK+Y` establishes the active action and post, the two formerly
colliding cards now read differently in every register. In the celestial
register:

- `AIR+Y`: “Entlang der Ringbahn: im laufenden Gang setze den
  Positionsposten.”
- `Y+AIR`: “Im laufenden Gang setze den Positionsposten; entlang der
  Ringbahn.”

The same code produces Verarbeitung-, Stations-, Transfer- and Lesebahn in the
other registers. The state before and after both cards is unchanged; only the
licensed written order survives.

An unseen atom and a known-atom recipe absent from the 1,563-key catalog both
stop before state mutation. A following valid card therefore resumes from the
same action and argument.

All 29 validation checks pass, including a byte-identical rebuild. No meaning,
surface or page was added. The reader is ready for the next step: subject the
entire 1,563-card catalog—not only the main 49—to the same transition-signature
audit.
