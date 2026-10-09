# Next nonliteral content supply: compositional calculation and verification

**Status:** SOURCE_ONLY_RAW (2026-09-15). This is a source-grounded
hypothesis packet. No Voynich text, target body, image, reserve, decoder, or
target gloss was used.

## Predecessor review and scope

The refreshed route keeps 0 confirmed words and asks for a content consequence
beyond literal body-term incidence. I reviewed IDEA000126 (broad complete
astronomical calculation registers), IDEA000341 (directed formal carrier chain),
GDT902 (Treviso decimal-register exclusion), and GDT608 (formal compositional
roles). The new candidate below is narrower and differs in mechanism: it
requires a role-carrying arithmetic relation plus a verification/qualification
closure. It does not posit a decimal digit code or rename formal positions.

## Complete primary source

W. W. Skeat's public-domain transcription of Chaucer's *Treatise on the
Astrolabe*, section II.25, is at:
https://web.archive.org/web/20090813233205/http://www.umm.maine.edu/faculty/necastro/chaucer/texts/astr/astr207.txt

Retrieved text artifact SHA-256:
8a6691961db5dea8ef02046e3bc2ff5b0acd138f6f3656d501799d9c654bafd1

The complete instructional/example block is lines Astr 2 25 13–28, including
the continuation of the qualification and verification invitation:

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
    Astr 2 25 28 preve the same.

The primary consequence is fully checkable: constant 90 degrees minus observed
noon altitude 38 degrees gives result 52 degrees, under the stated
Aries/Libra/equinoctial condition. The final Oxford caveat and verification
invitation are part of the same complete record.

The Bodleian image witness is MS Rawl. D.913, fol. 29r, in the Digital Bodleian
IIIF manifest:
https://iiif.bodleian.ox.ac.uk/iiif/manifest/e587f7ee-c786-4659-8486-c104d5633fe9.json
The image was inspected only as source verification; no image is copied or
published.

## Candidate: role-carrying calculation with verification closure

A compact source-role grammar is:

    CALC = SETUP(condition) ; OPERATOR(ABATE_FROM) ;
           INPUT(observed) ; RESULT(complement) ;
           QUALIFICATION(caveat) ; VERIFY(invitation)

For II.25 the fields are:

- SETUP: noon, Sun at the heads of Aries or Libra, moving on the equinoctial
  line;
- OPERATOR: abate observed altitude out of 90 degrees;
- INPUT: 38 degrees;
- RESULT: 52 degrees latitude;
- QUALIFICATION: Oxford is certain minutes less;
- VERIFY: “thow might preve the same.”

This is a provisional compositional reading architecture. The field names
describe source roles and do not assign any target word or symbol.

## Coupled observable consequences

1. **Arithmetic and argument order must agree.** A candidate construction must
   encode a complement relation whose result is computed from two independently
   typed operands. Swapping the operands or treating 90 and 38 as a flat pair
   breaks 52. The same source section supplies a second check: approximately
   56 degrees noon altitude minus approximately 18 degrees north declination
   yields approximately 38 degrees and odd minutes (Astr 2 25 39–46).
2. **The result must feed a closure role.** The computed result is followed by a
   qualification about Oxford and then a verification invitation. A paragraph
   that only repeats values but lacks result-to-caveat/verification scope does
   not satisfy the source architecture.
3. **The setup conditions constrain the operation.** Noon and Aries/Libra are
   not interchangeable decorations: they license the equinoctial complement
   rule. A source-style construction must keep setup, operator, operands,
   result, and closure linked in one bounded record.

A secondary complete chain in Astr 2.3 (lines 15–37) supplies a different role
order—date 1391-03-12, measured altitude 25 degrees 30 minutes, first degree of
Aries and instrument setting, pointer X, 9 o'clock, and 20 degrees Gemini
ascending. It can test whether a role-carrying account generalizes from
arithmetic to instrument operations, but it is not required to establish the
II.25 subtraction.

## Distinguishing rival and failure

The nearest rival is a flat numerical/list reading: repeated numbers and
operation-like words occur locally, but no typed operand order, computed result,
or result-to-verification closure is required. IDEA000126 is broader and leaves
the historical register's digit/key representation open; this candidate fixes a
source relation without inventing a cipher.

The candidate can fail in several source-grounded ways: the target may not
expose typed operands or a result field; an apparent result may be a copied
number with no arithmetic dependency; qualification and verification may not
scope over the result; or source witness variation may prevent one frozen
calculation. The edition has a known presentation variant with 38 degrees and
10 minutes and 51 degrees 50 minutes, so the Skeat 38 -> 52 calculation and
that variant must remain separate. No target fit would resolve this source
variation.

## Decision

Retain as one raw, source-grounded nonliteral content proposal. It has a changed
semantic consequence—an ordered calculation relation with post-result
qualification/verification—rather than direct string equality or body-family
coincidence. It remains untested and does not reopen GDT902 or select a target
experiment.

