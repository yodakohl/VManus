# SCP001 star-color source capacity

## Decision

**PASS — source panel frozen; Voynich text features remain unopened.**

Human page descriptions and manual scan QC identify 120 marginal stars on
9 pages / 7 physical folios whose centers alternate exactly between red
and faded yellow. The manually transcribed ZL `<%>` marker count equals the
described star count on every page, giving a direct marker-to-line binding.
Every bound physical locus has exactly one ZL3b, IT2a, and RF1b row. Six
otherwise clean-color pages were rejected because the visible star count did
not equal the retained manual ZL marker count; no proximity repair was used.

Seven pages start RED; f113r and f114v start YELLOW. The two reversed
pages contribute 28 markers, so color is not identical to odd/even ordinal
position. The final panel has 63 RED and 57 YELLOW markers.
Manual inspection of both the 2004 and independently digitized 2014 scan
families agrees on the first-color phase for all nine retained pages; both
public URLs and exact SHA-256 identities are frozen in the binding table.

Excluded before text scoring: f103r/f108r (white/three-state), f104r
(nonbinary red forms), f105r (only mostly alternating), f108v (mid-page
restart), f115v/f116r (red versus unpainted), plus f103v, f106v, f107r,
f111r, f111v, and f112r because visible-star and manual-marker counts differ.

The intended falsifier is page-phase exchange: preserve every line, ordinal,
alternation, page, and folio, but flip RED/YELLOW phase at whole-page level.
This tests a color-conditioned construction after controlling the otherwise
perfect local odd/even alternation.

No Voynich surface, root, role, English meaning, lexeme, plaintext, language,
or translation has been tested or inferred.

## Reproduction

```bash
./vpy experiments/semantic_assumptions/star_color_phase/build_star_color_source_panel.py
```
