# GDT393 method — residual page connector census

## Question

Does the complete residual page-role frame outside GDT389 contain an
author-visible directed connector between two separately localizable
inscriptions?

## Inputs

The pre-image frame is selected mechanically from
`existing_human_page_role_matrix.tsv`: reject every `f84*` row by its raw page
field before parsing, exclude the 61 pages already reviewed in GDT389, and
retain every remaining page with at least one catalogue `L`, `C`, or `R` locus.
The already exhausted Rosettes road/connector route is excluded. This yields
12 pages. The selection sees page/layout metadata only; it opens no
Voynich surface, family, PAGE_HOST, joint tuple, or formal score.

Before the authoritative freeze was built, an ad hoc capacity command split
two forbidden page-description metadata rows before output filtering. Neither
row was displayed, selected, retained, scored, or used to define this frame;
no image or formal payload was opened. The frozen loader corrects this by
rejecting the raw page selector before parsing the rest of each row.

## Method

Freeze the exact page list and review categories before opening any target
image. Review each official manuscript canvas for connector geometry only.
Classify the whole page as:

1. `NO_CONNECTOR_CANDIDATE`;
2. `AMBIGUOUS_CONNECTOR`;
3. `CONNECTOR_WITH_FEWER_THAN_TWO_EXACT_LABEL_LOCUS_ENDPOINTS`; or
4. `CONNECTOR_WITH_TWO_OR_MORE_EXACT_LABEL_LOCUS_ENDPOINTS`.

Only the fourth class can nominate an edge, and only when the visible device
itself fixes direction between two distinct exact locus endpoints. Roads,
tubes, spokes, radial order, drawing adjacency, and prose flow are not enough.
Review is complete-page, not positive-only. Formal identities remain locked
unless the inherited GDT388 capacity floor is met.

## Decision rule and claim ceiling

The inherited minimum is 50 singular directed edges on five physical folios,
with a mobile matched target null and whole-folio holdout. Below that capacity,
publish the visual census and stop without a formal join or score.

GDT393 can establish only whether the previously unreviewed page-role remainder
adds eligible visible relation edges. It establishes no parent, reference,
operator, syntax, POS, meaning, language, plaintext, or translation. All `f84*`
material is forbidden.
