# R1: a finite compositional whole-group writing proposal

2026-09-15. Source-only proposal; inclusive checkpoint 14:20 UTC.
Status: RAW_UNREVIEWED_NOT_SELECTED. No target parser or decoder is built.

R1 is a concrete alternative writing rule for the existing finite semantic
language S0. It adds no new alloy semantics and claims no historical notation.
Its distinguishing hypothesis is that an operator and its atomic material,
reference and numerical arguments form one written group. Nested operations
remain explicitly connected across groups. The same global component code and
two fixed agreement functions generate every group; there are no per-word
meanings, silent words or exceptions. Complete programs have variable expression
trees and statement counts within S0's already declared bounds.

## Predecessors and the exact remaining question

The current route, composition topic, bounded idea search and instruction-code
route-check were read before drafting. The relevant full primaries were read:

- [IDEA000124](../../proposals/linear_material_register_program.json) already
  specifies whole-group opcodes, decimal register/rational arguments, and a
  global symbol key. Its missing independently owned inventory endpoint remains
  a stop. R1 is not a claim that whole-group instructions are new. That card
  consumes physical stock and creates new states; S0/R1 instead refers to
  immutable recipe definitions. Reusing a recipe is not duplicating possessed
  metal. For example `MIX(RREF(0),RREF(0))` denotes two batches of one recipe in
  S0, whereas consuming the same physical input twice violates IDEA124's rule.
- [S0/R0](ALLOY_FINITE_GRAMMAR.md) already supplies those recipe semantics,
  complete two-path and generated accounts, and a finite prefix component code.
  R1 retains S0 exactly and changes only grouping and deterministic allomorphy.
  It is a rival writing model, not another source discovery or new arithmetic
  hypothesis. The existing source projection and all omitted Latin content
  remain explicitly outside S0/R1.
- [GDT882](../../../experiments/yolo/gdt882_additive_line_lattice/REPORT.md)
  excludes nontrivial fixed additive whole-line invariants on its exact scope,
  including the stated solvable-group corollary. R1 asserts neither a common
  additive line sum nor a common whole-line group product. Literal spaces mark
  complete syntactic groups; complete accounts may contain different content.
- [GDT903](../../../experiments/yolo/gdt903_universal_reversible_line_action/REPORT.md)
  supplies an unrestricted reversible-automaton compatibility witness without
  identifying a writing rule. R1 cannot add states or transitions to fit a text:
  its only entry state has two fixed values; its six agreement categories are
  fixed functions below. Semantic recipe registers are S0's bounded typed
  values, not arbitrary automaton states.
- [GDT708](../../../experiments/yolo/gdt708_v81_variable_batch_terminal_product/REPORT.md)
  retains variable attribute stacks and a scoped terminal-product reading; its
  analytical endpoint is not authorial punctuation and its edge packet remains
  unscored. [GDT741](../../../experiments/yolo/gdt741_local_attachment_boundary_relay_grammar/REPORT.md)
  compresses inherited attachment decisions but remains fitted in-sample with
  singleton rules and unresolved collisions. Neither licenses S0's operations,
  quantities, code, group boundaries or target owners. No old gloss is imported.
- [GDT971](../../../experiments/yolo/gdt971_alloy_numeral_binding_control/REPORT.md)
  identifies the identity digit map only under its complete five-account source
  oracle, known roles, arithmetic and decimal spelling. Adding path P after Q
  removed no additional map: identity and the unused 8/9 swap both survived.
  Thus a second branch is not automatically an extra discriminator. Its free
  whole-quantity-label rival remains a counterexample to unbound numerical
  meaning. R1 retains shared numerical components rather than assigning each
  complete amount its own value.

The precise new unknown is whether one bounded globally shared **grouping and
realization rule** can express complete S0 accounts while fitting literal whole
groups. R0 separates most constructors/arguments into words; R1 joins an operator
with its atomic arguments and records every remaining nested argument explicitly.
The same semantic account therefore makes different written-boundary predictions.
No target search is selected by this proposal.

## S0 is unchanged

The authoritative syntax, limits, complete source-derived programs and new
`(4,4,12)` account are [ALLOY_FINITE_GRAMMAR.json](ALLOY_FINITE_GRAMMAR.json),
SHA-256 `b852e2ec8e191bebdc904d1274a79174b5fa08bb3cd24980128286895dbab109`.
Its source-only evaluator is [alloy_finite_grammar.py](alloy_finite_grammar.py),
SHA-256 `bc04278d040217de9b7d97bd08943429374f97c3a36d02d38001f54e900f5ce3`.
This proposal reads those existing examples; it does not rewrite them.

