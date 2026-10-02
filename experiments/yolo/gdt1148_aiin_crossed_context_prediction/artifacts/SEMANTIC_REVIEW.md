# GDT1148 scoped inference review

The registered `NO_JOINT_TRANSFER` decision follows the fixed gate. The primary
effect is the leaf-macro gain of the combined left/right context predictor over
the baseline; each stratum also needs its stated capacity in both ZL3b and
IT2a and at least 0.01 gain in each. Capacity is met, but the fixed combined
gain is below 0.01 for both strata in both deciding readings:

| Stratum | ZL3b | IT2a | RF1b descriptive |
|---|---:|---:|---:|
| Bare | 0.001951 | 0.001210 | 0.002101 |
| Nonbare | -0.000049 | 0.001434 | 0.000965 |

Thus both strata are `NO_MATERIAL_TRANSFER`, yielding `NO_JOINT_TRANSFER`.
Small positive gains on an individual side, event-macro scores, or accuracy do
not replace the preregistered combined leaf-macro gate. The RF results remain
descriptive; ZL3b, IT2a and RF1b are alternate readings of one manuscript, not
independent replications.

The inference claim remains appropriately narrow. The predictor tests exact
pure-spelling `ain`/`aiin` tail classes, while withholding the target's entire
orthographic prefix and every physical leaf in its modulo-five fold from
training. Adjacent `ain`/`aiin`-family neighbours, including `aiiin`, are
masked as contexts. This limits direct prefix, leaf and serial-tail reuse.
It does not establish an argument function, number, conjunction scope,
lexical meaning, or any relation between the observed tail classes and a
semantic category. `aiiin` is separately inventoried and unscored; the binary
outcome does not imply a numeric ladder.

The negative applies to this encoding, smoothing, and immediate whole-word
context model. It does not establish that all grammar or context predictors
fail. Coverage merits explicit caution: each bare stratum has only one prefix
(the empty prefix) and strongly imbalanced outcomes (ain 82–110 versus aiin
389–436 across readers). Since the empty prefix is withheld as a whole family,
bare predictions transfer from nonbare training cases rather than measuring
within-bare-prefix learning. Only 79–133 bare events per reader have an
eligible left context and 152–170 have an eligible right context. These
limitations do not reverse the fixed result, but event totals alone overstate
how often a usable context contributed. No significance, semantic probability,
meaning confirmation, or independent confirmation is claimed.
