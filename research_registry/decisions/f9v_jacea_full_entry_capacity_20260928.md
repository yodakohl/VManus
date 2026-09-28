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
