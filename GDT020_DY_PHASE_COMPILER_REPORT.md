# GDT020 DY-phase compiler

Status: **DY WITHIN LINE PHASE PROVISIONAL**

The frozen inventory contains 2667 DY checkpoints.  1256 of
2471 lines contain at least one; 2344 checkpoints have a following
group.  Splitting mechanically after DY yields 4815 formal phases and
190 recurrent collapsed segment templates with support >=3.
The dominant post-DY closed segment is a single `DY_RESOLUTION` group:
737 occurrences across 51
folios.  Other recurrent closed fields are `Q_OUTER_STATE > DY_RESOLUTION`
(81), `CARRIER_STATE > DY_RESOLUTION`
(64), and `OL_STATE > DY_RESOLUTION`
(56).  This favors chains of compact closed fields over
an analogy to long prose clauses separated by DY.

With four position bins, knowing whether any DY has already occurred saves
556.648 held-folio bits on
77/94 folios.  The selector-paid gain
is 554.326; the conservative BIC-net
gain is 166.650.  Raw phase gains remain
positive at 8, 10, and 16 bins, although their expanded parameter penalties
erase the net gain.  After removing immediately post-DY groups, the raw gain
is 179.985 bits but the BIC-net value is
-203.433.

The best current compiler is therefore:

```text
LINE         := CLOSED_FIELD* OPEN_TAIL?
CLOSED_FIELD := PAYLOAD_WITH_DY
PHASE        := INITIAL_FIELD | POST_DY_FIELD
```

GDT018 showed that the post-DY distribution is not line-initial, so
`POST_DY_PHASE` is an embedded continuation rather than a fresh record.
GDT019 showed that the tested checkpoint payload does not choose the following
state.  Together these support a two-layer technical-register architecture:
payload-bearing fields plus a partially independent control/phase channel.

The persistence evidence beyond the immediate next group is weaker after
complexity payment, and DY occurrence still correlates with continuous line
position.  The compiler is post-selected and lossy.  f84r was absent from the
sole input and was not opened, retained, joined, or scored.  No morpheme,
sentence syntax, word, sound, language, plaintext, meaning, or translation is
confirmed.
