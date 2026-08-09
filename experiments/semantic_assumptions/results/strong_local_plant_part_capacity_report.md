# Strong-local plant-part capacity audit

## Result

**STOP — no replicated, explicitly owned plant-part contrast.**

The source-only audit searched the existing human exact-locus atlas, without
opening interlinear strings, for unhedged exact-local `PLANT` rows containing a
root, leaf, flower, stem, or fruit term and at least one strong local relation.
It finds only eight rows on five pages:

| Term | Rows | Pages |
|---|---:|---:|
| root/tuber/bulb | 2 | 2 |
| leaf/foliage | 3 | 3 |
| flower/bloom | 2 | 1 |
| stem/stalk | 3 | 2 |
| fruit/berry/seed | 0 | 0 |

Terms overlap within rows. Five rows are editorial labels, but none has the
atlas relation `REL_EXPLICIT_ATTACHMENT`. Source-level review leaves only
`f2r.15` as a plausible label enclosed within a leaf. The two FLOWER hits refer
to the central flower-like geometry of the East rosette, not a botanical
flower label. The remaining label cases say that writing runs into a leaf,
stem, or root tip, including contact with a neighboring drawing; three further
rows are prose rather than labels. Contact or accidental overlap is not
semantic ownership.

Therefore the apparent five-page coverage does not provide even two replicated
owned part classes. No Voynich string was selected or scored, and absence of a
part term was never treated as a negative.

## Reproduction

Run:

```text
./vpy experiments/semantic_assumptions/strong_local_plant_parts/audit_strong_local_plant_part_capacity.py --output experiments/semantic_assumptions/results/strong_local_plant_part_capacity.json
```

The script binds the source hash and asserts every reported count.
