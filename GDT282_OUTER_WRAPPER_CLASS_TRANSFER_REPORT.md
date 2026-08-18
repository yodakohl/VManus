# GDT282 — outer-wrapper class transfer

Status: **OUTER_WRAPPER_IDENTITY_TRANSFERS_ACROSS_REGISTERS**.

The collision-free GDT281 wrapper direction is decomposed without inspecting PAGE_HOST substrings. Scores below are base-minus-model bits/event; positive is better.

## Voynich transfer

| regime | presence | q binary | full identity | identity beyond presence |
|---|---:|---:|---:|---:|
| PUBLISHED_HELD_FOLIO | +0.0668 | +0.0279 | +0.1305 | +0.0637 |
| LOFO_SAFE_HELD_FOLIO | +0.0913 | +0.0402 | +0.1927 | +0.1014 |
| HELD_SECTION_PUBLISHED | +0.0101 | +0.0078 | +0.0255 | +0.0154 |
| HELD_HAND_PUBLISHED | +0.0023 | +0.0042 | +0.0108 | +0.0084 |

Full wrapper identity is positive in **5/6** held sections and **3/4** powered held hands. Hand `@` is descriptive only.

## Native Latin calibration

| panel | published presence | published full | safe presence | safe full |
|---|---:|---:|---:|---:|
| LATIN_SCHOLASTIC_GRAPHEMATIC | +0.1591 | +0.2120 | +0.1792 | +0.2493 |
| LATIN_MEDICAL_GRAPHEMATIC | +0.1239 | +0.1736 | +0.1314 | +0.1612 |
| LATIN_15C_GRAPHEMATIC | +0.1123 | +0.1226 | +0.1186 | +0.1344 |

## One-vs-rest class probes

| class | published | safe folio | held section | held hand |
|---|---:|---:|---:|---:|
| NONE | +0.0668 | +0.0913 | +0.0101 | +0.0023 |
| q | +0.0279 | +0.0402 | +0.0078 | +0.0042 |
| ch | -0.0276 | -0.0105 | -0.0021 | -0.0014 |
| d | +0.0436 | +0.0533 | +0.0024 | -0.0002 |
| sh | +0.0538 | +0.0658 | +0.0192 | +0.0091 |
| che | -0.0099 | -0.0008 | -0.0003 | -0.0006 |
| t | -0.0018 | +0.0026 | -0.0026 | -0.0013 |
| s | -0.0096 | -0.0053 | -0.0030 | -0.0006 |

These eight probes are exhaustive but nonadditive. The initial unique-rename diagnostic was a bijection and is explicitly discarded in the method and counterexamples.

## Frozen gates

- `all_three_total_positive`: **PASS**
- `identity_beyond_presence_all_three`: **PASS**
- `sections_positive_at_least_4_of_6`: **PASS**
- `hands_positive_at_least_3_of_4`: **PASS**
- `q_redundancy_exact`: **PASS**

`q_flag` is a deterministic duplicate of `wrapper=q`; the exact full-plus-q model equals full wrapper identity and is not evidence for a separate q dimension.

## Claim ceiling

At most this establishes a transferable opaque wrapper-class character channel. It does not identify prefix morphology, abbreviation, a linguistic function, sound, language, code, notation, meaning, plaintext, or translation. No f84 row was opened, parsed, retained, joined, or scored.
