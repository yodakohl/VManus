# BERRY001 explicit berry/no-fruit target report

## Result

**Final validated nonconfirmation.** None of the 359 frozen recurrent
literal/root features passes all six candidate gates on the exact 6,435-way
page-assignment orbit.

The panel uses only exact human illustration assertions: eight Herbal pages
tagged `berries that have no added circles` and seven tagged `no fruits or
flowers`. Silence and ambiguous descriptions are not negatives. All fifteen
pages are section H, Currier A, hand 1. The text consists of 663
reading-specific confirmed-prose loci from the alternate ZL3b, IT2a, and RF1b
readings; OCR and automated image recognition are absent.

## Sole near-miss

| Feature | adjusted familywise p | raw familywise p | minimum adjusted effect | minimum raw effect | enriched-class page support |
|---|---:|---:|---:|---:|---:|
| `ROOT_PREFIX:oii` | 0.080963480963 | 0.139238539239 | 0.015174244870 | 0.014821417773 | 6 |

`ROOT_PREFIX:oii` has the same direction in all three readings and both
nuisance-control views, and that direction survives every single-page
deletion. It nevertheless fails both frozen familywise thresholds: adjusted
`p <= .05` and raw `p <= .10`. No threshold was changed after exposure.

An independent implementation imports no production runner and reconstructs
the source panel, all 359 features, every primary and raw score, all inclusive
familywise tails, the candidate row, and the zero-pass decision in 16 checks.
Each result and validation artifact also reproduces byte for byte on its own
rerun.

## Scope

This closes only the fixed page-level recurrent-morphology test. It does not
show that the Voynich author ignored berries, and it does not turn unannotated
pages into no-berry examples. `oii` is not established as BERRY, FRUIT, NO,
any plant term, or any English word. The experiment supplies no plant
identity, language identification, plaintext, or translation.

## Reproduction

```text
./vpy experiments/semantic_assumptions/berry_explicit_contrast/run_berry_explicit_contrast.py --mode target --output experiments/semantic_assumptions/berry_explicit_contrast/TARGET_RESULT.json
./vpy experiments/semantic_assumptions/berry_explicit_contrast/validate_berry_explicit_target.py --output experiments/semantic_assumptions/berry_explicit_contrast/TARGET_VALIDATION.json
```
