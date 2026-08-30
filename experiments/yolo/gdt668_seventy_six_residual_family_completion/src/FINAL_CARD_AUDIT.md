# GDT668 final card synthesis

## Decision

The V44 stem compositor supplies the formal spine, the recipe master supplies
practical object and operation wording, and the passage reader supplies
sentence-local direction. The final 76-card deck contains 74 role-composed
cards and two learned exact wholes. It adds two narrow recurrent blocks to the
52-role V44 sheet; no new page or image is used.

## The high-frequency spine is inherited

The eight most frequent targets need no new value:

- `okeor = O_PREP+K_HOT+E_MIDDLE+OR_PORTION` occurs fifteen times;
- `cheeor = CH_DRY+EE_END+OR_PORTION` occurs thirteen times;
- `shedain = SH_MOIST+E_MIDDLE+D_MEASURE+AIN_II` occurs twelve times;
- `cheeol = CH_DRY+EE_END+OL_MATERIAL` occurs nine times;
- `okees = O_PREP+K_HOT+EE_END+S_TERM_SPECIES` occurs nine times;
- `qolchey = QOL_ADD+CH_DRY+E_MIDDLE+Y_START_OR_CLOSE` occurs nine times;
- `qotcho = QO_COMMAND+T_COLD+CH_DRY+O_PREP` occurs nine times;
- `tody = T_COLD+O_PREP+DY_FINISHED` occurs nine times.

These cards distinguish portion, material, charge, closure, and completion
without changing the meanings of their shared process heads.

## New terminal block: `YD_POST_CLOSE`

The inherited exact token `yd` means “vorstehenden Rezeptposten abschließen.”
The known `dsholyd` already places that same visible ending after a complete
measured moist-drug head. The new panel adds `otchyd` twice and `rokyd` once.
Across the four forms there are seven positions; every `yd` is either the
complete token or the absolute token-final ending of a complete process or
material head. The resulting narrow role is:

`YD_POST_CLOSE = yd = Posten abschließen`.

It composes:

- `otchyd = O_PREP+T_COLD+CH_DRY+YD_POST_CLOSE`, “kalten Ansatz trocknen und
  den Posten abschließen”;
- `rokyd = R_ROOT+O_PREP+K_HOT+YD_POST_CLOSE`, “Wurzelansatz erhitzen und den
  Posten abschließen.”

This is preferable to forcing internal `Y_START_OR_CLOSE` before a second
terminal `D_TERM_CLOSE`. The block does not license arbitrary internal `y+d`.

## Reader-visible block: `SQOKEO_SEED_HEAT_PREP`

ZL3b writes `sqokeodaiin` as one token at f88v.20. IT2a and RF1b independently
write the exact same line as `sqokeo daiin`. The right card is already the
productive `D_MEASURE+AIIN_III`, three doses. The left block is therefore kept
as one locally reader-visible card:

`SQOKEO_SEED_HEAT_PREP = sqokeo = erhitzte Saatgutzubereitung der Mittelstufe`.

The full target becomes
`SQOKEO_SEED_HEAT_PREP+D_MEASURE+AIIN_III`, “drei Dosen erhitzter
Saatgutzubereitung der Mittelstufe.” This avoids widening initial `S_SEED` into
an unsupported wrapper before every `QO_COMMAND`; no free `sqo-` rule is added.

## Two learned wholes retained

- `dairin`: the visible `air+in` would attach preparation Form II directly to
  the fraction-II block, outside the inherited IN scope. It remains the exact
  card “abgemessene zweite Fraktion, Zubereitungsform II.”
- `eaiin`: the surface lacks a material or process head that would decide
  whether `aiin` is a quantity or a process grade. It remains the exact card
  “drei Teile auf Mittelstufe.”

Both preserve concrete defaults. “Learned” means memorized as a whole workshop
card, not untranslated.

## Passage wording rule

Nominal cards remain nominal in the manual passages. A command is introduced
only by a command/reference card or by an explicitly operational whole. Every
visible drying, moistening, heating, cooling, measuring, preparation, finish,
and closing block remains in the German reading; no water, wine, oil, salt,
vessel, disease, or cure is supplied by context alone.
