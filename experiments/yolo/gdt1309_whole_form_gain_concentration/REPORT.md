# GDT1309: the whole-form gain is spread across many exact forms

**FIXED_SCORE_CONCENTRATION_ACCOUNTED.** The20largest positive whole-form
contributors supply about one quarter of1308's positive type contribution,
not most of it. In ZL3b,66positive types cover half and287cover90%. This is
an exact post-result accounting of the unchanged predictor, not a new held
experiment, a fitted smaller wordbook or a minimum lexicon size.

| Reading | Positive-net types | Top20share of positive mass | Types for50% | Types for90% |
|---|---:|---:|---:|---:|
|ZL3b|644|25.013%|66|287|
|IT2a|704|24.125%|72|311|
|RF1b|611|24.295%|69|270|

Reader agreement is sensitivity within one manuscript. Ranking forms on already
scored evaluation outcomes is explicitly descriptive. A small reusable grammar
could explain many of these forms; the table does NOT prove287independent
exceptions, mental dictionary entries or source meanings are needed. It does
show that the existing fixed gain should not be described as only a handful
of unusually frequent whole forms.

## Exact gain accounting

Every occurrence retains its original1308score and its original equal-leaf
weight: on leaf f withN_feligible words amongLleaves, contribution is
log(MIX/M1)/(L*N_f). Sum occurrences of the exact same unit tuple to getC_w.
Sum allC_wto recover the original gain. No word is removed and no predictor,
probability, leaf denominator or mixture weight is refitted.

| Reading | Sum of positive type contributions | Sum of negative type contributions | Original net gain, nat/word |
|---|---:|---:|---:|
|ZL3b|+.297040|−.209690|+.087350|
|IT2a|+.284445|−.213825|+.070620|
|RF1b|+.306645|−.218912|+.087732|

Shares in the first table divide by POSITIVEtype mass, not the much smaller
net gain. Dividing by net can give percentages above100%because gains and losses
cancel. A form may have positive occurrences in one Currier cell and negative
ones in another; all are combined into its signed type contribution. The TSV
also retains positive/negative occurrence mass separately.

The TRAIN-selected20most frequent forms give original contributions
+.032295/+.031763/+.041488in ZL/IT/RF. Their complements still contribute
+.055055/+.038857/+.046245under the UNCHANGEDoriginal weights. This is not a
new out-of-sample score after deleting20words, nor a tested20-entry model.

## Frequency bands and manual form inspection

ZL's complete frequency accounting illustrates why frequency alone is not
the explanation. Frequency here means total eligible TRAINcount across its
Currier cells; it is not the full manuscript profile or a substring count.

| TRAINfrequency | Held types | Held occurrences | Original signed contribution |
|---|---:|---:|---:|
|0|1351|1592|−.172216|
|1|336|569|+.052894|
|2–4|299|773|+.050533|
|5–19|187|1742|+.087588|
|20–99|44|1673|+.043770|
|100+|10|1279|+.024782|

All bands, readers and every negative contribution are retained in artifacts.
Rare TRAIN-known forms can gain strongly relative to a very small M1probability;
that does not make them frequent, semantically important or independently confirmed.
Globally unseen forms keep their negative contribution, including1308's declared
empty-cell fallback. No post-result exclusion rescues the score.

Post-result inspection of exact forms, with existing `words profile` retrieval
used to keep the broader word distributions in view:

- `daiin` contributes most in all three readings; ZLheld193occurrences span40leaves.
- `qoky` is among the top3in all three. ZLTRAIN46, held41on17leaves. This is the
  standalone whole, not the inner qoky string in qoteytyqoky or a sound assignment.
- `oeees` has only1eligible TRAINoccurrence and4held occurrences in each reader.
  Three held CurrierAoccurrences gain strongly; the CurrierBoccurrence loses
  because that cell hasQ=0. In ZL the Aprobabilities areM1=.000022746 and
  Q=.001890359, giving+3.738959nats per occurrence; Bcost is−log(2).
- `doiir` is a strong ITcontributor with1TRAINoccurrence and3held occurrences.
  ZL/RFhave no eligible TRAINoccurrence and therefore lose on their2/3held
  occurrences. The isolated ITspike is not promoted across readers. The full
  profile and the strict eligible TRAINpanel are different populations.

The five working units o/e/e/e/s are not a demonstrated stem/suffix analysis,
number or e-lengthening rule. No word meaning is proposed. Smallcounts,
transcription conventions, Currier cells and original leaf weighting remain
visible instead of turning a high score into an interpretation.

## Avoided repeated experiment

A suggested first-unit-to-last-unit followup was stopped BEFORE any new model
or target run. The direct predecessor is
`experiments/semantic_assumptions/SOURCE_NATIVE_EDGE_COUPLING_TEST_SPEC.md`:
alpha.5predicts the last STAfamily from second and penultimate families,
min(length,8), locus position and Currier; the full model adds the first family.
Its target report gives−.058951nat/group and13/94positive leaves, with validated
nonconfirmation and an explicit no-retuning decision.

The contemplated22-unit odd/even variant would also REMOVEthe second-unit
control. A positive result could then merely reflect that the first unit
predicts the second, which in turn relates to the ending.1308does not justify
that reopening. GDT283's separate endpoint-negative standard diagnosis and
GDT318's line/previous-DYwrapper effect retain their different scopes. The older
productive FIRST/LASTgrammar concerns groups at LOCUSedges, not the two ends
inside a word. These observations are now explicitly distinguished in a curated
review of the old coupling result; no old payload, model or experiment was rerun.

## Decision and reproducibility

Keep the whole-form predictive constraint, including its broad contribution
pattern and the complete cost of new words. Do not replace it by a claim that
a few exceptional high-frequency abbreviations have explained the signal.
Likewise do not require one arbitrary lexical value for every positive form.
A proposed simple construction must still supply an independently stated
combination/selection rule and its behavior on new combinations. No such new
writer or translation was established by this accounting.

The source hash lock precedes this decomposition. Separate code recomputes all
23496log-ratio scores from saved probabilities, checks6983reader-specific type
rows, every frequency-band/rank/coverage total and all conservation identities.
PASS verifies the attribution, not a selected miniature model or semantic truth.
Both programs are root-authored independent implementations. No new raw corpus,
image, model fitting, significance test or reserve access. f84/f84rremain sealed;
f116v/f1rbody and old327/336body remain unopened. The fixed40minute total budget
covers14:35:15–15:15:15UTC, including preparation, validation and publication.
