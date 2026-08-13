# GDT001 whole-manuscript global decipherment tournament — YOLO result

**Status: EXPLORATORY. This is not a confirmed translation and must not be merged automatically into the canonical evidence branch.**

## Outcome

The strongest complete generative account in this tournament is `nonsemantic_ngram_o2` at **3.053577 bits per source symbol**. It is a line-reset, second-order character generator and emits no plaintext. The strongest language-like candidate is `abbr_lang_multigraph_middle_high_german_nonull_s0101` at **5.117051 bits/symbol**. The strongest homophonic cipher is **5.401351**, the strongest anonymous record model is **5.182018**, and my line-entry/body-channel hybrid is **4.546773**.

No candidate qualifies for freezing as a decipherment. The nonsemantic winner is both much shorter and fully explicit; the language/cipher mappings are restart-unstable and their fixed-packet outputs are orthographic-looking noise rather than defensible readings.

## Complete leaderboard

| rank | candidate | class | system | bits | bits/source symbol | key | latent | reconstruction | exceptions |
|---:|---|---|---|---:|---:|---:|---:|---:|---:|
| 1 | `nonsemantic_ngram_o2` | NONSEMANTIC_GENERATOR | CHAR_2GRAM_KT | 593383.29 | 3.053577 | 3.00 | 0.00 | 593377.29 | 0.00 |
| 2 | `nonsemantic_ngram_o3` | NONSEMANTIC_GENERATOR | CHAR_3GRAM_KT | 610290.27 | 3.140468 | 5.00 | 0.00 | 610282.27 | 0.00 |
| 3 | `nonsemantic_ngram_o1` | NONSEMANTIC_GENERATOR | CHAR_1GRAM_KT | 643430.25 | 3.311803 | 3.00 | 0.00 | 643424.25 | 0.00 |
| 4 | `nonsemantic_ngram_o4` | NONSEMANTIC_GENERATOR | CHAR_4GRAM_KT | 654662.28 | 3.368887 | 5.00 | 0.00 | 654654.28 | 0.00 |
| 5 | `nonsemantic_ngram_o5` | NONSEMANTIC_GENERATOR | CHAR_5GRAM_KT | 723158.04 | 3.721116 | 5.00 | 0.00 | 723150.04 | 0.00 |
| 6 | `nonsemantic_neural_gru_h48_s0072` | NONSEMANTIC_GENERATOR | QUANTIZED_GRU_H48 | 796655.14 | 4.125673 | 133832.00 | 0.00 | 662820.14 | 0.00 |
| 7 | `nonsemantic_neural_gru_h48_s0071` | NONSEMANTIC_GENERATOR | QUANTIZED_GRU_H48 | 798513.43 | 4.135297 | 133832.00 | 0.00 | 664678.43 | 0.00 |
| 8 | `nonsemantic_neural_gru_h48_s0073` | NONSEMANTIC_GENERATOR | QUANTIZED_GRU_H48 | 799209.39 | 4.138901 | 133832.00 | 0.00 | 665374.39 | 0.00 |
| 9 | `hybrid_dual_channel_entry_body` | HYBRID | ENTRY_STATE_PLUS_STEM_MODIFIER | 877968.25 | 4.546773 | 143600.05 | 466010.77 | 268354.44 | 0.00 |
| 10 | `abbr_lang_multigraph_middle_high_german_nonull_s0101` | ABBR_LANG | middle_high_german_MULTIGRAPH | 988087.21 | 5.117051 | 571.56 | 645205.54 | 342307.12 | 0.00 |
| 11 | `abbr_lang_multigraph_middle_high_german_nonull_s0303` | ABBR_LANG | middle_high_german_MULTIGRAPH | 990791.06 | 5.131054 | 571.56 | 672589.25 | 317627.25 | 0.00 |
| 12 | `abbr_lang_multigraph_middle_high_german_nonull_s0202` | ABBR_LANG | middle_high_german_MULTIGRAPH | 991072.42 | 5.132511 | 571.56 | 676159.77 | 314338.10 | 0.00 |
| 13 | `record_notation_fields` | RECORD_NOTATION | ENTRY_PREFIX_CORE_SUFFIX | 1007042.23 | 5.182018 | 156543.67 | 701043.07 | 149452.49 | 0.00 |
| 14 | `abbr_lang_multigraph_middle_high_german_nullq_s0202` | ABBR_LANG | middle_high_german_MULTIGRAPH | 1013459.07 | 5.248445 | 566.86 | 679644.24 | 333244.97 | 0.00 |
| 15 | `abbr_lang_multigraph_middle_high_german_nullq_s0101` | ABBR_LANG | middle_high_german_MULTIGRAPH | 1016514.20 | 5.264267 | 566.86 | 667734.65 | 348209.70 | 0.00 |
| 16 | `nonsemantic_page_unigram` | NONSEMANTIC_GENERATOR | PAGE_CONDITIONED_UNIGRAM | 1034025.80 | 5.323663 | 15.00 | 0.00 | 1034007.80 | 0.00 |
| 17 | `nonsemantic_ngram_o0` | NONSEMANTIC_GENERATOR | CHAR_0GRAM_KT | 1034034.34 | 5.323625 | 1.00 | 0.00 | 1034030.34 | 0.00 |
| 18 | `abbr_lang_multigraph_middle_high_german_nullq_s0303` | ABBR_LANG | middle_high_german_MULTIGRAPH | 1035860.64 | 5.364457 | 566.86 | 703784.81 | 331505.97 | 0.00 |
| 19 | `homophonic_cipher_middle_high_german_s0101` | HOMOPHONIC_CIPHER | middle_high_german | 1049190.86 | 5.401351 | 123.10 | 856145.93 | 192918.83 | 0.00 |
| 20 | `abbr_lang_middle_high_german_s0202` | ABBR_LANG | middle_high_german | 1052666.91 | 5.419944 | 93.97 | 902117.83 | 150452.11 | 0.00 |
| 21 | `abbr_lang_middle_high_german_s0303` | ABBR_LANG | middle_high_german | 1052667.51 | 5.419975 | 93.97 | 902118.43 | 150452.11 | 0.00 |
| 22 | `abbr_lang_old_hungarian_s0202` | ABBR_LANG | old_hungarian | 1058823.78 | 5.451195 | 93.97 | 908745.86 | 149980.96 | 0.00 |
| 23 | `abbr_lang_old_hungarian_s0101` | ABBR_LANG | old_hungarian | 1058830.52 | 5.451230 | 93.97 | 908752.60 | 149980.96 | 0.00 |
| 24 | `homophonic_cipher_middle_high_german_s0303` | HOMOPHONIC_CIPHER | middle_high_german | 1062136.62 | 5.466056 | 123.10 | 841817.08 | 220193.45 | 0.00 |
| 25 | `homophonic_cipher_old_hungarian_s0202` | HOMOPHONIC_CIPHER | old_hungarian | 1062699.71 | 5.471291 | 123.10 | 874335.50 | 188238.11 | 0.00 |
| 26 | `homophonic_cipher_old_italian_tuscan_s0202` | HOMOPHONIC_CIPHER | old_italian_tuscan | 1063749.37 | 5.476244 | 123.10 | 873047.43 | 190575.84 | 0.00 |
| 27 | `abbr_lang_old_hungarian_s0303` | ABBR_LANG | old_hungarian | 1064615.10 | 5.480757 | 93.97 | 914414.20 | 150103.94 | 0.00 |
| 28 | `homophonic_cipher_old_hungarian_s0303` | HOMOPHONIC_CIPHER | old_hungarian | 1065113.84 | 5.483522 | 123.10 | 876911.52 | 188076.22 | 0.00 |
| 29 | `abbr_lang_old_italian_tuscan_s0101` | ABBR_LANG | old_italian_tuscan | 1073070.58 | 5.522780 | 93.97 | 922590.50 | 150383.11 | 0.00 |
| 30 | `abbr_lang_old_italian_tuscan_s0202` | ABBR_LANG | old_italian_tuscan | 1073070.58 | 5.522780 | 93.97 | 922590.50 | 150383.11 | 0.00 |
| 31 | `homophonic_cipher_old_hungarian_s0101` | HOMOPHONIC_CIPHER | old_hungarian | 1077579.95 | 5.547501 | 123.10 | 890902.10 | 186551.76 | 0.00 |
| 32 | `homophonic_cipher_old_italian_tuscan_s0101` | HOMOPHONIC_CIPHER | old_italian_tuscan | 1081753.66 | 5.567555 | 123.10 | 887307.17 | 194320.40 | 0.00 |
| 33 | `record_notation_dictionary_o0` | RECORD_NOTATION | ANONYMOUS_VALUE_DICTIONARY_0GRAM | 1082141.06 | 5.604132 | 389357.01 | 424426.61 | 268354.44 | 0.00 |
| 34 | `abbr_lang_middle_high_german_s0101` | ABBR_LANG | middle_high_german | 1084349.56 | 5.582841 | 93.97 | 933809.97 | 150442.62 | 0.00 |
| 35 | `abbr_lang_old_italian_tuscan_s0303` | ABBR_LANG | old_italian_tuscan | 1087127.68 | 5.595300 | 93.97 | 936695.75 | 150334.96 | 0.00 |
| 36 | `homophonic_cipher_middle_french_s0303` | HOMOPHONIC_CIPHER | middle_french | 1100703.82 | 5.664475 | 123.10 | 863116.26 | 237461.46 | 0.00 |
| 37 | `homophonic_cipher_old_italian_tuscan_s0303` | HOMOPHONIC_CIPHER | old_italian_tuscan | 1101199.25 | 5.667579 | 123.10 | 896863.13 | 204210.03 | 0.00 |
| 38 | `homophonic_cipher_middle_high_german_s0202` | HOMOPHONIC_CIPHER | middle_high_german | 1106893.75 | 5.698911 | 123.10 | 898275.64 | 208492.01 | 0.00 |
| 39 | `abbr_lang_medieval_czech_s0101` | ABBR_LANG | medieval_czech | 1111926.75 | 5.724912 | 93.97 | 961468.37 | 150361.41 | 0.00 |
| 40 | `abbr_lang_medieval_czech_s0303` | ABBR_LANG | medieval_czech | 1115165.83 | 5.741589 | 93.97 | 965057.70 | 150011.16 | 0.00 |
| 41 | `homophonic_cipher_medieval_czech_s0101` | HOMOPHONIC_CIPHER | medieval_czech | 1115446.26 | 5.742737 | 123.10 | 964850.97 | 150469.20 | 0.00 |
| 42 | `homophonic_cipher_middle_french_s0101` | HOMOPHONIC_CIPHER | middle_french | 1118801.25 | 5.757668 | 123.10 | 933528.48 | 185146.67 | 0.00 |
| 43 | `homophonic_cipher_latin_s0101` | HOMOPHONIC_CIPHER | latin | 1123201.97 | 5.782220 | 123.10 | 931225.90 | 191849.98 | 0.00 |
| 44 | `homophonic_cipher_middle_french_s0202` | HOMOPHONIC_CIPHER | middle_french | 1123417.68 | 5.781544 | 123.10 | 936053.43 | 187238.15 | 0.00 |
| 45 | `homophonic_cipher_latin_s0202` | HOMOPHONIC_CIPHER | latin | 1125255.88 | 5.791809 | 123.10 | 893950.38 | 231179.40 | 0.00 |
| 46 | `abbr_lang_latin_s0202` | ABBR_LANG | latin | 1131976.95 | 5.827723 | 93.97 | 981504.76 | 150375.22 | 0.00 |
| 47 | `abbr_lang_latin_s0303` | ABBR_LANG | latin | 1131983.43 | 5.827757 | 93.97 | 981507.65 | 150378.81 | 0.00 |
| 48 | `homophonic_cipher_latin_s0303` | HOMOPHONIC_CIPHER | latin | 1137618.06 | 5.857157 | 123.10 | 884563.99 | 252927.97 | 0.00 |
| 49 | `abbr_lang_middle_french_s0101` | ABBR_LANG | middle_french | 1139108.63 | 5.862417 | 93.97 | 989057.21 | 149954.45 | 0.00 |
| 50 | `abbr_lang_middle_french_s0303` | ABBR_LANG | middle_french | 1139110.20 | 5.865202 | 93.97 | 988437.82 | 150575.42 | 0.00 |
| 51 | `abbr_lang_middle_french_s0202` | ABBR_LANG | middle_french | 1139707.85 | 5.866467 | 93.97 | 989443.98 | 150166.90 | 0.00 |
| 52 | `abbr_lang_medieval_czech_s0202` | ABBR_LANG | medieval_czech | 1139967.03 | 5.869312 | 93.97 | 989626.60 | 150243.47 | 0.00 |
| 53 | `homophonic_cipher_medieval_czech_s0303` | HOMOPHONIC_CIPHER | medieval_czech | 1140735.36 | 5.873419 | 123.10 | 990426.91 | 150182.35 | 0.00 |
| 54 | `record_notation_entry_fields` | RECORD_NOTATION | ENTRY_PREFIX_CORE_SUFFIX | 1153695.53 | 5.936663 | 156724.27 | 847506.86 | 149461.40 | 0.00 |
| 55 | `record_notation_dictionary_o1` | RECORD_NOTATION | ANONYMOUS_VALUE_DICTIONARY_1GRAM | 1160341.66 | 6.009113 | 389359.01 | 502625.20 | 268354.44 | 0.00 |
| 56 | `record_notation_dictionary_o2` | RECORD_NOTATION | ANONYMOUS_VALUE_DICTIONARY_2GRAM | 1172773.66 | 6.073495 | 389359.01 | 515057.21 | 268354.44 | 0.00 |
| 57 | `homophonic_cipher_medieval_czech_s0202` | HOMOPHONIC_CIPHER | medieval_czech | 1176771.92 | 6.056438 | 123.10 | 981410.85 | 195234.98 | 0.00 |
| 58 | `nonsemantic_copy_w32` | NONSEMANTIC_GENERATOR | PAGE_COPY_MODIFY_W32 | 1184103.92 | 6.096087 | 11.00 | 0.00 | 1184089.92 | 0.00 |
| 59 | `nonsemantic_copy_w128` | NONSEMANTIC_GENERATOR | PAGE_COPY_MODIFY_W128 | 1185016.71 | 6.100880 | 15.00 | 0.00 | 1184998.71 | 0.00 |
| 60 | `nonsemantic_copy_w8` | NONSEMANTIC_GENERATOR | PAGE_COPY_MODIFY_W8 | 1208312.30 | 6.220942 | 7.00 | 0.00 | 1208302.30 | 0.00 |
| 61 | `abbr_lang_latin_s0101` | ABBR_LANG | latin | 1244312.48 | 6.405991 | 93.97 | 1094183.01 | 150032.50 | 0.00 |

