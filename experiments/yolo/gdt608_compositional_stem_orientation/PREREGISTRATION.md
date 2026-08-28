# GDT608 collapsed-unit compositional role attack

Frozen before the comprehensive held-folio analysis.  This is an exploratory
train-to-held falsifier, not a blind preregistration: the preceding independent
GDT606 role attack already exposed held summaries for `o`, `ol`, `or`, `ot`,
and several high-frequency controls.  No new outcome-dependent endpoint may be
added after this file.

## Scope

- Read only the already guarded, f84/f84r-free GDT605/GDT606 artifacts.
- Use the exact 64 ordered BPE rules as the composition tree; do not infer
  substring decompositions not present in `gdt605_bpe_merges.tsv`.
- Analyze all 64 direct merges, with nominated contrasts `o+l=ol`, `o+r=or`,
  `o+k=ok`, `o+t=ot`, `d+y=dy`, and `a+N=aN` reported regardless of result.
- Preserve the inherited 68-train/23-held physical-folio split.
- Structural roles only.  No generated Latin/Italian/MHG output, workshop
  meaning, sound, lexeme, POS, plaintext, or English gloss is admissible.

## Pinned inputs

- `gdt605_bpe_merges.tsv`:
  `4625c9389ead390907e4ac74e65bc158236f02b439c69cf3b09157f0cd6ca539`
- `gdt605_unit_inventory.tsv`:
  `ade74733200e941ddc66285988eb1498ac98e87ad374cad11ac412ce42893e82`
- `gdt605_unit_result.json`:
  `c2d293c121f1ee01fe0ddcbe4647c77f5f94796b4ecc4b1adc554cc2f740c3d9`
- `guarded_rows.tsv`:
  `d6674f3d54edc49590c884b5d703cb032b966c1abd4da6338093795ce1f31ef9`
- `unit_sequences.json`:
  `3ee0841e211314b72719acbbf79ed3a6dc7bfc3c157734f54dbdac92ac458fdf`
- `complete_mappings.tsv`:
  `005ddec8e5b67763c9ccfd1d3244e44c1e68d8c0c6c46a2c7d7edcc36fa4aabe`
- Latin category table:
  `2a43d309b78392781ab9111c00dcead82424d648ad820fd02f1479dbb33e7997`
- Old Italian category table:
  `069023255a729b0918f7298ca5482f9bfa6fa1815541098f801db7ddc4704169`
- Middle High German category table:
  `998a6f093584f26321bc4e4ef2f88171ff245383eecb786adde7fe98733e81b5`

## Observation layer

Reconstruct every final-unit event from `unit_sequences.json`.  Immediate
neighbours never cross hard chunks.  Physical-line edges come from ordered
chunks at one locus.  Paragraph edges use only existing IVTFF `<%>`/`<$>`
markers in guarded rows.  For every unit and split retain:

- standalone, chunk-initial/final, line-initial/final, and paragraph-initial/
  final rates;
- exterior left/right neighbour distributions;
- section, hand, Currier-code, and physical-folio distributions;
- train occurrence count and effective train-folio fraction.

## Models

All distributions use Jeffreys/Dirichlet smoothing `alpha=0.5` over the frozen
training vocabulary.

1. **GLOBAL:** pooled train feature distributions, with no unit identity.
2. **ATOMIC:** the merged unit's own train distribution predicts that same
   unit's held events.
3. **DIRECT-COMPOSITION:** for a registered merge `L+R=M`, exterior-left,
   chunk/line/paragraph-initial predictions come from `L`; exterior-right and
   corresponding final predictions come from `R`.  Section, hand and Currier
   predictions are the normalized geometric mean of `L` and `R`.  Standalone
   probability is the geometric mean of their standalone probabilities.
4. **SWAPPED:** the same rule with `L` and `R` reversed; this is the directional
   null.
5. **LOMO-RIDGE:** for each edge rate separately, a leave-one-merge-out ridge
   regression (`lambda=1`) learns from the other 63 train merge profiles using
   left/right component logits and log frequencies, then predicts the held
   rate of the omitted merge.  It cannot use that merge's atomic train rate.

Primary event-level endpoints are held mean bits/event for left/right exterior
neighbours and the six initial/final Bernoulli edge indicators, reported per
feature and jointly.  Secondary endpoints are mean absolute error of the seven
rates (including standalone), per-merge log-loss advantages, pairwise
Jensen-Shannon distances, and LOMO coefficient direction.

## Controls and nulls

- **Frequency/mobility-matched component-pair null:** for each of 1,000 fixed-
  seed replicates, replace every real component pair by a donor pair sampled
  from the eight nearest other merges in standardized train log frequency and
  train effective-folio fraction.  Held outcomes stay fixed.  Report the
  empirical tail for the real direct-composition score.
- **Matched-frequency atomic controls:** each merged unit is paired, with
  replacement, to the nearest-frequency unit that is not the output of any of
  the 64 rules.  Compare train-to-held profile drift; this calibrates stability
  caused merely by event count.
- **Existing GDT606 destroyed-reference null:** relate composition advantage to
  36-real-start and 12-destroyed-start W fractions.  This is diagnostic only;
  exact outputs are prohibited.  A W association that disappears after
  frequency adjustment is architectural, not semantic.
- Report every merge, not only successful families.  Direct left-stem or
  right-stem families require at least three registered children.

## Decision rules

- **Strong compositional code:** DIRECT-COMPOSITION beats GLOBAL, SWAPPED, and
  the matched mobile null and is no worse than ATOMIC by more than 0.02 joint
  bits/feature/event.
- **Partial compositional backoff:** DIRECT-COMPOSITION beats GLOBAL and the
  mobile null with empirical `p<=0.05`, but ATOMIC remains better by more than
  0.02 bits/feature/event.
- **Atomic/residual code:** ATOMIC wins and DIRECT-COMPOSITION does not beat the
  matched mobile null, or stable individual counterexamples dominate.
- A **stable stem-side role** needs at least three direct children, positive
  held directional advantage over SWAPPED in at least 75% of children, and a
  family aggregate advantage beyond its mobile null.  It is named only by the
  observed edge/context tendency, never semantically.
- Any nominated pair with a held sign opposite its train/composition
  prediction is reported as a counterexample.  No post-hoc repair, merge-tree
  rewrite, or semantic reinterpretation is allowed.
