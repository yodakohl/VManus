# GDT145 — MHI004 retrieval mechanism

This exposed post-hoc audit asks why the f6r→f51r relation was the only
top-decile O/OT retrieval in GDT144.  It uses only the same published f84r-free
GDT112/GDT137 inputs.

Recompute exact-host set Jaccard, corpus-IDF-weighted Jaccard, a target-set-size
matched rank, and a minimum-host-length-two sensitivity.  The IDF weight is
`log((N+.5)/(document_frequency+.5))` over the 93 eligible Herbal A/hand-1
pages.  No representation or target is selected beyond explaining the already
exposed GDT144 lead.

Use `MHI004_O_OT_LEAD_EXPLAINED_BY_UBIQUITOUS_SINGLETON_HOST` if the shared
host occurs on more than 80% of eligible pages, IDF weighting moves the target
outside the top decile, and length-two filtering leaves no pairwise capacity.
Otherwise use `MHI004_O_OT_LEAD_MECHANISM_UNRESOLVED`.

This is a mechanism audit, not a lexical test.  In particular, no one-character
PAGE_HOST receives a plant-part meaning.
