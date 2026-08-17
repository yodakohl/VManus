# GDT254 — corrected f80r field lattice method

GDT244 proved that the old q13 role coordinate merged five physical f80r
paragraphs into two records.  GDT254 rebuilds the page from the frozen HPR2
group inventory on the five corrected paragraph coordinates.

For every covered prose line, a field ends at a source-local DY closure or at
the physical line end.  PAGE_HOST and compiler components use the unchanged
HPR2 parser rules.  Uncovered prose lines remain missing: each contributes a
minimum of one field and a maximum equal to its observed source-group count.

The already published readable-recipe instrument is then evaluated at every
feasible missing-field coordinate.  Only the coarse classes
`INSTRUCTION_CLAUSE_LIKE`, `SHORT_ARGUMENT_LIKE`,
`UNRESOLVED_EDGE_CLASS`, and `RECORD_CLOSER_LIKE` may be retained, and only
when the coarse class is invariant across the feasible range.  These are
formal extent/placement analogies, not meanings.

The input group file contains no f84r rows; all f84-prefixed rows are rejected
before retention.  No f84 row is joined or scored.
