# GDT284 — wrapper positional-profile architecture calibration

Status: **VOYNICH_POSITIONAL_PROFILE_DISTINCT_IN_CURRENT_CONTROLS**.

## Standard held-folio fingerprint

| panel | architecture | capacity | initial | internal | final | EOS | sign | distance |
|---|---|---|---:|---:|---:|---:|---|---:|
| ORDINARY_NATURAL_LANGUAGE | REAL_NATURAL_LANGUAGE | UNSCORED_NO_CONTEXT_REUSE | +0.0000 | +0.0000 | +0.0000 | +0.0000 | UNSCORED | 0.1860 |
| ABBREVIATION_HEAVY_MEDIEVAL | REAL_DIPLOMATIC_ABBREVIATION | UNSCORED_NO_CONTEXT_REUSE | +0.0000 | +0.0000 | +0.0000 | +0.0000 | UNSCORED | 0.1860 |
| LEARNED_ABBREVIATION_MAP | GENERATED_HISTORICALLY_LEARNED_ABBREVIATION | UNSCORED_NO_WRAPPER_CAPACITY | +0.0000 | +0.0000 | +0.0000 | +0.0000 | UNSCORED | 0.1860 |
| LEARNED_ABBREVIATION_SAMPLED | GENERATED_HISTORICALLY_LEARNED_ABBREVIATION | UNSCORED_NO_WRAPPER_CAPACITY | +0.0000 | +0.0000 | +0.0000 | +0.0000 | UNSCORED | 0.1860 |
| AUGSBURG_ACCOUNTS_1402_1424 | REAL_STRUCTURED_NATURAL_LANGUAGE | SCORED | +0.0266 | +0.0110 | +0.0038 | -0.0035 | +++- | 0.1594 |
| ARBITRARY_LOCAL_CODEBOOK | SYNTHETIC_LEXICAL_CODEBOOK | SCORED | -0.0286 | +0.0152 | +0.0096 | -0.0164 | -++- | 0.2099 |
| COMPOSITIONAL_TECHNICAL_NOTATION | SYNTHETIC_FACTORIAL_TECHNICAL_NOTATION | SCORED | -0.0255 | -0.0128 | -0.0045 | -0.0187 | ---- | 0.2090 |
| HYBRID_SHORTHAND | SYNTHETIC_HUMAN_GROWN_HYBRID | SCORED | +0.0495 | +0.0167 | +0.0199 | -0.0107 | +++- | 0.1418 |
| LATIN_SCHOLASTIC_GRAPHEMATIC | REAL_DIPLOMATIC_ABBREVIATION | SCORED | +0.1352 | +0.0367 | +0.0180 | +0.0221 | ++++ | 0.0935 |
| LATIN_MEDICAL_GRAPHEMATIC | REAL_DIPLOMATIC_ABBREVIATION | SCORED | +0.1037 | +0.0390 | +0.0091 | +0.0219 | ++++ | 0.1055 |
| LATIN_15C_GRAPHEMATIC | REAL_DIPLOMATIC_ABBREVIATION | SCORED | +0.0627 | +0.0343 | +0.0092 | +0.0164 | ++++ | 0.1335 |
| VOYNICH_REFERENCE | UNKNOWN_VOYNICH_ARCHITECTURE | SCORED | +0.1727 | +0.0385 | -0.0392 | -0.0416 | ++-- | 0.0000 |

Voynich exact standard sign pattern: `++--`.  Matching scored controls: none.  Matching architecture categories: none.

The three nearest scored standard vectors are: LATIN_SCHOLASTIC_GRAPHEMATIC (0.0935), LATIN_MEDICAL_GRAPHEMATIC (0.1055), LATIN_15C_GRAPHEMATIC (0.1335).

## Unseen-host sensitivity

After every exact host identity in the target bucket is excluded from training, Voynich changes to `++++`.  That sign pattern is shared by AUGSBURG_ACCOUNTS_1402_1424, LATIN_SCHOLASTIC_GRAPHEMATIC, LATIN_MEDICAL_GRAPHEMATIC, LATIN_15C_GRAPHEMATIC.  Its nearest nested vectors are HYBRID_SHORTHAND (0.2232), LATIN_15C_GRAPHEMATIC (0.2405), LATIN_SCHOLASTIC_GRAPHEMATIC (0.2467).  Thus the standard `++--` fingerprint is distinct in this panel, but its terminal-negative half does **not** transfer to unseen host identities.

## Interpretation

The learned-abbreviation outputs are an observation-layer capacity result, not a failed positional profile: the frozen parser assigns them no wrapper contrast. The ordinary and diplomatic Nuremberg overlays have no context reuse under this exact instrument and are also capacity-unscored. Exact component vectors, nested sensitivities, nulls and distances are exported in the TSVs. No fitted classifier or post-score rescaling is used.

## Claim ceiling

This only calibrates the positional shape of opaque wrapper-conditioned character compression. It establishes no morphology, abbreviation mechanism, lexical identity, language, meaning, plaintext, or translation. No f84 row was opened, parsed, retained, joined, or scored.
