# V73 R1 — complete Herbal third edition

## Outcome

The four fixed Herbal pages now have a complete third edition at all requested levels:

- 100 occurrence-bound event defaults, E001–E100;
- 20 complete fields, F001–F020;
- 19 selected V72 statements;
- five complete record articles, H1–H5;
- four unidentified whole-plant owners inherited unchanged from V71.

The edition is deliberately concrete but not lexical. Water, wine, oil, honey, habitat, plant part, preparation, target, indication, and dose are written as occurrence-specific values copied from a hypothetical master exemplar. None becomes the meaning of its tuple, surface form, wrapper, stem, or card component.

## Fixed R1 background

1. Du bildest mehrere Schreiber aus, die dasselbe praktische Buch zuverlässig fortsetzen müssen.
2. Du denkst in vorzeigbaren Exemplaren, häufigen Ganzkarten, einfachen Regeln und prüfbaren Abschreibeschritten.
3. Du fragst bei jeder Theorie, wie ein Lehrling sie lernt, ausführt, korrigiert und an eine zweite Hand weitergibt.
4. Du bevorzugst keine Sprache oder Bedeutung, sondern den kleinsten praktisch lehrbaren Produktionsablauf.
5. Du lieferst eine konkrete Schreibanweisung, eine Rücklesung und die Fehler, die ein echter Lehrling machen würde.

## Inputs and binding rule

The builder uses only the frozen V69 173-card dictionary, first 100 Herbal events and first 20 fields; the selected V70 image revision; the central V71 owner ledger; and the 19 selected V72 Herbal statements. It does not derive any meaning from internal tuple coordinates or substrings.

The binding is:

```text
exact opaque event identity
  + V71 whole-plant owner
  + existing known card/formal prompt, if any
  + one occurrence-specific typed master-exemplar value
  = one concrete German event default
```

The whole plant is the only image-supplied owner. There are no leader lines that authorize treating individual text pockets as captions of roots, leaves, flowers, or other parts.

## Source-layer accounting

The V69 parser support remains unchanged: 29 supported events and 71 exemplar-only events.

| V73 source layer | Events |
|---|---:|
| known card with exemplar fill | 18 |
| known card + formal prompt with exemplar fill | 6 |
| known formal prompt with exemplar fill | 5 |
| formal closure marker with exemplar fill | 5 |
| exemplar only | 66 |

Thus the final two rows together are the same 71 events that lack V69 parser support. The 24 known-card occurrences and 11 formal-prompt occurrences retain only their already frozen uncertain labels. Five terminal occurrences retain closure as layout/formal evidence; their concrete closing actions are still exemplar values.

## Literal event edition

Every row in `V73_R1_100_EVENT_INTERLINEAR.tsv` contains:

- event, page, locus, record, field, and statement identity;
- exact opaque tuple ID and display-only surface;
- opaque formula, existing card, existing formal prompt, and terminal status;
- V71 whole-plant owner and owner status;
- one typed German default;
- source layer and internal working-confidence score;
- strongest practical/material rival;
- the specific contradiction that keeps the value provisional.

The confidence number measures only coherence inside this third edition. It is not a probability that the phrase is historical plaintext. Known formal structure can raise it; unpictured medium, habitat, part, use, or indication lowers it.

## Twenty-field edition

| Record | Field | Article function | Main concrete default |
|---|---|---|---|
| H1 | F001 | root extraction and first use | clean, cut, cover with water, prepare first extract, use measured portion, store remainder |
| H1 | F002 | second warm use | resume first extract, warm, link to same preparation, use at readiness |
| H2 | F003 | first aerial harvest | take young tops, press, add oil, measure, warm |
| H2 | F004 | earlier comparison harvest | take pre-bloom portion, resume previous post, equalize measure and treatment |
| H2 | F005 | parallel salves | keep two fractions separate, thicken, cover, choose one for external use |
| H3 | F006 | clarified wine extract | take spring tops, boil in wine, strain twice, cool after clarity gate |
| H3 | F007 | reserved flowers | hold back a flower portion for a second preparation |
| H3 | F008 | internal dose | resume clear extract, administer a small measured drink |
| H3 | F009 | oil preparation | warm reserved flowers in oil and use externally at readiness |
| H4 | F010 | first leaf maceration | set register post, measure leaves, add wine, cool under closure |
| H4 | F011 | clarify and store | measure, wring, settle, store clear extract |
| H4 | F012 | external wash | wash the exemplar-specified wound with the clear extract and close |
| H4 | F013 | honey leaf poultice | measure retained leaves, target, warm, make second preparation, add honey |
| H5 | F014 | harvest and measure | take the unidentified whole plant at an exemplar-specified damp site and bloom stage |
| H5 | F015 | short skin application | crush sticky leaves, place briefly on an exemplar-specified skin target |
| H5 | F016 | application aftercare | remove, wash with water, repeat only if tolerated, close |
| H5 | F017 | dried reserve | take flowering stems, shade-dry, grind, store |
| H5 | F018 | weak wine extract | extract dried material in mild wine and strain |
| H5 | F019 | honey chest drink | add honey, warm, administer for exemplar-specified dry cough |
| H5 | F020 | flower-portion dose | select the designated opened part and measure each dose |

