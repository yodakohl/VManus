# GDT774 design registry

Date: 2026-09-03.

This file records the transfer contract used for the final executable pass.
The 376-position census, direct-signature counts, and GDT773 calibration
outcomes were already known when the experiment was designed. The structural
nulls were added during the same exploratory round after the register pattern
was noticed; they are labelled diagnostics and do not receive lexical credit.

## Fixed material

- exactly the 376 reader-exact `ol` rows in GDT769's published target atlas;
- the GDT769 F14/F15 and direct-signature fields already attached to those rows;
- all seventeen occurrence-specific edges reconstructed from GDT760/GDT762,
  with GDT763 slot provenance;
- the fifteen fixed GDT773 context outputs;
- a guarded crosswalk to the old GDT683 renderer;
- the 24 authored contrast contexts in
  `src/MANUAL_24_CONTEXT_AUDIT_SPECS.tsv`.

No new page may enter this round. `f84` and `f84r` are forbidden. Mixed-source
rows may be queried only after the safe GDT769 page-selector set is known, with
explicit output columns.

## Fixed automatic precedence

1. amount left of `ol`, not line-final → `Ansatz:`;
2. `ol` left of amount → `Menge:`;
3. direct PROCESS/`oly` right → `und dann`;
4. direct CLOSE left → `;`;
5. direct CLOSE right → nominal veto;
6. F15 and F14 state bridge → `und`;
7. otherwise → `Ansatz-/Zubereitungsposten`.

The automatic policy may not consult GDT773 case IDs. The hybrid must copy all
fifteen fixed GDT773 outputs first and use the same automatic policy elsewhere.
An automatic `:` is disallowed because no case-independent trigger has been
identified. Line-final position, line-first position, F14 alone, PROCESS-left,
or adjacent `ol` alone must not create punctuation.

The inventory-derived mechanical expectations before the final builder run
are ten `Ansatz:`, five `Menge:`, four `und dann`, three `;`, 27 `und`, and 327
nominal fallbacks. The automatic calibration replay is expected to match 9/15;
the hybrid must match 15/15. A different result requires an explicit rule or
source correction, not a silent count edit.

## Structural diagnostics

The final diagnostic contract uses 20,000 iterations with fixed seeds:

- N01 folio-stratified exact-slot position/repetition null, seed 776;
- N02 folio+line-position-stratified neighbor-diversity null, seed 778;
- N03 section+language+hand-stratified repetition null, seed 774.

Every result is published with observed value, null mean, 2.5/50/97.5%
quantiles, both add-one empirical tails, algorithm text, and the guarded slot
count. These diagnostics may motivate a new partition but may not add a German
word to this round.

## Outcome interpretation

- contextual automatic output: a rule above emits anything other than the
  nominal fallback;
- nominal automatic output: the close-right veto or generic fallback emits the
  whole-form noun;
- calibration transfer: exact equality between automatic and fixed GDT773
  output at the same locus and ordinal;
- practical hybrid: preserved GDT773 output at its fifteen positions plus
  automatic output elsewhere.

The 24 contrast rows are an implementation/readability audit with zero
independent score credit. Alternate-reader exactness establishes the written
boundary only and does not validate meaning.

## Claim ceiling

The strongest allowed conclusion is a mixed complete-whole record-head/operator
working model, with a measured contextual coverage rate and an explicit
fallback population. No output is a recovered translation. No liquid,
substance, unit, operation, language, cipher, lexical class, EVA component, or
plaintext clause may be confirmed.
