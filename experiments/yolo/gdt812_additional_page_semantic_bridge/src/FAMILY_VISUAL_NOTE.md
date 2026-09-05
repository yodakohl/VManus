# GDT812: manual f32v family-context check

Date: 2026-09-05. Post-result exploratory visual note, not a preregistered
experiment, new count study, family decoder, or semantic validation.
Only already admitted f32v was viewed; no additional page admission.

## Source and bounded method

The cached full-page image was inspected manually at 2000 x 2646 pixels.
Its SHA-256 matches `src/IMAGE_SOURCES.tsv`:
`78c1a563e626656f890e5a0690eee11e117ffa2ede13b08ca199e5c02529dd5c`.
Registered source: [Yale canvas 1006137, f32v](https://collections.library.yale.edu/iiif/2/1006137/full/2000,/0/default.jpg).
No OCR, stroke-count classifier, new image page, or language identification
was used. EVA strings below locate inscriptions; they are not Latin letters.

All eleven cached f32v loci, including paragraph flags and all three readings,
were obtained with this guarded projection:

```sh
./vmanus-exp query-tsv experiments/yolo/gdt812_additional_page_semantic_bridge/artifacts/ADMITTED_PAGE_LINES.tsv --selector page --allow f32v --columns page,locus,line_number,kind,paragraph_start,paragraph_end,eva_clean,it2a_clean,rf1b_clean --forbid-prefix f84 --forbid-prefix f84r
```

## Visible facts at the two critical sequences

- **f32v.3, `dsho dain daiin s`:** the two family groups occupy the same
  continuing baseline, well inside the upper text block and to the left of
  the plant interruption. Neither begins or ends the physical row. Visible
  blank intervals separate the groups, but they are not conspicuously wider
  separators than nearby word gaps. No box, ruling, leader, or separate
  display line isolates either group as its own entry.
- **f32v.8, `otchol daiin daiin`:** the repeated groups follow the initial
  group on the same baseline in the second row of the lower text block.
  Both precede the plant interruption. Their gap does not create a visible
  column or independent row; writing continues immediately afterwards.
- At both sites the family forms have the same general script scale and ink
  appearance as their neighbours. Related looped beginnings and low-stroke
  bodies are visible. The line-3 groups differ in their internal extent;
  the line-8 groups repeat a closely similar outline. This is a qualitative
  comparison, not a fresh determination of minim counts or glyph units.
- The page has two separated text blocks. Their short final rows agree with
  the cached paragraph divisions at loci 6/7 and 11. Neither critical pair
  lies at those divisions. Plant-related interruptions elsewhere in the
  rows must not be converted into boundaries between these paired groups.

## What this does and does not discriminate

These sites do not visually present two independently delimited short
entries or a labelled scale. An account that needs such boundaries must
supply evidence beyond the observed gaps. Inline numerical values, an
unmarked list, qualification, repetition, or ordinary word-form variation
remain possible: running-text layout alone cannot choose among them.
The similar shapes are compatible with related spellings, but establish
neither a shared lexical stem and inflection nor a numerical progression.
No visible unit, equality sign, or scale ties the stroke difference to value.

All three readings retain `dain daiin` at locus 3 and the initial doubled
`daiin daiin` at locus 8; that is transcription agreement about one manuscript,
not three independent semantic observations. Later in locus 8, RF1b retains
the fused `cthodaiin` against ZL3b/IT2a `ctho daiin`; this note does not split
it or extend the agreement to every family boundary. Outcome remains open:
no word meaning, number, grammatical function, or language is confirmed.
