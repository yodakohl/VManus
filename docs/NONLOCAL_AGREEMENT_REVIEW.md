# Nonlocal ending agreement: what the proposed count can identify

2026-09-06. IP021 source/design review, not a new manuscript experiment.
No source-corpus query, image access, model fit or inferential score was run.
Published examples are exposed discovery material, not held confirmation.

## Actual motivating passages

[GDT611 REPORT](../experiments/yolo/gdt611_lexical_slot_permutation_audit/REPORT.md)
prints these complete EVA displays from f111v:p1:

```text
f111v.8  sho otchey cheol kechy chcthey okain ol l keey qokain checkhy chedar am
f111v.23 qokaiin sheckhy qokar chalkain chckhedy lcheol okaiin qokain cheol daiin lam
```

The first contains `okain [ol l keey] qokain`; the second contains
`qokaiin [sheckhy qokar chalkain chckhedy lcheol] okaiin`. These matching
endings and different intervening sequences are real published observations.
The second line also contains the unequal adjacent pair `okaiin qokain`
and the unequal pair `qokain cheol daiin`. A procedure that jumps past an
unequal candidate to select a matching one has not independently identified
a grammatical partner. These displays do not establish a new all-reader
agreement claim or the physical character segmentation.

[GDT627 REPORT](../experiments/yolo/gdt627_value_head_role_atlas/REPORT.md)
already reports near pairs within three token positions:33 lines,30
reader-stable pairs and20 same working ending values;9of13 adjacent pairs
match. Its quality names and numerical meanings are not adopted as gold.
Thus another near-pair inventory alone would repeat an existing observation.
The predecessor's `make_axis_pairs()` in
[src/run.py](../experiments/yolo/gdt627_value_head_role_atlas/src/run.py)
enumerates all cross-family candidates at distances1–3, not a best partner.

## Why counting all partners does not solve selection

For one line and two distinct literal head families A and B, let n_A(e)
and n_B(e) count occurrences with ending e. If all A-to-B occurrence pairs
are eligible, the number with equal endings is exactly

```text
M_all = sum_e n_A(e) * n_B(e).
```

This is an identity: each A occurrence with e pairs with every B occurrence
with e. It uses no positions, intervening text, direction or dependency.
For example, both sequences below have two equal cross-family pairs:

```text
A0 B0 A1 B1
A0 B1 A1 B0
```

Their adjacent cross-family matches differ (two versus one), but their
all-pair count is identical. The toy labels are illustrative mathematical
objects, not assigned Voynich meanings or newly observed manuscript forms.

If “far” simply means all such pairs except those within a fixed near radius,
then, for that line inventory,

```text
M_far = M_all - M_near.
```

Under a null that preserves each line's family-by-ending inventory, a far
excess measured by this unweighted match count is exactly a near deficit.
It cannot by itself identify selective coordination of distant partners.
The statement concerns these particular counts, not every possible statistic
of distance, order, repeated constructions or independently located partners.

If instead a null moves endings between lines on the same folio, it changes
those inventories. A positive result can then reflect a shared line-specific
preference, topic, production state or grammatical agreement. That would be
a different, weaker claim about common line composition. It would not isolate
nonlocal grammar merely because immediate neighbors were excluded.

## Decision and scope

Do not implement the proposed all-partner count as a test of nonlocal
agreement. The observed passages remain useful discovery examples, including
their unequal alternatives. A genuinely selective partner prediction needs
an independently motivated written relation or an order-sensitive prediction
whose alternatives are distinguished before seeing the target outcomes.
This review does not invent such a rule, declare that agreement is absent,
or require a word translation before any further structural discovery.

[GDT273](../GDT273_Q13_FIELD_SEQUENCE_GRAMMAR_REPORT.md) tested coarse adjacent
field sequences; [GDT344](../experiments/yolo/gdt344_grammar_transition_paths/REPORT.md)
tested adjacent formal-tuple transitions. Their failures do not generally
disprove literal nonlocal dependencies. Conversely, changing their model or
IL026's unsuccessful null calibration would not cure the identity above.

The proof and counterexample are the complete analytic artifact. They are
not a preregistered empirical result or an additional GDT trial. This design
screen prevents an uninformative fit; it supplies no deciphered word.
An independent agent obtained the same count identity and toy counterexample;
root checked the primary near-pair implementation. No statistical validation
or new manuscript count is claimed by that conceptual cross-check.
