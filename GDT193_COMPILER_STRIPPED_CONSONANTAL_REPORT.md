# GDT193 — consonantal stripping helps but remains far from language

Status: **COMPILER_STRIPPED_CONSONANTAL_FALSIFIED**.

After deleting `a/e/i/o/u` from the six target training packs, the best
PAGE_HOST mapping is `old_italian_tuscan`. It loses
**88,117.6 bits** to the matched anonymous
source code (1.468 bits/event). This is materially
smaller than the literal named-letter loss of 121,129.1 bits, but remains
far from competitive. The complete mapping is not stable
across the three starts.

| pack | best gap (bits) | gap/event | stable | omitted consonant |
|---|---:|---:|---|---|
| `latin` | 101,497.4 | 1.691 | no | `k` |
| `middle_high_german` | 101,906.6 | 1.698 | no | `q` |
| `middle_french` | 105,038.4 | 1.750 | no | `w` |
| `old_italian_tuscan` | 88,117.6 | 1.468 | no | `w` |
| `medieval_czech` | 92,050.1 | 1.534 | no | `q` |
| `old_hungarian` | 88,241.7 | 1.470 | no | `x` |

The direction is worth retaining as architectural evidence: vowel omission is
less incompatible with PAGE_HOST than literal alphabetic text. It is not a
language or phonetic result, because the paid channel still loses by tens of
thousands of bits and supplies no stable key. Any viable skeleton theory needs
context-dependent restoration or a different unit, not this static alphabet.

No sign, sound, word, language, plaintext, meaning, or translation is
established. Every f84 row was rejected before parsing or scoring.
