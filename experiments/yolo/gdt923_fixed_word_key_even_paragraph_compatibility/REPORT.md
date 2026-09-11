# GDT923 — fixed 26-word key on complete even-leaf paragraphs

The unchanged RF key does not gain informative whole-paragraph transfer in its primary reading. There is one **descriptive ZL compatibility witness**, with two locked words and fifteen unknowns. Neither result confirms a translation.

The public preregistration is commit `536320cb`, before execution. All 26 word values, source units and transcription eligibility remain unchanged. The runner reused the original GDT893 matcher, without a new decoder or optimizer. GDT893's original partial-optimum result and GDT894's two failed immediate continuations remain intact.

## Complete panel result

“Informative” was fixed before matching as at least two distinct known key types. A baseline window matches the COMPLETE word-equality pattern before the fixed values are imposed.

| Reading | Eligible paragraphs / leaves | Informative paragraphs | Informative baseline-positive | Informative compatible | All compatible paragraphs / windows |
|---|---:|---:|---:|---:|---:|
| CONSENSUS | 2 / 2 | 0 | 0 | 0 | 1 / 252 |
| IT2a | 239 / 37 | 156 | 34 | 0 | 21 / 90102 |
| RF1b | 9 / 8 | 1 | 0 | 0 | 1 / 252 |
| ZL3b | 18 / 10 | 9 | 4 | 1 | 5 / 285 |

The primary RF panel contains nine complete paragraphs on eight even physical leaves. Only f52v has two locked types (`daiin → adhuc`, `qokeey → de`); its complete repetition pattern has **zero baseline source windows**. Its failure therefore cannot isolate the 26-word key. Of the three other RF paragraphs with baseline windows, f10v and f20r fail the fixed key, while f108r survives ambiguously. The main machine verdict `NO_INFORMATIVE_COMPATIBILITY` must not be read as a well-powered general rejection of the key.

RF f108r.35–36 has only one locked type, `chedy → et` at its final position. It admits **252 source windows representing 250 different full written texts**. Its 18 other positions remain unknown. The consensus reading repeats this same manuscript observation; it is not another confirmation.

The descriptive ZL f106v.26–27 paragraph G807-P0481 has exactly one compatible source window: `ALIM:213:segment:0002`, zero-based start18, length17, complete plaintext SHA256 `55046ec257fdbbfb623e74f18facdb52ae0a444667979651da25818b39eb3bdd`. Its fixed prediction is:

```
UNKNOWN UNKNOWN UNKNOWN UNKNOWN UNKNOWN sed UNKNOWN UNKNOWN UNKNOWN UNKNOWN UNKNOWN UNKNOWN UNKNOWN UNKNOWN UNKNOWN de UNKNOWN
```

The corresponding ciphertext is:

```
tar air kshdain okal chdy lchedy kshar chopchy otches aral opchdy olcheo odaiin sheotal shoor qokeey oarar
```

All seventeen forms are distinct. Of 34,056 equality-pattern windows, one also satisfies the two present values and the inverse reservation of all 26 Latin values. This is a real compatibility survivor in the frozen descriptive panel, not a confirmed source identification or seventeen-word translation. Its uniqueness is conditional on an exhaustive search across this specific pool; there is no whole-search significance test. It cannot replace the preregistered RF primary. Unknown correspondences were not added to the key.

IT has 156 informative paragraphs, of which 34 have baseline windows and none survives the fixed key. Its 21 surviving zero/one-type paragraphs are all retained. These are alternate transcriptions of the same manuscript, not independent populations or opportunities to choose a preferred outcome.

## Whole-leaf separation and confirmation capacity

The original key fit used odd physical leaves; all paragraphs here are even. Fold A is leaf number modulo4=0, fold B modulo4=2, fixed before matching. Neither fold selected or changed a candidate for the other. All caches had prior project exposure, and many related tests were already performed; no historical blindness is claimed.

