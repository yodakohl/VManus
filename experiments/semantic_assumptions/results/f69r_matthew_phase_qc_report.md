# f69r / Matthew Paris 12-of-16 phase QC

Date: 2026-08-09
Decision: **PASS_STRONGER_SYSTEM_LAYOUT; EIGHT-WAY PHASE AMBIGUITY; NO KEY**

Direct human inspection of the public f69r scan confirms the catalogue's
four-class geometry: four blank cardinal axes, four green diagonal spokes,
and eight blue spokes flanking the cardinal axes. In a sixteen-position
coordinate this is `blank=0 mod 4`, `green=2 mod 4`, and `blue=odd`.

The Matthew Paris wind construction in British Library Cotton MS Nero D I
ff.185r-v has the complementary twelve-of-sixteen organization: four
principal positions, eight collateral positions, and four unused diagonal
positions. Mapping `principal -> green`, `collateral -> blue`, and
`unused -> blank` produces an exact class match after a 45-degree phase
change.

This does **not** orient f69r. Exhaustive enumeration finds eight of the 32
rotations/reflections give the same exact class match: offsets 2, 6, 10, and
14 in either handedness. The colored spokes also are not author-owned labels
for the separate sixteen outer text records. The already validated FDC001
nonconfirmation further rejects literal four-base parsed-root compounding in
those outer records at its frozen resolution.

Retain a sharpened **12+16 WIND/DIRECTION SYSTEM-FAMILY MATCH**. Do not
transfer North, East, South, West, any compound direction, any Matthew Paris
word, or any orientation to a Voynich locus. This result supplies no root,
lexeme, plaintext, language, or translation.

Reproduction:

```bash
./vpy experiments/semantic_assumptions/f69r_matthew_phase_qc/check_f69r_matthew_phase.py
./vpy experiments/semantic_assumptions/f69r_matthew_phase_qc/validate_f69r_matthew_phase.py
```
