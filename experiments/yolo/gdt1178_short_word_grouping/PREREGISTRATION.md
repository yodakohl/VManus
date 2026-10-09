# GDT1178 — source-spelling-independent short-word grouping

Exploratory construction test after1176/1177, before new measurements. All four
collections b4,w1,bs1,gr1 are known design data. No independent holdout claim.
The exact function-word lists failed; do not add spelling variants to them.

Two new fixed mechanisms L2/L3: every entirely alphabetic source token with
at most2 / at most3 Unicode codepoints binds to the next source token. All
consecutive eligible short tokens bind forward. A token with punctuation or
any nonletter closes its group. A final pending run closes at recipe end.
No language tags, part-of-speech decisions, exception list, deleted word,
reordered component or crossed recipe boundary. Each group is an exact tuple
and must expand to the original complete normalized source word sequence.

Use the already preserved GDT1177 source projection without changes. Retain
all complete recipes and their original uncertainty exclusions. For each of
both variants and all four sources use the same first8000-group convention
and inherited GDT1174 type-ratio and top10 tolerances0.05, each of3 readings.
A variant passes only every condition simultaneously. No redefinition of
success or source selection. If none passes, stop full writer implementation
on those fixed groupings. If one passes, build and test an actual glyph writer;
these two statistics alone do not constitute a working Voynich-compatible
system. No post-test length threshold or punctuation exception repair.

GDT910's native short/long recurrence failure stays closed; this is only a
forward artificial spelling rule, not a native abbreviation claim. Rule
simplicity does not establish medieval practice. Source words carry meaning
through ordinary language, not invented native assignments. No target text
or reserves accessed. Remaining portion of60-minute block beginning04:58 UTC.
