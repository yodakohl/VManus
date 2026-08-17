# GDT277 — calibration of the frozen GDT276 residual-channel signature

## Question

Does the frozen GDT276 result—especially a held-folio advantage for
compiler-conditioned character form—diagnose abbreviation/language-like
payload, or can the same signature arise in a local codebook, compositional
technical notation, or hybrid shorthand?

GDT276 is immutable.  This experiment imports its scoring functions, five
world definitions, 256-bucket ceiling, priors, selector cost, and 64 matched
context controls without changing them.  No PAGE_HOST substring is searched
or selected.

## Frozen controls

Five ground-truth controls are fixed before scoring:

1. `ORDINARY_NATURAL_LANGUAGE`: expanded Nuremberg letter-book text.
2. `ABBREVIATION_HEAVY_MEDIEVAL`: the paired diplomatic Nuremberg text.
3. `ARBITRARY_LOCAL_CODEBOOK`: frozen GDT172 lexical System A.
4. `COMPOSITIONAL_TECHNICAL_NOTATION`: frozen GDT172 factorial System B.
5. `HYBRID_SHORTHAND`: frozen GDT173 human-grown irregular B2.

The two Nuremberg views use the GDT155 blind edge-operation parser with
inventories learned outside the held book.  The three synthetic controls use
the already-published `SURFACE_ONLY` GDT172/GDT173 observation-layer parses.
Oracle/expanded files establish the known control architecture and exact
reversibility; no oracle field is a predictor or target.

## Matched-capacity observation view

The primary comparison uses one shared, frozen subset of the f84-free GDT276
event scaffold.  It contains 4,476 group opportunities with exact PAGE_HOST
length quotas:

```text
L2=1731, L3=277, L4=791, L5=1003, L6=448,
L7=137, L8=60, L9=22, L10=7.
```

These are the component-wise minimum capacities across Voynich and all five
controls, fixed without running a GDT276 score.  Scaffold rows are selected by
a deterministic SHA256 order inside each length.  For each control, visible
occurrences of the required parsed-host length are selected in source order
and assigned to same-length scaffold opportunities.  Thus every primary panel
has identical host-length-by-position, page, physical-line, record, field,
closure-opportunity, and held-folio structure.  The control's surface-only
wrapper/edge parse and register remain attached to its occurrence.  Because
this overlay does not preserve native adjacency across different length
queues, sequential/HYBRID results are reported but are not used to diagnose
the primary character-plus-compiler signature.

Alphabet capacity is fixed at the GDT276 capacity: the 20 most frequent
visible control-host characters map deterministically by frequency then
Unicode tie-break to the 20 used Voynich host symbols; all other characters
map to `?`.  EOS is unchanged.  Mapping coverage and collisions are reported.
This is an opaque capacity normalization, not a phonetic or letter mapping.

## Frozen instrument and endpoint

Run all five unmodified GDT276 worlds and all 64 matched context permutations
on each matched panel.  The diagnostic signature is fixed as:

```text
ABBREVIATION_HEAVY_LANGUAGE has the lowest selector-paid held-folio MDL
AND it beats COMPRESSED_NATURAL_LANGUAGE
AND its matched-context saving is positive.
```

Report bits/group, bits/host-symbol, rank, folio wins, matched saving, and
lower-tail calibration value.  The primary conclusion is categorical: which
known control architectures exhibit the same signature as Voynich.  No
threshold is tuned and no composite score is created.

## Representation-leakage sensitivity

The published full-inventory representation is compared with a strict
leave-one-held-folio representation.

- Voynich: reconstruct the pre-O/OT host from the published event inventory;
  learn the O/OT licensing set without the held folio; reparse both training
  and held rows with that training-only set.
- Nuremberg: relearn the fixed GDT155 edge-operation inventory from matched
  training folios only and reparse visible surfaces.
- Synthetic A/B/B2: relearn the fixed GDT170 surface-operation inventory from
  matched training folios only and reparse visible surfaces.
- For every control, learn the 20-character capacity map from training folios
  only.

All scoring remains held-folio.  This sensitivity may change represented host
lengths; it is not rematched or repaired after seeing the result.  It tests
representation leakage, not a new world.

## Interpretation ceiling and seal

The calibration can establish only whether the operational GDT276 signature
is selective among these five known architectures.  It cannot identify a
language, notation, codebook, plaintext, meaning, or translation.  No f84
source is an input.  The only Voynich source is the already-published,
f84-free `gdt276_event_inventory.tsv`; no f84 row is opened, parsed, retained,
joined, or scored.
