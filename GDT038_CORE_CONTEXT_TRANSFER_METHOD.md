# GDT038 — local-context transfer for DAIIN, DAM, OKAM, and ODAIN

## Question

Do the four GDT037 residual cores preserve the same anonymous constructional role in Herbal Currier B and Currier-B Stars/Recipe S when their full local field contexts are compared?

No meanings are assigned. The source is the f84-free, all-reading-agreeing GDT016 physical/manual group inventory.

## Context reconstruction

Each physical line is split after every `DY_RESOLUTION` group. For every target occurrence the export records:

- wrapper plus exact residual core and anonymous target state;
- immediate previous and following token, core, and state;
- line and field index;
- position inside the current field;
- exact and compact previous/current/following field templates;
- a target-masked current-field template;
- immediate-state, field-role, and neighbouring-field context clusters.

Nothing crosses a physical line. Final material without a DY resolution is explicitly `OPEN`.

GDT016 contains only strict, all-reading-consensus prose groups. It may omit
alternative-bearing groups while preserving their original `group_index` and
`group_count`. Accordingly, the occurrence export records retained-group
count, exact completeness of the retained physical line, and whether the
target is the source-native physical final group. Field templates on an
incomplete retained line are explicitly inventory-relative and are not a
claim that no omitted group intervenes.

## Comparison

Eleven declared categorical context views are compared separately for each core: target state, wrapper, field position, field role, previous and next state, previous and next field shape, immediate micro-context, masked field template, and neighbouring-field context.

Distribution preservation uses probability weighted-Jaccard overlap and Jensen-Shannon divergence. Section labels are permuted exactly at the physical-folio level while retaining the observed number of Herbal-B target-positive folios. All occurrences on a folio move together. Local and within-core maxT values are reported across the eleven views.

Every target-positive folio is deleted in turn; the worst remaining overlap/divergence is retained. Hand-3-only overlap is a sensitivity because only two Herbal-B hand-3 folios exist.

## Role decision

An abstract role is preserved when target-state overlap is at least 0.8, worst leave-one-folio-out state overlap at least 0.75, and the median overlap across field position, field role, previous state, and next state is at least 0.4. At least four folios per section are required to omit the `LOW_CAPACITY` qualifier. Target-state overlap of 0.3–0.8 is `CONDITIONALLY_COMPATIBLE_SECTION_SHIFT`; lower overlap is not preserved.

These thresholds classify only anonymous formal behavior. They do not name a grammatical, technical, medical, or semantic function. f84r remains sealed.
