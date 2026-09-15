# *De balneis*: operator countercase review

**Status:** SOURCE_ONLY_UNREVIEWED (2026-09-15). This review corrects the
interpretive scope of raw proposals IDEA000344 and IDEA000345. It does not edit
the frozen source packet, inspect target data, or assign target meanings.

## Frozen source and review boundary

Source:
research_registry/work_batches/ten_hours_20260915/balneis_cache/ALIM553.txt

Source SHA-256:
397968f02fc5faf54161f2c0df9e7557f96d36e649a27a140e64c2cfe0c69ecd

Relevant complete entries are XI (lines 122-134), VII (74-85), XIX (219-228),
and XXXIII (393-404). The source clauses below retain printed spelling. The
source-family packet remains separate from whole-clause operator hypotheses.

The live idea commands were temporarily stale on the imported ledger, so this
review does not infer absence from an empty search. Explicit predecessor files
and registry rows were checked directly: IDEA000017 (prior mention/anaphora),
IDEA000028 (modal obligation), IDEA000030 (causal connector), IDEA000034
(exception override), IDEA000042 (conditional applicability), IDEA000047
(restriction/default), IDEA000343 (source/recipient sign), and IDEA000344-345
(operator grammars).

## Countercase 1: XI requires a recipient heat-tolerance guard

The complete XI sequence is:

- 'Illa recens in fonte suo sinthomata tollit,' (line 129)
- 'Languidus ardorem si paciatur aque.' (line 130)
- 'Fonte relicta suo nichil affert utilitatis;' (line 131)
- 'Hec eadem prodest frigida facta parum.' (line 132)
- 'Qui petit ergo sui bene de langore iuuari,' (line 133)
- 'Senciet auxilium, si renouabit aquam.' (line 134)

The earlier raw operator sketches treated the fresh-source clause as a simple
fresh-state-to-effect pair and omitted line 130. That is unsupported. The
fresh-source reading must carry the recipient Languidus and the conditional
heat phrase si paciatur aque; the exact historical scope of ardorem aque is
retained as a source-language question, but it cannot be deleted.

The text also does not state that one patient executes the sequence
fresh -> removed -> cooled -> renewed. It contrasts source states and outcomes:
water fresh in its source has one claim, water left at the source has no utility,
the same water cooled has little benefit, and renewal is a condition in the
final aid clause. A sequential transition grammar may remain a hypothesis, but
it must explicitly mark these as alternative or conditional cases unless an
independent source boundary supports event succession.

This changes IDEA000344's guard representation to:

GUARD(SOURCE=XI water, STATE=recens in fonte suo, RECIPIENT=Languidus, CONDITION=si paciatur ardorem aque) -> EFFECT(sinthomata tollit)

with separate conditional cases:

- STATE=Fonte relicta suo -> EFFECT=nichil affert utilitatis;
- STATE=frigida facta -> EFFECT=prodest ... parum;
- CONDITION=si renouabit aquam -> EFFECT=Senciet auxilium.

For IDEA000345, retain an ordered possibility only as a proposed grammar
property. Do not call the source itself an executed state path. Its falsifier
must include failure to distinguish alternatives from transitions.

## Countercase 2: XIX has a chronicity restriction and an avoidance closure

The complete XIX closing clauses are:

- 'Luminibus lumen reddit, vestigia claudis,' (line 225)
- 'Passio ni fuerit inueterata diu.' (line 226)
- 'Rem loquitur certam non est incognita multis:' (line 227)
- 'Culma nocet sanis, morbida membra iuuat.' (line 228)

The sign contrast in line 228 cannot be detached from line 226. The source
restricts the preceding effect by whether the condition has become longstanding,
then supplies an authorial assertion and a healthy/diseased contrast. A
condition-to-effect grammar must preserve this scope and the final closure,
rather than count only the body target or the words nocet and iuuat.

## Countercase 3: VII and XXXIII do not support a fixed hydrops sign

VII states:

