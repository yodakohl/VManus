# GDT1176 — necessary source-word frequency gate

Before extracting or measuring the two collections,5 October2026. This tests
four fixed word partitions on natural complete source texts. No glyph key is
chosen here; every partition must be recoverable to the same ordered source
words. This is not yet an executable22-glyph writer or statistical full pass.

Use cached CoReMA recipe XMLs b4 and w1, hashes from GDT1159 SOURCE.json.
These are derived recipe editions, NOT the separate diplomatic TEI bodies
reviewed in COREMA_WRITTEN_DATA_CONTRACT.md. b4 is construction source; w1 is
fixed transfer. Both are previously exposed; not independent confirmation.
No substitute collections or sample expansion after seeing results.

For each recipe in document order, omit editorial note subtrees while retaining
tails; otherwise flatten text in document order. Empty lb/pb elements do not
create new characters. NFC and lower case; collapse whitespace only. Retain
punctuation and non-ASCII characters as part of source tokens; do not silently
strip them. Retain the whole extracted recipe and the original file hash.
Exclude a complete recipe if it contains gap/unclear/supplied nodes, visible
square brackets, ellipsis, or three consecutive dots; publish its identifier,
reason and length. No partial-word salvage. Keep recipes in original order.
Words are the declared editorial whitespace tokens, not manuscript facts.

Four fixed partitions, no code or predicate assignments:
P0: each source word one written group.
P1: consecutive exact words from CONJ set bind to the next source word.
P2: consecutive exact words from CONJ+ARTICLE sets bind to the next word.
P3: consecutive exact words from CONJ+ARTICLE+LINK sets bind to the next word.
Every nonlisted source word closes a group, including attached punctuation.
A pending sequence at recipe end is one group. Never cross recipe boundaries.
No sorting or omission. Group identity is the complete ordered tuple. Lists
are deliberately finite exact spellings; unfamiliar variants are ordinary words.
The sets are in src/SPEC.json and are locked before measuring.

Use the first8000 groups of each source/partition in document order, exactly
the inherited GDT1174 comparison size. No drawing, replacement or repetition
of short corpora. A last recipe may be truncated only for the descriptive
statistic; the full projected source and full partition remain the coverage
and reverse-reading objects. Insufficient groups is missing capacity, not pass.

Reuse the already computed GDT1174 target summaries, separately for ZL/IT/RF;
no transcription input or new manuscript access. Necessary gate only:
Top10 fraction within0.05 absolute and type fraction within0.05 absolute of
EACH reader, BOTH collections. These are the unchanged two inherited tolerances,
not newly natural constants. No sign alphabet can alter these tuple counts
under a bijective spelling of groups.

Passing permits constructing a fully specified meaningful writing rule with
explicit source-independent learning costs; remaining eight tests and stronger
structural baseline stay untested. Failure stops full glyph-code implementation
for that fixed source/partition combination. Do not select a best partial score
as a successful writer. No root replacement of1175, no target word codebook.

Wall-time budget:60 minutes including preparation, execution, validation and
local checkpoint, starting04:58 UTC in the existing decision note. One question.
