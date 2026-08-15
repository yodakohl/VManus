# GDT132 — cross-register continuation-arity transfer

Status: `FROZEN_BEFORE_EXTERNAL_TARGET_PAIR_ENUMERATION`

## Motivation

GDT131 found one weak, postselected Q20 lead: after controlling aggregate OPEN
compiler structure and final-field opportunity lengths, character trigrams of
the final OPEN field's stripped PAGE_HOST improved prediction of the first BODY
field chiefly through its group-count bin.  It did not improve exact field
identity, wrapper choice, or a discrete compiler transduction.

GDT132 freezes that one scalar continuation-arity hypothesis and transfers it
outside Q20 before enumerating or scoring the target pairs.

## Frozen training rule

Train on all 170 ZL3b Q20 records used by GDT131.  The target is only the first
BODY field's group-count bin `1/2/3/4+`.  Ridge 1000, SHA-256 modulo-32
trigrams, HPR2 parsing, and the following models are inherited without tuning:

1. `REFERENCE`: current-line group/member count, final-field group/PAGE_HOST/raw
   lengths, and aggregate current-line compiler profile;
2. `LAST_HOST_CHAR3_HASH32`: reference plus final-field PAGE_HOST trigrams;
3. `LAST_RAW_CHAR3_HASH32`: reference plus final-field raw-token trigrams.

## Frozen external target

Use `gdt016_group_state_inventory.tsv` and the source separator table only.
Select every pair satisfying all of these mechanical conditions:

- both loci are complete strict source-native physical lines;
- the first line is editor-marked `paragraph_start=1`;
- the second is the immediately following numeric locus on the same page and
  is not another paragraph start;
- section is one of `H/B/P/T/C`, excluding Q20 section `S` entirely;
- neither physical folio is one of the eight Q20 training folios;
- page/locus is not f84r.

The first line supplies its final field; the second supplies its first field.
No target pair may be selected by its token, PAGE_HOST, compiler state, or
target field length.

## Score and controls

Fit all coefficients on Q20 only, then score the frozen external pairs without
refitting.  Primary gain is the reduction in standardized squared-error
pseudo-bits for `LAST_HOST_CHAR3_HASH32` versus `REFERENCE`.  Report held
top-1/top-3 count-bin accuracy and every section/folio contribution.

Use 4,096 target-side permutations of the added representation within section
× Currier × hand × current-line group-count bucket.  Keep target, source-line
shape, reference prediction, and every stratum fixed.  Report local and
max-two p-values.  This null is an exploratory structure-preserving diagnostic,
not a linguistic test.

The frozen transfer lead requires host gain above zero, above raw trigrams,
positive gain on a majority of physical folios, and max-two p<=.05.  Failure
rejects a cross-register continuation-arity rule at this representation.  It
does not erase GDT131's within-Q20 descriptive lead or PAGE_HOST as a formal
layer.

The experiment predicts a formal next-field extent only.  It assigns no
heading, recipe, semantic role, object, gloss, word, morpheme, POS, sound,
language, plaintext, meaning, or translation.  f84r remains sealed and is
rejected before target retention.
