# Chaucer, *Treatise on the Astrolabe*: worked astronomical calculation source

**Status:** `SOURCE_ONLY_AUDITED` (2026-09-15). This is a source packet for a
possible historical content constraint. It uses no Voynich transcription,
image, reserve, target fit, or target-language meaning.

## Why this source was selected

Geoffrey Chaucer's *Treatise on the Astrolabe* is dated 1391 in its own
worked examples (and is therefore pre-1420 as a composition). Section II.25
contains a compact, explicit subtraction with both operands, operation, result,
and explanatory conditions. Section II.3 supplies a second complete worked
instrument chain with a date, measured altitude, settings, pointer result, time,
and ascendant. Together they are a concrete source precedent for a future
whole-reading hypothesis that would have to preserve arithmetic and repeated
operational terms.

This packet is deliberately narrower than `IDEA000126`: it identifies a
specific, reproducible worked example with stated values. It does not claim
that this source supplies a code, a target dictionary, or a binding to any
manuscript entry.

## Source and receipts

- Edition/transcription: W. W. Skeat, *A Treatise on the Astrolabe*,
  reproduced as a public-domain Middle English text at the eChaucer/Maine
  plain-text mirror: <https://web.archive.org/web/20090813233205/http://www.umm.maine.edu/faculty/necastro/chaucer/texts/astr/astr207.txt>.
  Retrieved text receipt (local retrieval artifact `astr207.txt`), SHA-256
  `8a6691961db5dea8ef02046e3bc2ff5b0acd138f6f3656d501799d9c654bafd1`.
  The `Astr 2 25 n` and `Astr 2 3 n` labels below are the transcription's
  chapter/line labels, not manuscript line numbers.
- Edition provenance: Writers Inspire/Oxford describes the text as Skeat's
  edition from the earliest manuscripts and links the Bodleian scan:
  <https://dev.writersinspire.it.ox.ac.uk/content/treatise-astrolabe-addressed-his-son-lowys>.
- Image witness: Bodleian Libraries, MS Rawl. D. 913, Digital Bodleian IIIF
  manifest:
  <https://iiif.bodleian.ox.ac.uk/iiif/manifest/e587f7ee-c786-4659-8486-c104d5633fe9.json>.
  Retrieved manifest receipt (local retrieval artifact `rawl_d913_manifest.json`), SHA-256
  `907c24e1c2eae2635adb08fee07e45ea389a5bcc62ef596707078ff2be0c7b72`.
  The selected image canvas is **fol. 29r**, canvas image identifier
  `05dba30c-a00c-40b8-b274-7d338af56119`; IIIF image URL:
  <https://iiif.bodleian.ox.ac.uk/iiif/image/05dba30c-a00c-40b8-b274-7d338af56119/full/1600,/0/default.jpg>.
  Local inspection receipt (not a publication asset; artifact `rawl029r.jpg`),
  SHA-256 `43f8b044ec4e9a65a61ef774a3e3c05cc74bac262d3718d3456accddcfcc6c75`.
  The catalogue/manifest records the image rights as © Bodleian Libraries,
  CC-BY-NC 4.0; no image is copied into this repository.
- A publicly accessible web presentation gives a modern English rendering
  beside Middle English for II.25 and discusses editorial variation:
  <https://medievalscience.org/treatise.html>. That rendering is used only as
  a cross-check; the exact excerpts below come from the Skeat text receipt.

The transcription is an edited witness, not a diplomatic line-by-line reading
of Rawlinson D.913. The manuscript image verifies the presence and placement of
the II.25 example on fol. 29r; the edition supplies the searchable exact text.

## Complete worked block A: latitude by equinoctial noon altitude

The complete instructional/example unit is `Astr 2 25 13` through `Astr 2 25
27`. Line 28 begins the optional invitation to verify the result and is not
needed to bind the calculation. The following is copied exactly from the
retrieved Skeat transcription, including its spelling and punctuation:

```text
Astr 2 25 13 Than if thou desire to knowe this latitude
Astr 2 25 14 of the regioun, tak the altitude of the sonne
Astr 2 25 15 in the myddel of the day, whan the sonne is
Astr 2 25 16 in the hevedes of Aries or of Libra; for than
Astr 2 25 17 moeveth the sonne in the lyne equinoxiall;
Astr 2 25 18 and abate the nombre of that same sonnes altitude
Astr 2 25 19 out of 90 degrees, and than is the
Astr 2 25 20 remenaunt of the nombre that leveth
Astr 2 25 21 the latitude of the regioun. As thus:
Astr 2 25 22 I suppose that the sonne is thilke day at
Astr 2 25 23 noon 38 degrees of height; abate than 38
Astr 2 25 24 degrees oute of 90; so leveth there 52; than is
Astr 2 25 25 52 degrees the latitude. I say not this but for
Astr 2 25 26 ensample; for wel I wot the latitude of Oxenford
Astr 2 25 27 is certeyn minutes lasse; thow might
```

Working source reading (not a target gloss): take a noon solar altitude when
the Sun is at the heads of Aries or Libra, subtract that altitude from 90°, and
read the remainder as the region's latitude. The numerical instance is:

| role | source value | operation/check |
|---|---:|---|
| complement/constant | 90° | fixed stated operand |
| observed solar altitude | 38° | fixed stated operand |
| intermediate operation | `90 − 38` | explicitly ordered as “abate 38 ... out of 90” |
| result | 52° | explicitly stated as the latitude |
| qualification | Oxford is “certeyn minutes lasse” | example is rounded/illustrative, not a precise Oxford measurement |

The arithmetic is independently checkable: `90 − 38 = 52`. The paragraph also
binds the operation to noon, Aries/Libra, and the equinoctial line; those clauses
must travel with the numbers in any future source model.

