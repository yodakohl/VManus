# GDT476 method

## Question

How many of GDT474's 64 locally tied coordinate/instruction/catalogue bundles
can be given a better concrete default once GDT475's eight multi-locus records
are read as whole units?

## Inputs

- GDT474's 146 locus bundles and all three unchanged German working readings;
- GDT475's 146 boundary assignments, 135 microrecords and eight multi-locus
  continuation chains.

Only f17r, f71v, f72r, f77r, f88v and f89r are used. No new page or source
transcription is opened.

## Method

1. Select exactly the 64 GDT474 bundles whose minimum-repair model is tied.
2. Join them to their GDT475 record IDs and boundary roles.
3. Apply record context only when a record contains more than one locus. This
   touches twelve tied bundles in eight records. The other 52 keep their GDT474
   local default, so no form loses a meaning merely because context is absent.
4. Choose the record head in visible order:
   - a unique initial instruction is an action head;
   - an initial tied bundle that visibly contains an action root may be used as
     an instruction head;
   - a unique initial coordinate is an address head;
   - otherwise a learned-name initial bundle keeps the catalogue head already
     used by GDT474.
5. A tied bundle takes the head model when that model is one of its local
   minima. There is one bounded extra rule: an OL-bound continuation under an
   action head may recover an instruction model whose only local cost was one
   implicit verb. The inherited action supplies that verb, giving a contextual
   repair credit of exactly one.
6. Print the eight integrated record readings and all 64 tie decisions. Every
   alternative local minimum is retained in its own column.

“OL-bound” is a functional record relation, not a claim that the glyph sequence
`ol` is always a surface prefix. The literal GDT474 trace is preserved: for
example, `qkol`, `ykolairol`, and `doly` place the learned name before their OL
function in the working decomposition.

## Decision rule and claim ceiling

The context edition succeeds if it replays all 64 tied bundles, assigns each a
nonempty default, changes only selections among the three already printed
GDT474 readings, and gives every nonlocal instruction choice exactly one visible
action head plus one OL relation. Ties outside multi-locus records remain local
defaults rather than being forced by page proximity.

This is a creative working grammar. It may select and combine existing German
readings, but it may not change a component meaning, learned name, surface,
recipe, event, owner or page. It establishes no plaintext, language, confirmed
syntax, historical genre, object identity or confirmed lexeme.
