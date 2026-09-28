# GDT1080 — exact `chor`/`shor` versus drawn flower/berry states

**Decision: the GDT768 flower/fruit direction remains tied.** The complete
GDT364 panel intersects the admitted word cache on 32/34 pages. `f54r` and
`f90v2` are absent from that cache and were explicitly excluded before any
target-word query. All 32 retained pages, including zero-occurrence pages, are
in `artifacts/PAGE_COUNTS.tsv` for each of three alternate readings.

| Reader | flower pages `chor/shor` | berry pages `chor/shor` | neither class | F/B target odds ratio |
|---|---:|---:|---:|---:|
| ZL3b | 38/12 on 17 pages | 10/5 on 8 pages | 17/7 on 7 pages | 1.613 |
| IT2a | 36/13 | 13/5 | 17/7 | 1.102 |
| RF1b | 40/11 | 10/6 | 17/6 | 2.180 |

The primary ZL3b result misses the frozen 2.0 magnitude gate. All three
readers have the same aggregate sign, but they read the same manuscript; they
are sensitivity checks, not independent replications. The two within-physical-
folio contrasts oppose one another in ZL3b and IT2a: f4 favours `chor=flower`
at odds ratio 1.667; f17 favours the reverse at 0.333. Their log odds sum is
negative while the all-page contrast is positive, failing the pair gate. RF1b
reads f17 at 1.0. The `NO_FRUIT_OR_FLOWER` class still contains 17 `chor` and
7 `shor` in ZL3b. Thus page content is at best a weak, nonspecific ecological
association, not a bound depicted-organ reference.

The test has enough raw instances under the predeclared capacity gate, so this
is a failed directional contrast rather than missing data. It does not refute
that either word can refer to a plant part; it refutes selecting one direction
from this specific visual panel under the registered rule. No significance
claim or confirmed word follows. Prior BERRY001/FLOWER001, GDT364 and GDT366
nonconfirmation remain intact. The page annotations and target forms were
previously exposed; the fixed method was written before querying target
counts, with the missing-page membership correction documented there.

`src/run.py` reads only the guarded, admitted descriptive cache and checks its
source/allowlist receipt plus the frozen panel hash. `src/validate.py` checks
96 page-reader rows, class sums, odds arithmetic, seals and the final decision:
**PASS**. Elapsed work was below the 75-minute cap (preparation and execution
in the first 10 minutes); no further decoder or visual feature search is
warranted by this result. Reopen this route only for a new independently owned
organ referent and a different predeclared word-to-referent consequence.
