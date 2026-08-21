# V10 candidate — picture-owned Herbal monographs with local owner cards

Date: 2026-08-21

Status: independent speculative sidequest candidate. This is not a GDT result,
a decipherment, or a translation. No English word below is assigned to a
Voynich form. `f84` and `f84r` were not accessed.

## Decision

The strongest picture-addressed reconstruction is an **illustrated simple's
monograph written around an already present plant**, not a set of captions
attached to particular leaves and not a rigid page form.

```text
PICTURED PLANT = silent dossier owner
PAGE-LOCAL OWNER CARD = optional repeated textual address/name of that owner
PARAGRAPH 1 = name/synonym/description/quality material
PARAGRAPH 2 = virtues, preparation, application, warning or further properties
PHYSICAL LINE/FIELD = text fragment fitted into remaining canvas space
```

The two best local owner candidates are deliberately anonymous:

| candidate | exact tuple | occurrences in the four-page panel | reason |
|---|---|---:|---|
| `OWNER-10` | `4d4559019a961b834aa1` | 2, both f10r | one occurrence in each of f10r's two records, with different surface wrappers (`char`, `dar`) |
| `OWNER-56` | `2cc054357a929df85f64` | 4, all f56r | distributed through the one long record; twice line-first (`sho`) and twice medial (`cho`) |

`OWNER-10` and `OWNER-56` are **not** claimed to be plant names, pronouns or
the word *herb*. They are the two least bad candidates for a page-local
plant-address packet. They could instead be ordinary high-frequency content or
construction cards sampled locally by chance.

The resulting role allocation is a mixture:

1. plant identity/address is supplied primarily by the picture and optionally
   repeated by a page-local owner card;
2. the remaining opaque cards are most plausibly abbreviated ordinary Herbal
   prose containing some mixture of synonyms, qualities, plant parts, habitat,
   preparation, applications and effects;
3. no fixed card presently distinguishes those content classes;
4. line and Herbal field boundaries are largely physical reflow, not semantic
   slots.

This beats a water-key, four-part checklist, or pure nonsemantic page code
because it explains the long continuous records, the large page-local lexical
tail, the two paragraphs on f10r, and the demonstrably picture-shaped writing
space without requiring that every graphical adjacency be meaningful.

## Frozen observation scope and provenance

The exact-card census uses only guarded selections from the already f84-free
GDT276/GDT327 formal layer:

```text
./vmanus-exp query-tsv gdt276_event_inventory.tsv
  --selector page --allow f10r --allow f56r --allow f11r --allow f55v
  --forbid-prefix f84

./vmanus-exp query-tsv gdt327_joint_tuple_interlinear.tsv
  --selector page --allow f10r --allow f56r --allow f11r --allow f55v
  --forbid-prefix f84
```

The four images were obtained from Yale's public IIIF manifest for Beinecke MS
408, object 2002046. Canvas/image IDs were 1006094 (10r), 1006096 (11r),
1006183 (55v), and 1006184 (56r). The visual judgments below come from those
four pages only.

## Physical ownership before semantics

### f10r

One large plant occupies the lower and right page. The text has two visibly
separated blocks above and to the left of it. Lines in the lower block shorten
where the flower and stem take space. The drawing supplies one page owner; the
blank between text blocks is therefore better read as two paragraphs about one
simple than as a second plant entry.

The same exact `OWNER-10` tuple appears once in the first record (`f10r.2#3`)
and once in the second (`f10r.8#8`). This is the best internal reason to treat
both paragraphs as continuing the same pictured dossier. It is not proof of a
name: the two occurrences could be an ordinary discourse card.

### f56r

One tall plant occupies the right and lower page. Its flower, spiral structure,
stem and large dark/spiny organs force the text into a long narrowing block on
the left. The seven exposed lines belong to one record. Their exposed line
lengths are only 3--5 cards, exactly where available horizontal space is
restricted.

`OWNER-56` occurs at `f56r.5#2`, `.7#1`, `.12#2`, and `.18#1`. Its alternating
line-first/medial realization is compatible with a recurrent owner address or
plant/self reference in continuous prose. It is incompatible with a unique
one-time title and supplies no particular botanical name.

### f11r and f55v controls

f11r puts its exposed text in a block entirely above the plant. It offers no
reason to assign a card to one particular flower, leaf or root by proximity.

