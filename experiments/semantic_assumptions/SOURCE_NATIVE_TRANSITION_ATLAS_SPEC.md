# Held-folio source-family transition atlas

Status before family-pair inspection: **FROZEN_DESCRIPTIVE_DECOMPOSITION**

## Distinct question

The exact-position-controlled target already confirms an aggregate local
dependency. This atlas does not retest that claim. It asks which physical
left/right STA-family adjacencies carry stable held-folio excess or depletion
after exact position is controlled. No pair identity or pair statistic was
inspected before freezing the rules below.

Use all 21,899 strict complete confirmed-prose source groups on 94 physical
folios. For each physical folio and each orientation, fit a Dirichlet-.5
baseline on every other folio for `P(current | Currier, complete length, exact
ordinal position)`. Score only positions `j>=1` in the held folio. For each
previous family `p` and candidate current family `y`, store observed count,
baseline-expected count, previous-family opportunities, and held-folio excess
rate `(observed - expected) / opportunities`.

The manuscript-order physical pair `left,right` is evaluated as `left->right`.
The fully reversed view is evaluated as `right->left`. The observed adjacency
count must be identical. A physical pair receives a structural label only when
both views independently meet the same rule; orientation-specific diagnostics
remain stored but cannot promote a label.

## Frozen classification

A held folio is eligible for a context family only with at least five context
opportunities. Require at least 12 eligible folios in each orientation.

`FAVORED_ADJACENCY` requires, in both orientations:

- observed count >=30 and expected count >=10;
- `log((observed+.5)/(expected+.5)) >= log(2)`;
- positive held-folio excess in at least 75% of eligible folios;
- in each Currier register, at least 30 context opportunities, expected count
  >=5, and log observed/expected ratio >=log(1.3).

`DISFAVORED_ADJACENCY` requires, in both orientations:

- expected count >=30;
- `log((observed+.5)/(expected+.5)) <= -log(2)`;
- negative held-folio excess in at least 75% of eligible folios;
- in each Currier register, at least 30 context opportunities, expected count
  >=10, and log observed/expected ratio <=-log(1.3).

All other pairs are `UNRESOLVED`. These are fixed descriptive stability rules,
not pairwise p-values or a separately confirmatory family scan.

## Bindings and ceiling

Freeze masked panel
`16d7395ae0410c8fc72b5e5462d6d425cd3a2685e7ea70eee0677bd936106ae5`,
source groups
`a202d93498e8a350a5d7e0ca46e831dcc37ea5c0182dc404d63cb797a98b1225`,
source validation
`fcb6a53461b4f9df36f34161ed1d42087f4395988bea0d71f74a7dd635b68b76`,
confirmed exact-position target
`5c59e783919dc35046ad8f941f4ad28e4f272d3e062773a783a6f048c3d8ec33`,
its independent validation
`9f621e977e0640f9f2104e6b0133c898a2802f7ae063ce396e6cb746b6f96282`,
and official STA definition
`7f37853510144fb3e2dc3ee9458d634f41e6d95bc1fbf1c4b8f479a53a021f81`.

The atlas may identify reusable neutral adjacency constraints and official
family-member examples. It cannot choose a spoken direction or establish a
sound, letter, syllable, morpheme, prefix, root, suffix, word, part of speech,
language, cipher operation, meaning, plaintext, or translation.
