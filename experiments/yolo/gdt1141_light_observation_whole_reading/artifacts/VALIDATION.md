# GDT1141 independent validation

**Validator: PASS_ACCOUNTING_ONLY. Experiment decision: `MISSING_CORE_DESIGN`.**

The validator independently replayed the registered selector-first projection from the pinned BB account. All nine source pins and all four final author-freeze hashes were checked. The projection matches byte-for-byte: 288 native positions total, including 97 IT2a primary positions (19 ring + 78 prose); ZL3b has 95 and RF1b has 96. All 58 ring and 230 prose positions, exact forms, separators, and uncertainty/entity metadata remain in the guarded projection.

The freeze correctly records two attempted cores, no accepted core, no Stage2 release, and `MISSING_CORE_DESIGN`. Proposal 01 remains byte-identical to its frozen proposal and its gate records `NOT_ACCEPTED_FOR_STAGE2`. Candidate 02 is hash-frozen but unaccepted. Its author clarification records the missing LIGHT_OF-to-scalar projection, the undefined consecutive-DAL/CHDY overlap, and that DALG has a reference record plus a LIGHT_OF noun rather than two observation records. The validator checks frozen bytes and declared types/bindings; the CHDY-overlap conclusion is the author's clarification, not an independent semantic proof.

The complete 97-position author table was not authored. Actual two-observation dependency interventions were `NOT_RUN_NO_CAPACITY`; this validation did not manufacture a baseline or perturb semantic outputs. Accordingly, `PASS_ACCOUNTING_ONLY` verifies the correct recorded stop and source/core bookkeeping; `FAIL_MISSING_CORE_DESIGN` remains the core gate outcome. This is not a manuscript contradiction, a rejection of lunar content, a semantic test, or meaning confirmation.

See `VALIDATION.json` for exact pin checks, per-reader/per-part counts, gate facts, and all accounting assertions.
