# GDT700 method

## Question

Does the complete current-scope `ACTION → one-token NOMINAL_BLOCK → ACTION`
census support nominating one occurrence-bound B-tier case in which an
action's written material patient is hypothesized to remain its result and the
participant of a following deictic, objectless action across an independently
evidenced state checkpoint?

## Inputs

- GDT699 supplies the immutable current scope: 479 tokens, 51 lines, 36 pages,
  three bound spans and inherited edge C010.
- GDT695 supplies the 175 fixed V68 clause realizations.  The 51 safe locus
  selectors are taken from the GDT699 line projection before the mixed source
  is queried through `./vmanus-exp query-tsv`.
- GDT687 supplies the independent local dispatch check: `f26r.2#5 chedy` is
  `NOMINAL_FINISHED_RESULT_STATE`, is not action-licensed, and carries
  `STATE_ONLY_NO_OBJECT` both before and after dispatch.
- GDT696 supplies held rivals H002--H005, held reference rows
  R012/R013/R016/R017 and the C006/C008 relation prototypes.  GDT697 supplies
  the frozen C001--C009 coverage; GDT699 supplies C010.
- GDT388 supplies the external edge-intake capacity contract.

## Method

The builder queries all 175 clauses at the 51 explicitly allowed current-scope
loci and slides a three-clause window within each locus.  A census member must
be exactly:

1. an `ACTION_CLAUSE`;
2. one single-token `NOMINAL_BLOCK` with no verb; and
3. the immediately following `ACTION_CLAUSE`.

Exactly ten windows meet that mechanical shape.  Their surfaces, ordinals,
verbs and current German working readings must reproduce the fixed ten-row
specification.  The predeclared candidate signature then requires all three of
the following at once: written material inside the source action, a state-only
middle block, and a deictic objectless target action.

One middle block, `chedy`, is independently evidenced as an exact state-only
result checkpoint.  Two more, `keey` and `kain`, are only state-like in the
current working gloss and have no written material head; seven are explicitly
material-bearing.  Two targets are deictic.  Only `f26r.2` combines a deictic
target, a written material patient in the source action and the exact
state-only checkpoint.  The `keey` and `kain` labels remain weaker
census-level editorial classifications and are not promoted to lexical facts.

The other deictic case, `f77v.7`, must remain held because its intervening
`rr#4` explicitly carries the competing working material *getrocknete Wurzel*.
The builder also proves that H002--H005 and R012/R013/R016/R017 remain held,
that C006 is only an action-output role prototype, and that C008 is merely a
nonadjacent B-tier precedent with a different fan-out topology.

C011 is emitted as a two-node B-hypothesis from #4 to #6.  Position #5 lies
inside the window hull but has no edge membership.  Positions #3 and #5 are excluded as
donors, #7 remains structural closure, and no edge reaches #8.  The complete
479-token, 51-line and three-span projections are replayed byte-identically.

Finally, the same edge is rendered in the GDT388 packet schema and passed to
`./vmanus-exp check-edge-packet`.  It is intentionally invalid/not score-ready
because its selection used formal text and it has no external capacity,
holdout or mobile-null evidence.

## Decision rule and claim ceiling

Pass requires exactly 175 source clauses, ten A--N--A windows, one externally
evidenced state-only checkpoint, two weaker state-like blocks, seven
material-bearing checkpoints, two deictic targets and one complete nomination
signature.  It adds only the working edge C011
`f26r.2#4 → #6`, retains C001--C010 unchanged, excludes #3/#5/#8, and changes
zero inherited token glosses, line translations, spans, word meanings or
pages.

C011 is an occurrence-bound B-tier working hypothesis.  Its source action
writes *Krautdroge* as a material patient, not as an output label; persistence
as “die erhitzte Krautdroge” is the proposed edge itself.  It makes the local
German microrecord more concrete, but it is not a verified identity, general carry rule, a new
meaning for `chedy`, `ykecthey` or `ytedy`, an externally grounded relation,
or a decipherment of Voynich plaintext.
