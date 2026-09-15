# Bounded review: an exact consequence of the existing transport card

2026-09-15, completed before the inclusive 14:43 UTC checkpoint.
Status: SOURCE_ONLY_RAW_REVIEW; no new idea, target test or writing model.

All six raw proposals IDEA000349–354 were reread. No additional source family
or card is added: the concrete result below strengthens the already retained
[IDEA000349](../../proposals/raw_global_transport_safety.json), without supplying
a new target owner or global writing contract. R1/R2 and all six source cards
remain unchanged. No target input/result, raw target cache, image, reserve or
outside contact was accessed.

The stable live route, controls topic, bounded transport idea search and
transport/state route-check were consulted. The returned
[GDT344 primary](../../../experiments/yolo/gdt344_grammar_transition_paths/REPORT.md)
was read completely: its formal transition path and readable event-path
comparator were not calibrated, and its joint gate did not authorize alignment.
That stop is retained; the word “path” does not reopen it.
[IDEA000140](../../proposals/complete_historical_game_move_narratives.json) was
reread completely: fixed game rules/setup, a full writing contract and an owned
target state remain missing. Transport safety was already a distinct content
case in IDEA349, so deriving its state graph is not a new game proposal.
The earlier complete IDEA124 read retains its missing physical inventory endpoint.

## Exact source-derived consequence, without a fixed path length

Use only IDEA349's existing formalization of Propositiones XVIII: one man rows
every crossing, carrying zero or one co-located cargo; unattended wolf–goat and
goat–cabbage pairs are forbidden. Those two dietary prohibitions formalize the
source's no-damage requirement and are not separately printed axioms. Every
agent begins left and ends right; no cargo is copied, discarded or renamed.
This is a conditional semantic model, not a newly identified historical notation.

Write E/W/G/C for empty/wolf/goat/cabbage cargo besides the man. The complete
safe-state graph has ten vertices and ten undirected edges. It has exactly two
simple start-to-goal paths:

```
G E W G C E G
G E C G W E G
```

The first is the complete owned source solution; the second follows from the
declared wolf/cabbage symmetry and is a calculated alternative, not another
printed solution. Repeated states are permitted: legal complete histories are
not restricted to these two simple paths or to seven crossings.

For **every** finite legal complete history, its crossing counts satisfy exactly

```
count(G) = 3 + 2a
count(W) = 1 + 2b
count(C) = 1 + 2c
count(E) = 2 + 2d            a,b,c,d independently nonnegative integers.
```

Necessity: erase closed subwalks until a simple path remains. Both possible
simple paths have the same base counts. A closed subwalk returns every cargo
and the man to the same shores, so each cargo count is even. Its total length
is also even; therefore its empty-cargo count is even. Restoring any erased
subwalk adds a nonnegative even number to each component.

Sufficiency: either simple path uses every cargo label, including E. On an edge
with label X, insert the immediate safe return and repeat crossing. Both endpoint
states are already safe; this adds exactly two X crossings and changes no
subsequent state. Such insertions can be repeated independently for all four
labels, realizing every displayed vector. Thus the formula is an exact inventory
of counts attainable by some safe path, not just a lower bound. The first and
last actual crossing must also carry G, since start and goal each have only one
incident safe edge.

These are computed consequences of the stated source model. They are not
printed source formulas, source-token counts, target-word counts or a grammar
for explanatory prose. A valid count vector does **not** certify an ordered
history. IDEA349's retained source rival exchanges trips one and three, keeps
all counts and the final inventory, and immediately leaves G and C unattended.
This separates physical path legality from aggregate accounting, including the
immutable-recipe semantics of the alloy family. It does not identify literal
animal names: W/C interchange, shore reversal and consistent identity renaming
remain symmetries.

## Reproducible source-only check and ownership

The following dependency-free Python enumerates the entire declared safe graph
and all simple complete paths. The proof above extends its finite output to
histories of arbitrary finite length; no depth cut-off is used for that theorem.
State bits are ordered man, wolf, goat, cabbage, with zero denoting the initial
shore. None of these bits or letters is a proposed manuscript character.

```python
from itertools import product

def safe(s):
    return not ((s[1] == s[2] != s[0]) or (s[2] == s[3] != s[0]))

states = [s for s in product(range(2), repeat=4) if safe(s)]
graph = {s: [] for s in states}
for s in states:
    for cargo in [None, 1, 2, 3]:
        if cargo is not None and s[cargo] != s[0]:
            continue
        t = list(s)
        t[0] ^= 1
        if cargo is not None:
            t[cargo] ^= 1
        t = tuple(t)
        if safe(t):
            graph[s].append((t, cargo))

start, goal = (0, 0, 0, 0), (1, 1, 1, 1)
paths = []
def visit(s, seen, moves):
    if s == goal:
        paths.append(moves)
        return
    for t, cargo in graph[s]:
        if t not in seen:
            visit(t, seen | {t}, moves + [cargo])
visit(start, {start}, [])
assert len(states) == 10
assert sum(map(len, graph.values())) == 20
assert paths == [[2, None, 1, 2, 3, None, 2],
                 [2, None, 3, 2, 1, None, 2]]
assert len(graph[start]) == len(graph[goal]) == 1
assert graph[start][0][1] == graph[goal][0][1] == 2
print("SOURCE_GRAPH_AND_TWO_SIMPLE_PATHS_PASS")
```

The existing [complete source dossier](NEXT_GLOBAL_MEANING_SUPPLY.md) owns both
problems and solutions XVIII/XIX, including their full native page inspection.
The [Migne PL101 public scan](https://www.documentacatholicaomnia.eu/02m/0735-0804,_Alcuinus,_Propositiones_Alcuini_Karoli_Magni_Imperatoris_Ad_Acuendos_Juvenes,_MLT.pdf),
PDF page 4 / printed columns 1149–1150, has SHA-256
`269d1c57add8dd719a392819aa63f22b6f1ec7e0ed4f68238d2de0f7b90f820e`.
The work is traditionally attributed to Alcuin. The cited BLB catalogue dates
a containing manuscript to the last third of the tenth century; those leaves
were not collated. PL101 was published in 1851 and reprinted in 1863, and this
extracted scan's particular impression is unidentified. No new source or image
acquisition was made for this bounded review.

The review changes no experimental selection. It supplies a useful exact
consequence for a future complete transport hypothesis, but merely assigning
arbitrary groups to crossing labels would still leave meaning unbound. A joint
reading may begin without a confirmed word; it needs a concrete shared writing
rule and an independently checkable consequence in a complete owned object.
Neither prerequisite is newly supplied here. Adding a second raw transport card
would duplicate IDEA349, so the pipeline retains this note and stops expansion.
