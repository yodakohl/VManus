# GDT733 method

## Question

Can the current V99R4 dictionary, all exact V99 context readings and GDT732's
spoken-grade layer be compiled into one complete cache reader without
globalising occurrence-local values, losing existing bound spans, speaking
debug metadata, or changing evidence and confidence?

## Inputs

- GDT671's f84/f84r-free cache: 179 admitted pages, 4,128 lines and 32,339
  aligned ZL3b token cells;
- GDT727's 479 exact context positions and 471 practical output units,
  including eight two-position bound spans;
- GDT730's 1,586-row V99R4 dictionary with score, confidence, evidence, scope
  and export fields;
- GDT731's frozen practical-blocker rules;
- GDT732's 2,431 licensed spoken overlays and its 4,752-cell full-cache
  residual lineage table;
- eight GDT664/GDT665 legacy contextual alias cards;
- GDT733's precedence, 52-template legacy renderer, one exact `chockhy`
  special, eight legacy merge specifications and four structural-punctuation
  specifications.

No image, OCR, raw transcription, new page, f84 or f84r source is opened.

## Cell integration

Every cache key is the exact `(page, locus, token ordinal, surface)` tuple.
Exactly one of eight precedence classes owns each key:

1. thirty exact V99 contexts also licensed by the GDT732 spoken overlay;
2. 52 exact V99 contexts that supersede a grade-bearing V48 cell;
3. 397 other exact V99 contexts;
4. 2,401 global GDT732 spoken cells outside exact context scope;
5. 4,692 occurrence-local active-surface legacy grade cells;
6. eight occurrence-local legacy alias/merge anchor cells;
7. 6,866 further unconditional V99R4 global defaults; and
8. 17,893 inherited V48 cells.

The classes are disjoint and sum to 32,339. Exact context always wins over a
surface-level default. An active reading outside its licensed exact positions
never becomes a portable surface meaning.

The 4,692 legacy cells use a complete 52-template map from the exact inherited
V48 phrase to shorter German state prose. Each template preserves the written
heat/cold/dry/moist axis, stage and workflow closure. Mixed modalities retain
both axes; `angefeuchtet` is not strengthened to `eingeweicht`; `abgekühlt`
is used for the attained cold result. The one exact current context that still
contained an analytical grade phrase, f104v.2 ordinal 3 `chockhy`, receives its
own source-bound rendering.

## Practical-unit integration

The token-cell register remains exhaustive, but it is not itself the spoken
unit stream. GDT733 therefore reconstructs a second, explicit unit layer:

- all eight inherited GDT727 `BOUND_SPAN` rows consume their sixteen exact V99
  positions and emit the already licensed render-once value;
- eight legacy alias/merge specifications consume another sixteen positions
  and emit eight occurrence-local values;
- four exact punctuation positions remain visible in the cell register but
  attach to the preceding unit and emit no lexical unit;
- every other cell emits once.

The 32 span positions and four punctuation positions are unique and disjoint.
Thus `32,339 - 16 span collapses - 4 punctuation units = 32,319` practical
units. Diagnostic phrases such as `keine Einzelausgabe` and `Gesamtspan`
remain available in source token audit cells but are forbidden from the
practical output. Connectives already beginning with punctuation, such as
`; hierzu:`, supply their own separator and cannot produce `; ;`.

## Validation and decision rule

Pass requires unique ordered reconstruction of all 32,339 source keys; the
eight-class count vector; all 479 exact contexts; all 2,431 GDT732 cells; all
4,692 template-bound legacy cells; all 52 superseded exact cells; sixteen
non-overlapping two-token spans; four punctuation attachments; 32,319
practical units; zero remaining analytical grade-frame phrases; zero practical
debug fragments or doubled separators; exact modality and closure
preservation; no new page; zero component credit; unchanged scores,
confidence, evidence, semantic scope and export rights; and byte parity for
twelve inherited artifacts.

The independent validator reconstructs these conditions from inputs and
source decks without importing `run.py`.

## Claim ceiling

This is an integrated reader over an exploratory working dictionary, not a
decipherment. It adds no word meaning, plaintext, language, sound, ingredient,
disease, cure, action or component value. “Zero audible grade frames” refers
only to the inherited analytical forms `… des Grades`, `Gradanfang`,
`Gradmitte` and `Gradende`; 755 indexed placeholders and other semantic debt
remain visible.
