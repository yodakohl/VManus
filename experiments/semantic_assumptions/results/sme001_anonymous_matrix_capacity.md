# SME001 anonymous paragraph-matrix capacity

## Decision

**PASS — target-blind matrix built; morphology assignments remain unjoined.**

The exact-count source panel supplies 171 manual ZL paragraph-opening markers. Every reconstructed ZL span starts with OPEN and contains only CONT lines until the next marker or page end; RF does not carry this marker metadata and IT omits it at four starts, so those alternate metadata columns are not treated as independent layout evidence. One unit, f106r.27, is excluded without consulting morphology because IT2a omits physical line f106r.29 while ZL3b and RF1b retain it. The remaining 170 units have identical physical line sets in all three readings and span 2–7 lines. Their 510 reading-specific rows form the frozen anonymous matrix.

The matrix has 84 prespecified or support-selected features: 19 opening-line formal measures, 15 whole-paragraph layout/formal measures, 32 root-atom rates, and 18 composite root-form rates. Root candidates were selected only by global support in every reading (at least 20 occurrences, 12 paragraphs, six pages, and five physical folios); target ray/tail values were never joined. Composite root forms retain within-space word structure, while atom features test reusable stems.

No morphology column occurs in the binding or feature matrix. This artifact does not report any feature association. It supplies no ray/tail function, recipe class, root meaning, word meaning, lexeme, plaintext, language, or translation.

## Reproduction

```bash
./vpy experiments/semantic_assumptions/star_morphology_entry/build_sme001_anonymous_matrix.py
```
