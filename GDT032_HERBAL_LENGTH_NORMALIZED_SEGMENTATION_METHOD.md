# GDT032 Herbal length-normalized segmentation

GDT032 is a fixed follow-up to GDT031. It reuses the eight published Herbal
Currier-A/B page pairs and their human illustration/layout matching without
rematching on the outcome. Each page belongs to a distinct physical folio on
both sides. Four pairs have affirmative `ALPHA`/`MIXED` profiles and four are
jointly `UNCLASSIFIED`.

Three one-sided B-minus-A tests separate segmentation from line length:

1. `DY_PER_100_GROUPS`: DY checkpoints divided by all source groups;
2. `INTERNAL_BOUNDARIES_PER_100_POSSIBLE`: DY checkpoints followed by another
   group on the same physical line, divided by all possible internal group
   gaps, `sum(groups_in_line - 1)`;
3. `EXACT_LENGTH_STANDARDIZED_FIELDS_PER_LINE`: inside each GDT031 page pair,
   lines are stratified by exact source-group count. At every shared length the
   A and B mean compiled-field counts are contrasted and weighted by the
   smaller line count. Shared-length strata are then averaged within the page
   pair. Page pairs, not lines, are the sign-flip units.

A compiled field is the frozen GDT020 construction: every DY-closed segment
plus a nonempty open tail, or one field on a line without a checkpoint. The
three primary p-values receive Bonferroni correction. The four affirmative
visual-profile pairs are reported separately without substituting for the
full fixed match.

This test can establish length-normalized formal segmentation density only.
Currier remains perfectly confounded with hand in this Herbal sample. The
frozen GDT016 inventory contains no f84r row; no annotation or transcription
source is opened beyond the existing f84r-free artifacts. No role, record
meaning, word, sound, language, plaintext, or translation is inferred.
