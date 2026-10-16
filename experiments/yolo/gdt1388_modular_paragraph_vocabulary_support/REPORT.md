# GDT1388 Whole paragraph modular vocabulary support

Two registered cases are excluded by a short exact word-pattern certificate: IT2a and ZL3b cannot come from the fixed Tuscan vocabulary under the declared packet-to-character contract. The other sixteen registered solver cases timed out. A separately declared posthoc analytic check then excludes the IT2a case for the fixed Latin charter vocabulary. Fifteen reader/inventory combinations remain unresolved. No complete source message, historical key or word meaning was recovered.

## The complete source contract

Every group of f75r.32–46 supplies one source character. All source positions are retained: IT120, ZL122, RF121. The same22unknown drawing weights, each0–26, determine every uniquely parsed group by a sum modulo27. SPACE is0; a–z are1–26. Distinct drawings or groups may share values. IT119, ZL119 and RF98groups have a unique literal22unit parse; the remaining1/3/23positions are independent free characters. This is an explicit relaxation of unknown contents, not permission to drop groups or repair their boundaries.

The whole message must be a sequence of words from one complete frozen source inventory, with exactly one encoded SPACE between words and none at its ends. Physical linebreaks add no source character. Six pre-existing ASCII-projected historical inventories are checked separately. IT/ZL have their own paragraph flags; RF is a corresponding window with an added closed-message assumption. Even for IT/ZL, treating a written paragraph as a whole source message is a model premise. Readers are alternate descriptions of one manuscript, not independent confirmations.

Finite-bank membership, all27class coverage, spelling-choice weights and physical wrapping are optimistically omitted. Thus a contradiction excludes the stronger writer with this source contract too. A satisfying assignment would establish only necessary support compatibility, not a complete writer or meaningful language. Unlike a likelihood comparison, this Boolean test does not need choice-probability normalizers. GDT1322/1335 still require them when ranking keys by probability.

## Registered result

The independently prepared six source inventories give the following pattern counts. These are complete vocabulary-type scans, not estimates of language-wide possibility.

| Fixed pack | Vocabulary types | Words containing AABBA | Registered IT / ZL / RF |
|---|---:|---:|---|
| Latin charters |9327|4|UNKNOWN / UNKNOWN / UNKNOWN|
| Middle High German |153647|8|UNKNOWN / UNKNOWN / UNKNOWN|
| Middle French |9020|5|UNKNOWN / UNKNOWN / UNKNOWN|
| Tuscan poetry |12626|0|UNSAT / UNSAT / UNKNOWN|
| Medieval Czech |62977|1|UNKNOWN / UNKNOWN / UNKNOWN|
| Old Hungarian |27943|23|UNKNOWN / UNKNOWN / UNKNOWN|

IT/ZL f75r.38 begin `qokeedy qokeedy qokedy qokedy qokeedy`. Any deterministic whole-packet to single-character decoder must give AABBA. A and B may coincide. Both occur in an adjacent pair, so neither can be SPACE under the no-double-space source rule. All five letters therefore lie inside one source word. No Tuscan inventory word contains this pattern, including the all-five-identical case. This local certificate does not depend on the modulo arithmetic or a semantic paragraph boundary; it does depend on the exact repeated packets and the fixed word/spacing contract. RF's marked forms remain free and cannot inherit it.

The remaining16cases each reached the frozen60second solver limit. Their aggregate solver time was approximately962CPU-worker seconds; this is not elapsed research time. Model preparation took about17worker seconds in total. No budget extension, dictionary repair or solver rerun followed. UNKNOWN supplies neither an exclusion nor a compatible reading.

## Posthoc manual consequences in the Latin inventory

The four Latin pattern-containing words are `deesse`, `preesse`, `piissimi` and `piissimo`. Their mere presence does not favor Latin: `deesse` also appears in the Czech and German collections. Corpus labels are not disjoint language vocabularies.

After the fixed run, a short analytic appendix checked the complete word and its neighboring SPACE obligations at the already selected position. Its expected outcomes were explicitly disclosed before the small proof-check program ran; this was validation of a derived argument, not a blind success or a replacement of the registered solver results.

