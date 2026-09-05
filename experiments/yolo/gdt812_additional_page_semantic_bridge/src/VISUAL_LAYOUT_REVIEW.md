# GDT812 — source-bound pharmaceutical layout review

## Scope and direct sources

The reviewer personally viewed the previously released f88r and, only after
`PAGE_ADMISSIONS.tsv` recorded their admission, the new f100v/f101r spread.
No other new manuscript image was opened. This is manual observation, not
OCR, image generation, an automated visual score or a species identification.

The official [Yale IIIF manifest](https://collections.library.yale.edu/manifests/2002046)
labels canvas/image **1006249** “100v and 101r”. Its native dimensions are
7486 by 3715 pixels. The inspected [4000-pixel official image](https://collections.library.yale.edu/iiif/2/1006249/full/4000,/0/default.jpg)
is 4000 by 1985 pixels, SHA256
`2b15a1174546ec5a5770811306064e46320d021ec3d4e4a576ec35b9412b22e6`.
f100v is the narrower left page; f101r is the wider right page. A shared
digital canvas does not turn them into one physical page.

The inspected [f88r image](https://collections.library.yale.edu/iiif/2/1037112/full/2000,/0/default.jpg)
has SHA256
`aa266580695fc4a84cd031015c56f51f1b6ce807b6998c6ef4b8b68bae11983b`,
matching GDT811 `src/VISUAL_SOURCES.tsv`. No private cache path is a public
reproduction dependency.

## f100v: local inscriptions, one vessel, a collective prose block

A tall, comparatively simple vessel-like drawing stands at the upper left.
Its upper body is painted red and blue. The remaining drawing field contains
separate botanical figures arranged in loose horizontal tiers. Some show
branched stems and attached roots, some have broad leaves, and others have
fine repeated leaflets. Several have only a small basal stem or root remnant.
These are observations of depicted components, not named botanical taxa.

Short inscriptions occur in the spaces around the botanical figures, often
near their lower stems or roots. No visible leader lines or enclosing caption
boxes turn those neighbours into a complete, mechanically recoverable owner
mapping. One connected plant can contain several distinguishable components;
one nearby inscription need not be its whole-plant name.

A substantial running-text block lies below the botanical tiers. The picture
does not divide the page into one vessel plus one paragraph for each plant
row. Nor does one drawn vessel require the text to describe only one plant.
The layout is compatible with a collective material discussion, with a
preparation involving multiple entries, or with another grouping rule.

The subsequently available complete admitted reader agrees with this broad
distinction: f100v has 13 local `L` inscription loci and nine running `P`
lines in one source-marked paragraph. Those are transcription counts, not
13 independently certified botanical name assignments.

## f101r: the displaced vessel is real; the caption-transfer test is not

The wide page has dense upper and middle bands of separate botanical figures,
two broad visual bands of running text across much of the page width, and
another botanical band below them. These visual bands are not paragraph
counts: the complete admitted reader marks three source paragraphs,
`f101r.1–2`, `.3–6` and `.7–10`, in ten running `P` lines and has zero local
`L` inscriptions. The first two source paragraphs occupy the upper broad
text band. Roots, basal stems, leaves and flower-like heads
are drawn with different amounts of detail and colouring. Incomplete paint
and blank interiors are not encoded as absent organs or different substances.

Two tall vessel-like figures stand near the left edge of this page. A third,
largely unpainted vessel is embedded among the bottom-row botanical figures:
there are botanical figures to its left and right. This directly confirms the
catalogue-selected layout intervention. Its visible position is not the
left boundary of that complete botanical row.

There are no comparably evident isolated plant captions around these f101r
figures of the kind visible on f100v and f88r. Thus the displaced vessel does
**not**, by itself, supply a label that can be tracked from a margin to an
interior object. The bottom vessel and botanical row are below both broad
text bands; there is no new prose block visibly beginning immediately below
that vessel. A universal rule requiring every vessel to begin its own
following, captioned row-plus-paragraph unit does not describe this layout.

Three source paragraphs and three vessels still permit a count-based proposed
alignment. Equal counts do not establish its direction, boundaries or owners.
The present observation must not be reported as a two-paragraph/three-vessel
numerical mismatch.

This does not prove that a preceding paragraph cannot refer to the bottom
row, that a vessel cannot stand for a preparation, or that one paragraph
cannot discuss several vessels. Those remain possible relations, not drawn
connectors. Moving the supposed subject forward or backward through the
text would require independent evidence.

## f88r: three inscription records are not three pictured owners

The lower grouping must not be simplified from GDT811's transcription loci
into an object count. Its local records are `f88r.23` (`ofyskydal`),
`f88r.24` (`otor am`, alternatively one written whole in RF1b), and
`f88r.25` (`ofaldo`). These are three inscription records, not a demonstrated
three-name/three-object bijection.

In that part of the image, a smaller root-and-leaf figure is to the left,
a much larger root system with attached green foliage occupies the right,
and a vessel is at the left margin. Two inscriptions occupy the neighbourhood
of the left plant/vessel interface; another is near the upper part of the
large right-hand figure. The visible layout alone does not resolve whether
the first pair separates vessel from plant, describes two plant components,
or supplies a name plus another kind of information. One plant having two
labels remains possible. No such assignment is selected here.

A separate broad-leaf/root figure also lies below the final running-text
block without a fresh adjacent inscription. The large right-hand root drawing
and this bottom figure should not be collapsed merely to restore a regular
number of items per paragraph.

The middle-tier `okol` inscription and its prose recurrence remain a text
identity, not a picture-ownership edge. Its position among a hanging leaf,
neighbouring root crown and intervening blank space has no drawn pointer
that independently proves the named owner.

## Semantic consequence and stopped inference

The new pages support a concrete content-level contrast: botanical materials
can be presented with local inscriptions and collective prose (f100v), or
with dense uncaptioned drawings and broader prose blocks (f101r). Vessels
participate in both layouts but do not impose one invariant record boundary.
This is useful context for substance, component, quality, storage and recipe
rivals; it does not choose an English or German meaning for any word.

The originally proposed relocated-label discriminator has insufficient
visible capacity on f101r. Do not replace the missing local inscription with
the nearest prose word, a paragraph opener, or an inherited PAGE_HOST.
Similarly, a one-label-per-whole-plant model cannot be assumed on f88r in
order to make `ofaldo` a plant name. Narrow name, component/property and
category/reference readings remain competitors.

This is not a rerun of GDT169/351/352's exposed same-plant formal recurrence
tests. No new same-plant identity, scored relation packet, word meaning,
component gloss or translated clause is supplied. A future relation would
need independently fixed ownership and the full GDT388 evidence gates.
