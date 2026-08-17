# GDT223 — f82v module-set direction hits, but `AR` does not transfer

Status: **MODULE_SET_DIRECTION_HIT_AR_LOCAL_ADDRESS_TRANSFER_FAILED**.

The prediction was frozen and pushed at commit
`dc266ccfdb70e2cb7ba7c8bb681c1c6727f27fc8` before the f82v target module
presence was displayed.  All 12 prose lines are complete, so this result does
not inherit GDT222's incomplete-line ambiguity.

The eight-module Jaccard assignment lead is **+0.057143**: top-label→top-prose
0.428571, top-label→bottom-prose 0.200000, bottom-label→top-prose 0.571429,
and bottom-label→bottom-prose 0.400000.  Thus the predeclared direction is a
hit, but only barely.  A one-page top/bottom swap has two worlds and `p=.5`;
this is not statistical confirmation.

The specific `ar` transfer prediction fails.  Neither label bag contains
`ar`, while both prose bags do, so `ar` distinguishes no side.  The only exact
module-side match is instead `dal`: it occurs in the top labels and top prose
and in neither bottom bag.  This was not the frozen named-module prediction.
Removing `dal` reverses the assignment lead to **-0.183333**, whereas removing
`ar` leaves it positive (+0.083333).  The f82v direction is therefore a
post-reveal `dal`-concentrated fact, not a rescue of `ar`.

Across f75v, f83r, and f82v, the most defensible synthesis is now:

- a small module inventory can weakly align local label/prose assemblies;
- the identity of the discriminating module changes by page (`ar` in the
  exposed all-row f75/f83 view, `dal` in the prospective f82 view);
- the earlier `ar` effect was coverage-unstable and now fails prospectively;
- this behavior fits page-local content/address reuse better than a universal
  `AR` lexical value, but remains compatible with ordinary local string reuse.

Do not search another module on f82v after seeing this result.  A future test
must freeze a module-agnostic prediction on several independently defined
assemblies or obtain an external readable parallel.  No source group or
substring receives a segmentation, word, morpheme, object, process, direction,
sound, language, plaintext, or translation.  No f84 row or artifact was used.
