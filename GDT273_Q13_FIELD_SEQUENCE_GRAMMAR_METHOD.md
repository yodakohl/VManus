# GDT273 — q13 field-sequence grammar

## Question

GDT224/226 established a q13 field-size balance resembling structured
practical records, but did not show a transferable sequence syntax. GDT273
tests whether the state of one field predicts the next field on a completely
held physical folio beyond target position and record length.

## Frozen source and representations

Use the f84-free `gdt227_q13_abstract_interlinear.tsv`: 701 ordered fields in
33 records on nine physical folios. Four deterministic formal views are
reported as one family:

1. `SIZE2`: group count `1–2` versus `3+`;
2. `SIZE4`: `1`, `2`, `3–5`, `6+` groups;
3. `END2`: field endpoint `DY` versus `LINE_END`;
4. `JOINT4`: `SIZE2 × END2`.

These are formal states. The former “short-argument-like” and
“instruction-clause-like” names are deliberately not used because GDT255
showed they collapse exactly to field size.

## Held-folio prediction

For every adjacent field pair inside a record, predict the right-hand state.
The baseline is a Dirichlet-1/2 categorical model conditioned on:

- record field-count bin (`1–10`, `11–20`, `21+`); and
- target field relative-position quartile.

The sequence model adds only the previous formal state. Train counts on eight
folios and score the ninth. Report summed held gain in bits and each folio's
contribution. A predictive sequence requires positive total gain and positive
gain on at least six of nine folios.

## Structure-preserving null

Use 4,096 deterministic worlds. In every world, independently permute field
identities within each record while preserving:

- record boundaries and lengths;
- every record's complete multiset of all four state views; and
- every target position/opportunity.

The same field permutation is applied to all four representations. Seed each
world from SHA-256 of `GDT273_Q13_FIELD_SEQUENCE_NULL_V1|<world>`.

For held gains, standardize each representation by its null mean and standard
deviation and report local and max-four inclusive p-values. Also report the
number of equal-state adjacencies. This second diagnostic can reveal ordering
even when the predictive model is too sparse, but endpoint ordering is
explicitly topology-coupled because DY is how the fields were segmented.

The primary family passes only if at least one representation has positive
held gain, at least six positive folios, and max-four p <= 0.05. A repeat-count
effect alone cannot satisfy the predictive gate.

## Claim ceiling

A pass establishes a transferable formal first-order field syntax only. A
failure means the tested state views are not predictively ordered beyond
position and record size; it does not imply ordinary prose or lack of meaning.
No field receives a semantic role, word, language, plaintext, or translation.
No f84r access is authorized or performed.
