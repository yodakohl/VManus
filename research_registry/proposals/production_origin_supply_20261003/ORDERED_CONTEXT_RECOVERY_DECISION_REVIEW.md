# Ordered context recovery: a distinct question, not yet a useful next fit

3 October 2026. Bounded independent decision review. Read current route,
controls topic, bounded ideas search and route-check, then original reports
1159,1160,340,341,343,344 and176; also 1159/341 methods and176's actual source
unit extractor. No target data, source reacquisition, model fit, or annotation
changes. No GDT1162 annotation packet or result was used.

**Recommendation: do not launch another source ordered-context learner now.**
Joint recovery of operation and ingredient identities from unlabeled ordered
text is a real unanswered question. But the available proposed experiment
does not yet distinguish an actual Voynich reading choice. This is not a
logical prohibition on unsupervised recovery and not a claim that neural
methods or all ordered relations have failed.

## What the previous experiments actually settle

| Primary | Result relevant here | What it does not settle |
|---|---|---|
|1159|Unknown ingredient forms, supplied ingredient spans, four candidate concepts plus OTHER; exact co-occurrence assignment fails all continuation gates. Named recovery9.48% versus4.96%; whole-search rank.145.|Joint lexical recovery from unlabelled full text and directed predicate/argument relationships was not tested.|
|1160|Raw neighboring source groups improve ranking of *known candidate expansions*: C76.155%, N79.651%, baseline68.857%.|It neither induces the candidate senses nor learns an unknown writing channel or ingredient/event ontology.|
|341|Ordered anonymous recipe topology gives worse retrieval than unordered topology: selected ordered MRR.4682 versus.4960; no calibration.|Lexical values were not jointly inferred; equality-edge topology is not an interpreted material transformation.|
|343|Given normalized global concept identity helps retrieval; additional identity flow does not: MRR.8736 versus.8755.|It does not recover unknown identity. Supplying identity is precisely the advantage unavailable to an unknown-word task.|
|344|Anonymous event-path comparator changes held loss by−1.842bits, positive2/6; neither comparator nor formal path gates pass.|No general exclusion of causal or procedural semantics follows.|
|176|Position/span-length predicts coarse instruction/argument/closer likeness; tools collapse with ingredients.|Its OPERATION class is a whole instruction span, not a normalized action such as MIX, POUR or HEAT.|

That last distinction is an implementation-level fact:176 maps XML
`instruction` to OPERATION and takes a first direct word as its opaque
identity. Commodity identifiers are available for ingredients/tools. Reading
that output as a gold operation lexicon would fabricate the essential input.
Instruction containment is also editorial segmentation, not an author-visible
predicate boundary transferable for free to Voynich.

## Genuinely different mechanism: material lineage, not order alone

The useful extra constraint would be a **shared state transition**. In a
preserving operation, a material participant before and after the operation
has the same reference. In a combining operation, two inputs become one
mixture which later instructions consume; repeated mentions of an input do
not automatically name that mixture. Order, ingredient incidence and record
length can be identical while these two graphs disagree.

A concrete semantic contrast is therefore:

    preserve(A, location1, location2) -> later consumer(A)
    combine(A, B) -> C; later consumer(C)

Here A/B/C are anonymous referents, not ingredient names. A later consumer
written under a fixed reference rule can distinguish the accounts without
already knowing the lexical root for a substance. Recovering both the
operation class and entity reference is necessary; giving either through
held XML labels defeats the proposed task. Merely fitting directed bigrams
or preferring a generic “take–prepare–apply” order does not express this law.

This differs from1159's unordered co-occurrence and from341/343's fixed flow
features. Nevertheless, noncommutativity must be physically/semantically
constrained: latent state labels attached to sequence positions can fit any
order and remain just another unconstrained codebook.

## Smallest adequate source task, if a reading decision selects it

Use the existing CoReMA collections, whole held collection, original complete
recipe bodies and all raw words. Keep editorial ingredient identities and
operation/reference annotations solely as training supervision or held gold,
never as held inputs. If the chosen mechanism requires normalized operations
or entity-result links,176's existing coarse labels do not supply them; they
would need an explicit small source annotation packet from the already
available full text, not another corpus acquisition.

The narrowest honest endpoint would be **joint unknown identities plus
preserved-versus-produced referent**, scored on every predeclared held
occurrence, including unsupported concepts and ambiguous expressions. Supply
only raw sequence, document boundaries and within-document literal equality
on the held side. Do not provide gold ingredient spans, clause roles,
operation locations, or “the noun after this verb” features. Source-side
candidate concepts can come from training, but held selection must not choose
only words known to have supported gold labels. Alias and OTHER alternatives
must remain. A same-capacity unordered model and an ordered lexical model
without state transitions are necessary comparators; otherwise ordinary
frequency or adjacency can explain a gain.

Even this is a supervised-source-to-unknown-lexicon calibration, not a model
of the unknown Voynich channel. It needs complete-search controls preserving
the simpler marginals/order features and withholding the lineage relation;
a shuffle that destroys all syntax is not a specific causal-lineage control.
There is no selected annotation budget or fit in this note. Designing this
whole task before a target reading choice would be a substantial new project,
not a cheap extension of1160.

## Exactly which Voynich decision would change?

The existing Q/FS construction question is the closest real decision: does a
shared construction preserve participant M, create a new referent χ(M), or
denote a product without a relay? These alternatives become distinguishable
only when a fixed later consumer requires M versus χ(M), under the same
whole-unit writer. Neither source success nor source failure supplies that
written consumer.

- **Source success:** earns considering a material-lineage scorer *once*
  complete alternative target accounts and their observation channel are
  frozen. It does not select preservation, transformation, a recipe genre,
  an operation word or an ingredient. It would justify investment in that
  specified future comparison, not a target decoder by itself.
- **Source failure:** stops that particular recovery instrument. It does not
  favor either Q/FS meaning because historical texts may express lineage in
  ways the instrument cannot infer.
- **Current situation:** both outcomes leave the actual uncompleted reading
  alternatives unranked. Therefore the new fit fails the present decision-value
  test even though its scientific question is distinct and potentially useful.

The next meaningful work is to author the competing full participant accounts
and their unequal later consequence from already exposed units. That is
allowed exploratory reasoning before independent confirmation; no translated
anchor is required in advance. If the only difference is renamed latent
states and every consumer remains unspecified, stop that account rather than
build a source control to make it seem more concrete. No closed route is
reopened and no word meaning is assigned here.
