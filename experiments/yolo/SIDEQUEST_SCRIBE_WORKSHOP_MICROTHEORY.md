# YOLO sidequest: six-page scribe-workshop microtheory

Status: **deliberately speculative, post-hoc, and non-confirmatory**.

This is not a GDT result and does not modify any canonical claim. It asks what
a small workshop might plausibly have been doing if one deliberately tries to
make the current VManus grammar intelligible. The sample is fixed here to two
approximately comparable Herbal pages (`f10r`, Currier A; `f55v`, Currier B),
two biological pages (`f82r`, `f83r`), and two circle/astronomical pages
(`f67r2`, `f69v`). ZL3b is used for the displayed surface; reading uncertainty
is retained where it matters. `f84` and `f84r` were not accessed.

## Rapid iterations

### Version 0 — ordinary prose with encrypted words

Assume every visible group is a word and repeated groups are repeated lexical
items. This gives easy-looking sentences but explains the evidence badly:

- the same small pieces occur free, joined, and inside many surface groups;
- Currier B has many more compiled fields than comparable Herbal A pages;
- `s` is selected at physical-line entry and `q` after DY;
- exact-tuple/PAGE_HOST identities do not behave like a stable global lexicon;
- free predictive clustering of the 1,676 joint tuples produced no stable
  equivalence classes in GDT398.

Verdict: reject as the workshop's primary writing rule.

### Version 1 — a clean agglutinative language

Read `q-`, `d-`, `s-`, `-dy`, `-dal`, `-dar`, and `-sy` as morphemes around a
root. This explains `otedy/qotedy`, split/join forms such as `dar | ol/darol`,
and dense labels. It fails as a complete model: GDT003 does not beat strong
string baselines, segmentations overlap, the visual roles do not transfer, and
`AROL` occurs in plant/pharma labels as well as flow-like diagrams.

Verdict: retain productive-looking *formal construction*, reject a clean
global morpheme dictionary.

### Version 2 — pure nomenclator/codebook

Assume every exact joint tuple is an indivisible code. This explains opaque
repetition but not the regular line reset, wrapper licensing, DY fields,
split/join economy, or the shared grammar across registers.

Verdict: a codebook is present, but it is embedded in a compiler.

### Version 3 — leading workshop reconstruction

The best small-sample story is a **hybrid technical register: local address
codebook plus a shared record compiler**.

```text
PAGE_PROFILE := local inventory + diagram/specimen/process template

RECORD := ENTRY? FIELD (DY FIELD)* B3?
FIELD  := (WRAPPER FRAME? ADDRESS RIGHT_VALUE?)+

render(FIELD):
  choose joined/detached realization
  select s-form at a new physical-line entry where licensed
  select q-form after a DY closure where licensed
  abbreviate frequent address/value combinations
```

The content-bearing object is probably not one substring. It is the complete
page-conditioned address/construction. A visible group is therefore closer to
a filled form cell than to an ordinary word.

## Workshop dictionary v0.3

The right column is an intentionally aggressive guess, not a translation.

| Form coordinate | Best structural reading | Deliberate workshop guess |
|---|---|---|
| `PAGE_HOST` / exact address | page-conditioned opaque value | local item, state, material, or diagram-node code |
| `s-` | licensed physical-line-entry renderer | **NEW ENTRY / resume at margin** |
| `q-` | licensed post-DY renderer; productive `q+X` | **NEXT / linked continuation** |
| `d-` | recurrent binding wrapper | **OF / AT / WITH** relation |
| `ch-` | broad construction wrapper | ordinary **DESCRIPTOR** |
| `che-` | related extended wrapper | elaborated/derived descriptor |
| `sh-` | contrasting construction wrapper | state/result descriptor |
| `O` | local frame | default/current frame |
| `OT` | marked frame | alternate, referenced, or derived frame |
| right `aiin/ain` | recurrent right-side value family | count, index, or measure class |
| right `al/ar` | recurrent paired value families | two opposed variant classes, not left/right directions |
| `DY` | field closure | semicolon / **FIELD COMPLETE** |
| `B3` | harder record closure | full stop / **RECORD COMPLETE** |
| joined label | compressed record address | catalogue key with omitted field separators |

