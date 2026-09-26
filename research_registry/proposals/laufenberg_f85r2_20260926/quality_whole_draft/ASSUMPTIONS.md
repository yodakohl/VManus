# A complete, freely authored ZL hypothesis: scope and cost

Status: COMPLETE_ZL_A_DRAFT / B_ARGUMENT_GAPS / NO_SEMANTIC_FIT_CLAIM.
This is an exploratory interlinear hypothesis, not a translation, experiment,
source identification, or preference for one real Voynich meaning. Confirmed
translated words remain zero. No dictionary or earlier family is changed.

## Decision note and budget

The unknown is whether one complete, stable, explicitly costed reading can be
written around the two fixed quality bases without deleting the remaining
material, and whether its fixed syntax supplies the correction rival's required
arguments. A complete A reading would permit a consistency audit; a failed A
would stop this scaffold. A complete B would permit a genuine two-reading
comparison; an incomplete B leaves that comparison unperformed. Neither
outcome identifies a word. The smallest adequate work is hand authoring,
occurrence accounting and a fixed rival audit. Budget: 35 minutes including
input reading, authoring, checking, hash receipt and handoff. No decoder,
automatic candidate search, corpus extension, new GDT or target access.

## Inputs and what they license

- The owned GDT1042 `native_groups.tsv` is the only target input. This packet
  uses N.2–6, E.7–11, S.12–17 and W.18–23. It assigns all 108 ZL native groups
  and all 85 exact raw types. Its 73 hapax types expose very large freedom.
- `ideas/07_quality_complement_constructor.json` fixes dar=HOT, daiin=MOIST,
  and qo=NOT on exactly those two bases; qodar and qodaiin are derived.
- `READING_SELECTION_REVIEW.json` supplies the retained underbinding and the
  correction rival. Choosing ZL is openly motivated by literal presence of
  both anchor spellings. It is not an independent selection or validation set.
- `SOURCE_CLAUSE_BRIDGE.md` supports the physician/four-complexion setting in
  the external Karlsruhe witness. `PRINT_ELEMENT_PASSAGE_ROOT.md` supplies
  the complete printed argument: mixed four-element composition, different
  predominance, contrary qualities, and constitution-sensitive regimen. Its
  body/element correspondences are source propositions, not Voynich bindings.
- The former spring/water-flowering account is not used. The doctor does not
  identify a season; the four target blocks are not four identified figures,
  seasons, patients, humours, or a proved ordering of any such categories.
- GDT884's exact fixed-introduction STA morphism remains excluded. This is
  neither that source text nor that encoder. GDT812's scalar daiin family and
  GDT624's historical quality reader remain separate incompatible C0 families.
  Their exploratory values provide no inherited lexical confirmations here.

The result is deliberately less specific than an alleged source paraphrase.
It invents a short medical discourse including air, water, fire and earth, but
its exact clauses are not extracted from, aligned to, or attested by that
source. The N/E/S/W element choices are four fitted noun bindings, not
identified diagram owners or inherited source-to-target alignments. Some detailed clauses could be historically wrong. Medical fluency
and completeness alone cannot establish their truth or historical accuracy.

## Fixed meaning and reference policy

All occurrences of a whole raw form have exactly one typed value. A printed
uncertainty (`chok{co}m`, `chz[s:r]`, `ckhed[a:y]`, `qose?y`) remains part of its
opaque raw spelling. Binding that exact marked object is an explicit guess;
it neither resolves the mark nor equates it with another edition's spelling.

Nouns denote generic kinds, not silently supplied individuals. BODY denotes
the same BODY kind wherever aiin occurs; FLESH and DIET likewise retain their
kind identity. There is no reset to a different patient, season, world, or time
at a block boundary. Generic predication does not assert that every historical
individual always has the quality. English articles merely render nominal
syntax; they add no identifiable person. All static predicates use the one
explicit evaluation index T. A process word can introduce its own start/end
relation by its declared lexical meaning; none moves a qo quality claim to
another time to save a contradiction.

HOT(x,T) means predominant heat quality of the written owner x at T; MOIST(x,T)
means predominant moisture quality of x at T. Neither means CONTAINS_FIRE or
CONTAINS_WATER. NOT_HOT does not entail COLD, and NOT_MOIST does not entail DRY.
The quality threshold and the decision to treat these as unary predicates are
free trial assumptions. Actual moisture/heat may be present below the named
predominance threshold. The source's contrary components therefore do not
create a same-predicate contradiction automatically.

PART_OF, assigned to or, is a recursive entity constructor: PART_OF(x) denotes
a proper constituent or portion of x. It is the same operation for body,
blood, food and diet. Two consecutive or tokens apply it twice. This models
`or or aiin` as PART_OF(PART_OF(BODY)), with no deletion, repetition repair or
special gloss for either or. This is a particularly unconstrained invention,
not evidence of the manuscript's actual word building. oraiin is independently
SOFT; it is not parsed as or+aiin. That inconvenient whole-form exception is
retained, not concealed.

WITH is one accompaniment relation, ACCOMPANIES(x,y,T), across entities and
explicitly written clause events. It is not changed into an instrument verb
at W.23. There it means the sustaining is accompanied by broth and wine; it
does not itself assert that those substances cause the sustaining. WARMS
requires a written agent and patient and means increasing the patient's heat,
not necessarily making it HOT. FEELS introduces an explicitly perceived
property; the N moisture predicate is inside that sensory operator.

## Complete assumption count

- 2 seeded whole-form values: dar and daiin; 1 seeded constructor qo on their
  two-base domain; 2 derived whole types, qodar and qodaiin (3 occurrences).
