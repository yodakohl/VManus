# GDT304 — wrapper field-entry hypothesis generation

## Status and provenance

This is an explicitly **post-hoc mechanistic decomposition** of the three
GDT303-selected operations.  During route selection, all listed endpoint
deltas were inspected.  Therefore no p-value in GDT304 can confirm the
hypothesis; the output freezes a concrete formal interpretation and future
predictions.

## Fixed operations and endpoints

Use the exact GDT303 pairs for `wrapper:ch>s`, `wrapper:d>s`, and
`wrapper:NONE>q`.  For each operation, average pair deltas equally within host
and then equally across hosts for:

- physical line `FIRST` and `LAST`;
- HPR2 field `FIRST` and `LAST`;
- record ordinal 1 and field ordinal 1;
- line close and paragraph close.

No spelling, PAGE_HOST substring, or semantic annotation enters the analysis.
HPR2 field position is parser-dependent; physical line position is the
independent mechanical anchor.

## Hypothesis-generation rule

Generate `FIELD_ENTRY_WRAPPER_HYPOTHESIS` when all three operations increase
field-first rate, `NONE→q` decreases field-last rate, and none has an absolute
record-ordinal-1 delta above 0.10.  Record the exact direction counts and every
counterexample.  Freeze the following predictions for a genuinely new panel:

1. a q-wrapped member of a matched same-host pair will be more field-initial
   and less field-final than its neutral counterpart;
2. an s-wrapped member will be more field-initial than matched ch- and
   d-wrapped counterparts;
3. those operations will not consistently select record ordinal 1.

## Claim ceiling

At most this proposes a formal field-entry rendering class.  It does not name
a grammatical category, part of speech, discourse meaning, morpheme, sound,
language, plaintext, or translation.  No f84 row may be opened, parsed,
retained, joined, or scored.
