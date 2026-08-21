# V19 selection — complete four-page Herbal reconstruction

Date: 2026-08-21

Status: **selected concrete sidequest reading, not deciphered plaintext**.

## Selection

V19 forced all four Herbal pages (`f10r`, `f11r`, `f55v`, `f56r`) into complete
articles: 100 visible events, 66 exact cards, and concrete alternatives for all
55 singleton cards. Four independent historical perspectives first froze the
visible plants, then assigned text. The selected basis is **R2's illustrated
materia-medica reconstruction**, with two constraints supplied by the other
passes:

1. R3's exact-card consistency rule is mandatory: a card cannot be a local
   plant name when it occurs next to two visibly different plants.
2. The V18 meanings of 17 cards that also occur outside Herbal are preserved.
   V19 may refine only the 49 Herbal-only cards. This prevents local narrative
   fluency from silently breaking the common workshop deck.

| candidate | score / 100 | disposition |
|---|---:|---|
| R2 medical/Herbal scribe | 96 | **selected article reconstruction** |
| R3 technical-register writer | 94 | exact-card and OWNER→PART→BATCH discipline incorporated |
| R1 workshop master | 92 | learnable article compiler and apprentice rules incorporated |
| R4 chancery corrector | 90 | copying, line-fill and segmentation nulls retained |

## Concrete working articles

The picture supplies a silent page owner. The text then moves among plant part,
habitat, gathering time, medium, measure, preparation, application, indication,
storage, reference and closure. A physical line is reflow around a pre-drawn
image and need not end a clause.

### f10r

Working family: scabious/knapweed-like waterside or meadow simple with paired
swollen basal organs.

> Take the fibrous lower root and wash it in running water. From the same
> prepared batch, pound it evenly to coarse powder; add red wine and drink it
> for stomach pain in the usual measure, keeping the remaining root dry. Use
> the preparation warm. The second block gives damp-meadow habitat, decoction
> and expressed juice, collection before flowering, equal measured portions,
> and preservation under oil.

Water is therefore explicit content in the working theory, but not a claimed
translation of a glyph sequence or a feature inferred merely from the drawing.

### f11r

Working family: wild-carrot/umbellifer-like shaded-ground simple.

> Gather the root in spring before the flowering crown opens. Press the bruised
> root through cloth, strain the liquor again until clear, and leave it to cool.
> Bind the prepared portion on a swelling, and make a warm leaf poultice.

### f55v

Working family: greater-plantain/broad-leaf wound-herb article.

> Boil the measured broad leaf gently in white wine, steep until clear, mix and
> wash the sore once. A second preparation combines warm liquor and white wine,
> mixes equal portions in a covered jar, and uses the decoction fresh.

### f56r

Working family: spiny or glandular wet-heath simple; the narrow
*ros solis*/sundew association remains an iconographic bet, not identification.

> Gather in spring; take the lower root in measure. Steep the next part in white
> wine before flowering and apply locally. The pictured simple grows on damp
> shaded heath. Dry a plaster, seed/head and narrow leaf in their respective
> stages; use a further preparation for stomach pain, another with honey, and
> finally take the pale opened flower in measure.

## Contradiction-driven lexical correction

Exact card `d665560c...`, rendered `dchol` on f11r and `schol` on f56r, was
previously allowed to mean a local plant name. The pictures show different
plants, so that assignment is incompatible with one exact card having one
default. Three independent candidates converge on an owner expression. The
selected default is:

> **of this pictured simple**

R4's “for painful swellings” remains a concrete rival because both articles can
support application, but it explains the picture-relative recurrence less
directly.

## Executable selection discipline

- 49 Herbal-only exact cards adopt R2's selected meanings (56 events).
- 17 cards shared with Biological pages retain their V18 defaults.
- The complete dictionary still contains 569 entries and the complete ledger
  776 events, all with nonempty concrete defaults.
- Singleton meanings are grouped into 13 historically ordinary source classes
  rather than 55 unrelated exotic ingredients or diseases.
- Exact species, disease and dose remain low-confidence bets. Broad article
  coherence outranks botanical resemblance.

The machine-readable selection is in:

- `V19_SELECTED_HERBAL_DICTIONARY.tsv`;
- `V19_SELECTED_100_EVENT_INTERLINEAR.tsv`;
- `V19_SELECTED_COMPLETE_DEFAULT_LEXICON.tsv`;
- `V19_SELECTED_COMPLETE_TRANSLATION_LEDGER.tsv`.

`V19_VALIDATION.json` is `PASS`. The full fluent R2 articles remain in
`V19_R2_COMPLETE_HERBAL_ARTICLES.md`; the selected machine ledger overrides its
wording at the 17 cross-register cards where global consistency is stronger.

## Interpretation ceiling

This is intentionally a complete, risky working translation used to expose
contradictions. It establishes no English lexeme, plant identity, language,
plaintext or decipherment. A default survives because it currently makes the
four fixed articles more coherent than its recorded rivals, not because it has
been proved. f84 and f84r remained sealed.
