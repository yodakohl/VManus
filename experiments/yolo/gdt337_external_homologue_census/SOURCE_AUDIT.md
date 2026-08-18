# GDT337 external source audit

Date: 2026-08-18

Status: `PROVENANCE_CLEAN_GEOMETRY_TOPOLOGY_CENSUS`

## Scope and evidential classes

The audit retains exact catalogue or scholarly statements about cardinality,
layout, readable labels, order, and ownership. It does not infer a diagram's
content from visual resemblance and does not use modern unsourced image lists.
No external manuscript image was required for the new audit. Earlier local
source audits that used direct human inspection retain their published access
statements; their conclusions are not silently upgraded.

## Strong exact external donors

### British Library Add MS 25435 — ordered 28 wheel

The [official British Library catalogue](https://searcharchives.bl.uk/catalog/032-002029758)
dates the German manuscript to 1345–1355. It documents:

- 28 lunar-month records associated with 28 named Old Testament prophets;
- a wheel on the inside upper cover numbered I–XXVIII;
- a movable central figure whose hand points to the wheel;
- one illustrated, named prophet record for every position.

This is the cleanest external 28-slot donor now in the repository: its values,
order, ownership, and pointing mechanism are explicit. It does **not** repair
the Voynich target. f69v has no author-visible origin/direction and only one
physical folio; f68r1's 28 noncentral stars have no authorial sequence and also
occupy one folio.

### Walters W.73 — readable ordered diagram family

The [Digital Walters manuscript description](https://t.thedigitalwalters.org/Data/WaltersManuscripts/html/W73/description.html)
and [official object page for W.73.2V](https://art.thewalters.org/object/W.73.2V/)
document several unusually explicit external comparators:

- f.1v: twelve named winds in owned spokes, Greek and Latin names, four
  cardinal directions, East at top, and a catalogue-given circular order;
- f.2v: Earth, seven named bodies in concentric rings, and twelve zodiac names
  in the frame;
- f.6v: lunar days I–XXX in an ordered ring and twelve zodiac names beginning
  with Aries;
- f.7v: named fourfold element/season/quality/humour correspondences.

These diagrams prove that medieval scientific compilations can supply exactly
the order and ownership devices GDT337 requires. None is an exact transferable
Voynich endpoint: the potentially similar target structures are confined to
one folio, lack a common phase, have different ring topology, or belong to
already exposed and withdrawn semantic routes.

### Ordered 29/30 rota tradition

The [Digital Bodleian record for St John's College MS 17](https://digital.bodleian.ox.ac.uk/objects/cca30c56-0751-4f52-a952-bbffcb7b64e9/)
and the repository's Teresi-based computus audit retain numbered 29/30-sector
tidal rotae as real historical analogues. The f68r1 target is instead a field of
29 labelled stars, one central, with no authorial wedge order; the zodiac target
has 30 positions but no common phase across seven panel topologies.

## Ordered external systems without matching visual topology

The A-65 scholarly edition remains a strong ordered-system comparator: 12
signs, 30 degrees per sign, three ten-degree parts, seven luminaries, and a
1–28 lunar-night schedule with odd/even rubrication. The accessed source does
not document a homologous A-65 circular diagram. KART001 already found the
system profile no more specific than generic medieval astrology and directly
falsified the lag-14 table-transfer prediction.

The *Libro de astromagia* / *Astrolabium planum* paranatellonta tradition gives
ordered degree-specific records. The [Vatican digitization](http://digi.vatlib.it/view/MSS_Reg.lat.1283.pt.A)
and the prior [public-source audit](../../semantic_assumptions/results/zodiac_paranatellonta_public_source_audit.md)
support the external 1–30 order, but do not determine a Voynich degree-1 slot,
direction, or continuation between its unequal rings.

The *Liber astrologiae* / Fendulus tradition supplies a sign-plus-three-decan
hierarchy. The official [British Library Sloane MS 3983
catalogue](https://searcharchives.bl.uk/catalog/040-002116376) records the
zodiac/paranatellonta picture cycle, while the official [Morgan M.785
catalogue](https://www.themorgan.org/collection/astrological-treatises/144038)
states that each sign is followed by three decan folios. It is a 3×10 system
comparator, not a 30-slot circular donor.

## Source-family comparators that fail one-to-one ownership

- [NYPL MA 069](https://digitalcollections.nypl.org/items/1fbe4680-28ab-013b-27fe-0242ac110002)
  combines zodiac, number/letter, fourfold, Sun–Moon and nineteen-year modules,
  strengthening a computus/cosmography family prior but matching no complete
  target topology.
- [Wellcome MS.202](https://wellcomecollection.org/works/aeb73uat) is a
  chronologically close 1443 computistical miscellany with coloured fourfold
  and Sun–Moon diagrams, again without a one-to-one target map.
- Human-curated FDTW metadata for Oxford MS. Arab. c. 90 describes a layered
  Earth/seven-climate, 28-section, 36-constellation and 12-zodiac diagram. Its
  28-slot start/order and individual ownership are not documented strongly
  enough, and a proposed Voynich match would combine separate f67 and f68
  diagrams.
- Gotha Chart. A 472 has a seven-diagram run, but the official catalogue shows
  that the seven titles are not seven individual luminaries.
- The Landsberg ca.1494 *Sphaera* frontispiece supplies a late exact
  seven-occupied-of-twelve pattern in a human audit of the reproduced image.
  Richard L. Kremer's open-access study, [“Printing Sacrobosco in Leipzig,
  1488–ca. 1521”](https://doi.org/10.1007/978-3-030-86600-6_12), identifies
  the design as newly Christianized and explicitly flags its misplaced zodiac
  signs; the [BSB digitization](https://nbn-resolving.org/urn:nbn:de:bvb:12-bsb00029417-1)
  binds the printed witness. No earlier exact witness is established here, and
  the one-folio f67r2 target cannot validate it.

## Census conclusion

The external-source problem is partly solved: exact readable donors exist.
The remaining failure is on the target side. No current Voynich candidate has
all of:

1. a text-blind start/direction and slot correspondence;
2. singular owned slots; and
3. disjoint-folio discovery and holdout capacity.

The complete machine-readable source statements and statuses are frozen in
`artifacts/gdt337_external_source_manifest.tsv`.
