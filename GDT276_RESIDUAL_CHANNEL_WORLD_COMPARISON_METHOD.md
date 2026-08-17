# GDT276 — compiler-conditioned residual channel and world comparison

## Question

After jointly conditioning out the established formal renderer, how much
held-folio information remains, where does it reside, and which complete
residual generator describes it most economically?

This replaces local feature/gloss mining.  The target is always the opaque
`PAGE_HOST`; no target is given a semantic value.

## Frozen panel and seal

Use the same complete-line panel as GDT174: the intersection of the frozen
HPR2 inventory and line-frame table after rejecting every `f84*` page/locus.
The loader must split raw TSV rows, inspect only the page/locus fields, and
discard `f84*` rows before constructing a dictionary or parsing any formal
column.  The expected retained panel is 8,448 groups, 1,143 physical lines,
180 pages, and 91 physical folios.  GDT237 supplies the already-published
partial label-renderer prefix; it contains no f84 row.

Physical order determines paragraph/record ordinal, field ordinal and
within-field position.  A DY-bearing group closes a field; physical line end
closes the final field.  The joint compiler/nuisance key is:

```text
register + record ordinal + field ordinal + within-field position
+ wrapper (including q) + O/OT frame + inner-D + right family
+ DY + B3 + line close + paragraph close + known label renderer
```

Exact page identity is conditioned prequentially: while a held folio is
scored, a page-local model may use only earlier groups already scored on that
page.  It never uses later held-page targets.

## Common code and capacity

All worlds encode the same PAGE_HOST strings over the mechanically frozen
21-symbol non-f84 alphabet plus EOS.  A held-folio character-trigram code is
the common literal/escape distribution.  Exact-token models use hierarchical
Dirichlet-half prediction with this literal code as their base measure.

Every nonlocal world has exactly 256 deterministic SHA256 context buckets.
Priors are frozen: character context mass 11, global-token mass 32,
page-token mass 32, and context-token mass 64.  No lambda, bucket count,
alphabet, feature family, or model is tuned after scoring.  The five-way world
selector costs `log2(5)` bits equally.  Integrated predictive codes and the
fixed context ceiling are the capacity control; occupied contexts and cells
are reported.

Sixty-four matched controls permute each world's group-level context buckets
inside register × record-ordinal × within-field-position × PAGE_HOST-length
strata.  This preserves bucket frequency, opportunity, target length and all
listed coarse nuisance variables while breaking the specific context-to-host
alignment.  These are calibration controls, not confirmatory p-values on an
exposed panel.

## Five residual worlds

1. `COMPRESSED_NATURAL_LANGUAGE`: character code conditioned on previous-host
   edge context and physical position, but not the HPR2 compiler.
2. `ABBREVIATION_HEAVY_LANGUAGE`: character code conditioned on the complete
   compiler/nuisance key.
3. `LOCAL_CODEBOOK`: prequential exact PAGE_HOST dictionary local to each
   held page, with the common literal escape.
4. `TECHNICAL_NOTATION`: exact PAGE_HOST code conditioned on the complete
   compiler/nuisance key.
5. `HYBRID`: exact PAGE_HOST code conditioned on compiler/nuisance plus the
   immediately preceding PAGE_HOST on the same physical line.

All are operational coding worlds, not linguistic identifications.

## Residual accounting

Report held-folio bits, bits/group, bits/host character, folio wins, matched-
control excess and selector-paid MDL.  Under the abbreviation character code,
partition bits into first character, interior characters, final character and
EOS/length termination.  Verify separately that `(PAGE_HOST + complete
compiler tuple)` reconstructs the raw source group uniquely; if so, conditional
full-tuple residual equals the PAGE_HOST residual by construction.  Report the
HYBRID minus TECHNICAL difference as the sequential-context contribution.

## Interpretation

Rank the five worlds by selector-paid held-folio MDL.  Do not create a
post-hoc composite or assign a semantic role.  A winning world is only the
best of these five formal residual codes; it cannot identify natural language,
notation, a language family, plaintext, meaning, or translation.
