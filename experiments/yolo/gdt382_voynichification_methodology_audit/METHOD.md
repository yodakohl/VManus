# GDT382 — methodology stress-test / Voynichification audit

## Purpose

GDT382 is an instrument calibration, not a Voynich operator search.  It tests
whether known functional structure remains recoverable when the readable
GDT378 comparator panel is hidden behind a composite observation architecture.
The GDT381 outcome is not an input to the design and is not used to choose an
encoder, representation, endpoint, threshold, or decision.

## Inputs and seal

The sole observation source is the already public, form-blind GDT378 comparator
layer.  It contains 133,183 elements in 3,235 records from CoReMA, PCEEC2,
Curious Cures, Harleian cookery, and *The Book of Quinte Essence*.  Its
`opaque_form_id` preserves equality but exposes no word.  The hidden GDT378
oracle is hash-bound at freeze time but is read only after the encoder and
recovery contract have been frozen.

No Voynich table is an input.  No f84 row, file, image, text, or formal payload
may be opened, parsed, retained, or scored.

## Oracle-blind base encoder

The base encoder is deterministic and never reads an oracle label.  Each
element is mapped to:

`DOMAIN_LOCAL_HOST × WRAPPER × POSITIONAL_STATE × BOUNDARY_STATE × RECORD_STATE × RENDERER_VARIANT`.

Host IDs are stable domain-local hashes of opaque equality identities.
Wrapper and renderer variants are deterministic functions of collection,
record, occurrence and identity, so one host has multiple composite/surface
states while the same wrapper and renderer are shared by many hosts.  Position
and record states are coarse mechanical bins.  Boundary state is copied from
the form-blind physical-record observation.  Fields are created mechanically
at a frozen width of four elements, additionally terminating at an observed
record boundary.  The rendered group is a reversible-to-the-sealed-encoder
synthetic display code, not a model of Voynich glyphs and not tuned to any
Voynich statistic.

## Hidden endpoints

The primary audit endpoints are `FUNCTION_WORD`, `ALTERNATIVE_OR`,
`POLARITY_EXCLUSION`, `UNTIL_STATE_GATE`, `COORDINATOR`, and `REF_ANAPHORA`.
The readable labels are used only as positive-control truth.  They do not
become Voynich interpretations.

## Representation ablation

Six frozen levels are compared:

1. `SOURCE_TOKEN_EQUALITY` — source token equality, still represented only by
   its opaque ID;
2. `DOMAIN_LOCAL_OPAQUE_ID` — a fresh domain-local opaque hash (equality-isomorphic
   to level 1, an explicit information-preservation check);
3. `HOST_IDENTITY` — the content/host ID with renderer hidden;
4. `COMPOSITE_JOINT_STATE` — exact host+compiler composite;
5. `COMPLETE_RENDERED_GROUP` — complete rendered group identity plus fixed
   character-bigram hash features; and
6. `FIELD_CONSTRUCTION_SPAN` — ordered field-local composite pattern and field
   location/boundary state.

No representation is selected after outcomes are visible.

## Recovery models

Two fixed recovery regimes are compared.

* `STRICT_UNIVERSAL`: hold one complete domain out; learn only shared structural
  component effects.  Exact domain-local identities cannot transfer.
* `DOMAIN_LOCAL_HIERARCHICAL`: hold one collection/page-block out inside each
  domain; learn local opaque identity and realization effects while sharing
  only the endpoint definition.  Metrics are macro-averaged across domains.

Both use a low-capacity smoothed categorical naive-Bayes model.  All feature
vocabularies and counts are learned inside the training fold.  Constant and
structure-only baselines are scored in every fold.  The main outputs are held
log-loss gain, AUC, average precision, and positive-domain count.

## Overcontrol audit

For each of eight structural variables—line/field position, record-relative
position, boundary/closure, recurrence, frequency, record length, previous
state, and next state—three frozen treatments are compared:

* `GRAMMAR_FEATURE`: the variable is available only to the full model;
* `CONDITIONED_NUISANCE`: the variable is available to both baseline and full
  model, so its direct signal is removed from the incremental endpoint; and
* `REMOVED`: the variable is available to neither model.

The contrast measures how much true positive-control function signal is lost
when a structural variable is residualized rather than modeled as grammar.

## Free and bound positive controls

The base encoder is supplemented by seven explicitly oracle-driven diagnostic
encodings: free token, prefix, suffix, wrapper alternation, boundary choice,
positional alternation, and zero/suppletive construction.  Marker inventories
are domain-local, so a universal exact marker cannot cheat across domains.
The encoder rule is frozen before the oracle is read.  These controls diagnose
which realization types the instrument can recover; they are not historical
claims about the comparator text or Voynich.

## Discovery versus confirmation

Exploration ranks all frozen endpoint×representation cells by held gain and
AUC.  Confirmation keeps strict held-domain/held-collection, codelength,
stability, and fixed-prediction max-family diagnostics.  A separate prospective
simulation selects a representation on predetermined development collections
and evaluates it on predetermined untouched confirmation collections.  The
audit reports how often a genuine known endpoint is visible in exploration,
survives an all-at-once family correction, and survives a small frozen follow-up.
Confirmation standards are not lowered.

## Ontology audit

Two predeclared summaries are reported.  The natural-language-like inventory
uses coordinator, alternative, polarity, state gate, reference, and function
classes.  The technical-notation-like inventory maps the same hidden truth to
`ADD_ITEM`, `ALTERNATIVE_SLOT`, `EXCEPTION`, `NEXT/GATE`, `COPY_PREVIOUS`,
`RELATION/END` proxies.  Comparator performance alone cannot identify the
Voynich ontology.

## Decisions

The report uses the requested methodological decision matrix.  If recovery
fails after composite encoding, GDT376–381 negatives are instrument-limited
for that representation.  No new Voynich operator experiment is authorized
until the instrument is repaired.
