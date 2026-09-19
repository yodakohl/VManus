# GDT977: leaf and breadth consistency does not select a reading

**Decision: park serial one-atom projection additions.** The registered shared
LEAF/BROAD extension retains **8,986 of 8,990 old code/page candidates (99.9555%)**.
Exactly four are contradicted; none is a timeout. The survivors still contain
1,318 of the 1,320 name-code classes, all 52 possible IRIS values and all 138
possible XIPHION values. No individual name value is eliminated. No translated
word or preferred reading follows.

This is an actual four-atom consequence of unchanged GDT963, evaluated for every
GDT976 candidate. The source meanings label conditional model variables; they
are not identified meanings of Voynich strings. The original GDT963 UNKNOWN
and GDT976 counts remain unchanged.

## Registered predictions and complete results

Registration `e09eeaa80` was publicly pushed before execution on 19 September
2026. [CASE_PREDICTIONS.tsv](artifacts/CASE_PREDICTIONS.tsv) fixes all 8,990 old
candidate IDs, their names/pages and four required whole-string patterns before
fitting. [CANDIDATE_RESULTS.tsv](artifacts/CANDIDATE_RESULTS.tsv) reports every
case, a saved LEAF/BROAD witness for each success, all of that witness's Acorus
and Meum supports, and the exact factored count of distinct-leaf completions.
[CASES.json.gz](artifacts/CASES.json.gz) adds all positions and every negative
search-tree certificate. [RESULT.json](artifacts/RESULT.json) contains aggregates.
[NAME_CLASS_RESULTS.tsv](artifacts/NAME_CLASS_RESULTS.tsv) groups all 1,320 old
name-code classes, including both excluded classes and every survivor.

| Outcome | Cases | Meaning |
|---|---:|---|
| PARTIAL_FOUR_ATOM_WITNESS | 8,986 | At least one four-value partial code and a valid four-leaf completion |
| FOUR_ATOM_PROJECTION_CONTRADICTED | 4 | Finite prefix search exhausted; this old code/page row cannot extend |
| UNKNOWN | 0 | No cases lost to CPU or wall limits |
| Total | 8,990 | Every registered old candidate accounted for |

Every actual contradiction:

| ID | I.1 page | IV.20 page | IRIS code | XIPHION code | Exhaustion certificate |
|---:|---|---|---|---|---|
| 868 | f2r | f10r | kyda | pcho | 289 root states fail the local projections |
| 931 | f2r | f19r | kyda | pcho | 242 local failures; 14 lack a four-leaf completion |
| 1102 | f2r | f4v | kyda | pcho | 244 local failures; 12 lack a four-leaf completion |
| 8964 | f95v1 | f8v | tol | ctho | 289 root states fail the local projections |

The two absent ordered name-code classes are `(kyda,pcho)` and `(tol,ctho)`.
Their individual values still occur in other surviving classes. Failures exclude
these exact pairs/assignments, not the strings generally, source-unknown pages,
the manuscript's language, or all plant-content hypotheses.

## What the surviving witnesses do and do not say

All four selected values must be nonempty and pairwise prefix-incomparable.
They occur at every prescribed source event with all intervening minimum lengths
and tails respected. Both fixed pages and all eligible supporting Acorus/Meum
pages are considered, with four different physical leaves. Old earliest name
positions are not frozen; each new certificate supplies valid new positions.

The saved LEAF witnesses use ten distinct one-character values; saved BROAD
witnesses use eleven. These are **one deterministic existence certificate per
old row**, not complete new-word domains. Their frequencies reflect the fixed
breadth-first/alphabetical traversal and must not rank possible meanings.
There may be other LEAF/BROAD strings and alignments for every surviving row.
The code may cross original written groups under the old source contract, so
these fragments cannot be described as identified Voynich words.

Only thirteen of 613 source occurrences are constrained: IRIS four times,
XIPHION twice, LEAF four times, BROAD three times. The other six hundred still
need all equalities and prefix constraints in the full model. They were relaxed
here, not read or excused. The very high survival shows that **this necessary
projection provides little discrimination among the already surviving rows**.
It is not evidence that 99.9555% of these readings are likely, that plant meanings
are confirmed, or that the original complete code exists.

## Scope, validation and next decision

The same exposed GDT976 domains were used: IT2a has 33/101/101/100 pages in the
four roles over 58 physical leaves. ZL3b/RF1b retain their prior lack of four-role
capacity; 254 source-unknown original frames remain unknown. No image, raw mixed
TSV, new target admission or reserve was opened. f84/f84r remain sealed and
f116v unadmitted. Transcriptions are alternative readings of one manuscript.
Independent confirmation capacity is zero; no whole-search null or significance
claim, no scored relation packet, and no confirmed plant name.

Before target execution, 27 synthetic problems compared the search against an
exhaustive common-substring enumeration and checked both positive and negative
certificates. These include a negative prefix-extension branch and a positive
case in which both new values must extend a common initial character. All pass;
this is engineering validation, not semantic calibration. The separate
certificate checker uses regex/occurrence positions and independent leaf-count
aggregation. Root corrected its draft before registration; it is not a blinded
replication or a second semantic source.

The registered decision threshold was 90% retention, solely a practical stop
rule. At 99.9555%, **do not continue by adding one more weak projected noun at a
time and do not restart the complete solver merely because these witnesses
exist**. A new proposal must constrain substantially more joint content or the
full writing relation, with a justified bounded test and retained source/channel
assumptions. The raw IDEA360 subset-account proposal is unrelated, unreviewed
and not selected by this result. No automatic substitute experiment is launched.

The inclusive block began 17:30 UTC; checkpoint 18:05 UTC. Primary execution
used 32 workers and 4.224 seconds wall time. No decoder/source/transcription
rule was changed after registration. Final certificate and publication checks
are recorded below.

Final certificate validation: **PASS, all 8,990 cases checked, zero errors**.
Every positive witness and all four exhaustion trees were verified; the result
table cells, aggregate counts, source projection and registration hashes agree.
The saved code/page supports remain conditional hypotheses, not confirmed words.

Closure checks: the 1,320-row class table reproduces all case/class counts.
Live-context checks PASS. The repository-wide check retains exactly eight
pre-existing failures: seven unbound GDT600 files and GDT953's missing large-
artifact justification. No GDT977 failure is reported; no global repository
PASS is claimed. Scientific work and certificate checks were complete by
17:56 UTC; publication closure follows within the same bounded work block.
