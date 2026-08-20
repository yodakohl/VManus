# GDT396 semantics-light panel fail-closed correction

Status: `AUTHORITATIVE_BEFORE_QUALIFICATION_GENERATION`.

The final prequalification re-audit found one residual fail-open path. The
qualifier rejected a missing event-level false-positive rate inside a present
W10 route, but treated a completely absent W10 route as an empty list and
therefore as a zero false-positive rate.

The corrected qualifier requires exactly five distinct W10 qualification
seeds for every semantic property, decoder, representation, and surface route.
Each of those rows must expose the registered event-level false-positive
quantity. Missing worlds, seeds, or rates now raise an error rather than
qualifying the route. A development-only adversarial fixture verifies this
failure mode.

This is an enforcement correction only. No qualification or confirmation
observation existed when it was made. No hidden-world truth, generator,
decoder method, property threshold, manuscript source, Voynich row, `f84`, or
`f84r` data was inspected or changed.
