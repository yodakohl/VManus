# GDT407 method

## Question

Can the selected old 22-page basis and GDT404's four random pages be assembled
into one deterministic edition without changing a recipe, statement boundary,
owner, or scope attachment?

## Inputs

- GDT399: 3,888 running events and 627 rebuilt statements;
- GDT402: 4,374 factorized old attachments;
- Pass 1009: all 693 local labels/section markers;
- GDT404: 688 events, 88 statements, and 677 factorized attachments;
- GDT405: the fixed 46-atom value sheet.

## Method

Normalize source IDs to global GDT407 IDs, preserve every source ID beside it,
sort the 26 physical pages by folio order, and publish separate running-event,
local-group, statement, attachment, page-summary, and unified-group tables.
Local labels never enter prose scope. A human-readable statement edition is
derived from the same rows.

## Decision rule and claim ceiling

The build passes only if it contains exactly 26 pages, 5,269 visible groups,
4,576 running events, 693 local groups, 715 statements, and 5,051 attachments;
all event/action/statement links must resolve, no owner or statement boundary
may be crossed, and a second build must be byte-identical. This is an edition
and accounting result, not new semantic evidence.
