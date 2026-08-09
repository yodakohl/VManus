# FLOWER001 blocked flower/no-flower target report

## Result

**Final validated nonconfirmation.** Zero of 430 frozen recurrent
literal/root features passes all seven gates. No feature even enters the
predeclared adjusted familywise `p <= .20` diagnostic table.

The source panel contains seven explicit `no fruits or flowers` pages, each
blocked with two nearby pages carrying the exact human phrase `flower(s) seen
from the side`. All 21 units are distinct folios in section H, Currier A,
hand 1. Silence, tentative plant names, OCR, and automated image recognition
are excluded.

The least noncompetitive adjusted diagnostic is literal internal piece `oe`:
adjusted familywise `p=.473251028807` and raw familywise
`p=.518975765889`. It is not a candidate and has no semantic gloss.

An independent implementation imports no production runner and reconstructs
the source assignment, all 430 primary and raw feature scores, all inclusive
familywise tails, the empty candidate table, and the final zero-pass decision
in 13 checks. The target and validation artifacts each reproduce byte for
byte on their own reruns.

## Scope

This closes only the fixed blocked page-level morphology test. Together with
BERRY001, it gives no evidence that the tested recurrent morphology directly
tracks these two visible reproductive-structure contrasts at whole-page
scale. It does not show that the author ignored flowers or fruit, and it does
not turn unannotated pages into negative examples. No feature means FLOWER,
FRUIT, NO, a plant name, a language, plaintext, or translation.

## Reproduction

```text
./vpy experiments/semantic_assumptions/flower_explicit_contrast/run_flower_explicit_contrast.py --mode target --output experiments/semantic_assumptions/flower_explicit_contrast/TARGET_RESULT.json
./vpy experiments/semantic_assumptions/flower_explicit_contrast/validate_flower_explicit_target.py --output experiments/semantic_assumptions/flower_explicit_contrast/TARGET_VALIDATION.json
```
