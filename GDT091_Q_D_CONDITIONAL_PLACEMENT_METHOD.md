# GDT091 — q/d placement conditional on O/Y PAGE_HOST base

Reuse the state-blind GDT087 matched-tail panel.  Compare `q` versus `NONE`
only on O-base hosts and `d` versus `NONE` only on Y-base hosts.  Outcomes are
position quartile, DY closure, and absence of an explicit RIGHT_FAMILY.

Shuffle wrapper labels 10,000 times inside exact
`physical folio × matched tail × register` cells.  This preserves page,
register, host spelling after its first sign, and wrapper totals.  The primary
directional statistic is `d late shift - q early shift`; secondary outcomes
remain descriptive.  This refines the formal record compiler and assigns no
meaning.  f84r is absent upstream and asserted absent.
