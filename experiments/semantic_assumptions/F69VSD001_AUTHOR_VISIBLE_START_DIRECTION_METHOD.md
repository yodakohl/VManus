# F69VSD001 author-visible start/direction audit

Status: **FROZEN_BEFORE_REOPENING_THE_IMAGE**

## Question

Does the official Yale image of the 28-slot f69v radial register contain an
author-visible device that fixes a unique start slot, a traversal direction,
or both?

This is a one-canvas source-acquisition audit, not another test of the 28
Voynich strings.  The strings, roots, families, long/short feature results,
and proposed external rosters are forbidden.  Grove's editorial numbering and
the existing `X1.1` coordinate do not count as manuscript evidence.

## Frozen source and scope

- Official Yale canvas: catalogue child `1006199`, containing f69v together
  with f70r1 and f70r2.
- Public catalogue URL:
  `https://collections.library.yale.edu/catalog/2002046?child_oid=1006199`.
- Frozen 2000-pixel image SHA-256 from the already validated complete
  special-circle visual screen:
  `99d824d8d5491a2f4511a0c0f719f9f165063335f53540c63d12b3bbe6c73edf`.
- Inspect only the f69v 28-slot ring.  The other panels on the canvas are not
  comparators and cannot supply a preferred orientation.

## Qualifying devices

Record one of `START_AND_DIRECTION`, `START_ONLY`, `DIRECTION_ONLY`, `NONE`,
or `UNCERTAIN`.  A positive requires at least one unambiguous author-visible
ink device tied to the 28-slot register:

1. a unique radial leader/spoke that selects exactly one slot;
2. an arrowhead or continuous directed trail between slots;
3. a deliberate band break/junction with a unique endpoint mark tied to one
   adjacent slot;
4. a unique plain-alphabet or numeral-like start mark physically owned by one
   slot; or
5. a uniquely differentiated slot marker plus an independent direction cue.

The following never qualify: the top of the page, clock position, Grove's
numbering, transcription order, a long-versus-short log, ordinary spacing,
damage, trimming, binding folds, paint variation, one decorative motif, or a
different-looking Voynich word.  If a putative mark cannot be separated from
damage or ordinary drawing variation, record `UNCERTAIN`, not positive.

## Decision and claim ceiling

- `NONE`: close this visual-start route.  The 28 slots retain only an
  editorial cyclic coordinate with no author-visible origin or direction.
- `UNCERTAIN`: stop; do not score or resolve using the text.
- Any positive: retain only the visible physical coordinate and require an
  independent source-bound reconstruction before using it in a new test.

Even a positive establishes no lunar mansion, day, number, direction name,
word, sound, language, cipher, plaintext, meaning, or translation.
