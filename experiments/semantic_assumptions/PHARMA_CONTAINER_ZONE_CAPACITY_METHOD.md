# Pharmaceutical container-zone capacity

## Question

Do existing human source comments provide enough directly attached labels to
test a formal contrast between inscriptions on an upper physical container
part and inscriptions on a lower physical container part?

This is a source-only worth screen. It reads no Voynich transcription,
family surface, member code, root, role, or formal feature.

## Fixed source rule

Read `results/existing_human_exact_locus_annotations.tsv`. Retain only
unhedged rows whose normalized layout code ends in `Lc`. Classify an upper
physical part only from either exact comment stem:

- `On top lid.`
- `On container, top (bigger) part.`

Classify a lower physical part only from the exact comment stems describing a
`bottom half`, `bottom bulge`, or a `bottom (wider|widest|smaller)
section|part`, including the three explicitly numbered lines on one lower
part. Collapse multiple numbered lines having the same page, unit, and class
to one physical unit-state observation.

Exclude page-row descriptions such as `container 1 (top)`, free-standing
placement such as `near top`, `below container`, and `below bulge`, vague `on
container` comments, and all hedged rows. Those describe page/object position
or uncertainty rather than an explicitly named physical container part.

## Worth gates

Do not open any label identity unless all are true:

1. both states occur on at least five physical folios, so a one-sided folio
   sign orbit can attain `p <= .05`;
2. at least five pages contain both states;
3. at least three individual container units contain both states; and
4. there are at least 20 class-balanced page-level opportunities.

The gates are deliberately about independent transfer and directly repeated
physical ownership, not the number of labels on one pharmaceutical folio.

## Duplicate-route boundary and claim ceiling

This differs from the closed DARK/LIGHT root-marker test, the horizontal
EAST/WEST label-placement test, the stopped generic ABOVE/BELOW placement
panel, and the stopped container-versus-plant owner-class screen. It tests a
physical part of a container only. A stop says only that the current human
annotations cannot support that contrast. No lid, top, bottom, container,
part, word, sound, language, cipher, plaintext, meaning, or translation is
established.
