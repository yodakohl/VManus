# GDT016 record-state assembler

Status: **TRANSFERABLE RECORD STATE GRAMMAR PROVISIONAL**

The compiler assigns 15592 strict prose groups on 2471 physical
lines and 94 folios to 15 anonymous states.  It finds
73 run-collapsed line templates occurring at least three
times.

## Held-folio sequence prediction

Across 15592 held states, the line-reset first-order model uses
46592.720 bits versus 47760.554 for the state unigram: a gain of 1167.834
bits.  The same trained models use 48238.230 bits on within-line shuffled held
sequences, so true ordering gains 1645.510 bits while preserving every held
line's state multiset and length.

This establishes a transferable ordering grammar for the deliberately coarse
state projection.  It does not establish that the states are linguistic.

## Strongest transitions

- `AL_STATE → Q_OUTER_STATE`: 19 observed versus 62.69 expected; log2 enrichment -1.70; adjusted p=0.06647.
- `AR_REFERENCE → Q_OUTER_STATE`: 20 observed versus 61.26 expected; log2 enrichment -1.59; adjusted p=0.06647.
- `AR_REFERENCE → ENTRY_STATE`: 24 observed versus 56.92 expected; log2 enrichment -1.23; adjusted p=0.06647.
- `ENTRY_STATE → Q_OUTER_STATE`: 56 observed versus 95.87 expected; log2 enrichment -0.77; adjusted p=0.06647.
- `DY_RESOLUTION → ENTRY_STATE`: 88 observed versus 141.07 expected; log2 enrichment -0.68; adjusted p=0.06647.
- `DY_RESOLUTION → Q_OUTER_STATE`: 354 observed versus 223.69 expected; log2 enrichment +0.66; adjusted p=0.06647.
- `CARRIER_STATE → Q_OUTER_STATE`: 297 observed versus 197.85 expected; log2 enrichment +0.58; adjusted p=0.06647.
- `Q_OUTER_STATE → CARRIER_STATE`: 266 observed versus 197.85 expected; log2 enrichment +0.43; adjusted p=0.06647.
- `OTHER → ENTRY_STATE`: 186 observed versus 245.79 expected; log2 enrichment -0.40; adjusted p=0.06647.
- `OTHER → Q_OUTER_STATE`: 164 observed versus 211.40 expected; log2 enrichment -0.37; adjusted p=0.06647.

The single GDT015-inherited `DY_RESOLUTION → OT_*_LOCAL` hypothesis occurs
{inherited_observed} times versus {inherited_expected:.2f} under the same
within-line reorderings (log2 enrichment
{math.log2((inherited_observed+.5)/(inherited_expected+.5)):+.2f}; one-sided
p={inherited_p:.4g}).  Its three destinations are individually positive:
AR {observed[("DY_RESOLUTION","OT_AR_LOCAL")]}, AL
{observed[("DY_RESOLUTION","OT_AL_LOCAL")]}, and OL
{observed[("DY_RESOLUTION","OT_OL_LOCAL")]}.  This inherited one-test result
is kept separate from the 133-way exploratory atlas, where no transition has
a search-adjusted p below .05.

The template table shows which complete line-state arrangements recur across
folios and sections; these are the next units for semantic interpretation.

The projection is post-selected, priority-based, and lossy.  It can conflate
core identity with renderer state, and a first-order model is not a sentence
grammar.  f84r was not retained, joined, or scored.  No morpheme, syntax,
word, POS, sound, language, plaintext, meaning, or translation is confirmed.
