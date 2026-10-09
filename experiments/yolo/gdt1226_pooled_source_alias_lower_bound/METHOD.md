# Certificate logic

Five source types occupy at most ten output forms under a global two-spellings
contract. The ten largest output forms contain at least their combined mass,
even if source forms coalesce. Two private equal aliases per source word attain
the five-largest-source sum in the continuous relaxation.

Let a[S,b] be the count of a five-word set S in book b. Each mixture has top5
mass >= sum_b lambda[b]*a[S,b]. Nonnegative d[S] summing1 preserve this bound
when averaged over sets. Consequently the mass is at least
min_b sum_S d[S]*a[S,b], an exact lower certificate. Evaluating every word at
one rational lambda supplies an upper certificate for the minimum. Numerical
optimizer correctness is not needed for these inequalities.

The separate validator rebuilds32000old source positions and checks every
rational certificate without the LP. A tight bracket identifies the relaxed
optimum; any bracket decides ceilings strictly outside it. Engineering bands
are not significance tests. No integer text, physical script or native meaning.