### Alternate branch in the same complete section

`Astr 2 25 29`–`Astr 2 25 46` gives a second worked subtraction when waiting
for Aries/Libra is inconvenient. The explicit values are approximately 56° noon
solar altitude and approximately 18° north declination, yielding 38° and odd
minutes after subtraction. The relevant exact lines are:

```text
Astr 2 25 39 of Aries and Libra. As thus: My sonne
Astr 2 25 40 is peraventure in the 10 degre of Leoun,
Astr 2 25 41 almost 56 degrees of height at non,
Astr 2 25 42 and his declinacioun is almost 18 degrees
Astr 2 25 43 northward fro the equinoxiall; abate than thilke
Astr 2 25 44 18 degrees of declinacioun out of the altitude
Astr 2 25 45 at non; than leveth there 38 degrees and odde
Astr 2 25 46 minutes. Lo there the heved of Aries or Libra
```

This branch is a linked corroborating example, not a replacement for block A:
the words `almost` and `odde minutes` retain numerical uncertainty. Its
working check is `approximately 56 − approximately 18 ≈ 38° plus odd minutes`.

## Complete worked block B: dated astrolabe observation

`Astr 2 3 15`–`Astr 2 3 37` is a complete example from the same edition. It
does not reduce to one arithmetic subtraction, but it gives all stated inputs,
instrument intermediates, and outputs in a single explanatory chain:

```text
Astr 2 3 15 Ensample as thus: The yeer of oure lord
Astr 2 3 16 1391, the 12 day of March, I wolde knowe the
Astr 2 3 17 tyde of the day. I tok the altitude of my sonne,
Astr 2 3 18 and fond that it was 25 degrees and 30 minutes
Astr 2 3 19 of height in the bordure on the bak
Astr 2 3 20 side. Tho turned I myn Astrelabye, and by
Astr 2 3 21 cause that it was before mydday, I turned
Astr 2 3 22 my riet and sette the degre of the sonne, that
Astr 2 3 23 is to seyn the firste degre of Aries, on the right
Astr 2 3 24 side of myn Astrelabye upon 25 degrees and
Astr 2 3 25 30 mynutes of height among myn almykanteras.
Astr 2 3 26 Tho leide I my label upon the degre of my
Astr 2 3 27 sonne, and fond the point of my label in the
Astr 2 3 28 bordure upon a capital lettre that is clepid
Astr 2 3 29 an X. Tho rekned I alle the capitale lettres
Astr 2 3 30 fro the lyne of mydnight unto this forseide
Astr 2 3 31 lettre X, and fond that it was 9 of the
Astr 2 3 32 clokke of the day. Tho loked I doun upon myn
Astr 2 3 33 est orizonte, and fond there the 20 degre of
Astr 2 3 34 Geminis ascendyng, which that I tok for myn
Astr 2 3 35 ascendent. And in this wise had I the experience
Astr 2 3 36 for evermo in which manere I shulde
Astr 2 3 37 knowe the tyde of the day and eke myn ascendent.
```

The chain is:

`1391-03-12` → measured altitude `25°30′` → first degree of Aries set on the
right side before midday → almicantaras setting at `25°30′` → label reaches
capital `X` → counting from midnight gives `9 o'clock` → east horizon gives
`20° Gemini` ascending. The date and readings are source values, not a claim
that this observation is historically accurate or a clinical/astronomical
measurement standard.

## Why this can support a distinct future hypothesis

The source supplies a small, complete content relation rather than an unknown
register alphabet: a stated constant and observation undergo an ordered
operation, producing a stated result inside explanatory prose. A future
whole-reading architecture could therefore predict jointly (i) repeated
operational terms, (ii) stable operand/result roles, and (iii) a coherent
paragraph relation between setup, operation, and conclusion. Block B adds a
different typed chain (date → instrument placement → pointer/time → ascendant)
whose order and output roles could be checked separately.

This is materially different from the existing decimal-register line. `GDT902`
reports `ALL_PANELS_EXCLUDED_BY_NECESSARY_CONSTRAINTS` for the Treviso 1478
complete multiplication register; its question concerns a shared prefix-free
decimal digit code and global word assignments. `IDEA000137` records the same
Treviso architecture as an inconclusive, scoped exclusion. The present source
has no decimal code, no cipher extraction, and no target fit. It is also
different from geomantic register proposals: the source's result is an
explicitly stated physical/geographical quantity linked by an explicit
operation.

## Limits and reversible uncertainties

- The Skeat text is an edited transcription. Rawlinson D.913 fol. 29r is the
  image witness for block A; no diplomatic image transcription is asserted.
- There is an edition/presentation discrepancy. The Skeat receipt says “38
  degrees” and “52”; the medievalscience presentation gives a variant with
  “38 degrees and 10 minutes” and a corresponding `51°50′` result. These are
  retained as separate witness/rendering variants and must not be silently
  merged. The present packet uses Skeat's exact text for its arithmetic check.
- Block A's 90° complement is explicit. Block B's astrolabe transformations
  rely on the instrument's geometry and tables; those unstated mechanics are
  not invented here. It is therefore an observational worked chain, not a
  claim of a fully self-contained numerical algorithm.
- The source is historical astronomical instruction. Its statements are not
  medical claims, and none of its English meanings may be imported as Voynich
  meanings. No source word is proposed as a target word.
- This packet does not select an experiment or reopen any closed route. A
  later test would need a predeclared representation of numerical roles and a
  falsifier that can distinguish this ordered source relation from generic
  sequential prose.

**Conclusion for the bounded search:** retain as a source-backed candidate
packet for a future content hypothesis; do not add a new idea card merely for
quota. The evidence is strongest for block A (`90 − 38 = 52`) and secondary for
the dated instrument chain in block B.
