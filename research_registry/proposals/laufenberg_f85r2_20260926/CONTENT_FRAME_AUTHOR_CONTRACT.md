# ContentFrame writer: first interface contract

27 September 2026. Started 03:58:55 UTC; first-contract ceiling 04:08:55 UTC.
Root's overall trial ceiling is 04:50 UTC, including review/publication.
This file freezes interfaces and the small compositional family before any
whole-page draft. It neither claims a complete reading nor licenses repairing
the contract after the first review. Root review is required before authoring.

Read current route, composition topic, `CONTENT_FRAME_ROOT_DECISION.md`, the
complete owned III.13 and the frozen source intakes. Root's predecessor review
is the selection basis; this stage does not rerun old composition tests.
Only the owned1042 projection was inspected, in its entirety. No other target,
source, image, reserve, contact, executor, registry/state or Git action.

## Decision, target and source before the remaining vocabulary

Try the constrained family below. It is not already impossible at the level
of its declared types, but its actual page capacity and complete source
ownership remain unknown. The field constructors, binders and references
must be realized in the later reading; naming their types here is not coverage.
If their actual arguments cannot be written in the fixed order, retain that
gap rather than replace the mechanism with independent whole-word glosses.

The full target is all156 ZL3b groups, native numeric locus order .1 through
.24, then numeric group order within each locus. The annuli are included.
This traversal is an exploratory ordering choice, not a manuscript fact.
All157 IT2a and160 RF1b groups remain literal alternate-reading obligations;
they are the same page, not three independent observations. Every raw group
will retain its spelling and boundary. No alias normalization or canonical
reader fallback is licensed.

Source: the complete III.13 P15–22 account, printed307–313, including **every**
obligation in the frozen `GALEN_CONTENT_FRAME_INTAKE_A.md`. The target aim is
complete selected-unit content, not merely three transport sentences.
Any unachieved claim will be listed as an omission and will prevent a claim
of complete source coverage. The source is the1916 translation, not medieval
identification or clinical truth. Whole-chapter qualifications remain in
force, without silently adding the rest of the chapter to this selected unit.

## Fixed meanings, cuts and whole-form obligations

| Form/component | Fixed new hypothetical denotation | Type |
|---|---|---|
|ar|STOMACH|Organ|
|aiin|LIVER|Organ|
|ain|SPLEEN|Organ|
|d|Build an organ-owned contents frame builder, D below.|Organ → FrameBuilder|
|qo|Lift that builder to a supply specification constructor, Q below.|FrameBuilder → SupplyBuilder|
|dar|D(STOMACH)|FrameBuilder|
|daiin|D(LIVER)|FrameBuilder|
|qodar|Q(D(STOMACH))|SupplyBuilder|
|qodaiin|Q(D(LIVER))|SupplyBuilder|
|qodain|Q(D(SPLEEN))|SupplyBuilder|

Exactly five observed compound analyses are licensed: d+ar, d+aiin,
qo+(d+ar), qo+(d+aiin), qo+(d+ain). The inner d+ain computation in qodain does
not require an independently occurring dain token. It does require the same
D law. No additional cut, ot deletion, prefix reinterpretation, or inherited
568/565/572 value is admitted. Forms merely containing these strings remain
unassigned whole forms, unless they are one of the five listed compounds.

The mapping is chosen here as a new hypothesis, partly for the visible
distribution of the family, not derived from the source or independently
confirmed. Repeated qodaiin must retain LIVER; qodain must retain SPLEEN.
No owner may be recovered by inverting an arbitrary predicate.

| Reader | ar | aiin | ain | dar | daiin | qodar | qodaiin | qodain | Total assigned occurrences |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
|ZL3b|4|6|2|2|3|1|2|1|21|
|IT2a|6|5|2|2|3|1|1|2|22|
|RF1b|6|5|2|2|3|0|2|0|20|

There are115 ZL whole types, of which8 are fixed here;107 remain unassigned.
IT has115 types and RF123. Alternate-only types are additional obligations,
not automatic spellings of these values. For example, IT .16 has qodain where
ZL/RF have qodaiin, while RF marked forms at .10/.19 do not literally instantiate
qodar/qodain. IT/RF also have extra bare ar and a final ar ar sequence. These
are retained future consequences; the contract does not silently repair them.

## Denotation types: records are not propositions or binders