The least bad content guesses are deliberately abstract:

- `AROL`: **referenced unit/branch/item**, not water. This permits its reuse in
  plants, pharma, and diagrams. It may also be merely a frequent local address
  family whose value is rebound by page profile.
- `AIIN`: an **index/quantity-bearing value**, because it occurs both as a host
  and a right family. No number is assigned.
- `OK/OKEE/OKCH`: a broad family of **standard local entries/states**. The
  individual values remain page-local.
- `DAL/DAR/SY`: compact **variant/relation/status values** used especially in
  labels; they are not established suffixes or meanings.
- `OL`: a common **link/unit class**, compatible with free and joined use.

## Six-page micro-edition

### Herbal A — f10r

The page behaves like a relatively unsegmented specimen description. In the
GDT278-covered material, DY and B3 closures are absent. A representative line
is:

```text
f10r.2
dchey | cthoor | char | chty | os | chair | otytchol | oky | daiin | etyd

D:CHEY  CTHOOR  CH:AR  CH:TY  OS  CH:AIR  OTYTCHOL  OKY  D:AIIN  ETYD
```

Workshop paraphrase:

> Open the specimen entry under CHEY; list its CTHOOR, AR, TY, OS and AIR
> descriptors; add the OTYTCHOL/OKY classification and AIIN index; close the
> line.

This is not word-for-word plaintext. It treats the line as one long form whose
slots carry several local observations. The many `ch-` realizations are more
naturally repeated descriptor constructions than repeated content words.

### Herbal B — f55v

The matched page has the same broad illustration profile but uses a denser
record style. A covered line divides cleanly at `oldy`:

```text
f55v.11
ykaiin | cheoar | cheeky | oldy  //  aiin | okal | oltchy | or | y | orain

YK+AIIN  CHE:O+AR  CHE:EKY  O:L+DY
// AIIN  OK+AL  OLTCHY  OR  Y  OR+AIN
```

Workshop paraphrase:

> Specimen/index YK-AIIN: elaborated O-AR and EKY descriptors; field complete.
> Then record the AIIN value, OK-AL class, OLTCHY item, and OR/Y/OR-AIN detail.

The important contrast is architectural: B compresses a page entry into more
explicit fields. It need not be a different language. A small workshop could
have an older/descriptive A register and a later/tabular B register, with hand
and Currier differences inseparable.

### Biological — f82r

Here the same compiler is used as a dense apparatus/process ledger. `f82r.2`
contains four fields, the first two being single closed cells:

```text
dchedy // qolchedy // qokain | dy | qokeedy // qokal | lcheckhy | lched

D:CHE+DY
// Q:OLCHE+DY
// Q:OK+AIN  D:Y  Q:OKEE+DY
// Q:OK+AL  LCHECKHY  LCHED
```

Workshop paraphrase:

> Register component/state CHE; next linked OLCHE; continue with indexed OK,
> Y, and OKEE; then open the linked OK-AL detail and its two descriptors.

The diagram labels `darol` and the reading-unstable `darary` are then compact
addresses attached to two independently described flow-like structures:

```text
darol  ≈ D(relation) + AROL(local unit)
darary ≈ D(relation) + AR... (reading unstable)
```

The theory does **not** say AROL means flow. It says the page profile can bind a
generic/local address to an apparatus node.

### Biological — f83r

The page supplies a particularly form-like three-cell line:

```text
f83r.47
otchdy // qokchdy // shedal

OT:CH+DY // Q:OKCH+DY // SH:ED+AL
```

Workshop paraphrase:

> Mark the CH item in the alternate frame; continue with linked OKCH; finish
> with the ED state of variant AL.

The nearby labels can be made coherent without making them water words:

```text
darolsy   ≈ D(relation) + AROL(unit/address) + SY(variant)
saroldal  ≈ S(entry)    + AROL(unit/address) + DAL(variant)
```

The second form is transcription-uncertain (`sasoldal` in ZL3b versus
`saroldal` in IT2a/RF1b). The attractive reading is therefore only that two
parallel structures receive two related *catalogue addresses*. Their shared
part identifies a local class; the edges distinguish relation/entry and
variant. `AROL = water` remains excluded by plant-label counterexamples.

