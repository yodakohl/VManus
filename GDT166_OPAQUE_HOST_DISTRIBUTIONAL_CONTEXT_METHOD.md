# GDT166 — opaque PAGE_HOST distributional context

Status: `METHOD_AND_ANALYSIS_FAMILY_FROZEN_BEFORE_SCORING`

## Question

GDT165 rejected fixed immediate-next-host prediction.  GDT166 removes fixed
order from the endpoint: does an exact opaque `PAGE_HOST` identity predict a
stable bag of surrounding host identities on unseen folios, sections, and
hands beyond frequency, section, Currier, position, and line-size effects?
Do frequency-selected hosts retain the same distributional nearest neighbors
when those strata are excluded?

This is a formal identity test.  Exact identities are categorical IDs only.
No character, glyph, substring, edit, substitution, wrapper, inner-D, local
frame, right family, DY, B3, semantic feature, or English gloss is available.

## Inputs and f84 firewall

`gdt062_right_family_inventory.tsv` supplies only `PAGE_HOST`, physical
locus/index/count, folio, section, Currier, hand, and mechanical position.
`gdt046_line_frames.tsv` supplies only locus/page and the existing editorial
paragraph-start flag for the paragraph sensitivity.  For both files, every
row whose page or locus begins `f84` is rejected before retention.  No f84r
row, image, transcription, or formal payload may be opened, queried, retained,
joined, or scored.

The existing GDT165 `ok -> y` display pair is frozen as a special-case control.
It is not used to select a context scale, feature, panel, threshold, or model.

## Contexts

For each focal occurrence use three fixed unordered bags, excluding the focal
itself:

1. `WINDOW_PM2`: other groups at physical offsets -2,-1,+1,+2 on its line;
2. `WHOLE_LINE`: every other group on the same physical line;
3. `PARAGRAPH_BAG`: every other group in the same paragraph among the complete
   lines retained by the frozen line-frame table.

Paragraph IDs are reconstructed page-locally in numeric physical-line order;
a new paragraph begins at the first retained line or where the frozen
`paragraph_start` flag is one.  This is an editorial layout grouping, not an
authorial semantic record.

Each occurrence's context Counter is divided by its own context size, so every
focal occurrence contributes exactly one unit of pseudo-codelength regardless
of line or paragraph length.  Context members remain exact opaque host
identities.  Correlated bag members are therefore weighted descriptive events,
not independent samples.

Frozen capacity after f84-prefix rejection is 15,364 source groups on 2,431
physical lines and 93 folios.  Window and line modes each retain 15,203 focal
occurrences, with 47,192 and 105,274 raw context links.  The paragraph
sensitivity retains 8,447 focal occurrences, 393,238 raw links, 288 paragraphs,
1,143 complete lines, and 91 folios.

## Held context prediction

Target alphabet is the exact context-host inventory.  For each training split,
the nuisance prediction is the equal arithmetic mixture of six separately
smoothed target distributions:

`section, Currier, hand, global focal-host frequency bin,
 position quartile, physical-line group-count bin`.

Each component has concentration 32 toward the training target unigram.  The
exact focal-host model has concentration 16 toward that nuisance mixture.
These are inherited unchanged from GDT165.  No mixture weight is fitted.

Fit without and score on:

- one held physical folio;
- one held section;
- one held hand.

Report weighted nuisance minus exact-host codelength, bits per focal occurrence,
positive-fold fraction, and seen-source coverage for each context scale.  The
primary conditional null has 1,024 deterministic worlds.  Within every held
folio and exact six-variable nuisance stratum, it permutes focal host IDs while
leaving context bags and trained distributions fixed.  Local p-values are
upper-tail; maxT uses gain per focal occurrence across the three context modes.

The frozen special-case sensitivity removes only focal `ok` -> context `y`
mass and reports the resulting aggregate gains.  It is a control, not a seed,
and is never promoted to a meaning.

## Distributional nearest neighbors

Select the 64 focal hosts with greatest full-panel occurrence frequency and
the 256 context hosts with greatest full-panel context mass; all ties use
opaque SHA256 identity order.  Selection sees no pair association.  Remaining
contexts collapse to `OTHER`.

Use `WHOLE_LINE` as the sole nearest-neighbor context; the other two scales
remain likelihood endpoints only.  For every train/held split, build
positive-PMI context vectors independently.
For each focal host with at least 16 training and four held context units,
choose its training cosine-nearest other host.  Rank that fixed predicted
neighbor by cosine similarity in the held-only profiles; the predicted
neighbor must also have four held units.  Report top-1, top-5, reciprocal rank,
eligible hosts and folds for held folio, section, and hand.

The neighbor null permutes predicted neighbor IDs within split and global
focal-frequency bin, preserving the number and frequency ecology of predictions.
Run 1,024 worlds and maxT across the three split axes.  Exact identity strings
do not enter similarity.

## Decisions

- `OPAQUE_HOST_DISTRIBUTIONAL_CONTEXT_SUPPORTED` requires at least one context
  mode with positive gain under folio, section, and hand exclusion and maxT
  p<=.05, plus neighbor reciprocal-rank above its maxT null on all three axes.
- `OPAQUE_HOST_CONTEXT_WITHOUT_STABLE_NEIGHBORS` requires the held context
  criterion but not neighbor stability.
- `DISTRIBUTIONAL_CONTEXT_LOCAL_ONLY` applies when a mode is positive on held
  folios but fails section or hand transfer.
- `OPAQUE_HOST_DISTRIBUTIONAL_CONTEXT_NOT_TRANSFERABLE` applies when every
  context mode has nonpositive held-folio gain.

All modes and controls are reported even if no confirmation gate passes.

## Claim ceiling

At most this experiment can establish a stable distributional class or
co-occurrence relation among opaque PAGE_HOST identities without fixed word
order.  It cannot establish a word, lexeme, code value, morpheme, POS, language,
semantic role, meaning, plaintext, or translation.
