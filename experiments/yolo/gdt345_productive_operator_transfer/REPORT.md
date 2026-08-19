# GDT345 — productive formal-operator transfer

Status: **LOCAL_OR_LEXICAL_OPERATOR_DEPENDENCE_ONLY**.

GDT345 formed 8,268 adjacent formal transitions from 8,448 source groups on 91 physical folios. The inventory contains 776 registered boundary-aware operators. Unlike GDT344, the target delta was never used as a predictor: each held operator was selected from source-side state and observable boundary/layout only, applied to the source, and scored against the next six-coordinate formal state.

The factorized operator model changes LOFO codelength by +371.555 bits relative to exact atomic predecessor and by +579.248 bits relative to layout. It exactly reconstructs 2209/8268 next states, versus 2202 for exact predecessor. On 1028 events whose source state and operator were individually known but whose combination was unseen in training, its gain over exact predecessor is +39.236 bits with 89 exact recoveries versus 89.

The factorized model beats exact predecessor on 57/91 physical folios. Held-category transfer is: {"HAND": {"aggregate_gain_over_exact": 495.991212627, "passes": true, "positive_categories": 4, "powered_categories": 5}, "REGISTER": {"aggregate_gain_over_exact": 465.630797426, "passes": true, "positive_categories": 4, "powered_categories": 5}, "SECTION": {"aggregate_gain_over_exact": 412.084016025, "passes": true, "positive_categories": 5, "powered_categories": 6}}. Section H, register HERBAL_A, and hand 1 are negative counterexamples. The exact-layout fixed-prediction max-two p is 0.350500366 over 7961 mobile events; the seven-hit exact-recovery advantage is not unusual under that null. Gate outcomes are {"held_transfer_families": true, "lofo_bits_over_all": true, "lofo_exact_recovery_over_all": true, "max_two_p": false, "positive_folios": true, "unseen_combo": true}.

The earlier source-relative-label diagnostic is explicitly invalidated in `CORRECTION.md`; only this common-target-value V2 result is evidence.

No semantic comparator was run. Exact joint tuples stayed opaque and atomic; PAGE_HOST was not factored; no glyph string, role, meaning, or translation was used. All f84 selectors were rejected before row parsing.
