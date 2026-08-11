# f102r1 fifth repeated-plant label ownership

Status before inspection record: **SOURCE_BOUND_NATIVE_VISUAL_ACQUISITION**

## Purpose

The closed S100 composition route required a fifth Herbal↔pharmaceutical
drawing relation with a singularly owned pharmaceutical label. A cached 2025
human comparison table supplies nine good drawing relations, but the old
text-only audit could not establish label ownership for a fifth pair.

This bounded source-acquisition check asks only whether the official f102r1
image fixes ownership for the human relation `JSP2025_05`:

- Herbal page `f37v`;
- pharmaceutical page `f102r1`, row 3, item 1;
- human status `GOOD_HERBAL_PHARMA`;
- copied root and leaves, omitted flower.

## Frozen sources

- `cache/existing_human_annotations/stolfi_2025_internal_plant_pairs.tsv`,
  SHA-256 `53248c1ab2a50ec43a56ecee0bb22478a890a00f38671c75882620d8c5d28230`;
- `results/existing_human_page_annotations.tsv`, SHA-256
  `b358f244cbe853448dd5c32dbc04004cb8ce63d9a8c5ed5afe2a679a115d87fa`;
- cached public q19 HTML, SHA-256
  `119fe32a005723833ec07a313fd87e1cd044a1f685ddd4fdd199e573c1dff1fb`;
- current Stolfi line metadata table, SHA-256
  `b4c83c18f8f814e547ab4a849dab8cf24188680fc512d9497885bdaa0d944988`;
- prior four-pair SNPL001 capacity result, SHA-256
  `a16700eafc88653c3b95f8fcd840a4c86a185ca240a0e19123e880a46373cb2e`.

Official Yale source:

- manifest `https://collections.library.yale.edu/manifests/2002046`;
- canvas `1006251`;
- image `https://collections.library.yale.edu/iiif/2/1006251/full/full/0/default.jpg`;
- exact downloaded JPEG SHA-256
  `30fd529fc6bf8999d5be48024ee6a1676af55e8d66dc0a4f77993fe2565e9d94`;
- dimensions 8176 × 3864.

The relevant review window is the f102r1 bottom row, full-image rectangle
`x=2600, y=1900, width=3000, height=1900`. Cropping is navigation only. No OCR,
transcription, automated vision, embedding, similarity score, or plant naming
is permitted.

## Ownership rule

Call the label **SINGULAR_DIRECT_INTERIOR** only if all are visible:

1. the writing is inside or directly across the target fragment's drawn body,
   not merely nearest in open whitespace;
2. the local writing region overlaps no competing plant fragment;
3. the public page description independently says f102r1 has exactly one plant
   fragment label;
4. the current metadata has exactly one `@Lf` row on f102r1.

The label's characters and surface remain sealed. The visible judgment is a
source-bound machine-authored observation, not inherited human annotation.

## Decision ceiling

A pass adds `f37v ↔ f102r1 row3/item1 ↔ f102r1.2` as a provisional fifth
strongly owned repeated-plant relation. It authorizes only a new score-blind
five-pair capacity and design audit. It does not authorize running the old
four-pair S100 scorer or opening the new label string before a new freeze.

No plant name, component name, word, sound, language, cipher, plaintext,
meaning, or translation follows from ownership or drawing similarity.
