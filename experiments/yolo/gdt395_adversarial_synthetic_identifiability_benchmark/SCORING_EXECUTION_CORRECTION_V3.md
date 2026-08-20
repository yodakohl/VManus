# GDT395 scoring execution correction V3

Status: `FROZEN_BEFORE_SCORING_V3`

The gzip-corrected V2 scorer ingested the blind event claims, then stopped on
the first train-only world-level architecture claim. The frozen decoder API
allows blind structural hypotheses rather than requiring Boolean literals;
the five decoders emitted a mixture of booleans, probabilities, HIGH/LOW, and
`UNRESOLVED`. The original scorer admitted only Boolean text. V2 stopped before
the scorer's explicitly marked first sealed-oracle access and wrote no score
artifact.

V3 retains the V2 gzip transport correction and aligns world-claim handling to
the independently frozen aggregate validator:

- TRUE/HIGH and FALSE/LOW are Boolean predictions;
- probabilities in `[0,1]` use the validator's frozen `0.5` threshold;
- MEDIUM/UNRESOLVED are abstentions;
- architecture clustering and the language/notation/codebook proxy endpoints
  are `UNSCORED` because no valid family/mapping was frozen;
- only the W10 semantics-light diagnostic is scored, using the validator's
  frozen adversarial abstention completion.

This changes no event-level claim, split, oracle allow-list, representation,
property metric, threshold, decision rule, or output schema. The correction is
frozen and validated before V3 scoring. No synthetic oracle, Voynich source, or
f84 data was opened in diagnosing or freezing it.

