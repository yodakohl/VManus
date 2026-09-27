# RAW572 author: frozen component and scope contract

Author start 2026-09-27 01:54:56 UTC, after current-route and full root-contract
reading. Absolute author ceiling 02:39 UTC. This first contract is frozen before
assigning the remaining whole forms. Source critic B was read completely.
No previous target meanings are inherited. Root's selected direction, complete
Md2 conclusion C01–18 and all four108ZL/107IT/109RF blocks are retained.

## Exact component choices

These are new C0 hypotheses, not previously identified words:

| Literal | Fixed meaning | Type |
|---|---|---|
| ar | POWER respect | Respect |
| aiin | RECEIVED_PROPERTIES respect | Respect |
| ain | LAST_RESPECT anaphor | RespectRef, evaluated to Respect |
| d | graded-relation lifting | Respect → GradedTemplate |
| qo | greatest-comparison lifting | GradedTemplate → TopTemplate |

The Respect domain of this component family is exactly POWER and
RECEIVED_PROPERTIES. `ain` introduces no third respect. Its fixed resolution
rule returns the most recent preceding **standalone evaluated Respect-valued
expression** in the declared N,E,S,W discourse. A component occurring internally
inside a derived word is not a standalone mention and does not update that
register. Evaluating an anaphor can repeat the already resolved Respect but
cannot switch it. A missing antecedent is a gap, not a default. This rule also
applies to free `ain` and inside `qodain`; no line-specific resolution is allowed.
Any future independently assigned standalone Respect expression would obey the
same register rule and must use one of these two domain values.

Exactly five compound licenses are chosen:

```
dar      = d | ar
daiin    = d | aiin
qodar    = qo | d | ar
qodaiin  = qo | d | aiin
qodain   = qo | d | ain
```

There is no independent `qod` value. The last compound is not exempt because
free `dain` is absent. It computes the same selected-respect operation after
resolving its anaphor; it earns no third distinct-input demonstration.
`oraiin`, `odain`, `sorain`, `sodaiiin`, `qotaiin`, all marked variants and all
other apparent neighbors remain opaque unless separately assigned whole values.
No additional internal cuts, aliases, i-run collapse or universal prefix stripping
are permitted in this packet. Literal `aiinog` is not `aiin og`.

Component inventory cost: three atomic whole-form values, two bound-only
component values, five computed whole types, five licenses and eight internal
boundaries across those five type spellings. The reference value and its
resolution rule are extra costs. These are inventory counts, not a net
compression claim.

## Closed comparison-frame interface

A Respect is a key, not a proposition or a degree. Each respect has its own
ordinal Degree sort and preorder; no common units, numeric scale, calibrated
strength map or cross-respect equality is assumed.

A complete ComparisonFrame F contains:

- respect R;
- a nonempty domain of planet indices q;
- holder(q), retaining who possesses the graded item;
- provenance(q), retaining the donor where relevant;
- an explicit person/event or person/profile context;
- a typed graded observation relation Observe_F(q,v), v:Degree[R].

There are exactly two admissible frame schemas for this family:

1. **PowerFrame(p,e,U):** R=POWER; q ranges over the written seven-planet
   collective U; holder(q)=q; provenance is absent; the scope is time(e),
   where e is explicitly an event of p. The observation is q's degree of
   power at e. Rising-east and great-power requirements are separate guards,
   not consequences of the frame or the comparator.
2. **ReceiptFrame(p,H):** R=RECEIVED_PROPERTIES; q ranges over the actual
   contributor support of the written generic profile H owned by p;
   holder(q)=p; provenance(q)=q; scope is H, not silently e or birth b.
   The observation is the degree of properties received by p from q in H.

A frame is not complete merely because a planet or a person is mentioned.
Its holder, index, profile/event and provenance must be supplied by written
constructions in the subsequent draft. Different holder maps do not make the
two comparisons use different index sorts: both compare PlanetRef values.
No generic HAS shortcut silently turns a human possessor into a planet donor.
A generic profile H may include the leading planet's written contribution,
but no equality of power support and contributor support is inferred.

The component operations are genuinely uniform:

```
d(R) = a GradedTemplate G_R
G_R(F,q,v) iff F.respect=R and q in F.domain and Observe_F(q,v)

qo(G_R) = a TopTemplate T_R
T_R(F,q) iff F.respect=R and q in F.domain
             and some v satisfies G_R(F,q,v)
             and for every r in F.domain and every w with G_R(F,r,w),
                 w <=_R v
```