- **81 additional whole-form bindings**, each listed once in LEXICON.json.
  A repeated English gloss still costs another binding when its raw form is
  different. No value is inherited as known. The 16 other qo-initial types
  (17 occurrences) are independent wholes, NOT applications of qo. Thus this
  packet offers zero evidence of general qo productivity. qodain=GENTLE is
  expressly not an alias of qodaiin=NOT_MOIST.
- **15 finite construction rules** below. Some are broad, and one alternate
  verb order is needed by only one authored clause. Every parse choice and
  clause boundary in ALL_OCCURRENCES.json is another fitted choice; syntax
  is neither learned nor independently justified. The exact number of clauses
  and rule applications is included in that artifact's accounting.
- There is 1 kind-reference policy, 1 static-state policy, 1 typed quality
  interpretation, 1 two-base constructor-domain restriction and 1 fixed
  attachment/parse selection per listed clause. These are not free evidence.
- All source-topic labels are only plausibility categories. LEXICON.json
  distinguishes source-topic attestation from free semantic invention. Even
  topic-attested words have **zero** target lexical bindings from the source.
- Synonym freedoms are exposed: chol/ar/olchey all coordinate; sheo/chotey
  both FEELS; shedaiin/ckhed[a:y] both NEEDS. These are separate fitted entries,
  not a claimed inflection or allographic relation.

## The finite clause grammar

G01. A noun introduces its named kind as an explicit NP; no implicit patient.
G02. A property before an NP modifies that NP; nested PART_OF NPs are allowed.
G03. An NP followed by a unary verb asserts that verb's proposition. An NP
     followed by one or more properties asserts their conjunction about that
     NP, with a zero copula. A postposed property can instead restrict a subject
     NP only when the frozen parse explicitly assigns that scope.
G04. `or NP` constructs PART_OF(NP); recursion is allowed, with no depth repair.
G05. A written coordinator conjoins two constituents of the same semantic type.
G06. NP V NP is a binary subject–verb–object clause.
G07. NP NP V is the explicitly allowed alternate subject–object–verb clause.
     The sole use is W.19. No argument reversal follows from this choice.
G08. NP FEELS property-expression asserts that the NP presents that sensation;
     the property-expression can contain written coordination.
G09. NP MAKES NP property-expression is a causative result construction.
G10. An adverb modifies its explicitly listed clause. Its frozen attachment
     does not jump to another subject or furnish an unexpressed participant.
G11. CL BECAUSE CL is the causal connection written in E.7.
G12. WITH NP is an accompaniment adjunct of the listed preceding NP or clause.
G13. Adjacent complete clauses form an asyndetic sequence; physical lines are
     not assumed to be sentence boundaries. Every actual cut is frozen.
G14. NP SHOULD property-expression is a normative clause; SHOULD is written
     as olkar. It does not turn other clauses into unexpressed prescriptions.
G15. THEREFORE CL links the last explicitly listed E assertions to that clause.

This is an explicit grammar inventory, not a claim of a small explanatory
code. It uses 81 new lexical choices plus much syntactic freedom for only
108 observations. No token is a sentence-sized English macro, but the numerous
new atomic meanings can still manufacture plausible prose. That is precisely
why complete coverage is not a fit statistic.

## Fixed rival and concrete discriminator

A = qo(P)(x,T) := NOT(P(x,T)). B keeps both base values and every other lexical
entry and parse fixed, but qo(P) := INTENDED_CORRECTION_OF(P). B requires a
written treatment/action a and a written patient x. Its own qo hypothesis
supplies intended rather than achieved status; this is an unconfirmed lexical
assumption, not a demand for an extra unprovided intention word. Its target
proposition would be INTENDS(a, REDUCE(P,x)) without claiming that P is already
absent. Merely naming a doctor or diet in an external source cannot fill the
action/patient slots.

In this authored parse the A owners are URINE at E.10, FLESH at S.16 and DIET
at W.21. HOT is owned by HEART at S.15; MOIST is perceived of SKIN at N.4 and
modifies NOURISHMENT at E.9. These are different written noun kinds; no actual
P/NOT(P) same-owner pair has been created. No negation contradiction is found,
but the proposed truth-condition discriminator is **not instantiated**.

The frozen B display replaces only three qo occurrences. It cannot form a
fully bound correction proposition at any of them: E.10 and S.16 supply neither
a treatment action nor a written patient-of-treatment relation; W.21 supplies
DIET, but no written patient. Even allowing DIET to stand for its implementation
as a regimen action would leave that patient unfilled. The written qo itself
supplies intention under B, and no extra intention marker is demanded.
Reinterpreting FLESH/URINE as a remedy, inventing a generic patient, changing a
nearby word into PRESCRIBE, or silently converting a property to an event would
be a new packet. No such repair is made. B's argument gap is a failure of this
**author-selected scaffold**, not a target-derived preference for A.

A real discriminator would need the same overt x,T with P(x,T) and a qo(P)
clause, plus an independently fixed action/patient/status construction where
appropriate. A would then clash if both stative assertions hold, whereas B
could express intended correction without achieved absence. Nothing in this
packet provides that independent binding; no experimental test is ready.

## Stop and evidence ceiling

Do not train a decoder, query another page, use reserves, contact anyone,
collapse alternate readings, extend qo to the remaining wholes, or publish a
semantic preference on the strength of this draft. A consistency reviewer can
check conservation, repeated values and frozen argument ownership, while also
rejecting the invented grammar or the generic-kinds policy. A failure of those
checks is a draft failure, never grounds to rewrite the seed after the fact.
The correct continuation is an independent audit and explicit underbinding
assessment. The old closed-source equation and the old scalar family stay put.
