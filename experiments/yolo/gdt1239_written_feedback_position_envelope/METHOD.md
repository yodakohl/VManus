# GDT1239 — position-aware necessary source envelope

Retain GDT1238's fixed injective row family: one source letter emits one
working sign; the previous emitted sign alone chooses the next row. An output
run g^k starting at zero-based a forces the source substring [a+1:a+k] to
contain one repeated source letter. Word length is preserved. The substring
may be part of a longer source run. No maximal-run equality is required.

For each saved native run of length at least three, ask if ANY word of the
entire fixed Deot projection has the same length and a constant substring in
those positions. Examine logical and fully reversed source words separately.
Allow a different source word for each target run and arbitrary entering
state. Even multiple runs in one target word may have different carriers.
This is deliberately only a necessary envelope, not a consistent alignment,
common table, complete word analysis, frequency comparison or decoding.

One missing carrier disproves coverage of that target word by this source
under this fixed family/orientation. An entirely nonempty envelope is
inconclusive. Distinguish no source word of that length from same-length
words that lack the required repetition. Do not repair or remove rare forms.
No claim about another source text, source language or different writing rule.

The runner indexes all constant source substrings; a separate validator scans
every same-length source word directly for each target run. The fixed 1238
input/validation hashes and complete native provenance are retained.
