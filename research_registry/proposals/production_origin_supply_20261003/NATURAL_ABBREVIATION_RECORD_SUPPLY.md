# Natural abbreviation record supply: code available, complete records not supplied

2026-10-03. Bounded source-only availability check of the nominated author repository and paper. No target text/image, reserve, author contact, learner, fitting or corpus reconstruction. **No complete recipe nominated.** The checked public repository supplies software and a visualization, not the transcription or alignment inputs. This is a bounded supply result, not a claim that the corpus is unavailable everywhere.

## Exact checked sources and availability

- [Author repository](https://github.com/suomela/medieval-abbreviations), main commit **dbfcfaf39b42756fecba7825042ccb082d29a8f7**, committed2021-01-29T11:01:13Z. The recursive GitHub tree is complete (`truncated=false`): **16 blobs**, comprising13 Python scripts, README, LICENSE and `samples/blocks-language-sort-words.png`. The initial verbal count17 was a counting error, corrected before this report.
- All **15 public commits** were checked through their changed-file inventories. Across that history the same16 distinct paths occur; no XML, JSON, workbook, CSV, TSV, HTML or text corpus file occurs. There is one branch (`main`), no tags and no releases at inspection. This is stronger than inferring missing data from README alone; it still covers only this named public repository/history.
- [Paper DOI](https://doi.org/10.1093/llc/fqab007): Honkapohja–Suomela, *Lexical and function words or language and text type?*, DSH37(3),765–787. The publisher URL and its supplementary-data fragment failed through the browser service. The [author-institution PDF](https://acris.aalto.fi/ws/portalfiles/portal/80689338/Lexical_and_function_words_or_language_and_text_type_Abbreviation_consistency_in_an_aligned_corpus_of_Latin_and_Middle_English_plague_tracts.pdf) was readable through web text extraction. Direct byte retrieval returned403: no local PDF byte pin or downloaded PDF is claimed.
- README and actual code require `data/*_DSH_final.xml` and manually corrected `data/jburgundy.xlsx`. Neither is in the repository. `extract.json` and `extract2.json` are described outputs, not supplied data. The sample PNG is aggregate visualization, not a complete record; it was not viewed or decoded here. No input is reconstructed from its pixels.

Code byte pins, obtained directly from commit-specific raw URLs:

|Path|SHA256|
|---|---|
|README.md|58d3c641508cbe181a48c52ebad00772b135dde8b085a830a6a41e659a352f9e|
|alignment/align.py|8eec67d8a6284a4bbc11dcf407e85bb0d50028d60f8fc4b96c81c2a028b3ce19|
|parsing/extract.py|68b805d3b6e3dfe51106b2d2ffc065604f73935f36ef27a764e61d00d628e19a|
|misc/outline.py|2349327c0f6098920cbcc12f2ba60b547a492eb966941fd95ef534b416b02df8|

Existing local navigation is [GDT755 source registry](../../../experiments/yolo/gdt755_top24_historical_register_crosswalk/src/HISTORICAL_SOURCE_REGISTRY.tsv), rowHX006, which explicitly records cache **NONE**. Its source/expression cards are evidence summaries, not hidden XML. [GDT755 report](../../../experiments/yolo/gdt755_top24_historical_register_crosswalk/REPORT.md) is the earlier claim-bearing crosswalk; its later working meanings are not imported here.

## Witnesses and observed natural relationships

The paper identifies British Library Sloane2320 and Sloane3566; Trinity College O.1.77; Boston Medical Library Ballard19; Gonville and Caius336/725; and Takamiya33. The witnesses are fifteenth-century copies. Tokyo lacks a leaf and is excluded from the alignment analysis; Tokyo/Gonville share a scribe. This is not six independent traditions.

The study distinguishes Latin long, Middle English and Latin epistolary versions, encoding recipes separately. `JBlong1` names its first long-version recipe; the article does not supply its complete transcription here. Tables and discussion show recipe formulae and shared signs, including crossed-p variants for per/por/par in different lexical hosts. These are real historical observations, not cipher-generated parts, but do not establish the requested recurrent-sign condition within one complete available recipe. [Primary paper](https://doi.org/10.1093/llc/fqab007), §§2–3,5.2,5.5 and tables1,4.

## Representation limits visible in the published code

`alignment/align.py` recursively reads expanded text but marks an abbreviation branch as a boolean; the abbreviated string itself is not its alignment key. `parsing/extract.py` separately derives short and full strings, but `fix_word` normalizes whitespace and changes `+t` to thorn. `parse_word_am` strips trailing question marks and `(sic)`, then applies `AM_MAP`. Several annotation labels map to the same encoded symbol; superscript position is represented by a caret and some signs by private-use characters. Some labels themselves name meanings, such as DRACHM and RECIPE. Those labels would leak answers if handed to a supposedly opaque learner.

`parsing/freq.py` and the README describe grouping spelling variants. Such aggregate output cannot replace original XML for literal carrier order, sign identity, uncertainty, scope and editorial boundaries. Code inspection proves these transformations exist; without the missing XML it does not quantify which records they affect. Native sign geometry, allographic identity and transcription accuracy were not checked. MIT licensing of software does not by itself establish a corpus-data license.

## Is paragraph pairing essential?

**No, for a conditional type-level writing constraint.** If visible literal letters are known, an independently declared suspension/contraction channel requires those carriers to occur in the proposed expansion in their written order, with insertion/deletion allowed only by its finite rules. The same observed abbreviation sign must share one output domain/conditioning rule across lexical hosts. This can reject word candidates without any paragraph pair. It is a necessary compatibility condition, not a guarantee of unique expansion; copied letters, homography, context-sensitive signs and optional abbreviation remain distinct.

For unknown writing values, sharing carrier identities can still couple candidate assignments, but their values and conditioning must be inferred jointly. A different expansion rule per whole form removes the proposed constraint. A known readable parallel record provides additional lexical/content information and must therefore be declared as supervision rather than called unpaired recovery. Nothing here establishes such a parallel for the target manuscript.

[GDT1160 SPEC](../../../experiments/yolo/gdt1160_contextual_abbreviation_inverse/SPEC.json) already preserves exact marked group identity and raw neighboring spelling. It uses an exact-type onehot plus offset-tagged neighbor character n-grams; the target group at offsetzero is excluded from context features. Its output domain is supplied by all training-attested per-type expansions. It does **not** induce that domain by enforcing one common forward carrier/sign rule across types. Merely adding raw neighbors or describing its existing onehot as morphology would repeat1160. GDT1164 separately removed subword relations by opaque whole-type IDs, so its negative geometry result does not test this missing common writing constraint. GDT832's co-lemma factor and995's conditioned inverse remain separate predecessors, not demonstrations that a naturally observed writer can now be learned.

## Bounded outcome and next action

The requested deterministic nomination cannot be made from the checked supply: no complete recipe body is available to establish boundaries, repeated-sign occurrences or two lexical hosts. `JBlong1` is only a documented record label, **not** a certified qualifying candidate. No hand-enumerated record, word-candidate lattice or training relation was fabricated.

Stop this acquisition attempt here. A subsequent separately selected supply step would need a public complete original XML record with its abbreviation branches/uncertainty and licensing, or an explicitly authorized native collation of one public witness. Neither is acquired by this report. Do not launch a learner, substitute the paper's aggregate word table for complete prose, or contact authors as an automatic continuation. No word meaning, target compatibility, new historical writer proof or decoder result follows.
