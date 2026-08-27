# GDT557 method — thirty-page OT/OL/DY state grammar

## Question

Does the local GDT478 distinction `OT=next` versus `OL=continue` transfer to
the complete admitted 30-page running edition, and does adding
`DY=close` produce a compositional start–continue–close reader whose atom
order predicts local scope and statement closure?

## Inputs

- GDT407's 4,576 running events and 715 statements from the old 26-page
  edition, materialized only through guarded `vmanus-exp query-tsv` calls with
  explicit page allow-values, explicit output columns and `f84` forbidden;
- GDT539's 546 contextual events and 78 statements on the current four pages;
- GDT478's 69-slot six-page paired OT/OL result as the local seed;
- GDT556's complete 705-occurrence DY atlas as an exact parity reference.

The union contains 5,122 events and 793 statements. Twenty-eight admitted
pages have running events; f69v and f70v are retained as admitted local-only
pages with zero running cards. No new page is opened.

## Method

1. Reconstruct each old and current statement without changing an event,
   recipe, order or statement boundary.
2. Materialize every exact `OT`, `OL` and `DY` atom. Record its left and right
   atom, recipe role, statement position, neighboring cards and present German
   working reading.
3. Render the unchanged meanings as short state operations:
   `OT` opens/advances the next carrier, `OL` keeps the current carrier active,
   and `DY` closes the current step.
4. Enumerate every marker-only sequence in a card. For each of the three marker
   pairs, count both orders rather than forcing the dominant order onto rare
   reversals.
5. Compare closure rates for sequences ending in DY and marker-bearing events
   without DY. Preserve bare OT, post-DY tails, internal DY and reversed pair
   orders as explicit compositional edge rows with a default reading.
6. Compile one page profile for every admitted page and a seed-to-full transfer
   row against GDT478.
7. Independently rebuild the counts from guarded sources, check exact DY parity
   with GDT556, then replay the compiler byte-identically.

The directional formulas are deliberately compact:

- `OT · X` → danach X; `X · OT · Y` → nach X folgt Y;
- `OL · X` → weiter mit X; `X · OL · Y` → X in Y weiterführen;
  `X · OL` → X weiterführen;
- `X · DY` → X abschließen; `X · DY · Y` → X schließen, dann Y.

An atom standing alone receives its carrier from the same statement context.
The formulas are renderer operations, not additional dictionary entries.

## Decision rule and claim ceiling

The working grammar transfers if all three markers remain positionally
distinct in the full corpus and every observed pair order can be read by the
same three operations in written order. Rare reverse orders are retained as
local compositions; they are not rejected merely for violating the dominant
start–continue–close direction.

This is an exploratory positional working reader for three already assigned
components on already admitted pages. It may add a state-operation layer and
contextual scope formulas, but it changes no surface, recipe, segmentation,
root value, statement boundary or existing clause. It establishes no
plaintext, historical syntax, language, codebook identity, object or
future-form license.
