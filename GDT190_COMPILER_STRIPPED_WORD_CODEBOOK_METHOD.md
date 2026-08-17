# GDT190 — compiler-stripped word-codebook screen

## Question

GDT189 rejects a stable one-source-sign to one-named-letter language beneath
the frozen HPR2 compiler.  A different possibility is that an exact PAGE_HOST
identity is an opaque abbreviation or nomenclator entry for a whole historical
word.  GDT190 tests that bounded alternative directly.

This is not the earlier GDT001 visible-group nomenclator.  The source units are
the frozen non-f84 PAGE_HOST values after removal of the HPR2 wrapper,
licensed O/OT rendering, right family, carrier-D, DY, and B3 layers.

## Frozen model

- Exclude every `f84*` row before formal parsing or retention and exclude the
  single unknown-transcription locus `f102v2.33`.
- Preserve physical-line order.  Each unmapped host resets the mapped run, so
  no transition is invented across a literal escape.
- Test the deterministic top `K = 8, 16, 32, 64` PAGE_HOST identities.
- For each of the six already frozen GDT001 historical-language packs, map the
  selected identities bijectively to that pack's `K` most frequent words.
- Score an order-1 word model with Dirichlet-1/2 smoothing.  Optimize one
  mapping by exact best-pair-swap descent from three deterministic starts.
- Pay `log2(6)` for language and `log2(K!)` for the codebook permutation.  The
  four predeclared K choices are common to candidate and matched null.
- Compare each candidate with a source-identity order-1 KT code over exactly
  the same mapped runs.  Literal residuals and manuscript reconstruction are
  common and therefore omitted from this conditional channel comparison.

The route passes only if some paid language codebook beats its matched KT
control and the winning mapping is identical across all three starts.  K is
selected only after all four values are scored; no assigned target word may be
read as a translation unless the complete paid and stability gates pass.

This bounded screen cannot reject arbitrary phrase codes, nonbijective
expansion, page-specific dictionaries, or context-dependent codes.  It can
reject the simplest compiler-stripped fixed whole-word nomenclator.  No f84r
payload is accessed.
