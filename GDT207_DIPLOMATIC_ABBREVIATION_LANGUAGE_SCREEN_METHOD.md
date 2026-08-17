# GDT207 — authentic diplomatic-abbreviation language screen

## Question

GDT157 showed causally that a learned medieval expansion-to-diplomatic channel
generates part, but not most, of the Voynich surface architecture.  GDT189 then
showed that the frozen compiler-stripped PAGE_HOST stream is not competitive
under six ordinary historical-language character models.  Does the real
diplomatic side of a large medieval abbreviation parallel corpus provide a
materially better named-letter target than the corresponding expanded text?

This is the smallest bounded screen before attempting any flexible inverse
abbreviation transducer.  It changes only the target character model.  It does
not alter the HPR2 parser, source representation, source boundaries, search
budget, mapping family, or matched source control.

## Fixed data and representation

- Voynich input and PAGE_HOST extraction are exactly the GDT189 source and
  parser, with all `f84*` rows and the one unknown-sign locus rejected before
  retention.
- The comparator is the Nuremberg Letterbooks line-aligned corpus frozen and
  unblinded by GDT155: 48,337 real diplomatic lines and their 48,337 expanded
  parallels.
- Both views are normalized identically by Unicode NFKD, the frozen long-s and
  dotless-i folds, `ß -> ss`, lowercase `a`--`z`, and one SPACE between runs.
- Physical lines reset an additive-half order-2 character model.

## Model and accounting

The exact GDT189 static injective model maps the 20 active PAGE_HOST source
signs into 26 named letters.  Three deterministic pair-swap descents are run
for each of two packs (`REAL_DIPLOMATIC`, `EXPANDED_PARALLEL`), with exact CPU
rescoring and exhaustive retained-key pair-swap checks.

Each candidate pays the common model/order cost, `log2(2)` pack selection, and
the complete injective key `log2(P(26,20))`.  The matched control is the same
line-reset integrated Dirichlet-1/2 order-2 KT model over the 20 anonymous
source identities plus SPACE.

The result is a directional mechanism screen.  A flexible inverse transducer
is not justified unless the real diplomatic pack both beats its expanded
parallel and beats the matched source control with a stable key.  Relative
improvement alone is retained as an architectural clue, not a plaintext.

The primary search seeds are 20701--20703.  After the primary result, an audit
also ran the older GDT189 seeds 18901--18903 because a scratch estimate had
landed in a different local optimum.  Those rows are explicitly
`POSTHOC_SEARCH_SENSITIVITY`; they cannot change the primary gates.  Their
purpose is to expose how much the estimated diplomatic-versus-expanded saving
depends on heuristic initialization.

The source table contains 228 `f84v` group rows and no `f84r` rows.  The
existing guarded loader examines only locus/page identifiers and rejects every
`f84*` row before retaining or parsing formal fields.  No f84 row is joined or
scored, and no f84 formal payload is displayed.
