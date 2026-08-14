# GDT003 formal paradigm prediction method

GDT003 tests whether predeclared GDT002 string transformations combine as a
predictive formal algebra. It assigns no linguistic or semantic category.

The primary corpus contains one physical record for each manual source group
whose nearest-basic-EVA display, source-group count, and topology agree across
ZL3b, IT2a, and RF1b. The readings are alternate observations, never samples.
Cleaner-created fragments are excluded as boundaries. The f84r formal holdout
is filtered before formal records are retained.

Candidate operations are retained only when their exact input/output contrast
recurs in training. The fixed GDT002 candidates are prepend `q`, initial
`d→s`, initial `o→ot`, append `dy/dal/dar`, and final
`dal→dar`, `dal→dy`, `dar→dy`. Their attachment classes are rederived from the
observed edit locations rather than supplied to the interaction analysis.

A rectangle contains `X`, `A(X)`, `B(X)`, and the common value of
`A(B(X))` and `B(A(X))`. All complete, three-cell, and two-cell structures are
retained. Interactions whose two composition orders differ are recorded rather
than coerced into rectangles.

The primary fourth-cell task hides a target form globally, retains the other
three cells, and requires both transformations plus their combination to be
supported on other hosts. Folio- and section-held tasks rebuild transformation
support and baselines without the held physical fold, generate absent fourth
cells from training triples, and then test whether those exact strings occur in
the held fold. A model-visible target is never credited as novel. These are
computational cross-validations of already-public manuscript readings, not new
external evidence.

Baselines are a character order-4 KT score, visible whole-group frequency,
nearest-edit score, and source/target-length-matched randomized transformation
graphs. The GDT001 context mixer is reported as not directly comparable because
its decoder is conditional on the full serialized lattice/context, not an
isolated missing-group API. Structure-preserving graph randomization preserves
each operation's observed source set, target multiset, and edge count.

All ambiguous-reading groups are excluded from the primary analysis. A
separate edition-union sensitivity records whether headline transformation and
rectangle support changes when alternate surfaces are admitted. Split/join
support is taken only from manual-source evidence already exported by GDT002;
spaces are not interpreted as linguistic words.

The outcome vocabulary is restricted to `PRODUCTIVE COMPOSITION SUPPORTED`,
`LIMITED/LOCAL COMPOSITION ONLY`, `NOT DISTINGUISHABLE FROM STRING STATISTICS`,
or `PRODUCTIVE COMPOSITION FALSIFIED`.
