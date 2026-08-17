# GDT176 report — a partial readable-recipe record schema

## Outcome

**PARTIAL EXTERNAL ROLE INSTRUMENT SUPPORTED; Q20 SCHEMA EXPLORATORY.**

This is useful progress toward a translation architecture, but it is not a
translation.  A model using only unit position and span length recovers a
coarse role structure across six entirely held medieval recipe collections.
Applied unchanged to Q20 fields, it separates three defensible abstract
classes:

- `INSTRUCTION_CLAUSE_LIKE` — long procedural/clausal units;
- `SHORT_ARGUMENT_LIKE` — short nominal/content arguments, without separating
  ingredients from tools; and
- `RECORD_CLOSER_LIKE` — late closing/qualification units.

The external instrument does **not** recover tools as a separate class and is
almost unable to recover openers.  Those distinctions are not exported as
Voynich semantics.

## Source-first calibration

GDT176 froze 1,136 recipes from six CC-BY CoReMA annotated-detail collections
before running the Q20 projection.  The external observation contains 22,394
calibration units in five oracle classes.  CoReMA concept IDs and editor English
labels were excluded from predictors.

| External model | Held bits/unit | Gain over fold prior | Accuracy | Mean fold macro-F1 | Positive collections |
|---|---:|---:|---:|---:|---:|
| training-role prior | 1.640679 | 0 | 0.4408 | 0.1227 | — |
| position + span length | **0.722623** | **+20,558.94 bits** | **0.8260** | **0.4906** | **6/6** |
| plus opaque recurrence | 1.108560 | +11,916.27 bits | 0.7964 | 0.4853 | 5/6 |

The projection model was selected solely by external held-collection log loss.
Opaque identity recurrence made the result worse, not better.

### What the selected model actually recovers

| Oracle class | Support | Recall | Precision | Transfer decision |
|---|---:|---:|---:|---|
| OPERATION | 9,871 | 0.907 | 0.914 | retain as `INSTRUCTION_CLAUSE_LIKE` |
| INGREDIENT | 9,411 | 0.975 | 0.772 | merge into `SHORT_ARGUMENT_LIKE` |
| CLOSER | 604 | 0.588 | 0.755 | retain as `RECORD_CLOSER_LIKE` |
| OPENER | 633 | 0.017 | 0.045 | unresolved |
| TOOL | 1,875 | 0.000 | undefined | merge into `SHORT_ARGUMENT_LIKE` |

The crucial negative is the TOOL collapse: almost every tool is structurally
indistinguishable from an ingredient.  The model recognizes an argument slot,
not the argument's semantic type.

## Q20 projection

The frozen model was applied without refitting to all 4,443 fields in the
existing f84-free Q20 inventory (1,483 ZL3b, 1,487 IT2a, 1,473 RF1b).  The
three transcriptions are alternate readings, not three samples.  Among 1,467
field keys available in all three, 1,407 (95.91%) have the same top class.

For ZL3b, the projection is:

| Record scope | Instruction-clause-like | Short-argument-like | Record-closer-like | Unresolved edge |
|---|---:|---:|---:|---:|
| OPEN | 249 | 269 | 0 | 39 |
| BODY | 476 | 329 | 121 | 0 |

The first field of a record is 103 instruction-like, 28 short-argument-like,
and 39 unresolved-edge.  The final field is 121/170 record-closer-like, with 25
instruction-like and 24 short-argument-like counterexamples.  Thus the best
current low-resolution parse of a typical Q20 record is not simply “heading
then prose.”  It is a sequence mixing clause-sized and argument-sized fields,
often ending in a distinct closer/qualification-sized field.

## Opaque host leads

These are **placement leads**, not word meanings.  Several first PAGE_HOST IDs
recur on at least three folios while remaining in the same projected abstract
class.  The cleanest short-argument-like IDs are `che` (16/16, six folios),
`oke` (14/14, seven), `okche` (14/14, five), `e` (13/13, seven), `opche`
(8/8, seven), and `okee` (23/24, eight).  `chey` is instruction-clause-like in
8/8 occurrences on five folios; `or` is instruction-like in 27/33 occurrences
on all eight folios.

This does not show that `che` is an ingredient or that `chey` is a verb.  The
selected model does not use host identity, and short fields preferentially
contain those hosts.  The atlas identifies high-value positions for a future
independent content test.

## Interpretation

The result supports a **coarse record compiler** over Q20: field size and
record position carry enough structure to look like procedure/argument/closer
organization learned from readable medieval recipes.  It does not localize
semantic information inside PAGE_HOST, because adding opaque recurrence hurt
external transfer.  This fits the active hierarchical record theory better
than a flat stream of lexical words, while remaining compatible with natural
language expressed through an abbreviation/notation layer.

The strongest next test is independent of the calibration features: freeze
the three-class projection and ask whether unused Q20 compiler features and
cross-folio host behavior distinguish the classes, with special attention to
whether short-argument-like hosts recur across different instruction-like
contexts and whether closer-like fields have a stable source-native closure
profile.  That can strengthen or break the schema without assigning a word.

## Claim ceiling

GDT176 establishes at most a transferable cross-corpus **role likeness** for a
coarse Q20 record schema.  It establishes no Voynich ingredient, tool, verb,
heading, language, plaintext clause, or translation.  f84r was not accessed.
