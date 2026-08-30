# GDT671 final card audit

## Verdict

PASS. The root synthesis contains all 15 surfaces in the exact first-occurrence
order of GDT670 `NEWLY_EXPOSED_ONE_HOLE_LINES.tsv` and covers 71 full-panel
positions. Thirteen cards use only the unchanged 56 V47 roles; `daiiy` and
`otoiir` are the only learned exact wholes. Every productive sequence spells
its complete visible surface exactly once and from left to right.

No correction is required. There is no generic filler, new role, hidden `n`,
hidden `a`, or hidden terminal `y`.

## Formal checks

- Source order is exactly: `otoiir`, `dolchedy`, `olcheol`, `cth`,
  `oteedaiin`, `qoeedy`, `shekain`, `keocthy`, `ychekch`, `ychey`, `daiiy`,
  `teol`, `ldar`, `qotod`, `toldy`.
- Full-panel count sum is 71.
- Productive/learned architecture is 13/2.
- All productive atoms occur in the 56-row sheet; no extension sheet is
  needed.
- `olcheol` correctly begins `O_PREP+L_WOOD` and ends in the separate bound
  `OL_MATERIAL` carrier.
- `ychekch` ends in visible `CH_DRY`, not an invented
  `Y_START_OR_CLOSE`.
- `daiiy` remains whole instead of being falsely expanded to `d+aiin+y`, which
  would require an absent `n`.
- `otoiir` remains whole instead of borrowing the absent `a` of `aiir` or
  changing final `r` into the `n` of an `iin` form.

## Semantic adjudication

`qoeedy` is correctly retained as the productive command
`QO_COMMAND+O_PREP+EE_END+DY_FINISHED`. “Nimm den vollständig fertiggestellten
Ansatz” keeps the command head, preparation, complete grade, and finished
result without collapsing the card into the passage candidate's opaque whole.

`teol` and `toldy` are appropriately nominal in the final defaults:
“Drogenstoff auf mittlerer Kühlstufe” and “fertiggestellter kalter
Drogenstoff.” Their action readings remain explicit rivals. This preserves the
same `T_COLD` and `OL_MATERIAL` cores without forcing every process-bearing
surface into an imperative.

`shekain` is likewise correctly nominal: “bis zur Mittelstufe eingeweichte und
auf Stufe II erhitzte Droge.” It still renders `SH_MOIST+E_MIDDLE+K_HOT+AIN_II`
in order, while the executable two-part reading remains its rival.

`otoiir` is acceptably fixed as the learned “kalter Ansatz, Fraktion III.” The
meaning is provisional but concrete; the learned namespace makes clear that
`AIIR_FRACTION_III` is not being claimed as a visible decomposition.

`qotod` correctly says “kühle den Ansatz und schließe ab.” Here
`QO_COMMAND` supplies a command frame; it need not add a second lexical “nimm”
before the already explicit cooling action. The rival preserves the take/abzieh
reading without contaminating the default.

## Reader evidence

The guarded three-reader evidence is compatible with the final architecture:

- `daiiy`, `shekain`, and `keocthy` are exact at their frontier loci.
- ZL3b and RF1b agree on `otoiir`; IT2a has `otoiis`. This supports keeping an
  exact ZL whole, not an invisible productive suffix.
- Both alternate readers join ZL `ychekch y` as `ychekchy` at f18r.14. That is
  an occurrence-level RIGHT boundary. The base card remains exactly
  `Y_REFERENCE+CH_DRY+E_MIDDLE+K_HOT+CH_DRY`.
- IT2a shortens `oteedaiin` to `oteedain`, while RF1b preserves ZL. With no
  two-reader alternative, the visible ZL composition remains the correct base
  card.
- Reader merges elsewhere on the same lines (`ol cheor`, `y kchaiin`) do not
  alter the target boundaries for `olcheol` or free `cth`.

The final 15-card sheet therefore needs no structural or wording amendment.
