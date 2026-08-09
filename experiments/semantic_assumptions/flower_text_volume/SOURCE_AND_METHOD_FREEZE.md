# FLOWERVOL001 flower-panel text-volume freeze

## Question and exposure

FLOWER001 found no recurrent literal/root morphology on its corrected
distinct-folio panel. This prospective follow-up asks a different question:
does the amount or packing of confirmed prose differ between pages explicitly
tagged `flower(s) seen from the side` and pages tagged `no fruits or flowers`?
No class-conditioned page-level volume statistic has been extracted when this
freeze is written. The source panel and its seven triplets are reused read-only
from FLOWER001; no page, block, or source predicate may change.

## Root-free measures

For each page and each alternate manual reading, use only `CONFIRMED_PROSE`
loci and freeze exactly three author-visible or directly transcribed measures:

1. `LINE_COUNT`: number of confirmed physical line loci;
2. `TOKEN_COUNT`: sum of the interlinear word counts on those lines;
3. `TOKENS_PER_LINE`: token count divided by line count.

No root, glyph identity, word type, paragraph reconstruction, illustration
proximity, OCR, automated vision, or plant identity is used. ZL3b, IT2a, and
RF1b are alternate readings of one manuscript, not replications.

## Exact inference and gates

Reuse FLOWER001's exact `3^7 = 2,187` within-triplet assignments and contrast
the mean of the two putative flower pages with the selected negative page,
averaged equally over blocks. Standardize each measure over the orbit. The
two-sided score is the minimum same-direction standardized effect across the
three readings; reading disagreement scores zero. Correct the three measures
with the assignment-wise family maximum and inclusive tails.

A provisional volume association requires all of:

1. exact familywise `p <= .05`;
2. the same nonzero direction in every reading;
3. a minimum absolute raw effect of one line for `LINE_COUNT`, five tokens for
   `TOKEN_COUNT`, or 0.25 token/line for `TOKENS_PER_LINE`;
4. the direction survives deletion of every block in every reading;
5. at least five of seven individual blocks have that direction in every
   reading.

Anonymous controls must bind the panel, parent runner, input, measure matrix,
exact orbit, a unique synthetic assignment, reading disagreement, a
block-constant signal, deterministic output, and target absence. A
nonimporting implementation must reconstruct the controls before one target
invocation.

## Claim ceiling

Even a pass supplies only a page-level text-volume association with this exact
human illustration contrast. It cannot prove that a specific line describes a
flower, identify a word, establish FLOWER/FRUIT/NO, name a plant or language,
or supply plaintext or translation. A failure weakens only the simple
whole-page volume/packing mechanism.
