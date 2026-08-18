# GDT285 — exact-host reuse and terminal localization

Status: **TERMINAL_PENALTY_REQUIRES_EXACT_HOST_REUSE**.

## Recurrent-host endpoint

| panel | recurrent events | standard onset | standard terminal | exact-excluded onset | exact-excluded terminal | matched-excluded terminal |
|---|---:|---:|---:|---:|---:|---:|
| LATIN_SCHOLASTIC_GRAPHEMATIC | 6524 | +0.1958 | +0.0516 | +0.1315 | +0.2863 | +0.0501 |
| LATIN_MEDICAL_GRAPHEMATIC | 5282 | +0.1818 | +0.0497 | +0.0923 | +0.3302 | +0.0484 |
| LATIN_15C_GRAPHEMATIC | 4933 | +0.1252 | +0.0448 | +0.0959 | +0.2099 | +0.0445 |
| VOYNICH_REFERENCE | 7661 | +0.1863 | -0.0840 | +0.2945 | +0.0190 | -0.0850 |

## Frozen gates

- `standard_recurrent_terminal_lt_zero`: **PASS**
- `exact_excluded_recurrent_terminal_gte_zero`: **PASS**
- `exact_terminal_improvement_gt_matched_terminal_improvement`: **PASS**
- `exact_excluded_recurrent_onset_body_gt_zero`: **PASS**

The five recurrence bins, every held folio, and the exact donor-tier capacity are exported. Standard all-event component scores reproduce GDT284 exactly. The Voynich matched control removes exactly 306525 events across target-host/fold cases; tier counts are `[83033, 19200, 24064, 24674, 155554]`, so 50.7% use the coarsest any-nonhost fallback. Equal removal volume is exact, but opportunity matching is not uniformly exact. Ordinary past-within-page held history remains available in all modes.

## Claim ceiling

At most this localizes an opaque wrapper-conditioned terminal penalty to reuse of exact parsed host identities in this scorer. It establishes no morphology, abbreviation, lexicon, sound, language, meaning, plaintext, or translation. No f84 row was opened, parsed, retained, joined, or scored.
