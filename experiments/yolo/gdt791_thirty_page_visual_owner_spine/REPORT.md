# GDT791 — Thirty-page visual-owner spine

## Result

**PASS.** All 30 released pages now sit in one executable visual/text spine:
1,007 lines, 5,866 tokens, 5,122 running events and 744 local cards replay
exactly. The correct line split is 612 running-prose lines, 392 local
label/marker lines and three zero-token transcription lines on f66r.

All 30 pages have a prior direct visual page review. Annotation depth is not
uniform: f77r, f82r and f83r have ten explicit panels, thirteen prose records
and 28 component-label tokens; the other 27 receive only their defensible page
context. `PANEL_NOT_DEEPLY_ANNOTATED` means missing panel annotation, not that a
page has no panels or images.

## What the full 30-page view changes

The image/register distinction is large and useful before any translation:

| visible topology family | pages | running events | local cards |
|---|---:|---:|---:|
| whole-plant article | 12 | 1,118 | 2 |
| radial array | 6 | 523 | 574 |
| pool/apparatus network | 6 | 1,811 | 40 |
| material register | 3 | 603 | 68 |
| text block | 3 | 1,067 | 60 |

Thus the same transcription stream is being used in sharply different visual
address regimes. A page-level or paragraph-level model can now test that fact
without confusing local labels with prose.

## The boundary conflict

Of 235 GDT581 statements on the three deeply annotated pages, 230 lie wholly in
one GDT790 record. Five cross a record boundary:

- G407-S357: f77r, F77_P1 → F77_P2, also a panel change.
- G407-S527: f82r, F82_P2 → F82_P3, also a panel change.
- G407-S576: f83r, F83_P1 → F83_P2, also a panel change.
- G407-S597: f83r, F83_P2 → F83_P3, also a panel change.
- G407-S631: f83r, F83_P4 → F83_P5 under the same panel.

All five end under the old `LICENSED_DY_CLOSE` rule. The old parser therefore
absorbed the first token or tokens of a new visible record into the preceding
statement. GDT791 selects `PANEL > RECORD > LEGACY_STATEMENT` and emits 240
record-local fragments while retaining the 235 legacy IDs as provenance.

Only the f77r crossing carries concrete inheritance across the boundary. Two
aliases transfer CH action and Y object from `qolchy` at f77r.24/F77_P1 to
`otedy` at f77r.25/F77_P2. A third raw focus governor crosses the same edge, but
its effective host is already the local `CONTROL:G407-E2535:OT>G<DY` envelope.
The two aliases are quarantined, the raw governor is clipped and the local
control host survives. Consequently the inherited rendering “take the same
station item” is removed from `otedy`; no replacement translation is invented.

The remaining 460 concrete aliases stay inside their record. All 283 source-free
owner defaults are reparented to the local record owner rather than allowed to
float at page level.

## Exact label/prose reuse

All ten GDT790 exact label/prose bridges cross panel owners, including the three
same-page edges. They remain a separate `EXACT_STRING_REFERENCE` graph with
zero record-merge and zero meaning-transfer credit. In particular, exact reuse
can nominate `otedy` or `okal` for a host-distribution test, but it cannot join
their source and target panels or supply a gloss.

## Immediate semantic capacity

| complete form | running occurrences | pages | statement-first | use |
|---|---:|---:|---:|---|
| `otedy` | 18 | 9 | 8 | strongest record-head versus continuation conflict test |
| `okal` | 16 | 11 | 4 | strongest broader field/record-position test |
| `otchdy` | 3 | 3 | 1 | low-capacity control |
| `olaiin` | 11 | 8 | 1 | lower-capacity cross-page control |
| `darol` | 0 | 0 | 0 | image-local only |
| `darolsy` | 0 | 0 | 0 | image-local only |

`darol/darolsy` remain plausible local identifiers at their image loci but have
no running-prose occurrence on the 30 pages. They cannot currently bridge into
a portable prose meaning.

## Decision and next route

The lossless 30-page occurrence spine and record-precedence repair are selected.
No token meaning or component is selected.

Next, mask the image occurrences of `otedy` and `okal` and classify their hosts
on the other 27 released pages: record/statement opening, continuation, local
field, closing environment and page topology. `otchdy` and `olaiin` serve as
capacity-limited controls. The question is whether the outside pages predict a
stable discourse or nominal role before any concrete gloss such as water,
vessel, plant or action is attempted.
