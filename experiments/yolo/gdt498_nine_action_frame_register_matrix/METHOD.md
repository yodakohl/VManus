# GDT498 method

## Question

How much of the full 9-action×11-frame×5-register space is already observed,
how much can be rendered solely from old owner-local values, and where do
compositions have complete-frame support rather than only component support?

## Inputs

- all 4,576 exact GDT416 imperative clauses and the GDT416 renderer;
- the 95 all-register core expansions from GDT415;
- the 55 frame-specific old value cells and eleven fixed frames from GDT493;
- the complete 110-cell current T/R deck from GDT497.

## Method

1. Form every Cartesian cell from nine ordered action roots, eleven fixed
   `@ACTION` frames and five ordered registers.
2. Replace `@ACTION` with the action root and look up the exact recipe/register
   cell in GDT416. Exact cells retain all observed clauses and receive a
   deterministic modal observed default; T/R cells inherit the GDT497 current
   default exactly.
3. For an unobserved cell, require an old owner-local value for every component
   from the union of GDT415 and GDT493. Render it with the unchanged GDT416
   sentence compiler. Active-argument frames use a context-safe referent; OL
   compositions use `Fahre fort:` syntax.
4. Class each composition by complete-cell support: two or more other observed
   heads in the same frame/register, one such head, the same action/frame in
   another register, or old values only.
5. Publish the 495 cells, exact and composed subsets, nine-action,
   eleven-frame, five-register, 99 action-frame and 55 frame-register coverage
   tables.

## Decision rule and claim ceiling

A cell is `READABLE` only when every component has an old register value and
the fixed renderer returns a phrase. `OBSERVED_CLAUSE` requires an exact
GDT416 recipe×register carrier; all other readable cells remain
`COMPOSED_WORKING`. The support class ranks working usefulness and never
promotes a composition to observation. The matrix predicts neither a surface
nor an occurrence and changes no working root meaning.
