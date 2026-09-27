# GDT1057 report — whole-source quality direction

Decision: **retain the provisional dry-majority direction**, but do not assign
a meaning to any Voynich word. The audited 1415 comparator has 177 dry and
33 moist entries among 210 qualifying numbered entries. Even if all 82
unclassified positions across printed numbers 1–292 were moist, dry remains
177/292 (60.6%). This is a historical control finding, not manuscript meaning.

The frozen GDT623 target has 168/192 exact `qo(k|t)(ch|sh)(y|ey)` tokens on
the `ch` side. Among the eight inherited assignments, the quality-grid
orientation `KT_THERMAL__K_HOT__CH_DRY` ranks first by smoothed total
variation (0.162152); its temperature-reversed partner ranks second
(0.263811). The two thermal-axis `CH_MOIST` assignments score 0.710757.
The historical corpus is 150/210 hot (71.4%) whereas the target's first
orientation is 106/192 hot (55.2%), so even its best fit is imperfect.

The source is UCC CELT's Part IV editorial English translation of Tadhg Ó
Cuinn's 1415 *An Irish Materia Medica*. The fixed parser found 286 distinct
numbered starts spanning printed 1–292. Six numbers (7, 20, 160, 181, 220,
244) lack the literal numbered-start pattern; at least no. 7 appears as a
real unnumbered entry. This is therefore a complete census of detected
numbered starts, **not** of every underlying drug. The first-320-character
rule found 213 automatic pairs. Native audit accepted 210 and excluded
ordinals 31 (qualities attributed to different authorities), 250 (general
styptic-herb class), and 276 (patient condition plus remedy list). Accepted
counts: hot/dry 125, cold/dry 52, hot/moist 25, cold/moist 8. The fixed
window leaves 73 numbered starts without a pair; no post-result extension
was made. All rows and decisions are retained in the artifacts.

The dry-majority conclusion survives the maximal missing-as-moist bound.
The exact eight-way top rank is less robust: the 82 unclassified positions
could change the four-way distribution and the orientation ordering. Their
qualities are not observed, so the present first rank is a property of the
fixed eligible subset, not of a complete source census.
The source is one work and its English translation; the 192 target tokens
include repeated forms and do not represent independent plants. Source and
Voynich material need not share category frequencies. The previously known
Herbal-only temperature reversal and broader quality-grid rivals remain.

`src/validate.py` independently rechecks the raw source and frozen GDT623
hashes, every opening hash and automatic class, the complete manual decision
set, all category totals, and all eight distances; 891 checks pass. No f84,
f84r or reserved text was used. **Confirmed translated words: 0.** The next
research decision still requires an independently bound manuscript referent
or content contrast; this frequency control cannot supply one.
