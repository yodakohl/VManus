# GDT134 — general adjacent-continuation transfer

Status: `FROZEN_BEFORE_GENERAL_ADJACENT_PAIR_ENUMERATION`

## Question

GDT132/133 leave a tiny, post-hoc raw-token trace on 31 paragraph-start to
next-line pairs, but no PAGE_HOST/compiler localization.  GDT134 tests whether
that raw trace transfers to ordinary adjacent continuation lines or is confined
to the exposed paragraph-start panel.

## Frozen training

Use the same 170 ZL3b Q20 records, HPR2 parser, target count bins `1/2/3/4+`,
reference opportunity/compiler variables, SHA-32 character trigrams, ridge
1000, and target standardization as corrected GDT132.  Fit exactly three added
representations:

1. final-field `RAW_CHAR3`;
2. final-field `HOST_CHAR3`;
3. final-field `COMPILER12` without a redundant length term.

## Frozen external panel

Use only f84-free `gdt046_line_frames.tsv` and
`gdt016_group_state_inventory.tsv`.  Select every numeric adjacent line pair
on the same page where:

- both lines occur as complete lines in both inputs;
- the second line has `paragraph_start=0`;
- section is H/B/P/T/C;
- every Q20 training folio is excluded;
- f84r is absent by input construction.

Retain whether the first line is a paragraph start.  The primary generalization
subset is first-line `paragraph_start=0`; the already exposed start-to-next
subset is a named sensitivity.

## Frozen score and null

Apply the Q20-trained models without external refitting.  Report whole-panel,
start-to-next, continuation-to-continuation, section, and folio gains plus
top-1/top-3 accuracy.

Use 4,096 shared target-side representation permutations within exact
opportunity strata:

`section × Currier × hand × first-start × source-group-count bucket ×
final-field group count × PAGE_HOST length × raw-token length`.

If fewer than 50 records are swappable at that exact resolution, report
`INSUFFICIENT_EXACT_NULL_CAPACITY` and also run a clearly labeled coarse null
that stops after source-group count; the coarse p-value cannot pass the primary
gate.

The raw trace transfers only if RAW gain is positive overall and on the new
continuation-to-continuation subset, exceeds HOST and COMPILER, is positive on
a majority of physical folios, and has exact-opportunity max-three p<=.05.

## Claim ceiling

A pass would establish only transferable raw source-string dependence for
next-field extent.  It would not establish a content host, record semantics,
heading, recipe, semantic role, word, morpheme, POS, sound, language,
plaintext, meaning, or translation.  The prior limited f84 audit exposure is
disclosed; GDT134 performs no new f84 access.
