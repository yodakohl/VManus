# GDT007 YOLO approximate physical-cut report

## Result

**WEAK_UNSTABLE_TARGET_GAP_LEAD.**

The relaxed YOLO pass produced a real exploratory signal, but not a stable
physical segmentation result. Two source-aware AI localizers marked all 34
registered cuts. They agreed within the frozen 50-pixel tolerance on 23 cuts;
both variants were retained for the other 11, yielding 45 opaque crops. Two
fresh `fork_turns=none` reviewers then scored every crop without locus,
transcription, target/control identity, or hypothesis access.

No human reviewer was used. Every localization and crop judgment is an
`AI_DIRECT_VISUAL_OBSERVATION`.

## Strongest lead

On the 23 localizer-agreement probes, the mean of the two reviewers gives:

| Quantity | Target | Control | Difference |
|---|---:|---:|---:|
| mean ordinal gap score | 1.250 | 0.818 | +0.432 |
| paired mean, 10 complete target/control pairs |  |  | +0.600 |

The exact paired sign-flip diagnostic is `p=0.1640625`. Reviewer A alone gives
`+0.326` and reviewer B `+0.538`, so this restricted surface has a consistent
direction. It is labelled **INTERESTING_EXPLORATORY_BUT_UNSTABLE**.

The lead is concentrated. The second f37v pair contributes `+3.0` and the
second f114r pair `+1.5` of the total `+6.0` paired reviewer-mean sum. Those two
pairs therefore supply 75% of the nominal agreement-surface effect.

## Full sensitivity surfaces

| Localization | Reviewer | Target − control | Paired diagnostic |
|---|---|---:|---:|
| A | A | +0.059 | 1.000 |
| A | B | +0.353 | 0.383 |
| A | mean A/B | +0.206 | 0.560 |
| B sensitivity | A | **−0.118** | 0.884 |
| B sensitivity | B | +0.529 | 0.195 |
| B sensitivity | mean A/B | +0.206 | 0.616 |
| localizer-agreement only | A | +0.326 | 0.375 |
| localizer-agreement only | B | +0.538 | 0.188 |
| localizer-agreement only | mean A/B | +0.432 | 0.164 |

The reviewer-mean full-panel effect happens to be `+0.206` under either
localizer surface, but the individual surfaces do not retain one direction.
No paired diagnostic reaches `p<=.05`; these values rank the lead and are not
confirmation tests.

## Dirt and instability

- Each localizer graded only three cuts MEDIUM and the other 31 LOW.
- Reviewer exact-state agreement is 25/45 (55.6%).
- On the 11 disputed localization variants, reviewers preserve the same state
  only 4/11 and 3/11 times.
- Reviewer A reverses the overall effect under the B-localizer surface.
- Agreement-only results are a post-localization sensitivity subset.
- The target forms were postselected GDT003 successes, while GDT003 itself was
  `NOT DISTINGUISHABLE FROM STRING STATISTICS`.
- f81v cut 2 and f93v cut 1 are direct agreement-localized counterexamples.

## Conclusion

There is a weak suggestion that some proposed target cuts are visually more
open than matched ordinary within-group cuts, driven especially by one f37v
position. The effect is too dependent on marker placement and reviewer to
support physical modules. Its proper YOLO status is a weird lead worth
recording, not a discovery to promote.

GDT006's localization-capacity stop remains historically correct under its
strict rules; GDT007 is a separately labelled permissive analysis. No f84r
image or formal payload was opened. No confirmed spacing effect, grapheme
boundary, morpheme, linguistic slot, language, meaning, semantic role,
plaintext, or translation is claimed.
