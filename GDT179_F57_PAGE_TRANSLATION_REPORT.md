# GDT179 — f57 page-translation scaffold report

Status: **PROVISIONAL_COMPLETE_F57_ROLE_SCAFFOLD_LOCAL_TWO_BIT_QUALITY_DECODER**

## Outcome

The strongest coherent reading of f57v is now executable.  Under the
independently frozen Walters W.73 phase, the page is provisionally a
four-element/four-quality technical diagram:

| Page sector | Element | Qualities | Season | Humour |
|---|---|---|---|---|
| top | Fire | Hot, Dry | Summer | red/yellow bile |
| right | Air | Hot, Moist | Spring | blood |
| bottom | Water | Moist, Cold | Winter | phlegm |
| left | Earth | Cold, Dry | Autumn | black bile/melancholy |

The inter-sector positions NE/SE/SW/NW are consequently
Hot/Moist/Cold/Dry.  That phase comes from the official Digital Walters
description, not from fitting the Voynich strings.

## The local two-bit decoder

Two physically distinct four-item registers implement the same four-state
square with different first coordinates and one shared second coordinate.

| Register | Position | Source readings (ZL / IT / RF) | Coordinate bits | Provisional role |
|---|---|---|---|---|
| N1 | NE | `otodara[g:m]` / `otodarod` / `otodarag` | starts-`ot`=1, final-`y`=0 | HOT |
| N1 | SE | `oparairdly` / same / same | 0,1 | MOIST |
| N1 | SW | `olkeedal` / `olkchdal` / `olkchdal` | 0,0 | COLD |
| N1 | NW | `otardaly` / same / same | 1,1 | DRY |
| D1 | NE | `ara?arar` / `oralaror` / `aralarar` | has-`ok`=0, final-`y`=0 | HOT |
| D1 | SE | `okeely` / `okchoy` / `okeely` | 1,1 | MOIST |
| D1 | SW | `ocfhor,okear` / `ocfhor.okear` / same | 1,0 | COLD |
| D1 | NW | `ark[a:o]ldy` / `ackaldy` / `askaldy` | 0,1 | DRY |

The N1 selector identifies the qualities incident to Fire: Hot and Dry.  The
D1 selector identifies the qualities incident to Water: Moist and Cold.
Terminal `y` identifies the Moist/Dry pair in both registers.  These rules
decode all eight labels without an exception and survive the three alternate
readings at the level of the binary features.

This is the strongest current semantic mechanism because it explains several
facts jointly: two different surface registers, free/bound-looking source
components, a shared right-edge operation, and a fourfold historical system.
It is still post-hoc on one page.  The labels are proximity-owned, and the
same geometry was used to discover the rules.  Therefore `ot`, `ok`, and `y`
are not promoted to manuscript-wide meanings.

## The circular bands

The 13 page loci now have a complete role scaffold:

- f57v.1: outside start/title label — untranslated;
- f57v.2 (R1): outer circular commentary/legend candidate — untranslated;
- f57v.3 (R2): four repeated 17-sign records — four-element property-table
  candidate;
- f57v.4 and f57v.5 (R3/R4): circular commentary/legend candidates —
  untranslated;
- f57v.6–.9 (N1): four figure-near quality-position labels, provisionally
  decoded above;
- f57v.10–.13 (D1): four interfigure radial quality-position labels,
  provisionally decoded above.

R2 has one all-reading-stable changing column: `f,f,p,p` across
Fire/Air/Water/Earth.  It matches the hot-element versus cold-element split.
It also matches the upper versus lower half of the page and the masculine
versus feminine grammatical gender of the Latin element names.  Those three
explanations are exactly aliased here, so the glyph states receive no lexical
gloss.

## Forward predictions

The predictions in `gdt179_predictions.tsv` are deliberately more specific
than the current evidence:

1. another independently owned same-system quality register should place
   terminal `y` on Moist and Dry only;
2. a register referenced to Fire should select Hot/Dry, while one referenced
   to Water should select Moist/Cold;
3. a readable close homologue of the 4×17 table should reveal whether its
   changing column is thermal rather than geometric or grammatical;
4. the three long rings should behave as commentary/legend material, not four
   separately owned element names.

No eligible unexposed target currently tests these predictions.  f84r remains
sealed.

## What remains awkward

- all eight owner relations are proximity-only;
- the decoder was discovered after the four historical positions were known;
- R2 exposes only one stable changing column;
- the apparent f57v.8/f77v.3 Cold-form bridge breaks outside ZL3b;
- previous attempts to export `ot`/`ok`/`y` globally failed or were
  coordinate-confounded;
- three long bands and the outside label remain untranslated.

## Conclusion

GDT179 does not produce a confirmed word translation.  It does produce a
complete, auditable page-role reading with an explicit local decoder:
f57v is best treated as a four-element/four-quality technical schema, and its
two short-label registers behave as two binary encodings of the same four
quality positions.

That is useful progress toward translation because it turns a visual analogy
into falsifiable decoding rules.  Confirmation requires a new independently
owned four-quality register or a readable structural homologue.  Until then,
the result remains page-local theory generation rather than plaintext.

External comparator: [Digital Walters W.73 manuscript description](https://t.thedigitalwalters.org/Data/WaltersManuscripts/html/W73/description.html).
