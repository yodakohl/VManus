# GDT566 method

## Question

Can the current sidequest be rendered as one complete working German edition of
all 5,122 running events and all 793 statements on the 30 already admitted
pages, while using the compact GDT565 state-card renderer and preserving every
nonstate contextual clause unchanged?

## Inputs

- GDT515 supplies the fixed 5,122-event navigation order and 30-page ledger.
- GDT416 supplies 4,576 event clauses and 715 statements for the older 26-page
  cohort.
- GDT539 supplies 546 event clauses and 78 statements for the current four-page
  cohort.
- GDT565 supplies the generated working phrase, template identifiers and atom
  alignment for exactly 1,656 state cards.

No new page, transcription, surface, event, statement, recipe atom or root
meaning is admitted.

## Method

1. Traverse GDT515's running-event spine in exact ordinal order. Older events
   join GDT416 by global event ID. Current events join GDT539 by GDT515's
   `source_event_id`; both the navigation ID and authoritative event ID remain
   visible.
2. Treat GDT416/GDT539 as the authoritative owner-bound control channel. The ten
   places where later context work changed GDT515's navigation recipe are kept
   in an explicit repair deck rather than silently overwritten.
3. If an authoritative event ID occurs in GDT565, select its generated
   owner-free microphrase. Otherwise select the inherited owner-bound clause
   byte-for-byte.
4. Reassemble each statement twice: once from the selected hybrid working
   clauses and once from the complete owner-bound control clauses. Demand that
   the latter reproduce all 715 GDT416 and all 78 GDT539 source statements
   byte-for-byte.
5. Retain all 30 admitted physical pages, including the two pages with zero
   running events. Produce event-, statement-, page-, mode-, layer- and
   recipe-repair tables plus a readable page-by-page edition.

## Decision rule and claim ceiling

Pass only if all 5,122 events and 793 statements occur exactly once in source
order; all 1,656 state events reproduce GDT565; all 3,466 nonstate events
reproduce their source clauses; all owner-bound statements are byte-exact; the
ten named recipe repairs remain explicit; all 30 page counts agree with GDT515;
and deterministic replay changes no artifact.

This is a complete edition of the current *working interpretation*. It does not
upgrade any German root value to a confirmed historical lexeme or plaintext.
