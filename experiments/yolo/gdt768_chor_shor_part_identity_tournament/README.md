# GDT768 — chor/shor part-identity tournament

GDT768 produces a concrete twelve-line working reader and tests what the two
complete words `chor` and `shor` can consistently be allowed to mean within
it. The winning result is a relation, not a deciphered word pair:

> `chor` and `shor` behave like parallel nominal plant-part or content wholes;
> the direction flower versus seed/fruit remains unresolved.

The clearest line is `f17r.5`:

```text
EVA: ychekchy cthy chor shor cphor cphaldy dair cthey qody
Reader: Ansatzposten: Blattgut; Blütenstand; Fruchtstand; Dosisposten;
        fertiger Anteil I; Anteil II; Droge Form I; fertige Zubereitung.
```

This is an explicit working rendering. `Blütenstand` and `Fruchtstand` are
replaceable concrete defaults, not confirmed translations. Their reversal is
still equally compatible with the evidence.

## Result at a glance

| rank | model | score | directional minimum |
|---:|---|---:|---|
| 1 | M02: `chor` flower; `shor` seed/fruit | 0.820437 | failed; shared two-part relation supported |
| 1 | M03: reverse direction | 0.820437 | failed; shared two-part relation supported |
| 3 | M01: dry/moist form of one reproductive part | 0.644178 | failed |
| 4 | M04: general herb plus reproductive part | 0.631987 | failed |
| 5 | M05: unrelated learned roles | 0.132523 | failed |

The M01 state contrast does not survive family ablation. At D1, `shor` changes
from DRY/MOIST `8/12` at ED0 to `8/5` at ED1 and `7/2` at ED2. In the exact
state-whole deck, `shol` disappears at ED1, `sheol` at ED2, and only
`qokchol` remains at ED2 (`chor` 2 contacts, `shor` 1). Conversely, the
target-excluding ED2 cofields remain highly similar: cosine 0.966080 at D1,
0.984115 at R3, and 0.990899 at line scope.

## Coverage

- 404 anchor occurrences on 135 pages and 350 loci;
- 33 multi-anchor lines on 26 pages;
- six complete-word dictionary entries;
- 94 tokens in twelve complete line readers;
- 54 target-context exposures to GDT754 source-composed forms blocked before
  scoring;
- no new pages or images; `f84` and `f84r` untouched.

The validator passes **53,504 checks** with byte replay of all twelve declared
builder outputs.

## Run

```bash
python3 experiments/yolo/gdt768_chor_shor_part_identity_tournament/src/run.py
python3 experiments/yolo/gdt768_chor_shor_part_identity_tournament/src/validate.py
```

Start with [REPORT.md](REPORT.md) for the result and
[artifacts/HISTORICAL_PART_REGISTER_READER.md](artifacts/HISTORICAL_PART_REGISTER_READER.md)
for all twelve concrete readings. [METHOD.md](METHOD.md) defines the scoring;
[PREREGISTRATION.md](PREREGISTRATION.md) records the fixed competitors and
replacement rules; [artifacts/README.md](artifacts/README.md) maps every output.

Confirmed lexemes, component values, and plaintext clauses: **0**.
