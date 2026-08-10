# `cho/che` independent co-switch capacity audit

## Purpose

Determine whether the already validated `ch/sh+o/e` page-side state has a
fair, source-native route for testing additional formal changes.  This is not
the closed paragraph-scope experiment: that experiment scored the defining
`o/e` choice itself.  The proposed successor will score only formal material
outside every group containing a defining `ch/sh+o/e` site.

The validated state is a **physical page-side** state (`f68r`, `f68v`, and so
on), not a state assigned once to an entire recto-verso leaf.  A physical leaf
is the held-out and permutation unit.

## Frozen inputs

- `results/parisel_cho_che_folio_states.tsv`, SHA-256
  `4c713c379b33d04985c0efbf9dd4025cb810a9c1006975f7855ed6cc52ff381c`
- `results/parisel_cho_che_source_audit_validation.json`, SHA-256
  `17009e151704d91f795216eed0913cfece447a396d08234df9af46624f286f3b`
- `results/source_separator_transcription.tsv`, SHA-256
  `4b649c8290d5afc7a5fbcc8e98db2bc123a1ceb5f3858d3befa781ce96b680f0`
- `results/source_separator_transcription_validation.json`, SHA-256
  `8698a2643219fd8ab00b05bba8705a1f1e8219c9b468824fbe2dc92117043deb`
- `results/source_sta_group_alignment.tsv`, SHA-256
  `f23654f1d4c854db6d458b418a0d3530115731604854cf0a0495565e58341840`
- `results/source_sta_group_alignment_validation.json`, SHA-256
  `cc53d32646b21e4135f0b23d98662e10835307ad860d021ea8c487261d7646fd`

ZL3b, IT2a, and RF1b are alternate readings of one manuscript.  They are
required to agree on every primary page-side state; they are never counted as
three replications.

## Score-blind construction

Use only the source-valid `SOURCE_ALL_SEPARATORS` EM assignment.  Collapse
numbered panels to their physical page side and retain a leaf only when:

1. recto and verso are both present;
2. all three readings agree on each side's state;
3. the two sides have opposite states;
4. at least one exact `(section, Currier, hand, kind, grammar_scope)` cell is
   represented on both sides in every reading after the exclusions below.

Within those leaves, retain only source groups with one clean ASCII fragment,
zero registered STA alternatives, and no literal `ch` or `sh` immediately
followed by `o` or `e` anywhere in the group.  This last rule is deliberately
stronger than replacing the defining symbol: the entire defining group is
removed.

Store only IDs, fixed metadata, page-side state, formal length, page-position
quartile, and group-position class.  Do not store or score raw surfaces, STA
codes, STA family sequences, target-family values, effects, classifiers,
feature directions, or p-values.

## Capacity gates

- all three validated readings and exactly 600 source-valid state rows;
- at least 196 all-reading-agreed page sides;
- at least eight eligible opposite-state physical leaves common to all
  readings;
- at least three high-recto and three high-verso leaves;
- at least five leaves containing confirmed prose and at least two containing
  diagnostic/nonprose material;
- at least 1,600 eligible groups in each reading and at least 30 groups on
  every retained page side;
- exact metadata-cell overlap on both sides of every retained leaf;
- a synchronous leaf-flip orbit of at least 256, giving an attainable
  one-sided floor no larger than `.01`;
- zero defining-site groups, family surfaces, target associations, scores,
  p-values, or English glosses in the capacity artifact;
- independent byte-for-byte reconstruction.

## Authorized successor and frozen claim ceiling

A pass authorizes only a target-free synthetic/power preflight and a separate
preregistration.  The primary future analysis must be leave-one-physical-leaf
out and compare high versus low page sides within each retained leaf.  It must
control recto/verso orientation, exact metadata cells, exact formal length and
position, and a frozen state-blind construction/template baseline.  It must
include:

1. the defining `o/e` choice as a tautological positive control only;
2. strict off-site and canonicalized representations as separate tests;
3. same-state recto/verso leaves, state complement, one-leaf, circle-only,
   prose-only, and alternate-reading controls;
4. synchronous physical-leaf permutations, familywise correction, positive
   minimum deletion, and a concentration cap;
5. an explicit power gate before any independent family/state association is
   opened.

If only the defining control survives and the powered strict-off-site and
canonicalized tests do not, a canonical latent-form representation may be
tested.  If several independent, held-leaf formal families survive all gates,
the state may be retained as a broader formal register/system state.  A
failure without demonstrated power decides neither branch.

No result identifies meaning, sound, wordhood, a language, a cipher,
plaintext, or a translation.
