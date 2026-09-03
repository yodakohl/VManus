# GDT787 — `keedy` remainder cross-family transfer

Status: `WHOLE_ONLY__FORMAL_FAMILY_STRONG__SEMANTIC_REMAINDER_TRANSFER_FAILS`

GDT787 follows every admitted complete surface ending in `keedy`.  The corpus
contains 601 raw tokens in 38 written forms; 370 tokens in 27 forms survive as
exact complete words in all three current alternate readings.  Nine different
left contexts fill the complete `Xkey/Xkeey/Xkedy/Xkeedy` square, so the family
is formally real and not an accident of `qokeedy` frequency.

The semantic prediction nevertheless fails.  A target-masked, physical-folio-
balanced model predicts each held `Xkeedy` from its three sisters.  It beats
the standalone-X null in 5/9 rows, a form-selected learned-whole null in 4/9,
and both together in only 3/9.  Its macro score is essentially tied with the
learned-whole null.  Exact `X keedy` spans and the legacy Stolfi split support
occasional boundary alternation, but they do not rescue semantic equivalence.

Practical outcome:

- bare `keedy` remains the replaceable whole card **heißer Endzustand**;
- `okeedy` and `qokeedy` retain their own shortened HOT+END whole readings;
- no meaning is exported from `keedy` into arbitrary longer forms;
- automatic `CLOSED/abgeschlossen` is removed from the ordinary default;
- Holz/Wurzel/Samen/Saat and automatic q-imperatives are removed where they
  came from retired source composition;
- every one of the 38 observed forms receives a short concrete working
  display from one explicit C0 family prior, with the eleven non-exact forms
  visibly marked as reader warnings;
- these are display cards, not 38 independent semantic confirmations, and
  GDT787 grants zero new renderer licences.

Run:

```bash
python3 -B experiments/yolo/gdt787_keedy_remainder_cross_family_transfer/src/run.py
python3 -B experiments/yolo/gdt787_keedy_remainder_cross_family_transfer/src/validate.py
```

See `REPORT.md` for the result and `METHOD.md` for the exact comparison.
