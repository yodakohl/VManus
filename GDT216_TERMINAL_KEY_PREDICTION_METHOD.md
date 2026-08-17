# GDT216 — frozen label-terminal to paragraph-initial key prediction

## Question

Does the existing nonsealed Voynich label panel contain a compact positional
reference field analogous to the independently documented Wellcome MS 49
Wound Man mechanism?

The external positive control is frozen first.  The target score is not yet
present in this checkpoint.

## Frozen panel

Use exactly the 23 pages and eleven physical folios in the published GDT187
page inventory.  That panel already has label and confirmed-prose roles and a
432-world whole-folio null matched on section, Currier, hand, and eligible-page
count.  Do not add a page, remove an unfavorable page, or use visual content.

For those pages only, stream-select source-native family-consensus groups from
the existing consensus table.  Reject every `f84*` row before retaining or
parsing its formal payload.  Alternate readings are one manuscript; family
consensus is one observation, not three replications.

## Frozen keys

For every consensus-covered label locus, select the final physical source
group.  For every consensus-covered confirmed-prose paragraph-start locus,
select the first physical source group.  Preserve drawing-interrupted
multi-group loci and use only within-group family sequences.

Score exactly three source-native mappings:

1. `FINAL_GROUP_EXACT -> INITIAL_GROUP_EXACT`;
2. `FINAL_FAMILY_1 -> INITIAL_FAMILY_1`;
3. `FINAL_FAMILY_2 -> INITIAL_FAMILY_2`.

The first mapping is the closest analogue to a separate numeral token.  The
one- and two-family mappings allow a compact key fused at a group edge.  No
other substring, prefix, suffix, HPR2 field, raw transcription spelling, or
semantic class may be selected after scoring.

For each representation, form a count bag of label-side keys and a count bag
of paragraph-side keys per page.  The score is mean page-level weighted
Jaccard over all 23 pages; a page with no consensus-covered opening contributes
zero rather than being removed.

## Null and decision

Reuse the exact 432 GDT187 whole-folio label-bundle assignments.  Report exact
inclusive local tails and a max-three standardized tail.

Call a compact terminal-key lead only if all conditions hold:

- max-three `p <= .05`;
- the effect is positive in both powered GDT187 sections, Pharma and
  Biological/Balneological;
- the winning representation is `FINAL_GROUP_EXACT` or `FINAL_FAMILY_2`, not
  the single-family coarse channel;
- at least two physical folios contribute an exact label-key/paragraph-key
  overlap.

Otherwise retain the readable positive control and record
`VOYNICH_TERMINAL_KEY_NOT_SUPPORTED`.

## Claim ceiling

Success would license only a source-native compact positional reference-field
lead.  It would not identify a number, letter, paragraph index, label owner,
word, morpheme, sound, language, plaintext, or meaning.  Failure rejects this
specific terminal-to-initial mechanism on the frozen panel, not the GDT215
hybrid architecture.

No f84 artifact may be retained, parsed, joined, or scored.
