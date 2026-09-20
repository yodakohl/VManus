# Finite commitment-and-causality constructor: source-only worked account

Status: RAW_UNSCREENED, unselected. This is a source/content constructor, not
a Voynich reading or a target test. No new target rows, image, reserve, sealed
folio, decoder or experiment was opened.

## Why this is a distinct constructor

IDEA000397 already owns the complete Phaedrus I.1 content and its broad
reported-speech distinction. This note supplies the missing executable layer:
a finite typed constructor with fixed arities, explicit world facts, a separate
commitment state, deterministic rebuttal checks and a generated counterfactual.
It is different from IDEA000398's Llull rule-species/correlative shorthand and
IDEA000128's chamber-table/morphism model. It also does not treat any source
word as a Voynich component.

The source is the complete 15-line *Lupus et Agnus* text in the existing
`DISCOURSE_CONSTRAINT_RAW_SOURCES_20260920.json` packet. The packet records the
Latin text, its hashes, the two accusations, two rebuttals, father substitution,
completed killing and final moral. The digital witness ancestry is uncollated;
the father accusation remains unverified.

## Declared finite language

The context contains typed participants `WOLF`, `LAMB`, `FATHER`, `NARRATOR`,
places `STREAM`, `WOLF_DRINKING_PLACE`, `LAMB_DRINKING_PLACE`, and times `NOW`,
`SIX_MONTHS_BEFORE_NOW`, `LAMB_BIRTH`. A fact store contains only declared
relations. A commitment store records `REPORTED`, `REBUTTED`, `ENDORSED`, or
`UNVERIFIED`; it never promotes a report to world truth automatically.

```text
LOCATE(x, place, relation)
INTRODUCE(x, type, scope)
FLOW(medium, from_place, to_place)
EXISTS_AT(x, time)
PARENT_OF(parent, child)
ALLEGES(speaker, agent, act, recipient, time)
ASSERTS(speaker, proposition)
REBUTS(speaker, claim, reason)
ENDORSES(speaker, reason)
DOES(agent, patient, act, status)
GENERALIZES(speaker, story, rule)
```

The constructor has two fixed rebuttal rules. `UPSTREAM_FLOW_CHECK` rejects
`MUDDY_WATER` when the alleged muddying agent is downstream of the accuser's
drinking place. `NOT_YET_BORN_CHECK` rejects an alleged earlier action when the
agent's `EXISTS_AT` interval begins after the alleged time. `REBUTS` changes
commitment status only; it does not delete the allegation or block later
`DOES`. `PARENT_OF` introduces a related participant but supplies no evidence
that the parent performed the alleged act.

## Fully executable source example

The initial context is:

```text
LOCATE(WOLF,STREAM,ABOVE)
LOCATE(LAMB,STREAM,BELOW)
FLOW(STREAM,WOLF_DRINKING_PLACE,LAMB_DRINKING_PLACE)
EXISTS_AT(LAMB,LAMB_BIRTH)
LAMB_BIRTH > SIX_MONTHS_BEFORE_NOW
PARENT_OF(FATHER,LAMB)
```

The ordered constructors are:

```text
ALLEGES(WOLF,LAMB,MUDDY_WATER,WOLF_DRINKING_PLACE,NOW)
REBUTS(LAMB,MUDDY_WATER,UPSTREAM_FLOW_CHECK)
ENDORSES(NARRATOR,UPSTREAM_FLOW_CHECK)
ALLEGES(WOLF,LAMB,VERBAL_OFFENSE,WOLF,SIX_MONTHS_BEFORE_NOW)
REBUTS(LAMB,VERBAL_OFFENSE,NOT_YET_BORN_CHECK)
ALLEGES(WOLF,FATHER,VERBAL_OFFENSE,WOLF,SIX_MONTHS_BEFORE_NOW)
DOES(WOLF,LAMB,KILL,COMPLETED_UNJUST)
GENERALIZES(NARRATOR,STORY,OPPRESS_INNOCENT_WITH_INVENTED_CAUSES)
```

Evaluation is deterministic:

| Proposition | Result | Reason |
|---|---|---|
| wolf says lamb muddied water | `REPORTED`, then `REBUTTED` | declared flow runs from wolf's side toward lamb's side |
| lamb offended six months earlier | `REPORTED`, then `REBUTTED` | lamb's existence begins after that time |
| father offended | `REPORTED`, `UNVERIFIED` | parent relation does not entail the act |
| wolf kills lamb | `COMPLETED_UNJUST` | action is independent of truth of the earlier allegations |
| narrator's moral | `ENDORSED` generalization | source explicitly assigns the fable's purpose |

Every argument is typed and consumed by one constructor. No nearest-noun rule,
free filler, hidden participant, or truth upgrade is available.

## Observable consequence beyond the fitted source

The same constructor generates a held counterfactual by changing one declared
fact at a time. If flow is reversed to
`FLOW(STREAM,LAMB_DRINKING_PLACE,WOLF_DRINKING_PLACE)`, the first muddy-water
rebuttal no longer fires. If `LAMB_BIRTH` is moved before
`SIX_MONTHS_BEFORE_NOW`, the temporal rebuttal no longer fires. In both variants
the final `DOES(WOLF,LAMB,KILL,COMPLETED_UNJUST)` remains executable. A flat
true-event account predicts both allegations as true; a rebuttal-blocks-action
account predicts no killing; an outcome-entails-truth account promotes the
rejected accusations. Each differs on a declared consequence outside the
source's fitted fact assignment.

This is a source-side discriminator only. It does not identify a target
operator, word, language, or historical transmission path.

## Costs and stopping point

The finite language spends explicit commitment-state and rebuttal semantics,
and it assumes that causal direction and temporal existence are represented as
typed facts. The digital source is not a medieval manuscript witness, the
father allegation is unresolved, and no target passage is independently owned.
The proposal therefore remains RAW_UNSCREENED. A later selection would need a
complete target owner and a fixed realization of these constructors before any
fit; this dossier supplies neither.
