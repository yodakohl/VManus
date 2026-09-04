# GDT790 — panel-owner image grammar overlay

## Result

**The image grammar fits as an additional owner layer and does not conflict
with the surviving text model.** GDT790 assigns all 123 prose lines on f77r,
f82r and f83r to thirteen paragraph records under ten visible image panels,
while leaving every token and all H1–H4/whole-word/bounded-field structures
unchanged.

The selected model is `PANEL_OWNER_WITH_EXACT_LOCAL_LABEL_REFERENCES`:

```text
PAGE
└── IMAGE PANEL = silent owner/topic
    └── PARAGRAPH RECORD
        ├── line-head tendency (H1–H4 or open)
        ├── bounded field such as X daiin
        ├── exact local label reference
        └── open complete forms
```

This is not a translation. It is a more informative renderer and a concrete
route toward meaning: the prose is no longer ownerless, but the picture is not
pretended to decode every word.

## Complete coverage

| Scope | Count |
|---|---:|
| official images reviewed | 3 |
| visible panel owners | 10 |
| paragraph records | 13 |
| prose lines | 123 |
| prose tokens | 940 |
| graphical label loci | 27 |
| label tokens | 28 |
| exact label-token/prose occurrence edges | 10 |
| usable multi-character edges | 9 |
| token meanings changed | 0 |
| prefix/root exports | 0 |

The page-level pattern is coherent:

- f77r's label-rich upper arch owns the longest local record: eight labels and
  142 prose tokens, versus one/92 and one/87 in the other two panels.
- f82r's lower communal pool is both the most visually populated and the most
  label-heavy: twelve labels and 126 prose tokens, versus zero/72 and one/80.
- f83r's three single-figure panels have no separate labels and 72, 84 and 63
  tokens. Its lower coupled system has four labels and 122 tokens distributed
  over two main and two embedded records.

This supports panel-level ownership. It does not by itself identify the
language or turn label count into syntax.

## The exact bridges that matter

Four multi-character label forms recur exactly in prose, producing nine usable
occurrence edges:

| Label form | Picture owner | Prose bridge | Current use |
|---|---|---|---|
| `otedy` | f77r upper arch, inner port 2 | f77r P2 opener plus four f82r/f83r occurrences | same-page back-reference candidate; cross-page name/formula |
| `okal` | f82r lower pool, upper station 2 | f82r P1 and P2 | forward/shared-station reference candidate |
| `otchdy` | f77r middle west figure-zone | f83r Q1 opener | recurring name/formula at an embedded record head |
| `olaiin` | f82r lower pool, figure 6 | f77r P3 | recurring label/name form |

The remaining edge is the one-character token `o` from f77r.50; it is retained
for completeness and excluded as an anchor.

The useful asymmetry is new. `otedy` is first a visible upper-arch label and
then exactly the first token of f77r P2. `okal` runs in the opposite document
direction: it occurs in two earlier prose records before appearing as a lower
pool label. Labels can therefore behave as references or learned names, not
only as captions sitting next to their paragraph.

## Best visual composition leads

Five whole-form families survive as explicit exploratory leads:

1. **`darol/darolsy` → Zufluss-/Auslasskennung.** This is the strongest new
   image-conditioned family: `darol` is at the left vertical inflow on f82r;
   `darolsy` is at an open lower outlet on f83r.
2. **`okal/okaldy` → benachbarte Beckenstellenkennung.** Both labels occupy
   adjacent upper stations in the same f82r communal pool; `okal` also has two
   exact prose occurrences.
3. **`dchdy/otchdy` → Anschluss-/Stationskennung.** The forms occur at an
   inner arch opening, a body-station zone and the head of an embedded coupled-
   panel record.
4. **`otedy/dotedy` → Bogenstellen-/Übergangskennung.** Both are labels on the
   same f77r upper arch; `otedy` supplies the strongest same-page text bridge.
5. **`otol/otolaiin/olaiin/olsaiin` → Gefäß-/Bogenstellenfamilie.** These forms
   cover an inner arch point, a lower vessel station, a communal-pool figure and
   a right arch endpoint.

These are useful working semantics for the *observed whole labels in their
image contexts*. They do not license `d`, `ot`, `ol`, `dy`, `sy` or `aiin` as
free dictionary entries. In particular, this panel set gives no reason to call
`ol` “water” or “oil”: ol-like forms label figures, arch endpoints and station
zones as well as liquid-looking structures.

## Renderer example

f82r.1 belongs to the upper coupled two-woman system with a central apparatus.
The exact line is:

`qosheedy qokeol daiin shckhy okeeor cheey daiin shey`

The new structural rendering is:

> Bildbesitzer: oberes gekoppeltes System aus zwei Frauen und einem
> Zentralapparat. `[qosheedy] [qokeol → Wert-III-Kandidat daiin] [shckhy]
> [okeeor] [cheey → Wert-III-Kandidat daiin] [shey]`.

That is deliberately less fluent than the old invented procedural prose and
far more informative than “take the work item”: it fixes the paragraph's
visible subject, exposes its two parallel bounded value fields and leaves the
unresolved words unresolved.

For f77r.25, the renderer additionally marks its first token:

`[BILDVERWEIS otedy → F77_TOP_ARCH/INNER_PORT_2]`

For f83r.47 it marks:

`[LABELFORM otchdy]`

because the exact form is known as a label on another page, but its f77r object
meaning is not silently transported to f83r.

## Compatibility with the existing model

Nothing structural is destroyed:

- H1/H2 entry bias and H3/H4 internal/late bias remain text-internal roles.
- Exact whole words still outrank any component hypothesis.
- GDT741's occurrence-local attachment logic remains the only route from a
  nearby field to a text relation.
- GDT764's bounded `X daiin` grammar remains intact; the image supplies the
  record owner, not the value unit.
- GDT590's warning survives: ordinary prose words do not acquire a particular
  pictured woman merely from proximity.
- GDT201, GDT262 and GDT263 still block universal prefix zoning and automatic
  label-family-to-paragraph lattices.

What is retired here is only the renderer path that filled unresolved prose
with generic actions or obsolete drug-part assumptions.

## Interpretation

The best current working theory is now more specific:

> These three pages are configuration sheets. A paragraph is primarily a
> record about the adjacent visible body/vessel/channel configuration. Labels
> name local stations or components. A small subset of those label forms can
> reappear as record-internal references or learned names. Text grammar then
> describes fields within that externally supplied topic.

That model explains why the paragraphs are grammatically repetitive while the
images provide the missing concrete noun phrase. It also explains why a
word-by-word image translation kept failing: much of the subject is silent in
the text because it is already drawn.

## Next route

Stay on these same three pages. Compare complete-form and bounded-field
distributions across the ten topology classes—single figure, paired figures,
multi-port arch, transfer channel, communal pool and outlet system. The next
useful meanings should be complete forms that repeatedly discriminate those
visible topologies. Only after that should another page be used to test whether
the learned panel-conditioned meanings hold.
