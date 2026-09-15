# Independent Digby 40 source review

Completed 2026-09-15 before target-image inspection or public registration of
GDT968. This review read the complete PAL transcription of chapters 1–2,
checked the next-chapter boundary, and natively viewed the cached source
facsimiles of f2v, f3r and f3v. It did not inspect any Voynich image or text.
It is a source review, not an independent diplomatic edition.

**Decision:** the METHOD's modest shared-pole predicate has direct source
support. Two distinct common endpoints, a member on each side of their
diameter, and a transverse diameter are defensible properties of the intended
chapter-2 framework. A minimum of two nonstraight interior members **in total**,
one on each side, is acceptable. Exact member counts, a complete degree grid,
and a fully reconstructed compass algorithm are not certified. The source's
compass-placement wording leaves a real unresolved difficulty; the topology
test must not silently convert that difficulty into a verified metric model.

## Source and chapter boundaries

The reviewed background is
[GEOMETRIC_SOURCE_SUPPLY.md](../../../../research_registry/work_batches/ten_hours_20260915/GEOMETRIC_SOURCE_SUPPLY.md),
SHA256 `f08da0e537e981a5553be5cead372adb04d7749243849b373c9ac126828b8125`.
Its source references, rather than its conclusions alone, were followed.

Chapter 1 starts on [f1v](https://ptolemaeus.badw.de/ms/236/338/1v), continues
through [f2r](https://ptolemaeus.badw.de/ms/236/338/2r), and ends on
[f2v](https://ptolemaeus.badw.de/ms/236/338/2v) immediately before the first
diagram and chapter-2 heading. The plate is round. A/I identify east/west,
E/O north/south, and V the centre. Two straight lines cross through V. Further
concentric circles define the interior frame; the two inward radial gaps are
related. The text prescribes 360 divisions. The accompanying drawing gives an
abbreviated labelled frame, without that complete division inventory or the
specified suspension hardware. These omissions are present in the source
witness; they are not permissions to omit arbitrary target geometry.

Chapter 2 begins below that figure on f2v, continues across
[f3r](https://ptolemaeus.badw.de/ms/236/338/3r), and ends on
[f3v](https://ptolemaeus.badw.de/ms/236/338/3v) with an explicit introduction
to its figure. [f4r](https://ptolemaeus.badw.de/ms/236/338/4r) begins chapter 3,
which introduces a different curve family. Those later curves must not be
silently imported into the chapter-2 stage. The source calls the chapter-2
members *almucantarat*; this review preserves its terminology without deriving
a modern astronomical identification from that name.

## What fixes the endpoints

On f3r the first member is drawn from the inner-circle intersection on the
southern diameter, through a ruler-generated point on the western transverse
radius, to the inner-circle intersection on the northern diameter. Subsequent
members use successive transverse points; the other half is then instructed.
The continuation on f3v explicitly says that the members of **both halves**
meet and join at these two points. It repeats the same two places when
describing coarser division steps. Thus the two poles are shared by the whole
intended family, not selected separately for each curve or each half.

The source endpoints lie on the **inner** circle. The outer plate edge and
its other rim circles are separate objects. In a target interpretation the
candidate carrier circle may therefore be an interior enclosing ring of the
whole composition; it need not be the outermost visible circumference. This
does not permit selecting an arbitrary local lens as the entire composition.

Native f3v inspection is consistent with bowed members on both sides of a
common vertical diameter and a transverse diameter. It also shows diagonal
ruler positions. The lower convergence is at the physical leaf edge, so the
image alone does not certify every final stroke endpoint with equal clarity.
The explicit text supplies the intended common-endpoint relation. I do not
certify an exact count of depicted members per half. A requirement of two or
three nonstraight members **per half** would need a stronger source audit than
this review supplies; the METHOD requires only one per half.

## Compass placement remains unresolved

The f3r transcription places one compass foot “inter V et A”; its apparatus
gives *intra* in the comparison witness F. This is not textual authority for
placing that foot anywhere along an unbounded eastward line. The instruction
is explicit for the first member; whether every detail of this position is
carried forward by the instructions to make later members similarly also
requires interpretation. No emendation is established here.

The background's modern coordinates need a distinction: its unit east/west
points are the diameter's intersections with the **inner circle**, whereas
the cardinal letters label sides of the mater. Write the inner-circle
intersections as E0=(0,1), O0=(0,-1), I0=(-1,0), A0=(1,0), with V=(0,0).
Let the plate's east endpoint be A=(a,0), where a is finite and greater than
1. Equating the literal plate label A with A0 suppresses this radius difference.
Consequently, a centre outside the inner unit circle alone is not a
contradiction of placement between V and A.

The mathematical issue nonetheless survives in a qualified form. For a
division point Q=(x,y) in the upper-left quadrant, the line O0Q meets the
transverse diameter at P=(p,0), with p=x/(1+y). Any circular member through
O0, P and E0 has centre (c,0) and radius r satisfying

```text
c = (p^2 - 1)/(2p),     r^2 = c^2 + 1,     -1 < p < 0.
```

This follows by subtracting the equal squared distances to P and E0. The
centre is within the finite segment VA only if

```text
p <= a - sqrt(a^2 + 1).
```

For example, at p=-1/2 the centre is c=3/4; at p=-1/10 it is c=99/20.
As p approaches zero, c diverges. At p=0 the three points are collinear and
no finite supporting circle exists. Equivalently, parameterizing Q as
(-cos(theta), sin(theta)) gives c=tan(theta). These are this review's analytic
consequences, not formulas transcribed from the manuscript.

There are two limits on claiming an outright textual contradiction. The
actual prescribed grids are discrete, and the chapter does not give a numeric
outer/inner radius ratio. Also, the bounded placement is stated at the first
member before the recursive instructions. Nevertheless, a modern full-grid
reconstruction cannot simply assert all bounded centres, all prescribed
crossing points, and a finite compass at the central point without resolving
these issues. The source figure's abbreviation does not resolve them.
The appropriate status is **metric construction unresolved**, not “the source
author permits outside centres” and not “the shared-pole statement is false.”

## Minimum usable consequence and its ceiling

For the particular complete representative framework hypothesized by GDT968,
the following necessary test is defensible:

1. A whole circular composition contains an enclosing carrier circle and two
   distinct pole points where a diameter meets that circle.
2. At least two nonstraight interior partition members, one in each half,
   run between those same poles. The boundary circle's own two semicircles
   cannot supply these interior members.
3. Every member assigned to this family shares those endpoints. Extra retained
   geometric boundaries must be described rather than erased to isolate a
   convenient pair. The crossed transverse diameter belongs to the source
   frame, although passing a still weaker pole-only screen cannot establish it.

This tests an explicitly complete representative with both halves, rather
than every possible abbreviation of the work. An uncertain carrier boundary,
clipped junction or ambiguous continuation stays unresolved. Mere concentric
rings, separate roundels, or radii meeting only at a central hub cannot meet
the predicate. A surviving pair establishes only a necessary configuration;
it does not establish complete stage identity when other boundaries remain
unexplained, and does not identify an astrolabe uniquely.

The figure does not license universal retention of construction helpers.
Conversely, ignoring complete pictorial icons, writing and pigment is the
prospective target-layer hypothesis, not a convention proved by Digby 40.
This review endorses no arbitrary deletion of geometric compartment lines.
No metric spacing, exact circularity, numerical scale, target text ownership,
word meaning or complete reading follows from passing the topology screen.

## Source-image receipt

The cached bytes actually opened for this review match these public sources.
Only the citation and hashes are recorded; source pixels are not republished.

| Source | SHA256 |
|---|---|
| [f2v](https://ptolemaeus.badw.de/repros/ms/Oxford%2C%20BL%2C%20Digby%2040%20%23236/%23338/002v.jpg) | `69f6bb58c03198299df4808262eb39afbb3b1ebd09b84b2ae2f666fe04ec11e2` |
| [f3r](https://ptolemaeus.badw.de/repros/ms/Oxford%2C%20BL%2C%20Digby%2040%20%23236/%23338/003r.jpg) | `e617de97f1b9dfce0f91b3da289ed3e7e64951f0a232463e737fda3510f4c54d` |
| [f3v](https://ptolemaeus.badw.de/repros/ms/Oxford%2C%20BL%2C%20Digby%2040%20%23236/%23338/003v.jpg) | `8164ff54d8cd35373860825c4b37c4e142a0e975f6123f2d1510d5c14b8f2715` |

No image editing, automated measurement, OCR, target viewing, target fitting,
helper-retention universality claim, or new data admission occurred.
