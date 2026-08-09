# Source-native opening-to-closing coupling one-time target test

Status before execution: **REGISTERED_SINGLE_RUN**

## Authorization and frozen inputs

This target is authorized only by the unchanged model in
`SOURCE_NATIVE_EDGE_COUPLING_TEST_SPEC.md` and its independently reconstructed
target-free synthetic preflight.

- `results/source_native_edge_coupling_masked.tsv`, SHA-256
  `db78519f12283f6ac2ae30e0e8898c769f1491f8d48dae1733b5de703154e82c`
- `results/source_native_edge_coupling_capacity_validation.json`, SHA-256
  `889f55a0763703c25d9589d1c656e960bc9ff264e20e72deed1a85b6c3af69a5`
- `source_native_edge_coupling_core.py`, SHA-256
  `c7ab314c49b9e81c4eafe5d5056fa46dfc68f5dcf63c8933504861e26d267349`
- `SOURCE_NATIVE_EDGE_COUPLING_TEST_SPEC.md`, SHA-256
  `634eff5ddf6e3e823728d3aa40e4fd0465b5743ba003216c69692f21ef3f466c`
- `results/source_native_edge_coupling_preflight.json`, SHA-256
  `901eea3a922c866d5c6705ac284cfc3c9406580853c0bb624216bf40e8587d61`
- `results/source_native_edge_coupling_preflight_validation.json`, SHA-256
  `7ec2b481b320ead5fb847f3faf74877c25e59536279b525e071e7f9d3e9c3b2c`
- `results/source_sta_family_consensus_groups.tsv`, SHA-256
  `a202d93498e8a350a5d7e0ca46e831dcc37ea5c0182dc404d63cb797a98b1225`
- `results/source_sta_family_consensus_validation.json`, SHA-256
  `fcb6a53461b4f9df36f34161ed1d42087f4395988bea0d71f74a7dd635b68b76`

The result and report must be absent before invocation and are installed with
paired no-clobber semantics. NumPy and BLAS thread counts are pinned to one
before import. No alternate model, threshold, subset, or target analysis is
permitted.

## Single target join

Join every frozen masked row to exactly one source row by
`consensus_group_id`. Require equal unit identity and metadata, strict
zero-alternative confirmed-prose scope, a source family surface of length at
least three drawn only from the official 24-family alphabet, and exact equality
of `source family_surface[:-1] + "#"` to `masked_family_surface`. Encode only
the final family as its fixed alphabet index. Require exactly 19,203 joined
rows, 14,955 eligible rows, and 94 physical folios.

Score once with the frozen leave-physical-folio-out Dirichlet proper-score
model and gates. Store only the aggregate 24-family count vector, the aggregate
score summary, gate decisions, bindings, and access counters. Do not store
event-level outcomes or complete family surfaces.

## Decision and ceiling

- If every frozen gate passes, retain a transferable opening-conditioned
  closing-family selection relation beyond second family, penultimate family,
  capped length, locus position, Currier, and physical folio.
- Otherwise close this exact cell/model/threshold test without retuning.

A pass is compatible with edge agreement, paired affixal selection, or
templatic morphology; it does not choose among them. Neither result identifies
an affix, circumfix, operator, spoken direction, sound, word, language, cipher
operation, meaning, plaintext, or translation.
