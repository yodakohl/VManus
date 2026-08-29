# GDT622 — concrete temperament-codebook working reader

Status: **CONCRETE_COMPOSITIONAL_WORKING_TRANSLATION_V1**.

## Result

The first useful concrete reader is not “one long Voynich word equals one long
instruction.” It is a hybrid page-record model:

`learned name candidate + distributed quality code + possible degree marker`

The working quality dictionary is:

| Surface composition | Working reading |
|---|---|
| `qo-k-ch-(y/ey)` | quality: hot and moist |
| `qo-k-sh-(y/ey)` | quality: hot and dry |
| `qo-t-ch-(y/ey)` | quality: cold and moist |
| `qo-t-sh-(y/ey)` | quality: cold and dry |

Thus the atomic defaults are `k=hot`, `t=cold`, `ch=moist`, and `sh=dry`.
`qo-` introduces the quality field. The final `y/ey` closes or connects the
bundle; it cannot be a particular degree because the same ending occurs on
source candidates with different degrees.

This is a concrete working theory, not a solved manuscript. In particular,
the pictured plant, a proposed page heading, and a later code have not yet been
shown to be one grammatical clause.

## Why this historical model is real

Official BSB Clm 667, catalogued to 1481–1490, contains readable learned drug
names followed by tiny compositional property codes. Across 28 manually read
rows the grammar is:

`WHOLE DRUG NAME + (c|f) [degree]? + (s|h) [degree]?`

Here `c=calidus` (hot), `f=frigidus` (cold), `s=siccus` (dry),
`h=humidus` (moist), and barred `p` is *primo*, degree I. Examples include
`Balsamum c s 2`, `Bdellium c 2 h pbar`, `Galla f 2 s 3`, and
`antimonium c s 4`. Individual qualities and degrees may be omitted. This is
the exact historical mechanism sought by the sidequest: learned whole words
and reusable technical stems in the same compact record.

The official provenance is bound in `SOURCE_PROVENANCE.tsv`. Hartmann Schedel
is the manuscript's provenance, not an asserted author.

## Formal Voynich support

All four combinatorial corners occur. Counting both `-y` and `-ey` spellings in
the f84-free working corpus gives KCH 89, KSH 17, TCH 79, and TSH 7 exact
forms. In Herbal-A the corresponding counts are 42, 4, 55, and 5. The dry
corners are therefore real but rare.

There are thirteen exact within-line minimal pairs: ten change only `k↔t`, and
three change only `ch↔sh`. The clearest examples are:

- f24r.12 `qokchy qotchy` — only the `k/t` axis changes;
- f25r.3 `qotchy qotshy` — only the `ch/sh` axis changes;
- f28v.5 `qotchey qotshey` — the same moisture contrast with `-ey`.

These lines strongly support a formal 2×2 composition. They do not by
themselves label the axes. They also warn against assigning every code on a
page to its pictured plant: f24r.12 places the proposed hot/moist and cold/moist
codes side by side. The record may contain contrasts, multiple referents, or a
different semantic orientation.

On the four preferred, pre-existing external plant proposals, comparing all
eight binary-axis assignments puts `k=hot, t=cold, ch=moist, sh=dry` first by
local occurrence count: 8 of 13 family occurrences, versus 6 for the runner-up,
with at least one match in all four blocks. This is the leading orientation,
not a fixed key. On the separate internal direct-image deck it remains first by
raw count but only second by binary page contact, and only two of four local
degree defaults match. `DECK_ORIENTATION_COMPARISON.tsv` exposes both views.

## Concrete candidate readings

The table deliberately separates a source expectation from the exact Voynich
span that receives a meaning.

| Rank | Page hypothesis | Exact target-span working reading | Source expectation not yet decoded |
|---:|---|---|---|
| 1 | f38r Balsam; `tolor` is the provisional name carrier | f38r.1 `okshol` → KSH → **hot and dry**; f38r.2 `otaiin` is a degree-II candidate | the name itself |
| 2 | f3r Diptam; `tsheos` is the provisional name carrier | f3r.13 `qokshey` → KSH → **hot and dry**; f3r.16 `qokol daiin` is a degree-III candidate | the name itself; name-to-quality distance is 12 lines |
| 3 | f45r liquorice; `pykydal` is the provisional name carrier | f45r.3 `kchol` → KCH → **hot and moist** | **root** and degree I have no decoded target span |
| 4 | f24r Cucurbita/squash page; carrier is unstable `por` (ZL3b) versus joined `porory…` (IT2a/RF1b) | f24r.12 `qotchy` → TCH → **cold and moist**; f24r.2 `qotaiin` is a degree-II candidate | the name itself; adjacent f24r.12 also contains opposing `qokchy` |
| 5 | f41v Myrrhis/sweet-chervil-like label, provisionally linked to Cerfolium | no temperament span | plant identity and “used in cooking” remain visual/source expectations only |

The readable source expectations are Balsam hot/dry degree II, Diptam hot/dry
degree III, liquorice hot/moist degree I and root, Cucurbita cold/moist degree
II, and Cerfolium as a familiar culinary herb. `WORKING_TRANSLATION.tsv` keeps
those expectations separate from target readings, so unassigned source content
cannot silently become a translation.

## Degree model

The best throughput defaults are currently:

- degree I: no dedicated marker in the two liquorice windows;
- degree II: the `otaiin` family;
- degree III: adjacent `(q)okol daiin`.

Their strengths are unequal. `otaiin` is common: 234 occurrences on 81 of 181
safe pages, including 45 occurrences on 29 Herbal-A pages. Absence is also
common: 94 safe pages lack both `otaiin` and adjacent `(q)okol daiin`. Neither
fact uniquely decodes degree I or II. The degree-III package is more selective:
only nine adjacent events on eight safe pages, and it occurs in both Diptam
candidate blocks. The bare `dain/daiin/daiiin` forms remain an unordered
number/degree family and must not be read as I/II/III.

## Alternate readings and attachment distance

ZL3b, IT2a, and RF1b are alternate readings of one manuscript. Stable points
include f24r.12 `qokchy qotchy`, f25r.3 `qotchy qotshy`, f45r.3 `kchol daiin`,
and f38r.1 `tolor ... okshol`. The crucial f3r dry corner is less secure:
ZL3b/RF1b read `qokshey`, while IT2a reads `qokchey`. f41v's label also varies
across all three readings.

Only f38r currently places the candidate name and selected quality form on the
same line. f45r separates them by two lines, f24r by eleven, and f3r by twelve.
Therefore the live grammar is a distributed page-record hypothesis, not an
established adjacent sequence.

## Boundary and next move

What is now materially better than the earlier generic edition:

- four short forms have concrete, compositional default readings;
- the four values predict an attested fourth corner and exact minimal pairs;
- one real late-medieval codebook demonstrates the required hybrid mechanism;
- every proposed plant name, property, degree, and unmapped source fact is
  separately visible.

What remains open is equally specific: attach a quality code to a named carrier
on repeated records, distinguish a true degree field from common formulae, and
extend the reader to a new folio without changing the four axis values. Until
that succeeds, this is the best working reader, not a full decipherment.

## Access correction

During a read-only audit, one reviewer used an unguarded repository search on a
mixed transcription and displayed an f84v row. No value from that row was used
in GDT622. The builder and every published result artifact use explicit guarded
selectors and exclude f84/f84r. The process breach is recorded in the active
ledger rather than hidden.
