# GDT612 simplified 34-slot decoder pilot and objective autopsy

Date: 2026-08-28
Status: **`HEURISTIC_DECODER_INVALIDATED__ORACLE_TRUTH_RANKS_LAST__ZERO_STABLE_TARGET_OUTPUTS`**

## Result in one sentence

The executed objective ranks its planted truth last of seven keys, the synthetic
control omits five truth items from train, and the archived target keys have
**zero exact restart-stable primitive outputs, zero exact restart-stable unit
outputs, and zero exact restart-stable held word spans**. This invalidates the
heuristic objective/control pair before semantics; it does not test or falsify
the exact GDT609 FST34 model.

## Question and executed pilot

The developmental run asked whether a hard-bucket decoder inspired by the
historically motivated 34-slot model could identify a compositional reading of
the public, f84/f84r-free GDT605/GDT606 stream. Its executed architecture was:

- Every one of the 34 primitive signs receives exactly one role:
  18 literal carriers, 4 syllabic carriers, 3 prefix operators, 3 suffix
  operators, 2 connectors, 2 contextual abbreviation marks, 1 wholeform
  logogram, and 1 layout/null sign.
- A 64-rule, 98-unit directed merge tree backs off recursively left-to-right to
  its components. An exact merge can override that backoff, but there are at
  most 8 exact overrides and at most 4 wholeform overrides.
- The single null must account for at most 3% of train leaf mass.
- The exact unit `qok` can never receive a wholeform override. It can receive a
  short compositional override; otherwise it backs off into `q`, `o`, `k`.
- Prefix, suffix, context-adjacency, and output-length violations are penalized.
  The historical exterior tendencies enter only as a small directional prior,
  not as fixed translations.
- The train objective is real-vs-within-word-order-destroyed character-order
  margin, plus a small independent-reference lexicon reward, minus grammar,
  overlength, and codebook costs. Chunk types receive square-root frequency
  weights. Each deterministic simulated-annealing fit uses 60,000 proposals.

The executable never opens a Held file. Only `primitives.tsv`, `units.tsv`, the
train chunk table, and an independent reference pack enter fitting. `evaluate.py`
loads Held material only after every fitted key has been written.

This is not the exact GDT609 implementation. Although a byte-identical
`model_v1.json` was copied into the run, the decoder never parses it. It
hard-fixes all bucket counts and one active null, replaces the published FST
with violation penalties, gives connector and wholeform the same transition,
guards only exact `qok`, and injects lexicon-derived wholeword candidates and a
lexicon bonus. The run is therefore a heuristic pilot, not a negative test of
`HISTORICAL_MIXED_ABBREVIATION_FST_34_V1`.

## Inputs and blinding

The route snapshot and only the primary GDT605, GDT606, and GDT608 method/report
files were read before implementation. Target material came exclusively from the
already published safe artifacts:

- `experiments/yolo/gdt605_multisymbol_unit_alphabet/artifacts/gdt605_bpe_merges.tsv`
- `experiments/yolo/gdt606_mixed_nomenclator_decoder/artifacts/guarded_rows.tsv`
- `experiments/yolo/gdt606_mixed_nomenclator_decoder/artifacts/unit_sequences.json`
- `experiments/yolo/gdt608_compositional_stem_orientation/artifacts/merge_tree.tsv`

Their expected SHA-256 values are sealed in `prepared/MANIFEST.json` and checked
again by `validate.py`. The stream contains 68 train and 23 Held physical folios:

| partition | chunks | unit events | observed unit types |
|---|---:|---:|---:|
| train | 20,336 (5,582 distinct) | 43,335 | 98 |
| Held | 9,838 | 21,679 | 97 |

The target evaluator covers all 9,838 chunks, all 255 paragraphs, and all 23 Held
folios in every run. No page, folio, or locus selector begins with `f84` or
`f84r`; the validator also checks the guarded source artifact directly. No
Voynich target plaintext, published key, or target translation enters any step.

Independent language references are the same hash-pinned Caesar Latin, Dante
Old Italian, and five MHG4SNA Middle High German texts documented in
`prepared/reference_meta.json`. Their word order is independently destroyed
within words to make the language-internal null packs.

