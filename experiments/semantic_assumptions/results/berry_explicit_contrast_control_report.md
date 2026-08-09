# BERRY001 explicit berry/no-fruit control report

## Status

**Anonymous controls pass; target unrun.**

The existing human page atlas supplies a literal, disjoint contrast:

- 8 pages contain the exact Gheuens/Rapaport tag `berries that have no added
  circles`;
- 7 pages contain the exact tag `no fruits or flowers`.

No missing tag or ambiguous description is treated as a negative. All fifteen
physical pages are Herbal section H, Currier A, hand 1 in every manual reading.
The current confirmed-prose panel contains 663 reading-specific loci. Token
totals are 1,368/1,355/1,361 literal tokens and 1,338/1,332/1,330 parsed-root
tokens in ZL3b/IT2a/RF1b.

The score-blind gates retain 359 recurrent features shared across all readings:
exact tokens, proper 2–4-character prefixes/suffixes/infixes, root tuples,
atoms, tuple boundaries, and adjacent root bigrams. Complete token length and
linear folio order are removed before scoring. The exact null contains all
`C(15,8) = 6,435` synchronized page assignments.

## Controls

| Control | Result |
|---|---:|
| exact assignments | 6,435 |
| eligible features | 359 |
| planted assignment tail | 1/6,435 |
| alternate-reading disagreement maximum | 0 |
| projected constant maximum | 0 |
| projected linear-order maximum | 0 |
| adjusted family maximum 95th percentile | 2.917924023188 |
| raw family maximum 95th percentile | 2.940700568437 |

The control artifact explicitly records `target_assignment_computed: false`,
and no target artifact exists. A standalone validator imports no production
code and independently reconstructs the literal source panel, uniform
metadata, six token totals, all 359 features, the canonical count-matrix hash,
both family-null distributions, the exact orbit, and every control in 20
checks.

This authorizes one frozen target invocation only. Even a pass can nominate
only a page-field pattern associated with these later human illustration tags;
it cannot establish that the author mentions berries, translate a word or
negation, identify a plant or language, or supply plaintext.

## Reproduction

```text
./vpy experiments/semantic_assumptions/berry_explicit_contrast/run_berry_explicit_contrast.py --mode controls --output experiments/semantic_assumptions/berry_explicit_contrast/CONTROL_RESULT.json
./vpy experiments/semantic_assumptions/berry_explicit_contrast/validate_berry_explicit_controls.py --output experiments/semantic_assumptions/berry_explicit_contrast/CONTROL_VALIDATION.json
```
