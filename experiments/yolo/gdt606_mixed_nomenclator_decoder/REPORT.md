# GDT606 historical-capacity mixed-codebook attack

Status: **MIXED_CODEBOOK_UNSTABLE_PSEUDOTEXT — STRUCTURAL WHOLE-WORD-CATEGORY LEAD**.

## Result

The tested mixed nomenclator is not yet a reading. Forty-eight complete keys
can make the held Voynich stream look strongly Latin, Old Italian or Middle
High German, but the three mutually incompatible languages all do so and the
exact unit outputs change almost completely between starts. No exact
carrier-stable held word survives.

The attack nevertheless localizes a useful structural class. Units `o`, `y`
and `ol` enter the whole-word category in every one of twelve real-model starts
per language across all three capacity grids. `C` and `d` do so in at least
eleven of twelve starts in every language. Their word values remain unknown.
The next attack should hold this five-unit role class fixed only as a
whole-word/formula-carrier hypothesis and infer roles from manuscript context,
not import any generated reference word.

## Target and unit stream

The guarded source query materializes 4,165 lines on 180 page selectors and 91
physical folios, with f84/f84r forbidden and absent. The unchanged GDT605 split
contains 68 train and 23 held folios. Boundary-aware segmentation gives:

- 20,336 train and 9,838 held hard-boundary chunks;
- 43,335 train and 21,679 held unit occurrences;
- 98 train and 97 held unit types;
- zero held-only unit types.

Uncertain source separators are joined before the 64 train-only merges;
certain separators and drawing interruptions remain hard boundaries.

## Historical-capacity attack

Every key assigns all 98 units. The primary grid contains 42
letters/homophones, four doubles, 34 two-/three-letter signs, seven nulls and
eleven whole-word signs. Sensitivities use 36/4/40/7/11 and 46/4/30/7/11.
Candidates come only from pinned Caesar Latin, Dante Old Italian and five
MHG4SNA texts. Six real primary starts, four order-destroyed-reference starts
and three starts for each sensitivity give 48 complete keys and 4,704 mapping
rows.

An early execution revealed that seeded initialization still depended on
Python set order. Sorting before every seeded shuffle corrected it. Two final
full executions then reproduced the same objectives and artifact bytes.

## Language-model fit does not identify a language

All real-reference keys obtain large positive held real-minus-destroyed
character-model margins, while keys trained against destroyed references have
large negative margins:

| language | real held margin, bits/char | destroyed-key margin | lexicon-char fraction |
|---|---:|---:|---:|
| Latin | 1.902–2.208 | −4.214 to −3.192 | 70.83–74.94% |
| Old Italian | 1.637–1.831 | −4.800 to −3.690 | 76.00–81.01% |
| Middle High German | 1.519–1.718 | −5.389 to −4.456 | 74.73–78.79% |

These margins show that the generator can manufacture each reference style.
They do not select one language. Whole-word candidates are drawn from the same
reference lexicon, so dictionary coverage is not independent evidence.

## Exact keys remain unstable

Primary six-start agreement is far below a usable reading:

| language | minimum held category agreement | minimum held exact-output agreement | exact mappings stable in all six starts |
|---|---:|---:|---:|
| Latin | 65.01% | 6.67% | 1/98 |
| Old Italian | 56.21% | 6.65% | 1/98 |
| Middle High German | 51.37% | 4.77% | 0/98 |

Mean held exact-output agreement is only 12.31% Latin, 13.68% Old Italian and
9.48% Middle High German. Across all capacity grids, no unit has one exact
output stable in all twelve starts for any language.

The generated values demonstrate the ambiguity. For unit `o`, the six primary
outputs are:

- Latin: `civitates`, `legiones`, `legiones`, `omnibus`, `haeduorum`, `helvetii`;
- Old Italian: `rispuose`, `convien`, `maestro`, `rispuose`, `comincio`, `quando`;
- Middle High German: `vrouuuen`, `geschach`, `geschach`, `geschach`, `geschehen`, `geschehen`.

Assigning `o` any one of these words would therefore be arbitrary.

## Carrier correction

A position-only screen reports 90 apparent consensus words. Every one changes
its source carrier across starts. The carrier-aware count is therefore:

- exact carrier-stable held words: **0**;
- exact carrier-stable word folios: **0**.

The only carrier-aligned substring family is `gesch` from unit `o` in five of
six Middle High German starts. It occurs at 597 held loci on all 23 held
folios. This happens because five starts choose either `geschach` or
`geschehen` for the same whole-word sign. It is a real restart-stable prefix
family inside this MHG model, but it is not cross-language and not an exact
word. It is retained as a diagnostic, not translated as “happen”.

## Structural whole-word-category lead

Category identity is much more stable than output identity. Across all twelve
real starts and all three capacity grids:

| unit | Latin W fraction | Old Italian W fraction | MHG W fraction | held occurrences |
|---|---:|---:|---:|---:|
| `o` | 12/12 | 12/12 | 12/12 | 609 |
| `y` | 12/12 | 12/12 | 12/12 | 554 |
| `ol` | 12/12 | 12/12 | 12/12 | 712 |
| `C` | 11/12 | 12/12 | 11/12 | 711 |
| `d` | 11/12 | 12/12 | 11/12 | 597 |

This stability can partly arise from their high standalone rates and the fixed
eleven-word capacity. It supports only the hypothesis that these units behave
like independent formula/whole-word carriers more than ordinary letters or
syllables. It establishes no lexical value.

## Decision and next route

No language passes the exact-output stability gate, and no carrier-stable word
exists. Decision: **MIXED_CODEBOOK_UNSTABLE_PSEUDOTEXT**.

Retain `o/y/ol/C/d` as the next concrete role-attack set. Compare their line,
paragraph, section, neighbour and mutual-substitution distributions against
function words, quantities, materials, actions, names and recipe-control
formulae. A future decoder must reward the same source carrier during fitting,
not merely audit it afterward. Do not transfer any generated Latin, Italian or
German word into the dictionary.

Validation passes 247 structural, hash, capacity, sealed-selector, mapping,
carrier and category checks.
