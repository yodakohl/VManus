# GDT1288: fixed overlapping-bank source capacity, before glyph fitting

## Decision note and old constraints
Known shape/context dependence motivates small context-sensitive writing, but
1180's previous-source-character-class tables failed.931's disjoint two-bank
14-sign teaching instance is excluded; its switch/next-only ambiguities remain.
1202 excludes any at-most-two whole-word spellings on these four fixed source
projections. Increasing the number of DISJOINT absolute-selector banks does not
escape that bound: first-character entry differs only by selector/no selector,
and the next state is thereafter fixed by each source character.
The newly proposed mechanism instead has OVERLAPPING source membership and retains
the current bank if it contains the next letter. The state can persist across
several letters/words; it is not1180's direct previous-letter class. For example
'as' has distinct payload indices(0,18),(17,9),(8,0)from the three banks below;
all banks are reachable from reset0 (t->2, then l->1). No native meanings inferred.

Unknown: does the actual fixed state history even offer enough different word
forms and sufficiently dispersed high-frequency words on the unchanged sources?
Any deterministic full carrier using only the source word and this entering bank
cannot distinguish repeated instances of the same(word,bank). Counting these
cells is an optimistic necessary screen before choosing output drawings. Failure
stops this exact bank mechanism on these sources, with no alphabet/table/window/
bank-count repair. Passing keeps capacity open only; it is not an encoder fit or
native reading. No native inference is drawn from a toy roundtrip.
Smallest adequate test: source state traces plus two existing frequency bounds;
no glyph mapping, full distribution fit or decoder. Inclusive budget00:55–01:35UTC
9October2026 covers proposal/predecessor review, implementation, validation and
local closure within the ten-hour user interval. No new sources or held reserves.

## Fixed hand mechanism
Ordinary source alphabet is case-sensitive lowercase a..z. Three banks, in order:
B0=abcdefghijklmnopqrs
B1=jklmnopqrstuvwxyzab
B2=stuvwxyzabcdefghijk
Each has19distinct letters. Home bank is0for a..i,1for j..r,2for s..z.
For each next lowercase letter: if current bank contains it, retain bank and write
its column payload0..18. Otherwise write one absolute selector for its HOME bank,
enter that bank and write its column. No optional switch or alternative home.
Visible word boundaries preserve each stored source token, with bank continuing
across words and physical wrapping. Each stored recipe begins with reset0, marked
by the recipe boundary; no within-recipe hidden reset.

A complete proposed carrier has19payload drawings and3separate selectors,22total.
The outside-a..z finite character list is the sorted set from the COMPLETE existing
source file, including uppercase, punctuation and rare letters unchanged. This
charges a literal table; no casefolding, deletion, vowel loss or new normalization.
An outside character is quoted as S0 S0 followed by exactly TWO base19 payload
digits for its zero-based index in that fixed list; quoting leaves the bank unchanged.
Require at most361outside characters; if exceeded, stop with source-contract failure.
A normal selector is always followed by a payload, so S0 S0 unambiguously introduces
a quote; other adjacent selector pairs are illegal. Decoder consumes two payload
digits literally and checks range. Unlisted source characters are unsupported.
This is a paid artificial construction, not historical attestation or glyph values.
No physical drawings are assigned in this necessary frequency test. Quote entries
are not genuine selector operations; the ordinary-selector subsequence cannot have
the same bank twice successively. Do not apply that rule naively to printed quotes.

## Sources, population and immutable decisions
Use exactly1177SOURCE_TEXTS.json, four already exposed complete CoReMA projections
b4,w1,bs1,gr1. All stored words, recipe boundaries and order retained. For each
book simulate the prescribed states over every stored recipe, retaining indexed
word trace; score the first8000stored words (one eventual printed group per token),
identical to1202. Later words do not influence earlier states. The rare-list inventory
uses all four old sources, openly exposed, not an independent source holdout.
No source words, source-language identity or code entries are assigned to Voynich.

Targets ONLY frozen1174RESULT.json['targets'],8000groups per alternate reader.
Use unchanged necessary tolerance directions: type lower bound = native distinct
count minus400; top10upper count = native top10count plus400. Both arise from
original +/-0.05fraction limits. No new target access, pooling or glyph scoring.
f84/f84r/f116v and all reserves remain closed. No raw mixedTSVqueries or images.

For each actual sampled source event count cell=(exact source word,entering bank).
Tmax=#nonempty cells. Cmin=sum ten largest cell counts. Any deterministic glyph
carrier in this class maps each cell to one form; coalescing cells cannot increase
form diversity or reduce the top10sum. This is NOT1202's optimally balanced free
allocation: the bank visits are now fixed by the source sequence. Report all
book/reader conditions separately; overall necessary pass requires both directions
for EVERY book/reader. A failure excludes this fixed source/mode/grouping contract,
not all contextual writing or every possible meaningful manuscript source.
If all pass, status NECESSARY_CAPACITY_ONLY; else FIXED_OVERLAPPING_BANK_CAPACITY_FAIL.
No automatic renderer, native selector search, fourth bank or row permutation.

## Verification
Freeze protocol/program/source hashes before counting. Independent validator imports
no runner, implements next-state behavior through set membership/home domains,
rebuilds every indexed source-word trace, exact source cells, sampling and all gates.
Small source-free examples check reachable banks, three distinct 'as' encodings,
quote roundtrip/canonical rejection, and cell-merging bound. These fixtures validate
the logic, not medieval usability, target plausibility or statistical power.
Retain all rare/source assumptions. No source-control result is decipherment progress.
