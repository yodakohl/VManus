# Method

## Question

Can the current 51-line V62 working edition print one concrete noun per intended content choice, bind every printed noun to an exact written ordinal, and move rival values plus renderer jargon into a separate apparatus without opening another page?

## Fixed material

The target population is exactly GDT689's 51 V62 lines: 479 token positions on 36 already admitted pages. No image, OCR, new page, f84 or f84r material is read.

The only upstream semantic tables joined are the exact-surface dictionaries and p/s/r/l grids from GDT635/636 plus the three state cells from GDT685. These compact tables contain no mixed page selector field. Missing joins remain explicitly missing.

## Construction

1. Split every V62 line into written surfaces and its aligned `v62_literal_token_glosses_de`; require both arrays to equal `token_count`.
2. Apply the 72-row `V63_NOUN_RENDER_RULES.tsv` by exact surface and exact expected old gloss. A rule cannot silently match a changed input.
3. Render source order with the same segment contract as V61/V62, retaining the exact character interval of every token.
4. Classify every German word form through the versioned noun lexicon or the disjoint non-noun allow-list. Unknown words stop the build.
5. Emit every noun occurrence with token-local and line-global half-open spans, exact ordinal, surface, canonical noun, noun class, selected head, rivals, provenance tier and upstream-source status.
6. Keep `p/s/r/l` productive only at complete token-initial forms longer than one character; exclude `sh`. Standalone `r`, alternate `rr`, and internal `l` do not become productive by substring.
7. Print one main value and move every slash/or alternative, CTH/Herbal label, frame label, `Eintrag`, and `Holzbindung` wording into the apparatus.
8. Preserve the concrete `olkar/olam → Holz` reading only as `PROVISIONAL_LOCAL_SCOPE_HEAD`, never as a free internal-`l` rule.

## Source status

For each written token, source support is recomputed as one of:

- `EXACT_GLOSS`: exact surface and byte-identical gloss in GDT635/636/685;
- `EXACT_SURFACE_ONLY`: exact surface but a different upstream gloss;
- `HEAD_ONLY`: no full card in scope, but a licensed productive initial p/s/r/l head;
- `NONE`: no exported upstream card in this scoped source set.

`NONE` is reported as `UPSTREAM_CARD_NOT_EXPORTED_IN_GDT690_SCOPE`. It is never replaced by an invented experiment or card identifier.

## Historical use

The historical table is a comparator deck, not target evidence. It asks whether short heads and their rivals occur in real early-fifteenth-century materia-medica organization. It cannot identify a Voynich word.

## Validation contract

The validator is independent of the builder module. It reconstructs both line renderers, word classes, 725 main noun spans, 773 source noun spans, productive-head and focus counts, source joins, historical table copy and sealed-page absence. It then runs the builder in a temporary output directory and demands byte identity for every artifact and `RESULT.json`.

## Claim ceiling

V63 is an exploratory concrete working renderer. It proves exact German-output-to-written-ordinal provenance, not that the German nouns are historical plaintext. Local Gummi/Blüte/Kraut and provisional olkar/olam Holz choices remain replaceable when a better compositional model appears.
