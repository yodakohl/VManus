# F77r residual-form assignment analysis

## Exposure and question

This is a **post-hoc diagnostic**, not a preregistered confirmation. The f57v
quality-position forms, the f77r segment forms, their two-bit state assignment,
and an initial edit-distance pilot were visible before this document was
written.

The narrow question is whether the f77r labels retain state-specific spelling
similarity to the corresponding f57v quality-position forms **after removing
the two surface features that defined the states**. A positive answer would be
independent residual support for lexical state identity. A negative answer
would leave only the previously reported two-bit structural transition bridge.

`HOT`, `MOIST`, `COLD`, and `DRY` below are inherited f57 source-homology
position names. They are not Voynich word translations.

## Frozen reconstruction

The four f57 exemplars are inherited unchanged from the exhaustive neighbour
inventory:

| State position | Exemplar |
|---|---|
| HOT | `f57v.6` |
| MOIST | `f57v.7` |
| COLD | `f57v.8` |
| DRY | `f57v.9` |

The six f77r segment labels and their states are inherited unchanged from the
transition-bridge artifact. For every manual reading, normalize each complete
surface by concatenating spaces, removing one leading `ot` when present, and
removing one terminal `y` when present. These are exactly the two defining
bits; no other glyph or parsed root is removed.

For each possible bijection from the four f77r target states to the four f57v
exemplars:

1. score normalized character Levenshtein similarity;
2. average across f77r labels within each target state;
3. average the four state means so duplicated HOT and COLD labels do not get
   extra weight;
4. compute each alternate reading separately and their equally weighted mean;
5. enumerate all `4! = 24` bijections with exact rational arithmetic.

Report the number of assignments strictly above and exactly tied with the
observed identity assignment. Do not break ties by permutation order and do
not report an inferential p-value.

Deletion diagnostics remove, one at a time, each member of the duplicated HOT
and COLD states: `f77r.2`, `.7`, `.4`, and `.5`. Singleton-state deletion is
undefined for the state-balanced score and is not performed.

## Decision ceiling

The identity assignment must be a unique optimum in the full joint score and
remain a unique optimum under all four defined deletions to support residual
lexical identity. Any failure is a final nonconfirmation of this fixed
residual-form model only. It cannot erase the author-visible f77r transition
topology, establish an alternative assignment, or translate a label, affix,
quality, element, apparatus part, clause, or language.