## Synthetic known-key calibration

Before interpreting the target, the unchanged decoder was run on a legal known
Latin mixed code. The generator uses the same 34 roles, candidate pools, merge
tree, eight exact overrides, four wholeforms, null rule, and `qok` guard. The
truth decoder reproduces 3,639/3,639 Held words exactly. There are 14,553 train
events (4,326 types) and six deterministic reconstruction starts.

| calibration metric | range over 6 starts |
|---|---:|
| exact primitive roles | 9–15 / 34 |
| exact primitive role + output | 0–4 / 34 |
| exact truth overrides | 0 / 8 in every start |
| exact Held words | 0–3 / 3,639 (0–0.0824%) |
| normalized Held character similarity | 12.23–17.05% |
| pairwise exact primitive agreement between restarts | 13.73% mean |

This is not a valid inverse calibration. Direct exposure audit finds four
primitive assignments—`F`, `K`, `f`, `i`—and the `dy` override with zero train
events. Ten output values also collide across truth items; in particular `F`
and the `ok` override both emit `t`, while connector `f` and wholeform `y` both
emit `in` and follow the same decoder transition. Exact recovery is therefore
partly impossible even before optimization. The binary and settings were then
applied unchanged to the target, but there was no automatic calibration gate;
the target phase is an archived exploratory stress run only.

## Oracle objective audit

An independent Python implementation reproduces all six recorded C++ objective
values with maximum absolute error below `5e-12`. Scoring the planted truth
under that same objective gives:

| key | objective / sqrt weight | score without prior | exact primitive role+output | exact overrides |
|---|---:|---:|---:|---:|
| planted truth | 1.914535 | 1.926591 | 34 / 34 | 8 / 8 |
| six wrong fits, range | 3.114952–3.386643 | 3.121073–3.396049 | 0–4 / 34 | 0 / 8 |

Every fitted wrong key beats truth by `1.200417–1.472108` normalized units.
Truth ranks 7th of 7. The objective—not merely the annealing budget—rewards
pseudokeys. More restarts or more iterations cannot make the planted truth win
under this scoring rule.

## Target design

For each of Latin, Old Italian, and Middle High German the archived pilot ran:

- six real-order starts (18 primary fits total);
- three within-word-order-destroyed starts (9 null fits total);
- 60,000 deterministic proposals per start;
- train-only fitting, followed by a separate 23-folio evaluator.

`held_order` below is the evaluator's real-minus-destroyed fourth-order
character likelihood in bits per emitted letter. `held_lexicon` is the fraction
of emitted letters inside exact words from the independent reference pack.

| language / fit | starts | Held order min / mean / max | Held lexicon min / mean / max |
|---|---:|---:|---:|
| Latin / real | 6 | 3.571 / 3.864 / 4.214 | 53.48% / 71.85% / 84.11% |
| Latin / destroyed | 3 | -11.291 / -11.101 / -10.732 | 0.000% / 0.002% / 0.007% |
| Old Italian / real | 6 | 3.064 / 3.809 / 4.418 | 46.33% / 61.93% / 79.52% |
| Old Italian / destroyed | 3 | -12.530 / -12.412 / -12.291 | 0.005% / 0.011% / 0.017% |
| MHG / real | 6 | 3.818 / 4.542 / 5.164 | 45.16% / 58.77% / 72.82% |
| MHG / destroyed | 3 | -12.085 / -11.928 / -11.757 | 0.000% / 0.002% / 0.005% |

This is not a matched real/null contrast. A destroyed fit reverses the language
model orientation **and** receives a separately destroyed candidate inventory;
the evaluator nevertheless always reports real-minus-destroyed score and tests
lexicon coverage against the real lexicon. In each condition the self-oriented
mean is positive: `3.809–4.542` for real fits and `11.101–12.412` for destroyed
fits. The table therefore says that both conditions learned what they were
explicitly optimized to prefer, not that the target selected a language.

