# GDT064 — cross-wrapper PAGE_HOST page-context preservation

Status: **YOLO exploratory internal proxy test**

Test whether the same PAGE_HOST under different wrappers preserves a reusable
page-context association.  This is an internal structural proxy for HPR2's
content-preservation claim, not semantic validation.

Aggregate the f84r-free GDT062 inventory into one unit per page × PAGE_HOST ×
wrapper.  Its context is the multiset of every other PAGE_HOST on that page,
with all copies of the target host removed.  Compare weighted-Jaccard context
similarity for cross-folio pairs in the same register:

- exact same host, different wrapper;
- exact same host, same wrapper;
- different-host controls matched on register, host-length bucket,
  page-size bucket, and wrapper contrast.

Pairs without an eligible matched control are excluded rather than assigned a
zero score.  This corrects 140 unsupported pairs found in a later GDT065 audit.

Summaries are balanced over host×register cells rather than dominated by common
forms.  Within each cell and pair type, retain the 200 SHA256-smallest pair IDs;
this deterministic, outcome-blind cap prevents common hosts from dominating
runtime or storage.  Report exact binomial sign tests over cell-level
same-host-minus-control directions and explicit results for GDT063's
postselected `d` and `ok` leads.
No page context includes the compared host itself.

Positive cross-wrapper retrieval would support wrapper-invariant internal
context, not meaning.  External-content preservation remains governed by
GDT059's negative/mixed result.  f84r remains sealed; no role, gloss, word,
morpheme, POS, sound, language, plaintext, meaning, or translation is assigned.
