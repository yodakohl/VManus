# GDT396 — repaired synthetic identifiability benchmark with Voynich-constrained surface channel

Status: `REGISTERED_UNSCORED`

Synthetic calibration only. GDT396 reuses the ten byte-frozen GDT395 hidden
world generators and compares two observation channels over identical hidden
events:

- `FREE_SURFACE`: the original GDT395 visible rendering;
- `VOYNICH_SURFACE`: a random world-specific recoding through the repository's
  frozen 24-position official STA family inventory, represented as raw atom
  bytes rather than EVA or manuscript-derived strings.

No Voynich corpus is an input. Both `f84` and `f84r` are forbidden. See
`METHOD.md` and `experiment.json`.
