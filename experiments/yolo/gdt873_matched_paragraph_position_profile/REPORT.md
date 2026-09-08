# GDT873: matched paragraph positions

The primary view supplies a descriptive comparison, but no robust anchor-specific
lead. The strict reading diagnostic fails the declared coverage threshold.
This is a retrospective structural follow-up to GDT872, not semantic evidence.

## Results

| View | Eligible anchors | Matched | Physical folios | Coverage | Unique controls |
| --- | ---: | ---: | ---: | --- | ---: |
| Primary ZL | 82 | 41 (50%) | 29 | PASS | 337 |
| All-traversed-lines identical readings | 3 | 1 (33.3%) | 1 | FAIL | 1 |

D = F_CH − F_SH − B_CH + B_SH, with each component a response-hit rate per
eligible offset. These are equal-anchor means, not conditional CH shares among
hits and not the original GDT872 endpoint.

| Primary population | F_CH | F_SH | B_CH | B_SH | D |
| --- | ---: | ---: | ---: | ---: | ---: |
| All 82 eligible anchors | .065041 | .017276 | .073171 | .041667 | .016260 |
| Same 41 matched anchors | .056911 | .024390 | .069106 | .036585 | .000000 |
| Their equally weighted control-pool means | .046804 | .022967 | .068065 | .033261 | −.010967 |
| Matched anchor minus its control-pool mean | .010107 | .001423 | .001040 | .003324 | .010967 |

The positive D of all eligible anchors is already absent in the matched subset
before control subtraction. Thus this does not establish that position explains
the original GDT872 composition observation, or even the full eligible population.
The matched residual is about 1.10 percentage points; physical-folio residuals
have 15 negative, 12 positive and 2 zero signs. This is not a significance test.
Overlapping windows and reused controls are not independent replications.

The diagnostic matched anchor has D=0, its single control D=1/6, and residual
−1/6. One matched case cannot support a diagnostic population conclusion.
ZL, IT and RF remain alternate readings of one manuscript.

## Decision and limits

Stop this position-control branch. No anchor state, procedure, operand, reset,
translation or causal position explanation is established. Do not expand forms,
lags or models, coarsen matching, or relax reading agreement to repair coverage.
Only half the primary eligible anchors match, and paragraph flags are source
structure, not established semantic boundaries. This result does not falsify
all possible semantic uses of these forms.

## Reproduction and validation

Preregistration and locked source were published in eab3abce before the count.
Run `python experiments/yolo/gdt872_whole_pair_directed_profile/src/run.py` first
if its ignored guarded runtime projections are absent. Then run this directory's
`src/run.py` and `src/validate.py`. No new transcription or image admission is used.
The source receipt binds the guarded input bytes and their upstream provenance.

Independent exhaustive center/mask/control-pool and metric validation passes:
16,659 center profiles and 85 anchor profiles across the two views. The validator
also checks an analytically specified synthetic fixture with 13 controls and
reading-disagreement isolation. This validates computation, not interpretation.
See `artifacts/RESULT.json`, `ANCHOR_MATCHES.json`, `CONTROL_CELLS.json`,
`SOURCE_RECEIPT.json` and `VALIDATION.json` for exact values and hashes.
