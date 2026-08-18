# GDT301 — whole-form physical-role domain transfer

## Question

GDT299 found held-folio physical-position information in exact opaque complete
forms beyond opaque hosts; GDT300 showed that the frozen cross-host renderer
grammar does not explain it.  GDT301 asks whether the host-specific alternant
mapping itself transfers across register, section, Currier stratum, and hand,
or is local to those domains.

No source spelling or host substring is inspected.  Complete forms remain
SHA-256 identities and the outcome remains mechanical physical group position
`FIRST/MIDDLE/LAST`.

## Frozen folds and models

For each axis `physical_folio`, `register`, `section`, `currier`, and `hand`,
hold out one complete axis value.  Retain only multi-group-line events whose
exact host and exact complete-form identity both occur in training outside the
held value.  Fit, only on training events:

1. a global Dirichlet-1/2 position distribution;
2. `LAYOUT`, using exact group count and every metadata axis except the held
   axis;
3. `PAGE_HOST`, backed off to `LAYOUT` with prior mass 11;
4. `WHOLE_FORM`, backed off to `PAGE_HOST` with prior mass 11.

The score is held codelength gain `PAGE_HOST - WHOLE_FORM` per eligible event.
Report coverage, top-1, gain, positive held levels, and each held-level score.
The folio axis must reproduce GDT299.  Prior masses 5 and 22 are fixed Voynich
sensitivities.

## Null and interpretation

In 64 deterministic worlds, permute complete-form identities within exact
physical folio × register × section × Currier × hand × group count × host
strata.  This preserves the form inventory and frequency in every tested
domain and destroys only within-opportunity form-to-position alignment.  Use
inclusive local tails and a max-five standardized statistic across the five
Voynich axes.  Synthetic controls enter register transfer where their frozen
metadata provide at least two register values; absent axes are marked
unscored, not zero.

Call `WHOLE_FORM_ROLE_CROSS_DOMAIN_SUPPORTED` only if section, Currier, and
hand gains are positive, at least four of five axes are positive, both prior
sensitivities are positive on those three axes, and max-five `p <= .05` for
each.  If folio transfer reproduces but at least two of register/section/
Currier/hand are nonpositive, call `WHOLE_FORM_ROLE_REGISTER_LOCAL`.
Otherwise call `WHOLE_FORM_ROLE_DOMAIN_MIXED`.

## Claim ceiling

At most this identifies cross-domain stability or locality of host-specific
opaque complete-form physical placement.  It establishes no lexicality, word,
morpheme, linguistic function, semantic role, sound, language, meaning,
plaintext, or translation.  No f84 row may be opened, parsed, retained,
joined, or scored.
