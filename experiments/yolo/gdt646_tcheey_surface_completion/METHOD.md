# GDT646 method

## Question

Can the newly exposed exact whole `tcheey` be given one concrete,
compositionally predictable reading that holds at every occurrence and closes
f35r.5 without importing f1r or new pages?

## Inputs

- Frozen GDT645 V22 allow-list, glossary, dictionary and line editions.
- GDT624 quality grid, GDT633 form ladder and GDT641 TCH family reports.
- Cached ZL3b token and ZL3b/IT2a/RF1b line projections.
- GDT631--GDT643 builders needed to replay the inherited line reader.

## Method

1. Replay V22 byte-for-byte before adding a card.
2. Materialize only the explicit 179-page allow-list through
   `./vmanus-exp query-tsv`; reject f1r and every f84-prefixed page before row
   materialization.
3. Census all exact `tcheey` positions and compare their three reader strings.
4. Build both complete quality ladders
   `{k,t}×{ch,sh}×{y,ey,eey}` and
   `{k,t}×{ch,sh}×{dy,edy,eedy}`. Compare the ordered E-length states with
   independently attested beginning/middle/end subdivisions of humoral
   degrees in Tadhg Ó Cuinn's 1415 materia medica. Observed reader-variant
   cells remain visible;
   absent cells receive no dictionary value.
5. Insert only the complete ZL3b surface `tcheey`, rebuild every line, and
   audit every changed position. Components remain bound analytic fields.
6. Replay the builder independently in a temporary directory and compare all
   output bytes.

## Decision rule and claim ceiling

Accept the surface only if it has at least one all-reader-exact occurrence,
the complete family supports one compositional default, every occurrence is
audited, and the source one-hole line closes without generic filler. Keep the
best rival explicit.

The accepted card is the replaceable working value
`tcheey = kalt und trocken am Ende des Grades`; „kalt-trockene Drogenform II“
and „kalt und trocken im zweiten Grad“ are the rivals. No component,
substring, absent cell, plaintext, phonetic value,
language, ingredient identity or universal syntax is promoted.

Run:

```bash
python3 experiments/yolo/gdt646_tcheey_surface_completion/src/run.py
python3 experiments/yolo/gdt646_tcheey_surface_completion/src/validate.py
```
