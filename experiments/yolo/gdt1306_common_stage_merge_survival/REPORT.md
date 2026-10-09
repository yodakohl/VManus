# GDT1306: later merging changes measured boundary profiles

**LATER_SELECTION_EFFECTS_WITH_READER_DEPENDENT_SIGN_CREATION.** Later processing
substantially enlarges some pre-existing group-final contrasts and reverses
others. A newly positive contrast occurs in one of64rows in ZL3b and one in
IT2a, at DIFFERENT merges; none occurs in RF1b. These two crossings are small.
There is no shared three-reader primary sign-creation result and no majority vote.

The more informative preselected examples are ol/l and or/r: their contrasts
already exist at the common intermediate stage, but later processing amplifies
them in every reading. This is neither an all-artifact explanation nor a reason
to attribute the entire final profile to the scribe. Readings are alternative
transcriptions of one manuscript, not independent replications.

## Exact result on the declared panel

| Reading | Groups | Scorable rules | Positive at both stages | Nonpositive at both | Newly positive | Positive removed |
|---|---:|---:|---:|---:|---:|---:|
|ZL3b|19332|64|40|21|1|2|
|IT2a|22528|64|43|18|1|2|
|RF1b|19321|64|40|22|0|2|

All64rules are retained per reader. None has a zero denominator here; the
implementation's zero-count cases remain explicitly unscorable in the fixtures.
No support threshold, pseudocount, statistical null or p-value is added.

The predeclared primary event is a common-stage gap<=0 becoming a final gap>0:

| Reading | M / right component | Common-stage gap | Final gap | Exact endpoint counts |
|---|---|---:|---:|---|
|ZL3b|CEy / Ey|−0.0594pp|+0.1115pp|M193/194 unchanged;R873/877→634/638|
|IT2a|ai / i|−0.0088pp|+0.6681pp|M3/558→3/247;R1/183 unchanged|
|RF1b|none|—|—|all64rows reported|

`C` and `E` are the old analytical ch/ee collapses, not identified native letters.
These small reader-dependent crossings should not be advertised as a robust
universal mechanism. The programmed per-reader decisions remain in RESULT.json.

## The six examples nominated BEFORE this diagnostic

Each entry is the M-minus-R group-final rate difference in percentage points,
COMMON STAGE immediately after creating M → FINAL STAGE:

| M / R | ZL3b | IT2a | RF1b |
|---|---:|---:|---:|
|ol / l|16.33 → 48.14|18.84 → 50.98|16.31 → 46.82|
|or / r|27.04 → 45.16|27.81 → 46.20|21.68 → 36.01|
|dy / y|11.37 → 6.81|11.92 → 7.20|10.59 → 2.15|
|aN / N|0.41 → 0.60|1.37 → 1.45|1.20 → 1.34|
|ok / k|-0.72 → -0.89|-0.60 → -0.65|-0.68 → -0.88|
|ot / t|-0.67 → -1.05|-0.70 → -0.98|-0.64 → -0.81|

Thus ol/l grows by31.80pp in ZL,32.14pp in IT and30.51pp in RF. The common-stage
contrast itself remains16.33/18.84/16.31pp: this diagnostic has not made it vanish.
Likewise or/r grows by18.12/18.39/14.33pp. The dy/y contrast instead shrinks in
all readings. None of these six preselected comparisons changes sign.
The common stage has already undergone earlier merges and the current merge;
it is NOT an unprocessed linguistic or source-memory baseline.

## A concrete reason the ol/l difference grows

In ZL, ol's final rate moves only from1805/2757 (65.47%) to903/1347 (67.04%).
The surviving l profile changes much more:1193/2428 (49.14%) to124/656 (18.90%).
After the common stage, rule9 `a+l→al` absorbs1459l occurrences, including ALL
1069lost group-final l occurrences. Rule58 `l+k→lk` absorbs another313l
occurrences, all nonfinal. The other readers have the same two consuming rules:
rule9 removes1283/1171final l occurrences in IT/RF; rule58 removes no final l.

For example, the fixed illustration ZL3b|f100r.14|G009 is raw `otal`.
At the ol common stage its tokens are `o t a l`; its final l is later absorbed
into al, and the eventual final token is otal. The written l and its original
position have not disappeared. It simply no longer counts as an active token
named l in the final inventory. This illustrates analysis selection, not a word
meaning or an interpretation of what the author intended by otal.

The reverse sign change od/d occurs in all three readings: ZL+12.72→−1.33pp,
IT+10.90→−2.78pp, RF+11.62→−1.62pp. In each case od's own cohort/rate is unchanged;
later removal of nonfinal d occurrences raises the surviving d final rate enough
to reverse the comparison. Additional small reversals are yk/k in ZL/RF and
Co/o in IT. Every row, exact fraction and consuming-rule count is retained.

## What was measured, and what was not

For rule j:M=L+R, BOTH M and R are measured immediately after the complete
rule-j pass, then again after all64rules. Actual token IDs, projected spans,
birth rank and immediate consuming rank/side certify which nodes survive.
An M inside a larger final token is not counted as an active M. The immutable
endpoint is its original complete written-group end, not a changing neighbor.

The exact identity is

`gap_final = gap_j + (M_final−M_j) − (R_final−R_j)`.

The last two terms are signed later-processing changes. They can oppose or
exceed another term. No0–100%artifact fraction is reported. In particular this
is NOT a decomposition of GDT608's held cross-entropy or multi-feature ATOMIC
advantage. Its directed backoff and original decisions remain unchanged.
The newly quantified mechanical shifts limit inferences drawn from final-token
profiles; they do not identify morphemes, lexical storage, nonlinear source
composition, actual historical abbreviations or a language.

## Scope, exposure and exact verification

Input is the unchanged already guarded1233cache:19332/22528/19321strict P-groups
in ZL/IT/RF, each with definite exterior spaces and literal22-unit parsing.
Every source page belongs to the current179selector allowlist. f84-prefixes,
f1r and f116v are absent. f106v is allowed TEXT in that list; its separate image
restriction is untouched. No image, reserve, raw mixed TSV,327/336payload or old
605guarded body was opened. The old605rule table is reused as model metadata,
with its historical training/exposure retained, not new independent training.

Each raw group is projected ONCE by the nine ordered605collapses, then processed
alone with the frozen64rules. No uncertain-space joining or annotation cleaning
is applied. The projection reverses exactly for these literal groups. This panel
is not608's91-folio hard-chunk population, train/held split or98-unit event sample.
The analytical units and their spans are not proven original glyphs or words.
All cases are already exposed exploratory material.

The producer reviewed source-code semantics and hand controls before any new
counts. Final protocol/code/source lock:13:17:15UTC. Runner applies forward
nonoverlapping replacements; the separate validator collects scheduled matches
and replaces intervals from the right, preserving the same creation identities.
It independently scans the projection, reparses all61181raw groups, replays
4875distinct projected traces, all192reader/rule rows,1518464weighted type-stage-
role cohorts and135fixed illustration records. All subset, loss, endpoint,
exact-fraction and source-ID checks pass. Same author, separate implementation;
not an independent manuscript or semantic replication.

Source-free fixtures cover real births versus overlapping pairs, post-j versus
R's earlier birth, absorbed children, non-idempotent collapse and zero final
cohorts. Input metadata has64unique products and no self-merge; the self-merge
fixtures test the general replay, not an observed defect in these64rules.

Stop this bounded diagnostic. No extra endpoint, favorable subset, changed
projection, new source, smoothing, holdout claim or decoder follows automatically.
Code, source hashes, full count/rate matrix and witnesses are bound in experiment.json.
