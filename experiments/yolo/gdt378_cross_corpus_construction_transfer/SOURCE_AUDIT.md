# GDT378 comparator source audit

This audit was completed before GDT378 detector scoring and before any new
Voynich access.

| domain | source | status | oracle strength | limitation |
|---|---|---|---|---|
| CoReMA | six previously frozen TEI collections | included | editor roles, annotations, parent links | same source already used by GDT376 |
| Cambridge Curious Cures | CUL MS Add. 9308, late 14th/early 15th c., Middle English with Latin | included | fixed high-precision lexical procedural oracle | HTR-assisted diplomatic transcription; one manuscript |
| PCEEC2 | Parsed Corpus of Early English Correspondence 2, exact Git commit | included | constituent parse and POS gold | correspondence, not procedural text; later date span |
| Harleian cookery | MSS 279 (c. 1430) and 4016 (c. 1450), Austin edition | included sensitivity | fixed high-precision lexical procedural oracle | Internet Archive text is OCR of a printed diplomatic edition |
| Quinte Essence | Sloane 73 (c. 1460–70), Furnivall edition | included | fixed high-precision lexical process oracle | edited text; one work rather than independent manuscripts |
| Regiomontanus, *Defensio Theonis* | Dartmouth digital edition | excluded | potentially strong scientific syntax | site says materials are proprietary and cannot be used without permission |
| MEMT | Middle English Medical Texts | excluded | potentially strong medical comparator | machine-readable corpus is commercial/not straightforward |

## Exact public sources

- CoReMA provenance remains bound through the GDT176/GDT376 source manifests.
- PCEEC2: `https://github.com/beatrice57/pceec2`, citation in its README:
  *Parsed Corpus of Early English Correspondence, second edition* (2022).
- Curious Cures collection:
  `https://cudl.lib.cam.ac.uk/collections/medievalmedicalrecipes`; collection
  IIIF manifest `https://cudl.lib.cam.ac.uk/iiif/collection/medievalmedicalrecipes`;
  manuscript manifest `https://cudl.lib.cam.ac.uk/iiif/MS-ADD-09308`.
- Harleian edition: Thomas Austin, ed., *Two Fifteenth-Century Cookery-Books*
  (EETS OS 91, 1888), public-domain scan at
  `https://archive.org/details/twofifteenthcent00aust`.
- Quinte Essence: Frederick J. Furnivall, ed., *The Book of Quinte Essence*
  (EETS OS 16; revised 1889), Project Gutenberg 17179.
- Excluded Regiomontanus edition:
  `https://regio.dartmouth.edu/about/about-project.html`.
- Excluded MEMT catalogue:
  `https://varieng.helsinki.fi/CoRD/corpora/CEEM/MEMTindex.html`.

The Curious Cures project reports that its corpus contains more than 8,000
recipes and that the public transcriptions are produced through an
HTR-assisted workflow.  MS Add. 9308 is independently catalogued as an English
medical recipe collection from about 1390–1410, written in Middle English with
some Latin, with line-level coordinates and paragraph regions in the public
diplomatic service.  Exactly 183 transcript-bearing pages are frozen here.

No unavailable source is silently replaced by a modern summary.  Raw words
remain in the source cache/oracle builder only and are absent from the scored
observation layer.
