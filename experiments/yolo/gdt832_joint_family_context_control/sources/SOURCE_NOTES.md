# GDT832 source grouping notes

The pinned UDante source repeats eight citation labels noncontiguously in Monarchia Book II. The source phase first stopped before writing outputs or generating a key. Before any fit, the coordinator clarified the unit as a maximal contiguous run of one exact citation. Repeated labels are disambiguated by occurrence; the original citation and source sentence IDs are retained. No chapter label is silently changed and no nonadjacent text is merged. The Book I versus Books II/III split and every other selection rule are unchanged.

| Original citation | Occurrence | Run ID | First source sentence |
|---|---:|---|---|
| Liber_Secundus,x,Paragraphus_1 | 2 | Mon:Liber_Secundus:x:Paragraphus_1:occurrence_2 | Mon-409 |
| Liber_Secundus,x,Paragraphus_2 | 2 | Mon:Liber_Secundus:x:Paragraphus_2:occurrence_2 | Mon-410 |
| Liber_Secundus,x,Paragraphus_3 | 2 | Mon:Liber_Secundus:x:Paragraphus_3:occurrence_2 | Mon-411 |
| Liber_Secundus,x,Paragraphus_4 | 2 | Mon:Liber_Secundus:x:Paragraphus_4:occurrence_2 | Mon-412 |
| Liber_Secundus,x,Paragraphus_5 | 2 | Mon:Liber_Secundus:x:Paragraphus_5:occurrence_2 | Mon-414 |
| Liber_Secundus,x,Paragraphus_6 | 2 | Mon:Liber_Secundus:x:Paragraphus_6:occurrence_2 | Mon-417 |
| Liber_Secundus,x,Paragraphus_7 | 2 | Mon:Liber_Secundus:x:Paragraphus_7:occurrence_2 | Mon-419 |
| Liber_Secundus,x,Paragraphus_8 | 2 | Mon:Liber_Secundus:x:Paragraphus_8:occurrence_2 | Mon-421 |

Normalization preserves every ordered alphabetic word after the specified casefold/ligature/NFKD transformation. A control run containing any still unrepresentable alphabetic word is excluded as a whole and recorded in CAPACITY.json. Punctuation and spacing are not scored. No word is individually deleted to make a control fit.

Reference uses only pinned ITTB TRAIN. Reference sentences sharing an exact twenty-word sequence with a retained control run are removed before both language-model and family preparation. CoNLL-U multiword tokens are reconstructed as written forms; their multiple syntactic analyses are not collapsed to one invented lemma. Exact single-token joins support the family dictionary, and any unresolved join stays unknown.

The historical resources carry CC BY-NC-SA 3.0; copied source READMEs and license text retain attribution and provenance. Attested lemma/form memberships are not an exhaustive historical paradigm generator. No Voynich data are inputs.

## Pre-fit active-rule design correction

The original source-capacity protocol stopped solely because one nominal suffix rule occurs in neither discovery nor held. Its CAPACITY.json bytes remain unchanged (SHA256 `f5563c6ecff3d78558de9bd497d76ee701663304931950e4f74a2557d2141fef`). Before any encoding key or fitted score existed, the coordinator explicitly changed only the new control's suffix coverage requirement to rules active in either partition. Each such rule still requires at least eight discovery occurrences. The inactive rule remains in the four-card deck but is unidentifiable and receives no key-recovery credit, as already specified for unused letters. No word, paragraph, book split, suffix/wholeword value, candidate pool, random seed or encoder operation was changed. ACTIVE_RULE_CAPACITY.json is a separate decision with source/spec/input bindings; the historical initial stop is not relabeled as a pass. Three active suffix values, not four, can be assessed in this control.
