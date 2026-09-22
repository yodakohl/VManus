# Independently checked source mapping

22 September 2026. Metadata/schema review only before registration; no split
enumeration or manuscript compatibility execution was performed for this note.

`O` is `experiments/yolo/gdt1023_amulet_complete_typed_assembly/src/SOURCE.json`,
SHA256 `a4afec1925b5561215124df1206d02c152786154756bb80c9a6a38c7470ab155`.
`E` is `research_registry/proposals/raw_f108r_amulet_frozen71_complete_commentary_20260921.json`,
SHA256 `3c55e256c1d389068660a003eea068ad7f8d1690466f1289e7a4e67cc41227c9`.

| Complete input | Exact JSON key | Groups by physical line |
|---|---|---|
| Original P12 projection, f83r.9–17 | O.target.owned_projection.records[].raw | 9,13,10,9,10,10,9,8,6 =84 |
| Original diplomatic ZL3b | O.target.diplomatic_ZL3b.lines[].words | 9,13,10,9,10,10,9,8,6 =84 |
| Original diplomatic IT2a | O.target.diplomatic_IT2a.lines[].words | 9,12,10,9,9,10,9,8,7 =83 |
| Extension diplomatic ZL3b, f108r.45–47 | E.target.complete_raw_record.lines[].words | 11,11,11 =33 |
| Extension diplomatic IT2a | E.target.alternate_IT2a_complete_record.lines[].words | 11,10,11 =32 |

Diplomatic lines retain `source_ids`, `locus`, `start`, `end`, `anchor_eligible`
and `offset`. Projection records contain literal `raw`, `locus` and paragraph
name; they are not diplomatic ZL records. Three known projection substitutions
remain distinct from `{ck}al`, `q{cphh}edy`, `dche[o:?]kedy`. An uncertain raw
group is not cleaned, repaired or assigned the projected word automatically.

O.lexicon has 71 exact-form keys with values `{tag,meaning,status}`.
E.frozen_parent.all_71_lexical_entries_unchanged is exactly equal to it.
E.new_17_lexical_entries has the same value shape and disjoint keys. The union
has 88 keys. Equal terminal tags do not erase different lexical ownership or
independently prove equality of all full denotations.

Original expected streams are O.complete_clauses[].terminal_tags, ordered
C01–C09. They coincide one for one with the nine physical lines, with the
projected lengths above. O.grammar_contract.productions explicitly freezes
these nine patterns. `model.py:compile_program` asserts exact per-line tag
equality, then creates a specified semantic plan. It is not a general parser.

Extension streams are E.complete_new_block_clauses[].terminal_tags, in order:

| Clause | Canonical terminal positions | Canonical physical span |
|---|---|---|
| C10 | 1–6 | .45/G001–G006 |
| C11 | 7–18 | .45/G007–G011 plus .46/G001–G007 |
| C12 | 19–24 | .46/G008–G011 plus .47/G001–G002 |
| C13 | 25–33 | .47/G003–G011 |

The selected decision matches their concatenated 33-terminal stream; these
are not fixed raw-group coordinates after packing. A group can contain a
clause seam. It cannot fuse across an existing space or a physical line.
The source keeps all physical boundaries even though extension tag matching
uses one complete block.

`experiments/yolo/gdt928_multi_anchor_complete_paragraphs/artifacts/PARAGRAPHS.json`
has SHA256 `667ca3ae0705a6bb3ccfcd09ea7ee04e28747e58d810e8fa9379f28c0f4fc89b`.
It is the copied paragraph provenance. Its RF1b list is empty. The existing
extension explicitly records no complete matching RF paragraph. Underlying
owned RF lines do exist, but all nine f83r.9–17 and three f108r.45–47 records
have paragraph_start=paragraph_end=0. Therefore report NO_WHOLE_READER under
this inherited boundary contract; do not manufacture an RF paragraph from
another edition's start/end flags.

For exact per-seam provenance, the already-owned input files are under
`experiments/yolo/gdt915_terminal_lr_phrase_transfer/artifacts/`:
`SOURCE_DISCOVERY_{ZL3b,IT2a,RF1b}.json` for f83r.9–17 and
`SOURCE_EVALUATION_{ZL3b,IT2a,RF1b}.json` for f108r.45–47. Their `lines[]`
contain `metadata.locus` and `groups[]`, with `group_columns` equal to
`source_group_id, source_group_index, ivtff_group_raw, left_separator,
right_separator`. The smaller copied paragraph records preserve group strings
and the aggregate eligibility flag, not each separator's exact class. This
note checked only the metadata for these twelve already-selected loci, not
word content on other targets.

The 88 meanings, both full readings, references, efficacy-attribution limits
and rivals remain hypothetical. Fixed-tag compatibility does not execute
their semantic reductions or prove the historical source association.
