# GDT801 method

## Inputs and exact join

Only five published artifacts are materialized: the 4,137 nonempty paired
GDT800 occurrences, the frozen 155-stem inventory, its structural card, and
the GDT791 occurrence and line spines. `GDT800.page` is a source selector, not
always a physical folio. The
only valid join is therefore:

```text
GDT800.page = GDT791.source_selector
GDT800.locus = GDT791.locus
GDT800.token_index = GDT791.token_ordinal_in_line
GDT800.surface = GDT791.surface
```

The physical-folio field remains a downstream grouping variable. Requiring
`GDT800.page = GDT791.physical_page` would silently lose the f89r1, f95v1 and
f95v2 selectors and is forbidden.

## Boundary definitions

- Physical line edge retains GDT800's frozen `multi_line_final` definition.
- Paragraph closure is the last token of a GDT791 `paragraph_end=1` line.
- Legacy-statement, record and panel closure are the greatest running-event
  ordinal within the corresponding non-`NONE` identifier.
- A strict structural-interior event lies on neither a paragraph-start nor a
  paragraph-end line and is not a legacy-statement, record or panel endpoint.

The primary discriminator re-estimates the exact-stem physical-edge effect on
the strict interior and repeats it under hand, topology and physical-page
conditioning. The effect must retain OR above 3 and exact one-sided `p<.01`
under all four specifications to exclude higher-scope closure as the sole
cause.

Each higher boundary has a capacity gate before any incremental coefficient is
interpreted. It needs both terminal outcomes at endpoints, at least one target
endpoint away from the physical line edge, support on more than one physical
page and at least one informative stem×line-position stratum. The combined
gate, rather than the endpoint-margin gate alone, controls scoreability. A
failed gate means not identifiable, not no effect. The wider frozen-stem
projection is reported separately from the exact 542-event join.

All joined statement, record and panel endpoints already lie on paragraph-end
lines. The 411-row primary population is therefore one composite exclusion,
not four independent robustness samples.

## Deep progress and local-label sensitivities

On f77r/f82r/f83r, line-final targets receive a predeclared normalized line
rank within their record and panel. Terminal labels are permuted exhaustively
within physical page at fixed page-specific margins. This can reject only a
strong monotone “`m` occurs later” rival.

Separately, every local GDT791 label ending in `l/m` whose nonempty preceding
surface belongs to the frozen GDT800 stem set is projected. This is a capacity
and unit-edge sensitivity, not a free meaning transfer. Label status is also
conditioned on physical page after singleton/line-final status; thin page
strata remain a stated limitation.

## Claim ceiling

The pass may refine the selected tag to
`PHYSICAL_LINE_EDGE_FAVOURED_TERMINAL_SURFACE__HIGHER_SCOPE_UNTESTED` and reject
paragraph/statement/record/panel closure as the sole source of the line-edge
association. It cannot establish `m=l`, allography, abbreviation, inflection,
case, a closing morpheme, sound, lexeme, plaintext, clothing/status value or
translation. A higher-scope capacity failure cannot be interpreted as absence.
