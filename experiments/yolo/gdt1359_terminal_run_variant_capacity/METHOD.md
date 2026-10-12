# GDT1359 — Terminal-run-dependent spelling budgets

## Decision and budget before source counting

IDEA001035 shortens a repeated terminal run using the following source word.
Its exact finite set-valued reader is correct, but source-free back-reading of
arbitrary native text is not a fit. The literal writer already inherits1240's
fixed five-source internal-run obstruction; do not recount or credit that here.
Select IDEA001037: test a larger ARBITRARY-WHOLE-SPELLING family constrained only
by the variable number of forms permitted by the terminal-run operation. Unlike
literal rewriting, arbitrary whole labels need not preserve internal letter runs.

1202allowed at mosttwo spellings per exact source word. That old bound cannot
simply be applied to1035: longer terminal runs allow more than two spellings,
while a one-character word cannot be shortened at all. Unknown: do those exact
run-dependent budgets permit the unchanged four source profiles to meet the old
necessary frequency screen? Failure closes this broader bounded-label family on
these profiles before any full writer or alphabet work. A pass retains only
count capacity; it does not override the old literal-source failures.
Smallest adequate test: fixed source frequency/run table and closed-form bound,
with independent round-robin allocation verification. No native census, decoder,
new source or fitted error budget. Conservative allocated window13:40–14:15UTC
12October2026 includes selection, proof, counting, validation and publication;
first explicit clock13:52:07. Allocation is not a measured start claim.

## Frozen source and inherited comparison

Use1177SOURCE_TEXTS.json, first8000exact stored words per b4/w1/bs1/gr1 in the
existing recipe/word order. Strings and terminal runs use original Unicode code
points without normalization, case folding, punctuation removal or word joining.
All stored words, including one-character punctuation, remain. These are fixed
comparison profiles, not identified Voynich originals or universal languages.

Reconstruct the original1174targets from RESULT.json (tokens8000, type_ratio and
top10_share), and require identity with1202RESULT.native_limits. Native type
lower limit is observed types minus400; Top10upper is observed count plus400.
These are the unchanged old engineering tolerances, not significance intervals.
This is NOT1358's new strict-FIRST8000panel or its exact replacement bound.
Inherited source/projection/target-sampling qualifications remain. No raw native
TSV, groupcache, image, newdata, f84/f84r/f116v/f1rbody or reserve is opened.

## Variable-budget relaxation and proof

For nonempty word w, length L and maximal terminal-identical-codepoint run t,
1035can delete at most min(t,L-1) characters. The number of possible remaining
prefixes is therefore a(w)=1+min(t,L-1). Give each word ANYa(w) fixed complete
written forms and grant arbitrary occurrence-by-occurrence selection. Do not
require these forms to resemble the source, preserve its letters, honor real
neighbors or record-final restrictions, or be humanly learned. Allow distinct
source words disjoint output-label sets. This is more freedom than1035.

For frequency f, at most min(f,a) different forms can be used. Summing gives the
exact optimistic maximum type count in the free-label relaxation. To minimize
Top10, split f into a integer cells as evenly as possible: q=f//a,r=f%a;
r cells receive q+1 and the rest q, dropping zeros. Concatenate all source-word
cells and take the ten largest. A Robin-Hood transfer within an unequal word
allocation cannot increase any global largest-k sum, so balancing each word
minimizes every TopK. Cross-word spelling collisions merge cells; they cannot
increase distinct forms or lower TopK. Thus these are sound generous bounds.
The same disjoint balanced allocation attains both bounds in the RELAXATION,
not necessarily in the complete contextual writer or a rendered language.

Retain each word/count/L/t/a and all positive balanced cells. For each book,
report source types, budget distribution, maximum types, minimum Top10count,
and all12book/reader conjunctions separately. Also compare with the existing
1202two-alias envelope: type gains from a>2 and losses from a=1, numbers of
words actually gaining/lossing possible forms, and signed Top10difference.
Do not hide one-character exceptions or let one passing condition rescue another.
No new threshold, book subset, third alias for t=1 or post-result carrier repair.

## Source-free checks and reproducibility

Before counting, enumerate small integer allocations and check balanced vectors
minimize every TopK and maximize nonempty cells; check merging cannot improve
bounds. Verify a1 for a one-character word and aL for a uniform word. The existing
1035local-reader/ambiguity proof is retained separately: at each nonmatching
boundary (or one-character left word) there are R+1 choices; this is cardinality,
not Shannon entropy or a failure just because a reader is ambiguous.

Freeze protocol, both programs, controls, source/profile summaries, raw1035/1037
and proof review before source-run counts. Independent validator imports no
runner, counts source words separately, obtains terminal runs via grouping,
and distributes occurrences cyclically among allowed cells. Check exact source
prefix digests, word tables, old1202counts and all inherited target intervals.
PASS means arithmetic/provenance validation, not historical or semantic evidence.
Retain all earlier source failures and all unknown-source possibilities. No
native word, sound, source language or record boundary is assigned.
