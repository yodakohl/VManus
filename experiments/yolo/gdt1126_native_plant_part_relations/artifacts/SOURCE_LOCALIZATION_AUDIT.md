# GDT1126 source-localization audit

**GB1 and GB4 have conflicting source-to-tested-canvas joins.** The cached public catalogue directly links fragment54’s f89v2 section to Yale1006234 and fragment240’s f102v1 section to Yale1006253. PVO001 and the frozen1126 admission instead selected1006235 and1006252. No excluded image was acquired/viewed here, no glyph/body was read, and no test is repaired.

| Case | Source-owned catalogue unit | Catalogue2014 scan link | Original1126/PVOcanvas | Consequence |
|---|---|---|---|---|
| GB1 | f89v2,row1:50,51,52,53,54; fragment54 is fifth | [Yale1006234](https://collections.library.yale.edu/catalog/2002046?child_oid=1006234) | 1006235 | Nominated fragment54 is not securely localized in tested canvas |
| GB4 | f102v1,row2:239,240,241; fragment240 is second | [Yale1006253](https://collections.library.yale.edu/catalog/2002046?child_oid=1006253) | 1006252 | Nominated fragment240 is not securely localized in tested canvas |

Cached primary locators: q15.html line862 owns the f89v2 heading and line874 its Yale link; q19.html line1470 owns the f102v1 heading and line1482 its Yale link. [Public q15 section](https://voynich.nu/q15/index.html#f89v2) and [public q19 section](https://voynich.nu/q19/index.html#f102v1) are institutional-image navigation sources; all evidence here comes from already cached bytes, not new page/image acquisition.

The complete relevant catalogue fragment-row lists are:

- f89v2 → 1006234: row1 [50,51,52,53,54]; row2 [55,56,57]; row3 [58,59,60,61].
- f89v1 → 1006235: row1 [62,63,64]; row2 [65,66,67].
- f102v1 → 1006253: row1 [234,235,236,237,238]; row2 [239,240,241].
- f102v2 → 1006252: row1 [214,215,216,217,218,219,220]; row2 [221,222,223,224,225,226,227]; row3 [229,230,231,232,233].

The catalogue defines these numbers as “The fragments of herbs, plants and/or roots have been numbered for (cross-)reference:”. They are editorial reference numbers, not native glyph values or label loci. Source assertions are “Fragment54 appears to be the same plant as on f48v” and “Fragment240 appears to be the same plant as on f19r”; each remains a human coidentity hypothesis. Fragment54’s label ownership was already explicitly ambiguous in SNPL001: under[1,4]/next to[1,5]. The nominal historical loci f89v2.6 and f102v1.17 are retained without new glyph/current-locus remapping.

The original tested1006235 belongs to catalogue f89v1, with3+3 numbered objects, whereas fragment54’s source section has5+3+4. Original1006252 belongs to catalogue f102v2, with7+7+5 listed numbers; fragment240’s actual source section has5+3. These are metadata-only source inventories, not this agent’s visual object counts. Missing228 in the cached f102v2 lists is preserved; no number is invented.

PVO001 hardcoded logical-part assignments and successfully checked their IDs against broad Yale labels. Its pharmaceutical-page set check and institutional ID/label check did not compare each catalogue section’s actual child_oid hyperlink. Labels “89v(part)” and “102v(part)” do not independently establish numbered-part identity. The metadata audit previously treated those assignments as stronger historical bindings; this new direct catalogue-link comparison exposes that limitation.

Whether catalogue and current-transcription conventions differ remains unresolved. This does not change the decisive requirement:1126 needs the exact source-nominated fragment image, not a name-only join. No general transcription/canonical nomenclature repair is made. GDT352’s singular fragment94 and ambiguous116 distinctions, other cases, formal failures and0words remain unchanged.

Close original GB1/GB4 as **invalid source localization**, not an anatomical falsification or repaired PASS. Any later examination of1006234/1006253 requires a separate prospectively registered access/test and constitutes new image input; it cannot rescue original1126. All local source pins and raw extracted row metadata are in the JSON.
