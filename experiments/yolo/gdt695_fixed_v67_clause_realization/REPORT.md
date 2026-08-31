# GDT695 — V68 fixed-word clause reader

Status: `PASS_V68_83_ACTION_CLAUSES__92_NOMINAL_BLOCKS__175_TOTAL__115_VERBS__ZERO_WORD_DELTA`

## Result

The fixed V67 words now have an explicit clause-level presentation. Across all
51 lines, V68 emits 175 units:

- 83 clauses, each containing exactly one written GDT689 action card;
- 92 maximal nominal register blocks;
- 115 active verb occurrences, all inside the 83 action cards;
- ten inherited local head/value bindings, nine shown by a colon and one
  retained inside an unchanged bound span;
- four exact right-bound connector positions;
- zero added, deleted or reordered content words.

The 16 `ACTION_SEQUENCE` lines contain 49 action clauses and 38 nominal
checkpoints. The 23 `MIXED_RECORD` lines contain 34 action islands and 42
nominal blocks; they are not promoted to continuous recipes. The six
`NOMINAL_REGISTER` and six `QUANTITY_LABEL` lines contain no action clause.
Here `NOMINAL_BLOCK` means a maximal non-action/register run, not a word-class
claim about every contained card; three such blocks include an exact
right-bound connector. A full stop around a result fragment does not make that
fragment an action.

## The important correction

An initial audit appeared to find five bad V67 cards by comparing them to
GDT688/V61's 85-position/113-verb table. That comparison was wrong because
GDT689/V62 had already superseded the action inventory.

Under V62, `olchdy` and `dshedy` are deliberately nominal. Conversely,
`ytedy`, `checthedy` and `qolsheedy` deliberately retain sister-derived active
verbs. The correct live totals are 83 action positions and 115 verbs. A fresh
full-deck scan gives exact ordered verb sequences at 83/83 positions, 115/115
occurrences, and zero verb matches at the other 396 positions. The proposed
five-card rewrite was therefore retracted before entering any artifact.

This also narrows the older GDT694 wording that “all 113 verb profiles survive.”
Those 113 rows remain a historical V61 preservation view; they are not the
current multiplicity inventory. The V67 text itself is sound against the live
V62 inventory, and GDT695 publishes the correct baseline explicitly.

## What the renderer changes

V68 changes punctuation and capitalization only. Action cards become separate
sentences; adjacent non-actions remain semicolon lists. Exact punctuation cards
never produce blank clauses. Four right-bound connectors are joined to their
immediate target, and only the ten already accepted GDT676 value bindings may
receive stronger punctuation. All three GDT694 spans remain byte-identical.

For example, f76v.10 keeps `dshedy` nominal:

> Eine Portion Arzneikompositum abmessen. Feuchte abgemessene Rohstoffmenge I
> in der Gradmitte. Fertig getrocknetes Pulver nehmen. Bis zur Mittelstufe
> angefeuchtete Drogenportion; mittlere Feuchtstufe erreicht; kalt-trockene
> Mittelstufe erreicht; Rohholz I, vollständig eingeweicht und kaltgestellt;
> bis zur Mittelstufe eingeweichtes und abgeschlossenes Arzneikompositum: drei
> Portionen des eingeweichten Arzneikompositums.

At f104v.2, three action islands are no longer buried in one semicolon stream:

> Hiervon drei Dosen bis zur Mittelstufe getrocknete Droge abmessen. Auszug
> vollständig abkühlen und abziehen. Trockene Arzneizubereitung, Gradanfang;
> kalter Ansatz, Grad III; davon drei Maße. Ein Maß nehmen und erhitzen.
> Unteranteil I des Anteils I des kalten Ansatzes; Rohdroge I, bis zur
> Mittelstufe getrocknet und abgeschlossen; Anteil II des kalten Ansatzes; eine
> Maßportion Ansatz.

## Limit and next route

This is a more usable rendering of the current working theory, not recovered
plaintext. It adds no object carry, unstated subject, inferred sequence word or
new semantic assignment. The next bounded route is to test only a finite deck
of cross-clause object/carry edges that already have an explicit donor and
existing local provenance. Unresolved `hiervon/hierzu/hieraus` positions must
remain unresolved rather than being completed by fluency.
