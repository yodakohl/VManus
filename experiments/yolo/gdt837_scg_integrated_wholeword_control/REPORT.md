# GDT837 — one wrong suffix defeats recovery; no wholeword gain

**STRICT_RECOVERY_FAIL.** All six selected keys recover all 34 active roles,
all 22 literal outputs and all eight wholeword outputs. One of four suffix
outputs is wrong: `ae` is read as `a`. Both arms therefore recover only 33 of
34 identifiable active role/output pairs, failing the predeclared exact-key
criterion even though every plaintext accuracy floor passes. The held word
accuracy gain from STRICT is zero on all three keys.

| Criterion | Result in each arm, each key | Required |
|---|---:|---:|
| Held words | 189616 / 192991 = 98.2512% | at least 95% |
| Held characters | 99.6947%; 3375 edits / 1105634 characters | at least 99% |
| Novel composed form occurrences | 20292 / 20871 = 97.2258% | at least 90% |
| Unambiguous novel composed lemma occurrences | 7979 / 8254 = 96.6683% | at least 90% |
| Identifiable active role/output pairs | **33 / 34** | **all 34** |
| Mandatory W violations, discovery / held | 0 / 0 | 0 / 0 for STRICT |

All six selections use restart 0 under the fixed discovery-score/tie rule.
They recover 11475 of 13828 complete held source sentences. These are supplied
annotated sentence units, not historical paragraphs or recovered syntax.
All 3375 incorrect held words lose the `e` in the encoded `ae` suffix; the active
literal and wholeword outputs are exact. There is no observed u/v substitution.

The selected discovery score is −1401028.476246 nats versus −1432617.648124 for
the planted key: the wrong output gains **31589.171877 nats** under the frozen
objective. A better search score therefore cannot by itself establish correctness.
The result does not show that ordinary language context is useless. It shows a
specific wrong suffix value preferred in this source/reference comparison and
tested candidate space. The searches enforce positional suffix legality and
per-role injection, but neither implements the full mandatory suffix inverse.
That untested restriction cannot be counted as either a success or a rejection.

STRICT rejects 10958, 10980 and 10834 proposals in the three selected fits;
RELAXED rejects none through this particular check. Their final active outputs
and all reported recovery metrics are identical. Rejected proposals are an
implementation observation, not evidence of recovery benefit. The effect found
retrospectively on GDT834 does not establish an improvement on this SCG control.
No source, spelling, threshold, objective, restart budget or selection was repaired.

A separately labeled **posthoc census of the saved fits** finds the sole active
`ae → a` mismatch in 45 of 48 restarts: all 24 RELAXED and 21 STRICT. Three
STRICT restarts have additional errors; none of the 48 has every active package
correct. No restart was rescued or re-ranked using truth. In every selected key,
2248 discovery words and 3375 held words are wrong, all and only those containing
the mismatched suffix; the held errors span 335 distinct form pairs. The census
adds no fit, objective evaluation or selection, and makes no causal orthography
claim. It is outside the preregistered decision, with its own source and compact
POSTHOC_ERROR_CENSUS.json artifact. Recompute it using
`python3 experiments/yolo/gdt837_scg_integrated_wholeword_control/src/posthoc_error_census.py --check`.

The public preregistration commit is `60e0d84b50d63699a315cbfbfd9ba173bc1b86f2`.
It precedes all real initializations and scores. The unchanged GDT836 engine ran
48 fits: three opaque keys, two arms, eight paired starts, 60000 steps and four
greedy sweeps. All 48 outcomes and six discovery selections were frozen before
held recovery or world-key truth access. FIT_LOCK SHA256:
`e25befd85b812a33c5ef600b5de4383367164a35f105409a53c3cfba9f8ff4a9`.
All 24 pairs share their exact initial key, attempt count and seeds. All 48
saved initializations satisfy W priority. The source capacity snapshot remains
byte-exact; the source and evaluation protocols are in METHOD.md and SPEC.json.

The fixed SCG Books I–II / III–IV split supplies 129120 discovery / 192991 held
words in 9859 / 13828 source sentences. All 22 active literal, four suffix and
eight wholeword rules have discovery support. SCG is new as ciphertext control;
its ITTB train subset was already a GDT832 reference. The current frozen reference
is native Monarchia, with original source spellings retained. Three key shuffles
share one content split and are not independent corpora. Word/atom/sentence
boundaries and nominal 26 L / 4 S / 8 W counts are supplied. This result provides
no Voynich word, language, optional-abbreviation rule or target-fit authorization.
GDT836's fixed Questio stop, GDT616 and CDA001 remain closed.

Independent validation and byte-exact validation replay both pass: 48 discovery
objectives, six selections and oracle scores, 1157946 held predictions, 204 active
role domains checked by independent maximum flow, 966333 source-word reencodings,
all 11 compressed/decompressed packet bindings, and the original 322111-word
source reconstruction. Seventeen invented integration tests also pass. These
checks confirm the scientific failure; they do not turn it into recovery success.

Publication checks cover the exact staged experiment and explicitly listed global
updates, including the decompressed contents of all gzip artifacts. The separate
full-repository check still reports the pre-existing seven unbound GDT600 files
and stale legacy TSV index state. Those unrelated files and rows remain untouched.
At preregistration the full Markdown index also differed because confirmation
files were intentionally withheld from the public tree; they are included with
this result. No global-clean-worktree claim is made.
