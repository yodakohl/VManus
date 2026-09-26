# Independent replay review (B)

I reconstructed the expected tables directly from the frozen GDT1042
`guarded_projection.tsv`, GDT1045 `SPEC.json`/`PREREG_LOCK.json`, and the
hash-bound 24-value exploratory S dictionary. I did not import or read
`src/run.py`. The new `src/validate.py` verifies the frozen input hashes and
independently regenerates the all-row context table, raw qod-initial selection,
two conditional type outcomes, S.16 token availability, block-level
unassigned-context lists, and compact tallies.

Replay passed: 473 projection rows, all 24 baseline forms, 10 literal
qod-initial occurrences (qodaiin 5, qodain 3, qodar 2), and 20 candidate rows
match exactly. All 473 full source groups, including literal separators and
alternate-reader spellings, are retained in `CONTEXTS.tsv`. The five required
S.16 forms are present in the three reader rows for that locus. The validator
also reproduces every complete spatial-block context and its unassigned-form
list; this exposes how much of the N/E/W context remains outside the S draft.

Under the frozen conditional type table, Q_RECIPIENT yields 5 typed,
3 type-error, and 2 unbound outcomes; Q_LOC_OWNER yields 5 typed,
3 typed-with-loc-owner, and 2 unbound outcomes. Only the exact S.16 frame
receives an authored goal-agreement result (2 rows for Q_RECIPIENT, 3 for
Q_LOC_OWNER). Typed occurrences in W receive no licensed transfer frame.
The Q_LOC_OWNER outcomes therefore depend on its explicit extra
`owner(AT(r))=r` representation; the table does not establish that
representation independently. More specifically, this composition derives an
ATTRACT prediction for previously unassigned `qodain` under Q_LOC_OWNER. That is
a new whole-form prediction, even though it reuses the `ATTRACT` predicate
already assigned to `qodaiin`; `new_whole_senses=0` refers only to zero new
atomic dictionary entries/sense values, not zero newly derived predictions.

This validates deterministic application of the preregistered conditional
type/reference-availability rules. It is not independent meaning confirmation,
a productive-prefix result, confirmation of a reading, or a semantic grammar
rejection. The five S.16 forms establish presence in the fixed authored frame;
their presence does not independently establish syntax. In particular,
`qodar` has an unassigned suffix (`ar`) and remains
unbound; its omission from typed outputs is not negative evidence against a
meaning. Nor do the alternative transcriptions count as independent witnesses.