Thus a top is greatest against all graded comparisons, not merely an element
with no known larger neighbor. The source does not supply degree values; the
writer can assert the relational facts without numerically evaluating them.
The same law applies for both respect values; it cannot inspect a whole-word
tag to dispatch a stored clause. No uniqueness or tie-breaking is introduced.
Multiple greatest candidates can satisfy T_R; the generic singular naming
assertion does not manufacture a unique-selection algorithm.

A GradedTemplate and a TopTemplate are function-valued terms, **not automatic
assertions**. Actual assertions need explicit application to a complete frame,
planet index and, for G_R, degree. A subsequent typed construction may take a
template as a named argument, but that mention does not count as an instantiated
compositional contrast. Application and any template-as-data use must be
separately declared in the whole grammar. Both POWER and RECEIVED_PROPERTIES
must receive actual instantiated graded and greatest applications before the
two-layer requirement is called satisfied. No undeclared cast is permitted.

This packet introduces no syntax/denotation-history layer. The templates above
are ordinary semantic functions. Future surface productions must state argument
order, result type and scope; unknown higher-order constructors are not a
standing rescue permission. Their signatures and uses must be explicitly
written and costed before final freeze.

## Source scopes, fixed before remaining words

One generic human p persists through attribution, receipt and naming. The
mother belongs to the conception relation. Initial e belongs to that p, with
kind(e)=BIRTH OR kind(e)=CONCEPTION; neither disjunct is erased or turned into
a second observed horoscope. Its time owns the initial power comparison and
east-rising/great-power guard. The qualifying leading planet q must satisfy
T_POWER(PowerFrame(p,e,U),q), great power and eastern rising before the child
claim. The same q gives its nature-qualified properties to p.

The full received profile H is a generic profile of that same p, introduced
by a written construction at counted cost. It is not an implicit sum of birth
and conception profiles or automatically identical to the power-at-e support.
C07 is read with the donor planet as strength bearer; property-strength remains
a recorded source alternative. Dependence of the given degree on strength is
retained without a linear rule, common measure or aligned power/share ranking.
C12 ranges over each actual contributor of H; its narrower attachment to the
immediately preceding all-planets class remains a source alternative.

The rare sole-power assertion is qualitative and permits such cases. Generic
multiple receipt is not made an exceptionless lower bound. The some-two,
some-three and some-all-seven assertions keep the same receipt/support domain
and are not an exhaustive allowed-count list. The seven-planet domain comes
from the source recap, not a picture count or seven invented proper names.

The naming planet r is in H's support and satisfies
T_RECEIVED_PROPERTIES(ReceiptFrame(p,H),r). It need not equal the initial q.
Final b is explicitly the birth of p: if e is birth, e=b; if e is conception,
e is distinct from b. BornUnder(p,r,b) and PlanetDay(r,b) OR PlanetHour(r,b)
retain that same r in both disjuncts. BornUnder is not defined as sole power,
greatest power or biological parenthood. These are necessary owned assertions
in the chosen synopsis, not a claimed sufficient or unique naming algorithm.

## Whole task and stopping boundary

Use N,E,S,W presentation, allowing only explicitly declared cross-line and
cross-block discourse rules. This is not a source-to-figure mapping. All C01–18,
including recap, two consequential links, adversative, and final etc., require
written places. All selected literal rows and every assigned outside occurrence
in .1/.24 remain obligations. Primary ZL is bookkeeping, not preferred pixels;
IT/RF are alternate readings of the same manuscript, not independent evidence.

No unassigned remainder may be filled by a one-word complete-source-sentence
macro. New whole values and generic grammatical constructions are allowed,
itemized and frozen in the final packet. If complete clauses cannot be authored
with these component choices, preserve the exact partial, all remaining groups,
and earliest unsatisfied ownership/type/source obligation. Do not repair this
contract, switch respect meanings, grant qodain a whole-form exception, or fall
back to an old quality/negation interpretation.

A rival aligning leading power, leading received share and naming under a
written common scope/order bridge remains possible. The source supplies no
observed unequal maxima. Report any equality of consequences honestly; a
complete hypothetical reading would not confirm a morpheme, a planet, the
source exemplar, or a historical horoscope.

First contract frozen 2026-09-27 01:59:24 UTC. Remaining whole values are not yet assigned.
