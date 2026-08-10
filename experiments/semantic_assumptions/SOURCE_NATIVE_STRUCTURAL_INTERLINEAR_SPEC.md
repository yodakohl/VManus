# Source-native structural interlinear v1

## Purpose

Create one lossless, reproducible structural reading table for every strict
all-reading STA-family construction group.  This replaces reliance on the
unreproducible, surface-incomplete legacy parser for current sentence/record
inspection.  It joins only already validated source-native structural layers;
it fits no model and introduces no semantic label.

## Frozen inputs

- strict consensus construction groups;
- the complete exact-group position atlas and its independent validation;
- the 576-pair held-folio transition atlas and its independent validation;
- the compositional edge-feature atlas and its independent validation;
- the 13-path favored-construction atlas and its independent validation;
- the official explicitly lossy STA-to-basic-EVA convenience rules.

Every input hash is enforced by the builder.  No legacy cleaner token, legacy
root/role, image/OCR output, automated-vision output, or English gloss may
enter.

## Row construction

Keep exactly `strict_zero_alternative=1` from the consensus group table.  Each
row preserves locus/page metadata, factual consensus group index/count, family
surface, three separate member-code readings, and both exact boundary profiles.

Add:

1. factual `SINGLE/FIRST/CORE/LAST` position from index/count;
2. boundary support counts, where line edges have support three and an internal
   profile counts readings whose state is not `NONE`;
3. explicitly lossy nearest-basic-EVA rendering of each reading by applying the
   official rule to each stored STA member code;
4. exact-form first/last and edge/core tendency labels from the complete
   position atlas, or `NOT_IN_PROSE_ATLAS` for a diagnostic form absent there;
5. every opening- or closing-associated `P1/P2/S1/S2/LEN` feature hit;
6. every favored, disfavored, and unresolved adjacent family pair inside the
   group;
7. all of the 13 validated favored paths occurring in the surface, plus the
   longest opening path and longest path anywhere.

All multi-value fields are semicolon-delimited and deterministically sorted.
The interlinear does not majority-correct member codes or separator states.

## Claim ceiling

This artifact is a complete formal wiring view of 3,572 strict shared loci.  It
can support structural inspection and future preregistration.  Factual position
and descriptive association tags are not words, parts of speech, semantic
roles, sounds, morphemes, lexemes, plaintext, language, cipher, or translation.
Nearest basic EVA is explicitly lossy and is never evidence over the retained
STA codes.
