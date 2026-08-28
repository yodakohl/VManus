# GDT606 W-category distributional role attack

## Decision

**`MULTIPLE_STABLE_FORMAL_SUBROLES__NO_SHARED_SEMANTIC_DEFAULT`**

The deterministic GDT606 trace that `ol`, `y`, `C`, `d`, and `o` enter the
decoder's whole-word output category does not define one exchangeable lexical
or semantic class.  On the inherited 68-train/23-held physical-folio split,
the identity of those five units is recoverable from context with held balanced
accuracy 0.6456, versus a conditional permutation mean of 0.3221
(`p=0.004975`).  Immediate neighbours alone reach 0.6493; section/hand/Currier
metadata alone reaches only 0.2224.  All ten held pairwise identity AUCs are
0.8502--0.9875.

The strongest alternative is architectural.  Across all 98 units, the
all-real W fraction correlates with frequency rank at Spearman 0.7306 and with
effective neighbour count at 0.6108, but correlates negatively with literal
standalone-chunk rate at -0.1351.  Four non-target units (`ar`, `s`, `or`, `k`)
also receive W in at least 31/36 real configurations.  Conversely, five
qok-family units that occur as a complete one-unit hard chunk in 97.2--98.9%
of pooled occurrences receive W in 0/36 real configurations.  GDT606 W is
therefore primarily a high-frequency/high-mobility output-capacity bucket, not
an observed "whole-form" property and not a word meaning.

The defensible defaults are structural tags only:

| unit | stable formal default | held anchor | strongest semantic compatibility, not identification |
|---|---|---:|---|
| `C` | strict hard-chunk opener/local head | chunk-initial 0.6934; chunk-final 0.0056 | action/formula head only at local chunk scale |
| `d` | hard-chunk and physical-line head carrier | chunk-initial 0.4992; line-initial 0.1759 | action-head-like or formula-head-like |
| `y` | hard-chunk, line, and occasional paragraph closure carrier | chunk-final 0.6390; line-final 0.2347; paragraph-final 0.0415 | recipe/formula-closure-like |
| `ol` | boundary and occasional standalone carrier | chunk-final 0.5463; standalone 0.1433 | weak formula-boundary/function compatibility |
| `o` | flexible bidirectional connector | chunk-initial 0.3120; chunk-final 0.2989; 34.46 effective neighbour types | function-word-like connector |

None of these tags is a translation, sound, part of speech, action, ingredient,
number, measure, name, or plaintext token.

## Scope, provenance, and sealed-data discipline

This attack reads only the completed GDT606 artifacts in
`experiments/yolo/gdt606_mixed_nomenclator_decoder/artifacts`.  It does not run
a new transcription query, open an image, add a page, inspect any forbidden
selector, or use historical/workshop meanings.  Section codes remain opaque.
The only page-side metadata used is the already guarded page, physical folio,
section, Currier code, hand, line number, locus, and IVTFF paragraph markers.

The source materialization used the guarded command shape

```text
./vmanus-exp query-tsv transcription/voynich_zl3b_lines.tsv
  --selector page
  --allow <each of 180 explicit values>
  --forbid-prefix f84
  --columns page,locus,line_number,section,language,hand,eva_clean,ivtff_raw
```

The exact 180 allowed values, physical-folio bindings, and inherited split are
in `guarded_page_selection.tsv` (SHA-256
`44094942f412ae956f9a793fc2b447233251c79f61700f06689fb61c78e1312c`).
Their allow-list source is `gdt327_joint_tuple_interlinear.tsv`, SHA-256
`7eba46774be44992064cc114f67329723ac7bf589321b0d763fb7f7f748cc1e9`.
The result has 180 page selectors, 91 physical folios, 68 train folios, 23 held
folios, and no page whose lower-case selector begins `f84`.

Pinned analysis inputs are:

