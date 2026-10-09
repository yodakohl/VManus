# V81 R1 Phase-1 historical-source report

## Frozen outcome

R1 freezes six exact, source-first entry↔code rows from a previously unused Este diplomatic key dated at Milan on 23 June 1435. The key was issued to Ugutioni de Abbatia, secretary of the Marquis of Este, and therefore falls inside both the required 1370–1450 window and the preferred North-Italian court/diplomatic setting.

Historical-key identity: `ESTE_MODENA_MO1_1435-06-23_UGUTIONI_DE_ABBATIA`.

The inventory is:

- `experiments/yolo/sidequest_theory_candidates_v81/V81_R1_SOURCE_INVENTORY.tsv`
- six data rows, each marked `EXACT_ENTRY_CODE_PAIR`
- SHA-256: `9ef4d4e265aa2d39042773b2ffa91a82e01787dfcff93e1a5ab88fc189eeb549`

No row is a reconstruction, decipherment, target-side suggestion, or English/German translation.

## Primary documentary source and provenance

Aloys Meister, *Die Anfänge der modernen diplomatischen Geheimschrift: Beiträge zur Geschichte der italienischen Kryptographie des XV. Jahrhunderts* (Paderborn: Ferdinand Schöningh, 1902), p. 35, “Modena, Beispiele: 1.”, with archival citation in p. 35 n. 3.

The printed heading is:

> MCCCCXXXV die XXIII junii. In Milano.  
> Zifra datum [!] Ugutioni de Abbatia segretario ill. dom. Marchionis Extensis.

Meister's archival citation is preserved as printed rather than silently modernized:

> Canc. duc. Arch. proprio Mappe II. Nr. 1.

Repository as cited by Meister: `Modena, Staatsarchiv`. Expanded collection wording from his Modena survey on p. 33 is `Cancellaria Ducale, Archivio proprio`; the item-level pointer for this key is the p. 35 n. 3 citation above.

Stable institutional record and locators:

- persistent record: `urn:nbn:de:hbz:6:1-143638`
- exact edition page 35: https://sammlungen.ulb.uni-muenster.de/hd/content/pageview/3076041
- complete ULB Münster scan object: https://sammlungen.ulb.uni-muenster.de/download/pdf/3075984.pdf
- exact ULB page-image object used for visual verification: https://sammlungen.ulb.uni-muenster.de/hd/download/webcache/2000/3076041

Source-object bindings, retrieved 2026-08-22:

| Object | Bytes | SHA-256 |
| --- | ---: | --- |
| Complete 83-leaf ULB PDF | 17,927,155 | `8cc91d4ed9ba4c7bf0ca6be46f2cc2d30e9a217366ff34d7d4ab02bfeb688cd6` |
| Exact p. 35 ULB JPEG, 2000 × 2617 | 590,651 | `fc91ed09a987b80d3ac9875c657f6fc62ab006288db476c25fe30d10ea5eec29` |

The edition page is scan leaf 48 in the complete PDF and `[47] 35` in the ULB page selector. The institutional page URL above resolves directly to printed p. 35.

## Row-selection rule

Only characters printed in ordinary roman type and visually unambiguous in the institutional 2000-pixel page object were admitted. The frozen pairs are:

| Exact entry | Exact printed code |
| --- | --- |
| `Q` | `4` |
| `Que` | `hs` |
| `Qui` | `s4` |
| `Quo` | `8o` |
| `e duplicatum` | `14` |
| `s duplicatum` | `zor` |

For `Quo → 8o`, the second character is retained as the printed lowercase roman `o`; it is not normalized to zero. Case and order are otherwise preserved exactly.

Two adjacent edition rows were deliberately not frozen: `Qua` has a raised small-o/small-circle code element whose lossless Unicode normalization is not certain, and `che` has a b-like opaque graph that should not be flattened to an ordinary letter. The three manuscript-style cipher-alphabet rows and the `Nihil importantes` signs were also excluded because plaintext Unicode would not preserve their exact graphs. This leaves a small but auditable inventory instead of inferring values from resemblance.

## Previously-unused-key check

The historical-key identity columns of the permitted V77 historical-source-only corpus tables were checked solely for duplicate keys. Those tables contain the previously used Lavinde 1379 keys 13 and 26; Mantua keys headed `Cum Paulo` (1395) and `Cum Simeone de Crema, Zifra ultima` (1401); the Mantua 1404 numeric nomenclator; the post-1412 Pisan-papal/Canetoli material; Florence Fi1 (1414); and the Pisa 1442 identities. They do not contain the 23 June 1435 Este/Ugutioni key. No V77 target or occurrence data was consulted.

## Phase boundary and blinding declaration

This report and its inventory were completed before any V81 target/card manifest was opened. R1 did not open any V80 artifact, V81 target/card manifest, Voynich occurrence table, sibling output, manuscript page/image/transcription, or f84/f84r material. The exercise remains a historical-source freeze only; no target comparison, semantic licensing, or Phase-2 decision has been attempted.
