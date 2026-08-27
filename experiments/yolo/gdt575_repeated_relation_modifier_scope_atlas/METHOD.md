# GDT575 method

## Question

Which repeated relation/modifier phrases in the complete current edition are
raw-adjacent repetitions of one atom, which are interrupted repetitions, which
are collisions between distinct atoms, and which differ by outer/inner scope?

## Inputs

The only text source is GDT574's complete 5,122-event German working edition.
No page, event, recipe, atom, root meaning or clause is added or changed. The
scan covers the already admitted thirty pages and explicitly excludes sealed
f84/f84r.

## Method

Thirty-three current surface forms cover fourteen atom families:

- four relation roots (`AL`, `AR`, `L`, `AIR`) with their register voices;
- grades `E`, `EE`, `EEE`, the two stage controls, `O` and `CARRIER_Q`;
- the `AN/HO` class voice, the local-variant family, and seven local-address
  atoms currently sharing one German phrase.

All candidates are matched case-insensitively with Unicode-safe boundaries
`(?<!\w)…(?!\w)`. Scoped variants are generated explicitly. Matches are
selected longest first, so the plain base is not counted inside an outer or
inner phrase and `Grad I` is not counted inside `Grad II` or `Grad III`.

Each selected phrase is aligned by occurrence order to the eligible atoms in
the event's fixed recipe. The alignment must cover every eligible atom once.

An exact duplicate requires the same complete German surface and the same
scope inside one event. Every group is classified on two independent axes:

1. all aligned atoms are the same root, or at least two roots differ;
2. their recipe positions are raw-adjacent, or another atom intervenes.

An outer and an inner rendering of the same base phrase is therefore not an
exact duplicate. Such pairs are inventoried separately and receive only a
scope-preserving coordination candidate.

## Decision rule and claim ceiling

`src/run.py` writes the complete phrase deck, all duplicate groups, their event
atlas, four topology profiles, all outer/inner pairs and a compact result.
`src/validate.py` independently rescans the source using a separately stated
phrase inventory and checks counts, atom positions, source clauses, recipes,
scope values, topology and guards.

The result licenses no rewrite by itself. It changes and confirms no Voynich
root, recipe, spelling, page, plaintext, lexeme, language or object identity.
