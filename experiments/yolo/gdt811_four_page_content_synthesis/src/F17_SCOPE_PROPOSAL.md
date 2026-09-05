# GDT811 — f17r complete-page reading and a two-field scope proposal

Design written before running `scope_inventory.py`. The two f17r cases below
were already noticed manually; they are discovery examples, not predictions.
The inventory uses the existing thirty-page GDT791 release only. This proposal
adds no dictionary meaning and does not replace the GDT809 working reader.

## Complete admitted page text

The page contains twelve running-prose lines in three paragraphs, plus a
separate marginal/label transcription record. The latter is not the end of
the third paragraph. Source: selector-first queries of the cached ZL3b and
cross-transcription line tables, restricted to `f17r`.

```text
f17r.1  fshody daram ydar chog opydy ypod chop otchy dody oldckhy
f17r.2  ydair choky okshy qodar ckhody dor otchol qodcthy ods
f17r.3  chol or chy qodam okor chor okchom

f17r.4  tcho shol qokol qor olaiin opydg som ypchy ypaim
f17r.5  ychekchy cthy chor shor cphor cphaldy dair cthey qody
f17r.6  tsho qof cho qokcheor cheteg

f17r.7  ksheo qokchy choldshy zepchy d opchordy
f17r.8  dchchy dychear schar ykchy
f17r.9  soy chckho o das chypcham
f17r.10 dar chear dcheor sain y mol
f17r.11 otchol cthar okaiin chol daiiin
f17r.12 ychod y chotom

Separate @Lx record:
f17r.13 oteeeon oiil
```

## Direct image reading, not automatic caption evidence

The inspected existing whole-page image shows one connected plant, many long
narrow leaves, three similarly drawn blue/white flowering heads, and fine
roots. Two red eye/lozenge-like outlines occur in the root region. There is no
unmistakably different fruit organ alongside the flowers. Thus leaf/herb and
flower/fruit are compatible candidates, not word-to-organ identifications.
The three flowering heads cannot confirm `daiin=III`: no complete `daiin`
occurs on this page. The text has `daiiin` at .11 instead. The two root outlines
identify neither a number nor an eye remedy.

The faint writing above the main text is spatially separate. The exact
location/extent of the cached @Lx extraction within it is not independently
recovered here. IVTFF records illustration interruptions after `opydg` on .4,
after `cphaldy` on .5, and around `d{c'a}` on .7. Those gaps around the drawn
heads are not established sentence boundaries.

## Observed repeated frame

```text
f17r.2–3  otchol [qodcthy ods]  chol [or ...]
f17r.11   otchol [cthar okaiin] chol [daiiin]
```

Each four-token `otchol X Y chol` span is exact in ZL3b, IT2a and RF1b. They
are alternate readings of one manuscript. The first span crosses a physical
line, the second does not. `qodcthy` and `cthar` are not silently equated, nor
is a `cth` component licensed by their resemblance to `cthy`.

The positional candidate is `otchol [material? form?] chol [specification?]`.
It predicts two intervening positions and a reusable attachment, not a
particular plant or numerical meaning. Two interior words might instead be
two separate items, a name plus qualifier, or an unrelated text fragment.

## Two coherent bracket readings

In both readings the unrecognized words keep their exact spelling. The
punctuation and brackets are editorial proposals, not decoded connectives.
Existing low-confidence whole defaults are `cthy=leaf/herb`, `chor=flower`,
`shor=fruit` (the reverse is equally live), `chol=dry`, `shol=moist`,
`okaiin=preparation`, `dair=portion II`, `cthey=drug form I`, and
`qody=finished preparation`. For this comparison alone, inherited
`otchol=cold-dry` and `daiiin=value IV` are disclosed assumptions, not new
dictionary licences. Unknown strings repeated in either rendering retain
the same unresolved identity.

### P — predicative, local material-and-quality frame

This treats the two interior positions as a tentative subject/form phrase.
The first quality precedes that phrase; the second qualifies it further.
It does not attach every property on the page to the pictured plant itself.

```text
P1: [fshody daram ydar chog opydy ypod chop otchy dody oldckhy]
    [ydair choky okshy qodar ckhody dor]
    [kalt-trocken?: qodcthy ods] [trocken?: or chy qodam okor]
    [Blüten?: okchom].

P2: [tcho] [feucht?] [qokol qor olaiin opydg som ypchy ypaim]
    [ychekchy] [Blatt/Kraut?, Blüten?, Früchte?] [cphor cphaldy]
    [Anteil II?] [Droge Form I?] [fertige Zubereitung?]
    [tsho qof cho qokcheor cheteg].

P3: [ksheo qokchy choldshy zepchy d opchordy]
    [dchchy dychear schar ykchy] [soy chckho o das chypcham]
    [dar chear dcheor sain y mol]
    [kalt-trocken?: cthar Zubereitung?] [trocken?: Grad IV?]
    [ychod y chotom].
```

