# V19 — complete Herbal article and singleton consolidation

Date: 2026-08-21

Status: maximally abductive ten-page sidequest; not deciphered plaintext or a
canonical GDT experiment.

## Fixed target

The four authorized Herbal pages contain exactly:

- 100 visible GDT327 events;
- 66 exact card types;
- 55 types occurring once in the four-page Herbal corpus;
- 11 recurrent Herbal types.

V19 must give all 100 events a coherent article reading and improve the 55 weak
singleton defaults without losing any concrete meaning elsewhere.

## Article hypothesis

Treat each page as an illustrated late-medieval simple/medicine article whose
possible source inventory includes:

```text
PICTURED SIMPLE / LOCAL NAME / SYNONYM
VISIBLE PART: root, stem, leaf, flower, seed, bark, juice
HABITAT or gathering time
QUALITY: warm, cold, dry, moist, degree or strength
PREPARATION: wash, dry, pound, boil, steep, strain, mix, preserve
MEDIUM: water, wine, oil, honey, vinegar or the plant's own juice
MEASURE or duration
APPLICATION: drink, eat, bind on, wash, bathe, anoint
INDICATION or claimed effect
CAUTION, comparison, continuation or inherited reference
```

This is a candidate source ontology, not a proven universal field order. A
physical line is not assumed to end a sentence.

## Four independent perspectives

Reuse R1–R4 unchanged. Each agent must remain blind to sibling V19 outputs.

## Required work

1. Inspect the four permitted plant drawings qualitatively and write a frozen
   visible-feature description before assigning text meanings.
2. Propose one concrete pictured-simple identification or historical source
   family per page. Exact species names are encouraged as guesses but must have
   a broader fallback such as `broad-leaved waterside simple`.
3. Reconstruct every paragraph/article across physical lines using the V18
   recurrent deck unchanged unless a contradiction forces an explicit
   concrete revision.
4. For every one of the 66 exact Herbal card types assign:
   - one concrete default phrase;
   - source class;
   - confidence;
   - every occurrence and local phrase;
   - whether picture, recurrent deck, syntax/order or historical practice
     supplies the assignment.
5. For every singleton compare at least two concrete alternatives. Prefer a
   historically ordinary article phrase that also improves its neighboring
   cards and complete article.
6. Count how many different semantic classes and inserted silent arguments are
   needed. Do not make every singleton a unique exotic disease or ingredient.
7. Produce fluent complete readings of f10r, f11r, f55v and f56r, explicitly
   preserving sentences that cross physical lines.

No final gloss may be `unknown`, `opaque`, `content`, `payload`, `item`,
`value`, `state`, `plant detail`, `property`, `operation` or another semantic
blank. A low-confidence singleton still receives a phrase such as `the fibrous
root`, `grows beside running water`, `dry it in shade`, `mix with honey`, or
`apply to the swollen place`.

## Consistency constraints

- The 11 recurrent Herbal types must retain one meaning across their
  occurrences unless one fixed construction-conditioned sense is necessary.
- The V18 shared recurrent deck remains the default bridge to Bio.
- Do not derive meaning from EVA substrings, glyph resemblance or PAGE_HOST
  decomposition.
- Do not force a rigid NAME→DESCRIPTION→RECIPE order.
- A water/habitat/medium reading is allowed where it improves the article; it
  is neither required nor prohibited.
- Inserted picture arguments must be marked explicitly.

## Deliverables

- candidate report;
- `V19_Rx_HERBAL_CARD_DICTIONARY.tsv` with all 66 exact types;
- `V19_Rx_100_EVENT_INTERLINEAR.tsv`;
- `V19_Rx_COMPLETE_HERBAL_ARTICLES.md`;
- `V19_Rx_SINGLETON_ALTERNATIVES.tsv` with all 55 singleton types;
- `V19_Rx_VISIBLE_PLANT_FREEZE.tsv` produced before textual assignment;
- reproducible builder and coverage checks.

## Final selection

Select the dictionary that yields the most coherent four complete articles,
the smallest reusable historical source inventory, and the fewest silent
repairs. Propagate it into the full 776-group dictionary/ledger. No Astro or Bio
meaning may disappear. Keep f84 and f84r fully sealed.