S0 has three grade types, a target grade and mass, one to three branches, at
most twenty statements per branch, eight quantity and eight recipe registers,
expression depth at most six, and the existing numerical bounds of 400.
Backward references, use of every declaration, positive portions/scales,
integral repeat-fill, all written assertions and every branch's final mass/
fineness must pass. The strict grade ordering prevents an all-equal-grade
collapse. Alternative outputs may have different ingredient vectors and
histories. Header bounds and statement limits are modern finite-model choices,
not manuscript measurements or a required source/paragraph word count.

```
Q := NUM(n) | MIXED(NUM(w),NUM(p),NUM(d)) | QREF(i)
   | ADD(Q,Q) | SUB(Q,Q) | MUL(Q,Q) | DIV(Q,Q)
   | MASS(R) | FINE(R) | GRADE(R)
R := RREF(i) | PORTION(type,Q) | MIX(R,R) | SCALE(Q,R)
   | REPEAT_FILL(R,R,Q,Q)
S := SETQ(i,Q) | SETR(i,R) | ASSERTQ(property(R),Q)
   | ASSERTWEIGHTS(R,Q,Q,Q) | YIELD(R)
```

The native mixed spellings stay mixed. For example `3+5/7` is not silently
rewritten as `26/7`; the latter may arise as an arithmetic value. Decimal digits
are shared across numbers and register indices exactly as in R0. No GDT969
INPUT/HIGH record, fixed step count or equal-width field code is used.

## Exact finite R1 productions

An **atomic argument** is one of:

```
TYPE(A|B|C)
NUM(canonical decimal n)
QREF(canonical decimal i)
RREF(canonical decimal i)
MIXED(NUM(w), NUM(p), NUM(d))
```

These are grammatical atoms, not independently assigned numerical values.
Their internal component spellings are, respectively:
`type`, `NUM digits(n)`, `QREF digits(i)`, `RREF digits(i)`, and
`MIXED NUM digits(w) NUM digits(p) NUM digits(d)`.
Digit strings are canonical and mixed fractions obey S0's proper-part rule.

For every other constructor `C(a1,...,ak)`, produce exactly one **core**:

```
head(C) slot(a1) ... slot(ak)
slot(a) := component_spelling(a), if a is atomic
         | HOLE, otherwise
```

`head(SETQ(i,...))` and `head(SETR(i,...))` include the shared decimal index
after SETQ/SETR; it is not a separately named register word. After emitting
the core, recursively emit every non-atomic child in argument order. Each HOLE
therefore owns exactly one subsequent typed subtree. Its type and arity follow
from the owning S0 constructor. No child may be skipped, borrowed from another
hole, repeated without a reference, or appended after all holes are filled.
This is a finite recursive grammar; recursion remains under S0's fixed depth.

Treat the header as `GRADES(A,NUM(a),B,NUM(b),C,NUM(c))`, `TARGET(NUM(t))`,
`TOTAL(NUM(m))`, followed by FIRST or ALTERNATIVELY and the corresponding
statement trees. These use the same core production. A branch has its complete
last YIELD; the complete account boundary is inherited from S0. There is no
invented extra END command and no reset at each physical line wrap.

Each complete written group is then:

```
h(ENTRY[e]) h(core_atom_1) ... h(core_atom_k) h(AGREE[type,mixed])
```

The context functions are fixed, not learned from target occurrences:

- `e=0` for the first group of the account or the first group after FIRST or
  ALTERNATIVELY; `e=1` otherwise. There are exactly two entry markers.
- `type=Q` for ADD/SUB/MUL/DIV/MASS/FINE/GRADE; `type=R` for
  PORTION/MIX/SCALE/REPEAT_FILL; `type=S` for statements and header/branch heads.
- `mixed=1` exactly when that core absorbs a MIXED atomic argument; otherwise
  `mixed=0`. It is a written-constructor condition, not an inferred fractional
  value elsewhere in the program. There are exactly six agreement markers.

The whole group thus depends on its operator and absorbed argument shape, plus
one fixed entry condition. This supplies a bounded possible interaction and
context effect; it is not a claim that the known whole-form residuals are now
explained. No whole-form dictionary or post-target exception is available.

The alphabet of components is exactly R0's 38 listed atoms plus HOLE, ENTRY0,
ENTRY1, AGREE_Q0, AGREE_Q1, AGREE_R0, AGREE_R1, AGREE_S0 and AGREE_S1: **47 atoms**.
Choose one injective prefix-free map `h` from these atoms to nonempty lowercase
letter strings of length 1–8, shared across every account. This preserves R0's
finite alphabet/code-length bounds and changes no literal sign into a claimed
historical letter. There is exactly one ordinary space between complete groups;
none inside a group. A layout line break may replace a separating space while
remaining a recorded boundary, and has no semantic or allomorphic state effect.
No other whitespace deletion or insertion is licensed.

