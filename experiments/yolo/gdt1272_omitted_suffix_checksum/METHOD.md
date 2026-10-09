# GDT1272 — fixed omitted-suffix checksum with a paid literal escape

## Decision note before execution
Positive: RAW978 carries information about omitted source letters, unlike IP014's
already contradicted checksum of the visible prefix. Its collision XXCA/XXAB
(A=1,B=2,C=3) remains.934 requires a paid grammar/interface;1202/1226 exclude
canonical whole-word repairs on their four fixed recipe profiles.1229 shows
that the unchanged full bare Deot projection is NOT excluded by both word-frequency
gates alone; its own branch-rank rule failed glyph entropies. We do not rerun it.
1183's fragment/initial-bank writer and subsequent failures are different and remain.

Unknown: does one complete fixed checksum/escape carrier shorten this source
once every marker is counted, and survive the six old bijection-invariant gates?
Failure stops this fixed source/rule, with no modulus, alphabet, source or carrier
repair. A survivor is only a coarse candidate: no glyph mapping, q/y, word-building,
line layout, historical usability or meaning claim. Missing capacity stays untested.
Smallest test: one entire source, one wordbook, one rule, all old cached equal-N
samples; no target access, parameter optimization or source truncation. Budget
22:51–23:16 UTC includes preparation, implementation, validation and local closure.
The starting minute is a conservative allocation, not a precise measured start.

## Fixed source and alphabet
Use GDT1228 SOURCE_PROJECTION.json unchanged: all71 sections,6288 words. This is
an already exposed lossy modern digital projection, not identified Voynich content.
Alphabet in logical order: אבגדהוזחטיכלמנסעפצקרשת. Source ranks are1..22.
The wordbook L is exactly every distinct complete word in that projection.
It is learned from the entire source and must be retained/charged: entry count,
total stored source letters and indexed buckets. It is not a free independent key.
No additions, pruning, frequency reordering or dictionary selected per passage.

## Complete group carrier
Use22 abstract output labels numbered0..21. Each stands for one working sign under
an UNSELECTED fixed bijection; none is assigned to a real native glyph or meaning.
Visible spaces delimit whole groups. Each source word emits one group; sections
are preserved. This tests the word channel, not a realistic native line layout.

Label21 is the literal escape, chosen as the last label by convention, not fitted.
Literal group: [21] followed by each source letter's zero-based index. Its cost is
n+1. Literal groups can contain21 inside the payload without ambiguity.

For n>=4, split word into first two letters P and suffix R. Compute
H(R)=sum((i+1)*rank(R[i])) mod19. Short group is exactly four labels:
[P[0] index, P[1] index, len(R), H(R)]. It is allowed iff:
- the first source-letter index is not21 (keeps modes disjoint);
- len(R)<=21 (one label for length);
- L contains exactly one word with that prefix, omitted length and checksum.
All other words, including out-of-book words, use literal mode. n>=4 guarantees
four labels are shorter than the n+1 literal option. The comparison to original
n-letter spelling remains separate: at n=4 no raw-letter saving occurs.

Decoder: first label21 means literal; otherwise require exactly4 labels and a
unique matching entry in L. Invalid or ambiguous codes reject. No invisible mode,
null, semantic guess or second encoding choice. Canonical re-encoding is checked.
An adversarial finite wordbook includes XXCA and XXAB to test both literal fallbacks.
A fixed word-local lossless code preserves word-equality frequencies; it cannot
repair the four recipe-profile exclusions. Contextual writers are outside that fact.

## Evaluation and verification
Use cached GDT1229 RESULT.json samples and its SPEC metric tolerances unchanged:
mean length relative0.20, SD relative0.25, top10/type share absolute0.05,
H1 absolute0.15, H2 absolute0.30. All3072 overlapping comparisons stay separated
by reader/cell/seed;18 no-capacity cells stay untested. ANY six-way matching sample
prevents exclusion for that reader. Exclude this fixed rule only if every reader
has zero joint passes. This is an operational engineering screen, not a p-value.

Report canonical short/literal counts, collisions, complete wordbook cost,
raw-letter and escape-only totals, all six metrics, and per-gate/cell decisions.
Independent validator imports no producer code: recompute suffix sums recursively,
bucket matches, decode serialized whole sections, check counts and recompute
entropies by conditional distributions and sample gates. Bind inputs, programs,
protocol and control results before the full source run. Tests and roundtrips
are engineering verification, not native evidence. Preserve all source bytes.

No raw transcription, image, new corpus, f84/f84r/f116v or reserve access; no word
meanings. No check-edge-packet is applicable: no semantic relation score is made.
Local-only4October exception; no commit/push.