f55v is the decisive layout control. The plant's central stem divides the same
physical lines into left and right text fragments; GDT327 accordingly exposes
two fields on both sampled lines. The visual split is sufficient to create a
field boundary. It need not mark two semantic cells. This warns against
interpreting f10r/f56r line ends, gaps or local adjacency as clause boundaries.

Thus the best ownership hierarchy is:

```text
plant picture owns page/record
paragraph owns continuous discourse
plant contour constrains physical line fragments
nearby leaf/flower does NOT automatically own a nearby card
```

## Complete exposed-card accounting

The target panel contains 65 exposed exact-card events: 38 on f10r and 27 on
f56r. The controls contribute 17 on f11r and 18 on f55v. The following is the
complete target sequence; line breaks reproduce source loci, not sentences.

| record | locus | cards | proposed source-class status |
|---:|---|---|---|
| 1 | f10r.2 | `dchey cthoor char chty os chair otytchol oky daiin etyd` | largely opaque identification/description; includes `OWNER-10`, one portable card and current-standard candidate |
| 1 | f10r.5 | `qokchy qotchol chol cthy` | portable Herbal construction ending in relation/property material; not a sentence end |
| 2 | f10r.6 | `ycheor cthy chor cthaiin qoctholy dy chy taiin shy` | property/relation material plus the complete `Y-AIIN-Y` shared-reference frame |
| 2 | f10r.8 | `qotchor chor otol chol cholor chol daiin dar` | relation-rich continuation; `OWNER-10` returns at the exposed line end |
| 2 | f10r.9 | `oykchor shor chor chy kaiiin dy chodaiin` | open continuation/closing material, mostly opaque |
| 1 | f56r.5 | `chochor cho chodaly daiin` | local entry material; `OWNER-56` medial |
| 1 | f56r.7 | `sho kchol otchor choky dal` | `OWNER-56` line-first plus portable/local content |
| 1 | f56r.8 | `schol choy choky cheeckhody` | portable line-entry card plus local content |
| 1 | f56r.12 | `sh cho kchey qokokchy` | `OWNER-56` medial plus opaque content |
| 1 | f56r.13 | `okchy chokcheo kchal` | portable Herbal card plus local content |
| 1 | f56r.18 | `sho chokchy kchoar sotodan` | `OWNER-56` line-first plus portable/local content |
| 1 | f56r.19 | `otchey keol daiin` | opaque final continuation plus current-standard candidate |

All recurrent target cards were forced through all occurrences:

| anonymous exact card | target count | distribution | disposition |
|---|---:|---|---|
| exact Y `b921...` | 5 | f10r only; five surfaces/positions | portable node/pointer deck; not a plant card |
| exact AIIN `2f1c...` | 5 | f10r 3, f56r 2; also controls | current-standard/reference candidate; not page identity |
| exact CHOR `7a4b...` | 4 | f10r only; also f55v | portable relation/card deck; not page identity |
| `OWNER-56` `2cc0...` | 4 | f56r only | leading f56r owner/address candidate |
| exact L/O `dcda...` | 3 | f10r only in target | associative relation candidate; not page identity |
| Herbal card `9ad6...` | 3 | f10r 1, f56r 2 | cross-page practical construction; no content gloss |
| Herbal card `276a...` | 3 | f10r 1, f56r 2 | cross-page practical construction; no content gloss |
| exact CTHY `e0b6...` | 2 | f10r 2; also f11r | property/state candidate; not plant identity |
| `OWNER-10` `4d45...` | 2 | one in each f10r record | leading f10r owner/address candidate |
| Herbal card `1048...` | 2 | f10r 1, f56r 1 | cross-page practical construction; no content gloss |

The remaining 25 target types occur once in the target panel. Sixteen f10r
types and fifteen f56r types occur nowhere else in the four-page panel. They
are the likeliest location of plant-specific names, properties, substances,
operations and applications, but singleton status cannot decide among those
roles.

Only four exact types are shared directly between f10r and f56r, accounting for
13/65 target events: AIIN and the three anonymous Herbal cards `9ad6...`,
`276a...`, and `1048...`. The low exact overlap is expected for two different
plant monographs with a small common construction deck and a large
plant-specific vocabulary. It also fits unrelated copied code, so it is not a
semantic proof.

## Concrete source-class pseudo-translation

Every insertion is marked:

