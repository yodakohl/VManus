# GDT278 — frozen magnitude calibration of the GDT277 residual

## Purpose

GDT277 showed that the *sign and rank* of the GDT276 compiler-conditioned
character-form result are not architecture-specific.  GDT278 asks the one
question that GDT277 did not preregister: can a known ground-truth system
reproduce the **magnitude** of the Voynich compiler-conditioned saving?

GDT277 is byte-frozen.  GDT278 does not revive HPR1 semantics, search Voynich
substrings, change the five GDT276 worlds, or assign meanings.  The experiment
is an instrument calibration over visible surface forms and known control
architectures.

This document and `gdt278_magnitude_design.json` are frozen before any expanded
control is admitted to or scored by the GDT276 instrument.

## Frozen magnitude endpoint

For the `ABBREVIATION_HEAVY_LANGUAGE` operational world only, let

```text
S = mean(bits in the 64 matched context-permutation worlds)
    - observed held-folio bits
S_event = S / number of scored group events
Z = S / population-SD(bits in the 64 null worlds)
```

Positive values mean that compiler context saves character-form codelength.
`S_event` is the primary normalized magnitude; `Z` is the mandatory
null-normalized companion.  The null is exactly the GDT276/GDT277 matched
context-bucket permutation.  No different world, substring, host class, or
semantic field may be selected after seeing a control.

The published GDT277 matched Voynich reference is fixed at 4,476 events,
`S=1607.821831893496` bits, `S_event=0.359209524551719` bits/event, and
`Z=21.073691854316383`.  The published native Voynich reference is fixed at
8,448 events, `S=3080.522234827527` bits,
`S_event=0.364645150902880` bits/event, and `Z=32.157409138546974`.
These values are exposed reference coordinates, not newly estimated evidence.

## Frozen comparison rule

A control reproduces the Voynich magnitude in a view only if **both** its
`S_event` and its `Z` equal or exceed the corresponding frozen Voynich value.
The ratios to Voynich and ranks are reported continuously; there is no
post-hoc tolerance band or composite score.  A robust reproduction must meet
both coordinates in both powered views.

The final architectural decision is mechanical:

- if any known non-language/code/notation architecture robustly reproduces
  the magnitude, the magnitude is not language-specific;
- if a control reproduces it only in one view, report order/matching
  sensitivity;
- if no admitted control reproduces it, Voynich is outside this *current*
  ground-truth envelope, not thereby identified as a language or cipher.

## Two fixed observation views

### Length-matched overlay (primary)

Reuse the exact GDT277 4,476-event Voynich scaffold and exact host-length
quotas.  Each control supplies source-order occurrences through exact parsed
host-length queues.  Page, line, record, field, closure opportunities, and
20-symbol capacity are therefore the same as GDT277.  Native adjacency across
different length queues is broken and is not interpreted in this view.

### Native-order sensitivity

Retain each control's native folio/line/event order and native layout rather
than assigning it to the Voynich scaffold.  Use every eligible event when the
panel has fewer than 8,448 events.  For larger panels, select source units by
a fixed SHA-256 ordering and retain native order within selected units until
8,448 events are reached; a final source unit may be deterministically
truncated.  Controls below 80% of 8,448 events are reported but cannot satisfy
the native reproduction gate.  Event count is always reported because null-z
is sample-size dependent.

The same 20-symbol capacity rule and the same 64 null worlds apply.  This view
is a sensitivity to authentic ordering/layout, not a replacement for matched
opportunity control.

## Representation safety

Published full-inventory parses are integrity anchors.  The primary control
magnitudes are also recomputed with representation learning strictly inside
each training fold:

- operation/edge inventories are learned without the held control folio;
- the 20-character map is learned without the held control folio;
- training and held events are reparsed with that training-only inventory;
- observed and all 64 null scores use those fold-local representations.

The Voynich sensitivity uses only the published f84-free GDT276 inventory and
relearns the licensed O/OT host representation without the held folio.  It
does not inspect source transcription tables.  A magnitude claim must report
both the frozen published-representation anchor and the LOFO-safe result.

## Control admission

After this endpoint freeze, admit diverse, already-published ground-truth
systems under a separately hash-bound source manifest: real natural language,
real diplomatic abbreviation/shorthand, nomenclator/codebook controls,
technical notation, hybrids, and synthetic matched-capacity variants.  A
control must have visible surfaces, physical or synthetic source units/folds,
an architecture label established independently of the GDT278 score, and
enough provenance to reproduce selection.  Oracle/expanded meanings may
establish the control label but may not be predictors or targets.

Control inclusion, parsing, alphabet mapping, native sampling, and exclusion
must be logged.  Existing GDT277 controls remain fixed reference rows.

## Limits and seal

The strongest possible result localizes a compression magnitude among known
architectures.  It cannot establish a language, word, morpheme, meaning,
plaintext, translation, or historical identity.  HPR1 semantic fields and
Voynich substring predicates are prohibited.

No f84 source is an input.  The only Voynich data permitted are the already
published f84-free GDT276/GDT277 artifacts bound by the freeze manifest.  No
f84 row may be opened, parsed, retained, joined, or scored.