- `piissimi` and `piissimo` force the group after their final letter, f75r.39G002 `qokeedy`, to be SPACE. But the same group already carries the word's i. Both alignments contradict exact identity in IT and ZL.
- `preesse` requires the preceding group to be SPACE. In ZL that group is `qokeedy`, already e. In IT it is `qokchdy`; the neighboring `qokechdy` must be p. The fixed A=e5/B=s19 pattern gives drawing-e weight13 modulo27, hence `qokchdy`=16−13=3, also not SPACE0.
- `deesse` remains locally compatible in both readings. In IT the preceding two characters must be s,n: `qokedy`=s19, while `qokchdy` is13 below the required SPACE-valued `qokechdy`, hence14=n. In ZL the corresponding group is instead `qokeedy`, giving s,e. The exact source difference matters.

A second small plan, written before its suffix count, checked only these two necessary endings in the unchanged Latin vocabulary. There are **zero words ending sn** and58ending se. An independent review recounts the fixed inventory and verifies coverage of all four candidate alignments. Consequently **IT plus this Latin inventory plus the modular packet rule is analytically excluded**. ZL remains unresolved. The result is conditional refutation, not a proposal that a Voynich word means deesse, e or s.

The registered RESULT remains2UNSAT/16UNKNOWN. The later analytic certificate resolves one of those UNKNOWN cases under exactly the same source/packet contract; it does not turn the timed-out computation into a solver success. The original programs, registration lock and outcomes are preserved. The local SAT checks for deesse are not whole-paragraph SAT.

## Verification and scope

Before native execution, the primary passed six exhaustive small modular fixtures, five parser cases, nine vocabulary/space cases and all243five-letter words over a three-letter alphabet for the AABBA check. The independent validator passed ten small fixtures with exhaustive finite keys, including homophony, explicit SPACE, opaque positions, full-string acceptance and modulo27 behavior. The code/input lock was written at00:51:13.910139UTC on16October2026 before any native result or inventory pattern count.

Independent native validation checks source identity and order, all six full inventories, their hashes, all18case outcomes and the exact Tuscan certificates. Positive native witnesses did not occur. No general solver UNSAT needed independent replay. The primary uses a finite string regex; the independent negative encoding uses a minimized finite automaton. Both use Z3 4.15.3, so they are not independent theorem kernels. Manual alignment proof checks are additional posthoc artifacts; their analytic review is distinct from the registered validator.

The source packs are old lossy Unicode-to-ASCII projections, not phonetic transcriptions or complete historical languages. They cover early medieval Latin legal charters, German mixed texts, French prose/fiction, Florentine poetry, Czech mixed texts and Hungarian codices. Their differing dates and genres do not establish an authorial source. The original public provenance and license metadata are retained in gdt001_language_pack_manifest.json. Cached raw packs are not copied into this publication; reproduce their frozen preparation through prepare_gdt001_language_corpora.py and verify the recorded hashes.

GDT001's earlier free whole-group language-model attacks, GDT604's pseudotext result, GDT1323's anagram capacity stop, GDT1324's toy recovery limits and GDT1339's different minim-stream failure remain unchanged. This experiment neither reopens them nor chooses a source language. No new image, raw mixed transcript, sealed page, reserve or word meaning was used.

## Decision and reproduction

Stop the timed global solver branch and the declared suffix check. The useful result is a concrete repeat-and-boundary restriction, not evidence for a cipher. Retain the other fifteen cases as unresolved and the writing-bank/directed-form explanation as unpaid. Any further reading proposal must account for these conditional failures without silently changing its source inventory or packet boundaries. There is no automatic longer solver run or next suffix search.

Run `python experiments/yolo/gdt1388_modular_paragraph_vocabulary_support/src/run.py`, then the corresponding `src/validate.py`. The two `check_manual_*.py` commands reproduce the separately planned analytic appendix. The50minute preparation-to-publication budget ends01:32UTC; this is a bounded checkpoint inside the outstanding ten-hour request, not its fulfillment.

Evidence: [registered protocol](PREREGISTRATION.md), [source/input lock](src/REGISTRATION_LOCK.json), [registered outcomes](artifacts/RESULT.json), [validation](artifacts/VALIDATION.json), [pattern certificate](artifacts/PREFILTER.json), [manual alignment plan](artifacts/MANUAL_ALIGNMENT_PLAN.json), [manual independent review](artifacts/MANUAL_ALIGNMENT_REVIEW.json), [manual alignment check](artifacts/MANUAL_ALIGNMENT_VALIDATION.json), [suffix plan](artifacts/MANUAL_SUFFIX_PLAN.json), [suffix result](artifacts/MANUAL_SUFFIX_RESULT.json), [independent suffix validation](artifacts/MANUAL_SUFFIX_VALIDATION.json).
