# GDT094 — nested unseen-tail and unseen-folio operator transfer

Reuse the 42 state-blind `o+TAIL/y+TAIL` pairs from GDT087.  For every scored
occurrence, remove from training both its complete physical folio and every
occurrence of its exact TAIL.  Predict q and d presence from register only,
then add one feature at a time: PAGE_HOST base O/Y, last tail character,
length, or last-character×length.  Use shrinkage `{1,4,16,64,256}` and pay the
five-way selector separately for each feature/outcome.

The formal O/Y factor is explicitly identical to a first-character source
string baseline.  Transfer can establish a reusable construction rule, but
cannot by itself establish morphology beyond string statistics.  f84r is
absent upstream.
