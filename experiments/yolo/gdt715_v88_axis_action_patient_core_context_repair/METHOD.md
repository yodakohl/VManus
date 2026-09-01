# GDT715 method — V88 axis/action core–context repair

## Question

Can the seven V87 readings held for an abstract value axis or an open action
patient receive a useful default without pretending that a locally supplied
axis or object belongs to the word itself?

## Inputs

- The complete V87 active dictionary, 479-position context table, confidence
  dictionary, held queue, bound spans, and f7r.2 renderer from GDT714.
- Exact value-cell rows from GDT626/GDT627, the GDT686 value-axis dispatch,
  and the exact GDT690 local `aiiin` selection.
- Exact whole/action rows from GDT662/GDT664/GDT678/GDT679/GDT681/GDT687.
- The seven exact admitted line contexts from GDT682.
- GDT711 family bonuses and caps; only `F_N` can add score in this pass.

## Method

Each target has two authored readings:

1. a narrow lexical core, reusable only as the existing exact-whole card;
2. a practical realization for its one active position, allowed to consume
   only the explicitly named immediate context.

The value terminal contributes only the Roman cell.  `aiiin` therefore has the
portable core `Wert IV`, with local `Menge IV`; `ydaiin` has `Bezugswert III`,
with local `davon: Wert III`.  For action cards, the verb/action skeleton stays
in the core while the patient is supplied only in the position rendering.

Every authored evidence claim resolves against an exact row and exact field
assertions in `V88_19_PRIMARY_EVIDENCE_BINDINGS.tsv`.  Score additions are
recomputed from the GDT711 family table, never copied from prose.  All 317
non-target active readings and all 472 non-target positions must survive by
fieldwise V87→V88 parity.

The two inherited bound spans remain byte-identical.  The existing f7r.2
`keo r` consumer is regenerated from V88 contexts; the right token is consumed
without output, while the revised `dold` context must appear at P291.

## Decision rule and claim ceiling

A target is accepted when its exact source row, exact active position, expected
left context, family-derived score, core/context split, and non-export rules all
replay.  No action score is raised for more fluent prose.  A local patient is a
working occurrence hypothesis and is kept in the context column, never in the
portable core.

This is an exploratory working dictionary and concrete renderer, not confirmed
plaintext.  Components are not promoted to free words.  Historical status is
`H0_NONE`; no new page, image, transcription, f84, or f84r is used.
