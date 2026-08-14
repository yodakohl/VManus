# GDT003 nested held-folio replication report

Status: **LIMITED/LOCAL COMPOSITION ONLY**

## Result

This replication removes the main selection weakness in the first GDT003 run.
Each of 102 outer folds excluded a complete physical folio, discovered
its added/replaced edge strings from training types only, selected operations
within the frozen edit-length strata, froze compatible operation pairs, and
then predicted exact types on the unseen folio.

The nested algebra made 1,017,225 distinct fold-target predictions
and recovered 925 exact unseen-folio types. Precision was only
0.000909336676. Its average precision
was 0.007898874356; the strongest string baseline
was 0.002828273522. The difference was +0.005070600834.
The 4,096-world within-folio label-permutation comparison gave
`p=0.000244081035` for algebra minus the best string
baseline.

## Same-candidate baseline comparison

| model | predictions | exact | AP | AUC | top-1 | top-5 |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| NESTED_PARADIGM | 1017225 | 925 | 0.007898874356 | 0.710101117195 | 4 | 5 |
| CHARACTER_ORDER2_KT | 1017225 | 925 | 0.002828273522 | 0.642458578149 | 1 | 2 |
| CHARACTER_ORDER4_KT | 1017225 | 925 | 0.001734562695 | 0.609551951302 | 1 | 2 |
| VISIBLE_WHOLE_GROUP_FREQUENCY | 1017225 | 925 | 0.000980285710 | 0.481946905973 | 0 | 0 |
| NEAREST_EDIT_DISTANCE | 1017225 | 925 | 0.001400497469 | 0.606451844130 | 0 | 2 |


The GDT001 context mixer remains a stronger complete-source model, but it is
not assigned an invented isolated-target score because its probabilities
depend on canonical serialized context.

## Training-discovered q plus right-edge subgroup

The named subgroup was not forced into any fold. The rules had to survive the
same training-only support and stratum selector as every other edge edit.
It generated 9,754 candidates and 25
correct held-folio completions. Paradigm AP was
0.002865533134;
the subgroup's strongest string AP was 0.051233255237, a difference of
-0.048367722103.

Fold survival counts for the previously discussed operations are recorded in
`gdt003_nested_result.json`; survival means only that the rule was rediscovered
from that fold's training corpus. It does not assign operator or suffix status.

## Exact model-hidden completions

