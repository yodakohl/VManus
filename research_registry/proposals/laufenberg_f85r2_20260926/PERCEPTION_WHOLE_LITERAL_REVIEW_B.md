# IDEA000588 literal and accounting review B

This is an independent literal/bookkeeping review of the frozen author packet against only the safe GDT1042 `native_groups.tsv`. It does not validate the source interpretation, grammar, or semantic derivations. The three editions are alternate readings of one manuscript, not independent witnesses.

The freeze receipt's SHA-256 and byte counts match the frozen JSON, Markdown draft, report, and 473-row TSV. The safe input hash is the declared `e50307f834b04ff2ce17a97f14fd2c7b3f24b4818bc7fda3f57c372afc6b9d3c`. The 473-row author TSV reproduces the input's first 12 fields byte-for-field and in order for every row; there are no duplicated group IDs. Both the TSV and JSON consequence list contain 473 matching rows: ZL3b 156, IT2a 157, RF1b 160, across 24 loci each. Per-edition previous/next IDs and literal strings follow the global sequence in the safe table.

The nine declared ZL fragments have sizes 11, 15, 9, 10, 14, 22, 26, 36, and 13 groups (156 total). Their IDs are unique and cover every ZL group exactly once. Against the safe table, each fragment's literal list, ID sequence, bounds, and literal leaves in its manual AST agree in order. No literal omission, insertion, or reassignment was found. This establishes the authored spans and serialization, not that their meanings follow from the grammar.

The JSON contains 115 whole-form lexicon entries with 158 declared payload units, 38 listed grammar conventions, eight named scope records, and zero retained cuts or component values. Each entry's `all_occurrences` list exactly matches the rows assigned that exact literal in the TSV; each such row has the corresponding declared whole value and type. There are 78 distinct type labels among the 115 forms. Thus the receipt's “115 types bound” is best read as 115 typed whole-form entries, not 115 different type labels. Total rows with an assigned value are 420; the remaining 53 are explicitly unassigned.

The alternate-reader accounting is internally consistent and keeps gaps distinct from fixed-template conflicts:

- ZL3b: 156/156 assigned whole forms and marked `author_manual_whole_candidate` across the nine fragments.
- IT2a: 136 rows have only `literal_value_only_full_reader_derivation_unprovided`; 21 rows are `unassigned_literal_no_alias` (21 distinct unknown forms). No alternate whole derivation is claimed.
- RF1b: 128 rows have only `literal_value_only_full_reader_derivation_unprovided`; 32 are `unassigned_literal_no_alias` (30 distinct unknown forms). No alternate whole derivation is claimed.

The three reported fixed-template clashes are also literal in the table and remain distinct from those unknowns: IT2a `.1 G007` is assigned `FIRST` where the ZL C01 continuation uses the `GENERATED` position; IT2a/RF1b `.20 G001` `ar` is assigned `GENITIVE` where the fixed C08 continuation uses `or`/`COORDINATE`; and the `.24` tail is separate `ar ar am` in IT/RF rather than ZL `ar aram`. Those entries retain their own values (`GENITIVE`, `BECAUSE`); the packet does not normalize them into a new `aram` meaning. These are conflicts with the stated fixed template, not proofs against every possible alternative parse.

No material literal, row-identity, lexicon-occurrence, type, count, fragment-span, or status-accounting error was found. My review does not establish semantic well-typedness, source equivalence, grammar plausibility, or that the 156 ZL mappings compose into true derivations: the ASTs are manually authored, and neither this audit nor the claimed leaf checks executes them. Root's separate semantic/source review is still required. All 53 alternate-reader gaps and the three fixed-template clashes remain as declared.
