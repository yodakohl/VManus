# SME001 star-morphology source capacity

## Decision

**PASS for 7-vs-8 rays and one-vs-two tails; STOP for visible core state. Voynich text features remain unopened.**

Jorge Stolfi's [public, human-authored table](https://www.ic.unicamp.br/~stolfi/voynich/Notes/076/star-props.txt) contains 323 marginal stars on 23 pages / 12 physical folios. It records top-to-bottom star number, center/core state, paint, color, ray count, tail count, and observations; the [page-by-page methodology](https://www.ic.unicamp.br/~stolfi/voynich/Notes/076/report/sec-per-page/page.html) is published with it. Both exact source URLs and SHA-256 identities are frozen. No OCR or automated/neural image analysis was used.

Only pages whose complete human star count equals the existing manual ZL `<%>` paragraph-marker count are admitted. Thirteen pages / eight physical folios match exactly, yielding 171 ordinal bindings. Every bound marker has exactly one ZL3b, IT2a, and RF1b row. Ten mismatched pages are excluded and no proximity, inferred nearest line, or Stolfi paragraph assignment is used.

After excluding the rare 6- and 9-ray forms, 7-vs-8 rays retains 164 entries; all 13 pages and all eight folios vary internally (90 seven-ray, 74 eight-ray). One-vs-two tails retains 170 entries; nine pages on seven folios vary internally (147 one-tail, 23 two-tail). Visible no-core vs dot retains 77 entries but varies within pages on only four physical folios, so it fails capacity and must not be scored. Opaque red cores are unknown (`--`), never negative.

The tail-absence classifier reported elsewhere is not reproduced: this strict panel contains only one tail-less entry, while the full source places most tail absence on a few pages/bifolios. The admissible tail contrast is one tail versus the separately drawn two-stroke/fat-tail state, with page-sequence structure preserved in any future null.

This source pass supplies marker morphology, not marker meaning. It establishes no category name, recipe class, number, word, lexeme, plaintext, language, or translation.

## Reproduction

```bash
./vpy experiments/semantic_assumptions/star_morphology_entry/build_sme001_source_panel.py
```