**Organ** is an anatomical participant value. STOMACH, LIVER and SPLEEN are
distinct. Other source participants would need explicitly counted bindings.

**Case** is a value with explicit identity. A named or bound case is not a
time, phase, guard or modal operator by itself. Statements linking cases to
one nutritional scenario, ordering them, or making one a feeding/fasting
alternative must be written. Distinct case mentions do not unify by proximity.

**Material** is an individual or explicitly generic portion variable. A
**MaterialDescription** is a predicate taking a Material and Case. All its
other arguments must be closed constants or explicitly bound references.
It is not a proposition, an organism, a source location or an arbitrary
English summary of an entire source sentence. Primitive descriptions and
their relational payload are counted separately in the later lexicon.

**CompartmentSpec** is an owner-relative description. The trial permits known
gastric contents/cavity, venous cavity, and organ body, plus an explicitly
written UNKNOWN specification. BODY and VEIN_CAVITY are not declared disjoint:
the source's liver body includes its vessels. Phase/appropriation must make
the relevant material distinction. UNKNOWN does not invent a cavity or
assert containment; it leaves the source at organ-level precision.

**PhaseSpec** is either UNKNOWN or KNOWN(phase description). Presentation,
adhesion and assimilation are distinct phase values. Digestion, availability,
satiety and transfer are not silently identified with them. A disjunction of
phases requires a written disjunction. Phase qualifies this frame's material
relative to its owner, not necessarily every material in that organ.

**FrameArgs** is the four-field product
`(case:Case, compartment:CompartmentSpec, phase:PhaseSpec,
material:MaterialDescription)`. Each field must have a written expression
or a reference to an explicitly introduced value. No defaults, nearest-noun
recovery or blank field counts as an instantiated argument. UNKNOWN is an
explicit information value, not an author's unfilled slot.

**ContentFrame** is the product
`(owner:Organ, args:FrameArgs)`. It describes potential contents and does not
assert existence, transfer, benefit, appropriation or successful nutrition.

**FrameBuilder** is a constructor record with an Organ owner and one defined
operation on FrameArgs. **SupplyBuilder** is a function from FrameArgs to
**SupplySpec**. A SupplySpec is a record containing exactly one ContentFrame;
it is not itself a frame, a material, an event, a predicate or an assertion.

**SourceSite** is a precision-tagged value. For a known compartment it is that
owned compartment. For UNKNOWN it is the supplying organ with compartment
unspecified. In particular, liver is not identical to its vein cavity.

**Prop** is a proposition/formula. **Guard** is an explicitly assembled Prop
used as an antecedent; it is not a case identifier or a hidden bundle of source
conditions. **Mode** has ASSERTED and POSSIBLE values, each needing a written
value or an explicitly scoped reference. NEGATION is a logical construction,
not a third owner, phase, guard or gloss of qo.

## Fixed D and Q; exact order of application

For Organ o and FrameArgs a:

`D(o) = FrameBuilder(owner=o, build(a)=ContentFrame(o,a))`.

`Q(B) = SupplyBuilder(a ↦ SupplySpec(frame=B.build(a)))`.

The three operations, with their distinct result types, are:

1. `Build(B,a) : ContentFrame`.
2. `SupplyBuild(Q(B),a) : SupplySpec`.
3. `SupplyApply(s:SupplySpec,r:Organ,x:Material) : Prop`.

The third denotes withdrawal/supply of x from `SourceSite(s.frame)` to r in
`CaseOf(s.frame)`. It does not mean production, ultimate origin, residual
origin, or transfer of every material in the frame. Its source organ is
`OwnerOf(s.frame)` and its exact source precision is the stored compartment.
No recipient, witness, mode or guard is obtained from that owner field.

The intended lexical head order is prefix application: a bare d compound
consumes one complete following FrameArgs expression to yield a ContentFrame;
a qo compound consumes one complete following FrameArgs expression to yield
a SupplySpec. SupplyApply then combines that specification with separately
written recipient and material expressions, in that order. A complete
argument may be a previously introduced explicit reference. It may not be an
arbitrarily earlier expression, an omitted phrase or an entire source clause
declared an atomic argument after failure.

The whole writer must give a finite grammar for any packaging/reference syntax
used to express these arguments. It cannot change the above arities, order or
types. There is no direct FrameBuilder→SupplySpec cast, Organ→Frame cast,
Description→Frame cast, or Frame→Prop cast. A SupplySpec is applied only by
the declared SupplyApply production; it is not silently a curried function.

