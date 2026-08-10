# LRG005 one-shot D1-specific cross-register target

Status: `REGISTERED_UNSCORED`

The target uses the exact 536-row, 68-cell LRG005 panel and the frozen two
held-folio scores:

- `D1_BARE`: exact D1-prepended sequence versus its bare sequence;
- `D1_OTHER`: exact D1-prepended sequence versus all other one-member
  extensions of the same sequence.

The panel is already conditioned on page, symbol count, and the exact first-A
member triplet in all three readings.  The target reconstructs the 144 manual
label and 392 prose roles once, preserves every cell quota, and evaluates the
unchanged v3 statistic, 8,192-assignment null, folio/section/parity balance,
deletion, and concentration gates.  Both channels must pass.

The label-side capacity disclosure precedes this registration: 61/180 primary
A-initial label rows had an exact D1-prepended prose counterpart somewhere.
No label-versus-prose score contrast, role-linked control score, folio effect,
or target statistic was opened before this method. The complete label-blind
two-channel matrix was constructed and hash-bound in the preceding capacity
audit.

The producer and clean validator may emit only aggregate channel/folio metrics,
hashes, gates, status, and decision.  They may not emit a unit ID, locus, page,
surface, family/member sequence, row score, or row role.

A pass may establish only that manual-label A-initial sequences preferentially
belong to exact sequence families with a D1-specific extended prose state.  It
may authorize structural tags such as `BARE_A_BASE` and `D1_EXTENDED_BASE`.
It cannot establish that D1 is a prefix, classifier, morpheme, grammatical
case, article, verb marker, sound, word, language feature, cipher operation,
English meaning, plaintext, or translation.
