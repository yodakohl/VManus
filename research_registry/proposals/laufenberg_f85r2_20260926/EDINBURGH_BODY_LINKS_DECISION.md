# Edinburgh Cr.4.6 f.121v body-link source check — pre-access decision

Started 2026-09-26 22:08 UTC; total task limit 40 minutes. Image/metadata access cap: 20 minutes from this note. Source-only, no Voynich access.

## Fixed question and evidence ceiling

The existing KdiH regional entry describes f.121v as a macro-/microcosm composition with a person at the center and red/black lines linking bodily points to planets and zodiac signs. The unknown is whether one institutionally identified, whole-folio image actually shows those endpoints and their relations clearly enough to establish a connected body/planet/sign diagram, or whether the catalogue description is the only available evidence. A positive result would establish a source-side relational program only; it would not identify any Voynich figure, direction, season, or word. A missing/unavailable image is an access gap, not evidence against the catalogue account.

## Exactly three public institutional discovery paths

1. **KdiH exact record, 87.2.5:** `https://kdih.badw.de/datenbank/handschrift/87/2/5`. Use the already retained public scholarly catalogue page only to confirm shelfmark, folio and its explicitly linked digitization route. Do not follow unrelated manuscript or subject links.
2. **UNC Libraries, MacKinney digital collection landing/search:** `https://dc.lib.unc.edu/cdm/landingpage/collection/mackinney`. Search the public collection by both exact shelfmarks `Edinburgh, Royal Observatory, Crawford 9.14.5` and `Cr. 4.6`, then verify any item-level result and folio metadata before considering an image. Do not repeat the previous API endpoint attempt that returned an HTML shell; do not infer an item identifier from its response.
3. **University of Edinburgh Archives and Special Collections public catalogue:** `https://archives.collections.ed.ac.uk/`. Search by `Royal Observatory`, `Crawford 9.14.5`, and `Cr. 4.6`; accept an image only if the institution's own item record binds it to the exact codex and f.121v. This is a catalogue discovery route, not an image URL guess.

No fourth discovery path, guessed IIIF/image identifier, alternate host, private contact, authentication workaround, or access bypass is allowed. Search-result snippets are navigation only.

## Predeclared image choice and stop rule

If one of the three routes yields an accessible, institutionally bound image for **exactly f.121v**, select that one image, record its institutional item/canvas identifier and exact official URL, then inspect the **whole folio only**. Do not inspect adjacent leaves, a crop, enhancement, OCR, or a montage. Record the depicted body-point links and all visible endpoint labels/signs together, including ambiguous, missing, or unmatched links; separate pixel observations from catalogue language. Do not map a line to a body part or planet when either endpoint is unreadable.

If no exact image is accessible within the 20-minute cap, stop image discovery. A final bounded check may quote exact wording from the already cited KdiH description or an openly accessible public scholarly schematic edition reached through one of the three fixed paths; distinguish quotation/paraphrase from native visual observation. Do not repair viewers, use derivative images, or reopen the regional search. Preserve the former UNC-shell failure and every failed public route in the receipt.

## Deliverables

Write `EDINBURGH_BODY_LINKS_REPORT.md` and `EDINBURGH_BODY_LINKS_RECEIPTS.json` in this dossier. Cache any permitted image only under its existing `external_cache/` directory, with relative paths and SHA-256. No registry, state, Git, or other dossier-file changes.
