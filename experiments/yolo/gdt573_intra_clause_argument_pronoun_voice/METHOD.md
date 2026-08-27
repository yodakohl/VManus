# GDT573 method

## Question

Can every repeated full owner-argument phrase inside one current card receive a
short, unambiguous German anaphoric voice while preserving the exact complete
argument wording in a reversible expansion channel?

## Inputs

- GDT572's complete 5,122-event, 793-statement and 30-page bracket-free edition;
- GDT572's complete twenty-cell register×argument-form table.

The already licensed GDT565 `Y|Y` phrase at `G407-E1058` supplies the sole
observed repeated paired-argument form. No page, transcription, recipe, atom,
root value, scope distinction or event boundary is added.

## Method

1. Match the explicit and carried form of each of the twenty owner-root cells
   with Unicode word boundaries. This deliberately prevents `den
   Positionsposten` from matching inside `die beiden Positionsposten`.
2. Inside each card and separately for each argument root, retain the first
   exact mention and collect the second through fifth mentions. Do not carry an
   anaphor across a card boundary.
3. Render masculine later mentions as `ihn` and feminine or plural later
   mentions as `sie`. Preserve outer, inner and third-level wording around the
   nominal host.
4. If two different masculine roots recur together as one exact coordinate,
   render the later coordinate as `beide`. This rule fires exactly three times
   and prevents the ambiguous surface `ihn und ihn`.
5. Store every replaced source fragment, its source and target spans, root,
   form class and voice card. Expand each anaphor from that channel and require
   exact recovery of the source card before rebuilding all statements and
   pages.

## Decision rule and claim ceiling

Pass only if all 854 repeat groups and all 1,046 later argument mentions are
covered; all twenty single-root cards plus the paired and coordinate cards are
used; the resulting 1,043 surface anaphors contain no `ihn und ihn`; no exact
owner argument remains multiply repeated; all 5,122 event expansions are exact;
all source order and boundaries remain unchanged; and generation is
deterministic. The anaphors are German workshop voice, not Voynich lexemes or
evidence for recovered syntax, plaintext, language, genre or object identity.