This is a finite code family with finite bounded source programs, although its
Cartesian search space is large. It is not an unrestricted state machine and
no tractable decoder/search capacity is claimed. No particular h is fitted or
artificial Voynich-like ciphertext generated here.

## Concrete different written consequences

For the same S0 expression `PORTION(A,NUM(2))`, R0 emits three groups:

```
[PORTION] [A] [NUM 2]
```

R1 emits one complete group:

```
[ENTRY[e] PORTION A NUM 2 AGREE_R0]
```

Square brackets and the spaces inside them are display notation for components;
the actual R1 group contains no interior spaces. `SCALE(NUM(2),RREF(0))` similarly
changes R0's three groups to one R1 group containing SCALE, NUM/2 and RREF/0.
For `MIX(PORTION(A,NUM(2)),PORTION(B,NUM(5)))`, R1 emits one MIX/HOLE/HOLE core
followed by the two complete PORTION groups. The holes preserve the nested
argument relation; they do not become separately chosen meanings.

The same `SETR 0 HOLE` core immediately after a branch marker versus after an
earlier used SETQ definition has different mandatory ENTRY codes under R1.
PORTION itself is always nested below a statement in S0 and therefore cannot
be the first group after a branch marker; no impossible PORTION context is
claimed as a contrast. An integral argument and
a literal MIXED argument also force different agreement endings. R0 has neither
requirement. These are actual shared-surface consequences, not synonyms for
arithmetic roles. They are conditional on a complete parse; no boundary or
context ownership has yet been found in target material.

## Complete examples, verification and meaning limits

The raw proposal contains the complete R1 component-group streams for S0's two
historical total-20 alternatives, the independently generated `(4,4,12)` account,
and the combined three-branch account. The exact source-only encoder is
[alloy_r1_source_encoder.py](alloy_r1_source_encoder.py). It reads only the owned
S0 JSON/examples and evaluator, emits abstract component groups, and evaluates
the same accounts. It neither reads unknown text nor searches a key or parse.
Model-generated group counts describe these examples only; they are not target
length choices or requirements on another legal program.

For the existing two-source account, R0 emits 106 groups and R1 emits 42. The
existing generated account gives 33 versus 13, and the combined account gives
128 versus 52. These are conditional differences for the **same specified
semantic trees**, not proof that the two entire variable-program languages are
disjoint. No target paragraph was chosen from any of these counts.

One further account is newly generated here, without changing S0 or R1: grades
4,6,10, target grade8, total mass12. It mixes 2A with 3B, explicitly checks the
intermediate grade `5+1/5`, adds 7C, states weights `(2,3,7)` and fine content96,
then yields. It is a complete six-statement account with different header and
quantity values, not new historical source text. The same components and
context functions encode it; no special surface rule is introduced.

The first source-derived branch yields `(5/2,25/4,45/4)`, the second `(2,7,11)`;
both have mass20 and fine content100. The new account yields `(4,4,12)` with
the same mass and fine content. All remain recipe definitions, not one physical
batch passing through all alternatives. S0's source scope excludes the Latin
introduction, table layout, citations and repeated exposition as documented in
the original card; R1 does not turn that subset into a full Latin translation.

Three distinct checks must stay separate. A legal tree satisfies syntax and
reference types. A valid S0 account also satisfies its **written** numerical
assertions and independently declared header. A supported target reading would
add a globally shared surface realization and an independently bound consequence.
For example, assigning the new 12-unit portion to A yields `(16,4,0)` with mass20
but fine content64, so it cannot satisfy the unchanged target grade5. It remains
a well-typed legal recipe before that arithmetic check. Rejecting it shows what
the semantic interpreter checks, not that an unknown group means “portion.”

Likewise correct agreement markers or prefix parsing supply no numerical truth.
If header values and every quantity were freely assigned per whole word, the
GDT971 free-label rival could remain satisfiable. Shared decimal pieces and
fixed arithmetic are therefore substantive assumptions. Grade/constituent
identification, units, physical manufacturing direction, and the target owner
remain unbound. Second-branch closure alone is not claimed to fix these.

No target necessity screen, model selection, morphology fit or decoder follows
from retaining R1. If a later test fails only its mandatory marker/group shape,
that excludes this writing rule before semantic recovery; it does not reject
all mixture content. No automatic R2 marker deletion, new code-length bound,
context expansion or source-count repair is authorized by this raw proposal.