- 'Sed nocet ydropicis, cum sit dulcissima potu:' (line 76)
- 'Vim consumendi non habet, unde nocet' (line 77)
- 'Pulmonem lesum sanat et inde Jecur.' (line 79)
- 'Subuenit egrotis est quibus egra cutis.' (line 83)

XXXIII states:

- 'Prodest ydropicis qui exfleumate grosso.' (line 396)
- 'Consueuit eam splene tumente Jecur.' (line 397)
- 'Ad guttam frigidam que est imbita neruis' (line 399)
- 'Frequentant aquam que euacuata crescit.' (line 400)

The source therefore supplies a counterexample to any fixed HYDROPS polarity:
VII has a stated hydrops harm condition, while XXXIII has hydrops help under a
thick-phlegm condition. VII also supplies help for an injured lung and an
affected skin, so the water identity and local condition cannot be discarded
after observing one negative clause. The source's claims are preserved as
historical assertions; no efficacy is endorsed.

## What remains supported in IDEA000344 and IDEA000345

IDEA000344 remains a possible finite guard architecture if it includes every
supplied condition and permits source-specific sign. It should not use one
body-family sign table. Its minimum source obligations are:

1. retain XI line 130 with Languidus and the heat-tolerance condition;
2. represent XI lines 131-134 as conditional/contrast cases unless a separate
   source rule licenses event succession;
3. retain XIX line 226 chronicity scope and line 228 closure;
4. allow VII and XXXIII to assign different hydrops outcomes under their stated
   source and condition fields.

IDEA000345 remains a possible state/exception grammar, but its state sequence is
a model proposal, not an observed source fact. It must distinguish state
alternatives from event transitions and must mark the VII/XXXIII hydrops
difference and XIX chronicity clause as explicit branches. If boundaries are
chosen only after seeing the desired sign or sequence, the grammar fails.

Neither proposal supplies a target gloss. The 13 source lexical families are
not operators, and no operator match would establish a Voynich meaning.

## Two qualitatively different next meaning routes

These are queue-informed exploratory routes beyond literal body-incidence
counting. They remain unreviewed and do not authorize target access.

### Route A: discourse reference and prior-mention binding

Predecessor: IDEA000017. The complete XI entry provides a source consequence
that can be read at the discourse level: Illa, suo, Hec eadem, and aquam may
maintain or re-identify a water referent across clauses, while Languidus
introduces a recipient condition. The route asks whether later references
depend on an introduced source/participant rather than merely repeating a water
noun.

Concrete observable prediction: in a complete bounded paragraph, repeated
referential constructions should preserve one antecedent through state or
condition changes, while first introductions should carry an introduction cue.
A matched local-list rival predicts no stable antecedent chain.

Why it may fail: XI's pronouns and repeated water references may be formulaic
or editorial, and a target passage may not expose independently bound
antecedents. Apparent continuity would then be compatible with ordinary
repetition.

### Route B: conditional applicability and advice scope

Predecessors: IDEA000042, IDEA000028, IDEA000030, and IDEA000034. The complete
source consequence is the combination of XI's si renouabit aquam, XIX's
Passio ni fuerit inueterata diu, and VII's explicit Sed nocet ydropicis
condition. This route treats conditions and final advice as operators that
license, restrict, reverse, or close an effect clause.

Concrete observable prediction: a complete bounded paragraph should show a
stable interaction between a preceding condition and the applicability or sign
of the following effect, with an explicit restriction or advice closure. An
unconditional descriptive/list rival predicts no condition-by-outcome
interaction after event and source controls.

Why it may fail: Latin conditional and advice syntax may be ordinary prose
rather than a reusable semantic operator, and target records may lack a
reliably bound condition/applicability endpoint. A result would remain
observationally equivalent to a procedural sequence unless the condition scope
is independently fixed.

The two routes have different evidence obligations: Route A requires antecedent
identity and discourse continuity; Route B requires condition scope and
applicability/sign interaction. Neither can be reduced to the 166 lexical
incidences in the frozen body-term packet.