- `P`: independently pictured or inherited;
- `F`: current formal card behavior;
- `S`: speculative Herbal source expansion;
- `U`: content remains unsupported.

### f10r, first complete exposed record

> **P** For the pictured simple: **S** [OWNER-10/name-or-self-address],
> [synonym/appearance/quality material **U**], under the currently stated
> standard **F**. Continue with [a common Herbal construction **F**], associate
> it with the local node **F**, and state its property/condition **F/S**.

Source-class decision: record 1 most plausibly **identifies/describes the
simple and establishes its quality/state**, rather than giving a finished
one-line recipe. Almost all lexical content remains `U`.

### f10r, second exposed record

> **P** Of that same pictured simple, [part/property **U**] is in the stated
> condition **F**. Relate [opaque item **U**] to the two marked nodes under the
> same active standard **F**. Continue with [preparation/use/effect **U**] in
> two associated relations **F**; reuse the stated standard **F** and return to
> OWNER-10 **S**. Add [further use, warning or property **U**].

`OWNER-10` returning in record 2 is the basis for “same simple.” Nothing in the
text establishes which plant part, preparation or disease is meant.

### f56r, one continuous record

> **P** For the pictured simple, establish [name/synonyms/quality **U**]. Invoke
> OWNER-56 **S**, give [property or preparation **U**], and retain the current
> standard **F**. OWNER-56 **S** then participates in [three different
> property/use statements **U**] through the remainder of the paragraph,
> interleaved with the small portable Herbal deck **F**. Finish with [opaque
> application/effect **U**] at the stated standard **F**.

This is intentionally not fluent plaintext. The useful proposal is the
monograph division and owner recurrence, not invented substances or actions.

## Water, habitat and visible plant parts

Water remains a legitimate *source-content* possibility, not the page key.
Medieval Herbal entries can include habitat, and water can occur as preparation
medium, extraction product or place of growth. But:

- neither target drawing shows an independently bounded pond, stream, vessel
  or poured liquid;
- pale blue regions on the parchment are not safe semantic objects and may be
  pigment transfer, wash, bleed or later handling;
- the f10r and f56r cards nearest a leaf, flower or dark organ are placed there
  because those are the remaining places in which a line fits;
- no exact card has a second independently water-owned occurrence in the fixed
  panel.

Accordingly no card is glossed WATER, WET, MARSH, ROOT, LEAF, FLOWER or SEED.
Habitat/water is somewhat more plausible in an identification/description
paragraph; preparation medium is somewhat more plausible in a virtue/remedy
paragraph. Those are genre expectations only.

The conspicuous f10r red root bodies, serrated leaves and blue flower, and the
f56r spiral head and dark spiny organs could motivate description or
part-selection. They do not provide enough independent instances to attach a
card to any one feature.

## Historical fit around 1420

The proposal uses ordinary practices attested around the manuscript's broad
period, without claiming a donor or region:

1. A medieval Herbal entry could mix synonyms, complexional qualities,
   appearance, virtues, recipes and place of growth. The Henry Daniel Project's
   description of the late-fourteenth-century Herbal explicitly lists all of
   these components, and notes that entry organization varies.
   <https://henrydaniel.utoronto.ca/herbal/>
2. Olga Timofeeva's structural study of medieval English Herbal entries treats
   habitat, flowering time, gardening and storage as optional rather than
   obligatory components. This is why WATER/HABITAT must remain possible but
   cannot organize every entry.
   <https://helda.helsinki.fi/server/api/core/bitstreams/9ab6008c-ab1b-44d6-b76e-30d680d7f233/content>
3. The British Library catalogue for Egerton MS 747 shows an integrated
   *Tractatus de herbis* plus an antidotary, dose text, substitution list,
   weights/measures and synonym lists. An illustrated medical Herbal could
   therefore contain identity, descriptive and practical layers rather than
   one uniform prose function.
   <https://searcharchives.bl.uk/catalog/032-001983805>
4. Penn's fifteenth-century northern-Italian Erbario (LJS 419) is particularly
   useful as a production comparison: only about a quarter of its plant images
   received medicinal/preparation notes, and those notes were written around
   or over the illustrations. It demonstrates organic image/text addition and
   unequal entry expansion.
   <https://colenda.library.upenn.edu/catalog/81431-p3n87308d>
