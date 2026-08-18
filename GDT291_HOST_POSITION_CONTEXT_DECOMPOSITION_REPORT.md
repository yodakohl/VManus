# GDT291 — host-position omitted-context decomposition

Status: **HOST_POSITION_EFFECT_REDUCED_BUT_REMAINS**.

## Held-folio nested increments

| panel | record | nonwrapper compiler | exact host rich | host×position rich | exact host shape | host×position shape |
|---|---:|---:|---:|---:|---:|---:|
| AUGSBURG_ACCOUNTS_1402_1424 | +0.0125 | +0.0119 | +0.0184 | -0.0024 | +0.0405 | +0.0000 |
| ARBITRARY_LOCAL_CODEBOOK | -0.0072 | -0.0124 | +0.0238 | -0.0154 | +0.0148 | -0.0156 |
| COMPOSITIONAL_TECHNICAL_NOTATION | +0.0018 | -0.0051 | +0.0395 | +0.0302 | +0.0217 | +0.0320 |
| HYBRID_SHORTHAND | -0.0101 | +0.0037 | +0.0094 | +0.0263 | -0.0019 | +0.0284 |
| LATIN_SCHOLASTIC_GRAPHEMATIC | -0.0061 | +0.1091 | -0.1141 | -0.0395 | -0.0112 | -0.0204 |
| LATIN_MEDICAL_GRAPHEMATIC | -0.0041 | +0.1171 | -0.1187 | -0.0380 | -0.0127 | -0.0203 |
| LATIN_15C_GRAPHEMATIC | +0.0097 | +0.0743 | -0.0648 | -0.0247 | +0.0020 | -0.0104 |
| VOYNICH_REFERENCE | +0.0102 | +0.0033 | +0.1228 | +0.0286 | +0.1326 | +0.0344 |

The target-history-free Voynich shape anchor is +0.0344 bits/event; after record and all frozen non-wrapper compiler coordinates the residual host×position increment is +0.0286.

## Voynich sensitivities

- HELD_PHYSICAL_FOLIO prior=5.0: rich host×position +0.0059; shape anchor +0.0100.
- HELD_PHYSICAL_FOLIO prior=22.0: rich host×position +0.0404; shape anchor +0.0474.
- HELD_SECTION prior=11: rich host×position +0.0274; shape anchor +0.0274.
- HELD_HAND prior=11: rich host×position +0.0252; shape anchor +0.0252.

In the whole-section and whole-hand splits, the richer record/compiler keys contain the held identifier and therefore have no exact training support; their increments are exactly zero by hierarchical backoff. Those sensitivities test the residual host layers only and are not evidence that record/compiler context is neutral across registers.

## Claim ceiling

This localizes a formal wrapper interaction only. It cannot establish lexical class, morphology, grammar function, abbreviation, sound, language, meaning, plaintext, or translation. No f84 row was opened, parsed, retained, joined, or scored.