The five structural projections have fixed types:

* `OwnerOf : ContentFrame → Organ`.
* `CaseOf : ContentFrame → Case`.
* `SiteOf : ContentFrame → SourceSite`.
* `PhaseOf : ContentFrame → PhaseSpec`.
* `DescriptionOf : ContentFrame → MaterialDescription`.

In addition `FrameOf : SupplySpec → ContentFrame` projects its actual stored
frame. SourceSite above abbreviates SiteOf, not an extra operation. Each
projection used in the reading requires a written construction or an explicit
typed production containing that projection, with its cost recorded. Merely
listing it here does not supply its target occurrence.

Reusing the same FrameArgs reference a with D(o) and Q(D(o)) builds the same
immutable frame value by the displayed definitions. This is a product-value
identity, not automatic identity of material witnesses or transfer events.
Two separately introduced arguments are not made identical merely because
the author narrates them similarly. Different owner arguments produce
different frames, even with the same FrameArgs.

## Witnesses, binder syntax, references and scope

The frame membership predicate is defined, not freely re-glossed:

`Fits(F,x) = DescriptionOf(F)(x,CaseOf(F)) AND
  SpecifiedLocation(x,OwnerOf(F),F.args.compartment,CaseOf(F)) AND
  SpecifiedPhase(x,OwnerOf(F),F.args.phase,CaseOf(F))`.

For an explicitly UNKNOWN location/phase, the corresponding conjunct supplies
no positive location/phase assertion. Known specifications retain their stated
constraints. The owner remains a stored value even when either field is
UNKNOWN. Availability is a separate material/guard assertion, not a consequence
of the UNKNOWN tag or of being somewhere in a vein.

Binder syntax has its own sort, **BinderSyntax<T>**; it is not a T value.
A declaration introduces a variable in a specified syntactic scope. A
**Ref<T>** is a written reference resolving in that scope to a T-valued term.
Resolving a ref does not copy a binder, introduce a new witness, or infer an
unwritten equality. Binding and lookup both require uniform written productions.

For material witnesses the permitted generic logical interfaces are:

* `SomeIn(F,binder,body)` denotes `∃x (Fits(F,x) AND body(x))`.
* `AllIn(F,binder,body)` denotes `∀x (Fits(F,x) → body(x))`.

In each, body has an explicit bound Material parameter and finite written
scope. `SupplyApply(s,r,x)` requires Fits(FrameOf(s),x) to be available in that
scope: for example from such a binder using the same frame value. It cannot
accept a description in place of x or an unintroduced individual. The positive
and negative cases may therefore respectively use SomeIn and AllIn; neither
is inferred merely from the prefix. A body-withdrawal exclusion must actually
negate SupplyApply under the appropriate material restriction, not negate the
existence of liver material or declare it unsuitable for the recipient.

Generic binders for Case/Organ likewise need written quantification and domain
restrictions. No unbound generic organ or universal recipient is inserted to
fill a required role. No direct capture of an unrelated preceding binder is
licensed by the word "same."

Guard/modal wrapping is explicit: `Under(g,Assert(P))` has content `g → P`;
`Under(g,Possible(P))` has content `g → ◇P`. A true/no-extra-condition guard,
if used, still needs a written value or an already established guard scope.
For possible supply the material existential must be **inside** Possible;
it is not an actual portion inferred from a possible event. An explicitly
introduced outer guard/mode scope may govern several clauses, but its exact
span and references must be written and counted. Every SupplyApply must be
inside such a guard/mode scope, including assertions in the imagined period
model. Neither a line number nor an author's English explanation supplies it.

A reference to a witness bound inside a conditional or possible scope remains
inside that scope. It cannot yield an unconditional actual witness outside.
Later claims must reuse that binder/reference in its continuing written scope,
or state a new quantified relation. In particular, projection from a source
frame is not extraction of a real material individual from a possible supply.

## Required concrete uses and later consequences

The full writer must own all of the following, in addition to the complete
source inventory:

1. Build and use CONTENT frames for at least two distinct organ arguments,
   including actual bare D(STOMACH) and D(LIVER) applications. Give every dar
   and daiin occurrence its same constructor type. A frame name without its
   four arguments is incomplete.
