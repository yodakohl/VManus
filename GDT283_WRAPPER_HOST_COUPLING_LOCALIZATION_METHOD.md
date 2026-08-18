# GDT283 — wrapper/host coupling localization

## Question

GDT282 shows that opaque wrapper identity predicts PAGE_HOST character form
across held folios, sections and hands.  GDT283 asks whether that channel
survives on exact host types excluded from training and whether it resides only
at the wrapper-adjacent first character or throughout the host.

No PAGE_HOST substring, lexical item, semantic field, or wrapper meaning is
selected.  GDT282 is frozen byte-for-byte.

## Frozen panel and models

Use the f84-free native panels for Voynich and the three Latin controls.  Score
the exact GDT282 no-wrapper base and full eight-class wrapper identity only.
Keep all other opportunity, frame, right, renderer and closure coordinates
fixed.

Partition target character bits exhaustively into:

- `INITIAL`: first PAGE_HOST character;
- `INTERNAL`: characters neither first nor last;
- `FINAL`: last character when host length is at least two;
- `EOS`: end-of-host event.

The four components sum exactly to total held bits.  This is positional
localization, not substring mining.

## Unseen-host test

Assign every exact PAGE_HOST identity to one of eight immutable buckets using
`SHA256("GDT283_HOST_FOLD|" + host) mod 8`.  In each physical-folio fold, an
event is scored from training counts that exclude both:

1. the held physical folio; and
2. every occurrence of every PAGE_HOST identity in the target event's host
   bucket.

All held-folio events are still scored once in native order, sharing only the
ordinary past-within-page target history.  Thus no exact target host identity
can occur in its training counts.  The published parser is used, so this is a
host-identity transfer sensitivity rather than a second LOFO parser-learning
replication.

## Matched null

For 64 deterministic worlds, permute wrapper identities within exact

`section × Currier × hand × within-field position × host length × first host character`

strata.  The base remains attached to each event.  The Voynich panel has 7,075
events in wrapper-mobile strata under this rule.  Apply the same definition to
each Latin control.  Report component and total observed gains, null mean/SD,
inclusive one-sided p, and max-four p across the four panels.  This null keeps
the most direct boundary/length opportunities while destroying the specific
wrapper-to-rest-of-host association.

## Frozen decision

Report `WRAPPER_CHANNEL_SURVIVES_UNSEEN_HOST_TYPES_AND_INTERNAL_POSITIONS` only
if all are true for Voynich:

1. nested held-folio/host-bucket total gain is positive;
2. nested `INTERNAL` gain is positive;
3. at least six of eight held host buckets have positive total gain;
4. the standard observed total exceeds its first-character/length-matched null
   at inclusive `p <= .05` after max-four panel correction.

Otherwise report `WRAPPER_CHANNEL_DOMINATED_BY_BOUNDARY_OR_HOST_LEXICON`.
All failed and negative positional components remain public.

## Claim ceiling and seal

At most this can locate a transferable same-group wrapper/host form coupling.
It cannot establish productive morphology, an abbreviation rule, lexical
identity, sound, language, meaning, plaintext, or translation.  No f84 row may
be opened, parsed, retained, joined, or scored.