All fitted outputs are selected from their scored reference packs, and the Held
cipher preserves carrier frequencies from train. All 18 real runs place their
dominant Held token on a connector or wholeform primitive; all 18 tokens are
exact reference words present in the injected candidate pool. The mean dominant
token share is 22.17%. A high-frequency carrier can therefore emit an injected
high-frequency word and generalize its order score without identifying meaning.

## Exact carrier stability

Stability is evaluated over all 15 pairs of the six real starts per language.
An exact mapping requires both role and emitted output to match. A Held word span
requires the same source record, outer-unit start/end, word ordinal, and output
in all six starts.

| language | primitive role pairwise | primitive role+output pairwise | 98-unit output pairwise | unanimous primitive outputs | unanimous unit outputs | unanimous Held word spans |
|---|---:|---:|---:|---:|---:|---:|
| Latin | 44.71% | 9.02% | 4.90% | 0 / 34 | 0 / 98 | 0 |
| Old Italian | 42.94% | 7.25% | 4.49% | 0 / 34 | 0 / 98 | 0 |
| MHG | 42.75% | 9.61% | 5.51% | 0 / 34 | 0 / 98 | 0 |

Exact stable Held source-position coverage is 0.000% in every language. Both
`stable_unit_reference_outputs.tsv` and `stable_held_spans.tsv` therefore have a
header and no finding rows. The number of restart-stable concrete meanings is
exactly **zero**.

Twelve primitive *roles* are unanimous, but none has a unanimous output. Most
are generic literal-carrier assignments. The only especially relevant exterior
role is MHG `y` as suffix in 6/6 starts, yet its output splits `oy` versus `ex`
3/3. This is structural support only, not a translation.

### Requested anchor audit

- `C`: no unanimous role in any language and no stable output.
- `d`: connector in 5/6 Latin starts, heterogeneous in Old Italian, literal in
  6/6 MHG starts (`r` versus `l`, 3/3). No cross-language or exact output.
- `y`: suffix only in MHG 6/6; heterogeneous elsewhere; no stable output.
- `o`: connector in 3/6 Latin, wholeform in 5/6 Old Italian, heterogeneous in
  MHG; no stable output.
- `ol`: six different complete outputs in each language; no stable output.
- `qok`: the hard wholeform prohibition passes. Only two Old Italian starts use
  a short override (`ve`, `e`); all other real starts back off compositionally.
  Its complete output differs in every start and carries no stable meaning.

Thus the historical opener/closer/connector expectations do not jointly select
a key. The most favorable observation (`y` as an MHG suffix) is language-local
and output-free.

## Output degeneracy and the best full Held paragraph

Real fits heavily overconcentrate on a few lexicon entries:

- Latin top-token share is 15.18–23.90% and top-10 share 66.89–78.94%; the
  reference values are 2.48% and 13.03%. Typical dominant outputs are `has`,
  `germanos`, `auxilio`, and `vix`.
- Old Italian top-token share is 18.44–25.37% and top-10 share 64.11–76.39%; the
  reference values are 4.79% and 23.34%. Typical dominant outputs are `lume`,
  `padre`, and `dicendo`.
- MHG top-token share is 15.79–29.50% and top-10 share 54.81–74.48%; the
  reference values are 3.02% and 18.91%. Typical dominant outputs are `doz`,
  `disiu`, and `gedahte`.

These are frequency-carrier assignments surrounded by short generated strings,
not coherent passages. The evaluator nevertheless selects and reports the
complete Held paragraph with the highest order margin among paragraphs of at
least 50 emitted letters. It is MHG seed 3103, `f103r:p18`, page `f103r`, three
lines, 178 letters, order margin 6.34193 bits/letter, lexicon-character coverage
27.53%:

> royy / oytex / roy doz olex / royoex / roytex / oyroex / royroyex / doz o disiu q / oyt disiu doz nex || n disiu ex / royoylex / royo disiu q / zam lex / royoex / oylex / royoex / royoex / doz oylex / doz oytex || l zam ex / roytyex / l disiu poylex / royoyex / roytex