## Failed runs retained

4 failed exact-audit/search runs remain in `GDT001_YOLO_LEDGER.tsv`; none was deleted from the run history.

## GPU and exact CPU accounting

The RTX 3090 proposed language, cipher, abbreviation, and neural-null parameters. Large population search showed a material CUDA crossover. Every retained discrete key was rescored by deterministic CPU code; the final nonsemantic leader is independently reconstructed context-by-context by `validate_gdt001_tournament.py`.

## Restart stability

No three-restart language/cipher/abbreviation configuration converged to one byte-identical decoder. See `gdt001_restart_stability.json`. The best-score spread can be small while the explicit key remains different; that is evidence for a broad accidental optimum rather than a recovered unique key.

## Counterfactual manuscripts

Within-line, page-conditioned, global frequency-preserving, boundary-preserving identity, and Timm/copy-modify controls were all fit with representative language/cipher/record/nonsemantic systems. Real Voynich structure is easier for all of them than destructive shuffles, but the same second-order nonsemantic family wins every control. This shows real local structure without making it linguistic. See `gdt001_counterfactual_analysis.json`.

## Fixed interpretation packet

Every exported candidate includes the same Herbal-A, Currier-B, biological f75v, f57v, f67r2, circular f69v, and f116v stress packet in `reverse_generation.tsv`, including alternate lattice readings and failures. The historical-language strings were not repaired or paraphrased.

