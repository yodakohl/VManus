# GDT833 — paired reference spelling intervention

6 September 2026. Status: **ORTHOGRAPHY_EFFECT_AND_RECOVERY_PASS**.
Independent source, objective and recovery validation: **PASS**.

## Result

With original reference spelling, the unchanged GDT832 OFF decoder recovers
**5,519/5,519 held words, 32,212/32,212 characters and 122/122 paragraphs exactly**.
All three encryption keys give this result. All 24 observed literal, three
suffix and eight wholeword values are correct. The three unused nominal
parameters receive no identification credit.

Replacing `v` by `u` **only in the same reference sentences** makes every one
of the 457 held v-containing words wrong. All 5,062 other words remain correct.
Neither the control spelling nor its evaluation metric is normalized to merge
u/v. Candidate pools, decoder, ciphertext and planted keys are common.

| Endpoint | NATIVE reference | Reference-only v→u |
|---|---:|---:|
| Exact held words | 5,519/5,519 — **100%** | 5,062/5,519 — **91.72%** |
| Aligned characters | **100%** | **98.58%** |
| Exact held paragraphs | **122/122** | **9/122** |
| Exact v-containing words | **457/457** | **0/457** |
| Exact non-v words | **5,062/5,062** | **5,062/5,062** |
| Novel composed-form occurrences | **2,138/2,138** | 1,946/2,138 |
| Novel joined-lemma occurrences | **1,270/1,270** | 1,151/1,270 |
| Correct observed L/S/W values | **24/24; 3/3; 8/8** | 22/24; 3/3; 8/8 |

All rows are identical across the three keys. These are robustness replicates
of the same historical content, not three independent text samples. The v-word
gain is 100 percentage points in each key, exceeding the predeclared 20-point
mean requirement. Non-v recovery changes by zero points. All four general
reconstruction floors also pass in NATIVE.

## Independent objective contrast

The single preregistered rival swaps the **outputs of both the v and z literal
carriers**, preserving a legal bijection and every other parameter. Truth-minus-
rival discovery score is:

| Reference | True key minus legal v/z-swap key |
|---|---:|
| NATIVE | **+5,470.2261 nats** |
| COLLAPSED | **−535.7301 nats** |

The direction reverses in every key as predeclared. This isolates the scoring
effect independently of frequency initialization or optimizer convergence.
The NATIVE selected score equals the true-key oracle score. The optimized
COLLAPSED fit instead selects **v→k**, with a score 627.0571 nats above truth.
That optimized wrong key is not the predeclared diagnostic v/z swap; both
comparisons are retained distinctly.

Thus the controlled loss of a reference spelling distinction is sufficient
to cause the observed identification failure **within this source pair and
pipeline**. It supports the mechanism suggested by GDT832. It does not prove
that every GDT832 error has the same cause, and GDT832 remains a failed run.
No old result was renormalized or rescored as a success.

## Design and chronology

The fresh control is De vulgari eloquentia: Book I discovery gives 120 citation
runs/5,866 words, Book II held gives 122 runs/5,519 words. All vernacular
quotations remain. Five noncontiguous citation-label reuses involving four
labels are kept as separate occurrence-numbered runs. No control run was
excluded or selected for a favorable decoder outcome.

The reference is all 682 Monarchia sentences, containing 19,162 words and
1,188 native `v` characters. COLLAPSED changes exactly those reference-side
characters, preserving every sentence and word position. No 20-word duplicate
required reference removal. A single candidate pool is derived from NATIVE
and shared by both conditions. The family factor stays OFF in both, so this
does not establish a new benefit for historical family information.

Sources, numerical criteria and all executable code were published at commit
`efa4aad80305a599d672d20bae8cf7ebf1ba0e69` **before fitting**. All 48 restarts and
six discovery-selected keys were locked before key-truth evaluation. The fit
lock SHA256 is
`a27568768a362806d4a5dc0c6876410f097d37ea2c2d316b4dc5d59110a777ec`.
No registered code, source, fit or threshold changed after publication.

## Verification and artifacts

Eight toy tests verify reference-only intervention, original-spelling metrics,
legal key swaps, paired search budgets and discovery-only selection. Independent
raw-source reconstruction checks 242 control paragraph runs/11,385 words and
the exact reference pairing. The final independent validator replays **48
discovery objectives, six held evaluations with 33,114 word predictions and
12 true/rival oracle scores**, including input commitments, key reconstruction
and every decision gate.

Compact results: `artifacts/RESULT.json`; independent replay:
`artifacts/VALIDATION.json`. All 48 restart fits, six selections, fit lock and
now-released control truth are retained. See REPRODUCE.md for auditing the
completed checkout. To repeat optimization itself, start from the preregistration
commit; the fitter refuses to overwrite a locked result.

## Claim ceiling

The decoder has recovered an entire held historical control under a supplied
mixed architecture with known atomic roles and word/paragraph boundaries.
Those assumptions are not established for Voynich. No hidden segmentation,
complete historical paradigm system, manuscript language or semantic anchor
was identified. No Voynich data were opened or fitted; confirmed Voynich words
remain zero. The result does not reopen GDT616/CDA001 or automatically select
a target fit.
