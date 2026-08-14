# GDT012 residual-core semantic atlas

Status: **YOLO exploratory hypothesis generation**

## Question

After removing one already recovered entry/carrier prefix (`t`, `s`, `d`,
`q`, `ch`, `sh`, or `che`) and one terminal `dy` closure, does the residual
host predict any independently human-annotated visual object or relation class
across pages?

This is a deliberately permissive meaning search.  Weak and post-selected
associations are retained and ranked.  It is not a confirmation experiment.

## Frozen inputs and unit

The source spine is the exact-family consensus and lossless three-reading
alignment.  A row is one physical/manual source group whose ZL3b, IT2a, and
RF1b nearest-basic display forms agree and whose consensus family has no
alternative site.  It must be linked to an existing exact human annotation
and have `DIAGNOSTIC_NONPROSE` grammar scope.  `f84r` is excluded before any
formal row is retained.

The nearest-basic display is used only to apply the already recovered GDT011
edge operations.  Source-native family surfaces remain in every row.  The
three readings are alternate observations, never three samples.

Primary tests use `UNHEDGED` human annotations.  All-certainty results are a
sensitivity analysis.  Multi-group loci remain visible and are explicitly
flagged; the primary result is also reported for single-group loci only.

## Layer stripping

Exactly one longest matching left layer is removed in this order:

```text
che, ch, sh, t, s, d, q
```

Then one terminal `dy` is removed when material remains.  `o/ot` are not
removed because GDT011 left them local or unresolved.  This is a renderer
projection, not a linguistic segmentation.

## Features and outcomes

The state-blind feature library contains:

- exact residual host and exact unstripped token types with support at least
  three and occurrence on at least two pages;
- exact source-native family expressions with the same support rule;
- presence/prefix/suffix of the predeclared strings `ar`, `ol`, `dal`, `dar`,
  `sy`, `te`, `tee`, `ai`, `aii` in the residual host;
- recovered prefix and `dy`-closure controls;
- residual-host and family length bins.

Each feature is tested against independently supplied object classes
`PLANT`, `FIGURE`, `WATER_OR_APPARATUS`, `STAR_OR_SKY`, and
`ROSETTE_OR_MAP`, and relation classes `REL_EXPLICIT_ATTACHMENT`,
`REL_ENCLOSURE`, `REL_OVERLAP_OR_CONTACT`, `REL_PROXIMITY`, and
`REL_ARRAY_OR_GROUP`.

## Page-conditioned test

For each feature/outcome pair, the statistic is a weighted within-page risk
difference.  Pages contribute only if both the feature and outcome vary.
The exact conditional null fixes, on every page, the number of feature rows
and outcome rows.  Its distribution is the convolution of the corresponding
hypergeometric distributions.  The two-sided inclusive p-value compares the
integer co-occurrence total with its conditional expectation.  Bonferroni
adjustment covers the complete state-blind feature-by-outcome library.

Leave-one-informative-page-out effects, single-group-only effects, all-
certainty effects, and token-versus-stripped-host reuse are diagnostics.  A
candidate with one informative page is explicitly page-confounded.  No p-value
is interpreted as confirmation on this post-selected YOLO branch.

The same exact conditional statistic is repeated with physical folio rather
than page as the stratum, with leave-one-folio diagnostics.  This is essential
because recto/verso or multiple diagrams on one physical leaf are not
independent cultural replications.  Page-level ranking is retained for YOLO
discovery, while the folio statistic quantifies how much of a lead is diagram-
family ecology.

Labels:

- `INTERESTING_EXPLORATORY`: at least three informative pages, local p < .05,
  stable leave-one-page direction;
- `WEAK`: at least two informative pages and either local p < .10 or a large
  absolute within-page effect;
- `LIKELY_PAGE_CONFOUND`: fewer than two informative pages;
- `UNSTABLE`: leave-one-page direction changes or certainty/single-group
  sensitivity reverses it;
- `NO_SIGNAL`: everything else.

## Claim ceiling

This atlas can nominate a residual formal host as a provisional visual
referent or relation carrier.  It cannot establish a word, morpheme, part of
speech, language, plaintext, or translation.  Any concrete meaning remains a
post-selected hypothesis until separately frozen and transferred.  f84r stays
sealed.