| input | SHA-256 |
|---|---|
| `guarded_rows.tsv` | `d6674f3d54edc49590c884b5d703cb032b966c1abd4da6338093795ce1f31ef9` |
| `unit_sequences.json` | `3ee0841e211314b72719acbbf79ed3a6dc7bfc3c157734f54dbdac92ac458fdf` |
| `complete_mappings.tsv` | `005ddec8e5b67763c9ccfd1d3244e44c1e68d8c0c6c46a2c7d7edcc36fa4aabe` |
| Latin category table | `2a43d309b78392781ab9111c00dcead82424d648ad820fd02f1479dbb33e7997` |
| Old Italian category table | `069023255a729b0918f7298ca5482f9bfa6fa1815541098f801db7ddc4704169` |
| Middle High German category table | `998a6f093584f26321bc4e4ef2f88171ff245383eecb786adde7fe98733e81b5` |

An initial pre-analysis hash guard caught GDT606 while its final deterministic
rerun was still replacing the unit-sequence artifact.  It aborted before any
target statistic was computed.  The preregistration was amended to the final
`3ee084...fdf` binding only after the completed GDT606 binding inventory and
247-check source validation agreed.  All other pins were byte-identical.  This
report and validator use only that final binding.

## Observation layer and counts

Certain spaces and drawing interruptions are inherited as hard chunk
boundaries; uncertain separators were already joined by GDT606.  Immediate
neighbours and masked frames never cross a hard chunk.  Here `standalone` means
only “the reconstructed hard chunk contains exactly one of the 98 units”; it
does not assert a manuscript word boundary.

Paragraph position is inferred only from already present `<%>` and `<$>`
markers.  Physical-line position uses the guarded locus.  No layout or image
interpretation is introduced.

| quantity | value |
|---|---:|
| guarded rows | 4,165 |
| hard chunks | 30,174 (20,336 train; 9,838 held) |
| all unit events | 65,014 (43,335 train; 21,679 held) |
| reconstructed paragraphs | 725 |
| target events | 10,277 (7,094 train; 3,183 held) |
| alphabet | 98 train units; 97 held units; zero held-only units |

The five target counts pooled are `ol` 2,537, `C` 2,156, `y` 2,108, `d`
1,741, and `o` 1,735.  Frequency controls were selected once by a monotone
minimum-total-absolute-log-frequency assignment among non-target units:
`ol→ar` (2,189), `C→or` (1,857), `y→s` (1,808), `d→aN` (1,725), and `o→ot`
(1,722).  No outcome or semantic label entered that match.

## Null construction

Three distinct controls address three distinct failure modes.

1. **GDT606 destroyed-reference category null.**  For each language, four
   primary starts use the existing within-word-order-destroyed reference.  The
   target stream and category capacity are unchanged.  These runs test whether
   W membership is forced by capacity/frequency even when reference order is
   destroyed.
2. **Frequency-matched structural controls.**  Every standalone, edge,
   repetition, frame, and target-adjacency rate is compared train and held to
   the five non-target controls above.  This prevents common units from looking
   special merely because they recur widely.
3. **Conditional identity null.**  A categorical multinomial Naive Bayes model
   is fitted only on target occurrences in the 68 train folios.  Held
   predictions remain fixed while true labels are shuffled 200 times within
   `section × hand × chunk-position` strata (seed `60620260828`).  This retains
   coarse metadata/position imbalance and destroys residual unit-specific
   context.  The resulting balanced-accuracy null is 0.32205 ± 0.00731; its
   elevation above the five-class chance value 0.2 is expected because the
   conditioning intentionally preserves coarse label structure.

Feature ablations isolate local neighbours, position, and metadata.  The
predeclared shared-role rejection threshold was held balanced accuracy at
least 0.50 or stable pairwise context separation; both are exceeded.

## GDT606 category trace

All five targets are W in all six primary real starts for every reference
language.  Across all 12 real starts per language (the primary grid plus the
capacity-sensitivity grids), the trace is:

| language | `ol` | `y` | `C` | `d` | `o` |
|---|---:|---:|---:|---:|---:|
| Latin | 12/12 | 12/12 | 11/12 | 11/12 | 12/12 |
| Old Italian | 12/12 | 12/12 | 12/12 | 12/12 | 12/12 |
| Middle High German | 12/12 | 12/12 | 11/12 | 11/12 | 12/12 |

In the four destroyed-reference primary starts per language:

| language | `ol` | `y` | `C` | `d` | `o` |
|---|---:|---:|---:|---:|---:|
| Latin | 4/4 | 4/4 | 1/4 | 3/4 | 0/4 |
| Old Italian | 4/4 | 3/4 | 4/4 | 3/4 | 4/4 |
| Middle High German | 4/4 | 4/4 | 0/4 | 3/4 | 0/4 |

Thus `ol`, `y`, and `d` remain strongly W-prone under the destroyed reference;
`C` and `o` retain some real-order sensitivity outside Old Italian.  Neither
pattern supplies a meaning: exact GDT606 outputs are restart-unstable and are
deliberately not used here.

## Architecture and the literal-standalone counterclass

The GDT606 category grid has exactly 11 W slots in every key.  An audit over all
98 units gives these associations with all-real W fraction:

| pooled feature | Spearman | Pearson |
|---|---:|---:|
| log occurrence count | 0.73065 | 0.42214 |
| effective neighbour types | 0.61081 | 0.52121 |
| folio effective fraction | 0.50956 | 0.41992 |
| section effective fraction | 0.32976 | 0.25415 |
| standalone hard-chunk rate | -0.13513 | -0.19605 |

Non-target W fractions over the 36 real starts are `ar` 34/36, `s` 33/36,
`or` 31/36, and `k` 31/36.  Those rates overlap the targets (`C` and `d`
34/36; `ol`, `y`, and `o` 36/36), so the target set is not exclusive.

The strongest direct counterexample to reading W literally is:

| unit | train standalone | held standalone | pooled mean chunk length | W in real starts |
|---|---:|---:|---:|---:|
| `qokaI` | 0.9851 | 1.0000 | 1.0109 | 0/36 |
| `qokaN` | 0.9947 | 0.9444 | 1.0267 | 0/36 |
| `qokEdy` | 0.9894 | 0.9714 | 1.0340 | 0/36 |
| `qokedy` | 0.9838 | 0.9839 | 1.0202 | 0/36 |
| `qokEy` | 0.9664 | 0.9776 | 1.0565 | 0/36 |

These units are almost literal one-unit chunks, have only 2.07--2.19 effective
neighbour types, and are much less frequent (pooled ranks 63--73).  GDT606
assigns them letter/digraph-like categories rather than W.  This inversion is
what a fixed-capacity optimizer selecting frequent carriers predicts; it is
not what an observed word-boundary classifier predicts.

## Position and exact formal defaults

| unit | split | standalone | chunk initial | chunk final | line initial | line final | paragraph initial | paragraph final |
|---|---|---:|---:|---:|---:|---:|---:|---:|
| `C` | train | 0.0042 | 0.6907 | 0.0104 | 0.0235 | 0.0014 | 0.0007 | 0.0000 |
| `C` | held | 0.0028 | 0.6934 | 0.0056 | 0.0141 | 0.0000 | 0.0028 | 0.0000 |
| `d` | train | 0.0192 | 0.6355 | 0.1914 | 0.2080 | 0.0533 | 0.0044 | 0.0035 |
| `d` | held | 0.0067 | 0.4992 | 0.1977 | 0.1759 | 0.0469 | 0.0084 | 0.0050 |
| `y` | train | 0.0438 | 0.2728 | 0.7111 | 0.1512 | 0.2503 | 0.0026 | 0.0296 |
| `y` | held | 0.0397 | 0.3321 | 0.6390 | 0.2220 | 0.2347 | 0.0054 | 0.0415 |
| `ol` | train | 0.1205 | 0.3699 | 0.5271 | 0.0362 | 0.0696 | 0.0016 | 0.0093 |
| `ol` | held | 0.1433 | 0.4045 | 0.5463 | 0.0295 | 0.0407 | 0.0014 | 0.0028 |
| `o` | train | 0.0311 | 0.3357 | 0.2327 | 0.1012 | 0.0453 | 0.0036 | 0.0036 |
| `o` | held | 0.0263 | 0.3120 | 0.2989 | 0.0591 | 0.0279 | 0.0049 | 0.0033 |

The train/held directions do not reverse.  Against their matched controls:

- `C` has chunk-initial odds ratios 6.78 train and 6.74 held, but line-initial
  odds 0.82 and 0.47.  Its default is therefore a **local hard-chunk opener**,
  not a physical-line formula head.
