# GDT336 — placement-conditioned exact tuple retrieval

GDT336 inverts the frozen GDT335 channel.  Within each register and outer held
physical folio, predict the exact opaque joint tuple among the tuples licensed
by its known compiler coordinate.

`COORDINATE` is a Dirichlet-1/2 tuple-frequency code.  `PLACEMENT` adds a table
conditioned on physical line entry, within-field position, and physical line
quartile, then shrinks it to the coordinate distribution.  Field ordinal is
excluded because GDT335 found a negative held contribution.  Concentration is
selected from `{32,64,128,256,512,1024}` only by inner leave-one-training-folio
out scoring.  Test events are scored only when their exact tuple is present on
another training folio in the same register.

Report held codelength and exact top-1 retrieval.  No glyph similarity,
semantics, external annotation, or f84 data are used.
