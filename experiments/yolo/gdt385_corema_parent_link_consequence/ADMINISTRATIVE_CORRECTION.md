# GDT385 administrative manifest correction

After the scientific score was exposed, the repository's structured
`experiment.json` schema became mandatory. The original public pre-score freeze
is commit `68244b6`; its exact administrative manifest hash remains recorded in
`gdt385_pre_score_freeze.json` and is reconstructed by the freeze validator
from that public commit.

The live `experiment.json` was migrated only to the repository-wide schema and
artifact index. No scientific method, route, threshold, input, source/outcome
definition, fold, null, score, result, or claim was changed. The final scorer
continues to consume the unchanged pre-score freeze artifact.
