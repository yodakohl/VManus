# GDT677 method

## Question

Can the nine remaining forms in GDT676's non-singleton one-hole lines receive
concrete, compositionally related meanings that remain unchanged at every
exact occurrence, and can those meanings close the lines without falling back
to generic work-item prose?

## Inputs

No new manuscript page is opened. The build uses:

- the published V48 panel for all 4,128 admitted lines and the twenty target
  occurrences;
- the GDT673 and GDT675 transferable-occurrence tables to verify that none of
  the twenty positions had already been assigned by an intervening overlay;
- GDT674/GDT675 result counts for the current global coverage state;
- GDT676's complete 51-line V50 reader for the nine one-hole lines;
- a guarded locus-selected cross-transcription query for only those twenty
  lines, with f84 and f84r rejected before row materialization.

The semantic input is explicit:

- `src/TARGET_CARD_SPECS.tsv`: nine exact-whole cards, compositions, meanings,
  rivals, confidence and expected occurrence counts;
- `src/OCCURRENCE_CONTEXT_SPECS.tsv`: one manual context decision for every
  exact occurrence;
- `src/THREE_READER_SYNTHESIS.md`: the disagreement and final choice among a
  recipe-copyist, practical preparer and historically informed apothecary
  reading;
- `src/HISTORICAL_ANALOG_SPECS.tsv`: eight dated genre and notation analogies,
  each with a source link and an explicit limit.

## Method

The nine target forms are grouped into five useful contrasts plus two
singletons:

1. `ltaiin / oltaiin`: initial `o` changes Holzdroge into Holzdrogenansatz
   while cold grade III remains fixed.
2. `ykcho / kchody`: initial `y` licenses an anaphoric preparation action;
   terminal `dy` licenses the finished hot-dry result.
3. `olchain / lolkaiin`: material heads combine with dry-II and hot-III
   quality/degree blocks.
4. `aror`: `ar` fraction I plus `or` portion yields one portion of the first
   drug fraction.
5. `losair`: RF1b's visible `los air` split selects drugwood batch plus second
   fraction; unsplit `lo+sair` remains the named seed-decoction rival.
6. `taiky`: only outer cold `t` and terminal light-hot `ky` are transparent.
   The word is retained as a learned whole; internal `ai` remains opaque.

`src/run.py` finds exact whitespace-delimited target tokens rather than
substrings. For each occurrence it verifies the old unknown marker, aligns
IT2a and RF1b to the ZL3b token sequence, applies exactly one unchanged card,
and emits the full before/after context. All twenty manual decisions must be a
named `HOLD_*`; a card is not allowed to acquire a different meaning at a
difficult locus.

For the nine GDT676 lines, the builder replaces exactly the one matching
`⟦surface:?⟧` chunk, preserves every other token chunk and recomputes action
scope, line mode and coverage. `ykcho` adds action ordinal 1 to f56r.6, changing
that one line from nominal register to mixed record. The other eight modes stay
unchanged. The complete 51-line V51 deck is then rebuilt, including all 42
untouched GDT676 lines byte-for-byte at the working-line layer.

The builder rejects the inherited hard-generic filler vocabulary. It writes
the nine cards, all twenty occurrence contexts, six forward predictions, eight
historical analogues, nine completed lines, the complete 51-line reader and a
compact result. The validator rebuilds all eight generated result files in a
temporary directory and compares them byte for byte, then checks token counts,
reader splits, exact meanings, action scope, line modes, coverage and file
hashes.

## Decision rule and claim ceiling

The pass requires:

- nine exact cards and exactly twenty inherited occurrences;
- the expected surface distribution `1/1/4/4/1/1/6/1/1`, with every context
  retaining the same surface meaning;
- 17 bilateral-exact and three one-reader-exact target positions, including
  the RF1b `los air` split, IT2a `aror+sheey` merge and IT2a `kshody` variant;
- nine complete token-preserving lines, one named mode correction, and no hard
  generic filler;
- V51 totals of 51 lines, 479 tokens, 352 assigned positions, 127 visible gaps,
  eleven complete lines and 49 licensed action positions;
- global current-panel movement from 7,943 to 7,923 gaps and from 1,382 to
  1,391 complete lines;
- byte-identical independent reconstruction of all generated result files.

The cards are concrete working meanings and make explicit sister predictions;
they are not confirmed plaintext or phonetics. Historical sources show that
substance/quality/degree, weights, fractions, learned drug names and process
instructions coexist in real medieval medical registers. They do not identify
the Voynich signs, language, exact ingredients, plant species, diseases,
patients, cures or carrier liquids.
