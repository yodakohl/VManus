# GDT688 method

## Question

Can all practical German verb occurrences in the complete V60 reader be
emitted inside the exact character span of one written, action-licensed token
ordinal, with zero verbs inferred from nominal states or fluent line syntax?

## Inputs

- GDT687's complete 51-line V60 reader and frozen debt totals;
- GDT686's V59 reader for the preceding action-leakage count;
- GDT684's V57 line audit and frozen 31-lemma comparison deck;
- the corrected 32-rule V61 verb deck in `src/V61_VERB_RULES.tsv`.

No page, image or raw transcription is opened. `f84` and `f84r` remain
forbidden.

## Method

1. Validate the complete V60 schema: 51 lines, 479 tokens, 85 action ordinals,
   matching action counts and exact ordinal-to-surface backprojections.
2. Replay GDT684's unchanged 31-lemma set comparison on V59 and V60 and read
   its published V57 line totals. This distinguishes the historical sequence
   74→66→4 from a stale prose claim that all 66 remained after V60.
3. Correct the occurrence scanner without changing a token card: add
   `aufbereiten`, recognize `schließen` under canonical `abschließen`,
   recognize separable `setze … an`, and prevent `kühle … ab` from being
   counted simultaneously as `abkühlen` and `kühlen`.
4. Scan character spans, not merely lemma sets. V60 contains 116 practical
   verb occurrences. Its forty already strict lines provide 95 exact spans;
   the untouched prose has seven one-candidate, ten multi-candidate and four
   zero-candidate occurrences.
5. Render every line by walking its literal token glosses in source order.
   Record the exact start and end offset of each token contribution. A free
   punctuation card changes punctuation but contributes no spoken word.
6. Accept a practical verb only when its complete match span falls inside
   exactly one token segment, that segment's ordinal is in `action_ordinals`,
   and the same canonical verb occurs in that token's literal gloss.
7. Rerender the ten previously untouched nontrivial lines. Eight changes only
   add exact renderer provenance. Two remove real leaks: `verbinden` and
   `abschließen` on f114v.36, `trocknen` and `bringen` on f75r.3.
8. Preserve all 479 token glosses, all 85 action licenses and all semantic-debt
   totals. Add a non-plaintext reader-mode channel inherited directly from
   the prior line modes: sixteen work sequences, 23 hybrids, six state lists
   and six quantity/state lists.
9. Rebuild every generated artifact byte-for-byte and independently validate
   character spans, rule matches, token ordinals, surfaces, glosses, action
   sets, before/after counts, hashes and sealed exclusions.

## Decision rule and claim ceiling

A verb survives in practical prose only if it has one exact token-span and
one exact action ordinal. Lexical resemblance elsewhere on the line and
monotone after-the-fact alignment are not sufficient compiler provenance.

V61 proves renderer provenance, not historical translation. The 113 verbs are
the current exploratory German values of 85 existing action cards. This pass
does not establish those values as plaintext, change any surface meaning,
identify a language or codebook, or resolve any ingredient, disease, patient
or cure.
