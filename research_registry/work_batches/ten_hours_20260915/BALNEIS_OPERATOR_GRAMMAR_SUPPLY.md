# *De balneis*: finite conditional operator grammar supply

**Status:** SOURCE_ONLY_RAW (2026-09-15). This dossier is based only on the
frozen ALIM553 source. Abstract operator names below are source-role labels;
they are not translations of Voynich forms or medical truths.

## Source and bounded review

Source: research_registry/work_batches/ten_hours_20260915/balneis_cache/ALIM553.txt
SHA-256 397968f02fc5faf54161f2c0df9e7557f96d36e649a27a140e64c2cfe0c69ecd.

The bounded duplicate search covered finite semantic operator grammar,
condition/effect polarity, water-state reuse, hydrops, and prior De balneis
material. It returned IDEA000047, IDEA000325, IDEA000334, IDEA000343, GDT212,
and generic operator/state histories. IDEA000343 already records the broad
source-by-recipient sign relation. The two proposals here are narrower grammar
architectures with different observable predictions: conjunctive guard scope
versus ordered state transitions with an override.

## Shared finite vocabulary

The proposed source-role inventory is finite:

- SOURCE: named bath/water identity;
- STATE: fresh at source, removed from source, cooled, or renewed;
- RECIPIENT: hydrops, healthy recipient, diseased body, or a specified body target;
- CONDITION: an explicit local condition such as sweet water, thick phlegm, or
  the source's own water state;
- EFFECT: a source predicate such as remove symptoms, give aid, help, or harm;
- SIGN: positive, negative, weak/limited, or null utility.

These are typed roles for source clauses. They do not claim that the source's
13 lexical families are 13 semantic units.

## Architecture A: conjunctive guard -> signed effect

Grammar:

CLAUSE = GUARD(SOURCE, STATE?, RECIPIENT?, CONDITION?) -> EFFECT(SIGN, TARGET)

A guard requires all fields that the source clause actually supplies. Missing
fields remain unspecified; no free cross-product of body terms and effects is
allowed. A single body noun cannot determine SIGN by itself.

Source instances:

- XI 122-134: (SOURCE=XI water, STATE=recens in fonte suo) -> remove symptoms;
  (STATE=Fonte relicta suo) -> no utility; (STATE=frigida facta) -> weak aid;
  (STATE=renewed) -> aid.
- VII 74-85: (SOURCE=Foris Cripte, RECIPIENT=hydrops,
  CONDITION=dulcissima potu / no consuming force) -> harm; the same entry has
  (RECIPIENT=injured lung) -> help.
- XIX 219-228: (SOURCE=Culma, RECIPIENT=healthy) -> harm, while
  (RECIPIENT=diseased body) -> help.
- XXXIII 393-404: (SOURCE=De Cruce, RECIPIENT=hydrops,
  CONDITION=exfleumate grosso) -> help.

Prediction: a complete paragraph under this grammar must preserve the joint
scope of source, recipient, and explicit condition. VII versus XXXIII must be
representable as two different guards for hydrops, and XIX must retain the
healthy/diseased split.

Strongest failure: the target or source representation cannot preserve which
conditions co-occur with each effect, or a single condition-free body-effect
table performs equally well. That would reject the conjunctive guard architecture
as overstructured.

Nearest rival: one fixed sign/effect per body family, with source identity and
water state treated as decorative context.

## Architecture B: ordered state transition with signed exception

Grammar:

ENTRY = INIT(SOURCE) ; STATE_UPDATE(STATE) ; EFFECT(SIGN,TARGET) ;
[REPEAT | DECAY | EXCEPTION(RECIPIENT, CONDITION, SIGN)]

This grammar makes order operative. A state update changes the current water
referent; an explicit exception can reverse or limit an otherwise active effect.
It is not a free list: every later effect must attach to the current state or a
marked recipient/condition branch.

Source instances:

- XI requires the sequence recens in fonte suo -> Fonte relicta suo ->
  frigida facta -> renouabit aquam, with outcomes respectively removal,
  no utility, little help, and aid.
- VII supplies an exception-like recipient branch: sweet water harms hydrops,
  while the later injured-lung clause is helpful.
- XIX supplies a recipient sign switch inside one entry: healthy recipients are
  harmed, diseased bodies helped.
- XXXIII supplies a separate source/condition branch where hydrops is helped
  under thick phlegm.

Prediction: a complete paragraph under this grammar must show a recoverable
state/update order, and sign changes must occur at an explicit recipient or
condition boundary. XI's removal, cooling, and renewal order is the strongest
falsifier; VII/XIX/XXXIII test whether the exception branch is marked rather
than silently fitted.

Strongest failure: source clauses behave as unordered independent claims, or
the supposed state/exception boundaries cannot be located without choosing
outcomes first. Then the sequential grammar adds unsupported structure.

Nearest rival: a bag of local effect statements whose order and repeated water
reference have no state-carry consequence.

## Architecture comparison and source ceiling

Architecture A predicts condition co-occurrence and permits independent clauses
in one entry. Architecture B predicts state carry, ordered updates, and explicit
branch boundaries. They therefore do not have the same falsifier. Both preserve
the known counterexamples: VII hydrops harm versus lung help, XIX healthy harm
versus diseased-body help, XXXIII hydrops help, and XI source/removal/cooling/
renewal dependence.

A future test would need complete bounded records, a frozen finite role table, and
a predeclared rival. It must score every declared clause and cannot infer a
target gloss from a matched operator. No target data, target body reading,
decoder, or experiment registration was used here.

