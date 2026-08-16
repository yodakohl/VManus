# GDT167 — register-conditioned opaque PAGE_HOST codebooks

Status: `METHOD_AND_ANALYSIS_FAMILY_FROZEN_BEFORE_SCORING`

## Question

GDT166 found nonrandom local PAGE_HOST context alignment but no manuscript-wide
exact-host context code.  GDT167 asks two narrower questions:

1. Does exact opaque host identity predict unordered physical context when a
   codebook is trained and tested strictly inside a section/Currier register?
2. If those register spaces differ in identity, can a fixed low-complexity,
   glyph-blind mapping learned from marginal structural signatures preserve
   held-out host--host co-occurrence geometry across registers?

The alternatives are register-specific lexical/code inventories, a common
compiler whose host values are re-bound by register, local distributional
ecology without stable code identities, or no powered signal at this scale.
These are formal alternatives, not word or meaning claims.

## Source firewall and strata

Input is `gdt062_right_family_inventory.tsv`.  Every row whose page or locus
begins `f84` is rejected before retention.  Retained fields are exact
`PAGE_HOST` identity, physical locus/index/count, folio, section, Currier,
catalogued hand, and mechanical position.  Raw token, wrapper, inner-D, local
frame, right family, DY, B3, and every glyph/string feature are inaccessible.

Freeze every section/Currier cell with at least five physical folios and 500
groups on multi-group physical lines:

| stratum | section/Currier | groups | lines | folios | hands |
| --- | --- | ---: | ---: | ---: | --- |
| `HERBAL_A` | H/A | 3,909 | 789 | 47 | hand 1 |
| `HERBAL_B` | H/B | 1,323 | 188 | 16 | hands 2, 3, 5 |
| `STARS_RECIPE_B` | S/B | 4,854 | 661 | 12 | hand 3 plus one `@` folio |
| `PHARMA_A` | P/A | 650 | 107 | 6 | hand 1 |
| `BIOLOGICAL_B` | B/B | 3,153 | 468 | 9 | hand 2 |

Excluded capacity cells remain explicit: T/B has 949 groups on four folios,
C/B 185 on two, S/A 301 on one, and T/A 31 on one.  They are not pooled into
an attractive post-hoc `OTHER` stratum.

## Within-register codebook prediction

Use exactly two normalized unordered contexts from GDT166:

- `WINDOW_PM2`: physical offsets -2,-1,+1,+2;
- `WHOLE_LINE`: every other group on the physical line.

Each focal occurrence contributes total context weight one.  Paragraph bags
are not rerun because GDT166 found no paragraph alignment excess and their
coverage is incomplete.

Within each frozen stratum, fit the inherited equal mixture of separately
smoothed section, Currier, hand, stratum-local focal-frequency bin, position
quartile, and line-count target distributions (concentration 32).  Exact focal
identity has concentration 16 toward this nuisance.  Leave one physical folio
out.  Run an additional leave-one-hand-out score only for `HERBAL_B`, the sole
stratum with at least two physical folios in every hand value.

For each of 5 strata x 2 contexts, report held gain, gain/focal, positive
folios, source reuse, and alignment excess over 1,024 focal-ID permutations
inside held folio and exact nuisance stratum.  Family maxT uses null-centered
gain/focal across all ten fixed tests.  A predictive codebook requires positive
held gain, at least 60% positive folios, and max10 p<=.05.

## Within-register geometry stability

For each stratum, hash each physical folio deterministically into half 0 or 1
using SHA256 of `stratum|folio`.  Select the ten most frequent opaque hosts
having at least four occurrences in both halves.  Selection sees frequency and
capacity only.  Pharma-A fixes the common capacity at ten.

Build whole-line positive-PMI host context profiles independently in each
half, with the 128 most frequent stratum-local context identities and `OTHER`.
Compare the two 10x10 host cosine-similarity geometries by Pearson correlation
over their 45 upper-triangle cells.  Against 1,024 permutations of the second
half's host labels within fixed frequency-rank blocks `[0:3],[3:5],[5:8],
[8:10]`, report local and null-centered max5 p-values.

The only cross-hand geometry sensitivity is Herbal-B hand 2 versus pooled
hands 3+5, on the same ten-host panel.  It is separately labelled and does not
turn alternate hands into independent manuscripts.

## Glyph-blind cross-register alignment

For every one of the ten unordered stratum pairs, run two folds.  Train on
half 0 and score half 1, then reverse.

For each host in the training half construct a 15-dimensional marginal
signature with no host/context identity feature:

- normalized log frequency;
- context entropy;
- top-1, top-3, and top-5 context concentration;
- self-context fraction;
- four position-quartile proportions;
- five physical-line-count-bin proportions.

Z-standardize each feature inside each stratum.  Use a deterministic equal-
weight minimum-cost Hungarian assignment independently within the same four
frequency-rank blocks used by the null.  Neither fitted nor random mappings
may cross a block.
No weight, dimension, K, or mapping is tuned on co-occurrence geometry.

The held target is the Pearson correlation between the two 45-cell whole-line
PPMI cosine geometries after applying the frozen mapping.  Context identity
dimensions are local to each register and are never aligned.  Run 1,024 random
one-to-one mappings within the four fixed frequency-rank blocks.  Report each
pair's two-fold mean, local p, null-centered max10 p, and an overall mean test.

A common re-bound compiler requires overall p<=.05, positive mean geometry in
at least 8/10 register pairs, and at least three max10-positive pairs involving
all five registers.  This is intentionally harder than finding one attractive
pair.

## Decisions

- `REGISTER_CODEBOOKS_WITH_COMMON_REBOUND_ALIGNMENT`
- `REGISTER_SPECIFIC_CODEBOOKS_WITHOUT_COMMON_ALIGNMENT`
- `REGISTER_GEOMETRY_STABLE_BUT_CODEBOOK_PREDICTION_NEGATIVE`
- `NO_STABLE_REGISTER_CODEBOOK_OR_ALIGNMENT`

Every per-stratum and pairwise result remains visible regardless of decision.

## Claim ceiling

At most this experiment can establish register-conditioned exact-host context
codes and/or an anonymous low-complexity correspondence between their graph
geometries.  It cannot establish a word, lexeme, code value, morpheme, POS,
language, semantic role, meaning, plaintext, or translation.
