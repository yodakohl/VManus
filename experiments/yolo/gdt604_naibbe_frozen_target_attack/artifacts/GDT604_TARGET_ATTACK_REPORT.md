# GDT604-style target attack — no stable Naibbe-family reading

Status: **LM_DRIVEN_PSEUDOTEXT_NO_READING**.

## Result

The independent P x S dictionary/Poisson-deviance attack does not produce a
stable reading of the f84/f84r-free GDT327 corpus.  Character order is
predictable enough that independently optimised Latin, Old Italian, and Middle
High German keys all beat within-line order shuffles on held physical folios.
But the three incompatible language attacks all do so, every decoded target is
globally less typical of its language model than of the matched
order-destroyed model, and keys from different seeds/restarts almost completely
disagree.

No language passes the frozen decision contract.  No surface is assigned a
sound, lexeme, plaintext, translation, or meaning.

## Routing and safe target materialisation

The route and targeted GDT601–603 material were read first.  GDT601 had already
rejected the literal published Naibbe key on the same f84-free corpus; GDT602
showed that the unknown key is recoverable on the control once oracle U/P/S
segmentation is supplied; GDT603 was still registered/unscored during this
standalone scratch-work pass.  The duplicate screen was:

```text
./vmanus-exp route-check 'P S dictionary Poisson deviance Naibbe segmentation key recovery held folio language null GDT327'
```

Target strings were emitted only through `./vmanus-exp query-tsv` with all 180
explicit page allow-values derived from the f84-free GDT327 artifact and
`--forbid-prefix f84`.  Requested columns were only
`page,locus,line_number,section,language,hand,eva_clean`.  The guarded result
contains 4,165 lines on 91 physical folios and has SHA-256
`d9186790969641f5dce9fb75d697bd926310936248d7214ef804ba29d0a1e413`.
No f84/f84r selector or row was materialised.

The physical-folio split was frozen by
`sha256("gdt604-held-v1|" + folio)`: 68 train and 23 held.  Held folios were
`f1, f18, f23, f28, f30, f33, f45, f47, f52, f53, f81, f85, f88, f89, f90,
f103, f105, f108, f111, f113, f114, f115, f116`.

Preregistration: `GDT604_TARGET_ATTACK_PREREG.md`, SHA-256
`47d54ab3b180d4cf1fdc57fd3bbd0f69af866ad39ff61879b72a19ec742c8d97`.

## Train-only segmentation

The primary model fixes the public maximum U size at 138.  P and S are also
capped at 138.  Dictionaries and pair marginals are learned on training folios
only; held forms use only frozen train dictionaries.  Unfactorable forms remain
explicit `UNKNOWN` gaps and reset the LM.

| model | train U/P/S | train occurrence coverage | train type coverage | held occurrence coverage | held type coverage |
|---|---:|---:|---:|---:|---:|
| U=115 navigation | 115/138/138 | 87.630% | 63.784% | 85.736% | 63.414% |
| U=132 navigation | 132/138/138 | 88.610% | 64.124% | 86.451% | 63.446% |
| **U=138 confirmatory** | **138/138/138** | **88.638%** | **64.244%** | **86.451%** | **63.446%** |

All three confirmatory dictionaries saturate their maximum while more than a
third of token types remain unexplained.  Among 1,657 held types unseen in
train, 1,043 have no frozen P/S cut, 545 have one, 68 have two, and one has
three.  This is already unlike the Naibbe control's nearly complete
factorisation.

## Language and null models

- Latin: Caesar, pinned source hash
  `84ac8411841a4d8f5f4a49b6a2cd1f466917c6a5af72916d5e0b2b1ecb2f659c`.
- Old Italian: Dante, pinned source hash
  `aafa15bbc0644dac7680ce3d0e4494b99775fbc83394cb7ad88145a0f8d6b31e`.
- Middle High German: five MHG4SNA texts at commit
  `3eddc3dc1620cf400c152d9ed8915416cb8d6d7a`.

Each model receives exactly 120,000 rendered characters under the frozen
23-letter renderer.  Its paired null independently shuffles characters inside
every 90-character reference chunk before fitting the same char-4 model.
Keys use the six-surface-per-state/letter capacity, seeds 11/29/47, 50,000
iterations, and two independent restarts per seed.  The train-only freeze
contains 36 keys over exactly 414 code types and has SHA-256
`4409cb99beded2c5ffb7a94c48d82bb895ac4dfafccb3498c5a921af50958a2d`.

Held order is compared with 32 deterministic within-run shuffles preserving
line, folio, gaps, run lengths, segmentation, and character counts.

## Held-folio evidence

| model | real-key order-z range | minimum positive folios | target `LL(real)-LL(destroyed)` bits/char | paired real-key advantage | minimum key type agreement | minimum held-weighted agreement | all-six character consensus |
|---|---:|---:|---:|---:|---:|---:|---:|
| Latin | 36.41–57.17 | 22/23 | **−0.726 to −0.468** | +1.101 to +1.437 | **9.42%** | **5.00%** | **0.098%** |
| Old Italian | 35.46–68.05 | 23/23 | **−0.907 to −0.517** | +1.423 to +1.766 | **12.56%** | **10.81%** | **0.498%** |
| Middle High German | 31.82–62.88 | 23/23 | **−0.904 to −0.595** | +1.107 to +1.522 | **7.25%** | **5.25%** | **0.055%** |

