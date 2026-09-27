# RAW569 author clarification: frozen commitments and remaining gaps

Started 2026-09-27 01:34:06 UTC; maximum ten minutes, including this record.
This is clarification and criticism of the frozen packet, not a revision of it.
No new target, source, image, lexical assignment, grammar or executor is supplied.
Only this file is owned by this follow-up. The current route was read first.

Inputs: the frozen author draft SHA256
`6f696bafb5a22f94fd2649558d0292183b1757cc2fdaa01a6dd0b9033416080d`,
its report SHA256
`958b9ff86a21551986c28448d33892bde6833fb489c7df9becfe60360cd03c16`,
and root's frozen initial review SHA256
`3f57b3dcb393f9f64901d66608ed23e1fe91218ab2dfc6623d081c261c678912`.
The independent B replay was not read. All references below are to the existing
JSON fields/rules, not newly adopted definitions.

## 1. View value versus retained expression structure

**A conceptual distinction is explicitly present, but its complete formal
interface is not supplied.** The type contract describes a View as a record
with referent, station and scope. The `or` definition separately says to retain
the input view in the expression tree. G04 mentions the inner expression node;
G05 lists inner and outer nodes for paired reporting. The N1 formula explicitly
names both v0 and v1 and then supplies both to PAIR. The report calls node
retention and the inner-before-outer ordering added choices.

Thus the freeze did not merely forget that the first station would be lost by
pure last-frame evaluation. It expressly requests access to an expression
structure in addition to a final View value. However, it never gives separate
formal types for expressions and denotations, a complete expression grammar,
an evaluation/projection function, or the typed interface through which G05
observes nodes while ordinary FRAME applications use View values. Those are
real remaining formal costs. Counting G04/G05 among 32 prose rules does not
make that interface a completed derivation certificate.

For the three-field View **denotation**, reframing from f to g can obey the
last-frame law: the final record is the same as a direct view at g. For the
retained **expression**, the nested construction still contains the f node,
whereas the direct construction does not. G05 observes that difference. The
packet therefore does not own an unrestricted equivalence saying the nested
and direct expressions can be substituted in every context, including G05.
If last-frame equality is instead imposed on the only available object and
all contexts must respect that equality, the inner report cannot be recovered
from that object. The current packet has not resolved this by a fully typed
two-layer semantics.

This also limits the rival statement. Direct contextual relations can retain
the same two written station arguments and paired expression structure without
an intermediate View ontology. A rival that first erases every inner node and
retains only the final triple cannot reproduce N1's two reports without some
other ownership mechanism. The frozen rival's equivalence is therefore an
extensional content comparison **with the written pairing structure retained**,
not a proof that every syntax-sensitive context reduces to one final triple.
This qualification describes the existing retention provisions; it adds no new
AST, evaluator or repair.

## 2. Outside `shedaiin olaiin`: local failure versus extension impossibility

The frozen G15 construction requires a GroundProperty to the right of
INDICATES. The literal next assigned value is `olaiin=SAME_TRAVELLER`, an
ObserverRef. Under that direct G15 application, the required operand is wrong.
G02 prohibits an undeclared coercion, and no frozen rule turns this person
reference into a ground-body property. Missing surrounding discourse does not
make this particular direct application well typed.

**G02 does not explicitly close the language against all future higher-order
constructors.** It says constructors consume explicit typed operands in written
order and prohibits arbitrary scalar/function interpolation and undeclared
coercion. It does not enumerate all permissible constructor signatures, state
that every relation token must immediately apply to its next token in every
context, or explicitly prohibit a relation from being passed as an operand
together with a person reference to some other declared constructor.

Conversely, the packet does not explicitly provide that higher-order facility
as a complete extension mechanism. Relations are assigned lexical types, but
there is no complete function-as-value type system, quotation law or enclosing
outside construction with a frozen signature that already consumes this pair.
Assigning an unknown surrounding word such a role would be an additional
semantic/type commitment whose admissibility under G02 would need to be fixed.
It cannot be treated as a free, already supplied rescue. No such assignment is
made here.

The supported result is consequently a **failure of the demonstrated G15
application**, not an exhaustive proof that no unchanged-value extension could
ever parse the outside sequence. Whether a future proposal could express an
enclosing constructor using the existing generic application wording, or would
need an additional grammar/type rule, is not settled by the freeze. Neither
“one more unknown word certainly fixes it” nor “no lexicon extension is
possible” follows. Root's initial review already keeps this distinction.

