# GDT269 — q13 q-wrapper record stage conditional on PAGE_HOST

## Status and question

This is an explicitly exploratory, post-hoc decomposition of GDT267.  GDT267
found more `q` wrappers in the earlier of two eligible q13 records and more
bare/`NONE` renderings in the later record.  Earlier work already established
that wrappers can preserve PAGE_HOST page context (GDT064) and that `q` shifts
the same host earlier inside a physical line (GDT010).  The remaining narrow
question is:

> Does the q13 earlier-record association remain after conditioning on exact
> PAGE_HOST identity and page, and how sensitive is it to physical field
> position?

This is not a semantic test.  PAGE_HOST is an opaque parser-derived identity,
and `q` is an opaque wrapper label.

## Frozen source and panel

Use the already published, f84-free
`gdt227_q13_abstract_interlinear.tsv`.  Reconstruct exactly the unchanged
GDT267 panel: on each page retain records spanning at least four physical loci,
then retain the nine pages having exactly two such records.  Lexical record ID
order defines `EARLIER` and `LATER`, as in GDT267.

Expand each field into aligned `source_tokens`, `page_hosts`, and
`compiler_cells`.  Retain only wrapper values `q` and `NONE`.  No visual data,
label semantics, language model, or f84 material enters the analysis.

## Conditional tests

The primary exploratory decomposition stratifies occurrences by exact
`page × PAGE_HOST`.  Within each stratum, hold fixed:

- the number of `q` and `NONE` occurrences;
- the number of earlier and later record occurrences; and
- exact PAGE_HOST and page.

Under the occurrence-exchangeable null, the number of `q` occurrences in the
earlier record is hypergeometric.  Convolve all movable strata exactly and
report the upper-tail and absolute-distance two-sided probabilities.  Also
report the Mantel–Haenszel odds ratio and the conditional score
`U = sum(observed q-early - expected q-early)`.

Because occurrences share fields and records, also aggregate conditional
scores by page and enumerate all `2^9` page-level sign flips.  Both p-values
are exploratory ranking diagnostics, not confirmation-level sampling claims.

The capacity audit exposed seven fixed decompositions, all of which are
reported rather than selected:

1. `PAGE_HOST_PAGE`
2. `PAGE_HOST_PAGE_ROLE`
3. `PAGE_HOST_PAGE_RELATIVE_QUARTILE`
4. `PAGE_HOST_PAGE_WITHIN_FIELD_POSITION`
5. `PAGE_HOST_PAGE_FIELD_END`
6. `PAGE_HOST_PAGE_ROLE_WITHIN_FIELD_POSITION`
7. `PAGE_HOST_PAGE_RELATIVE_QUARTILE_WITHIN_FIELD_POSITION`

`ROLE` is the existing nonsemantic GDT227 field-role-like projection;
`RELATIVE_QUARTILE` bins the existing record-relative field coordinate;
`WITHIN_FIELD_POSITION` is `SINGLE/FIRST/MIDDLE/LAST`; and `FIELD_END` is the
existing physical field endpoint class.  These are sensitivity strata, not
new grammatical meanings.

## Interpretation and stop rule

The result may license only one of these conclusions:

- the q13 q-wrapper stage association survives exact host/page conditioning;
- it is position-sensitive and cannot yet be separated from record-template
  composition; or
- it disappears after conditioning.

No result assigns `q` or PAGE_HOST a word, morpheme, sound, semantic function,
topic, plaintext, or translation.  GDT268's weak/nonconfirming Q20 transfer
remains unchanged.  No f84r access is authorized or performed.
