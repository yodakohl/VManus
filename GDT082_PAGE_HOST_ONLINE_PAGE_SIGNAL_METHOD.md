# GDT082 — PAGE_HOST online page-local identity signal

Status: **YOLO source-only content-layer localization**

Within the postselected HPR5 formal class `{ok, yk, yt}`, predict exact
PAGE_HOST identity on a completely held physical folio.  The baseline is a
register-conditioned host distribution followed by a held-folio
register×WRAPPER model (Dirichlet shrinkage 4).  The alternative starts from
that wrapper probability and adapts online to prior physical lines on the
same page.  All occurrences on a physical line are scored before that line is
allowed to update the page counts.  Page state resets on each page.

Scan page shrinkage `{1,2,4,8,16,32,64}`, pay its selector, and report every
register and page contribution.  The exploratory null shuffles exact host
identity within register×WRAPPER, preserving counts and the main compiler
association, then maximizes over the same page-shrinkage grid.  Use 5,000
deterministic draws.  This null does not rerun selection of the frozen HPR5
class or wrapper shrinkage and is therefore a search-qualified diagnostic.

The result tests whether host identity contains page-local information after a
major compiler coordinate is controlled.  It cannot identify what the page is
about.  Concentration on one page or register must be reported, not averaged
away.  f84r is absent from the source inventory and remains sealed.
