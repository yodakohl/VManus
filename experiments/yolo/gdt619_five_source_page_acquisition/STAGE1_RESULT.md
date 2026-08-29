# GDT619 Stage-1 result

Published: 2026-08-29

Status: `STAGE1_RESOLVED__GLOBAL_DELTA_MINUS_ONE__STAGE_B_AUTHORIZED_NOT_EXECUTED`

## Result

The two publicly authorized adjacent-page requests both succeeded without a
redirect and fully decoded at the registered dimensions. Scan 25 is 458,741
bytes at 1200x1733, SHA-256
`bc193b2a31b751d4c538abdd15a5ebe33bf5514ab4f5d31f7b1d01c10be62778`.
Scan 27 is 331,053 bytes at 1200x1847, SHA-256
`b1f2e7c02e5bfa4985190a6564aef397b46da6e12833dabc78142639bf688dd8`.

Manual full-page inspection gives the registered pair:

1. scan 25: `VISIBLE`. The Balsam entry is visibly present; the illustrated
   label reads `Balsami.`. The exact inflection is not used by the decision.
2. scan 27: `VISIBLY_ABSENT`. No Balsam rubric is visible; the distinct animal
   label `bos agrestis` is clear.

The primary reader and two independent manual readers agree on both decisions.
No OCR, automatic image classifier, captioner, embedding, or botanical-image
similarity was used. Under the frozen adjacent-pair rule this uniquely selects
global Clm canvas delta `-1`. The original metadata ordinals
26/76/165/97/102 therefore become 25/75/164/96/101.

## Public resolution packet

`artifacts/STAGE1_RESOLUTION.json` is the canonical output rebuilt from the
saved manifest, request journal, response bytes, and manual observations. Its
SHA-256 is
`95457d96fd7c8e4980c3e92bd1a4ac5009daf27090946b91407bbd476eb0d422`.
The packet contains no private filesystem path or image bytes. Its internal
`PUBLICLY_UNBOUND` status records the pre-publication generation state; this
public material pass is what binds the five literal Stage-B URLs.

An independent audit caught two representation errors before publication.
The packet now computes its minimum BSB spacing from every durable request
intent, including the failed width-only request: 4.000818967819214 seconds.
The registered selected-page schema now correctly describes IIIF `service` as
a one-element list rather than an object. Neither correction changes the
observations, delta, page identities, response hashes, or request history.

The five selected Clm pages are:

| Candidate | Folio | Canvas | Full-page dimensions |
|---|---:|---:|---:|
| DEV01 | f10v | 25 | 1707x2466 |
| DEV02 | f35v | 75 | 1707x2581 |
| DEV03 | f80r | 164 | 1707x2562 |
| DEV04 | f46r | 96 | 1707x2591 |
| DEV05 | f48v | 101 | 1707x2581 |

## Authorization and ceiling

Once this file and the resolution packet are public, Stage B may request only
the five literal Clm URLs in the packet followed by the five frozen Latin 6823
Gallica URLs, in the preregistered order. Stage B has not yet been executed.

This result verifies the Clm locator offset and five source-page identities.
It does not transcribe the five entries, open a Voynich target, establish a
source-to-Voynich relation, or assign any Voynich sign, word, plant, plaintext,
or meaning. `f84` and `f84r` remain forbidden.
