# GDT1224 — the paired-tail writer cannot cover the short whole forms

**SIX_FINAL_SHORT_GROUP_ARCHITECTURE_EXCLUDED.** Each alternative reading has
12 distinct final working signs among two-sign whole groups with definite
spaces on both sides. The unchanged1194/1195 architecture permits at most six.
This is a conditional exact-form contradiction, independent of the statistical
bands audited in1223. No older source-search result is rescored or rescued.

| Reading | Original sample | Internal two-sign groups | Whole types | Final-sign types |
|---|---:|---:|---:|---:|
| IT2a |8000|450|47|12|
| RF1b |8000|468|46|12|
| ZL3b |8000|393|40|12|

The same twelve final working signs occur in each reading:
`a d e k l m n o r s t y`. Some are rare: final n has one eligible occurrence
per reading; several other classes have only two to five. This is not a claim
of a high global error rate or independent palaeographic confirmation.
Every count and the first witness per ending in the original sample order
are preserved in RESULT.json; both outside seams are DEFINITE_SPACE.

## Why the six-sign limit is independent of its fitted key

1195 imports1194's unchanged Writer. Every output has one initial and one
final sign. A nonempty numeric body produces at least one additional sign:
each contract-loop iteration consumes one or two trits and emits one sign.
The q guard can add a sign; it never removes one. Therefore an output of
exactly two signs must have an empty body and no guard. Empty body selects
context0 regardless of depth. The inherited numeric writer has only final
categories25..30, so only final[0][:6] can be used.

Changing the dictionary, initial counter, pairing mask or table assignments
within this architecture cannot increase that maximum. A global bijective
renaming preserves the number of different final signs. Thus no such
renaming makes these complete two-sign forms all writable. This proof does
not rely on a low score of the particular6,000-proposal search.

For illustration, the registered witnesses include `da`, `od`, `am`, `an`,
`ar`, `os`, `ot`, and `dy` in all readings, already eight different endings.
These illustrations were taken from the completed certificate, not chosen as
a replacement success criterion. They have no assigned meanings. The complete
12-class certificate also contains compounds such as `she`: sh is one of the
22 working signs, so she has two working signs despite three EVA letters.

## Consequence, assumptions and limits

1193's earlier three-medial-sign counterexample remains separate;1195 has a
richer medial alphabet and was not covered by that argument. The new failure
concerns its short forms instead.1195's original full-screen failure, capacity
witness and complete source inverses are unchanged.1223's unstable cross-reading
conjunction also remains unchanged. Relaxing its numerical bands would not
remove the exact short-form contradiction established here.

The bound assumes one observed whole group corresponds to one emitted group,
the existing22working units remain distinct, and no new errors, glyph mergers,
short-word exceptions, hidden splits or additional state-dependent final tables
are inserted. These are not identified phonemes or a proved true ink alphabet.
All evidence is from already exposed transcriptions, and the three readings
are alternative descriptions of the same manuscript. This excludes the
stipulated architecture, not all simple human scripts or meaningful language.
No image was opened; no new native lexical value or source language follows.

## Reproduction and validation

Before native acquisition, the actual Writer was checked on126relaxed empty-
body rows:120have length two and use six final signs; six q-guarded rows are
longer. All61,952combinations of512pairing masks and ternary bodies of lengths
zero through four preserve a nonempty output exactly when the body is nonempty.
These fixtures verify implementation details; the loop proof covers all lengths.

The runner uses frozen1174parsing and the exact24,000saved1211IDs. Its separate
validator uses a regex parser, ID-rank joins and independently accumulated
word/final counts, and reconstructs every certificate and the empty-body table.
All agree: VALIDATION PASS. Both programs have the same author. The guard
retains the same179explicit selectors and eight required columns; f84/f84r
remain sealed, f116v and reserves excluded. No scored relation packet.

```bash
python3 experiments/yolo/gdt1224_short_word_final_capacity/src/run.py --out experiments/yolo/gdt1224_short_word_final_capacity/runtime/replay
python3 experiments/yolo/gdt1224_short_word_final_capacity/src/validate.py
```

Use a fresh replay output directory. The validator checks the retained original
result without replacing it. Source-free fixtures are in src/fixtures.py.
Preparation began04:14:13UTC; selection04:21:03; code/source lock04:21:42;
calculation04:21:43; separate validation04:21:56. Inclusive local closure
budget ends04:34:13. No automatic short-word repair or new optimizer. Local
construction checkpoint under the4Octoberinstruction; no public release claimed.
