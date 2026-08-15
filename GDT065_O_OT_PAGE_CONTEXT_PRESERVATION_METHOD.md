# GDT065 — O/OT PAGE_HOST page-context preservation

Status: **YOLO exploratory internal proxy test**

GDT054/GDT055 established a transferable O-early versus OT-later positional
contrast on unseen hosts.  GDT059 had zero exact cross-folio annotated capacity
to test whether O and OT preserve a host's external content association.
GDT065 uses internal page context instead.

From the f84r-free GDT062 inventory, aggregate one unit per page × PAGE_HOST ×
O/OT frame × wrapper.  Remove every copy of the target host from the page's
PAGE_HOST multiset.  For every exact same-host O-versus-OT pair on different
physical folios and in the same register and wrapper, compare its page-context
weighted Jaccard with different-host OT controls matched on register, wrapper,
host-length bucket, and page-size bucket.  A pair with no eligible matched
control is excluded rather than assigned an artificial zero-control score.

Balance the summary over PAGE_HOST×wrapper×register cells and report an exact
cell sign diagnostic.  The externally established early/late positional result
is inherited by hash; it is not rerun or treated as semantic evidence.

Positive context preservation supports O/OT as positional rendering around a
stable internal host key.  It does not show preserved external meaning.  No
role, gloss, word, morpheme, POS, sound, language, plaintext, meaning, or
translation is assigned.  f84r remains sealed.
