# GDT223 — f82v fixed-module assembly transfer freeze

## Purpose

Prospectively test the only actionable residue of GDT222 on a third
independently structured page.  The target is f82v, selected from visual/source
metadata rather than module values.  This is an exposed-corpus prospective
feature test, not a pristine manuscript holdout.

## Frozen assemblies

The human source annotations define three top-page labels (N1) and five
bottom-page labels (N3 plus X2).  Source order independently divides the prose
into the paragraph beginning f82v.5 and the paragraph beginning f82v.28.  The
exact loci and source descriptions are frozen in
`gdt223_f82v_assembly_prediction.tsv`.

Two lateral-margin labels, f82v.39 and f82v.40, are excluded before scoring
because they do not belong unambiguously to top or bottom.  No ownership is
inferred: every selected label remains proximity/possible-attachment evidence.
All twelve selected prose lines have complete GDT016 group coverage, so the
GDT222 complete-line failure cannot be evaded by changing coverage.

## Frozen representations and predictions

The module vocabulary and literal matching rule are inherited byte-for-byte
from `gdt222_module_manifest.tsv`: `ar`, `ol`, `dal`, `dar`, `sy`, `te`,
`tee`, and `dy` as overlapping contiguous substrings.  No module is added,
removed, resegmented, or weighted.

Two predictions are fixed before target module presence is displayed:

1. the correct top/bottom assignment has positive module-set Jaccard lead;
2. `ar` is discriminating: it occurs in both label and prose bags on exactly
   one assembly side and in neither bag on the other side.  The side is not
   predicted.

With one page, the exact top/bottom swap has only two worlds and minimum
`p=.5`; the value is prospective direction, not significance.  Failure rejects
the f82v transfer of the GDT222 local-address lead, not the existence of the
substrings.

## Access and seal

The f82v corpus has been used by earlier experiments.  Before this freeze,
geometry/role metadata and completeness counts were inspected, but no f82v
target token, PAGE_HOST, family, or module-presence row was displayed or used
to define the assemblies in this pass.  f84r and every f84 artifact remain
outside the route and are not accessed.

## Claim ceiling

Even a hit can establish only prospective reuse of an anonymous component as
a local assembly discriminator on one further folio.  It cannot establish a
manuscript-native cut, word, morpheme, semantic role, sound, language,
plaintext, or translation.
