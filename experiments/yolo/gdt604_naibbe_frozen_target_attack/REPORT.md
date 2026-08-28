# GDT604 — no stable Naibbe-family target reading

Status: **LM_DRIVEN_PSEUDOTEXT_NO_READING**.

## Result

The exact public-capacity U/P/S attack produces ordered-looking pseudotext in
all three reference languages, but no stable reading. Every language fails
every key-stability gate, and the decoded target is always less typical of the
real language model than of its matched order-destroyed model.

| model | train occurrence/type coverage | held occurrence/type coverage |
|---|---:|---:|
| U=115 navigation | 87.630% / 63.784% | 85.736% / 63.414% |
| U=132 navigation | 88.610% / 64.124% | 86.451% / 63.446% |
| **U=138 primary** | **88.638% / 64.244%** | **86.451% / 63.446%** |

All primary dictionaries saturate at U/P/S=138/138/138 while more than a third
of token types remain unexplained. Of 1,657 held types unseen in training,
1,043 have no frozen P/S cut, 545 have one, 68 have two and one has three.

## Held results

| language | real-key order-z | positive folios | target real−destroyed bits/char | min type agreement | min held-weighted agreement | all-six consensus |
|---|---:|---:|---:|---:|---:|---:|
| Latin | 36.41–57.17 | 22/23 | **−0.726…−0.468** | **9.42%** | **5.00%** | **0.098%** |
| Old Italian | 35.46–68.05 | 23/23 | **−0.907…−0.517** | **12.56%** | **10.81%** | **0.498%** |
| Middle High German | 31.82–62.88 | 23/23 | **−0.904…−0.595** | **7.25%** | **5.25%** | **0.055%** |

The large order-z values are not language identification: three incompatible
languages obtain them. The matched readable-reference control has the opposite
real-minus-destroyed sign: +1.715 bit/character for Latin, +1.349 for Italian
and +1.404 for Middle High German.

Across the 60 retained top lines, zero is identical across all six real-model
restarts. Examples that look locally pronounceable change almost every letter
when only the random start changes. The complete outputs are preserved in the
three top-line TSV files and their readable appendix.

## Consequence

GDT603 established that this architecture is identifiable on a true control;
GDT604 therefore closes the concrete whitespace-token U/P/S target attack,
not merely an underpowered decoder. It does not close mixed-length
nomenclators, learned units that cross observed separators, other cipher
families or non-cipher accounts.

The result assigns no target surface a sound, lexeme, plaintext, translation
or meaning. f84 and f84r were never materialised.
