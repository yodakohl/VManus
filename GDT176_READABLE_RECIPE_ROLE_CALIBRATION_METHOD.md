# GDT176 — readable medieval recipe role calibration

## Purpose

GDT176 supplies the missing external content endpoint for the Q20 record work.
It first learns what structural observations can recover **editor-established
roles** in readable medieval recipes.  Only a successful external instrument
may later be projected onto Voynich record positions.  The projection will not
use German strings, translations, or concept names as Voynich matches.

This is a new route.  It does not rerun host-neighbour prediction, visual gloss
mining, GDT003 morphology, or a language/cipher decoder.

## Source-first freeze

The external panel is frozen before any new Voynich score.  The source universe
is the official CoReMA recipe index.  A collection is eligible when:

1. its normalized manuscript interval lies wholly inside 1350–1500;
2. it has at least 30 indexed records;
3. a collection-level annotated-detail TEI source is publicly available;
4. it contains at least 30 recipe elements; and
5. it contains at least 30 explicit CoReMA `instruction` elements.

The resulting collections are B4, B6, Br1, Bs1, Gr1, and W1.  The exact source
bytes and selection outputs are SHA-256 frozen in
`gdt176_corema_collection_manifest.tsv` and `gdt176_source_freeze.json`.

## Observation and oracle layers

The tracked recipe inventory contains only record sizes and counts.  The role
oracle contains element order, token count, enclosing instruction ordinal,
CoReMA role tag, concept identifier, and editor-supplied English label.  No
Voynich analysis may see the English label or concept identifier while fitting
the transferable structural instrument.

The first calibrated targets are:

- record-level `OPENER`, `INSTRUCTION`, and `CLOSER` position;
- nested `INGREDIENT` versus `TOOL` placement;
- recurrence and document-frequency profiles of normalized external concepts;
- within-record transitions among the above roles.

Two low-capacity multinomial models are compared under leave-one-collection-out
evaluation. `POSITION_LENGTH` uses relative unit position, squared position,
log span length, and log record length.  The second adds normalized opaque-ID
frequency, document frequency, neighbour diversity, and prior within-record
recurrence.  Both use fixed ridge strength and deterministic optimization.
The model with lower summed held-collection log loss is selected before Q20
aggregates are inspected. Literal German characters, English labels, and
concept identities are forbidden predictors.

## Planned Voynich projection

If an external instrument beats the training-role prior, project its role
probabilities onto the existing f84-free Q20 record/field inventory without
refitting. Q20 scoring uses physical record/field position and field extent;
opaque first-PAGE_HOST recurrence is available only if the externally selected
model contains it. The projection is reported as `ROLE_LIKE`, never as a
translation of a host.

Class-specific transfer is mandatory. A failed oracle class is not exported
under its semantic name. In the completed calibration, OPERATION is mapped to
`INSTRUCTION_CLAUSE_LIKE`, INGREDIENT and TOOL are merged into
`SHORT_ARGUMENT_LIKE`, CLOSER is mapped to `RECORD_CLOSER_LIKE`, and the failed
OPENER class becomes `UNRESOLVED_EDGE_CLASS`.

The first falsifier is external: if the structural instrument cannot recover
known CoReMA roles on held collections, it cannot license any Q20 role claim.

## Seal and claim ceiling

f84r is not an input and remains sealed.  Even a positive GDT176 result may
establish only that a Q20 record position has a distribution resembling a
role-bearing position in annotated medieval recipes.  It cannot establish a
word meaning, German identity, language, plaintext, or complete translation.