### Astronomical/circle — f67r2

This page is best read as several circular legends, not prose. Human inventory
defines a seven-member circular label set and a twelve-member moon-associated
set. Representative constructions include:

```text
ydchos | ain | ar | amy
sor | chedaiin | dy
todaiin | dain | dy
qotoear
ytodal
```

Workshop reading:

> A page-local table names or addresses members of several closed systems. A
> multi-group legend can carry an address, index/value and closure; compact
> one-group labels are precompiled catalogue keys.

The seven and twelve positions suggest celestial/system inventories, but no
group is assigned to a planet, sign, direction, or number. The same formal
compiler can render a legend item more compactly than a prose field.

### Astronomical/circle — f69v

The external geometry is unusually strong: 28 radial text loci and a strict
14 LONG / 14 SHORT alternation. The text does not reliably distinguish the two
visual classes. Several labels nevertheless look like closed catalogue cells:

```text
ytody  okody  otody  ykeydy  ykeody  sarydy  okeody
```

Workshop reading:

> This is a 28-entry cyclic schedule or observational register. Each spoke
> receives a local address and sometimes an explicit closure. LONG/SHORT is a
> layout/parity convention—possibly two alternating table states—not a decoded
> odd/even word contrast. DY closes an entry; it does not mean “day”.

A lunar/calendar-like practical purpose is the best genre guess, but direct
table transfer is weakened by the poor lag-14 textual symmetry and by generic
medieval prevalence of 28-member lunar systems.

## How the workshop could produce the manuscript

1. A master prepares a page template and a small local list of content
   addresses.
2. A compiler convention specifies entry, continuation, frame, value and
   closure states.
3. The scribe fills records from a source notebook, memory, diagram, or spoken
   instruction.
4. Frequent combinations fuse; rare combinations remain separated. Spaces are
   therefore construction boundaries, not necessarily linguistic word spaces.
5. A label suppresses most record scaffolding and joins an address with one or
   two discriminating values.
6. Scribes share the compiler but differ in abbreviatory habits and local
   codebooks. Currier A/B can therefore differ sharply while remaining one
   workshop technology.
7. Fossilized pieces survive after their original compositional motivation is
   lost. This produces apparent morphology that is real historically but not
   synchronically recoverable as clean slots.

## What this model explains unusually well

- free/bound and split/join reuse without requiring every piece to be a live
  morpheme;
- productive-looking `q+X` and right-edge DY without beating generic string
  models as a natural-language paradigm;
- `s` at line entry and `q` after field closure;
- Currier-B field density and its different renderer regime;
- labels being more compositionally dense than running text;
- repeated identical labels such as `daldy` as repeated filled form cells;
- local label/prose reuse without a global label dictionary;
- strong page/register effects and weak manuscript-global host semantics;
- failures of phoneme mapping, simple cipher mappings, universal semantic
  roots, and free latent-tuple clustering.

## Awkward facts

- The model can explain almost any local code by rebinding it, so it risks
  becoming unfalsifiably flexible.
- No page-local codebook has been recovered independently.
- Exact joint tuples are sparse and do not compress into stable free
  equivalence classes.
- Some long lines may still contain natural-language syntax that this form
  interpretation washes out.
- There is no anchored value for even one address, wrapper, or right family.
- The f69v LONG/SHORT alternation remains visual only.

## Sidequest conclusion

If I had to act as one of the scribes, I would not think “write an encrypted
sentence.” I would think:

> choose the page's item code; place it into the current record slot; mark
> whether this is a new entry, a linked continuation, a framed variant, or a
> value-bearing form; close the field; abbreviate the result according to the
> hand's house style.

The best explicit meaning guess is therefore not a vocabulary but a writing
procedure. The manuscript is most plausibly rendered as a **technical
catalogue/process notebook with page-local addresses and a shared scribal
compiler**, possibly carrying compressed natural-language residue inside some
addresses. On these six pages, that theory makes more coherent sense than a
word cipher, a clean agglutinative language, or a pure nomenclator.
