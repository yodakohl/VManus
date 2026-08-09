# DIRECTIONAL-LABEL-PLACEMENT source-capacity freeze

Date: 2026-08-09

## Question

Does the existing human exact-locus annotation source contain a replicated,
transcription-covered contrast between labels explicitly described on opposite
sides of a nearby illustrated object?

This is a source-capacity audit, not a Voynich-text experiment. It must not
read or score a Voynich surface, root, token, or grammar feature.

## Frozen source rules

Use only rows from `existing_human_exact_locus_annotations.tsv` with:

- `certainty == UNHEDGED`;
- `relation_scope == EXACT_LOCAL_COMMENT`;
- a direction stated in `local_comment` itself (never infer it from
  `unit_description` or relation tags);
- all three cached manual readings ZL3b, IT2a, and RF1b at `source_locus`.

The two axes are audited independently.

- Horizontal: an exclusive literal clause matching `east of [object]` or
  `west of [object]`.
- Vertical: an exclusive literal clause matching `above [object]` or
  `below/under [object]`.

The frozen object vocabulary is plant, root(s), leaf/leaves, stem, nymph(s),
pond, channel, funnel, man, container, moon, sun, star(s), road, rosette,
canopy, triangle, and spike(s). A row containing words from both directions of
an axis is excluded even if only one direction completes a regex. This blocks
mixed relations such as "above X, below Y". `eastwards`, page-top/page-bottom,
row-top/row-bottom, and phrases in the unit description do not assign a class.

## Frozen matching and gates

A matched stratum is an exact tuple of:

1. exact annotated page/panel;
2. exact `normalized_code`, including its leading sigil;
3. exact `object_tags`;

and must contain both opposing classes. Physical folios are extracted as the
leading `f` plus digits, so panels and sides remain one independence cluster.

An axis is admitted to later preregistration only if all gates pass:

- at least 6 physical folios, so every one-folio deletion retains at least 5;
- at least 3 distinct exact code/object context families;
- no physical folio supplies more than 45% of matched rows;
- every admitted row has exactly the three manual readings;
- every stratum has both classes on the same exact page/panel.

No visual model, OCR, image measurement, plant identification, geometric
ownership inference, or Voynich-text score is permitted. Passing capacity
would authorize only a separate target-blind prescore design. It would not
establish ownership, a direction word, a lexeme, plaintext, language, or
translation.