## Structural coverage

The character winner captures line resets and local construction regularity but does not independently explain diagram registers or semantics. The hybrid explicitly models entry-state differences and reusable body stems, but its extra inventory cost leaves it 1.493 bits/symbol behind. See `gdt001_structural_coverage.json`.

## Score strata and transcription sensitivity

`gdt001_score_breakdown.tsv` reports common-code allocation by Currier and section and keeps model/key costs global. `gdt001_edition_sensitivity.json` evaluates ZL3b-, IT2a-, and RF1b-constrained paths under the frozen winning predictor. Neither diagnostic selects an edition as truth.

## Why every candidate may still be false

- The historical corpora are proxies, not perfect fifteenth-century domain corpora.
- Greedy multigraph segmentation is only one abbreviation transducer family.
- The record grammars may be too literal and dictionary-heavy.
- The null winner describes local form but does not establish that the manuscript is meaningless.
- Whole-manuscript discovery permits postselection; this branch deliberately makes no confirmation claim.
- Transcription is an alternate-observation lattice, not physical ground truth.

## Decision

`NO_DECIPHERMENT_CANDIDATE_FREEZE`. Do not create a confirmation branch. The exploratory result is that, among the implemented complete explicit systems, a compact nonsemantic local generator decisively wins. This is a tournament result, not a proof that no language, cipher, or technical notation exists.

