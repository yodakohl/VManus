# Artifacts

`TARGETS.tsv`: five source loci with raw ZL and three legacy clean readings.
`BLOCKS.tsv`, `PARAGRAPHS.tsv`, `INTERLEAVED_LABELS.tsv`, `NEIGHBORS.tsv`:
four whole P streams,74 P and nine separately retained L records.
`FULL_READER.md`: all selected context records and differing alternate readings;
its legacy ASCII spaces are explicitly not diplomatic boundaries.

`SOURCE_GROUPS.tsv`:129 original atlas groups at the five targets.
`GROUP_COMPARISON.tsv`:15 edition/locus comparisons; all15 atlas flattenings
match current clean text. `ISSUE_GROUPS.tsv`:16 groups with entities,
non-unit fragment counts or uncertain adjacent spacing, not16 independent defects.
These tables, rather than the clean reader, govern target boundary claims.

`RESULT.json`: scope, guarded projection provenance and explicit claim limits.
`VALIDATION.json`: independent source/metadata reconstruction and six rejected
mutations. Public image identities/regions/hashes and manual decisions are in
`src/`. The validator does not redownload images or validate ink/meanings.
