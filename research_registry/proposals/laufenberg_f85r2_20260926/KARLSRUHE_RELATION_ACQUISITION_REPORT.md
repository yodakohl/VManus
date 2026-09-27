# Karlsruhe source acquisition: no changed passage obtained

2026-09-27. Registered at 14:49 UTC; acquisition stopped at 14:57:31 UTC,
within the ten-minute acquisition allowance. The inclusive sixty-minute budget
is a ceiling, not a claim of time worked. Outcome:
**NO_CHANGED_SOURCE_TEXT_ACQUIRED**. This closes this acquisition, not the
Laufenberg hypothesis or all possible access to an edition.

## Actual consequences of the registered alternatives

| Route | Observed result | Decision |
|---|---|---|
| Higher-resolution Karlsruhe platform91v, canvas5967406 | Official IIIF service declares2160×2666 full dimensions. Largest listed size is also2160×2666. The prior receipt records a natively inspected2200×2715 rendition. | A larger size request to this same service is enlargement, not additional source resolution. No image requested. |
| Higher-resolution Karlsruhe platform92r, canvas5967407 | Same dimensions and prior2200×2715 exposure. Both services explicitly support `sizeAboveFull`. | The later1000px inspection did not make2200px new evidence. No image requested. |
| Menge1976 critical edition | Bibliographic lead already known. Catalogue access timed out; its linked contents endpoint also failed. No edited verse text or exact apparatus for this unit was obtained. | Access gap; no substitution of an editorial reading for Karlsruhe. |
| Jentsch1908 older study | Institutional catalogue search confirms the bibliographic reference. Search also located a scholarly description of its Munich picture-instruction excerpts; no actual edition passage was acquired. | Navigation only, not a newly read textual witness. |
| Zürich C102b comparison | Prior project report and the CIMA41 introduction identify the separate witness and complexion-prologue locator. Previous project work already inspected its physician passage. No new manuscript page opened here. | It cannot silently fill Karlsruhe gaps. No expanded witness/image acquisition. |

Primary metadata: [91v](https://digital.blb-karlsruhe.de/i3f/v20/5967406/info.json),
[92r](https://digital.blb-karlsruhe.de/i3f/v20/5967407/info.json).
The dimensions describe the currently served image resources; they do not
prove that the institution holds no higher-resolution archival master or
that a future rescan cannot help. No enhancement, OCR, crop or fresh native
inspection occurred. All33 previously inventoried baselines retain their old
readings and gaps. Zero baselines newly transcribed is not33 failed readings.

Edition navigation: [SLUB catalogue](https://katalog.slub-dresden.de/en/id/0-1605366439),
[linked contents](https://swbplus.bsz-bw.de/bsz005691842inh.htm),
[BLB historical catalogue](https://digital.blb-karlsruhe.de/download/pdf/1014456.pdf),
[CIMA41 introduction](https://www.omifacsimiles.com/brochures/cima41.pdf).
The SLUB failure repeats an already recorded delivery failure. That request
was unnecessary overhead, not a new research finding or grounds to retry.
Search responses did not provide a complete internet census; no claim that
the edition is unavailable everywhere follows.

## What the source comparison already knows, and what did not change

The complete1491 print argument was already read in
[PRINT_ELEMENT_PASSAGE_ROOT](PRINT_ELEMENT_PASSAGE_ROOT.md). Those source
relations are positive prior knowledge, not new findings of this turn:

| Existing relation | Existing f85 constraint, from GDT1043 and the ownership review | New consequence this acquisition supplies |
|---|---|---|
| Fire/warmth, water/blood/moisture, earth/flesh/bone, air/breath | No written link from a target token to the vessel's contents, a body material or an element. | None; no corresponding word can be selected. |
| Everyone contains a mixture; predominance varies between people | The target's four figures are not established as four mixtures or four patients. | None; cannot turn figure count into a four-entry plaintext. |
| Contrary qualities can cause illness; appropriate regimen differs | East is compatible with vessel inspection, but a depicted examiner, a described patient and an instructional speaker remain different owners. | None; no participant binding was acquired. |
| Year/body analogy and seasonal instruction | Plant, support/strand and raised vessel are retained attributes; North's role and exact season assignments remain open. | None; no WINTER/SUMMER or source-order assignment follows. |

This table compares **existing reports**, not fresh target observations.
The source's actual mixture/regimen argument remains useful historical
content. A clean transcript of the same known relations alone would still
leave target ownership unbound. That is why another freely authored f85
dictionary is not the next consequence of this acquisition.

The narrow conjecture that simply requesting a bigger Karlsruhe rendition
would supply new source detail is not supported by the service metadata.
No semantic candidate was tested or refuted here; no competing meaning was
selected. Zero confirmed words were added. No significance calculation or
independent confirmation is claimed.

## Exposure, dependencies and stopping decision

Root knew the earlier tentative Karlsruhe words, the separate print argument,
and the previous ownership review. The old2200px exposure was disclosed in
the registration before this lookup. Search results also included a previously
encountered Voynich-forum title/source snippet; its body and images were not
opened or adopted as evidence. This was not blind source discovery.

The bounded parallel supplier inspected existing proposals only. It added
zero duplicate cards: speaker ownership (IDEA000538), diagnostic specimen
(IDEA000533), and life subject versus physician (IDEA000563) already cover
the useful suggestions it found. It changed no file. Its reasoning supplies
neither a new manuscript observation nor independent semantic confirmation.

Stop the unchanged high-resolution acquisition and the free f85 writer.
Reopening this source attempt requires an actually different scan or accessible
edition passage with its witness identified. A semantic follow-up additionally
needs a stated target consequence under competing ownership accounts. A
written source link between observed sign, its owner and inferred constitution
would improve the source hypothesis, but would still need target attachment.
No source-text reading was obtained which meets that condition in this pass.
No next scientific candidate is selected by this report; the original broader
medical/cosmological tradition hypothesis remains provisional.

## Reproduction and validation scope

[Registration](KARLSRUHE_RELATION_ACQUISITION_DECISION.md),
[structured result and hashes](KARLSRUHE_RELATION_ACQUISITION_RESULT.json),
and the two published metadata snapshots retain the finding. Run:

```sh
python research_registry/proposals/laufenberg_f85r2_20260926/KARLSRUHE_RESOLUTION_CHECK.py
```

It verifies declared service dimensions against the unchanged prior exposure
receipt and frozen input hashes. `--fetch` retrieves only the two metadata
URLs into the untracked external cache; it never overwrites the published
snapshots/result, fetches images, or accesses Voynich material. The first
metadata probes and the retained snapshot requests are disclosed separately
in the result. Validation checks reproducibility/consistency, not the truth
of a reading. f84/f84r, f116v and all reserves remain closed.

Offline metadata, context and registry checks passed. A bounded read-only
artifact review found no concrete inconsistency; it did not independently
verify network requests or meanings. Global preflight still reports the same
eight prior issues: seven unbound GDT600 files and GDT953's missing large-artifact
justification. This work does not claim a globally clean repository.
