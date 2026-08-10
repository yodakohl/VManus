# LRG008 target-blind calibration v3 parity-balance amendment

Status: `FROZEN_TARGET_BLIND_SYNTHETIC_V3`.

V2 is independently reconstructed and changes no target data. It recovers all
16 intended distributed worlds and rejects every negative world except
`ONE_PARITY` world 6. That leak has parity effects `.535` and `.204`, giving a
weaker/stronger ratio `.381`. Across all intended v2 worlds, the minimum ratio
is `.537`.

V3 adds exactly one gate:

`both parity effects > 0 and min(EVEN, ODD) / max(EVEN, ODD) >= .50`.

It reads the already hash-bound and cleanly reconstructed v2 world records,
adds this ratio and gate to each evaluation, and recomputes only per-world
passes, pass counts, top-level gates, status, and decision. It must not rerun,
alter, or reorder a score, rank, null, effect, seed, amplitude, quota,
threshold, world, digest, or existing gate.

V3 passes only with 0/64 null, 8/8 at both distributed strengths, 0/8 in all
nine negative families, exact preservation of every inherited numeric/digest
leaf, and all v2 integrity gates. A pass authorizes only a separately
registered, committed, hash-frozen one-time aggregate target. It supplies no
manuscript association, identifier, name, noun, owner, object, word, sound,
language, meaning, plaintext, or translation.
