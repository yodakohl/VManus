# Descriptive baseline: final mentions in symmetric triples

2026-09-14. **Deprioritize the closing interpretation based on the final-mention argument.** The four shared cases remain real, but two are automatic last-mention cases because X occurs only twice. The two remaining dar cases are insufficient to establish a special function against a common background pattern. This is not a refutation of all possible closing meanings.

| Scope | ZL terminal / all | IT terminal / all |
|---|---:|---:|
| char, all symmetric triples | 2/2 | 1/1 |
| dar, all symmetric triples | 3/3 | 3/3 |
| sar | 0/0 (no capacity) | 0/0 (no capacity) |
| Other middle words, all | 157/280 | 155/270 |
| Other middle words, exactly two total X mentions | 101/101 | 105/105 |
| Other middle words, more than two total X mentions | 56/179 | 50/165 |
| dar, more than two total X mentions | 2/2 | 2/2 |
| Other middle words in target paragraphs | 0/1 | 0/0 (no capacity) |

The comparisons are descriptive and not exchangeable matched controls. Paragraph sizes, word frequencies and repeated operands differ. Occurrences can overlap or share a paragraph; the two transcriptions are readings of one manuscript. No p-value, probability of the hypothesis or significance claim is justified. Same-paragraph comparison capacity is effectively absent.

## Which target cases actually bear on the argument?

- f23r `qokchol dar qokchol`: the only two qokchol mentions in that paragraph. No-later-X is automatic in the exactly-two-X stratum.
- f82r `okain char okain`: likewise only two okain mentions, despite different paragraph boundaries in ZL/IT.
- f52r `oty dar oty`: three oty mentions in total, the symmetric pair is last.
- f77v `qokal dar qokal`: five qokal mentions in total, the symmetric pair is last.
- ZL-only f34r `aiin / char aiin`: also exactly two X mentions, and segmentation-sensitive; not an additional independent confirmation.

Thus the four shared constructions reduce to two nonautomatic observations for the proposed ending behavior. The more-than-two-X baseline is 56/179 and 50/165, approximately 31% and 30%. The 2/2 target result is descriptively higher, but the source-wide baseline neither matches these cases nor controls their post-hoc selection and the history of searched forms. It cannot validate a closing word.

## Decision

Do not expand the closure hypothesis into a decoder or another control suite on this evidence. Retain the four literal constructions and the char/dar shared frame as structural observations; repetition, identity, coordination and other relations remain open. The earlier no-later-X observation was correct, but its apparent evidential strength was overstated if treated as four informative confirmations. Original reports remain unchanged; this qualification is recorded here and in the current route.

No translated word or nearly complete reading has resulted. The present route has reached its information limit: another choice of a middle-word gloss would not distinguish the alternatives. No next semantic experiment is selected by this baseline. This decision does not forbid a genuinely different later consequence or new admitted evidence, and does not reopen failed recipe, numeric or alias models.

## Reproduce and limits

DECISION.md was written before baseline extraction, after all target outcomes were known. run.py enumerates every consecutive X M X with X != M within the complete GDT928 paragraph cache, including physical line crossings but never paragraph crossings. All whole-group uncertainty is retained. The 285 ZL and 274 IT triples, all target and control rows, are in TRIPLES.json; RESULT.json gives complete denominators and input/decision hashes. validate.py independently reconstructs matching positions and endpoint counts; this is same-author extraction validation, not semantic validation.

The input contains 659 ZL and 690 IT complete exposed paragraphs; RF lacks paragraph capacity. No new page, image, reserved content or f84/f84r access. The bounded idea producer supplied no independent executable candidate. Full-search controls and independent meaning confirmation remain absent. Stop at this descriptive check as declared; no automatic additional baseline or decoder work.