The order-z values are real but non-identifying: all three mutually
incompatible languages obtain them.  Their key instability is catastrophic.
Across the fifteen restart pairs per language, mean type agreement is only
16.36% Latin, 17.78% Old Italian, and 12.71% Middle High German; mean
held-weighted agreement is 21.63%, 22.83%, and 18.59%.  Majority-vote character
consensus is only 44.45%, 45.32%, and 41.32%, respectively.

More decisively, every target likelihood ratio is negative.  The matched
instrument behaves in the opposite direction on unused reference text:

| held readable reference | chars | `LL(real)-LL(destroyed)` bits/char | order-z |
|---|---:|---:|---:|
| Caesar Latin | 3,245 | **+1.715** | 78.76 |
| Dante Old Italian | 120,000 | **+1.349** | 349.11 |
| MHG4SNA Middle High German | 120,000 | **+1.404** | 478.32 |

Thus the target's positive relative-order statistic does not put it in the
reference language's typical distribution.  It merely shows that a flexible
homophonic key can exploit recurrent target order better than it exploits the
same characters after shuffling.

## Frozen gate decisions

All languages pass held occurrence coverage, raw order-z, positive-folio, and
paired real-key-versus-destroyed-key gates.  All three fail every stability
gate:

- minimum type agreement is far below 70%;
- minimum held-weighted agreement is far below 85%;
- all-six occurrence consensus is far below 90%.

Zero languages pass all gates.  The hard result is therefore
`LM_DRIVEN_PSEUDOTEXT_NO_READING`.

## Concrete highest-scoring lines

These are the rank-1 held lines under the median real-versus-destroyed order
gain.  They are printed in full and are **not translations**.

### Latin — f85r2.15

EVA: `ypshedy dar chedy or am`

- seed 11/restart 0: `mdesariitu`
- seed 11/restart 1: `ntstiterec`
- seed 29/restart 0: `mdereriisu`
- seed 29/restart 1: `nrtisiisib`
- seed 47/restart 0: `dmitaresex`
- seed 47/restart 1: `mditerisex`

All-six consensus: 0%; majority consensus: 48.33%; all restarts identical: no.

### Old Italian — f18v.9

EVA: `okchor qotchy qokchy ytol doky dy`

- seed 11/restart 0: `iieriselavam`
- seed 11/restart 1: `imeretamacas`
- seed 29/restart 0: `edematelicim`
- seed 29/restart 1: `atontienodon`
- seed 47/restart 0: `erianierrvre`
- seed 47/restart 1: `atestialeven`

All-six consensus: 0%; majority consensus: 43.06%; all restarts identical: no.

### Middle High German — f45v.8

EVA: `yksheor odal sho dy pchom otor oaiir`

- seed 11/restart 0: `<?>ncuuensgeinl`
- seed 11/restart 1: `<?>eluiniranieb`
- seed 29/restart 0: `<?>egesenomereb`
- seed 29/restart 1: `<?>ubetsiiletuc`
- seed 47/restart 0: `<?>smernuaginsd`
- seed 47/restart 1: `<?>ubeternhenug`

All-six consensus: 0%; majority consensus: 38.89%; all restarts identical: no.

All 60 predeclared top rows are preserved without truncation, with locus, full
EVA, all six restart outputs, coverage and consensus:

- `gdt604_top_lines_latin.tsv` —
  `8d6f0c1e33e817a5cbb3b63175a5daebeb0184f7dba3188f857d01b08769d5ba`
- `gdt604_top_lines_old_italian.tsv` —
  `e8c63a795d3bdfeabb56061242251066d21aa759a7acf82760675a13b05a36c0`
- `gdt604_top_lines_middle_high_german.tsv` —
  `db4260999e3af50a17b47b33bf93416c9bce69a25f3365180697d6d69a304afa`
- readable full appendix `GDT604_TOP_LINES_FULL.md` —
  `01cc06f5b1e94adab78128c31e8dbc96eee79ead413defe70a342f509efdf43b`

None of the 60 lines is identical across all six restarts.  In the top-20
sets, maximum all-six character consensus is 0% Latin, 9.09% Old Italian, and
0% Middle High German.

## Artifacts and scope

- Result JSON: `gdt604_target_result.json`, SHA-256
  `ddf807c856f314320ff118b047a165d8add38162682f57f427789d500267dcfc`.
- Reference calibration: `gdt604_reference_calibration.json`, SHA-256
  `86ea19d54adbcd814b0b20925f7a9e7038b3d38b111e76d088c978aef8a18a1d`.
- Source scripts: `src/run_all.py`, `src/pipeline.py`,
  `src/portable_factorizer.py`, and `src/portable_keylib.py`.

The experiment assumes given whitespace token boundaries and the public
one-versus-two-character, six-table architecture.  It says nothing against all
possible ciphers.  It does reject this concrete train-only P x S/U=138
Naibbe-family attack as a reading of the GDT327 target.