| held folio | visible cells | predicted fourth | learned operations | held locus | q/right | prior-nine |
| --- | --- | --- | --- | --- | ---: | ---: |
| f1 | `dsho`, `ksho`, `dshoy` | `kshoy` | `PREFIX_REPLACE:d>k` + `SUFFIX_ADD:y` | f1r.12 | 0 | 0 |
| f1 | `keol`, `lkeol`, `kody` | `lkody` | `PREFIX_ADD:l` + `SUFFIX_REPLACE:eol>ody` | f1v.2 | 0 | 0 |
| f1 | `chod`, `okod`, `chodar` | `okodar` | `PREFIX_REPLACE:ch>ok` + `SUFFIX_ADD:ar` | f1v.2 | 0 | 0 |
| f1 | `dchar`, `schar`, `dchody` | `schody` | `PREFIX_REPLACE:d>s` + `SUFFIX_REPLACE:ar>ody` | f1v.10 | 0 | 0 |
| f1 | `cho`, `sho`, `choshy` | `shoshy` | `PREFIX_REPLACE:c>s` + `SUFFIX_ADD:shy` | f1v.5 | 0 | 0 |
| f10 | `aiin`, `chaiin`, `air` | `chair` | `PREFIX_ADD:ch` + `SUFFIX_REPLACE:iin>ir` | f10r.2 | 0 | 0 |
| f10 | `cthody`, `chcthody`, `cthor` | `chcthor` | `PREFIX_ADD:ch` + `SUFFIX_REPLACE:ody>or` | f10v.2 | 0 | 0 |
| f10 | `saiin`, `osaiin`, `sain` | `osain` | `PREFIX_ADD:o` + `SUFFIX_REPLACE:iin>in` | f10r.10 | 0 | 0 |
| f10 | `cthol`, `qocthol`, `ctholy` | `qoctholy` | `PREFIX_ADD:qo` + `SUFFIX_ADD:y` | f10r.6 | 0 | 0 |
| f100 | `okeey`, `cheokeey`, `okeol` | `cheokeol` | `PREFIX_ADD:che` + `SUFFIX_REPLACE:ey>ol` | f100v.21 | 0 | 0 |
| f100 | `als`, `dals`, `alsy` | `dalsy` | `PREFIX_REPLACE:a>da` + `SUFFIX_ADD:y` | f100v.9 | 0 | 0 |
| f100 | `cheeol`, `okeeol`, `cheeos` | `okeeos` | `PREFIX_REPLACE:ch>ok` + `SUFFIX_REPLACE:ol>os` | f100r.16 | 0 | 0 |
| f100 | `cheo`, `olcheo`, `cheom` | `olcheom` | `PREFIX_ADD:ol` + `SUFFIX_ADD:m` | f100r.19 | 0 | 0 |
| f101 | `okal`, `dokal`, `okor` | `dokor` | `PREFIX_ADD:d` + `SUFFIX_REPLACE:al>or` | f101v.5 | 0 | 0 |
| f101 | `dar`, `odar`, `dariin` | `odariin` | `PREFIX_ADD:o` + `SUFFIX_ADD:iin` | f101r.7 | 0 | 0 |
| f101 | `qockhdy`, `shckhdy`, `qockheol` | `shckheol` | `PREFIX_REPLACE:qo>sh` + `SUFFIX_REPLACE:dy>eol` | f101v.27 | 0 | 0 |
| f101 | `chot`, `shot`, `chotey` | `shotey` | `PREFIX_REPLACE:c>s` + `SUFFIX_ADD:ey` | f101r.7 | 0 | 0 |
| f101 | `choraiin`, `soraiin`, `choraly` | `soraly` | `PREFIX_REPLACE:ch>s` + `SUFFIX_REPLACE:iin>ly` | f101v.9 | 0 | 0 |
| f101 | `qopchol`, `ypchol`, `qopcholy` | `ypcholy` | `PREFIX_REPLACE:qo>y` + `SUFFIX_ADD:y` | f101r.7 | 0 | 0 |
| f102 | `choldy`, `koldy`, `cholor` | `kolor` | `PREFIX_REPLACE:ch>k` + `SUFFIX_REPLACE:dy>or` | f102r2.8 | 0 | 0 |
| f102 | `odal`, `oldal`, `odeey` | `oldeey` | `PREFIX_REPLACE:o>ol` + `SUFFIX_REPLACE:al>eey` | f102v2.31 | 0 | 0 |
| f102 | `lor`, `otor`, `lory` | `otory` | `PREFIX_REPLACE:l>ot` + `SUFFIX_ADD:y` | f102v2.8 | 0 | 0 |
| f102 | `cheear`, `qoeear`, `cheeol` | `qoeeol` | `PREFIX_REPLACE:ch>qo` + `SUFFIX_REPLACE:ar>ol` | f102v1.20 | 0 | 0 |
| f102 | `or`, `qoor`, `orar` | `qoorar` | `PREFIX_ADD:qo` + `SUFFIX_ADD:ar` | f102r1.8 | 0 | 0 |
| f102 | `oteeey`, `sheeey`, `oteeody` | `sheeody` | `PREFIX_REPLACE:ot>sh` + `SUFFIX_REPLACE:ey>ody` | f102v2.31 | 0 | 0 |

First 25 of 925 broad-algebra hits are shown. All exact hits, including the independently deduplicated q/right hits, are in `gdt003_nested_correct_predictions.tsv`.


These are computationally hidden predictions of already-public readings, not
new manuscript evidence. The editions are alternate observations, not three
replications.

## Falsification assessment

- The actual transformation strings were learned independently in every fold;
  global GDT003's nine templates were not supplied.
- Every candidate target was absent from its training corpus.
- The comparison uses identical candidates for paradigm, KT2, KT4,
  visible-cell frequency, and nearest-edit scores.
- The broad selector emits over a million candidates and therefore has very
  low absolute precision. The decisive quantity is the same-candidate AP
  advantage `+0.005070600834`, not attractive exact forms alone.
- f84r remained sealed: no retained record, operation, candidate, or score uses
  its formal payload.
- No `q`, `dy`, `dal`, or `dar` meaning, morpheme, POS, language, or translation
  follows.

## Conclusion

The nested test asks a stricter question than the original GDT003 result: can
the algebra itself be rediscovered without the target folio and then outperform
ordinary string statistics? The answer is encoded by the same-candidate AP
comparison and the preregistered decision above.

LIMITED/LOCAL COMPOSITION ONLY
