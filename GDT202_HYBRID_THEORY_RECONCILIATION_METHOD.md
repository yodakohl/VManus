# GDT202 — hybrid-theory prediction reconciliation

## Purpose

GDT202 is a retrospective reconciliation checkpoint.  It asks which parts of
the exposed GDT181 hybrid technical-compiler theory remain live after
GDT182--GDT201.  It does not fit a new decoder, search for another local
gloss, or reinterpret a failed prediction.

The experiment reads only published result JSON files plus GDT181's prediction
and lexicon tables.  It reads no transcription table, manuscript image, or
sealed target.  f84r is not accessed.

## Fixed rules

1. Preserve each GDT181 prediction verbatim.
2. Distinguish a successful *negative* prediction from a translation-bearing
   success.  Demonstrating that a simple alphabetic decoder fails supports a
   layered architecture but translates nothing.
3. `NO_HOMOLOG_FOUND` and `UNTESTED_NO_CAPACITY` are not successes or
   falsifications.
4. A page-local semantic rule is withdrawn from the active decoder if its
   selecting feature is not unique and no fixed transfer or readable homolog
   succeeds.
5. Structural compiler labels remain formal.  Withdrawing a semantic gloss
   does not withdraw reproducible line/field/wrapper/PAGE_HOST/right/DY/B3
   structure.

## Decision

The local f57/f77 semantic decoder remains active only if at least one frozen
prediction yields a transferable semantic endpoint and its page-local feature
selection survives the later multiplicity/global-competition audits.

Otherwise use:

`HYBRID_COMPILER_ARCHITECTURE_RETAINED_F57_F77_SEMANTIC_DECODER_WITHDRAWN`

This status preserves an anonymous page-conditioned technical compiler as the
leading abductive architecture while resetting active translation coverage to
zero source words, zero plaintext clauses, and zero licensed semantic state
assignments.
