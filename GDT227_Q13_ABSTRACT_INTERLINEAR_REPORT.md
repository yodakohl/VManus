# GDT227 — q13 abstract interlinear

## Outcome

**`ABSTRACT_Q13_INTERLINEAR_BUILT_IDENTITY_PLACEMENT_DESCRIPTIVE`**
**`Q13_IDENTITY_SLOT_STABLE_CROSS_REGISTER_PAGE_HOST_TRANSFER_NULL`**

GDT227 publishes a complete working interlinear for the 701 q13 fields in the
GDT226 scaffold.  It retains 1,896 source-group occurrences, their raw tokens,
HPR2 PAGE_HOSTs, compiler cells, record/field coordinates, and only the four
externally projected abstract classes.  This is the closest current artifact
to a parse of q13, but it is not a translation.

An excerpt from the first mechanical record on f75r illustrates the format:

| field | locus | abstract class | source groups | PAGE_HOSTs |
|---:|---|---|---|---|
| 1 | f75r.3 | instruction-clause-like | `qokain chal orchey qey kain sheeky ltain olkar or` | `ok al orchey ey k eeky lt olk or` |
| 2 | f75r.7 | short-argument-like | `pchedy` | `pche` |
| 3 | f75r.7 | short-argument-like | `qokshdy` | `oksh` |
| 4 | f75r.7 | instruction-clause-like | `ytain chedy qokar chy lol chedy qoky` | `yt y ok y lol y oky` |
| 5 | f75r.9 | short-argument-like | `qokchdy` | `okch` |
| 6 | f75r.9 | instruction-clause-like | `chcthy lo qokedy` | `cthy lo oke` |

The alternation is literal field structure; “instruction” and “argument” are
role likenesses learned from position and span in readable recipes.

## Identity placement

There are 130 exact PAGE_HOST identities recurring on at least two q13
physical folios.  Thirty-eight occur at least five times and place at least
80% of their occurrences in one abstract class.  Examples include:

| PAGE_HOST | occurrences | folios | dominant abstract class | purity |
|---|---:|---:|---|---:|
| `ok` | 173 | 9 | instruction-clause-like | .873 |
| `y` | 130 | 9 | instruction-clause-like | .877 |
| `ot` | 67 | 9 | instruction-clause-like | .806 |
| `aiin` | 40 | 9 | instruction-clause-like | .875 |
| `lche` | 20 | 7 | short-argument-like | .800 |
| `che` | 14 | 6 | short-argument-like | .929 |
| `pche` | 6 | 4 | short-argument-like | 1.000 |

With a whole physical q13 folio removed, the modal class of an exact PAGE_HOST
seen on other folios predicts 1,300/1,700 covered group occurrences (`.7647`),
versus `.6841` for the training-fold majority class: `+8.06` percentage
points.  Raw exact tokens give nearly the same gain (`+7.91` points) on fewer
covered occurrences.  HPR2 stripping therefore expands reusable coverage, but
does not improve placement accuracy materially over the raw group.

## Cross-register result

The q13 and Stars-B scaffolds are globally similar, but exact PAGE_HOST role
assignments are not a shared dictionary.  Training q13 PAGE_HOST placements
and applying them to Stars-B gives `.7040` accuracy, **below** the `.7219`
training-prior baseline (`-1.79` points).  The reverse direction is only
`+1.11` points.  Raw tokens do slightly better, especially Stars→q13
(`+6.01` points), again warning that stripping can remove useful surface
information.

This pattern is compatible with a common record compiler whose opaque values
or renderings are rebound by register.  It is also compatible with ordinary
register-specific vocabulary and the perfect hand/section confound between
these panels.  The test cannot distinguish those explanations.

## Use and ceiling

The interlinear is useful as a working scaffold: it identifies recurring
opaque units that reliably occupy long clause-like versus short argument-like
positions inside q13.  It does **not** show that `che` is an ingredient, `ok`
an action, or any host a word.  The next semantic step requires an external
content endpoint attached to several scaffold fields, not another internal
identity-placement score.

No diagram oracle or semantic annotation was joined.  No host meaning, word,
language, plaintext, or translation is established.  Raw f84 rows were
discarded before column parsing; no new f84 access occurred.
