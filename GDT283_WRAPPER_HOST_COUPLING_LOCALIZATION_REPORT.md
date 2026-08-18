# GDT283 — wrapper/host coupling localization

Status: **WRAPPER_CHANNEL_SURVIVES_UNSEEN_HOST_TYPES_AND_INTERNAL_POSITIONS**.

## Summary

| panel | standard gain | unseen-host gain | unseen internal | positive buckets | local p | max4 p |
|---|---:|---:|---:|---:|---:|---:|
| LATIN_SCHOLASTIC_GRAPHEMATIC | +0.2120 | +0.3386 | +0.0373 | 8/8 | 0.0154 | 0.0154 |
| LATIN_MEDICAL_GRAPHEMATIC | +0.1736 | +0.2775 | +0.0401 | 8/8 | 0.0154 | 0.0154 |
| LATIN_15C_GRAPHEMATIC | +0.1226 | +0.1936 | +0.0344 | 8/8 | 0.0154 | 0.0154 |
| VOYNICH_REFERENCE | +0.1305 | +0.3152 | +0.0501 | 8/8 | 0.0154 | 0.0154 |

## Positional fingerprints

| panel | mode | initial | internal | final | EOS | total |
|---|---|---:|---:|---:|---:|---:|
| LATIN_SCHOLASTIC_GRAPHEMATIC | STANDARD_HELD_FOLIO | +0.1352 | +0.0367 | +0.0180 | +0.0221 | +0.2120 |
| LATIN_SCHOLASTIC_GRAPHEMATIC | NESTED_UNSEEN_HOST_BUCKET | +0.0868 | +0.0373 | +0.0322 | +0.1823 | +0.3386 |
| LATIN_MEDICAL_GRAPHEMATIC | STANDARD_HELD_FOLIO | +0.1037 | +0.0390 | +0.0091 | +0.0219 | +0.1736 |
| LATIN_MEDICAL_GRAPHEMATIC | NESTED_UNSEEN_HOST_BUCKET | +0.0413 | +0.0401 | +0.0235 | +0.1726 | +0.2775 |
| LATIN_15C_GRAPHEMATIC | STANDARD_HELD_FOLIO | +0.0627 | +0.0343 | +0.0092 | +0.0164 | +0.1226 |
| LATIN_15C_GRAPHEMATIC | NESTED_UNSEEN_HOST_BUCKET | +0.0366 | +0.0344 | +0.0211 | +0.1015 | +0.1936 |
| VOYNICH_REFERENCE | STANDARD_HELD_FOLIO | +0.1727 | +0.0385 | -0.0392 | -0.0416 | +0.1305 |
| VOYNICH_REFERENCE | NESTED_UNSEEN_HOST_BUCKET | +0.2556 | +0.0501 | +0.0045 | +0.0050 | +0.3152 |

Voynich differs visibly from all three Latin controls in the standard endpoint: its wrapper channel is strongly initial and modestly internal, but final-character and EOS contributions are negative. The Latin wrapper channels are positive at all four positions. This makes the Voynich coupling less consistent with the calibrated Latin abbreviation edge profile, even though it is not confined to the first character.

## Frozen gates

- `nested_total_positive`: **PASS**
- `nested_internal_positive`: **PASS**
- `positive_buckets_at_least_6_of_8`: **PASS**
- `matched_null_max4_p_le_0_05`: **PASS**

The nested endpoint excludes all exact PAGE_HOST identities in each target host bucket from training but uses the frozen published parser. The matched null preserves section, Currier, hand, position, host length and first host character.

## Claim ceiling

At most this localizes an opaque same-group wrapper/host form coupling. It does not establish productive morphology, abbreviation, lexical identity, function, sound, language, meaning, plaintext, or translation. No f84 row was opened, parsed, retained, joined, or scored.
