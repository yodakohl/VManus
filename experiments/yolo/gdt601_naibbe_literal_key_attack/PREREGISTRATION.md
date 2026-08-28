# GDT601 executable decision contract

Before target scoring, the executable fixes:

- normal glyph and token orientation;
- literal unigram or prefix+suffix table readings only;
- concatenation across visible parsed-token gaps and reset at unknown tokens;
- fourth-order Latin and Italian character models;
- 32 deterministic within-parsed-run shuffles;
- positive-control requirement `Latin z >= 8`;
- rejection requirement `Voynich Latin z <= 0` and `Voynich Italian z <= 0`.

The positive control, not the Voynich target, defines whether the attack can
detect the mechanism it claims to test. No best-looking line can override the
corpus-wide decision.
