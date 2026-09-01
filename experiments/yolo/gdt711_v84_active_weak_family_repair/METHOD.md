# GDT711 method

## Question

Can the least credible part of the active V83 dictionary be made more concrete
and more compositional by removing nouns supplied only by the fluent sentence
renderer, while keeping every occurrence usable?  In particular, can one
lexical value for `dain/daiin` predict the locally required grade/count
realizations without storing the neighbouring object inside the word meaning?

## Inputs

- GDT710's 332 active reading cards, 479 occurrence-evidence rows, 1,594-row
  complete confidence table and 2,115-card lineage table.
- Thirteen compact family rules distilled from the already admitted GDT647,
  GDT651–GDT655, GDT659, GDT661, GDT685–GDT687 and GDT689–GDT694 reports.
- Thirty explicit repair specifications selected from the complete set of 181
  active W0/W1 readings.  They cover 49 existing positions on 25 admitted
  pages.  No new manuscript page or transcription is read.

## Method

1. Partition all 181 weak active readings into eleven disjoint repair queues.
   This is a complete audit census, not a frequency sample.
2. Link exact normalized master cards for navigation, but assign those links
   zero automatic score credit.  A repeated spelling or matching old card is
   not by itself semantic evidence.
3. For each selected reading, delete the named unsupported atom.  Typical
   deletions are an unlicensed object (`Gummi`, `Arzneikompositum`), historical
   unit (`Gran`, `Handvoll`, `Dosis`) or product name (`Mazerat`, `Absud`,
   `Auszug`).  The repair specification records both positive evidence and the
   remaining counterevidence.
4. Store two distinct outputs:

   - `v84_lexical_core_de`: the reusable dictionary entry;
   - `v84_context_realization_de`: the wording licensed only at that token.

   Seven `daiin` readings therefore become one lexical `Wert III` card while
   their occurrences retain either `Grad III` or `drei`.  Three `dain`
   readings analogously become `Wert II` with `Grad II` or `zwei` in context.
5. Consolidate only selected readings with the same exact surface and the same
   new lexical core.  Keep all 479 source positions, spellings, segmentations
   and original GDT710 occurrence columns unchanged.  Semantic scope,
   applicability, export boundary, bound spans and source provenance travel
   with the lexical card instead of being flattened to a generic word type.
   Aggregate lexical span membership is distinct from the exact span ID at an
   occurrence; the latter is copied position by position.  The one GDT683
   `cheop ol` compound receives its explicit local `G683_CHEOP_OL` marker.
6. Recompute the exploratory working score as
   `min(max(source score) + declared repair delta, declared lexical cap)`.
   Context realization has its own, never higher, cap.  The delta rewards only
   a named removed debt or a common core shared by the retained rivals; it does
   not reward vagueness, frequency or fluency.
7. Replay the builder and validate hashes, source-field parity, occurrence
   conservation, family sources, all score/level boundaries, complete-table
   counts and critical readings.

## Decision rule and claim ceiling

Pass if the thirty specifications exactly match their GDT710 source meanings;
all 332 old readings map once to 324 V84 lexical readings; all 479 occurrences
survive unchanged; the repaired block covers exactly 49 positions/25 pages;
the complete table contains 1,586 readings/1,582 surfaces; every one of the 19
W3 readings and 77 W3 positions retains its meaning, score, scope,
applicability, export boundary, bound-span metadata, writer and provenance; all
historical states remain `H0_NONE`; and every relation-word delta remains zero.

This is an intentionally exploratory working dictionary.  W0–W3 are internal
audit levels, not probabilities.  A W2 card means the proposed core currently
fits its admitted family better than the removed over-specific gloss; it does
not identify plaintext, language, a historical codebook, a manuscript-wide
morpheme or an actual medieval substance.  `f84` and `f84r` are forbidden.
