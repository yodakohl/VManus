# GDT704 — one concrete herb-processing continuation

Status: `PASS_V77_15_ACTION_CONTINUATIONS__4_EXACT_HEAD_REPEATS__1_NEW_C015__C016_HELD__15_EDGES_10_COMPONENTS__ZERO_WORD_DELTA`

## Result

The strongest current continuation is now explicit enough to say what happens
to a material, not merely that "work continues":

> **f26r.2 / C011+C013+C015:** Die Krautdroge bis zur Mittelstufe erhitzen und
> abschließen. Zustand: mittlere Trockenstufe erreicht. Dieselbe erhitzte
> Krautdroge bis zur Mittelstufe abkühlen und abschließen. Die so abgekühlte
> Krautdroge mäßig trocknen, nochmals mäßig trocknen und abschließen.

The source of the first `hiervon` remains open.  The new claim begins only at
the already carried cooling batch: C015 links the output of the complete
cooling clause #6–7 to drying action #8, where `Krautdroge` is written again.

## Why this one wins the comparison

The full deck has 15 direct action→action transitions:

- 4 exact written material-head repetitions;
- 2 deictic targets;
- 3 related explicit heads;
- 5 explicit head changes;
- 1 transition with no written material head.

The four exact repetitions are not equivalent.  `f80v.35` and both
`f88r.19` cases repeat a Drogenstoff as an added ingredient.  They do not
process the output of the preceding addition.  At `f26r.2`, by contrast, C011
already supplies the same herb batch to #6–7, and #8 both rewrites that herb
and applies the next operation.  This makes it the sole output-compatible
member of the four-case control set.

The strongest rival remains live: #7 may close one batch and #8 may begin a
different herb batch with the same name.  That is why C015 remains local rather
than becoming a general repetition rule.

## C016 stays open

The tempting f115r.23 reading is:

> Die leicht getrocknete fertige Zubereitung weiter erhitzen, trocknen und
> ansetzen.

It is usable as a working alternative, but not yet as an edge.  `qokcho` at #5
contains no deictic marker and no material head, while the immediately
following #6 writes a Samenposten.  GDT704 therefore records C016 completely as
`HOLD_OPEN_B_LOW` instead of discarding it.

## Graph change

C015 changes M009 from a two-edge fork into a fork with a downstream action
chain:

```text
             #5 chedy (written intermediate state)
            /
#4 ykecthey
            \
             #6 yt(e)dy ──> #8 checthedy
                 #7 dy closes the source clause
```

The cumulative graph moves from 14 to 15 edges while staying at 10 components.
It now contains 28 unique edge nodes, 33 endpoint incidences, 30 minimal-hull
positions, 30 render positions, and 5 shared nodes.  Position #7 remains
structural but moves from render-only into the enlarged hull.  No #5→#6,
#5→#8, #4→#8, #6→#7, or #8→#9 edge is created.

## Scope and next move

All 479 token glosses, 51 line translations, 3 bound spans, and 36 pages remain
unchanged; no new word meaning is introduced.  The next useful pass is a
complete census of actions whose output is not separately named, beginning
with C015 target #8, looking for a later written state or repeated material
inside the same scope.  C016 remains available as the leading weaker rival.
