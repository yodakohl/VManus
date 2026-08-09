# Source-boundary grammar transfer capacity

## Purpose

Decide, without fitting or scoring a boundary model, whether the strict
three-reading exact-STA-family scaffold has enough physical-folio support for a
held boundary-grammar transfer test.

The future test may learn only from positions where all three readings place a
source separator (support 3) versus positions where none does (support 0). Its
unopened target will compare positions supported by two readings with positions
supported by one. ZL3b, IT2a, and RF1b remain alternate readings of one
manuscript, not independent samples.

## Frozen inputs

- `results/source_sta_family_consensus_loci.tsv`, SHA-256
  `84354a9e5d291ab00f45c9bfe161f62d8cbd8c39db7511ff263cd9fcfe9d9e77`
- `results/source_sta_family_consensus_boundaries.tsv`, SHA-256
  `b32aa0a197f9a09eb19087ca80fcc0346601576d49429c346a5df23826ef3974`
- `results/source_sta_family_consensus.json`, SHA-256
  `193ac76bd14b3967844035e8c3997f402d556c7aecf3190145c5295b4eeab3f7`
- this specification

## Reconstruction

Use only loci with `strict_zero_alternative=1`. For every internal gap after
family symbol positions 1 through length minus 1, assign support 1, 2, or 3
from the boundary table. A gap absent from that table has support 0. Reject
duplicate boundary keys, noninternal positions, metadata drift, or a boundary
whose stored left/right family differs from the locus sequence.

The physical folio is the leading `f` plus digits in the page identifier, so
recto/verso and panel suffixes stay in the same held unit. The primary local
context is the ordered pair `(left_family,right_family)`. A target position is
leave-folio-out covered only when that pair occurs at a support-0 or support-3
training position outside its physical folio.

## Capacity gates

All must pass before a scored preregistration is allowed:

1. exactly 3,572 strict loci and 91,879 internal gaps;
2. exact support counts 71,356 / 814 / 668 / 19,041 for support 0/1/2/3;
3. at least 600 positions in each unopened target class;
4. at least 80 physical folios contain both support-1 and support-2 positions;
5. at least 90 physical folios contain each target class;
6. every support-2 position and at least 99% of support-1 positions have a
   leave-folio-out support-0/3 training occurrence of their family pair;
7. holding out any physical folio leaves at least 18,000 support-3 and 68,000
   support-0 training positions;
8. section, Currier, locus-kind, and grammar-scope categories occurring in
   support 2 are all represented in support 1 and conversely;
9. no score, fitted parameter, support-2/support-1 contrast, p-value, lexical
   label, or English gloss is computed.

## Decision and claim ceiling

`GO_FREEZE_SOURCE_BOUNDARY_GRAMMAR_TEST` authorizes only a new preregistered,
physical-folio-held source-boundary grammar experiment. A pass supplies no
authorial word boundary, correction of any reading, grammar role, sound,
morpheme, lexeme, plaintext, language, or translation.
