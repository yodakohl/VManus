# GDT1084 — four source-native repeated-plant queries

Registered before any f18v/f19r/f23r/f48v target-prose read in this pass.

## Research decision and budget

SNPL001 established four source-described same-plant Herbal↔pharmaceutical
drawing pairs and score-blind source-STA motif capacity. GDT352 and FPR001
already fail exact-surface/parsed-root variants; it is unknown whether the
original source-STA member sequences retain a cross-register signal. A pass
would nominate, but not translate, one or more manuscript-internal reusable
referent carriers for contextual work. A failure closes this specific four-pair
motif route. Minimum adequate test: four fixed labels against four complete
Herbal pages and all 24 assignments. Wall budget 90 minutes, including
preparation, implementation, validation, and publication; stop expansion then.

## Frozen relations and prior exposure

Use SNPL001's public-catalogue/manual old-to-current bindings, in this order:

| Label | Herbal page | Source ownership |
|---|---|---|
| f89v2.6 | f48v | next to target, partly under neighbor: ambiguous |
| f102r2.21 | f18v | explicit plant position |
| f102r2.22 | f23r | explicit plant position |
| f102v1.17 | f19r | explicit plant position |

These pages and labels were already available to the project. SNPL001's
score-blind capacity pass did not open these four target-page prose rows.
Historical project exposure removes any claim of independent holdout. f84/f84r
remain sealed; no reserve page is opened.

## Input boundary and scoring

Use the SHA-bound `source_sta_family_consensus_groups.tsv` from SNPL001
(SHA256 `a202d93498e8a350a5d7e0ca46e831dcc37ea5c0182dc404d63cb797a98b1225`).
Read only the four target pages through `vmanus-exp query-tsv` with selector
`page`, four exact `--allow` values, explicit output columns, and
`--forbid-prefix f84`. Keep only section H, `CONFIRMED_PROSE`,
`strict_zero_alternative=1`. The label sequences and all motif document
frequencies come unchanged from the already published SNPL001 capacity JSON.
ZL3b is primary; IT2a/RF1b are alternate readings of the same ink.

For each label and reader use its *preexisting* distinct contiguous 4/5-code
motifs. For a target page, score each motif present in any admissible prose
group as `width * log(93/(df_A_hand1+1))`, and take the maximum, or zero if
none. `df_A_hand1` is SNPL001's count among 92 non-target A/hand-1 Herbal
pages. The assignment statistic is the sum of the four label→page maxima.
Enumerate all 24 bijections; ties count against the observed assignment.
No motif, label, or page may be dropped or manually repaired after scoring.
Also report all 16 label×page cells and each observed pair's best matching
motif. The ambiguous f89v2.6 pair remains included; a three-pair sensitivity
is descriptive only, with minimum permutation p=1/6.

## Fixed decision and ceiling

Call `FOUR_PAIR_FORMAL_SIGNAL` only if the observed mapping is the unique
maximum among 24 assignments in *each* reading, at least three of four own
pairs score above zero in *each* reading, and each own-pair positive is based
on a motif with background document frequency below 92. Otherwise call
`NO_FOUR_PAIR_FORMAL_SIGNAL`. The 24 assignments are a tiny internal control,
not a significance basis for the entire historical search. Either result is
limited to source-native formal recurrence; no plant name, lexeme, language,
sound, plaintext, or translation follows from it.
