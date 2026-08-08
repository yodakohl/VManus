# Typology-neutral structure audit

No European word class, plaintext language, cipher, or image is assumed. Odd folios discover; even folios confirm.

## Orthographic hierarchy

Only visible spaces that would produce the same monotone-unit cut if deleted are compared with internal unit joins.

| edition | internal joins / compatible spaces | compatible/all spaces | form AUC | + root AUC | page root increment / p |
|---|---:|---:|---:|---:|---:|
| ZL3b | 11585/22430 | 75.3% | 0.868 | 0.945 | +0.081 / 0.000020 |
| IT2a | 11947/22382 | 76.0% | 0.871 | 0.949 | +0.083 / 0.000020 |
| RF1b | 11322/22070 | 73.0% | 0.856 | 0.939 | +0.086 / 0.000020 |

Visible spaces are therefore a real hierarchical boundary, not merely optional separators between monotone units. This still does not prove that a visible token equals a European-style word.

## Productive combination

| edition | multi-unit raw / edge-stripped | unseen held tokens | rebuilt from seen units | rebuilt from seen root+form pieces | roots for 80/90% | forms for 80/90% |
|---|---:|---:|---:|---:|---:|---:|
| ZL3b | 39.4%/30.1% | 10.6% | 75.1% | 91.7% | 15/24 | 8/14 |
| IT2a | 41.2%/31.5% | 11.3% | 73.3% | 90.9% | 15/24 | 8/14 |
| RF1b | 36.5%/27.8% | 10.4% | 74.3% | 91.7% | 15/24 | 8/14 |

This is compatible with productive/agglutinative or deliberately compositional construction. It rejects an analysis in which every visible token is an unrelated opaque codeword.

## Stable page information by scale

Selection criterion: same-page reciprocal-rank gain over chance on ZL3b odd folios, corrected over all eight representations.

| representation | discovery MRR / chance | held MRR / chance | held top-1 / chance | held cosine margin |
|---|---:|---:|---:|---:|
| ATOM1 | 0.702/0.215 | 0.629/0.213 | 48.4%/7.6% | +0.062 |
| ATOM2 | 0.617/0.215 | 0.642/0.213 | 52.7%/7.6% | +0.123 |
| ATOM3 | 0.528/0.215 | 0.542/0.213 | 38.6%/7.6% | +0.127 |
| CANON_WORD | 0.456/0.215 | 0.472/0.213 | 28.8%/7.6% | +0.074 |
| UNIT | 0.510/0.215 | 0.563/0.213 | 41.3%/7.6% | +0.110 |
| ROOT | 0.498/0.215 | 0.462/0.213 | 29.9%/7.6% | +0.076 |
| FORM | 0.456/0.215 | 0.488/0.213 | 35.3%/7.6% | +0.037 |
| ROLE_ROOT | 0.531/0.215 | 0.551/0.213 | 40.8%/7.6% | +0.120 |

Frozen winner: **ATOM1**; discovery family p=0.000020.

| confirmation edition | MRR / chance | top-1 / chance | RR-gain p |
|---|---:|---:|---:|
| ZL3b | 0.629/0.213 | 48.4%/7.6% | 0.000020 |
| IT2a | 0.642/0.213 | 50.5%/7.6% | 0.000020 |
| RF1b | 0.633/0.213 | 48.9%/7.6% | 0.000020 |

Held cosine-margin increment over root-free FORM:

| edition | ROOT | UNIT | ROLE_ROOT | ATOM2 | ATOM3 |
|---|---:|---:|---:|---:|---:|
| ZL3b | +0.039 (p=0.000020) | +0.073 (p=0.000020) | +0.083 (p=0.000020) | +0.086 (p=0.000020) | +0.090 (p=0.000020) |
| IT2a | +0.041 (p=0.000020) | +0.077 (p=0.000020) | +0.084 (p=0.000020) | +0.088 (p=0.000020) | +0.093 (p=0.000020) |
| RF1b | +0.043 (p=0.000020) | +0.075 (p=0.000020) | +0.084 (p=0.000020) | +0.091 (p=0.000020) | +0.091 (p=0.000020) |

Low-level atom distributions retrieve page identity best by rank, while units and role-tagged roots also carry a large held signal beyond root-free form. This licenses a compact compositional/page-register channel; it does not license the claim that one glyph equals one concept.

## Directional form-state grammar

Positive template gain means a held line is compressed by previous state; positive direction gain means the original order is preferred to reversing the same states.

| edition | odd→even template / direction bits per unit | even→odd template / direction |
|---|---:|---:|
| ZL3b | +0.057 / +0.113 (p≤0.000020) | +0.064 / +0.107 (p≤0.000020) |
| IT2a | +0.059 / +0.109 (p≤0.000020) | +0.065 / +0.105 (p≤0.000020) |
| RF1b | +0.054 / +0.107 (p≤0.000020) | +0.056 / +0.094 (p≤0.000020) |

ZL3b state centers (0=start, 1=end): `Q_BOUND_E` 0.39, `Q_BARE` 0.41, `BOUND_E` 0.43, `Q_BOUND_D` 0.46, `FREE_R` 0.47, `Q_REL_I` 0.47, `BOUND_D` 0.50, `Q_FREE_R` 0.50, `FREE_L` 0.52, `Q_FREE_L` 0.52, `BARE` 0.52, `REL_I` 0.55, `Q_FREE_A` 0.75, `FREE_A` 0.79.

## What the language analogies now mean

- **Hungarian/agglutinative analogy:** viable at the abstract level: reusable roots and form pieces productively recombine inside meaningful orthographic boundaries.
- **Toki Pona/compact-primitives analogy:** viable as a small high-frequency core (about 16 roots cover 80% of units), but there is also a long rare tail and strong formal morphology.
- **Japanese analogy:** stable dependent and line-final states are possible, but the entry head failed the independent topic/title test; SOV or topic-comment is not established.
- **Chinese/isolating analogy:** short recurrent units and low-level distributional content are viable; a purely isolating account is weakened by productive root/form recombination.
- **Icelandic/fusional analogy:** bundled surface forms remain possible, but the held recombination result favors at least partially separable pieces over wholly opaque inflection.
- **Language isolate or purpose-built notation:** fully viable. None of the positive results needs external cognates or European semantics.
- **Procedural/generative system:** still viable because formal-state order and atom frequencies are exceptionally strong. Structure alone is not yet proof of ordinary spoken language.

## Decision

**LAYERED_COMPOSITIONAL_SYSTEM_PASS.** The safest current object is a layered, directional, productively compositional record system. Treat lines as utterance/record units, spaces as real but non-European orthographic boundaries, and internal units/short atom sequences as the first semantic search scale.

Planted boundary AUC: 1.000; planted page top-1: 100.0%.
Runtime: **23.98 s**; no image decoded.
