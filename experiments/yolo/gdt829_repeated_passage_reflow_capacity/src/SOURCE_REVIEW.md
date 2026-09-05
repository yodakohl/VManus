# Independent source-contract review

2026-09-05. Read-only review of source documentation and producer/guard code,
followed by review of GDT829 `SPEC.json` and `PREREGISTRATION.md`. No manuscript
payload was queried, candidate passage extracted, or result inspected for this
review. The review supports the input contract, not candidate capacity.

## Source representation

`experiments/semantic_assumptions/SOURCE_SEPARATOR_TRANSCRIPTION_SPEC.md` and
`build_source_separator_transcription.py` define the atlas used here. The
GDT829 projection contains the necessary group identities, source order,
raw text, separator states, paragraph flags, and recorded hand metadata.
Legacy `clean_ascii_*` fields are correctly absent from the matching input:
they reproduce a cleaner that can split or erase source groups.

The atlas splits outside bracket/brace/angle constructs only at `.`
(`DEFINITE_SPACE`), `,` (`UNCERTAIN_SMALL_SPACE`), `<->`
(`DRAWING_INTERRUPTION`), and `<~>` (`DRAWING_INTERRUPTION_UNALIGNED`).
First/last group positions supply `LINE_START`/`LINE_END`. Other source
constructs, including complete extended entities and uncertain readings,
remain verbatim. The row controls `<%>` and `<$>` are removed from group text
and retained as paragraph flags copied onto every group of that source row.

The registered opaque-construct lexer preserves this representation without
guessing glyph expansions or selecting an alternative reading. Its atoms are
comparison units, not established manuscript glyphs. Complete source-group
indices, count consistency, separator adjacency, and raw-span reconstruction
are appropriate implementation checks.

## Layout and missing-data constraints

`source_row_index` increases globally within each edition, including non-P
records. Filtering to P and simply joining successive retained records would
therefore silently skip labels. The registration instead treats non-P records,
nonconsecutive loci/rows, and drawing interruptions as barriers. This is
conservative: GDT819 documents genuine paragraphs with interleaved labels, so
the restriction can reduce capacity without proving the remaining text lacks
longer continuations.

Earlier SME001 source audits document absent RF paragraph markers, omitted IT
markers, and an IT physical-line omission at `f106r.29`. The registered explicit
ZL paragraph scaffold, exact alternate locus coverage, consecutive native
rows, and recorded marker disagreements address this obstacle. Borrowed ZL
layout remains one transcription-derived scaffold, not three replications.

Mapping definite gaps and admissible line joins to one comparison GAP is an
explicit matching convention needed for changed wrapping. The registration
correctly retains original boundaries separately, keeps uncertain gaps
distinct, and makes drawing interruptions barriers. It does not establish
authorial word boundaries. Page and panel selectors must remain exact.

Recorded `hand` values originate from source metadata. Matching equal known
labels does not independently verify modern palaeographic hand assignments.

## Guard and consistency verdict

`tools/guarded_tsv_query.py` delegates to `GuardedTSV` in
`tools/vmanus_experiment.py`: the raw selector is checked against forbidden
prefixes and explicit allow-values before the remainder is parsed. GDT829's
179-selector projection and explicit f84/f84r exclusions fit that contract.
The query command, guard statistics, input hash and projection hash should be
retained as reproducible provenance.

No blocking source-contract mismatch was found between the reviewed schema
and the GDT829 specification/preregistration. Flank length is understood as
twelve non-gap transcription atoms on each side; gaps are additionally
retained in the signature, as the preregistration states explicitly. This
review does not validate extraction code, statistical independence, terminal
outcomes, semantics, or the existence of qualifying repeated contexts.