- `d` has chunk-initial odds 9.55 and 4.32 and line-initial odds 615.39 and
  79.33 against `aN`, whose line-initial rate is effectively zero.  Its exact
  default is a **hard-chunk/physical-line head carrier**.  “Action-head-like”
  is compatible, but indistinguishable from a structural or formula head.
- `y` has chunk-final odds 4.34 and 2.70, line-final odds 4.15 and 4.95, and
  paragraph-final odds 2.78 and 4.74 against `s`.  Its exact default is a
  **closure carrier**.  “Recipe/formula-closure-like” is compatible, although
  the absolute paragraph-final rate is only 3.0--4.2%.
- `ol` has the highest target standalone rate, but only 1.25 and 1.32 times the
  odds of matched `ar`; repeated-frame odds are 1.03 and 0.92.  It is a
  **boundary/occasional-standalone carrier**, not a fixed formula or label.
- `o` is balanced between both chunk edges, with 39.43 train and 34.46 held
  effective neighbour types.  Its standalone odds exceed `ot`, but the
  absolute rate is only 3.1% and 2.6%.  It is a **flexible bidirectional
  connector**, the only function-word-like default in this set.

## Local neighbours

The following are held-folio distributions; boundary markers are analytical
hard-chunk boundaries, not semantic tokens.

| unit | most common left contexts | most common right contexts |
|---|---|---|
| `C` | BOS .693; `p` .051; `l` .037 | `ar` .082; `al` .063; `ok` .063; `Ky` .056; `d` .055 |
| `d` | BOS .499; `Ce` .104; `e` .080; `C` .065; `E` .064 | EOS .198; `air` .109; `am` .087; `ol` .059; `ai` .054; `or` .054 |
| `y` | BOS .332; `qok` .060; `ar` .054; `o` .049; `t` .045 | EOS .639; `Ce` .045; `S` .031; `p` .029 |
| `ol` | BOS .404; `p` .053; `E` .052; `d` .049; `Se` .049 | EOS .546; `aN` .038; `dy` .028; `Cedy` .028 |
| `o` | BOS .312; `Ce` .125; `E` .076; `e` .049; `Se` .046 | EOS .299; `daN` .095; `m` .076; `N` .051; `y` .044 |

This directional structure is the main source of cross-folio identity
recovery.  It separates `d`, `y`, and `o` especially sharply and makes one
mutual-substitution class untenable.

## Mutual substitution and held-folio prediction

The full train-only classifier obtains held accuracy 0.6503, balanced accuracy
0.6456, and log loss 1.4822 bits/event.  The frozen train-prior log loss is
2.3340, so the held gain is 0.8518 bits/event.  Diagonal held recalls are `ol`
0.5028, `y` 0.5993, `C` 0.9086, `d` 0.6164, and `o` 0.6010.

| features | held balanced accuracy | held gain over train prior, bits/event |
|---|---:|---:|
| local neighbours only | 0.6493 | 1.0511 |
| position only | 0.4100 | 0.2749 |
| metadata only | 0.2224 | -0.0737 |
| all features | 0.6456 | 0.8518 |

Held pairwise AUCs are:

| pair | AUC | pair | AUC |
|---|---:|---|---:|
| `ol/y` | 0.8931 | `ol/C` | 0.9540 |
| `ol/d` | 0.9200 | `ol/o` | 0.8502 |
| `y/C` | 0.9875 | `y/d` | 0.9112 |
| `y/o` | 0.9315 | `C/d` | 0.9779 |
| `C/o` | 0.9687 | `d/o` | 0.9002 |

Across the ten pairs, held median Jensen-Shannon divergence is 0.2848 bits for
left neighbours, 0.4364 for right neighbours, and 0.1325 for chunk position.
Median masked-frame Sørensen overlap is only 0.1011.  By contrast, section JS
has median 0.0178 and folio JS 0.0617.  Local role separation is strong while
coarse manuscript-location distributions mostly overlap.

## Sections, hands, Currier codes, and folios

Every target occurs on every one of the 23 held physical folios.  Held
effective-folio fractions are `ol` 0.808, `y` 0.868, `C` 0.738, `d` 0.756,
and `o` 0.679; largest single-folio shares are 0.103--0.164.  Held effective
section fractions are 0.447--0.631.  These are broad carriers, not folio-local
labels.

