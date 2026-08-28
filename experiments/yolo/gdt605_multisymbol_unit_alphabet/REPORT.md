# GDT605 — stable units, wrong alphabet model

Status: **STABLE_98_UNIT_ALPHABET__ONE_LETTER_READING_REJECTED**.

## Held result

The erased-space fit locates the transcription-boundary error directly:

| held separator | crossed | total | crossing rate |
|---|---:|---:|---:|
| uncertain comma | 185 | 749 | **24.70%** |
| certain point | 575 | 8,570 | **6.71%** |
| drawing interruption | 5 | 97 | **5.15%** |

The uncertain/certain crossing-rate ratio is 3.681 and the odds ratio is 4.561.
The uncertain rate exceeds the certain rate independently on 22 of 23 held
physical folios. The learned units therefore recover information about source
separator certainty although the BPE learner never receives that annotation.

## Boundary-aware inventory

Joining uncertain spaces while retaining certain and drawing boundaries yields:

| split | aligned rows | hard chunks | collapsed glyphs | unit occurrences | unit types | mean glyphs/unit |
|---|---:|---:|---:|---:|---:|---:|
| train, 68 folios | 2,980 | 20,336 | 87,655 | 43,335 | **98** | 2.023 |
| held, 23 folios | 1,171 | 9,838 | 43,655 | 21,679 | **97** | 2.014 |

Held-only unit types: **zero**. The complete ordered 98-unit inventory and all
64 merges are published as TSV artifacts.

## One-letter attack

The stable inventory is not an ordinary substitution alphabet. Held real-minus-
destroyed model scores are negative in every restart:

| language | held real−destroyed bits/character | restart type agreement | held-weighted agreement |
|---|---:|---:|---:|
| Latin | −0.0247, −0.0449, −0.0848 | 4.08–30.61% | 4.06–28.84% |
| Old Italian | −0.0732, −0.1657, −0.1597 | 7.14–17.35% | 5.61–19.22% |

Locally plausible strings such as `anti`, `star` or `atousl` change when the
random start changes and are language-model artifacts, not readings.

## Working consequence

The live unit scale is now about 98 recurrent symbols below unreliable spaces.
The simple alphabet route is closed. The next attack maps this inventory to a
historically plausible mixed nomenclator with variable outputs: homophonic
letters, doubles, syllables, nulls and a small word list. Concrete plaintext is
required before any unit receives a meaning.
