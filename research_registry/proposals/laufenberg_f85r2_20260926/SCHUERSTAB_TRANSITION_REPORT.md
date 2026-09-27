# Schürstab transition: exact canvases obtained, visual sequence inaccessible

2026-09-27 UTC. The fixed eight-surface source study was **not completed**. The official manifest resolved every requested folio, but the single full-image retrieval batch timed out; four images completed locally. No manuscript image was opened. The decision's access-gap stopping rule was applied: no retry, alternate rendition, replacement folio or repair chain followed. No RAW was added.

The [decision](SCHUERSTAB_TRANSITION_DECISION.md) fixed32v,33r,33v,34r,34v,35r,35v,36r before pixels. The [receipt](SCHUERSTAB_TRANSITION_RECEIPTS.json) binds the decision, manifest, exact canvas/resource URLs and successful image bytes. External cache files are not intended for publication.

## What the metadata establishes

The [official e-codices manifest](https://www.e-codices.ch/metadata/iiif/zbz-C0054/manifest.json) has distinct canvases labelled with all eight folios, each3248×4488. The [institutional catalogue](https://www.e-codices.unifr.ch/de/description/zbz/C0054/) places the heavens at32v–34r, temperaments at34r–36r and medical material beginning36r. It identifies a celestial interpreter on33v and temperament illustrations at34v,35r,35v,36r. These remain catalogue assertions in this task. Calendar localization is Nuremberg; Zürich is the present holding institution, not evidence of original Upper-Rhine production.

| Fixed surface | Official canvas | Download status | Native status |
|---|---|---|---|
|32v|[32v](https://e-codices.ch/metadata/iiif/zbz-C0054/canvas/zbz-C0054_032v.json)|First yielded request timed out|Not viewed|
|33r|[33r](https://e-codices.ch/metadata/iiif/zbz-C0054/canvas/zbz-C0054_033r.json)|No completed file|Not viewed|
|33v|[33v](https://e-codices.ch/metadata/iiif/zbz-C0054/canvas/zbz-C0054_033v.json)|Complete full-region JPEG cached|Not viewed|
|34r|[34r](https://e-codices.ch/metadata/iiif/zbz-C0054/canvas/zbz-C0054_034r.json)|Complete full-region JPEG cached|Not viewed|
|34v|[34v](https://e-codices.ch/metadata/iiif/zbz-C0054/canvas/zbz-C0054_034v.json)|No completed file|Not viewed|
|35r|[35r](https://e-codices.ch/metadata/iiif/zbz-C0054/canvas/zbz-C0054_035r.json)|Complete full-region JPEG cached|Not viewed|
|35v|[35v](https://e-codices.ch/metadata/iiif/zbz-C0054/canvas/zbz-C0054_035v.json)|Complete full-region JPEG cached|Not viewed|
|36r|[36r](https://e-codices.ch/metadata/iiif/zbz-C0054/canvas/zbz-C0054_036r.json)|No completed file|Not viewed|

A live directory listing initially showed three completed images. The final inventory found a fourth,35v, completed during batch shutdown; the table and receipt use the final bytes, and the preliminary three-image message is superseded.

All eight requests were submitted as one bounded batch with four workers. Only the first yielded exception was retained, so missing files other than32v are not individually diagnosed as HTTP failures. Partial retrieval does not establish permanent unavailability of the digital images.

## Predecessor and consequence

The current route, pictures topic and bounded registry/route searches preceded selection. The existing [regional report](REGIONAL_COMPOSITE_REPORT.md), [external source report](EXTERNAL_SOURCES.md) and [combined report](REPORT.md) label C54 catalogue-only. Targeted dossier checks found no earlier native receipt for these pages. This does not assert exhaustive historical non-exposure. Imported HIST:620985bb3f648549 points to an absent primary report; its broad compendium classification and strict-source-identity limitations remain imported claims, not revalidated evidence here.

The source question remains concrete: do the written transitions name a relation from celestial organization or elemental qualities to a person's complexion and appropriate medical conduct? Catalogue chapter adjacency does not settle that question. Neither the figure's catalogue label nor the four temperament entries establish an annular diagram, a single combined scene, a seasonal/life-age sequence, or an explicit causal chain.

The next source decision, if separately authorized, would concern access to the same fixed surfaces or native examination of the already cached subset with the incompleteness explicit. This task makes no such new selection. The complete source unit and its textual owners remain uninspected, so no novel content architecture, absence of links, source copying, Voynich provenance or target meaning is claimed.

No OCR, crops, montage, target text/pixels, current draft/result, reserve, contact, semantic test or registry mutation. Completed with an access-gap report within the35-minute ceiling.
