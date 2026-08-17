# GDT237 — leave-one-section graphical-label prefix transfer

## Result

**GRAPHICAL_LABEL_PREFIX_COMPILER_CROSS_SECTION_PARTIAL**

The graphical-prefix layer is not just a q13 accident.  Across 3,857 non-f84
first-family loci (741 editorial labels), the GDT233 prefix inventory was
rediscovered separately in each leave-one-section-out fold.  Seven prefixes
were selected in all eight training folds.  On held sections, precision exceeds
the section's label prevalence in A, B, C, P, and Z; B/q13 and P/Pharma have
strong nominal enrichment.

| held section | test labels / rows | selected prefixes | TP / FP | precision | prevalence | lift | recall | p |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| A | 95 / 168 | 19 | 39 / 22 | .639 | .565 | +.074 | .411 | .0971 |
| B | 98 / 646 | 14 | 34 / 12 | .739 | .152 | +.587 | .347 | 5.42e-21 |
| C | 31 / 157 | 21 | 10 / 36 | .217 | .197 | +.020 | .323 | .420 |
| H | 20 / 1,257 | 24 | 1 / 238 | .004 | .016 | -.012 | .050 | .986 |
| P | 202 / 326 | 12 | 82 / 5 | .943 | .620 | +.323 | .406 | 3.55e-15 |
| S | 0 / 846 | 22 | 0 / 111 | 0 | 0 | 0 | 0 | 1 |
| T | 53 / 208 | 19 | 2 / 11 | .154 | .255 | -.101 | .038 | .889 |
| Z | 242 / 249 | 16 | 111 / 2 | .982 | .972 | +.010 | .459 | .306 |

Pooled precision is `.390` against `.192` prevalence, with `.377` recall.
Pooling is descriptive because section label prevalence differs dramatically.
The fold table, not the pooled number, is the primary interpretation.

## Interpretation

The cross-section successes support a reusable **graphical-label rendering
family**, particularly in q13 and Pharma.  The Herbal and Text failures show
that it is neither complete nor universal.  The seven training-stable prefixes
are architecture candidates, not words: they may mark particular graphical
registers, label construction classes, or source-family opportunities.

Together with GDT235, the decomposition is now sharper:

```text
TRANSFERABLE_PARTIAL_LABEL_RENDERER + REGISTER_BOUND_OPAQUE_CONTENT
```

The renderer transfers labelhood in some sections.  Neither the renderer nor
its stripped residual transfers coarse object identity.  This is exactly the
behavior expected from a compiler layer that helps format labels while content
remains locally allocated or distributed.

## Claim ceiling

The endpoint is editorial label kind only.  This establishes no authorial
label marker, ownership, object class, source word, morpheme, sound, language,
plaintext, or translation.  No f84 row was retained, joined, or scored, and no
new f84 access occurred.
