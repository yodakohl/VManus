# GDT666 final card audit

## Result

The final deck has the required 151 unique surfaces and the stem model has 47
unique roles. All 151 declared compositions reconstruct their surface exactly;
all 20 `LEARNED_*_WHOLE` cards use the sole exact-surface namespace. Terminal
`-s`, terminal `-d`, `qol`, `qokol`, `iin`, and initial `Y_REFERENCE` pass their
declared positional rules.

The deck is **not yet a full scope PASS**. Three productive parses exceed the
published scope of their atom. Two further rows should recover the stronger
historical/editorial choice. No water or liquid wording occurs. Portion wording
is backed by `OR_PORTION` or an exact learned whole throughout.

## Required structural corrections

1. `chosory`: internal `S_SEED` is followed by `OR_PORTION`, not immediately by
   a grade, charge, or `DY` close marker. The existing validator only checks
   that `S_SEED` is nonterminal, so this is a false pass. With the current
   47-role model the honest repair is an exact learned whole.
2. `koddy`: internal `D_MEASURE` is followed by `DY_FINISHED`; the published
   `d-` scope permits initial `d` or `d` before a quantity, material, or form
   head. This occurrence satisfies neither condition.
3. `ldchey`: internal `D_MEASURE` is followed by the process head `CH_DRY`,
   likewise outside its scope. The historical candidate already made this an
   exact whole.

Exact recommended replacement rows:

```tsv
chosory	eine Portion Saatgut im Trockenansatz, abgeschlossen	LEARNED_CHOSORY_WHOLE	abgeschlossene Trockenansatz-Charge	SEED
koddy	erhitzten Ansatz abmessen und fertigstellen	LEARNED_KODDY_WHOLE	fertig erhitzte Ansatzdosis	ACTION
ldchey	Holzdroge abmessen und bis zur Mittelstufe trocknen	LEARNED_LDCHEY_WHOLE	abgemessene mitteltrockene Holzdroge	ACTION
```

These changes require no new stem-model row.

## Recommended historical/editorial restorations

`g` is structurally legal as `LEARNED_G_WHOLE`, but “Mischung fertig” has no
visible family relation and discards the historical candidate's concrete
apothecary reading. Restore its documented grain default and drop default/rival
duplication.

`chololy` is structurally legal as an exact whole, but “seihe ... ab” introduces
the deck's sole flow operation without a flow-bearing stem license. The
historical candidate gives an exact, fully licensed `ch+ol+ol+y` parse and is
therefore preferable under the stated no-invented-flow rule.

```tsv
g	ein Gran	LEARNED_G_WHOLE	ein Tropfen; historisch ist G auch für gutta belegt	MEASURE
chololy	zwei Drogenstoffe leicht zusammen trocknen	CH_DRY+OL_MATERIAL+OL_MATERIAL+Y_START_OR_CLOSE	einen Drogenstoff in zweiter Ansatzform trocknen	DRY
```

## Focus-card disposition

- `ykeeochody`: PASS. `y+k+ee+o+ch+o+dy` is exact; the two Ansatz frames are
  explicitly represented and `Y_REFERENCE` is initial.
- `chokokor`: PASS. `ch+o+k+o+k+or` is exact and the portion language is
  licensed by terminal `OR_PORTION`.
- `keeees`: PASS as an exact whole. A productive `K_HOT+EEE+S_TERM` parse would
  spell `keees`, not the observed four-`e` form.
- `dshodar`, `dsheedal`: PASS as exact wholes. Their historical productive
  parses also reconstruct and respect scope, but retaining learned wholes is
  conservative rather than contradictory.
- `qochol`: PASS. The final `QO_COMMAND+CH_DRY+OL_MATERIAL` correctly spells
  `qo+ch+ol`; the historical candidate's added `O_PREP` would spell
  `qoochol` and must not be restored.
- `qopchaiin`: PASS. `qo+o+p+ch+aiin` and its three-part powder wording agree.

## Validator/replay note

Running the current validator after the central synthesis gives
`FAIL 7690/7718`. The semantic/source failures name `qopchaiin`, `g`,
`checthey`, `eey`, and `ycheckhey`; the remaining failures are the stale input
hash and byte-replay artifacts caused by changing `CARD_SPECS.tsv` without a
fresh run. In addition to regenerating artifacts, the validator needs explicit
scope checks for internal `S_SEED` successors and every noninitial
`D_MEASURE` successor; its present nonterminal-only tests miss the three hard
errors above.
