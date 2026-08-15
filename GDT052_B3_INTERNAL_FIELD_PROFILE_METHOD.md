# GDT052 — B3 close versus internal DY field profile

This is the first test of frozen HPR-2 prediction `HPR2_P02`. The question is
whether lines ending in the source-native B3 close class contain a distinct
number of internal DY checkpoints after nuisance control.

Use the 1,164 complete lines with stable all-reading first and final source
members from GDT046. Reconstruct internal DY count from GDT016, excluding the
final group. Fix B3-close counts inside exact physical-folio × register × line-
length-bucket × editorial-paragraph-start strata. Test four predeclared
statistics: internal DY count, any DY, at least two DY, and at least three DY.
The null distribution is exact: dynamic programming enumerates the sum of
every equally likely B3 assignment within each stratum, then convolves strata.
Four-test Bonferroni values are reported.

The test concerns record hierarchy only. It neither assigns B3 or DY a word
meaning nor changes the independent B3 endpoint result. f84r is absent before
line assembly.
