# GDT833 source notes

The fixed source is the pinned UDante repository. All Monarchia sentences form the reference; fresh De vulgari eloquentia Book I is discovery and Book II is held. Whole works and their original sentence/word order are preserved. DVE includes quoted vernacular material; these words are not removed. This is a historical-text control, not a claim that every quoted word is Latin.

Control paragraph units are maximal contiguous citation runs. Five reuse events involve four distinct citation labels; original labels and sentence IDs are retained and occurrence suffixes disambiguate runs. No chapter correction is inferred.

| Original citation | Occurrence | Run ID | First source sentence |
|---|---:|---|---|
| Liber_Secundus,xi,Paragraphus_3 | 2 | DVE:Liber_Secundus:xi:Paragraphus_3:occurrence_2 | DVE-363 |
| Liber_Secundus,xi,Paragraphus_1 | 2 | DVE:Liber_Secundus:xi:Paragraphus_1:occurrence_2 | DVE-365 |
| Liber_Secundus,xi,Paragraphus_3 | 3 | DVE:Liber_Secundus:xi:Paragraphus_3:occurrence_3 | DVE-368 |
| Liber_Secundus,xi,Paragraphus_4 | 2 | DVE:Liber_Secundus:xi:Paragraphus_4:occurrence_2 | DVE-369 |
| Liber_Secundus,xi,Paragraphus_6 | 2 | DVE:Liber_Secundus:xi:Paragraphus_6:occurrence_2 | DVE-371 |

The NATIVE and COLLAPSED reference files contain identical sentence and word positions. The only difference is exact v-to-u replacement in each reference word. Candidate suffixes and the native-frequency wholeword pool are shared. families.json is empty in both arms. The original control plaintext, ciphertext and recovery spelling are never collapsed.

Any unrepresentable alphabetic word excludes its complete control citation run; no individual word is dropped. Exact twenty-word overlaps remove reference sentences only. All exclusions/counts are recorded before key generation. The GDT832 normalizer and annotation join are used through a fixed SHA256 import; no predecessor file is changed.

Source annotation ambiguity is retained as unknown when a written word has multiple syntactic components or an uncertain alignment. Novel-lemma comparisons use all supported discovery analyses, and held novelty requires one unambiguous join. These annotations are evaluator truth only, not decoder inputs.
