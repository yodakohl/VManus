# GDT395 independent validator review

Date: 2026-08-20
Final disposition: **GO**

## Audit scope

This was a static, pre-oracle review of `VALIDATION_DESIGN.md`,
`src/validate_identifiability.py`, `src/freeze_blind_claims.py`, and
`src/validate_blind_claims.py`. No corpus, claim, oracle, decoder, generator,
scorer output, Voynich/f84 material, or project history was inspected. Runtime
checks were limited to `py_compile` and the validator's fabricated self-test.

## Initial HOLD defects and repairs

1. **Claim-binding shape mismatch.** The first validator required
   `freeze["bindings"]` to contain only the three claim roles, while the V2
   freezer correctly emitted those roles plus `implementation`. The repaired
   validator now requires exactly
   `{authentic_event_claims, pair_event_claims, world_claims, implementation}`
   and returns only the three disjoint claim-role lists for claim
   authentication.
2. **Implementation-binding lookup mismatch.** The first validator searched
   only top-level implementation containers, but the V2 freeze stores hashes
   at `bindings.implementation.hashes`. The repaired lookup derives the
   canonical experiment-relative key (including the exact
   `artifacts/gdt395_corpus_manifest.tsv` key), searches the nested
   `bindings["implementation"]` container, and requires exactly one matching
   current SHA-256. A fabricated nested-freeze case now exercises both repairs
   in the built-in self-test.

## Final GO checks

- The freezer binds both `VALIDATION_DESIGN.md` and
  `src/validate_identifiability.py`; blind-claims validation independently
  requires the exact implementation set and rehashes every member.
- Claims freeze and claims validation content, status, checks, seals, and their
  single freeze binding are authenticated before claim files. All bound claim
  hashes, schemas, panel identities, and event sets are then authenticated
  before manifest or oracle access.
- The implementation-bound corpus manifest must have the exact 200-row,
  eight-column W01--W10 by seed 00--19 matrix and canonical oracle names.
  Oracle selection is exactly the 50 unique held files for seeds 15--19;
  training-oracle files are never opened.
- Repository and oracle paths reject absolute labels, traversal, escape, and
  symlink file targets. Failures expose stable gate codes rather than paths,
  event identifiers, or oracle values.
- The validator independently recomputes the seven narrowly qualified
  clustering partitions, preserves all ten authentic interface HOLDs and all
  pair HOLDs, excludes singleton truth entities from entity-reuse scoring,
  applies the frozen seed/decoder/world and 2-Sol/3-Luna rules, and reproduces
  the exact 3,125-sample W10 diagnostic. Confirmatory promotion remains
  disabled.
- Scorer artifacts are checked by exact aggregate schemas, keys, row sets, and
  values. The one-shot validation artifact contains only stable hashes,
  aggregate row counts, Boolean checks, and total oracle rows read; it cannot
  contain event rows, oracle labels or values, visible text, joined records, or
  local paths.
- `py_compile`: **PASS**. Fabricated `--self-test`: **PASS**.

## Audited byte identities

- `VALIDATION_DESIGN.md` — SHA-256
  `3142cbaedc91ef851bf9cf30f608bbf61df353abc9721c71d6f847635f454cdf`
- `src/validate_identifiability.py` — SHA-256
  `cc68516cb7cdd7b296c71b92276bfca2a099f611e9dfe0528f76c7e238bc22ec`
- `src/freeze_blind_claims.py` — SHA-256
  `61fd8ad9d3f97b46b88c7a6fd469309a0dec3fcde64a27cf0b34d2cb923845cc`
- `src/validate_blind_claims.py` — SHA-256
  `3e35ab85402ec97d108eb2fd8ef170a621db41981238d73bc27d4d6a41fa7757`
