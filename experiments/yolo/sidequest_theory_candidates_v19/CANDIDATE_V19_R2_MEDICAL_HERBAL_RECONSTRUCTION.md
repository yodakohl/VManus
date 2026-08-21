# V19 R2 — four complete materia-medica articles

Date: 2026-08-21

Status: deliberately bold ten-page workshop reconstruction. These are concrete
defaults for fast theory-building, not deciphered plaintext.

## Result

The four Herbal pages read most economically as **short illustrated articles
of simples whose descriptive matter quickly gives way to preparation and
use**. The picture supplies the omitted plant owner. Physical lines are pieces
of a continuing article fitted into the available spaces, not sentences.

The R2 construction gives:

- 100/100 visible events a concrete English default;
- 66/66 exact Herbal cards a fixed dictionary entry;
- all 55 singleton cards one selected reading and two concrete rivals;
- 13 broad source classes rather than 55 unique singleton functions;
- 43 explicitly marked silent plant/part arguments;
- one complete reading for every page and no neutral placeholder.

The source-class inventory is deliberately small:

```text
PLANT_PART        HABITAT          GATHERING_TIME
MEDIUM            MEASURE          INDICATION
APPLICATION       STORAGE          REFERENCE
PROCESS_CONDITION CLAUSE_HEAD      CLAUSE_CLOSURE
PREPARATION_ACTION
```

## Frozen pictures and working plant families

The descriptions in `V19_R2_VISIBLE_PLANT_FREEZE.tsv` were fixed before the
text assignments. The narrow identifications are guesses; the broad fallbacks
are the actual working owners.

| page | narrow source-family bet | broad fallback used by the reading |
|---|---|---|
| f10r | scabious/knapweed article tradition | serrate meadow or waterside simple with paired swollen basal organs |
| f11r | wild carrot or related umbellifer | dense-crowned divided-leaf simple of shaded ground |
| f55v | greater plantain / broad-leaf wound herb | large broad-leaved roadside medicinal simple |
| f56r | *ros solis* / sundew tradition, perhaps contaminated by thistle/teasel imagery | spiny or glandular wet-heath simple with conspicuous radial heads |

The f56r assignment intentionally takes the user's water possibility seriously:
the default `CHOY` phrase is “which grows on damp shaded heath.” Water is
therefore real article content in this reconstruction without pretending that
the drawing itself depicts a stream.

## Why this is plausible for a scribe around 1420