The bracket before `chor` in P1 is not an identified syntactic boundary.
The actual unresolved issue is whether its dry qualification reaches that
flower candidate through `or chy qodam okor`. P2 likewise has no recovered
word that selects the subject of `shol`. These holes remain explicit.

### R — forward rubric, material-state sections

Here the same qualities introduce categories instead of predicates about a
single continuing subject. `chol` can be read as a dry/dried-material rubric;
`shol` as a moist-material rubric. Fresh material is a possible narrower
interpretation, not an established synonym. Rubric scope ends at another
quality marker or the paragraph boundary; an unresolved preliminary header
does not receive an invented command.

```text
R1: [fshody daram ydar chog opydy ypod chop otchy dody oldckhy]
    [ydair choky okshy qodar ckhody dor]
    KALT-TROCKEN?: [qodcthy ods].
    TROCKEN/GETROCKNET?: [or chy qodam okor] Blüten? [okchom].

R2: [tcho]
    FEUCHTES MATERIAL?: [qokol qor olaiin opydg som ypchy ypaim]
    [ychekchy] Blatt/Kraut?, Blüten?, Früchte? [cphor cphaldy]
    Anteil II?; Droge Form I?; fertige Zubereitung?
    [tsho qof cho qokcheor cheteg].

R3: [ksheo qokchy choldshy zepchy d opchordy]
    [dchchy dychear schar ykchy] [soy chckho o das chypcham]
    [dar chear dcheor sain y mol]
    KALT-TROCKEN?: [cthar] Zubereitung?.
    TROCKEN?: Wert IV? [ychod y chotom].
```

R makes the two `chor` occurrences potentially the same plant part in dry
and moist material contexts. It does not prove the boundaries, state change,
or the value's dimension. Its final short rubric still lacks an explicit
material unless carry-over is established. That is a concrete bottleneck,
not permission to invent an omitted ingredient or operation.

The alleged connective `y` is unsuitable as a local rescue: RF1b omits the
standalone .10 token and IT2a/RF1b read .12 as `ychody chotom`. Also do not mix
the older `okaiin=hot III` reading into a sentence while counting the current
`okaiin=preparation` dictionary as support. Those are rival interpretations.

## Inventory declared before execution

1. Use exactly GDT791's thirty physical pages / thirty-five explicit source
   selectors. The extra selectors are foldout subdivisions, not new pages.
   Load the existing line-owner atlas; only `RUNNING_PROSE` enters scope.
   Query the mixed cross-transcription table through `query-tsv`, with these
   allow-values and explicit columns, rejecting `f84` and `f84r` first.
2. A strict paragraph begins with a start flag and ends with an end flag.
   It must stay within one selector, have consecutive line numbers, and
   contain no non-prose or missing line. A change between distinct nonempty
   GDT791 record IDs also breaks scope. Orphan/incomplete spans are excluded.
3. Emit every running-prose `otchol` occurrence, including an explicitly
   unscorable row when its line lacks a strict complete paragraph. In an
   eligible paragraph find the first following exact `chol`, or record
   absence to paragraph end. Other intervening `otchol` tokens are retained.
   Count intervening whitespace tokens, exact width two, and physical-line
   crossing. Never search across a paragraph to obtain a preferred partner.
4. For a found target, concatenate the same source lines in each alternate
   reader and count the exact complete source segment. Support requires its
   multiplicity to equal the nonzero ZL3b multiplicity. This avoids fixed
   token-index alignment after reader word-boundary differences. For absence,
   the complete source suffix must additionally remain an exact suffix of
   those same alternate lines; a later added `chol` cannot masquerade as
   absence. Missing alternative lines give no support. Unscorable rows give
   no segment support. Retain all reader counts, not only successful cases.
5. Report the whole inventory and an external subtotal excluding all f17r.
   No external exact-width-two case means no extension on this released
   scope, not refutation of the two visible examples. An external case is a
   formal recurrence lead only; there is no null-derived discovery claim.
   Exact width two does not identify the interior words, subject roles,
   cold/dry meanings, grammar, lexemes, or a preferred P/R interpretation.

This differs from GDT748's one-neighbour question and GDT810's number of
following value tokens: the new object is a two-position bracketed interval,
with physical-line crossing preserved. It does not reopen those routes.

Outputs: `SCOPE_INVENTORY.tsv` and `SCOPE_RESULT.json`. The result records
source/design hashes and scope exclusions. New relation evidence remains
already-inspected text-only evidence; GDT388 intake must be performed by the
enclosing experiment before any score-ready claim. No semantic credit or
free component export is issued by this inventory.
