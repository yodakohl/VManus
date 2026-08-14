# KART001 A-65 source audit

Date: 2026-08-14

Status: `EXTERNAL_COMPARATOR_FROZEN_BEFORE_VOYNICH_SCORING`

## Manuscript and edition identity

The comparator is Tbilisi, Korneli Kekelidze Georgian National Centre of
Manuscripts, MS A-65. The *Comparative Oriental Manuscript Studies*
codicological handbook describes it as an illustrated Georgian translation of
an Arabic astrological treatise and dates it to 1188--1210. Abuladze and
Giunashvili independently describe A-65 as a twelfth-century Arabic-derived
astrological manuscript concerning planetary classification, lunar movement,
and seven heavenly bodies.

The primary text witness used here is Akaki Shanidze's 1975 edition,
*Eṭlta da šwdta mnatobtatws: Astrologiuri txzuleba XII sauḳunisa*, as
digitized by Ketevan Gočitašvili and published by the TITUS project. The
National Parliamentary Library of Georgia catalogue independently records the
1975 edition and its Old Georgian astronomical/astrological contents.

## Feature audit

### A65_F01: twelve zodiac signs — SUPPORTED

The electronic edition has twelve consecutively numbered sign chapters,
Aries through Pisces. This is scoring-eligible as cardinality 12 but has
near-zero geographical specificity.

### A65_F02: thirty degrees per sign — SUPPORTED

The sign chapters explicitly state thirty degrees for a sign; for example,
Aries at edition page 16, lines 6--7. The repeated three-part descriptions end
at degrees 10, 20, and 30. This is scoring-eligible as cardinality 30 and is a
generic zodiac convention.

### A65_F03: three ten-degree parts — SUPPORTED

Every sign chapter contains a three-part ruler scheme whose boundaries are 10,
20, and 30 degrees; Aries is at edition page 17, lines 30--34, with comparable
passages in the later chapters. This is scoring-eligible as `3 x 10`, but the
decan-like organization is common medieval astrology.

### A65_F04: seven luminaries/heavenly bodies — SUPPORTED

The tract title itself specifies seven luminaries. Abuladze and Giunashvili
also describe the doctrine of seven heavenly bodies. This is scoring-eligible
as cardinality 7 and has near-zero geographical specificity.

### A65_F05: ordered 28-night lunar sequence — SUPPORTED

The lunar section, edition pages 35--36, successively describes lunar nights 1
through 28 and their rising/setting times. The terminal entry is explicitly the
twenty-eighth night. This is a true ordered 28-member textual schedule, not a
claim about an A-65 lunar-mansion diagram.

### A65_F06: odd/even red-black convention — SUPPORTED

The edition note after the 28th night states that odd-numbered entries are
written in red and even-numbered entries in black. The supported fact is thus
an exact alternating two-state manuscript presentation on the ordered 28-night
schedule. No equivalence with Voynich LONG/SHORT is asserted. Broader medieval
prevalence of this exact convention remains unknown.

### A65_F07: sign-specific fortunate degrees — PARTIALLY SUPPORTED

The sign chapters explicitly enumerate degrees at which a person born is
described as fortunate. Before Voynich scoring, the following source-clear
sets are frozen:

| sign chapter | degrees | edition locator |
| --- | --- | --- |
| Aries | 19 | p.17, lines 45--46 |
| Taurus | 3, 14, 16, 27 | p.18, lines 39--41 |
| Gemini | 11 | p.20, lines 50--51 |
| Leo | 2, 3, 5, 12, 20 | p.23, lines 50--52 |
| Virgo | 3, 12, 20 | p.24, lines 51--52 |
| Libra | 3, 5, 21 | p.26, lines 45--47 |
| Scorpio | 7, 12, 20 | p.28, lines 47--48 |
| Sagittarius | 13, 20 | p.29, lines 49--50 |
| Aquarius | 7, 16, 17, 20 | p.32, lines 48--50 |
| Pisces | 12, 20 | p.34, lines 51--52 |