The complete German fields are published in `V73_R1_20_FIELD_EDITION.tsv`, including the verbatim event-to-field binding and the selected V72 statement paraphrase.

## Five record articles

### H1 — f10r root preparation

The whole f10r plant owns both fields. The article first prepares an aqueous root extract, gives a small inner dose, and stores the remainder; it then reheats a fresh portion and continues it under the formal active-state link until `BEREIT?`. The strongest rival is raw-material lot handling. The image does not identify a root subarticle, water, pot, dose, or ailment.

### H2 — f10r paired harvest states

The same whole f10r plant owns a fresh first top-harvest and a pre-bloom comparison harvest. `ANSATZ?`, `VORIGES?`, equal measure, and repeated active-state links make a two-post comparison the simplest workshop expansion: process both alike, retain two salves, and choose one for an external use. This is still an exemplar reading; neither comparison nor salve is pictured, and the purely technical rival reads the same sequence as two controlled material batches.

### H3 — f11r clarified extract and reserved flowers

The article makes a twice-strained wine extract, retains a flower fraction, gives a measured internal use of the clear extract, and makes a second oil preparation for careful external use. The `KLAR?`, `MASS?`, and `BEREIT?` handles fit the order without expanding into sentence meanings. The image supplies none of spring, wine, linen, indication, oil, or target.

### H4 — f55v leaf preparations

The four text pockets remain one whole-plant article. The article establishes a first leaf post, clarifies and stores its extract, uses it as a wash, then creates a second measured honey-leaf poultice. The formal relation slot is retained exactly but receives the occurrence-specific external target only from the exemplar. A two-fraction material/test protocol remains equally possible.

### H5 — f56r external use and dried reserve

The article explicitly leaves the plant unnamed. It collects material at an exemplar-specified damp site and bloom stage, gives a short sticky-leaf application with after-wash, dries the remaining flowering material, makes a weak wine-and-honey drink, and closes with a measured flower portion. This is the most semantically expensive record: almost every diagnostic detail is absent from the image, and a coating/material-preparation record is the strongest rival.

The fully readable German articles and their literal control sequences are in `V73_R1_FIVE_RECORD_ARTICLES.md`.

## Teachable article template

The apprentice is taught the following fixed routine:

1. Set the page’s whole plant as `OWNER`; never name the species from the image.
2. Reset `ACTIVE`, `TARGET`, and `PREVIOUS` when H1–H5 changes.
3. Copy the next exact opaque card from the master exemplar.
4. If it is one of the existing known control cards or formal prompts, copy that handle exactly, including `?`.
5. Fill its local object/action/medium/condition from the same occurrence in the master exemplar.
6. Carry the whole-plant owner across the field and physical-line layout.
7. Let `CLOSE` finish only the current field post; continue the article if the record continues.
8. On correction, compare exact card order first, then owner, then occurrence value. Never repair a rare card by decomposing its surface spelling.

Forward production is therefore easy with the exemplar. Backward recovery without it stops after owner, exact-card sequence, known control handles, and closure positions.

## Likely apprentice errors

- treating a text pocket as a leaf/root caption rather than carrying the whole plant;
- importing a narrow species name from resemblance;
- reading water, wine, oil, honey, habitat, or ailment from the drawing;
- turning `MASS?`, `ANSATZ?`, `KLAR?`, or another mnemonic into a German word;
- extending `VORIGES?` from H2 backward into H1 despite the record reset;
- assigning the same German event phrase to every recurrence of one unknown exact card;
- ending the article at a physical line or field close;
- merging H1 and H2 merely because they share a page owner.

## Strongest revision beyond V72

V72 supplied one source-class sentence per statement. V73 makes every event explicit and resolves the remaining Herbal fragments into article grammar. The strongest new editorial choice is H2’s paired-harvest structure: the first/previous/linked/equal-measure sequence is expanded as two locally comparable preparations. This is more coherent than a single blended sequence, but it remains provisional because the comparison itself is not a card meaning or image label.

No narrower plant identity is restored. No surface component, stem, prefix, suffix, or exact tuple receives a newly generalized meaning.

## Validation and ceiling

The executable validation passes all count, binding, owner, source, species-anonymity, and no-new-card checks. Every German event sentence appears verbatim in its field, and every full field appears verbatim in its record article.

The supported result is only:

```text
four unidentified whole-plant owners
+ a complete, learnable, occurrence-bound Herbal article edition
+ unchanged exact control-card/formal infrastructure
```

It is not a plant identification, plaintext recovery, word dictionary, stem analysis, or translation.
