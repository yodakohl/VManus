# GDT136 — behavior-profile transfer to the legacy out-of-panel atlas

Status: `FROZEN_POSTHOC_CROSS_PANEL_BEFORE_DESCRIPTOR_SCORING`

## Question and chronology

GDT068 found, on an archived and postselected 332-locus panel, that a
source-only `PAGE_HOST` behavior profile using the host's own compiler states
and its neighboring compiler states (with position removed) described several
external annotation axes better than raw or PAGE_HOST character trigrams.
GDT109 later tested a different, fixed 44-locus legacy plant-annotation panel
with string and compiler representations; every representation lost to the
folio-excluded descriptor prevalence code.  The GDT068 behavior profile was
not tested there.

GDT136 freezes that single model/target crossing before joining the legacy
descriptor outcomes to new behavior predictions.  Both source archives and
the target panel are public and exposed, so this is a post-hoc cross-panel
stress test, not fresh confirmation.

## Fixed panels

- Target: the complete 44-locus, six-physical-folio GDT109 target inventory.
- Training: the complete 83-locus, five-folio GDT095 plant-label panel.
- Endpoints: all 19 frozen GDT095 descriptor tokens, plus the already defined
  target-capacity subset with at least three positive and three negative target
  loci.  No token may be selected from a new result.
- Source behavior: `gdt062_right_family_inventory.tsv`, with every `f84*` row
  rejected before behavior events are retained.

The capacity audit reads target folio and alternate display forms but does not
retain, join, or score `descriptor_tokens`.

## Frozen behavior representation

For each PAGE_HOST, count the GDT068 `BEHAVIOR_SELF_NEIGHBOR_NOPOS` events:

- own wrapper, inner-D, O/OT frame, right family, DY, and B3;
- preceding/following wrapper, frame, and DY states;
- no absolute position feature.

For a held target folio, rebuild every host profile from source events on all
other physical folios.  Average event frequencies within host, then sum the
profiles of the hosts in a target or training label.  The target-folio
exclusion applies to both the target feature and all training-label features.

Alternate readings are sensitivities, not replications.  An edition rendering
is profileable only when every PAGE_HOST in it has source events on at least
one non-target physical folio.  The primary averages every profileable edition
rendering and retains a locus if at least one is profileable.  Frozen
sensitivities require (a) at least two outside folios per host and (b) all
three readings profileable.  Missing editions are missing formal evidence,
not negative semantic evidence.

The score-blind audit fixed the resulting capacities at:

- primary: 31 loci on six physical folios;
- two-outside-folio sensitivity: 27 loci on six folios;
- all-three-readings sensitivity: 15 loci on five folios;
- at least 55 of 83 training labels profileable in every target-folio fold.

## Models and evaluation

Run exactly three representations on each identical eligible panel:

1. `BEHAVIOR_SELF_NEIGHBOR_NOPOS` — frozen primary;
2. `PAGE_HOST_CHAR3` — stripped-string baseline;
3. `RAW_CHAR3` — raw string-statistical baseline.

Use GDT109's fixed five-nearest-neighbor weighted-Jaccard rule (`K=5`, shrink
`4`) and folio-excluded descriptor prevalence code.  Candidate training labels
must be behavior-profileable in the target fold for all three models, keeping
the comparison pool identical.  Report total and per-folio gains, token-level
gains, coverage, and alternate-reading sensitivities.

Permute each complete 19-token target vector within physical folio in 10,000
shared worlds.  Report local and max-three inclusive p-values.  This null
quantifies the fixed archive crossing; it does not undo that GDT068's model was
selected on another exposed annotation panel.

## Decision and claim ceiling

A provisional structural transfer requires the behavior model to have
positive selector-paid gain, beat both string baselines, be positive on at
least four of six primary folios, remain positive in the two-outside-folio
sensitivity, and have max-three `p<=.05`.  Failure does not erase GDT068's
descriptive archive lead; it says that lead does not transfer to this fixed
legacy stratum.

Even a pass would identify only a reusable source-formal behavior class.  No
descriptor is a gloss, and no semantic class, role, word, morpheme, POS,
sound, language, plaintext, meaning, or translation is assigned.  No `f84*`
row may be retained, parsed, joined, or scored, and no new f84 access is
authorized.
