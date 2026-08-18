# GDT280 — fine decomposition of the edge compiler

Status: **VOYNICH_EDGE_PROFILE_DIFFERS_FROM_LATIN_RIGHT_FAMILY_LEAD**.

The GDT279 panel, views, endpoint, null and full compiler model remain frozen. This pass allocates only the incremental edge signal over the fixed opportunity-plus-closure base.

## Native-order primary profiles

| panel | outer wrapper | local frame | right family | display renderer | edge increment | leader |
|---|---:|---:|---:|---:|---:|---|
| LATIN_SCHOLASTIC_GRAPHEMATIC | +0.1768 | +0.0386 | +0.2217 | +0.0024 | +0.4395 | RIGHT_FAMILY |
| LATIN_MEDICAL_GRAPHEMATIC | +0.1248 | +0.0357 | +0.1812 | +0.0108 | +0.3525 | RIGHT_FAMILY |
| LATIN_15C_GRAPHEMATIC | +0.1289 | +0.0523 | +0.1458 | +0.0008 | +0.3278 | RIGHT_FAMILY |
| VOYNICH_REFERENCE | +0.1702 | +0.0858 | +0.0318 | -0.0194 | +0.2684 | OUTER_WRAPPER |

## Exact matched-source layout bridge

| panel | view | outer wrapper | local frame | right family | display renderer |
|---|---|---:|---:|---:|---:|
| LATIN_MEDICAL_GRAPHEMATIC | LENGTH_MATCHED_OVERLAY | +0.0057 | -0.0009 | +0.0456 | +0.0016 |
| LATIN_MEDICAL_GRAPHEMATIC | MATCHED_SAMPLE_NATIVE_LAYOUT | +0.0329 | +0.0028 | +0.1298 | -0.0031 |
| LATIN_15C_GRAPHEMATIC | LENGTH_MATCHED_OVERLAY | +0.0271 | +0.0075 | +0.0469 | -0.0019 |
| LATIN_15C_GRAPHEMATIC | MATCHED_SAMPLE_NATIVE_LAYOUT | +0.0907 | +0.0334 | +0.1467 | +0.0009 |
| VOYNICH_REFERENCE | LENGTH_MATCHED_OVERLAY | +0.2144 | +0.0433 | +0.0135 | -0.0136 |
| VOYNICH_REFERENCE | MATCHED_SAMPLE_NATIVE_LAYOUT | +0.2144 | +0.0433 | +0.0135 | -0.0136 |

## Representation-safe sensitivity

| panel | outer wrapper | local frame | right family | display renderer | leader |
|---|---:|---:|---:|---:|---|
| LATIN_SCHOLASTIC_GRAPHEMATIC | +0.2775 | +0.0339 | +0.3480 | -0.0081 | RIGHT_FAMILY |
| LATIN_MEDICAL_GRAPHEMATIC | +0.1819 | +0.0189 | +0.3321 | -0.0007 | RIGHT_FAMILY |
| LATIN_15C_GRAPHEMATIC | +0.2014 | +0.0523 | +0.2125 | -0.0003 | RIGHT_FAMILY |
| VOYNICH_REFERENCE | +0.0809 | +0.0268 | -0.0099 | -0.0660 | OUTER_WRAPPER |

The winner labels are stable, but the magnitudes are not symmetric. Voynich's native edge increment falls from **+.2684** published to **+.0319** bits/event LOFO-safe, whereas the three Latin right-family edge increments remain large or grow (**+.6513, +.5322, +.4659**). Thus `OUTER_WRAPPER` is the surviving Voynich direction among these four blocks, not a stable effect comparable in magnitude to the Latin right-family channel.

All Latin `DISPLAY_RENDERER` fields are constant `NONE`. Their tiny nonzero Shapley values expose the fixed 256-bucket approximation: adding a constant tuple coordinate can reassign hash collisions. The right-family leads are much larger and representation-stable, but exact fine-component magnitudes still include this bounded collision noise.

## Interpretation

The leading component identifies where this fixed character compressor finds reusable edge-conditioned form. It does not give that component a linguistic function. The Latin controls have a robust right-edge-family architecture; Voynich does not share it. Voynich's weaker leakage-safe outer-wrapper lead is a distinct residual, not evidence that q or another wrapper is a linguistic prefix. A separately frozen collision sensitivity is required before treating the fine allocations as intrinsic values.

Every FULL_EDGE observed score and published null world reproduces GDT279. No f84 source was opened, parsed, retained, joined, or scored.
