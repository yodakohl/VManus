# GDT1300 — complete message recovery, failed held-form screen

**FIXED_CODEC_SCREEN_FAILED.** The frozen canonical-pair writer recovers all four complete source texts exactly, with838actual output lookup entries below the1200cap. Nevertheless it fails the whole fixed screen on every source/reader combination. It is not a selected Voynich construction, key, word meaning or translation. No parameter, table or source repair followed the result.

## A complete rule instead of an invented glossary
The writer converts ordinary source characters to a continuous Huffman bitstream, including one explicit END. It then uses a small family of code tables to select the number of written pieces and their head/interior/tail realizations. The sixteen learned pairs are:

    dy  ok  qo  ai  in  ed  ee  che  ol  ey  ii  ke  ot  ka  da  she

Here che and she are each TWO of the declared working units(ch+e,sh+e), not three Latin letters. The vocabulary also retains all22single units. A fixed greedy rule resolves overlap, and its forbidden boundary combinations make the emitted token sequence recoverable. The decoder obtains the piece count from the written whole, reconstructs the same context-specific bit codes and restores the source text through END. Zero padding finishes only the final word; extra zero words are rejected.

No table assigns a whole Voynich word an English or German meaning. These are synthetic outputs under a constructed key learned from exposed TRAIN material. Original spaces and recipe line breaks are source characters in the bitstream; output spaces delimit coding groups, not original words. The input is the unchanged old1177textual projection, not all original editorial/manuscript metadata. Any finite new string over the fixed37-entry source alphabet (including END) is supported; no whole-source-word vocabulary is stored.

Training used9,325strict ZLgroups on odd physical leaves. The model and its hash were saved before scoring even-leaf material or generated-source statistics. The fixed old1264binary contrast supplies only a structural table selector; m uses a declared pooled fallback, not a newly inferred phonetic class. The even panels contain10,007ZL/11,662IT/10,032RFgroups on46leaves each; the first8,000in predeclared natural order enter each comparison. All material was historically exposed, and the readings are alternatives of one manuscript.

## Actual table cost and complete readback
There are24distinct filtered output code tables containing838token-to-bit entries, plus37source-character entries and13piece-count entries:888binary lookup entries overall. The16pair definitions,22class labels, eight38-element weight rows and role/filter rules are additional explicit key information. Reporting only the few weight rows would conceal the reader's actual lookup work. Historical use and human speed were not demonstrated.

| Fixed source | Encoded words in full output | Source bits including END | Zero padding | Exact full recovery |
|---|---:|---:|---:|---|
| b4 |30,436|410,456|36|yes|
| w1 |28,433|381,687|4|yes|
| bs1 |35,156|472,921|3|yes|
| gr1 |33,842|455,160|13|yes|

Together these preserve all1,054projected recipes/80,931stored words and their declared separators. The source character table uses pooled character counts, not source word sequences or a concealed plaintext dictionary. The independent validator recovers the exact source bit prefixes and checks that END lies in the final word, with only zero padding afterward.

The invented teaching messages `nimm wasser`, `nimm kein wasser` and the empty message all return exactly. They use4,7and2synthetic coding groups respectively. These are tests of preservation, including an explicit negation and empty input; none is a proposed reading of manuscript text. Synthetic examples and outputs are labelled as such in EXAMPLES and SYNTHETIC_TEXTS.

## Statistical result
The original1174ten tolerances and1194strengthening were applied to this newly declared even-leaf8,000group sample. They are engineering tolerances, not pvalues or universally portable bounds. There are16reported conditions because both the original loose and stricter edit-one conditions remain visible; they are not16independent tests.

| Source | Conditions within bounds: ZL / IT / RF |
|---|---|
| b4 |10/16,9/16,8/16|
| w1 |10/16,9/16,9/16|
| bs1 |10/16,9/16,9/16|
| gr1 |10/16,9/16,9/16|
| Fair-bit control (not a source message) |8/16,8/16,9/16|

Every book also fails the basic ten-condition conjunction. A partial count of passes is not a statistical fit. The main ZLcontrasts make the failure concrete:

| Metric | Held ZL | Four actual-source outputs | Fair-bit control |
|---|---:|---:|---:|
| Mean working-unit length |4.563|4.630–4.681|4.648|
| Length standard deviation |1.527|1.973–2.049|1.962|
| Type fraction |0.2704|0.3100–0.3150|0.4515|
| Conditional glyph entropy, bits |2.098|2.822–2.857|2.841|
| Whole-word entropy, bits |9.437|9.995–10.092|10.746|
| Adjacent identical words |1.305%|0.085–0.100%|0.228%|
| Adjacent edit-one words |4.802%|1.152–1.396%|1.253%|

Mean length, letter-frequency shape and q-followed-by-o can look plausible while stronger within-word and between-word dependencies fail. The generated length spread is too wide, conditional glyph entropy is too high, and immediate equal/near-equal words are too scarce. These are deficiencies of this fixed writer, not proofs that one particular alternative mechanism or semantic reading is correct.

A limited control observation is positive: actual natural-language source bits reduce output diversity and whole-word entropy substantially relative to fair bits under the SAME key. All four actual-source type fractions meet the ZLtolerance, while the fair-bit type fraction does not. Thus a random-bit surrogate would not correctly represent this writer's actual text-driven output. This does not rescue its failed joint screen. Huffman code probabilities are dyadic; the input code does not make natural text bits independent or fair. The single seeded fair control is not an uncertainty estimate or a semantic message.

## Validation and decision
Before empirical execution,7,224source-free token sequences verified the greedy boundary criterion,31toy messages including empty input roundtripped, and an added all-zero word was rejected. The producer reviewed the general proof before looking at any empirical file. Its one-pair precedent1253remains acknowledged; ordinary legal form coverage is not a new manuscript result.

The independent validator imports neither producer nor codec. It reconstructs odd-leaf counts and Huffman tables by a different merge implementation, finds the unique canonical tokenization by constrained parse search, checks complete source recovery/minimal completion, and recomputes8metric decks and15comparison decks with separate entropy/edit-distance formulas. All pass. This verifies software/source accounting, not a historical key or meaning.

Decision: retain a fully specified modern synthetic control with a clear measured failure. Do not increase pair count, add higher-order or whole-word tables, alter smoothing, whiten source bits, relax thresholds or select a different corpus as an automatic continuation. Any later design must explicitly confront both the internal ordering and adjacent whole-form discrepancies. Existing positive component findings and known whole-form effects remain; no native interpretation is selected here.

No new image, raw TSV, source corpus, reserved page or semantic relation was accessed. f84/f84r/f116v remain excluded. The trained key, source/control outputs, protocols and validator are retained for replay and privacy-checked publication.
