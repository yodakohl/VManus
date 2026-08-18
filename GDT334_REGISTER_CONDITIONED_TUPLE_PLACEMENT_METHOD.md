# GDT334 — register-conditioned joint-tuple placement

GDT334 tests the intermediate architecture suggested by GDT332--333: exact
joint tuples may have stable placement within a register even though their use
does not transfer uniformly between registers.

Within each of the five registers, hold out one complete physical folio.  Score
only held events whose exact joint tuple occurs on another training folio in
that register.  The four targets are physical line entry, within-field
position, field ordinal 1/2/3/4+, and physical line quartile.

`COORDINATE` uses a Dirichlet-1/2 distribution conditioned on compiler
coordinate.  `TUPLE_SHRUNK` estimates each exact tuple's distribution and
shrinks it toward the coordinate probability.  Its concentration is selected
from `{2,4,8,16,32,64}` by an inner leave-one-training-folio-out loop, separately
for every outer fold.  The held folio never chooses its concentration or
counts.  Wrapper, PAGE_HOST glyph shape, DY/B3 target values, semantics, and
external annotations are absent.

This is an exposed architectural test.  Report total and per-register held
gain and folio signs, without a post-hoc permutation p-value.  No f84 row is
used.
