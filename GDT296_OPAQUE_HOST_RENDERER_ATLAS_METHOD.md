# GDT296 — opaque host renderer atlas

## Purpose

Turn GDT293--295 into a practical normalization inventory.  For recurrent
opaque PAGE_HOST identities, measure whether the same-group renderer tuple is
globally canonical, predictably conditioned by the four coarse field
positions, or genuinely variable across held physical folios.

This is a descriptive formal atlas, not a semantic search.

## Frozen population and metrics

Use only the f84-free Voynich native panel.  Include every exact host with at
least 20 events on at least five physical folios; no host spelling or substring
is selected.  The score-blind census contains 59 hosts and 5,715 events.

For each host, hold out one complete physical folio.  Predict the exact
`wrapper|frame|inner-D|right|DY|B3` tuple from:

1. the host's renderer counts on other folios (`HOST_CANONICAL`);
2. host×within-field-position counts on other folios, shrunk with prior 11 to
   model 1 (`HOST_X_POSITION`).

Report exact top-1/top-3, codelength, empirical renderer entropy, dominant
tuple/share, position gain, sections, hands, folios, and per-position dominant
tuples.  Use Dirichlet-1/2 smoothing over the fixed global tuple inventory.

## Frozen descriptive labels

- `CANONICAL_RENDERER_CANDIDATE`: canonical held top-1 >= .70 and empirical
  entropy <= 1 bit;
- `POSITION_CONDITIONED_CANDIDATE`: not canonical, but position held top-1 >=
  .70 and improves top-1 by >= .10;
- `VARIABLE_RENDERER`: all other powered hosts.

These labels rank normalization candidates.  They are not inferential tests
and receive no p-values.

## Claim ceiling and seal

An atlas row can establish only held-folio predictability of a parser-defined
renderer for an opaque host ID.  It cannot establish lexicality, a word,
meaning, code value, sound, language, plaintext, or translation.  No host
substring is mined and no f84 row may be opened, parsed, retained, joined, or
scored.
