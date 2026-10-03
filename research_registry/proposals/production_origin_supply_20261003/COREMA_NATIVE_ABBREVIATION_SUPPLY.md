# CoReMA original TEI: usable abbreviation supply, with editorial limits

Source-only review, 3 October 2026. No learner, target query, image inspection, or contact was performed. The companion `COREMA_NATIVE_ABBREVIATION_SUPPLY.json` freezes retrievable-byte receipts and two complete original XML fragments.

**A useful representation is available in a previously known corpus.** The University of Graz's [original B4 TEI](https://gams.uni-graz.at/o:corema.b4/TEI_SOURCE) transcribes Berlin, Staatsbibliothek, Ms. germ. qu. 1187, dated 1437–1475 in its manuscript description. It contains 269 top-level `seg` records and 1,174 `abbr` elements. Of these, 1,164 contain supplied `ex` text and an explicit abbreviation `am/g` reference; ten lack both, and one abbreviation contains internal uncertainty markup. These are edition segment counts, not certification that every manuscript recipe survives complete. The text header licenses transcription reuse under CC BY 4.0; facsimiles have a separate license and were not acquired.

The literal schema is `abbr/ex/am/g`, rather than paired `choice/abbr/expan`. This preserves the needed distinction:

```xml
<abbr>gepratt<ex>e</ex><am><g ref="#bar_e"/></am>n</abbr>
```

Ordinary written carriers surround a sign reference; `ex` supplies omitted letters. A written view can omit `ex` while retaining `am/g`; an expanded view can retain `ex` while omitting `am`. Both views must preserve ordinary glyphs, revisions, uncertain text, line/page breaks and unmatched nodes. Neither a flat `itertext()` string nor the site's slightly normalized display is an untouched native transcription. The [editorial declaration](https://gams.uni-graz.at/o:corema.editorialdec) explains its conventions; the [character declaration](https://gams.uni-graz.at/o:corema.chardec/TEI_SOURCE) provides the referenced signs.

**The raw reference names leak expansion answers.** `bar_e`, `bar_m`, and `bar_n` each have glyph name COMBINING OVERLINE and codepoint U+0305, but their normalized mappings are respectively `e`, `m`, and `n`. Treating those three IDs as distinct unknown native signs would give a model editorial information absent from the documented visible sign. A future unknown-input protocol would need a frozen, shape-based representation drawn from the declaration, with value-bearing IDs/mappings withheld. This report implements no such protocol. It also does not claim that the editor's glyph classes retain every manuscript allograph or precise placement.

The deterministic first two top-level B4 entries supply complete bounded examples. Their exact source-byte slices, XML, and all 20 paired abbreviation instances are retained in the JSON; no spelling was repaired or a recipe chosen for model fit.

| Entry | Scope | Abbreviations | Shared written-sign evidence |
| --- | --- | ---: | --- |
| `/TEI/text/body/ab/seg[1]` | 071r.N002–071v.N012 | 10 | `bar_e` across gepratt-, Erst-, leczellt-, pratt-, versied- and prat-; also `bar_m` and `lbbar` |
| `/TEI/text/body/ab/seg[2]` | 071v.N013–071v.N024 | 10 | `bar_e` across Repphun-, schuepp-, pratt-, hecht- and prott-; `bar_m` in form- and `bar_n` in vo-/holczer- |

Both end with serving instructions and an explicit closing `seg`; neither contains `unclear`, `supplied`, or `gap`. The first crosses a physical page; the second preserves its out-of-line heading anchors. Their locators are edition positions, not invented manuscript node IDs. The source recipe meaning is already readable German; these records do not independently translate a hidden sign system.

B4 original XML is 496,931 bytes, SHA-256 `ca890ca0820c1ec6b1cb713eeb75cda77a2c580d017c0fa8fcbb813da068938f`. The character declaration is 78,834 bytes, SHA-256 `09d35185befb273eb13d95fc4d8054afc5c358dc0caada03eb20f51e70ec3945`. The JSON also records successful original-TEI retrievals for B6, Br1, Bs1, Gr1, and W1, without claiming every abbreviation in those streams is usable.

This is **not a new corpus or a rescue of an old result**. GDT155 already admitted CoReMA Ste1's 33 abbreviations; GDT176 and GDT1159 already used the six collections' recipe derivatives. Those owned `*.recipes.xml` files contain no `abbr` or `expan` elements. The newly inspected original streams retain substantially different writing information. GDT755's John-of-Burgundy card supplied no XML cache; the preceding availability review found the named public code repository lacked its required records. IDEA864's contextual ending ambiguity and IDEA865's incomplete native-channel limits remain unchanged.

The smallest justified next action is to hand-enumerate the common written overline's carrier-to-expansion relations in these two complete recipes, keeping its documented identical shape across `e/m/n` restorations and the ten corpus anomalies separate. That could constrain a source writer hypothesis. It neither supplies an unknown target candidate inventory automatically nor authorizes a decoder, new target access, or a claim that historical abbreviation explains Voynich writing.