## Fast decoder-assumption follow-ups

Two additional explicit Middle High German screens relaxed assumptions that could have hidden a decoder. Allowing source separators to map freely, allowing separate initial/medial/final glyph values, using separate Currier A/B keys, and applying fixed within-group reversal/rotation/odd-even transpositions all lost decisively to the same 2-gram null. The strongest was positional allography at 5.070408 bits/source symbol, still 391,919 bits worse overall; the strongest transposition was reversal at 5.428625 bits/symbol, 461,529 bits worse. All three-restart keys were byte-distinct. See `gdt001_contextual_language_results.json` and `gdt001_key_variant_results.json`. These results close only the tested compact transformations; they are not a general anti-language result.

A reversible anonymous-unit grammar selected zero BPE-style merges after paying for every merge rule; learned multi-character units therefore did not improve the common MDL. A separate abbreviation transducer allowed every source symbol to emit either one or two plaintext letters, but its best run scored 5.751066 bits/symbol—524,187 bits behind the null—and all restart keys differed. See `gdt001_bpe_notation_results.json` and `gdt001_expanding_abbreviation_results.json`.

Further exact screens found no rescue from limited opaque nomenclators, alternative reading orders, reversible carrier/payload interleaving, word-slot grammars, preceding-source-conditioned allography, adjacent-group edit records, fixed null signs, periodic keys, or direct STA-family/member language mapping. A whole-group historical-word nomenclator was initially close, so all mappings for codebooks of size 1–8 were enumerated exactly across six language packs and word orders 0–3. Its best language model remained 26.98 bits worse than the matched source-only code; the dense source-only sweep remained 67,824 bits worse than the character null. No word assignment is retained as a candidate reading.