2. Use the same Q law with STOMACH and LIVER suppliers in complete written
   supply assertions: some gastric supply to liver and guarded liver-vein
   supply to stomach. Q(D(SPLEEN)) must retain its third owner and receive
   an actual application accounting for the qualified spleen possibility.
   Both qodaiin occurrences remain LIVER applications, not free synonyms.
3. State the same-LIVER contrast: available venous-cavity supply versus no
   withdrawal of the already appropriated body material in the stated case.
   This requires written availability/phase, guard and negation. The frame
   constructor alone does not assert the physiological exclusion.
4. State a later phase consequence for both STOMACH and LIVER using an owner
   projected from their actual prior frames, and an explicitly retained
   material witness within the corresponding generic/conditional scope.
   The later Case and phase must be written, with the source's case ordering
   or common-scenario relation. No new phase follows automatically from
   supply, and no source frame is mutated in place.
5. Preserve the source's separate stomach purpose denial, timing, staged
   distribution, intestines/periphery, splenic processing and possible
   destinations, common-stock analogy, and return-path conclusion. These
   obligations are not all entailed by the four preceding demonstrations.

UNKNOWN may preserve the source's unspecified spleen compartment/phase. It
may not stand for an omitted argument expression. A description of material
worked up in spleen must not identify that organ as its ultimate origin or
erase the preceding liver-related supply. Opposite directions do not identify
the same physical portion or simultaneous transfers.

## Frozen cost baseline, residual freedom and rivals

The fixed lexical choice is three organ constants plus two productive
constructors: five semantic entries and five exact compound analyses.
Eight observed whole forms consequently have fixed meanings/types. The
organ bijection is an exploratory choice, not a successful decipherment.
FrameArgs, ContentFrame and SupplySpec introduce three product structures;
known/unknown compartment and phase distinctions introduce information-state
choices. These are additional representational costs, not free evidence.

The interface library explicitly adds Build, SupplyBuild, SupplyApply, six
record projections, Fits, SomeIn, AllIn, binding/reference resolution, guard
wrapping, mode wrapping and ordinary logical negation/conjunction. These are
specified operations rather than claimed target productions. The later
grammar must enumerate each realized production and each application, and
must count further packaging, case-linking, phase, material and lexical
choices. No savings is claimed by this list alone. All107 remaining ZL
whole-type meanings, any reader-only meanings, clause boundaries and source
departures will be counted. A lexical item hiding a whole conditional source
argument is prohibited; relational payload must be itemized.

The strongest rival is generic FROM with separately written owner-compartment,
phase, case, material, guard and recipient relations. It may express identical
content without stored frames. Another rival has a supplier constant within
each explicitly named case and therefore ignores the nominal owner input.
Separate names plus ordinary shared references also remain live. Reusing two
owners in this selected material is not a controlled independent experiment.
The author must show actual written sharing and what it saves or constrains;
neither unchanged coverage nor record notation alone discriminates these
rivals. No old named/constant-D failure is silently inherited as a new result.

Stop with an exact partial if the full source or required dependencies cannot
be realized under this contract. Missing arguments, alternate-reader gaps,
type contradictions and inadequate source entailment are different outcomes.
No automatic contract repair, extra cut, new corpus query or executor follows.

## Input receipts

Owned target: `experiments/yolo/gdt1042_f85r2_source_program_surface_census/artifacts/native_groups.tsv`,
473 rows, SHA256
`e50307f834b04ff2ce17a97f14fd2c7b3f24b4818bc7fda3f57c372afc6b9d3c`.
Counts and literal family census were obtained only from this safe projection.

Owned cache: `external_cache/galen3_frame_source.html`,102400 bytes, SHA256
`1d0f8547ae087a7c97d36f7600cee05dbb1b3321beb973b3065bba2ea8b0ad24`.
Selected source P15–22, byte interval[75314,81908),6594 bytes, SHA256
`2dd0e03d49716cad9d5c4028801c253e3d3e0d6c427fb3ed97197e0c935dcd96`.
Frozen intake SHA256
`63e616348f2195615076172ad5207badcdb5fc47068bb0028aed33f5d85061cd`.
Frozen origin critique SHA256
`285d95ae1a2b173bb716c407d1e0f8ef144cf33aee0fc453880545bde814ad0f`.
All prior packets and input bytes remain unchanged. Zero confirmed words;
no target or source acquisition beyond the existing owned inputs.
