# `okoaiin`: explicit relation candidates, without a selected meaning

29 September 2026. **A small written construction now makes the proposed
role reversal explicit. It does not yet translate the passages or select
`okoaiin = influences`.** The useful result is the exact difference between
three possible readings and the additional grammar each requires. All
288 input groups and their frozen formal analyses remain in the
[candidate table](INFLUENCE_CONSTRUCTION_TABLE_20260929.tsv).

This is the bounded exploratory authoring step registered in the
[contract](INFLUENCE_CONSTRUCTION_PREFLIGHT_20260929.md), informed by Q's
comparison of IDEA765/766/767. It is not a blind test, a new corpus search or
a repair of the earlier FROM hypothesis. The
[lock](INFLUENCE_CONSTRUCTION_LOCK_20260929.json) preserves seven inputs.

## The three actual readings

Use `R` solely as the **guessed** INFLUENCE relation. The other displayed
Voynich forms are unnamed participant classes, not Sun, drug, body or metal
translations. ZL's lower-ring first group is `okey`; IT reads `okeo`.

| Candidate | Lower-ring opening | f89v1.14 construction in ZL/IT | Consequence and added assumption |
|---|---|---|---|
| A: adjacent active arguments | `R(okey/okeo, okol)` | `R(chody, dal)` | The nearby `okol` is outside this clause. It supplies no relay merely by proximity. Assumes adjacent groups are arguments. |
| H: head-preserving modification | `R(okey/okeo, okol)` | `R([okol chody], dal)`, participant head `okol` | The class receiving the ring's influence can be the class exerting the prose influence. Adds `N chody` as a phrase retaining N's head; chody's property is unknown. |
| P: passive switch | `R(okey/okeo, okol)` | `R(dal, okol)` from `okol chody R dal` | `okol` receives influence in both clauses. Adds a passive/argument-order function to chody. |

H is therefore a concrete candidate for a **mediating participant**; P is a
candidate for **two incoming effects**. They do not say the same thing.
But those different readings are consequences of their assumed grammar.
Nothing independently read in the target yet chooses H over P or A. H's
agreement with the motivating relay cannot be counted as a new observation:
that is why H was proposed. No occurrence-indexed skip or extra gloss was
introduced to produce it.

The class recurrence is also weaker than physical identity. The same written
form on two leaves does not establish the same material portion, the same
drug species, or an anaphoric reference crossing leaves. Those stronger
identities are **not** inferred by the constructor.

## All readings and all remaining content

| Reading | Complete upper ring | Complete lower ring | Complete f89v1.13–20 |
|---|---:|---:|---:|
| ZL3b | 8 groups | 12 groups | 75 groups |
| IT2a | 8 | 11 | 78 |
| RF1b | 8 | 11 | 77 |

These are288 records of three alternative readings of one manuscript. They
are not288 translated words or three independent confirmations. Every group,
original separator flag, GDT1051 formal parse status and frozen wrapper/host
analysis is retained in the table. The two complete source packets remain
unchanged; GDT1051's BPE analysis is referenced rather than silently replaced
by a new segmentation. In particular, no `okaiin`, `qokaiin`, `chokaiin` or
`qokol` becomes another target by deleting a character.

RF has `cho@152;y` at the critical prose position. A can display it as an
unnamed adjacent argument; H and P cannot establish their required exact
marker there. Their RF prose derivations remain unresolved. The three lower
ring versions do admit the same local argument pattern, with their different
first whole forms retained. The upper ring has no exact `okoaiin`; no matching
verb, antonym or Moon/silver counterpart is supplied.

ZL has an **uncertain small gap between dal and chdy** at f89v1.14; IT/RF
mark that gap definite. All three ZL constructions therefore additionally
require choosing this gap as the end of the proposed right NP. Its strict
hard-chunk counterpart remains `dalchdy`; no joined reading is tested here.
The result marks these three cases conditional on the boundary choice.
This information was always preserved in the input/table. The first local
clause display did not explicitly surface its consequence; review corrected
that status before publication, without changing an input or repairing a
candidate rule. H's relay is thus an IT local derivation and a ZL conditional
derivation, with RF unresolved, not an unqualified all-reader result.