Even the objectively best paragraph is repetitive and non-semantic. Its high
score is explained by a few attested MHG tokens embedded in mechanically regular
fragments. It is not restart-stable: the same source paragraph receives a
different reading under every other start.

## Capacity and runtime

All 27 target fits contain exactly the prescribed 34-role inventory. Active
target overrides range from 4 to 8; every real fit uses four wholeform overrides.
Maximum observed null leaf mass is 2.9308%. The `qok` wholeform gate passes.
One Latin run leaves 26/9,838 chunks empty; all other target fits decode every
chunk nonempty.

With 12-way process parallelism, individual 60,000-proposal target jobs take
20.50–24.74 seconds (597.69 summed job-seconds). The six synthetic jobs take
31.04–32.18 seconds each (190.40 summed job-seconds). Outer evaluation takes
about 21 seconds on this host.

## Interpretation and next route

This heuristic decoder is invalidated. The planted control is undercovered and
non-identifiable, the objective explicitly prefers all six wrong keys to truth,
the target control is asymmetric, and the executed transitions differ
materially from GDT609. The missing fix is not another lexicon, a larger
wholeform budget, or longer annealing. The objective must first make a fully
observed planted truth outrank matched mutations under the exact intended FST.

Do not promote the positive Held-order margin, `y` suffix role, or any dominant
reference word as a translation. A future extension must first recover the
synthetic primitive and merge key to a prospectively fixed threshold and must
beat the present zero-span stability result without using Held selection.

The next run must: generate coverage-certified collision-free controls; parse
and execute `model_v1.json`; distinguish connector, wholeform and context
transitions; remove exact-word injection and lexicon bonus from the primary;
use a proper length/frequency-sensitive generative or MDL objective; and compare
real/destroyed conditions with one frozen candidate inventory and one score
orientation. Target fitting is forbidden until oracle truth beats all declared
mutations and multiple synthetic starts recover the truth equivalence class.

## Reproduction and artifacts

Core source:

- `experiments/yolo/gdt612_historical_fst34_target_attack/src/full/prepare.py`
- `experiments/yolo/gdt612_historical_fst34_target_attack/src/full/make_synthetic.py`
- `experiments/yolo/gdt612_historical_fst34_target_attack/src/full/decoder.cpp`
- `experiments/yolo/gdt612_historical_fst34_target_attack/src/full/run_all.py`
- `experiments/yolo/gdt612_historical_fst34_target_attack/src/full/evaluate.py`
- `experiments/yolo/gdt612_historical_fst34_target_attack/src/full/summarize.py`
- `experiments/yolo/gdt612_historical_fst34_target_attack/src/full/full_validate.py`

The published `artifacts/` directory contains the prepared manifests, complete
34/98-unit tables, all six synthetic keys, all eighteen real-order target keys,
the synthetic truth/held control, every compact evaluation table, and the best
paragraph. The large per-run decode tables are omitted; their paths, byte sizes
and hashes remain in `FULL_RUN_MANIFEST.tsv`. The compact validator independently
reconstructs every zero-stability claim directly from the published keys and
the canonical GDT606 held stream.

`oracle_objective_audit.py` reconstructs the exact truth-versus-pseudokey
ranking. `method_audit.py` reconstructs truth exposure/collisions, control
orientation, candidate-pool counts and all 18 dominant-token injections from
the compact result and reference-pack artifacts.

Run the compact audit with:

```sh
python3 experiments/yolo/gdt612_historical_fst34_target_attack/src/validate.py
```

`FULL_REPRODUCTION.md` gives the clean scratch-directory commands for fetching
the hash-pinned references, recompiling the C++ fitter and repeating all 33
fits without writing generated corpora or decodes into the repository.

A clean rerun of that published route completed successfully. Its canonical
`synthetic` and `target` result payloads are byte-identical after canonical JSON
serialization; only elapsed-time fields and hashes of the path-portability
edits differ. `artifacts/REPRODUCTION_CHECK.json` records both payload hashes.

The original full-run validator reports `VALIDATION_OK`; the published compact validator independently reconstructs the key, objective, method, stability and paragraph claims and passes **268/268** checks.
