# GDT377 report — local-head signature transfer

## Result

The frozen CoReMA local-head-with-dependents detector was applied once to all
8,448 f84-free GDT327 atomic tuple events in 288 physical records. It scores
1,676 exact tuple identities; 111 have the predeclared minimum of 12 events
and three physical folios.

**No tuple passes the transfer gate.** No powered tuple has mean comparator
probability >= .5, and none has at least 75% of its folio means >= .5. The
strongest powered tuple (`12286f9a28a5c841bc2d`) occurs 12 times on 12 folios,
has mean probability .326614 and structural-minus-nuisance delta +.216334, but
only 2/12 folios clear .5. The largest folio-consistency fraction anywhere in
the powered panel is .20.

## What did transfer

There is a narrower formal result. Of the 111 powered tuples, 102 have positive
mean structure-minus-nuisance delta. The maximum delta is unusually large
under 4,096 section/register/hand/length/position-preserving tuple-ID shuffles:
local max p = .003417 (null mean .150688, observed .216334). Exact tuples are
therefore concentrated in recurring structural contexts more than this null
expects.

That relative concentration is not the comparator functional class. Absolute
calibration and cross-folio consistency were frozen precisely to prevent a
post-hoc low-threshold nomination, and both fail. No tuple is promoted and all
semantic states remain `UNASSIGNED`.

## Consequence

The comparator-first roadmap has yielded a useful discrimination:

- form-blind structure can recover local heads in readable CoReMA;
- the same detector sees nonrandom tuple/context concentration in Voynich;
- but no exact Voynich tuple behaves consistently enough to inherit that
  anonymous class.

Do not lower the .5 or .75 gates, select the p=.0034 tuple as a predicate, or
infer action, POS, valency, arguments, meanings, or translation. The separate
high-valency and dependent endpoints already failed in GDT376.

No f84 row was opened, parsed, retained, or scored.
