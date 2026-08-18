# GDT329 — formula-position specificity audit

GDT329 tests the strongest post-hoc GDT328 observation under a search-aware
null: does any recurrent field formula occupy a more stable field ordinal than
expected after preserving register, field length, formula recurrence, and the
complete empirical field-position distribution?

The candidate family is exactly the 44 GDT328 formulas (15 exact joint-tuple
sequences and 29 PAGE_HOST sequences).  For each candidate, every pair of its
occurrences contributes one when the field ordinals agree.  The statistic is
the excess number of agreeing pairs over its register×field-length expectation,
divided by the square root of the summed Bernoulli variances.  This standardized
score is only a ranking statistic; inference comes from permutation.

In each of 8,192 deterministic worlds, field ordinals are permuted among all
fields with the same group length and register.  Formula labels, occurrence
counts, physical folios, registers, field lengths, and the complete ordinal
histograms remain fixed.  Local inclusive p-values use the candidate's own
null.  The primary p-value maximizes the statistic over all 44 candidates in
every world.

This audit was designed after seeing the GDT328 lead.  It can correct its
look-elsewhere interpretation but cannot make the lead prospective.

No semantics, word boundaries, language, plaintext, translation, or f84 data
are used.
