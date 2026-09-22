# Exposed native check of two f82r groups

2026-09-22. **The first group remains ambiguous; the second visibly contains more ink than bare `ra`.** No transcription or semantic model is changed.

The admitted GDT790 image of Yale canvas1006222 was personally viewed natively, first as a whole and then through exact pixel crops. Its2000×2721 pixels and SHA-256 match the existing receipt. This is the already exposed manuscript and an informed model inspection, not an independent witness, blind reading or a claim of palaeographic expertise. No new image was fetched. “Native” means direct model vision; the2000-pixel Yale rendition is not claimed to be the maximum capture resolution.

## f82r.15 / G004 — `qok[ee:ch]dy`

The [target window](TARGET_15_G4_CONTEXT.png) and [surrounding groups](LINE15_G3_G6_CONTEXT.png) preserve the disputed low sequence after the tall medial construction, as well as its rounded/descending ending. Two low open, rounded elements are visible. Their general appearance is compatible with the nearby cached `qokeedy` forms at [13/G003](COMPARE_13_G3_CONTEXT.png), [16/G001](COMPARE_16_G1_CONTEXT.png) and [16/G003](COMPARE_16_G3_CONTEXT.png).

The local cached `chdy` at [15/G009](COMPARE_15_G9_CH_CONTEXT.png) and `chey` at [16/G010](COMPARE_16_G10_CH_CONTEXT.png) show a more conspicuous extended connecting upper stroke. Against those comparisons, the disputed form gives a **weak local preference for the two-rounded-element / `ee` option**. The image does not securely resolve every connection, however. Stroke merging, the writer’s variation and this rendered resolution prevent a reliable exclusion of the `ch` alternative. Comparator spellings were known beforehand; their labels are not newly certified here.

**Decision:** retain `qok[ee:ch]dy`. `qokeedy` is visually compatible, not established as an independently confirmed diplomatic reading. No numerical confidence or vote over selected examples is claimed.

## f82r.16 / G011 — `ra{cty}`

The [target window](TARGET_16_G11_CONTEXT.png) and [whole line-ending context](LINE16_G9_G12_CONTEXT.png) show a short curved/rounded beginning followed by a conspicuous compact complex of upright/looped and connecting strokes, ending with a curved/downward continuation before the separately spaced final `dam`-labeled group. This additional material is visible in the ordinary text run. A transcription stopping at bare `ra` leaves it unrepresented.

No obvious insertion caret, separate interlinear addition, cancellation or drawn braces is identified. The general brown ink is compatible with surrounding writing, but that does **not** date the strokes or establish one writing session. The image alone does not determine whether the complex is an ordinary glyph sequence, a ligature, an abbreviation, an expansion or a later alteration. In particular, the editorial braces in the cached representation are not physical braces visible on the page and do not prove an insertion.

**Decision:** retain the full unresolved `ra{cty}` representation and the visible additional-ink obligation. Do not claim that each of `c`, `t`, `y` has been independently read, that an abbreviation has been recognized, or that its expansion is known.

## Locations, source and limits

The [whole middle-block crop](BLOCK_11_19_CONTEXT.png) keeps lines11–19 and following context. [Rows13–17](ROWS13_17.png) retain neighboring ink around both targets. These are rectangular viewing windows, not claimed exact word/glyph segmentations. Coordinates, purpose, dimensions and byte hashes for every crop are in [SOURCE.json](SOURCE.json); all coordinates refer directly to the original2000×2721 source, origin upper left, right/bottom exclusive. No crop was resized, filtered, sharpened, traced or generated.

Source identity: `experiments/yolo/gdt790_panel_owner_image_grammar_overlay/src/IMAGE_SOURCE_SPECS.tsv`, row `GDT790-IMG-02 / f82r`; JPEG SHA-256 `e9f9a8f97346ebf24b57b3425e038ed2ca1d4f2692f94e52535b5208b8f100c2`. Current whole-page access is documented by `docs/VOYNICH_DATA_SCOPE.md` and GDT791’s `PAGE_SELECTOR_SPECS.tsv`. The record locator is GDT790 `F82_P2`, lines11–19. The exposed GDT928 ZL3b cache supplied group labels; no OCR or new normalized transcript was produced.

Earlier GDT790/P30 inspection concerned panels/layout. W53 declined individual-letter determination. The later `F82R_LINE19_VISUAL` audit did view this whole block, but its detailed questions concerned line19 and its boundary. Thus this is neither a newly discovered manuscript region nor an unchanged repetition of a prior documented adjudication of these two groups.

GDT1015’s diplomatic-coverage withdrawal remains in force. This inspection supplies only a local source observation: weak compatibility at the first group and clearly retained extra ink at the second. It supplies no meaning, no independent confirmation and no main semantic research result. GDT1015 and GDT1039 remain unchanged; f84/f84r and reserves were not opened.

To regenerate the crops, pass an already available image with the recorded source hash to `derive_crops.py`. The script performs only exact rectangular extraction. It does not fetch data, adjudicate writing, expand abbreviations or validate semantic claims.
