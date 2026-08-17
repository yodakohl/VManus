# GDT241 — f82r HPR2 formal-field expansion

## Result

**F82R_HPR2_FORMAL_COVERAGE_EXPANDED_8_TO_17_LINES_SEMANTIC_ROLES_UNCHANGED**

The frozen HPR2 parser can segment nine additional f82r prose loci without
using visual information or inventing record positions.  Coverage rises from
8/32 to 17/32 human-catalogued prose lines (`53.1%`), producing 51 formal
fields rather than 26.  All eight overlapping GDT239 loci reproduce their
ordered source tokens, PAGE_HOSTs, compiler cells, and DY/line endpoints
exactly.

| layer | before | after |
|---|---:|---:|
| HPR2 formally segmented prose loci | 8 | 17 |
| formal fields | 26 | 51 |
| abstract/semantic-role-scaffolded loci | 8 | 8 |

The nine added loci are f82r.5, .6, .11, .13, .17, .18, .20, .21, and .30.
They contribute 25 formal fields.  Every new field retains `semantic_role =
UNASSIGNED`.

## Why roles were not extrapolated

GDT229's role analogy depends on record-relative position and a complete-line
frame.  These nine lines are absent from that frame.  Assigning them a guessed
position would be more damaging than leaving them unclassified: it would make
the page appear more translated by importing a coordinate the source does not
supply.

The resulting page stack is now explicit:

```text
45/45 human loci             coverage state known
32/32 prose loci             present in human census
21/32 prose loci             family consensus available
17/32 prose loci             HPR2 formal fields available
 8/32 prose loci             abstract role scaffold available
 0/32 prose loci             plaintext translated
```

## Next safe extension

The next formal task is not to guess roles for the new fields.  It is to build
an uncertainty-aware line/paragraph coordinate for the remaining prose while
preserving missing and alternative readings.  Only after that coordinate is
frozen can the external role instrument be applied to the additional fields
without position leakage.

## Claim ceiling

This expands formal field/compiler coverage only.  It assigns no new document
role, field ownership, object, action, material, condition, word, language,
plaintext, or translation.  No f84 row was retained, joined, or scored, and no
new f84 access occurred.
