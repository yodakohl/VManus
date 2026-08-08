# F76S001 — repeated-margin line-entry selector

Date frozen: 2026-08-09  
Status: **REGISTERED_UNSCORED; TARGET FORBIDDEN UNTIL CONTROLS PASS**

## Question

The permitted human sources agree that nine one-glyph marks form a vertical
column on f76r and are approximately aligned with nine selected prose lines.
They disagree about whether these are line labels, subparagraph marks, one
vertical title, or another notation. The only repeated mark is `s`, at fixed
positions 1, 4, and 9.

F76S001 asks one narrow structural question: do the three `s`-aligned prose
lines share a root-free first-word/line-entry state more strongly than almost
every other three-line subset of the same nine aligned lines?

This is not F76M001's whole-line or interval bag-similarity mechanism and does
not require F76J001's hypothetical fusion. It uses only the secure approximate
line alignment and only the opening construction of each aligned line.

## Frozen source and target

Input:

`experiments/semantic_assumptions/results/pre_grounding_interlinear.tsv`

SHA-256:

`8052a51fa37ad467e754be39648336ec4014442dab5e223daab2e77efaba4a43`

The source alignment report is frozen at SHA-256
`27593399b74b00e72cbd939519d324d5ace1c4846b457435263b92a3c3104744`;
its current-locus crosswalk input is frozen at SHA-256
`4a128ed3d4b87a9d804a336a6c22ced65839fa39c83f3ecf45092bbc64f2eabc`.

The nine fixed mark/line pairs are:

| position | mark locus | aligned prose locus | mark |
|---:|---|---|---|
| 1 | f76r.4 | f76r.5 | s |
| 2 | f76r.7 | f76r.8 | d |
| 3 | f76r.10 | f76r.11 | q |
| 4 | f76r.14 | f76r.15 | s |
| 5 | f76r.18 | f76r.19 | o |
| 6 | f76r.22 | f76r.23 | l |
| 7 | f76r.27 | f76r.28 | k |
| 8 | f76r.31 | f76r.32 | r |
| 9 | f76r.37 | f76r.38 | s |

The target triplet is therefore positions `{1,4,9}`. ZL3b, IT2a, and RF1b
are alternate readings of the same lines and are scored synchronously.

The target forms and the earlier F76 mechanisms are already exposed. This is
an explicitly exploratory registered test, not independent confirmation.

## Frozen root-free representation

For the first surface token of each aligned prose line, retain exactly three
channels:

1. `LINE_CARRIER`: the already frozen line-entry carrier field (`d`, `s`, `t`,
   or empty);
2. `Q_STATE`: whether the first formal role begins with `Q_`;
3. `BASE_ROLE_PATH`: the complete first-token formal role sequence after
   removing only an initial `Q_` marker from each role name.

No literal root, surface token identity, character n-gram, English gloss,
image feature, OCR output, or object label is used.

For a pair of lines, channel similarities are:

- exact equality for `LINE_CARRIER`;
- exact equality for `Q_STATE`;
- one minus normalized Levenshtein distance for `BASE_ROLE_PATH`.

The pair score is the unweighted mean of the three channels. A triplet score
is the mean of its three pair scores.

## Exact synchronous null

Enumerate all `C(9,3)=84` three-line subsets. Within each reading, standardize
the 84 triplet scores using their population mean and standard deviation. The
synchronous statistic for a subset is the minimum of its three reading-wise
z-scores. Higher means more coherent in every alternate reading.

The exact upper-tail p-value counts all null subsets whose synchronous
statistic is at least the target statistic. Ties count against the target.
No random permutations or asymptotics are used.

## Frozen gates

Every gate is mandatory:

1. exactly nine paired prose rows exist in each reading and every first-token
   role path is nonempty;
2. the three target first-token surfaces are pairwise distinct in each reading;
3. exact synchronous p-value is at most `4/84 = 0.047619...`;
4. the target rank is at most 3 of 84 in every reading;
5. the minimum reading-wise target-minus-orbit-median effect is at least 0.10;
6. each of the three target line-pair scores is strictly above the median of
   all 36 line-pair scores in every reading;
7. after separately deleting each of the three channels, the exact
   synchronous p-value remains at most `4/84`;
8. the orbit is nondegenerate and every frozen hash/control binding matches;
9. a nonimporting implementation reconstructs the input, features, all 84
   scores, all gates, and the final decision.

Failure of any gate is nonconfirmation. Gates may not be weakened after the
target score is opened.

## Required controls before target

The production implementation must pass and hash-bind:

- a three-channel planted target that passes every gate;
- a negative target with a different coherent triplet;
- a target coherent in only one channel, which must fail channel deletion;
- a two-of-three pair-leverage target, which must fail the pair gate;
- a target planted in two readings but contradicted in the third;
- exact 84-subset enumeration and conservative tie handling;
- complete degeneracy rejection;
- deterministic repeat equality;
- the production runner, future independent validator, preregistration, and
  input bytes.

## Claim ceiling

A full pass would nominate only this exploratory statement:

> The repeated f76r margin mark `s` is associated with a reusable root-free
> line-entry construction in the fixed aligned-line panel.

It would not establish mark ownership, the function of singleton marks, a
title, paragraph segmentation, joining, a detached prefix, a sound, letter,
number, word class, language, lexeme, plaintext, or translation. A failure
closes only this fixed three-channel repeated-`s` selector mechanism.