The source shape is not invented from modern botany. Tadhg Ó Cuinn's 1415
*Irish Materia Medica* says that a short chapter normally gives a Latin heading,
the vernacular drug name, hot/cold/dry/wet qualities, general virtues and
specific uses. It explicitly derives from the Salernitan/*Circa instans*
tradition ([UCC CELT edition](https://celt.ucc.ie/published/G600005/index.html)).

The British Library's Egerton MS 747 physically combines the illustrated
*Tractatus de herbis* with an antidotary, doses, substitutions, weights and
measures, and a long list of plant/ingredient synonyms. That makes the mixed
name–part–measure–preparation deck historically ordinary rather than an
anachronistic database
([British Library catalogue](https://searcharchives.bl.uk/catalog/032-001983805)).

Penn's fifteenth-century north-Italian LJS 419 is an especially close layout
mechanism: its notes concern medicinal properties and preparations and are
written around, sometimes over, the illustrations
([OPenn catalogue](https://openn.library.upenn.edu/Data/0001/html/ljs419.html)).

These witnesses justify the **kind of article**, not any Voynich word or plant
identification. No sound resemblance, EVA substring or internal GDT327
coordinate was used.

## Article-by-article decisions

### f10r: root preparation and two medicinal forms

The first record is no longer forced to begin with a fabricated plant name.
It reads as an immediately useful root recipe:

```text
take root → wash in running water → same batch
→ pound evenly → coarse powder → red wine
→ drink for stomach pain → usual measure → keep remaining root dry
```

The short `.5` continuation tells how to use it warm. The second record adds a
damp-meadow habitat and a decoction/expressed-juice preparation. Its dense
`Y–Y–AIIN–Y` sequence becomes a real equality instruction—successive current
portions are taken under the same stated measure—without assigning different
meanings to the same exact card.

### f11r: clarified root liquor and warm poultice

The apparently redundant cloth cards are given complementary stages:

```text
press bruised root through cloth
→ strain the liquor a second time
→ continue until clear
→ cool uncovered
```

The remainder of the article uses the resulting material on swelling and gives
a warm leaf poultice. This needs fewer unrelated ingredients than reading both
cloth cards as independent exotic operations.

### f55v: broad-leaf wound wash

This is the most overtly procedural Herbal page. The two blocks form two
preparations of the same broad leaf:

```text
leaf + white wine → steep clear → mix → wash once

white wine + warm liquor → gentle boil → combine equal portions
→ covered jar → use fresh
```

The greater-plantain identification is only the preferred iconographic family;
the preparation remains coherent for the broader class of broad-leaf wound
herbs.

### f56r: a wet-heath simple organized by successive organs

Four `CHO/SHO` occurrences behave as one dossier continuation: “then take the
following ingredient or plant part.” They introduce root, wine-macerated organ,
dried narrow leaf and honeyed fresh part. The single article therefore moves:

```text
spring gathering/root dose
→ pre-flowering organ in wine for local application
→ damp-heath habitat and drying plaster
→ seed/head and shade-dried leaf
→ stomach remedy
→ honeyed fresh preparation
→ pale flower dose
```

This is a better use of the recurrent card than repeating the plant name four
times. It is also easy for a workshop apprentice: CHO/SHO simply opens the next
part/use packet wherever the illustration forces a new short line.

## Recurrent-card discipline

All eleven recurrent types keep a single default. The most important are:

| exact-card function | selected concrete default |
|---|---|
| AIIN | in the stated or usual measure |
| Y | this present portion |
| OR | the prepared decoction or working liquid |
| CHO/SHO | then take the following ingredient or plant part |
| OKY | apply or use this portion |
| OKCHY | use the freshly prepared remedy |
| CHOL | with the foregoing preparation |
| CTHY | when the preparation is ready |
| OTCHOR | gathered before flowering |
| CHAR/DAR | from the same prepared batch |
| DCHOL/SCHOL | of this pictured simple |

The last correction matters: the same exact DCHOL/SCHOL card occurs on f11r
and f56r, so it cannot be two different local plant names. The generic owner
reference now works on both pages.

## Rival readings retained, not erased

The concrete singleton table makes the main uncertainty inspectable. Examples:

- f10r `CTHOOR`: wash in running water / steep in spring water / clean in cold
  water;
- f11r `SCHOAL`: shaded woodland / damp woodland edge / shaded garden ground;
- f55v `YKAIN`: boil the broad leaf / bruise the fresh leaf / simmer the root;
- f56r `CHOY`: damp shaded heath / beside running water / shaded marsh ground;
- f56r `KEOL`: pale flower / pale seed head / light root tip.

The selected reading is not “proved”; it stays until a rival gives a more
coherent article with fewer silent repairs.

## Main awkward points

1. f10r's repeated `Y` can be read fluently only by carrying two or three
   portions across the line; the named ingredients are partly silent.
2. f11r has very little text for both habitat, liquor preparation and poultice.
   Heavy abbreviation is required.
3. f55v's exact medicinal indication remains supplied by the broad wound-herb
   family rather than a dedicated card.
4. f56r's sundew/*ros solis* family is visually tempting but botanically
   imperfect; thistle, teasel or a composite mnemonic plant remains viable.
5. Some closures may be punctuation or renderer state rather than source
   imperatives. Here they receive concrete phrases because the sidequest
   requires total default coverage.

## Files and reproduction

- `V19_R2_VISIBLE_PLANT_FREEZE.tsv` — four picture descriptions and source
  family bets;
- `V19_R2_HERBAL_CARD_DICTIONARY.tsv` — all 66 exact types;
- `V19_R2_100_EVENT_INTERLINEAR.tsv` — all 100 occurrences with their complete
  local phrase;
- `V19_R2_SINGLETON_ALTERNATIVES.tsv` — all 55 singleton rival sets;
- `V19_R2_COMPLETE_HERBAL_ARTICLES.md` — the four fluent readings;
- `build_v19_r2_medical_herbal.py` — deterministic builder and assertions.

Run:

```bash
python3 experiments/yolo/sidequest_theory_candidates_v19/build_v19_r2_medical_herbal.py
```

Expected terminal line:

```text
PASS events=100 types=66 singletons=55 classes=13 inserted_silent=43
```

Only the authorized ten-page V18 ledger is read. f84 and f84r remain sealed.
