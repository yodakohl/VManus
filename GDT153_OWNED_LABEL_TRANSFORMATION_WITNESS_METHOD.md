# GDT153 — owned-label transformation witness audit

## Question

GDT152 found a weak ZL3b/IT2a raw-string assignment lead for five exposed
pharmaceutical-label → Herbal-page relations, while exact and character-level
HPR2 PAGE_HOST representations failed. Does the already frozen GDT003 formal
transformation inventory explain that raw-string near miss?

This is a post-hoc mechanism audit on an exposed panel. It is not a new
semantic test and cannot validate the five relations.

## Frozen operation vocabulary

The operation names are read from `gdt003_transformations.tsv`. Exactly the
nine retained GDT003 contrasts are allowed:

- prepend `q`;
- initial `d` ↔ `s`;
- initial `o` ↔ `ot`;
- append/remove `dy`, `dal`, or `dar`;
- final `dal` ↔ `dar`, `dal` ↔ `dy`, or `dar` ↔ `dy`.

Because neither the pharmaceutical label nor a Herbal prose witness has a
predeclared derivational direction, each fixed contrast may be traversed in
either direction. No operation, host, or threshold is selected from the five
target pages. Depth is capped at two operations.

## Panel and scoring

The five GDT152 label/page relations and all three alternate readings are
retained. For each label and each of the five candidate Herbal pages, the
complete GDT062 display-token bag is searched for:

1. the minimum ordinary character edit distance;
2. an exact token reachable within two fixed GDT003 operations;
3. the minimum macro-edit cost: operation count plus residual character edit
   distance after at most two operations.

The macro cost charges every formal operation one unit. If a fixed operation
really explains a multi-character contrast, it can beat ordinary edit cost;
otherwise the zero-operation path wins. All 5! page assignments are enumerated
for each reading and measure.

Nearest-basic display strings are a lossy representation. ZL3b, IT2a, and RF1b
are alternate readings of one manuscript, not replications. GDT003 itself was
not distinguishable from strong string statistics, so even a positive
operation path would be an exploratory formal witness rather than morphology.

## Claim ceiling and seal

This audit can say only whether the fixed GDT003 contrasts account for the
already exposed GDT152 raw-string resemblance. It cannot establish a
plant/component identity, address, semantic role, word, morpheme, POS, sound,
language, plaintext, meaning, or translation. The panel contains no f84r
query or target, and no f84r row is retained, joined, scored, or targeted.

