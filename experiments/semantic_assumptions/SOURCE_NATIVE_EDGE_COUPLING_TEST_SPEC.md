# Source-native opening-to-closing coupling test

Status: **REGISTERED_TARGET_UNOPENED**

## Model and target

Use the frozen 19,203-row masked panel. The target is the last STA family from
the 24-family official alphabet `ABCDEFGHJKLMNPQRSTUVWXYZ`.

For each physical folio, train on every other folio. The baseline categorical
cell is the frozen

`(second family, penultimate family, min(length,8), locus position, Currier)`.

The full cell adds the first family. With symmetric Dirichlet `alpha=0.5`, score
each of the 14,955 prespecified eligible held rows by

`log P(last | full cell) - log P(last | baseline cell)`.

Average rows equally within each physical folio and physical folios equally.
Compute the exact one-sided sign probability over positive folio effects,
treating zero as nonpositive. Also compute Currier A and B folio summaries,
leave-one-folio-out effects, and the maximum absolute folio-contribution
fraction.

The target passes only if:

- all 14,955 rows and 94 folios score;
- equal-folio gain is at least 0.02 nat/row;
- at least 65/94 folios are positive and exact sign `p<=0.01`;
- minimum leave-one-folio-out gain is positive and maximum absolute folio
  contribution is at most 0.08;
- Currier A and B each have gain at least 0.01, positive minimum deletion, and
  at least 60% positive folios.

## Target-free calibration

Before opening any final family, the preflight must use only:

- `results/source_native_edge_coupling_masked.tsv`, SHA-256
  `db78519f12283f6ac2ae30e0e8898c769f1491f8d48dae1733b5de703154e82c`;
- `results/source_native_edge_coupling_capacity_validation.json`, SHA-256
  `889f55a0763703c25d9589d1c656e960bc9ff264e20e72deed1a85b6c3af69a5`;
- `source_native_edge_coupling_core.py`, SHA-256
  `c7ab314c49b9e81c4eafe5d5056fa46dfc68f5dcf63c8933504861e26d267349`;
- this specification and the runner.

The fixed grid contains 64 opening-independent `NULL` worlds, eight
manuscript-wide opening-coupled worlds with coupling probability 0.2, eight
one-folio-only worlds at 0.8, and eight worlds with independent folio-specific
opening maps at 0.8. The preflight requires at most 3/64 null passes, at least
7/8 global-coupling passes, zero one-folio passes, zero folio-random passes,
exact invariance under a fixed permutation of all 24 outcome labels, capacity,
finite-score, schema/mutation, source-isolation, and target-absence gates. Use
32 forked workers with NumPy/BLAS threads pinned to one.

## Decision and ceiling

Only a validated preflight authorizes one target join by exact
`consensus_group_id`, exact prefix remasking, and no event-level outcome output.
A pass establishes a transferable opening-conditioned closing-family relation
beyond immediate core edges, length, locus position, Currier, and folio. It is
compatible with edge agreement, paired affixal selection, or templatic
morphology, but does not choose among them.

A failure closes this exact cell/model/threshold test without retuning. Neither
result identifies an affix, circumfix, operator, spoken direction, sound, word,
language, cipher operation, meaning, plaintext, or translation.
