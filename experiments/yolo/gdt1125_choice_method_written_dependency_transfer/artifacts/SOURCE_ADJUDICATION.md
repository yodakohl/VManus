# GDT1125 source summary adjudication

**The frozen validator assumed the wrong summary schema. The original registered source gate remains FAIL.** No validator, preparer, SPEC, packet, canonical TSV or original failure artifact was changed or rerun. This adjudication is explanatory evidence, not a replacement gate or semantic/scientific PASS.

The original [SOURCE_VALIDATION.json](SOURCE_VALIDATION.json) records `FAIL_SOURCE_REPRESENTATION` with exactly one error, `FORMAL_SUMMARY`. The failing check in [validate_source.py](../src/validate_source.py) compares whole dictionaries for exact equality. The frozen application preparer's six-field summary uses `unresolved_marked_or_nonlowercase_groups` and `new_rules_or_licenses`. The validator instead requires `marked_or_nonlowercase_unresolved_groups` and `new_rules_or_local_frames`, plus `eligible_exact_whole_types`, which the actual summary does not contain. Exact equality is therefore false irrespective of agreement in measured values.

## Independent value check

I recounted the existing scoped `APPLICATION_GROUPS.tsv`; its SHA256 `c277afa94e301e91ec2b50d28117943fc380be567fcd0f39dcb1085bd8cd9a69` exactly matches the original independently guarded query output and validation artifact. No new source query was needed. Counts came from canonical raw groups, literal separators and pure-lowercase eligibility, not prepared summary totals. No author/critic model contents, new images or decoder were opened/run.

| Frozen preparer field | Actual value | Independent/original validated value | Finding |
|---|---:|---:|---|
| `eligible_groups` | 614 | 614 | agrees |
| `unresolved_marked_or_nonlowercase_groups` | 32 | 32 | agrees; validator expects a different name |
| `hard_chunks` | 627 | 627 | agrees |
| `eligible_chunks` | 596 | 596 | agrees |
| `merges` | 64 | 64 from existing hash-pinned replay | agrees |
| `new_rules_or_licenses` | false | unchanged frozen functions/rules; no added local frame | supported; validator expects a different name |

The scoped canonical recount also confirms646 groups,20 loci,60 reader/locus cells and19 uncertain-small-space seams. The extra validator-requested eligible raw whole-type statistic is156. Its absence from the six-field summary does not imply any native group is missing. This statistic is not a new frequency-prior query or meaning constraint.

All frozen input checks in the original full validation matched. All614 eligible formal output records retain `NOT_FROZEN_FOR_NEW_INPUT`; the original validator reports exact group/chunk replay agreement. The two false-valued field names are not declared universal semantic synonyms; the common operational claim here is supported by unchanged hash-pinned application functions and existing exact replay, rather than by a renamed label alone.

## Invalidity and permitted limits

This is a **validator interface assumption error**, not an observed native-source/data error. The frozen code demanded discovery-style summary keys and an additional statistic while the frozen application preparer emitted its actual six-key interface. The original full validation reports no other discrepancy: all646 raw groups,18 canonical fields, native IDs/order, byte projection, raw seams, native boundaries/RF0/0 policy, pure formal group/chunk replay and FV/FW candidate scope flags agree. The independent canonical recount corroborates the measured totals.

The original registered source-gate result stays `FAIL_SOURCE_REPRESENTATION`. Mapping names in this explanatory table neither satisfies the original exact-dictionary check nor restores the registered experiment to PASS. No corrected summary, hidden alias, repaired code or replacement source result is supplied. The original failure and pinned preopening files must remain visible beside this adjudication.

Root may separately finish **diagnostic literal applications of the unchanged frozen models** on the conserved canonical inputs already opened. Such outputs must identify the failed registered source gate, retain all raw groups/unknown barriers and preserve the distinct scopes: FV current paragraphs only; FW previous+current complete windows. This diagnostic completion cannot donate previous FW text to FV, retrospectively repair either meaning model, claim scientific/semantic confirmation or reopen older failures. Internal consistency or a later diagnostic PASS would not supersede the original registered FAIL.

The application windows are previously project-exposed partial coverage on physical leaves75/104, not complete-leaf readings or independent holdouts. Independent confirmation and confirmed words remain **0**. Only this adjudication's [MD](SOURCE_ADJUDICATION.md) and [JSON](SOURCE_ADJUDICATION.json) were written; root owns further application decisions/publication and global records.
