# GDT1058 — thermal direction splits by text scope

Decision: **demote the global `k=hot, t=cold` default to unresolved**. With the
unchanged four-category distribution from GDT1057, all three `ALL_SAFE_NO_F1R`
cells select `k=hot` among the two fixed `ch=dry` thermal assignments, whereas
all six Herbal cells select `t=hot`. In each of the nine cells the winning
thermal assignment also ranks first among all eight inherited assignments.
The three modes (exact, q-prefix, substring) and the two Herbal scopes are
nested/reused target data, not nine independent confirmations.

| Scope | Exact winner, TV versus rival | q-prefix winner, TV versus rival | Substring winner, TV versus rival |
|---|---|---|---|
| ALL_SAFE_NO_F1R | k-hot .162152 versus t-hot .263811 | k-hot .152164 versus .280358 | k-hot .194457 versus .230071 |
| HERBAL_A | t-hot .147449 versus k-hot .277079 | t-hot .181258 versus .259239 | t-hot .200947 versus .223581 |
| HERBAL_ALL | t-hot .174449 versus k-hot .250079 | t-hot .214210 versus .221230 | t-hot .207153 versus .217375 |

The `HERBAL_ALL` q-prefix and substring margins (.007020 and .010222) are
small. GDT1057's source has 210 qualifying numbered entries, with 82 printed
positions unclassified under its fixed window and literal numbering rule.
Those missing quality pairs can change the four-way source distribution; no
robust thermal sign follows from this rescore. The retained dry-majority lower
bound is a separate result, not a fix for the temperature ambiguity.

This is a transparent post hoc diagnostic on already inspected inputs, not
independent evidence that either `k` or `t` means hot. It also does not show
that a Voynich temperature code changes meaning by section: genre composition,
word function and selection can produce the split. The only justified update
is to stop exporting one global temperature polarity from corpus frequency.
GDT623's original report and GDT1057's registered result remain unchanged.
Confirmed translated words: **0**. No new manuscript selectors or reserved
material were opened. All 72 scores and nine decisions are retained; the
validator rechecks all input hashes, row distances and completeness (106 checks).
