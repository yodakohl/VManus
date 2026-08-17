# GDT264 — q13 within-page record fingerprint

## Question

Before interpreting any label-to-paragraph recurrence as a topic or address,
ask whether a mechanically separated q13 record has a reproducible internal
formal fingerprint at all.  Can one half of a record retrieve the other half
from the competing record on the same physical page?

This is an exploratory prerequisite for semantic work, not a translation
test.  It uses the already published, f84-free GDT227 abstract interlinear and
does not open or query f84r.

## Frozen panel and split

Eligible records have at least four distinct physical loci.  Eligible pages
have exactly two such records, so every retrieval is a binary within-page
choice.  For each record and each of four fixed SHA-256 split seeds, distinct
loci are sorted by `SHA256(seed|locus)` and divided as evenly as possible into
views A and B.  All fields on one physical locus stay in the same view.

Each view predicts the identity of its mate in both directions, A→B and B→A.
The competing candidate is the other eligible record on the same page.  Thus
page, section, hand, illustration ecology, and broad register are exactly
controlled by construction.

## Fixed representations

The six representations are:

1. `STRUCTURE_ONLY`: field-size bins, closure type, and the mechanically
   size-derived broad field class;
2. `COMPILER_COARSE`: wrapper/frame/inner-D/right/DY/B3 coordinates without
   PAGE_HOST identity;
3. `RAW_EXACT`: exact visible source groups;
4. `PAGE_HOST_EXACT`: exact HPR2 PAGE_HOST identities;
5. `RAW_CHAR3`: within-group boundary-marked character trigrams;
6. `PAGE_HOST_CHAR3`: within-host boundary-marked character trigrams.

No n-gram crosses a source group or PAGE_HOST boundary.  TF-IDF cosine is
computed over all unlabeled views; record labels are used only to score mate
retrieval.  This is descriptive retrieval, not a trained language model.

## Null and decision

The exact scientific unit is the within-page mate assignment.  In each of
4,096 deterministic null worlds, candidate record identities are independently
swapped within every page and split, with the same swaps shared by all six
representations and both directions.  The report includes local inclusive
p-values and a max-six search adjustment.

After observing the primary compiler lead, one explicitly post-hoc diagnostic
decomposes it into five fixed blocks: wrapper, frame+inner-D, right family,
DY+B3 closure, and the joint compiler cell.  Its p-values use a separate
max-five adjustment and are mechanism localization, not preregistered evidence.

Interpretation is deliberately asymmetric:

- a PAGE_HOST result above raw and compiler controls would nominate a
  paragraph/record-local opaque content channel;
- a raw-only result would indicate surface texture rather than localization to
  PAGE_HOST;
- no above-null representation would close this particular record-fingerprint
  prerequisite and further weaken topic readings of local label recurrence.

No result assigns a record topic, object, procedure, word, morpheme, sound,
language, plaintext, or translation.  The prior f84r transient-parse breach is
disclosed in GDT257; this experiment performs no new f84r access.