Held target-identity association is weak for section (Cramér's V 0.1045), hand
(0.0853), and Currier code (0.0828), but much larger for hard-chunk position
(0.3289).  Section-specific exposure-normalized rates exist—for example `o`
is 43.0 per 1,000 events in section P and `C` is 50.4 in H—but the metadata-only
classifier fails held transfer and gives negative information gain.  The codes
therefore cannot support a section-derived material, action, or name meaning.

No safe image evidence was already bound into GDT606 beyond these page/locus
metadata.  Introducing page illustrations would violate this attack's no-new-
page/no-new-image scope, so no visual ownership claim is made.

## Targeted semantic-role falsification

These decisions apply to the preregistered compatibility profiles, not to all
conceivable uses of an unknown notation.

| proposed role | decisive train/held evidence | decision |
|---|---|---|
| one shared function-word class | held local-neighbour balanced accuracy 0.649; frame overlap median 0.101 | reject shared class; retain only `o` as connector-like |
| number/measure | target adjacency 0.154/0.136 vs controls 0.210/0.212; odds 0.685/0.587; self-neighbour also lower | reject; no serial/slot signature; number vs measure remains externally unidentifiable |
| material | all five occur on all held folios; folio JS median 0.062; metadata classifier 0.222 | reject as default material class |
| action | `d` passes train/held chunk- and line-initial thresholds; `C` passes only chunk scale | compatible for `d`, locally for `C`; action vs formula/structural head not identifiable |
| recipe formula | target-group paragraph-final odds 0.950/0.733 and repeated-frame odds 0.646/0.508; only `y` has stable final enrichment | reject shared/fixed formula; retain `y` as closure-like and `ol` as weak boundary carrier |
| person/plant name | target standalone 0.049/0.046 vs controls 0.097/0.089; all held folios; weak metadata | reject; person vs plant remains externally unidentifiable |

The target group also has lower exact-frame repetition than controls (0.614 vs
0.712 train; 0.522 vs 0.683 held) and lower within-class adjacency.  High raw
paragraph repeat rates are a frequency artifact: the frequency-matched controls
are nearly as high, and the held group odds are 0.93.

## Final interpretation

The GDT606 W trace survives as a useful warning about the decoder architecture,
not as a concrete semantic reading.  A fixed 11-slot W inventory repeatedly
absorbs common, mobile units and mixes at least three formal subroles:

1. head/opening carriers (`C`, `d`), with `d` extending to physical-line heads;
2. closing/boundary carriers (`y`, `ol`), with `y` extending to line and weak
   paragraph closure;
3. a flexible connector (`o`).

The qok-family counterclass shows that genuinely standalone reconstructed forms
can be assigned zero W slots, while frequent non-targets enter W.  Accordingly,
no internal distributional statistic here identifies any default word meaning.
The exact output-category result is also conditional on GDT606's fixed W
capacity of 11; a separate boundary-category/capacity experiment is required
to determine which carriers move when W competes with an explicit boundary
class.  This report does not anticipate or import that result.

## Reproducibility artifacts

- `PREREGISTRATION.md`: frozen predictions and the pre-analysis refreeze note.
- `src/context_role_attack.py`: end-to-end reconstruction, controls, classifier, and
  deterministic conditional null.
- `guarded_page_selection.tsv`: exact selector/folio/split list.
- `target_occurrences.tsv`: all 10,277 target events with structural context.
- `target_structural_summary.tsv`, `top_neighbors.tsv`, `metadata_rates.tsv`,
  `folio_rates.tsv`: position and location evidence.
- `category_trace.tsv`, `architecture_unit_audit.tsv`,
  `standalone_counterclass.tsv`: category/architecture evidence.
- `group_vs_frequency_controls.tsv`, `unit_vs_matched_control.tsv`,
  `pairwise_substitution.tsv`, `classifier_confusion.tsv`: null and held tests.
- `default_role_table.tsv`, `role_hypothesis_tests.tsv`: exact decisions.
- `RESULT.json`, `ARTIFACT_MANIFEST.json`: compact machine-readable result and
  analysis-output hashes.
- `src/validate_roles.py`, `VALIDATION.json`: independent count/hash/decision checks.