5. The Roccabonella *Liber de simplicibus* (Venice, BNM Lat. VI, 59) gives a
   near-period countermodel in which extensive synonym/name apparatus and
   illustration are central. This keeps PLANT IDENTITY and multilingual
   synonymy alive even when the picture already identifies the owner.
   <https://nbm.regione.veneto.it/StampaManoscritto.html?codice=58159>
6. Picture-first is not a universal medieval rule. Scholarship on early
   illustrated Herbals finds both production orders and long-lived traces of
   picture-first design. The fixed Voynich pages themselves, especially f55v,
   are the evidence for picture-constrained reflow used here.
   <https://doi.org/10.1080/02666286.2021.1951518>

The historical mechanism is therefore learnable for a small workshop:

```text
copy/draw plant exemplar
→ open the matching plant dossier
→ copy one or more abbreviated monograph paragraphs
→ repeat a local owner/name card when useful
→ flow the prose through remaining page space
→ use shared relation/reference cards plus a large copied lexical tail
```

No scribe needs a modern database schema or a different card for every leaf.

## Alternatives forced through the same pages

| model | fit | principal failure |
|---|---|---|
| plant identity/name list | medium | plausible owner cards, but 9--19 physical lines are excessive for names alone |
| visible part/property captions | low | text is paragraph-shaped and reflows around pictures; no repeated ownership of the same visible part |
| habitat/moisture/water register | low-medium | historically possible, but no independent water object or repeated water-owned card |
| preparation/action recipe | medium | plausible especially in later paragraph material, but f10r record 1 looks more dossier-like and no action is grounded |
| application/use/condition monograph | high as a component | historically ordinary, but cannot explain the identity/synonym and picture-address layer alone |
| amount/quality classification | medium | AIIN/property cards fit, but the large local tail and paragraph length require more content |
| nonsemantic exemplar/page address | medium-high adversary | explains local cards and workshop copying, but not why extensive text is retained around expensive content-rich plant images |
| abbreviated ordinary prose | **highest in mixture** | explains paragraph continuity and lexical tail; exact source words remain inaccessible |

The selected model is thus `picture-owned abbreviated monograph + optional
local owner card + physical reflow`, not a rigid checklist.

## Risky fixed predictions

These predictions were stated from the selected reading and can make it lose:

1. **Full-record owner recurrence.** In any later authorized complete mapping
   of the already fixed f10r/f56r transcription, `OWNER-10` and `OWNER-56`
   should recur or occupy coherent owner/self-address contexts beyond the
   exposed sample. If they prove to be ordinary placement-only cards with the
   same distribution on unrelated fixed-page material, the owner reading loses.
2. **One plant across f10r paragraphs.** The second f10r paragraph should not
   introduce a second independent plant dossier. A hidden second picture owner
   or explicit record reset would defeat the interpretation.
3. **Canvas rather than semantic field.** Reading order on f55v should continue
   across the left/right fragments produced by the stem more naturally than a
   model treating them as two stable semantic columns. A recurrent semantic
   two-slot opposition on comparable split lines would defeat this.
4. **No local-part dictionary.** Cards immediately beside f10r's flower or
   f56r's dark spiny organs should not uniquely recur beside the homologous
   visible part on f11r/f55v. A prospectively repeated part-owned card would
   defeat the whole-page monograph account and favor captioning.
5. **Water is ordinary content if present.** Any future water/habitat candidate
   must recur across independently water-owned contexts; it should not be
   selected from pale wash or simple nearness on f10r. A single robust repeated
   water-owned card would revise the model toward explicit habitat/medium
   encoding.
6. **Paragraph-functional asymmetry.** f10r's first record should be richer in
   identity/description/quality source material and its second in
   virtue/preparation/application material. If readable external parallels or
   repeated formal evidence reverse or erase that asymmetry, the proposed
   source order loses while picture ownership may survive.

## What this candidate actually adds

The useful gain is small but concrete:

```text
OWNER-10 := anonymous page-local card bridging both f10r paragraphs
OWNER-56 := anonymous page-local card recurring four times through f56r
HERBAL FIELD := usually a canvas fragment, not a committed semantic cell
HERBAL RECORD := pictured-simple monograph paragraph
```

The first plausible stable Herbal content core is therefore not WATER or a
plant part. It is a pair of page-local **owner/address candidates** embedded in
continuous abbreviated monograph prose. External grounding is still required
to decide whether either card is a name, pronoun, heading, index, or unrelated
lexical item.
