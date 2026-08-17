# GDT195 — readable f77 technical-homolog audit

## Question

Does a readable medieval technical comparator support the complete exposed
f77r proposal—six ordered state cells, one repeated state, four changing
boundaries with outputs, and one unchanged boundary without an output—or only
the much more generic background of four qualities, alchemical apparatus, and
staged transformation?

This is a target-exposed YOLO source-family audit.  It is not preregistered
confirmation.  It does not assign a word, sound, language, operation, material,
or plaintext to any Voynich group.

## Frozen target

The target is inherited unchanged from GDT180:

```text
COLD — DRY — HOT — HOT — MOIST — COLD
  out     out    no     out      out
```

The state names are the exposed GDT179/GDT180 hypothesis, not confirmed
translations.  The only author-visible target fact used here is the retained
mixed output topology: four emitting openings and one non-emitting central
opening.

## Source family

The audit retains six authority-bound comparators:

1. the already frozen official Walters W.73 four-element/four-quality square;
2. Barbara Obrist's scholarly survey of medieval alchemical visualization;
3. Wellcome MS.140, an early-fifteenth-century Italian medical-alchemical
   recipe compilation with distillation/sublimation and apparatus drawings;
4. a Wellcome catalogue record for a labelled fourteenth-century distilling
   apparatus (`Distilatio Aceti`);
5. Lehigh's fifteenth-century Arnald of Brussels alchemical diagram with four
   elements and four separation stages; and
6. the PAL scholarly manuscript catalogue record for Edinburgh Royal
   Observatory Cr. 2.3, whose five-circle volvelle carries five compound
   quality inscriptions, including a repeated `calidum et humidum` state.

The external HTML payload hashes were recorded on 2026-08-17.  The pages are
not copied into the repository.

## Exact-homolog rule

A retained comparator counts as an exact f77 homolog only if its source
documents all of the following in one authorial structure:

- six ordered state cells;
- state values expressed in the four-quality system;
- exactly one adjacent repeated state;
- five corresponding boundaries;
- four output/emission relations at changed boundaries; and
- one non-output relation at the repeated boundary.

Generic apparatus, a four-element square, a process with an unspecified number
of stages, or a repeated quality label is only partial source-family support.

## Algebraic specificity check

The four qualities are treated as the vertices of a four-cycle.  A changed
boundary is admissible only between adjacent vertices; an unchanged boundary
must repeat a vertex.  A complete cycle covers the four undirected edges once.

All `4^6 = 4096` six-state sequences are enumerated.  The check reports the
number satisfying the observed `1,1,0,1,1` output mask and the number satisfying
the same rule when the single non-output boundary may occupy any of five
positions.  This measures how much of the celebrated four-element coverage is
automatic after the exposed state assignment.

## Decision rule and ceiling

If no retained comparator satisfies the exact rule, the result is
`ALCHEMICAL_SOURCE_FAMILY_PLAUSIBLE_EXACT_F77_HOMOLOG_NOT_FOUND`.  Partial
comparators may strengthen only a broad medical-alchemical document-practice
prior.  They cannot confirm the state names or identify the f77 apparatus.

No f84 page, row, transcription, image, or formal payload is read, retained,
joined, or scored.