| Reading / fold | Eligible paragraphs / leaves | Informative paragraphs / leaves | Informative baseline-positive | Informative survivors / leaves |
|---|---:|---:|---:|---:|
| CONSENSUS / A | 2 / 2 | 0 / 0 | 0 | 0 / 0 |
| CONSENSUS / B | 0 / 0 | 0 / 0 | 0 | 0 / 0 |
| IT2a / A | 129 / 20 | 84 / 14 | 12 | 0 / 0 |
| IT2a / B | 110 / 17 | 72 / 12 | 22 | 0 / 0 |
| RF1b / A | 7 / 7 | 1 / 1 | 0 | 0 / 0 |
| RF1b / B | 2 / 1 | 0 / 0 | 0 | 0 / 0 |
| ZL3b / A | 9 / 7 | 4 / 3 | 2 | 0 / 0 |
| ZL3b / B | 9 / 3 | 5 / 2 | 2 | 1 / 1 |

RF has no informative baseline-positive paragraph in either fold, and no informative paragraph at all in B. ZL's single informative survivor is on B only; A supplies no independent compatible counterpart. Thus no candidate has an informative compatibility confirmation across both even-leaf folds. Different source witnesses, transcript editions and multiple windows do not create additional manuscript leaves.

## Candidate table and contradictions

[CANDIDATE_TABLE.md](CANDIDATE_TABLE.md) lists every one of the 26 fixed values and every eligible paragraph, including zero coverage, zero baseline windows and contradictions. [PREDICTIONS.tsv](artifacts/PREDICTIONS.tsv) gives the literal prediction at **every** position, with all unknowns marked; [PREDICTION_PACKET.json](artifacts/PREDICTION_PACKET.json) preserves complete original groups, IDs and key coverage. Both were written and hashed before source matching. [PARAGRAPH_RESULTS.tsv](artifacts/PARAGRAPH_RESULTS.tsv) gives the complete outcomes.

For every baseline-positive rejected window, the deterministic first failing position is counted by forward mapping or inverse reservation in PARAGRAPH_RESULTS.json and KEY_RESULTS.json. These counts partition rejected windows; they are not counts of all disagreements and cannot rank which individual key value is wrong. A reserved Latin value may rule out a window even when its locked ciphertext partner is absent. All baseline window coordinates are retained in the four compressed CSVs; all survivors retain unit, offset, length and full written-text hash in [WITNESSES.json.gz](artifacts/WITNESSES.json.gz). Identical plaintext hashes group equivalent predictions while retaining every provenance record. No best witness is selected.

## Decision and limits

Keep the 26 values as an unconfirmed, source-pool-relative candidate only; this test does not justify promoting `chedy`, `qokeey`, `lchedy` or any other word to a translation. The ZL compatibility witness is retained explicitly. No new key value, compiler change, source addition, clipped passage or automatic extension follows.

This is a new per-paragraph compatibility screen, **not** satisfaction of GDT893's stricter future held-decoding gate forbidding a newly selected source passage. Separately compatible unknown extensions could disagree across paragraphs; no joint enlarged key was solved or asserted. Baseline-zero cases do not diagnose the fixed values, and the old model allowed unselected paragraphs. No general source-montage refutation, significance, language identity, semantic relation promotion or independently confirmed meaning follows. Confirmed meanings: **0**. Sealed f84/f84r were not accessed.

## Validation and reproducibility

Independent complete replay **PASS**: 268 eligible paragraphs, 11,899 prediction positions, all four exhaustive baseline window sets and all 90,891 surviving provenance records. The independent oracle uses explicit forward/reverse maps, unlike the primary previous-occurrence matcher. Validator SHA256 `955165c8df27e684e54fdfa621185f4d02d2bd199efa0676469df84d431f5634`. Four synthetic filter checks and a complete synthetic oracle check pass. Original source bytes are supplied in SOURCE_UNITS.json, identical to GDT893's original input lock. The original matcher is a bound dependency. Run the manifest command, followed by the independent validator. The complete 25,258,524-byte witness JSON is losslessly compressed; PACKAGING.json binds its original and compressed hashes. Run src/package.py after the runner to reproduce that representation. Exact staged privacy/scope checks pass. The separate repository-wide check retains its eight pre-existing GDT600/index error groups; this is not a global PASS.
