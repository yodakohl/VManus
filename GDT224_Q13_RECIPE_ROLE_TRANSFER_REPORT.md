# GDT224 — q13 has a recipe-like global role balance, not a recipe-like close

Status: **Q13_RECIPE_ROLE_ARCHITECTURE_WEAK_OR_GENERIC**.

The GDT176 instrument was frozen publicly at commit `f51a140` before q13
field roles were generated. It was trained on 22,394 editor-tagged units from
1,136 real medieval recipes and uses only relative field position and field
span. Applied unchanged, it projects 701 q13 fields in 33 records and 163
same-hand Herbal-B fields in 22 records.

## Three frozen predictions

| Endpoint | q13 | Herbal-B | q13 direction | exact-size effect | 4,096-world local / max-three p |
|---|---:|---:|---:|---:|---:|
| mixed clause-like + argument-like record | 0.9341 | 0.7833 | +0.1508 | **-0.0741** | 0.8711 / 0.9878 |
| final closer-like field | 0.4820 | 0.7833 | **-0.3013** | **-0.4074** | 1.0000 / 1.0000 |
| advantage in JS distance to real-recipe role mix | 0.00488 | 0.03692 | **+0.03204** | **+0.05667** | 0.0203 / 0.0576 |

Only the aggregate-distribution prediction survives exact record-size control.
Its q13 advantage remains positive after deleting every one of the nine q13
folios in turn. The raw mixed-record effect is also positive in 9/9 deletions,
but reverses under exact size control. The final-closer prediction is negative
in all 9/9 deletions. Zero folds satisfy all three directions.

## Interpretation

This is a useful partial scaffold. q13 contains clause-sized and short-
argument-sized formal fields in almost the same **global balance** learned from
the readable recipes, substantially closer than Herbal-B. That is compatible
with a practical record compiler containing procedure-like spans interleaved
with compact argument/value-like spans.

It is not a complete recipe architecture. The expected final closer-like field
is much less common in q13 than in Herbal-B, and the apparent abundance of
mixed records is largely a consequence of q13's longer mechanical records.
The strongest surviving statistic is a distributional balance, not a recovered
role transition or readable clause.

The result therefore narrows the leading theory without translating it:
q13 is compatible with a **mixed procedural/argument record body**, but its
record termination differs from the readable recipe collections. A plausible
next step is to test whether q13's missing closer has moved into a diagram-
local label, page-final structure, or non-DY closure class using a predeclared
mechanism—not to call individual fields ingredients or actions.

The classifier cannot distinguish tools from ingredients and nearly fails
openers even in readable data. No PAGE_HOST, token, wrapper, source group, or
field receives an ingredient, tool, action, object, disease, bath, word,
language, plaintext, or translation. No f84 artifact was accessed.
