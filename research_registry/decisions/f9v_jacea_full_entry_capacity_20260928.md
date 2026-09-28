# f9v: historical Yacea profile and the two `chor` openings

2026-09-28. Exploratory decision after GDT1064; all source/target observations
below were already exposed before this note. This is not a fixed test, a
prospective preregistration, or independent confirmation.

## Question and scope

Can the historically attested pansy use of *Yacea/Jacea* make a specific
whole-entry reading for admitted f9v, beyond a name-shaped first word? Exact
target: f9v's twelve ZL3b lines, with the complete first paragraph at lines
1–4 and the complete second at lines 5–12. Existing `pchor` occurrences were
inspected only through the selector-first TSV guard over the 179 admitted
selectors. f84/f84r and reserves were not opened. No new image key or text
selector was admitted. Historical pages are source comparators, not claims of
direct copying or a 1420 authorial vocabulary.

## Source-written alternatives

| Witness | Owned name | Distinctive written content | Consequence |
|---|---|---|---|
| *Gart der Gesundheit*, Mainz 1485, ch. 432 | Printed `yacea` beside `freyschem krut` under pansy-like image. | The chapter's medicinal quality is reported as hot and moist in degree III, with childhood convulsions, skin trouble and phlegm among uses. A [historical source study](https://www.researchgate.net/publication/304142518_Viola_jacea_Zur_botanischen_Fachsprache_in_der_Renaissance) documents that its verbal morphology does not fully agree with its picture. The full chapter was not transcribed here from the primary print. | The 1485 caption securely supports historical name compatibility, but its contents cannot be projected onto f9v as a fixed template. |
| Fuchs, [*New Kreüterbuch* 1543, ch. 313](https://www.e-rara.ch/download/pdf/29723145.pdf) and [continuation](https://www.e-rara.ch/download/pdf/29723146.pdf) | Explicit Freyschamkraut / Herba Trinitatis / Jacea / Viola grouping. | Distinguishes garden and wild forms; describes five petals, colour variants, warm and dry nature, and applications to breathing, lungs, wounds and itching. | Confirms a later Viola/Jacea usage but **contradicts** the 1485 hot-moist profile. The choice of source changes any proposed quality reading. |
| Guy de Chauliac, *Chirurgie* 1363, as analysed in the [source study](https://www.researchgate.net/publication/304142518_Viola_jacea_Zur_botanischen_Fachsprache_in_der_Renaissance) | `Jacea` occurs. | Classified hot and dry; plant referent is not securely identified as pansy. | Earlier occurrence of the string does not establish the pansy sense around 1420. |

The source study checked named *Circa instans* witnesses without finding an
attested pansy/Yacea entry; this is a bounded negative source review, not proof
that no earlier witness exists. It strengthens the need for a specifically
identified earlier source before treating the 1485 content as contemporary.

## Voynich observations and rival readings

The guarded f9v projection has `fochor` at line 1 and `pchor` at the second
paragraph's line 5. The old GDT757 atlas already records `pchor` as a true
paragraph opener on f9v, f19r, f21r, f52v, f83r and f105v; f86v5 is the one
non-opening occurrence in that seven-row atlas. Thus the f9v pairing is
visually neat but `pchor` is a portable record-opening form. GDT757's f9v
body after `pchor` has content, amount and quality axes but no independently
marked process axis; its “nimm” is an unconfirmed whole-word working gloss.
GDT766 likewise keeps `chor`/`pchor` as role-distinct whole forms, not a
licensed `chor` morpheme or a first-letter cipher.

Two complete record architectures remain observationally equivalent:

1. **Name + treatment:** `fochor` names the pictured Viola-like owner;
   paragraph 1 gives entry information, `pchor` starts a preparation/second
   subentry, and later `ychor` continues it.
2. **Entry address + treatment:** `fochor` is an owner-specific address or
   heading; the same paragraph and `pchor` structure follows without any
   plant-name lexeme in the recovered text.

Neither source gives a necessary position-by-position f9v prediction under
either architecture. The source-written hot/moist versus warm/dry conflict
also prevents choosing a target quality code by source agreement. Neither the
shared visible `chor` sequence nor a presumed name-before-recipe template
resolves the rival. No full passage was translated, and zero words are
confirmed.

## Decision and reopening

Retain GDT1064's narrow positive: bare `Jacea` can historically refer to a
pansy-like plant. Do not select IDEA623/628 as a fixed whole-entry test from
these two late, divergent entries, and do not upgrade `fochor`. Reopen when a
source-owned pre-1450 pansy entry supplies a specific textual relation, or an
independent target relation distinguishes name from address without assigning
unseen words after inspection. A further census of paragraph starts or a
single matching quality word would leave the same decision unchanged.

Predecessors: [GDT1064](../../experiments/yolo/gdt1064_f9v_jacea_historical_synonym/REPORT.md),
[GDT757](../../experiments/yolo/gdt757_initial_formula_role_atlas/REPORT.md),
[GDT766](../../experiments/yolo/gdt766_ofch_chor_role_switch_prediction/REPORT.md),
[IL018 ledger row](../../experiments/semantic_assumptions/ACTIVE_EXPERIMENT_LEDGER.tsv).
The guarded query used `INITIAL_FORMULA_79_OCCURRENCE_ATLAS.tsv` with `page`
as the raw selector, all 179 allow-values from GDT631, output columns
`surface,page,locus,paragraph_start,written_line_eva`, and `--forbid-prefix
f84`: 79 selected, 0 forbidden, 0 outside the allowlist. The separate f9v
query over GDT661 selected all twelve lines and no other page.

## Bounded primary-print check, declared before opening chapter text

Unknown after GDT1064 and the source study: the complete wording and internal
consistency of chapter 432 in the Mainz 1485 print. If its full entry contains
a distinctive, image-linked written relation, the source-capacity judgment for
IDEA628 may change; if it is generic or conflicts with its own illustration,
the existing no-target-binding decision stays. The smallest check is the
chapter and its continuation only, from the institutional facsimile, without
new Voynich access or OCR corpus building. Budget: 25 minutes total for image
location, manual reading, decision, and publication; stop acquisition rather
than expand to another edition at that limit. A source parallel alone cannot
identify `fochor` or justify reading a Voynich passage.

### Primary-print result

Inspected the complete chapter in the [BSB Mainz 1485 facsimile,
335v](https://api.digitale-sammlungen.de/iiif/image/v2/bsb00032739_00674/full/full/0/default.jpg)
and [336r continuation](https://api.digitale-sammlungen.de/iiif/image/v2/bsb00032739_00675/full/full/0/default.jpg).
The red terminal rule on 336r precedes the next illustrated chapter; the
chapter is therefore bounded by these two pages, not just its image page.
Manual reading, normalized only at the level of propositions:

| Source order | Explicit content | Capacity for f9v |
| --- | --- | --- |
| Caption and morphology on 335v | `yacea` / `freyschem krut`; stiff stem, small pointed leaves, flowers in several colours including yellow, blue, white. | A historical alias and descriptive claims, but no Voynich lexeme independently assigned to either. |
| Quality and first application on 335v | Hot and moist in third degree; wine and pressed herb/juice are said to drive out bad fluids and cramps associated with `freyschen`. | More specific than caption alone, but cannot be matched to f9v by a known quality, disease, ingredient, or action word. |
| Continuation on 336r | For affected children, a little of the herb is put in porridge or its water given to drink; then a composite of chamomile, sanicle and this herb is boiled in wine, drunk for eight mornings, with bathing twice over eight days; the entry also mentions distilled water. | Multiple recipe clauses, but neither the f9v two-paragraph division nor `pchor` entails these exact ingredients, dosing, or bath. |

This **does not reopen** IDEA628 as a fixed target test. The complete entry
does supply a recognizable multi-step source sequence, which had been missing
from our direct source inspection. It still has no independently bound f9v
lexemes for chamomile, sanicle, wine, children, eight, bath, or distilled
water. If an all-passage reading later yields such claims independently, this
chapter can be an exploratory comparator, with its 1485 date and the prior
source-image mismatch disclosed. The source is no confirmation of `fochor`
and adds no translated Voynich word. The next sensible source route remains
a specifically identified pre-1450 illustrated Viola/Yacea entry with a
contrastive relation, or an independent target-side name/address discriminator.

### Next bounded source search, declared before inspecting new entries

Unknown: whether one of five named pre-1450 or mid-century illustrated herbal
witnesses (Carrara/Egerton 2020, Belluno/Add MS 41623, Roccabonella, the 1441
Guarnerino herbal, Brussels IV 1024) has an institutionally identified
Viola-tricolor-like entry with its own dated wording and a source-specific
contrast. Finding such an entry could change IDEA628's source-ownership
capacity, but without independent f9v word binding it would remain an
exploratory comparator. No such entry, an identified *V. odorata* only, or a
later marginal identification leaves the decision unchanged. Smallest check:
catalogue/index search for these five named witnesses, then at most two
relevant primary folios; no bulk OCR or new Voynich page. Wall-time budget:
45 minutes including provenance, inspection, decision and publication. The
known [BL Carrara catalogue](https://searcharchives.bl.uk/catalog/032-001982947)
already explicitly identifies f.94r as sweet violet/*Viola odorata*, so it
cannot by itself be counted as the sought wild-pansy witness.

### Result of the bounded five-witness search

The search located **no independently identified pre-1450 wild-pansy entry
with a usable source-written relation**. These are different outcomes, not a
claim that such an entry does not exist:

| Witness | Located evidence | Consequence |
| --- | --- | --- |
| Carrara, BL Egerton 2020 | [BL catalogue](https://searcharchives.bl.uk/catalog/032-001982947) identifies f.94r `De la viola` as *Viola odorata*. | A documented violet, but the wrong species for a wild-pansy owner. |
| Belluno, BL Add MS 41623 | [BL catalogue](https://searcharchives.bl.uk/catalog/032-002085314) dates it 1400–1440. The digitized index folios 142r and 145r were inspected; no unambiguous wild-pansy locator was found. | Incomplete index coverage prevents an absence claim; the bounded scan supplies no owner. |
| Roccabonella herbal | A [Padua study](https://bupd.cultura.gov.it/wp-content/uploads/2023/07/0cd0b741de10d55bc025d869c46a93fd.pdf) reports image transmission from Carrara but no independently identified wild-pansy folio was located in this check. | A derived Viola image, even if located, would need its own taxon and written relation; none was established. |
| Guarnerino, Bergamo MA 592 | The [holding library](https://www.bibliotecamai.org/iorestoacasa-erbario-guarnerino/) dates the signed herbal to 1441 and locates `trinitas` at f.108r. Its [BDL page 225](https://www.bdl.servizirl.it/bdl/bookreader/index.html?path=fe&cdOggetto=5145#page/225/mode/1up) timed out/returned a server error in direct image requests. An [archival reproduction of that same folio](https://www.giuliooraziobravi.it/pdf/Calendario.pdf), page 2, was inspected: three-lobed leaves and small blue, approximately six-petalled flowers are visible. | This morphology supports *Hepatica*-type `erba trinità`, not *Viola tricolor*. The homonymous name is **not** a wild-pansy witness. The reproduction is lower-quality than the inaccessible direct BDL image; the conclusion is visual exclusion at family level, not a definitive modern species identification. |
| Brussels, KBR IV 1024 | Catalogue/search located the manuscript as a *Livre des simples médecines*, but no institutional wild-pansy locator or entry text was recovered within the bounded search. | Missing target entry, not evidence against its existence. |

The Guarnerino image is a concrete warning against matching historical plant
names without their pictured owners: `trinitas` can designate visually
different plants. The 1485 Mainz Yacea chapter remains the only directly
inspected source-written pansy-like entry in this branch. It still cannot
assign `fochor` or any other f9v word. IDEA628's fixed-test decision stays
closed; confirmed Voynich word meanings remain zero. Reopen only on a dated
source entry that independently identifies the pictured *Viola*-like plant
and supplies a contrastive written relation, or on an independent target-side
name/address discriminator.

### Fixed image-capacity check for IDEA621, declared before the contact sheet

Unknown after GDT1063: whether any of the **fourteen already admitted Herbal
image keys** f2r, f4r, f6v, f9v, f10r, f11r, f13r, f17r, f18r, f20v,
f21r, f24v, f31r, f32v depicts a second plausible *Viola*-family owner.
This can change only IDEA621's visual-owner capacity, not establish a word.
The smallest check is one complete labeled contact sheet from the already
cached Yale renditions, followed by targeted inspection of any image with
individual five-petalled flowers **and** compatible simple leaves/stipules.
No Voynich prose is opened until all fourteen image judgments are written.
The known counterexample is GDT1059: `kooiin` heads visually different f2v
and f29v, so even a repeated head would not prove a plant name. Also GDT1063
has already found exact `fochor` only once in the 179-selector corpus: the
literal-repeat form of IDEA621 has no current capacity, irrespective of
visual findings. A productive change would require a predeclared, independently
licensed whole-form relation rather than post hoc substring matching.
Budget: 35 minutes for sheet, manual judgments, scope check, decision and
publication; no new image admission, OCR, embedding search or classifier.

#### Complete admitted-image result

The fourteen cached, admitted folio images were inspected together in one
labeled contact sheet; f10r, f11r and f24v were then viewed individually
because their blue flowers are the nearest superficial alternatives. These
are observations of drawn traits, not modern species identifications.

| Image keys | Visible reason they do not supply a second f9v-like owner |
| --- | --- |
| f2r, f17r, f18r, f31r | Terminal clustered/spiky heads rather than the f9v separate five-petal blue-and-pale flowers. |
| f4r, f21r | Tiny distributed branch structures, no corresponding showy five-petal flowers. |
| f6v | Round dark heads with radiating green structures, no f9v corolla. |
| f10r | One large blue composite-like head with a patterned centre and broad toothed leaves; not f9v's separate asymmetric flowers and lanceolate leaves. |
| f11r | Dense mound of many small blue narrow-petalled flowers, multiple thick root stems; no f9v blue-and-pale flowers or its simple/stipule leaf combination. |
| f13r | Large rounded leaves and a very small terminal blue structure; no repeated f9v-like individual flowers. |
| f20v | Thin grasslike leaves and scattered small blue marks; the f9v leaf and flower combination is absent. |
| f24v | Large blue funnel/irregular blossoms above round long-stalked leaves and tuberous roots; neither f9v's corolla form nor its leaf arrangement. |
| f32v | Dark blue trumpet/star-like flowers and deeply lobed leaves; no f9v combination. |
| f9v | The reference itself: several individual blue/pale flowers with five unequal petals and mixed simple/divided leaflike parts (GDT1063). |

Within this **complete fixed fourteen-image set**, no second independently
plausible *Viola*-like owner survives the declared two-trait screen. The
screen has limited botanical resolution and says nothing about unadmitted
images. More decisively for the literal form of IDEA621, `fochor` was already
unique in all 179 admitted text selectors before the images were viewed; an
exact shared-whole test is impossible with the current corpus. The scan
therefore changes IDEA621's **capacity** to `NOT_TESTED_NO_SECOND_OWNER`, not
the truth of the name hypothesis. The f9v C0 illustration/name reading
remains replaceable; no Voynich word is confirmed.

### Historical-name chronology check after the bounded source search

Ute Holtzegel's [2016 specialist study, pp. 181–183](https://www.researchgate.net/publication/304142518_Viola_jacea_Zur_botanischen_Fachsprache_in_der_Renaissance)
surveys the older *Circa instans* witnesses Egerton 747, Harley 270 and
Sainte-Geneviève 3113, the older German Macer (Heidelberg Cpg 369),
Megenberg, and selected ancient authorities. It reports no independently
identifiable wild-pansy/Yacea entry there. It distinguishes Puff von
Schrick's 1478 **unillustrated and undescribed** Freisam remedy from the
1485 *Gart*'s first described/pictured Freisam entry; its direct analysis
also notes that the *Gart* stem, leaves and color wording fit the pictured
plant imperfectly. This is a **bounded scholarly survey**, not a proof of
historical nonexistence or a new Voynich negative test.

The consequence is chronological: the 1485 `yacea` alias demonstrates that
the term *could* name a pansy-like illustration in a later German herbal, but
cannot be projected back to a c.1420 Voynich writer as an inherited plant
name. A pre-1450 same-name hunt now has a documented prior-capacity problem,
in addition to this branch's five-witness result. The visual *Viola*-like
f9v owner remains C0 and `fochor` remains equally compatible with an opaque
entry address. No target word has gained a meaning.

The same [study, pp. 183–187](https://www.researchgate.net/publication/304142518_Viola_jacea_Zur_botanischen_Fachsprache_in_der_Renaissance)
supplies a positive earlier-name contrast: a fourteenth-century German
Artemisia vocabulary glosses `iacea` with `cigenbein`, a regional cornflower
name, and the fourteenth-century *Sinonoma Bartholomei* relates dark `Jacia`
to knapweed-like names and white `Jacia` to scabious. These identifications
are reported by Holtzegel; the source manuscripts were not independently
verified in this check. They do not make every pre-1450 `Jacea` one botanical
species. Holtzegel argues that several *Gart* synonyms and parts of its
description retain a knapweed/scabious context even where the 1485
illustration depicts pansy; the mechanism of that transfer is uncertain.
Thus the 1485 image/name pairing establishes that a later compiler **used**
`Yacea` for a pansy-like picture, but is weak evidence for a stable c.1420
name convention. The admitted f2r drawing has thistle-like heads and remains
only an unassigned *Centaurea*-type visual rival; neither it nor the source
gloss assigns a Voynich head word.

Chronology is a **prior constraint, not a hard exclusion**. The reported
1404–1438 radiocarbon interval dates the manuscript's parchment, not the
moment its script was written ([radiocarbon account](https://www.voynich.nu/extra/carbon.html);
[Yale's manuscript description](https://beinecke.library.yale.edu/beinecke/collections/beinecke-cipher-voynich-manuscript)
does not supply an independently dated Voynich text). The `c.1420` writer in
this branch is a working historical scenario. A later use of older parchment
is possible, though this branch has no evidence that the f9v text postdates
the 1485 *Gart*. Therefore the *Gart* pairing is not a chronological
contradiction of `fochor ≈ Yacea`, but cannot establish that Voynich usage
either. The independently unresolved name-versus-entry-address distinction
remains decisive.
