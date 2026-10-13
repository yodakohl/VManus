# GDT1364 — Fixed raw-character sensitivity of nucleus-carrier bounds

## Decision and scope

Unknown: does1042's <=8carrier exclusion persist when the same raw transcription
is split into individual characters, allowing codes to start inside old ch/sh/
bench tokens?1355and1363do not answer this changed representation. Their original
22unit results remain unchanged. Smallest test: fixed RAW_CHAR refinement only,
exact hitting size and sameK3/5/7/8exception optima, independent bitset validation.
Budget25minutes inclusive preparation, validation/publication; no decoder/images.

If rawtau<=8, the zero-exception exclusion is not robust across these two
representations. If rawtau>8, retain only this TWOrepresentation sensitivity,
not every possible glyph/pen-stroke boundary. Report how Kexceptioncosts change.
Neither outcome identifies actual physical atoms, phonemes or a source language.

## Data and frozen representation

Use unchanged1233GROUPS.json.gz: same whole occurrences, exact reader and FULL/
GE2eligibility as1355/1363. GE2means wholeform on≥2physical leaves; not a repair or
holdout. First validate raw text re-parses to old working units, then set the
new units to list(ivtff_group_raw), without normalization or dropped characters.
Alphabet is sorted distinct raw characters in each FULL reader, retained forGE2.
No expected alphabet size is selected as a fit condition. No mixed rawTSV,
newimage,websource,f84/f84r/f116v/f1rbody,reserve or semantic relation is read.

The general representative proof now requires complete nonempty carrier strings
aligned to these RAW_CHAR boundaries. It does not cover codes cutting inside
these characters. A hit is still not a nucleus and optima are not vowel values.
Changing a transcription representation supplies no historical source evidence.

## Exact output

For each reader/panel findminimum numbertau of representatives hitting allwords,
and lowest numeric mask at thatsize. Compute K3/5/7/8minimum missed group-occurrences
and separately wordtypes, samefields and tie rule as1363. Keep both counts at
bothwitnesses, all missedforms/frequencies/first IDs/physicalleafsets. No joint
optimum is manufactured. Counts remain lowerbounds, not sufficient phoneticfits.

Compare only to old1355tau=22-max_null_TYPES and1363exceptionminima for IDENTICAL
wordpanels. Refinement cannot increase either: select one rawcharacter from each
oldrepresentativeunit, giving≤Knew representatives that preserve everyoldhit.
This necessary monotonicity is a sanity check, not a proof of linguistic status.

Primary adapts1363subset-zeta code with a changed support projection. Independent
validator adapts its own1363bitset enumeration, enumerates allrawsubsets and
checks tau and all48objectivewitnesses. Control: atomic bc andbd words require
two oldtypes tohitboth, but splitting them yields commonb andtau1. Originalsmall
weighted support fixtures retained. Hashlock source/protocol/oldresults before
new native counting. No post-result alternative splits or new alphabetical fit.
