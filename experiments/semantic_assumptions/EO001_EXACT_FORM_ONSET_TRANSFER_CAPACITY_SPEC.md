# EO001 exact-form onset-transfer capacity

## Question

Can a complete source-native group form carry the same following-group
construction signature when it occurs inside a physical line that it carries
when it occurs at the line opening?

This is not the earlier `NONE` versus `DA` operation test.  That experiment
held a remainder fixed and varied a short opening operation.  EO001 holds the
entire exact STA-family trigger form fixed and, if later calibration permits,
will test transfer of a trigger-specific continuation signature between two
factual positions.

## Frozen score-blind source and selection

Use only
`results/source_native_structural_interlinear_v1.tsv`, SHA-256
`95a15329c61a11c1c4dc671b4df2b3482af9d25a1108eadac2f69b066d3785af`,
and `results/source_native_group_position_atlas.tsv`, SHA-256
`c062678e85a365f1a4fa54180c10f5337d4b316e6ac5c08461bd851a9a69deff`.

Select all, and only, exact forms labelled `FIRST_ASSOCIATED` in the atlas.
In the strict interlinear retain `CONFIRMED_PROSE` occurrences of those forms
at factual `FIRST` or `CORE` positions, provided that at least one further
group follows the immediate successor (`group_index <= group_count - 2`).
Consequently the immediate successor is factually `CORE` in both states; a
future result cannot be an automatic FIRST-versus-LAST contrast.

Do not inspect, store, summarize, hash by value, or otherwise expose the
immediate successor's family surface, member codes, edge features, path tags,
or lossy EVA in this capacity pass.  The panel may contain only an opaque event
ID, the independently selected trigger form and state, physical-folio and
fixed manuscript metadata, and trigger position/length fields.

Physical folio is the leading `f` plus digits.  ZL3b, IT2a, and RF1b remain
three readings of one event and are not separate capacity rows.

## Capacity gates

Pass only if:

1. the atlas supplies at least six `FIRST_ASSOCIATED` exact forms;
2. every selected form has at least 20 retained events and ten physical folios
   separately in factual `FIRST` and factual `CORE` state;
3. every selected form has at least five physical folios containing both
   states;
4. the complete panel spans at least 60 physical folios and 1,000 events;
5. every row is strict confirmed prose, its factual position agrees with its
   state, and its immediate successor is necessarily factual `CORE` by index;
6. the output schema contains no successor, member-code, edge/path, EVA,
   parser-root, role, semantic, or English-gloss field.

These gates measure geometry only.  They do not authorize opening a successor
outcome.  A separate target-blind preregistration and synthetic
power/exchangeability calibration must first freeze the continuation feature
space, nuisance adjustment, held-folio statistic, exact null, controls,
thresholds, and claim ceiling.

## Claim ceiling

A pass establishes only that exact first-associated group forms have enough
source-native first/core positional alternation for a prospective held-folio
continuation-transfer experiment.  It does not show an embedded onset,
subrecord, clause, phrase, word, part of speech, function, sound, meaning,
plaintext, language, cipher, or translation.