Cancer's line contains editorially abbreviated/uncertain numerals and is
excluded. Capricorn states no fortunate-degree set and is excluded. The ten
clear sets may enter KART001-T5. Exact rosters may be recension-specific, but
the genre of sign-specific astrological degrees is not uniquely Georgian.

### A65_F08: sign elements/directions/triplicities — SUPPORTED, PROFILE ONLY

The sign chapters explicitly classify signs by attributes including element,
day/night, masculine/feminine, hot/cold and wet/dry qualities, and a direction,
and they supply the three-part planetary rulers. These are system-profile facts
but generic medieval astrology. The accessed source does not define the
specific Sun/Moon diagonal pairing needed to score f67v2, so they do not
authorize KART001-T7.

### A65_F09: authorial circular/tabular topology in A-65 — UNSUPPORTED

The accessed scholarly sources establish that A-65 is illustrated, and the
TITUS edition links individual sign images. They do not document an authorial
circular or tabular topology homologous to a Voynich array. This feature is
excluded rather than inferred from the presence of illustrations.

### A65_F10: further independent numeric hierarchy — UNSUPPORTED

No additional independent repeated numeric hierarchy was securely documented
before target scoring. The 10/20/30 partitions and the 28-night color
alternation are already represented by F03 and F05--F06 and are not counted
again.

## Generic-medieval prevalence audit

The strongest compatibility features are not geographically diagnostic:

- twelve signs, thirty degrees per sign, three decans, and seven classical
  planets are standard premodern astrology;
- 28 lunar stations occur in Arabic astronomy and also in other Eurasian
  traditions;
- the local repository's source-audited Latin computus/cosmography witnesses
  already combine zodiac, Sun/Moon, 19-year, 28-sector, 29/30-sector, fourfold,
  and seven-state structures;
- A-65 is itself described by scholarship as adapted from Arabic, so a match to
  its generic architecture cannot distinguish Georgian transmission from its
  wider source tradition.

The exact odd-red/even-black 28-night presentation and exact fortunate-degree
rosters are the only frozen candidates with potentially greater specificity.
For the color convention, the audit does not provide a reliable comparative
prevalence denominator; its specificity must remain `UNKNOWN`, not high by
default.

## Source limitations

The audit uses a scholarly electronic edition and catalogued scholarship, not
an independently inspected complete A-65 facsimile. Edition color notes are
valid evidence about the manuscript as reported by the editor, but no new
claim about drawing topology is made. No modern unsourced summary contributes
to scoring.

## Frozen source URLs

- TITUS Old Georgian text and edition metadata:
  <https://titus.uni-frankfurt.de/texte/etcs/cauc/ageo/etlta/etltat.htm>
- National Parliamentary Library of Georgia record for Shanidze 1975:
  <https://dspace.nplg.gov.ge/handle/1234/334991>
- Gippert et al., *Comparative Oriental Manuscript Studies: An Introduction*,
  Georgian codicology section:
  <https://art.torvergata.it/retrieve/0761645f-8f2c-46d7-8ae2-6ba1e81cdd28/COMSt%20%28Codicology%29.pdf>
- Abuladze and Giunashvili, “Georgia and Iran: Historical-Cultural Context and
  Tendencies of Georgian Renaissance (According to Georgian Handwritten
  Heritage),” *Pro Georgia* 31 (2021):
  <https://dspace.nplg.gov.ge/bitstream/1234/529060/1/Pro_Georgia_2021_N31.pdf>
- Simonia et al., *Astronomical Manuscripts in Georgia* (Ilia State University
  Press, 2015): <https://eprints.iliauni.edu.ge/4669/>

The generic controls additionally reuse the already source-audited repository
artifact `experiments/semantic_assumptions/results/computus_circle_module_source_audit.md`.
