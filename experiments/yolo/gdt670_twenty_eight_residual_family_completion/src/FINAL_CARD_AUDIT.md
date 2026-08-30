# GDT670 final card audit

## Verdict

The synthesis has the correct 28 surfaces in the exact first-frontier order
and covers 91 full-panel positions. All 25 productive compositions reconstruct
their ZL surface exactly once, from left to right, with roles from the unchanged
56-row V46 sheet. No new role is introduced. The learned namespace contains
exactly the required three surfaces: `oschotshl`, `qetal`, and `secheeol`.

The `chedol` rival defect and the root-detected `otodar` preparation omission
have both been corrected in the final card sheet. Every default and structural
composition now passes. No generic workshop filler or open meaning remains.

## Formal architecture

- Source order: 28/28 exact against the GDT669 newly exposed one-hole rows.
- Full-panel positions: 91.
- Productive cards: 25; learned exact cards: 3.
- New stem roles: 0.
- Every productive atom belongs to `STEM_MODEL_SPECS.tsv` and every atom
  sequence spells the complete visible surface in order.
- `qoiiin` correctly retains the visible preparation frame as
  `QO_COMMAND+O_PREP+IIIN_FORM_IV`; neither candidate omission of `O_PREP` was
  adopted.
- `olaiiny` correctly follows the inherited initial-`ol*` rule:
  `O_PREP+L_WOOD+AIIN_III+Y_START_OR_CLOSE`. It is not misread as initial
  `OL_MATERIAL`.

## Named narrow F licence

`ofalsheky` is acceptably composed as

`O_PREP+F_FLOWER+AL_RAW_I+SH_MOIST+E_MIDDLE+K_HOT+Y_START_OR_CLOSE`.

At f81v.1, ZL has the single token `ofalsheky`, while both IT2a and RF1b split
the same letters as `ofal sheky`. This supplies a genuine bilateral boundary
for the flower/raw-material head before the already known `sheky` process
block. The licence is therefore exact-card-only: it adds `ofalsheky` to the
named `F_FLOWER` examples but does not export `f` into arbitrary substrings.

## Learned forms and reader boundaries

- `oschotshl` is identical in all three readers. A mechanical decomposition
  would violate the internal `S_SEED` and terminal `L_WOOD` scopes, so the
  exact whole is justified.
- `qetal` is identical in all three readers. Keeping it whole avoids placing
  `E_MIDDLE` before its process head.
- `secheeol` is identical in all three readers. The whole prevents the same
  premature-grade overcomposition.
- Both IT2a and RF1b split `otarain` as `otar ain`; the productive composition
  `O_PREP+T_COLD+AR_FRACTION_I+AIN_II` reproduces the same concatenated
  structure, so no alias is needed.
- The single-reader splits `y cthar`, `oe r`, `r tain`, and `oto ar` do not
  override the two-reader or ZL-supported productive cards and introduce no
  invisible atoms.

## Applied correction

The current `chedol` default and parse are correct:

`Drogenstoff bis zur Mittelstufe trocknen und abmessen`

`CH_DRY+E_MIDDLE+D_MEASURE+OL_MATERIAL`

RF1b, however, reads the locus as the two tokens `ched l`. The earlier rival,
“Holzdrogenansatz bis zur Mittelstufe trocknen und abschließen,” was not a
faithful rendering of that boundary: it invented an `O_PREP`/Ansatz and treated
the separated free `l` as bound `L_WOOD`. The final sheet now contains:

```tsv
chedol	Drogenstoff bis zur Mittelstufe trocknen und abmessen	CH_DRY+E_MIDDLE+D_MEASURE+OL_MATERIAL	RF1b: bis zur Mittelstufe trocknen und abschließen; ein Pfund	MEASURE
```

With that applied correction and the `otodar` preservation below, no
structural, ordering, scope, reader-alias, or concreteness defect remains in
the 28-card synthesis.

## Root preservation correction

`otodar` contains two visible `O_PREP` atoms. The audit initially tolerated a
single compact Kaltansatz phrase, but that would hide the repeated preparation
step under the same standard applied to the manual passages. The final wording
therefore preserves both frames in visible order:

`Kaltansatz erneut ansetzen und die erste Fraktion abmessen`

This renders `O_PREP+T_COLD`, then the second `O_PREP`, followed by
`D_MEASURE+AR_FRACTION_I`, without adding an operation.