There are four exact `okol` occurrences per reader in this complete scope:
one in the lower ring, one before the prose relation, and two more on
f89v1.19. The last two acquire only the explicitly proposed unnamed class
identity. Neither has a derived predicate or participant relation under
these constructors. The two `qokol` forms on f89v1.18 remain separate and
unread. This is the actual additional consequence of looking beyond the
attractive opening: **no further relation is obtained**.

All three candidate tables leave270 positions without even a local syntactic
role. The other18 positions contain guessed relation/argument/modifier roles,
not18 established lexical values. H/P's unresolved RF clause is included in
these totals; assigning `R` there does not fill its arguments. Even the
displayed `okol` and `dal` arguments have no concrete translated denotation.

## Historical meaning and retained counterevidence

The complete Sloane73 passage is preserved in
[E_COMPLETE_PASSAGES.md](source_supply_20260929/E_COMPLETE_PASSAGES.md).
Its medical example distinguishes stars influencing a drug from that drug
**drawing away** humours from specified regions and explicitly not from
others. One exact INFLUENCE word does not express that entire chain. It does
not justify replacing both relations with the more precise verb “attracts,”
nor identify the Sun as the actor in that particular named-star example.
The source is a later fifteenth-century comparator, not an identified target
exemplar. The present authoring step introduces no new source or quotation.

IDEA765's selected whole account still owes an influenced medicine, a
region-selective removal relation, included and excluded body regions, and
their written scope. None is supplied by H's class-level relay. Removing
those obligations after this outcome would change the candidate. A more
general relation hypothesis can remain possible without pretending to have
passed the particular source account.

The f88r `okol` label's botanical/material neighborhood remains relevant;
its exact object owner is uncertain. Neither WATER, GOLD, ROOT, MEDICINE nor
LIGHT is installed here. GDT1052's strict globally two-sided FROM contract
remains rejected. H/P are different declared local constructions, not a
retrospective excuse for that failure. They make no universal chody claim
and have no outside transfer validation. GDT1053's local controls removed
independent support for the old DRY interpretation; no dryness gloss is
smuggled into the modifier.

The current179-selector profiles also remain obligations rather than gloss
selection: exact okoaiin occurs once outside the two locally admitted rings;
okol52/56/51 times, chody78/82/66, dal191/201/158 in ZL/IT/RF. Much astronomical
text is outside that global allowlist. A general relation or participant
reading must eventually explain its whole distribution, not just these two
physical positions. No probability is calculated from these counts.

## Decision and replay

Retain H and P as explicit **partial C0 constructions**. Do not select a
complete reading, promote INFLUENCE to a translated word, or run a fixed
semantic test on their self-generated role assignments. Compared with E,
we now have written argument rules rather than just alternative actor names;
we still have no unselected semantic consequence or bound selective body
effect. No automatic added dictionary, passive exceptions, decoder or source
hunt follows from this block.

`python research_registry/proposals/laufenberg_f85r2_20260926/influence_construction.py`
rebuilds the table and result from the locked existing artifacts.
`validate_influence_construction.py` independently checks unchanged input
accounting and the hand-derived direction contrasts, including the RF stop.
Its [PASS](INFLUENCE_CONSTRUCTION_VALIDATION_20260929.json) establishes those
checks only, not the truth of the semantic guesses or the manual judgment
that no complete reading was produced.

Preparation/construction/validation/publication belong to the10:55–11:40UTC
inclusive block; the20-hour research request continues. No new target text,
image, admission, reserve, contact or relation-score packet was used.
Independent confirmation capacity is zero new physical leaves; confirmed
translated words remain zero.
