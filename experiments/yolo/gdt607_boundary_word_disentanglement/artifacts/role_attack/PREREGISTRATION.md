# GDT606 whole-word-category distributional role attack

Frozen before computing target positional/contextual summaries.

## Scope and target

- Read only the already materialized, f84/f84r-free GDT606 artifacts.
- Target units are exactly `ol`, `y`, `C`, `d`, `o`.
- No new page, transcription query, image, workshop value, historical key,
  plaintext output or semantic gloss is admitted.
- `section`, Currier `language`, `hand`, IVTFF paragraph markers and physical
  folio are metadata already present in `guarded_rows.tsv`; section codes stay
  opaque codes.
- Hard chunks and the 98-unit alphabet are exactly those in
  `unit_sequences.json`. Certain/drawing boundaries are never crossed when
  defining local neighbours or masked chunk frames.

## Pinned inputs

- `guarded_rows.tsv`: `d6674f3d54edc49590c884b5d703cb032b966c1abd4da6338093795ce1f31ef9`
- `unit_sequences.json`: `3ee0841e211314b72719acbbf79ed3a6dc7bfc3c157734f54dbdac92ac458fdf`
- `complete_mappings.tsv`: `005ddec8e5b67763c9ccfd1d3244e44c1e68d8c0c6c46a2c7d7edcc36fa4aabe`
- Latin all-grid categories: `2a43d309b78392781ab9111c00dcead82424d648ad820fd02f1479dbb33e7997`
- Old Italian all-grid categories: `069023255a729b0918f7298ca5482f9bfa6fa1815541098f801db7ddc4704169`
- Middle High German all-grid categories: `998a6f093584f26321bc4e4ef2f88171ff245383eecb786adde7fe98733e81b5`

### Pre-analysis refreeze amendment

The first freeze named the then-present unit-sequence hash `cc71af...d728`
and observed that `binding_inventory.json` still described an older run.  The
input guard fired before any target statistic was computed: GDT606 completed
its deterministic rerun, wrote the final `3ee084...fdf` unit sequence and a
matching binding inventory/247-check validation.  The final hash above is the
operative pin.  All other pinned inputs stayed byte-identical.  The validator
must fail if any of them drift again.

## Observation layer

Every unit occurrence receives, without looking at category output:

- split, page, physical folio, locus, section, Currier code and hand;
- chunk length/index, only/initial/final/interior status and normalized slot;
- line unit count/index, first/last status and normalized quartile;
- paragraph-start/end line and within-paragraph line position derived only from
  existing IVTFF `<%>`/`<$>` markers;
- immediate within-hard-chunk left/right units, target adjacency, self-repeat;
- exact masked chunk frame (replace only the focal occurrence with `*`).

## Tests

1. Category trace: real-primary, all-real-grid and destroyed-reference W rates
   for every target unit and language.
2. Standalone and position: target-by-position contingency, odds against the
   five nearest-frequency non-target controls, separately on train and held.
3. Neighbours and substitution: left/right distributions, target adjacency,
   masked-frame sharing, pairwise Jensen-Shannon distances and a multinomial
   classifier trained on the existing train folios and evaluated on held
   physical folios.  Report accuracy, balanced accuracy, log-loss gain over the
   train-prior baseline, confusion and 200 label permutations within
   section×hand×chunk-position strata.
4. Concentration: section/Currier/hand contingencies, per-folio rate dispersion,
   effective folio count, Gini and pairwise folio-distribution JS distances.
5. Stability: every directional conclusion must be reported separately on
   train and held; a pooled effect with a held sign reversal is not stable.
6. Architecture control: relate all-real W fraction over all 98 units to log
   frequency and structural features, and compare target W rates to destroyed
   reference keys.

## Role predictions and decision rule

These are compatibility profiles, never translations.

- **Function-word-like:** broad folio/section dispersion, high neighbour
  diversity, substantial shared-context substitution, no strong label/formula
  boundary fixation.
- **Number/measure-like:** target-target adjacency or repetition at least 2x
  the matched-control rate plus shared slot contexts; internally the data
  cannot distinguish number from measure without an external scale.
- **Material-like:** stable section/folio concentration and specific recurrent
  neighbours, usually chunk-internal/final rather than line-initial.
- **Action-like:** train and held line- or chunk-initial odds at least 1.5 and
  directional left/right asymmetry.
- **Recipe-formula-like:** train and held line/paragraph boundary enrichment or
  repeated exact masked-frame concentration at least 2x controls.
- **Person/plant-name-like:** high folio/section clustering plus standalone or
  label-boundary enrichment and low mutual substitution; person versus plant
  is not identifiable without independent visual ownership.

If held balanced target-identity accuracy is <=0.35 and pairwise local-context
JS is uniformly small, one exchangeable default role may be nominated.  If
accuracy is >=0.50 or stable pairwise structure separates units, report
subroles or a nonsemantic architecture/frequency alternative instead.  A role
must satisfy its stated train-and-held predictions; otherwise it is rejected.
