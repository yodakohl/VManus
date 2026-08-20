# GDT395 interrupted V3 completion recovery

Status: `FROZEN_BEFORE_RECOVERY_EXECUTION`

The public V3 blind run was externally interrupted after all 2,100 held-event
claim files had been written. Forty-nine of fifty train-only world claims also
exist. The only missing scientific claim is:

`world_claims/W05/D01_MULTIVIEW_GRAPH/train_seeds_00_14.json`

The authoritative `blind_claim_manifest_all.tsv` was not written because V3
writes that manifest only after every job returns.

The recovery is deliberately narrower than a rerun:

1. `freeze_v3_interrupted_recovery.py` authenticates the exact 2,149-file
   prestate, proves that all event claims exist, proves that the one named
   world claim is the sole missing claim, and binds the recovery source.
2. `recover_v3_interrupted_completion.py` loads only W05 blind training seeds
   00--14, invokes the unchanged frozen D01 `classify_world` function, validates
   its frozen schema, writes the one missing JSON, then emits the exact
   2,150-row manifest from existing claim-file hashes.
3. `validate_v3_interrupted_completion.py` independently reconstructs the
   expected file matrix and verifies every manifest path/hash/count plus the
   recovery freeze/result hashes.

The recovery never opens a synthetic oracle, a Voynich source, or f84. It does
not change a decoder, split, representation, held-event claim, threshold, or
scoring rule. Any pre-existing claim-file hash change is a hard failure.

