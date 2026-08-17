# GDT190 — compiler-stripped whole-word codebook fails

Status: **COMPILER_STRIPPED_WORD_NOMENCLATOR_FALSIFIED**.

The frozen PAGE_HOST layer was treated as an opaque nomenclator rather than a
letter stream.  For each K in 8, 16, 32, and 64, the K most frequent hosts were
mapped bijectively to the K most frequent words of each of six frozen
historical-language packs and scored with an order-1 word model.  Rare hosts
reset the mapped run, and the matched source-identity KT model sees exactly the
same 5108 events and 3490 runs for the
winning K.

The best result is `middle_high_german` at K=8.  After the language
selector and 15.299-bit permutation key, it loses
**841.597 bits** to the matched anonymous
code.  Its three retained mappings are not identical.
All four K values lose; the gap by K for the best language is:

| K | best language | gap vs matched KT (bits) | stable |
|---:|---|---:|---|
| 8 | `middle_high_german` | 841.597 | no |
| 16 | `middle_high_german` | 1,911.517 | no |
| 32 | `middle_high_german` | 2,998.337 | no |
| 64 | `middle_high_german` | 3,527.574 | no |

The compiler-stripped substrate is therefore not rescued by a fixed frequent
whole-word nomenclator.  Together with GDT189, the remaining language routes
require nonbijective/context-dependent expansion, page-specific keys, or a unit
other than one source sign or one PAGE_HOST identity.  Assigned target words
are optimizer labels, not readings, and are not promoted as plaintext.

This closes only the bounded model above.  It establishes no word, language,
sound, plaintext, meaning, or translation.  Every f84 row was rejected before
formal parsing, retention, joining, or scoring.
