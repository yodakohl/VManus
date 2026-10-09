# GDT1230 — one-previous-source-letter alphabets excluded for all four fixed source cases

**ALL_FOUR_SOURCE_CASES_EXCLUDED_ALL_READINGS.** The empirical bound excludes every fixed previous-source-letter permutation table for the unchanged full bare Deot projection under both declared reset conventions and both source-word orientations. No source writer, ring order or glyph key was searched. The weakest exclusion margin is0.060485718bits beyond even the most generous scored nativeH2+0.30ceiling. This is an operational source/model-family result, not a language exclusion or a Voynich reading.

For a uniformly selected within-word output-pair position, let Xbe the current source letter, Pthe preceding one, and Qthe state used beforeP(or the public reset sentinel). The two output signs are Y=f_P(X), Z=f_Q(P). With only that state and a bijection in each row,

`H(Y|Z) >= H(Y|Z,P,Q) = H(Y|P,Q) = H(X|P,Q)`.

The last expression depends only on the source and declared resets, not on the unknown output tables. The producer independently checked this proof before any new source counts. Root independently validated the numerical count certificates; no human usability or historical attestation follows from either check.

| Source orientation | Reset | Empirical lower bound | Margin beyond greatest allowedH2: IT / RF / ZL |
|---|---|---:|---:|
| Logical | paragraph | 2.839332740 | 0.217643699 / 0.231441355 / 0.254768105 |
| Logical | word | 2.717874254 | 0.096185212 / 0.109982869 / 0.133309619 |
| Reverse each source word | paragraph | 2.867571056 | 0.245882014 / 0.259679671 / 0.283006421 |
| Reverse each source word | word | 2.682174759 | 0.060485718 / 0.074283374 / 0.097610124 |

The source has6288words,24668letters and18380within-word pairs. All four cases count every first word pair and every repeated occurrence separately. Under paragraph reset71pairs have a reset context; under word reset6218do. The70one-letter words contribute no own pair but still update a carried paragraph state. They were not discarded. Native summaries are unchanged1228: largest observedH2is2.321689042 IT,2.307891385 RF and2.284564635 ZL; adding the fixed0.30allowance gives the compared ceilings. Every reading has8scoreable cells and1024dependent samples. The18smaller reader/cell combinations remain untested.

These four cases reverse source words before writing where declared. They are not an assertion that reversing an already encoded word gives the same model. Physical wrapping may occur between whole groups but never resets state or changes scored words; this source's maximum12letters fits the24cell convention. The theorem does not cover extra counters, prior-output state, word identity, longer source histories, position-dependent rows, line resets, character expansion/contraction, noninjective spelling or altered word boundaries. It does not establish a universal minimum amount of writer memory.

Validation rebuilds the projection from all7rawchapter files, reconstructs four complete source-context count tables using a separate flat-offset traversal, checks the source/section/pair totals and all cached native ceilings. Joint-minus-context floating-point entropy and50-digit Decimal logarithms agree with the runner's conditional-frequency formula. Exhaustive two-letter permutation fixtures satisfy the bound; a noninjective constant-output null violates it, demonstrating the essential assumption. All checks pass. No new native query, image, reserve or semantic assignment occurred.

Decision: do not implement or optimize a fixed ring or arbitrary one-previous-decoded-letter row tables for this projection under these four contracts. GDT1217's original expanded-German-source failure remains; its reconsider diagnostic did not reopen that fixed model. GDT1180,1228and1229remain separate closed results. A genuinely different writing operation or source requires its own motivation and contract, not an automatic extension to more state. Local4October checkpoint; no public release.
