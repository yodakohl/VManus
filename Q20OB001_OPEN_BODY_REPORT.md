# Q20OB001 OPEN-to-BODY predictive dependence report

Status: **OPEN_BODY_DEPENDENCE_NOT_ABOVE_MATCHED_CONTROLS**

The frozen test used 170 clean star-delimited units on eight physical folios.
Each folio was held out once. ZL3b, IT2a, and RF1b were scored as alternate
reading sensitivities, not independent samples. f84r remained excluded.

## Held-folio OPEN increment

Positive gain means the unit's own OPEN improved BODY prediction above a
training-folio string model already augmented by the vocabulary of every other
BODY record on the held folio.

| reading | representation | true gain bits | gain/member | null median/member | local p | maxT p | positive folios |
|---|---|---:|---:|---:|---:|---:|---:|
| ZL3b | MEMBER | +0.000 | +0.000000 | +0.000000 | 1.000000 | 1.000000 | 0/8 |
| ZL3b | FAMILY | +0.000 | +0.000000 | +0.000000 | 1.000000 | 1.000000 | 0/8 |
| ZL3b | GROUP | +0.000 | +0.000000 | +0.000000 | 1.000000 | 1.000000 | 0/8 |
| IT2a | MEMBER | +0.000 | +0.000000 | +0.000000 | 1.000000 | 1.000000 | 0/8 |
| IT2a | FAMILY | +0.000 | +0.000000 | +0.000000 | 1.000000 | 1.000000 | 0/8 |
| IT2a | GROUP | +0.000 | +0.000000 | +0.000000 | 1.000000 | 1.000000 | 0/8 |
| RF1b | MEMBER | +0.000 | +0.000000 | +0.000000 | 1.000000 | 1.000000 | 0/8 |
| RF1b | FAMILY | +0.000 | +0.000000 | +0.000000 | 1.000000 | 1.000000 | 0/8 |
| RF1b | GROUP | +0.000 | +0.000000 | +0.000000 | 1.000000 | 1.000000 | 0/8 |

The primary ZL3b MEMBER endpoint has **+0.000**
bits of gain (+0.000000 per BODY
member), versus matched-null median
**+0.000000**. Its local
permutation p is **1.000000** and the
three-representation maxT p is
**1.000000**. Exact-length
permutation capacity is ZL/IT/RF
**124/126/122**
of 170 records.

The own-OPEN weight is nonzero in **0/8**
ZL folds, and **0/8** held folios have a
positive primary gain. The deterministic previous-compatible-OPEN gain is
**+0.000** bits.

## Baselines and interpretation

Training-only order-2 character/member and family models, an exact whole-group
dictionary with character escape, the other-BODY held-folio vocabulary cache,
and a separate BODY length/shape KT baseline are all published fold by fold.
The aggregate ZL member-string baseline is
**3.032821**
bits per BODY member. Both the fitted other-BODY cache and own-OPEN cache select
zero weight in all eight primary folds, so neither improves that baseline.
The permutation keeps BODY, folio, exact OPEN member count, total record member
length, and local vocabulary fixed. Singleton length strata contribute no
pairing evidence.

This experiment tests only whether the particular first line carries
transferable formal information about its later lines. `OPEN` and `BODY` are
positional names. The nonconfirmation applies only to the registered direct
MEMBER/FAMILY/GROUP cache family; it does not exclude every nonlinear
OPEN-to-BODY relation. No recipe, header, title, semantic field, language,
word class, plaintext, meaning, or translation follows.
