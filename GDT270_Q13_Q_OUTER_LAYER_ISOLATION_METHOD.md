# GDT270 — q13 q outer-layer isolation

## Question

GDT269 showed that the q13 earlier-record association is not merely a change
in PAGE_HOST vocabulary, but it weakened under local-position matching.  This
exploratory post-hoc decomposition asks whether `q` remains separable when all
other same-group HPR2/compiler coordinates are held fixed.

The tested group cell is:

```text
WRAPPER + O/OT_FRAME + INNER_D + PAGE_HOST + RIGHT_FAMILY + DY + B3
```

`q` and bare/`NONE` are the only wrapper values compared.  `OTHER_COMPILER`
means the exact tuple `(O/OT_FRAME, INNER_D, RIGHT_FAMILY, DY, B3)`.  No member
receives a linguistic or semantic interpretation.

## Panel

Rebuild the unchanged GDT267/GDT269 nine-page, eighteen-record q13 panel from
the f84-free `gdt227_q13_abstract_interlinear.tsv`.  Expand aligned source
tokens, PAGE_HOST values, and compiler cells.  Retain all 632 q-or-bare group
occurrences.  Lexical order of the two eligible record IDs per page continues
to define `EARLIER` and `LATER`.

## Reported conditioning family

The capacity audit tried the following fourteen conditionings; all are frozen
and reported rather than selecting only the best result:

1. PAGE_HOST and page
2. plus RIGHT_FAMILY
3. plus DY
4. plus B3
5. plus O/OT frame
6. plus INNER_D
7. plus the joint RIGHT_FAMILY/DY/B3 tuple
8. plus exact OTHER_COMPILER
9. exact OTHER_COMPILER plus within-field position
10. right/closure tuple plus within-field position
11. exact OTHER_COMPILER plus field endpoint
12. exact OTHER_COMPILER plus joint within-field-position/endpoint
13. exact OTHER_COMPILER plus record-relative quartile
14. exact OTHER_COMPILER plus existing field-role-like class

For each conditioning, retain only strata in which `q` allocation can vary
given the fixed wrapper and earlier/later margins.  Report the exact
hypergeometric conditional association, Mantel–Haenszel odds ratio, and page
conditional scores.

The clustered null uses the same nine page-level sign flips for all fourteen
conditionings.  Each statistic is the absolute standardized sum of page
scores.  Report local and max-fourteen inclusive p-values from the complete
`2^9` world set.  Duplicated/no-op conditionings remain in the declared family,
making the adjustment conservative rather than silently deduplicating them.

## Claim ceiling

A positive result can establish only that `q` behaves as a separable outer
constructional renderer within this q13 panel after fixing specified parser
coordinates.  It cannot establish a spoken prefix, word, morpheme, semantic
operator, universal record ordinal, language, plaintext, or translation.
GDT268 remains the weak/nonconfirming Q20 transfer.  No f84r access is
authorized or performed.
