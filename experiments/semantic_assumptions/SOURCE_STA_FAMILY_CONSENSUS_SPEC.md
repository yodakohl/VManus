# Exact-family three-reading grammar scaffold

## Purpose

Construct a high-confidence, source-aware grammar scaffold without dynamic
alignment, a preferred transcription, the legacy cleaner, or the unavailable
formal parser. The scaffold uses only physical loci whose primary STA family
sequence is exactly identical in ZL3b, IT2a, and RF1b.

This is a transcription-agreement and boundary-capacity pass. It assigns no
grammatical or semantic roles.

## Frozen inputs

- `results/source_sta_group_alignment.tsv`
- `results/source_sta_group_alignment.json`
- `results/source_sta_group_alignment_validation.json`
- `results/source_separator_transcription.tsv`
- this specification

ZL3b, IT2a, and RF1b are alternate readings of one manuscript, not independent
samples. RF is partly derived from ZL and GC, so agreement is a source-
confidence coordinate rather than replication evidence.

## Locus selection

For each reading and locus, concatenate the deterministic primary STA codes
from the source-group alignment and derive the sequence of their first
characters (STA families). A locus enters the broad exact-family panel iff:

1. it exists in all three readings;
2. page, section, Currier, hand, locus code, kind, and grammar-scope metadata
   agree exactly;
3. its complete family sequence is identical in all three readings.

No edit-distance alignment, gap placement, preferred reading, or threshold is
allowed. The primary grammar panel is the strict subset with zero square-
alternative sites in every reading. Loci with alternatives remain in the
broad descriptive output with an explicit flag.

## Boundary projection

Within an exact-family locus, each source separator is projected to the exact
integer offset after a family symbol. A union boundary row stores the separator
state or absence in every reading.

- support 3: every reading places a separator at this offset;
- support 2: two readings place a separator;
- support 1: one reading places a separator and the position is diagnostic;
- synchronized boundary: support at least 2.

Separator types are never silently majority-collapsed. Each reading's exact
type and the complete type profile are stored. A type consensus exists only
when every supporting reading uses the same type.

For every exact-family locus, split the family and member-code sequences only
at synchronized boundaries. This creates source-synchronized construction
groups. The primary grammar scaffold consists only of groups from the strict
zero-alternative locus panel.

## Hard gates

- exact hashes of all frozen inputs;
- exact three-reading locus and metadata intersection;
- exact family-sequence equality, with no dynamic alignment;
- every boundary position strictly internal and recoverable from source-group
  cumulative symbol counts;
- exact per-reading boundary reconstruction from union rows;
- exact member-code family equality at every retained symbol position;
- exact group reconstruction by joining synchronized groups and boundaries;
- separate broad and strict-zero-alternative counts;
- independent nonimporting reconstruction of every locus, boundary, and group
  output plus JSON/report;
- zero inherited formal roles, roots, English glosses, or semantic labels.

## Claim ceiling

The pass may establish a three-reading exact-family transcription scaffold and
source-synchronized boundary capacity. It cannot establish authorial word
boundaries, physical character identity, pronunciation, morphology, parts of
speech, language, cipher, lexemes, plaintext, or translation.