The author packet supplied zero outside clauses and expressly left all 47
assigned outside occurrences as obligations. This clarification does not
change that status or supply an outside observer/Earth scope.

## 3. E1 mixed celestial coordination and later reference

**The collective topic is declared in prose, but the output kind and reference
typing of the mixed coordination are not fully declared.** G03 says the stars
binder yields its introduced Class; `qokedy` has CelestialClass type; AND
coordinates matching types; G10 calls their coordination the current collective
topic. E1 writes `topicB=COORD(stars,SIGNS)`. E2 applies rising/setting comparison
to that topic, and E6 uses `aiin` as a WorldRef to the same topic.

These statements show the intended content. They do not explicitly define
COORD's result type or specify what happens to the declared kind. The type
contract describes a nonempty CelestialClass with kind Star or Sign. It does
not state that a single class may carry a mixed kind, that member kinds may be
heterogeneous, that coordination produces a pair/list of classes, or that such
a pair/list is itself admitted to WorldReferent and ordinary reference rules.
The shared outer name CelestialClass makes the intended input compatibility
plausible; it does not by itself establish closure of the output under every
refinement stated in the kind field.

If Star/Sign is a uniform tag on each class, a direct mixed union has no
specified output tag. If coordination instead produces a structured pair,
E6 needs an explicit way for its WorldRef anaphor to designate that pair.
Those are illustrations of the missing choice, **not alternative repairs
adopted by this clarification**. The freeze does not pick one of them.

Accordingly, the E1-to-E6 reference path is informally presumed, not certified
by a complete declared mixed-collective typing rule. This is a genuine formal
completeness gap. It need not be described as a contradiction under every
possible elaboration of CelestialClass, but the author should not claim that
the frozen types already decide and validate the elaboration. The reported
108-group coverage remains a count of authored assignments/formulas; it is
not proof that this collective reference is well typed.

## 4. Converse route, realization and endpoint identity

The frozen wording establishes route **roles and regions**, a new explicitly
distinct observer b, preservation of the two class referents, and a converse
case conditional on realizing the prior visibility regime. The `qokshedy`
definition says route pattern; `chckhy` describes a source endpoint in the
southern region and `ykeedy` a northern destination. G24 states reversal and
its realization guard. G25 owns the active converse before/after endpoints.

It does **not** write the equations `s_b=s2` and `n_b=n`. W3 uses the distinct
symbols s_b and n_b; the previous forward formulas use n and s2. Nor does it
write inequalities forbidding identical locations. Exact physical endpoint
identity is therefore unspecified. The prose “reversed route pattern” cannot
be upgraded retrospectively to a uniquely fixed pair of geographical sites.
The W3 scope symbol cB is also not explicitly equated to the earlier cC.

The realization condition is written, but its full endpoint-correspondence
relation and adequacy criteria are not. Southern/northern direction alone
would not compute the required visibility states. W3 explicitly **asserts**
the two reports using `qokal` and `shedy`; it does not derive their values from
the direction words. A source-compatible interpretation can select a
corresponding reverse case, but the freeze provides no numerical or complete
geometric evaluator proving that selection exists for every regional endpoint
pair. The source itself is not new evidence identifying those physical sites.

The author therefore retains the ambiguity: correspondence by route pattern
and conditional visibility content are declared; exact same locations and an
exact transferred physical observation regime are not. The new person/class
ownership claims remain as written. Nothing here changes an endpoint, chooses
an equality, adds a travel threshold or changes a report value.

## Clarified status

The frozen packet is a complete authored ZL assignment and proposed synopsis,
with known literal alternate failures. It is **not** a fully formalized ZL
compatibility certificate. The requested checks expose or sharpen three
remaining interface issues: syntax versus denotation, unknown-constructor
admissibility, and mixed-class coordination/reference. Converse endpoint
correspondence remains partly specified. These qualifications reduce what may
be claimed from the packet; they do not revise its meanings or retroactively
supply successful derivations.

Clarification frozen 2026-09-27 01:37:11 UTC. The decision, draft, report and root initial-review hashes were verified unchanged.
