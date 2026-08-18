# GDT286 — opaque host-to-wrapper transfer

Status: **WRAPPER_CONTEXT_CONDITIONED_HOST_VARIANT**.

## Held-folio scores

| panel | coverage | host gain | above null | host×position | null mobile | max8 p |
|---|---:|---:|---:|---:|---:|---:|
| AUGSBURG_ACCOUNTS_1402_1424 | 0.905 | +0.0455 | +0.0001 | +0.0003 | 76/8448 | 0.9692 |
| ARBITRARY_LOCAL_CODEBOOK | 0.570 | +0.0233 | +0.0002 | -0.0154 | 975/8448 | 1.0000 |
| COMPOSITIONAL_TECHNICAL_NOTATION | 0.569 | +0.0298 | +0.0029 | +0.0321 | 958/8448 | 0.1538 |
| HYBRID_SHORTHAND | 0.551 | +0.0120 | -0.0001 | +0.0283 | 928/8448 | 1.0000 |
| LATIN_SCHOLASTIC_GRAPHEMATIC | 0.772 | -0.0127 | +0.0001 | -0.0208 | 779/8448 | 0.9692 |
| LATIN_MEDICAL_GRAPHEMATIC | 0.625 | -0.0123 | +0.0004 | -0.0203 | 869/8448 | 0.8308 |
| LATIN_15C_GRAPHEMATIC | 0.584 | +0.0025 | +0.0005 | -0.0102 | 1113/8448 | 0.3692 |
| VOYNICH_REFERENCE | 0.907 | +0.1298 | +0.0123 | +0.0320 | 411/8448 | 0.0154 |

Voynich held-section exact-host gain: +0.4224 bits/event; held-hand gain: +0.4131. The exact null changes only 411/8448 Voynich IDs in world 0; the observed host gain exceeds the high null mean by +0.0123 bits/event. This is a low-mobility identity-alignment calibration.

## Frozen gates

- `held_folio_exact_host_gain_positive`: **PASS**
- `max8_p_le_0_05`: **PASS**
- `host_position_increment_nonpositive`: **FAIL**
- `held_section_or_hand_gain_positive`: **PASS**

## Claim ceiling

This distinguishes an opaque host-class association from a position-conditioned association only. It establishes no lexical class, morphology, abbreviation, sound, language, meaning, plaintext, or translation. No f84 row was opened, parsed, retained, joined, or scored.
