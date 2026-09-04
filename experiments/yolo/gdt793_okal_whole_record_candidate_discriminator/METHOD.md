# GDT793 method — `okal` whole-record candidate discriminator

The experiment changes the unit of evidence from a token neighbourhood to a
complete physical paragraph/record and its complete page-local label
inventory. It does not infer a gloss from frequency.

## Occurrence and context census

All GDT791 occurrences whose complete ZL3b surface begins with `okal` are
retained. Running occurrences inherit the full physical paragraph delimited by
the published line flags. Local occurrences inherit one of three already
published visual owners: the text-blind special-circle array, the GDT790 f82
panel/component inventory, or the GDT581 f88 material-group owner.

Alternate readings are diagnostic readings of the same manuscript. The mixed
crosswalk is queried through the guarded CLI; it never supplies independent
semantic votes.

## Target-masked owner fingerprint

For record `r` and candidate label owner `o`, all one-character forms and all
complete forms beginning `okal` are removed. On the remaining exact wholes:

```text
S(r,o) = sum log((number_of_page_owners + 1) /
                 (owners_on_page_containing_form + 1))
```

The source owner is recovered only if it has a positive score, is the unique
top owner and has a positive margin over the runner-up. Thus the target cannot
recover its alleged source merely by repeating itself.

## Member identifiability

For each informative record, every maximum exact whole-form assignment from a
running family occurrence to a source-owner label is enumerated by count. A
member reading passes only when the same single local member is forced in all
maximum assignments.

## Ordered-array test

The already inventoried visual slot order is used; transcription row order is
not treated as reference direction. Every observed A-before-B relation among
different complete forms becomes a directed constraint. If the same array
also supplies B-before-A, the strict ordinal model contains a cycle and fails.

The five homologous outer-slot-4 occupants from f70v1, f70v2, f72r1, f72r2
and f72r3 are reported separately. Four `okal*` occupants can support a
slot-renderer rival, but do not mean “four” because the family also occupies
other positions.

## Working renderer

If the class/slot gate passes while the address, unique-member and ordinal
gates fail, exact complete `okal` receives the replaceable display
`KENNSTELLEN-/SYSTEMEINTRAGSCODE`. This is an owner-conditioned working
default, not a plaintext word. No longer form inherits it and no substring is
exported.

## Exploratory-source incident

Before the executable build, two delegated scratch audits accidentally used a
raw regex scan broad enough to traverse the mixed crosswalk. Their displayed
output was restricted to explicitly requested released loci and contained no
`f84*` row. Nevertheless, every value from those raw scans is excluded. The
executable experiment reacquires its alternate-reader material independently
through the guarded selector interface and records the rejection counts.
