# GDT783 method

## Question

Can the two previously fixed two-of-three external readings of the GDT781
`chsky` card distinguish a portable quality label from material, preparation,
stage and process readings when the exact target position is masked and every
physical locus counts only once?

## Inputs

All inputs are hash-bound in `src/SOURCE_LOCK.tsv`. The runner reconstructs the
179-page inherited cache only through the GDT782 guarded-loader code, whose
hash is itself bound. The relevant semantic inputs are the GDT734 clean
complete-whole pool, GDT754 provenance sieve, GDT768 display overrides, the
four GDT781 analog relations, and the complete GDT782 renderer.

The three loci were fixed before reading their fields:

- exact target `f86v5.15@12`, `chsky/chsky/chsky`;
- external `f25r.2@3`, `chsky/chrky/chsky`;
- external `f103r.37@7`, `chsky/chsky/chsty`.

The historical controls are already bound observations from Clm 667,
Wellcome MS.542 and Pal.lat.1234. They test only whether single and paired
quality slots are historically plausible.

## Method

1. Reconstruct all three reader lines through `query-tsv`'s inherited guarded
   loader. Verify the fixed target ordinal independently in each reader.
2. Count each physical locus once. Admit an external field only when two of
   three readers put `chsky` at that fixed slot; do not interpret `r` or `t`.
3. Remove the target slot from every line, align remaining slots by offset from
   it, and take a neighbor only when at least two readers agree on its complete
   surface. Use R3 externally and a separately labelled R5 target sensitivity.
4. Rebuild the 770-reading/769-surface GDT734 clean whole pool. Apply GDT754
   sanitation before a card can vote, then use later GDT768 wording for display
   only. Thus `chky` is visible but blocked and `chor` displays as
   `Blütenstand` while retaining only its PART axis.
5. Score the six frozen candidates from complete-axis support in the three
   admissible analogs, two external physical fields and the lower-weight target
   sensitivity. Penalize opposite qualities and additional asserted axes.
6. Keep score ranking and practical selection separate. The score chooses the
   minimum HOT core. `FINAL_SELECTION_SPEC.tsv` retains the still-possible
   parent HOT|DRY card under the sidequest's exploratory retention rule, but
   splits confidence into HOT C1 and DRY C0 and publishes HOT-only dissent.
7. Copy all 109 GDT782 columns and all 376 rows unchanged. Add GDT783 fields;
   refine only the fixed target display. External displays are aggregate card
   audits, never renderer licences.

## Decision rule and claim ceiling

The diagnostic formula is published on every candidate row. It is a ranking
aid, not a probability. The frozen practical selection may preserve the parent
only while the pair remains possible and the minimum supported core and dissent
are explicit. A later card can replace it.

GDT783 may state one replaceable complete-whole quality/state hypothesis and
one existing local `ol`+whole display. It may not identify a lexeme, plaintext,
substance, unit, number, EVA component or reader-variant letter value. External
fields receive no new renderer licence. No new page, image, OCR or
transcription is opened; `f84` and `f84r` remain sealed.
