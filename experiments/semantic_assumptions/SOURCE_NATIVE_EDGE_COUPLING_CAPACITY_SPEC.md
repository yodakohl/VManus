# Source-native opening/closing edge-coupling capacity

## Question

Can the first STA family of a synchronized source group predict its last STA
family after immediate core edges, group length, locus position, and Currier
register are fixed?

This asks whether opening and closing morphology combine independently or show
a reusable paired-edge selection relation. It is distinct from adjacent-group
root transitions, first-versus-last classification, the failed smooth internal
coordinate, and fine member-code resolution. It assigns no operator or word
meaning.

## Frozen inputs

- `results/source_sta_family_consensus_groups.tsv`, SHA-256
  `a202d93498e8a350a5d7e0ca46e831dcc37ea5c0182dc404d63cb797a98b1225`
- `results/source_sta_family_consensus_validation.json`, SHA-256
  `fcb6a53461b4f9df36f34161ed1d42087f4395988bea0d71f74a7dd635b68b76`
- `results/source_native_edge_grammar_validation.json`, SHA-256
  `0a87ffb2c23fdc6882887e5a854112d678cb6c1de1946407068462ce91fca712`
- `results/source_native_internal_order_validation.json`, SHA-256
  `f41e44fda5d05fbd44a4fabdcfbec077dccdf045cdbbd6c90dad30794c5cf53a`

## Outcome-masked panel

Retain exact no-alternative `CONFIRMED_PROSE` groups of at least three STA
families. Define locus position as `SINGLE`, `FIRST`, `MIDDLE`, or `LAST`.
Define the baseline cell as:

`(second family, penultimate family, min(length,8), locus position, Currier)`.

The full cell adds the first family. Mask the final family as `#` immediately;
store no final-family outcome or complete surface.

A row is target-eligible when, outside its physical folio, the baseline cell
has at least 20 groups and the full cell at least five. This support test uses
no final-family value.

## Gates and ceiling

- exactly 19,203 masked groups on 94 physical folios;
- exactly 14,955 eligible groups on all 94 folios, including both Currier A and
  B, at least ten opening families, and at least 100 baseline cells;
- every row remasks to exactly one `#`, every target-eligible row meets both
  leave-folio-out support gates, and the schema contains no final-family,
  outcome, score, p-value, or English-gloss field;
- independent nonimporting reconstruction before calibration.

Passing authorizes only synthetic calibration of a leave-folio-out categorical
proper-score increment. It establishes no actual edge coupling, affix,
circumfix, agreement, direction of speech, sound, word, language, cipher
operation, meaning, plaintext, or translation.
