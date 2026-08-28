# GDT611 — lexical-slot permutation audit

Status: `NO_STABLE_LEXICAL_OR_FAMILY_SLOT__FORMAL_FRAME_RELATIONS_ONLY`

This experiment tries to attach 17 concrete recipe/medical words to the
published GDT605 units using GDT608 composition roles, exact local substitution
frames, section profiles, train-folio restarts, and 23 held physical folios.
None of the 17 word assignments or four semantic families survives. The run
does preserve three useful formal paradigms, especially
`ok+eol ↔ qok+eol` in the exact `*+eol` frame.

The complete outcome is in `REPORT.md`; `HELD_PARAGRAPH.md` prints the strongest
full held paragraph and exposes why a dense-looking default gloss is not yet a
translation.

Reproduce from the repository root:

```sh
python3 experiments/yolo/gdt611_lexical_slot_permutation_audit/src/run.py
```
