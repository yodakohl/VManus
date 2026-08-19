# GDT347 prepublication held-folio null correction

The first uncommitted scorer pass applied the frozen Voynich model to all 17
held folios as one pseudo-fold. Aggregate observed codelength was correct, but
the coupling null consequently stratified those events under one held label
rather than their physical folios, and the reported positive-folio count was
not meaningful.

This was detected before any GDT347 result, report, ledger result row, or
validation was published. The scorer now retains the same frozen graph,
weights, marginals, held folios, events, endpoints, and decision rules while
emitting one score fold per physical held folio and using physical folio in the
already-frozen null stratum. All control code and all graph parameters are
unchanged. The initial result bytes are superseded and have no evidential
status.

No f84 data was accessed.

After the corrected aggregate decision was visible, the scorer was augmented
with a requested decomposition of the three already-frozen edges. It reports
each edge's gain, support, coordinate-change capacity, inclusive null p, and a
max-four diagnostic over the combined graph plus three edges. This adds no
edge, changes no weight, does not enter the frozen decision, and is labeled a
post-score diagnostic rather than confirmatory evidence.

The first diagnostic build also aggregated section/register/hand gains by
whole held-folio membership. A folio spanning more than one section therefore
duplicated its fold gain across categories. This was caught before publication.
The final scorer accumulates environment gains at the scored-event level and
counts positive held folios separately inside each environment. Panel, graph,
edge, null, and decision values are unchanged.
