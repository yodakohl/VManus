# GDT368 direction-label clarification

The first uncommitted scorer pass used a best-single-state contrast to count
same-direction arrays for every multiclass endpoint. Inspection of the leading
`TERMINAL_ARM_COUNT` row showed that this omitted arrays in which the selected
single state did not occur, even though those arrays contributed to the
multiclass conditional mutual information.

Before validation, reporting, or publication, the count endpoints were
corrected to use their frozen natural bin order:

- `MAJOR_BODY_COUNT`: `ONE < TWO < THREE_PLUS`;
- `TERMINAL_ARM_COUNT`: `ZERO_ONE < TWO_THREE < FOUR_PLUS`.

Direction is now the within-array difference in mean ordered bin between
feature-present and feature-absent rows. Any opposite mobile-array direction
prevents `INTERESTING_EXPLORATORY`. Hue remains a categorical best-state
contrast and retains its page-confound rule.

This clarification does not change the visual calls, formal library,
conditional mutual information, 4,096 permutation worlds, local p-values, or
maxT p-values. It changes the leading `ACA` row from an apparent lead to
`UNSTABLE`, because f99v/L1 reverses the count direction seen in f100r/L2,
f89r2/L4, and f99v/L2. No alternate feature was selected after that correction.
