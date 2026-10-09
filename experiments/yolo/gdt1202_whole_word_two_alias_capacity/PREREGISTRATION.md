# GDT1202 — whole source words with at most two spellings

A necessary capacity bound, not a rendered writer or native interpretation.
Preparation began2026-10-05 12:52:35UTC. Total-work budget25minutes, ending13:17:35UTC,
including predecessor review, implementation, independent check and local closure.
No automatic more-alias scan, state change, dictionary extension or alphabet fit.

## Decision note before data counting
1200supports recurrent B/By/Bdy/BBdy forms;1201shows that transparent learned
chunks can preserve one message across several parses. Neither creates sufficient
word diversity or a native meaning. A candidate with a stable word body and at
most two initial variants motivates this bound; the bound generously covers ANY
at-most-two whole-word spellings, regardless of the part varied or the rule used.
It does not assume that daldy actually has this source mechanism.

Strongest predecessors:1180V2-flat/edge already tried full source words with a
vowel/other entry context and fixed97-unit/code tables; all fixed tables failed.
1196proved bounds for VOWEL FRAGMENTS plus E/C, including A=1..16 free spellings.
It did NOT count entire source words for that relaxation.1197ALT/MTF are unrun
and can create more than two word forms; they are not this model.1002is a shared
native alias-meaning grammar audit, not this source-frequency bound. Those
original decisions remain untouched. No old proposed followup is rerun.

Unknown: can even ideally allocated TWO spellings of each complete source word
reach the inherited necessary type-count and top-ten concentration directions?
If no, ANY two-spelling whole-word writer fails this source benchmark before
choosing glyphs, even one with a large occurrence-specific selection mechanism.
If yes, merely keep capacity open; no glyph/statistical/semantic/historical pass
or automatic return to the already failed1180tables. A positive bound is not an
executable public spelling-selection rule.

## Fixed scope and sampling
Exactly GDT1177 SOURCE_TEXTS.json, exposed CoReMA expanded-edition projections
b4,w1,bs1,gr1. Every stored word is preserved exactly: case, punctuation, rare
characters and order; no new normalization, segmentation, joining, deletion,
semantic equivalence class or choice of an alternative edition. For each book,
flatten stored recipes in order and take its first8000WHOLE words as8000printed
groups. Retain the exact contributing recipe index ranges, sample frequency table
and full-source book/recipe/word counts. This is not a complete diplomatic source
or a new independent holdout. No source copies need be republished.

Targets are ONLY the existing1174three cached reader summaries at8000groups.
ZL3b/IT2a/RF1b remain alternate readings. No new manuscript data, native word
profile, source image, reserve, f84/f84r or f116v opened. This test needs no
GDT388relation packet: no new semantic or image relation is scored.

## Fixed two-alias bound
For each literal source word with sample frequency n, any at-most-two-spelling
writer yields at most min(n,2)positive form cells. Summing gives Tmax. Allow all
cells from different source words to be distinct for this optimistic upper bound.

Split each n as ceil(n/2),floor(n/2), omitting a zero count for the histogram.
Pooling all those cells and summing the ten largest gives Cmin, a lower bound
on the most frequent ten surface forms. This balanced allocation minimizes every
top-k sum. Coalescing cells across source words cannot improve either bound.
Thus the bound even permits contextual homographs; no global distinct-word
cipher assumption is silently used. Choosing glyph lengths cannot repair a fail.

A short exchange proof and tiny exhaustive two-bin allocations will verify the
bound. The independent validator distributes occurrences round-robin instead of
using the runner quotient formula and obtains the whole-word sample by indexed
recipe positions. This validates the arithmetic/source projection only.

Use UNCHANGED1174tolerances: type_ratio +/-0.05 and top10_share +/-0.05. Only the
necessary directions are tested: Tmax >= native_types -400; Cmin <= native_top10
count +400 at8000groups. Recover native integer counts from their exact8000-token
ratios and check consistency. Report all reader conditions separately. Overall
NOT_EXCLUDED requires every direction for every reader and all four books.
Do not reject excess potential types or insufficient minimum concentration;
those can be changed by an actual writing policy or coalescence. Do not call
NOT_EXCLUDED a joint feasible solution for the full tolerance ranges.

Include the one-spelling whole-word baseline and its frequency histogram as
DESCRIPTIVE ONLY. Do not sweep A=3,4,... or select a new state after an outcome.
No concrete V2 recensus/refit, encoder/decoder or glyph metric is in this test.
Existing1180negative source control remains separate from the more general bound.
No assignment is made to a native word, source language, morpheme or cipher key.

## Decision and assumptions
If any fixed book/reader direction fails, status WHOLE_WORD_TWO_ALIAS_CAPACITY_EXCLUDED;
show each failure, preserving any individually non-excluded books/directions.
Otherwise status WHOLE_WORD_TWO_ALIAS_NOT_EXCLUDED, explicitly limited to necessary
capacity. Either outcome closes THIS census, with no automatic repair chain.
The decision concerns these source projections and this one-group-per-word rule,
not every language, meaningful medieval text, source corpus or writing system.
Known q/o,endings,entry context,whole-form residuals and stronger metrics remain
unmet duties of any complete writer.1201does not waive them. Local construction
checkpoint under the live route; no publication or native discovery claimed.
