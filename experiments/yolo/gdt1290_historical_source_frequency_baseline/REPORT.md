# GDT1290: none of three fixed source profiles meets both pooled bands

**NO_PRIMARY_REFERENCE_COMPATIBILITY.** No selected historical source sample
meets both existing pooled frequency bands under the frozen one-form-per-group
comparison. The reasons differ: Latin has an admissible type count but excessive
top-ten concentration; Old Italian and Greek have TOO MANYtypes, not too few.
This does not identify or exclude a Voynich source language or a general cipher.

| Fixed primary source projection | Groups | Distinct forms | Type share | Top10count | Top10share |
|---|---:|---:|---:|---:|---:|
| Old Italian |8000|3210|40.125%|1557|19.4625%|
| Latin PROIEL |8000|2357|29.4625%|1750|21.875%|
| Ancient Greek PROIEL |8000|3072|38.400%|1413|17.6625%|

The unchanged acceptable type intervals are2051–2851IT,2130–2930RF,2100–2900ZL;
top10intervals are665–1465IT,608–1408RF,630–1430ZL. They are the old engineering
bands, not significance thresholds or universally necessary manuscript properties.
Latin's type count passes allthree; its concentration does not. Greek's concentration
passesIT/ZL but exceedsRF by5counts; its type count fails every reader band anyway.
All individual checks remain in RESULT. Readers are alternate readings, not replicas.

## A useful consequence despite the joint nonconfirmation
These data do not support a universal response of inventing more spellings to raise
word diversity. Latin supplies an explicit, unchanged source projection whose type
count already lies inside the pooled range; the other two primary projections even
exceed it. The four CoReMA source failures remain exactly as registered. Neither a
new encoder nor a better alphabet table has been selected here. Frequency compatibility
alone would not establish ordinary substitution, but frequency noncompatibility on
one source cannot be exported to all historical texts.

GDT1225already showed that the pooled bands reject a sufficiently large ACTUALnative
hand category under every prescribed sample. This check therefore evaluates only
the old pooled reference profile. It does not reimpose that profile as a universal
hard requirement for every author, section, text or book, and it does not rehabilitate
any previous failed writer on a favorable stratum or altered tolerance.

## Exactly which historical text was counted
Only the three frozen r2.18TRAINfiles named in the old003source provenance were
retrieved; every original byte count and SHA256matched. No mixed Voynich/control
payload archive was opened. The sampled primary intervals are:
- Old Italian: OldItalian_Dante_Inferno-1 through-338.
- Latin: sent_id12667 through13791; source metadata Matthew1 through18.
- Greek: sent_id64362 through64947; metadata Histories Book1,chapters1 through83.
The final sentence may be partial at the8000group cutoff. Stored train sequences
can omit material allocated to dev/test; these are not complete uninterrupted books.

The Old Italian resource contains Dante's Comedy in an edited modern transcription;
this is a corpus control, not a Voynich-poetry hypothesis. Its documentation specifies
its edition and train/dev/test subdivision. [Official source README](https://github.com/UniversalDependencies/UD_Italian-Old/blob/r2.18/README.md).
Latin PROIEL includes Vulgate and other Latin texts; Greek PROIEL includes New
Testament and Herodotus material. The selected prefixes above are determined by
file order, not a later choice of subject. [Latin source README](https://github.com/UniversalDependencies/UD_Latin-PROIEL/blob/r2.18/README.md), [Greek source README](https://github.com/UniversalDependencies/UD_Ancient_Greek-PROIEL/blob/r2.18/README.md).
These different genres, authors, orthographies and editions are not interchangeable;
no causal effect of language or genre is isolated by comparing their three profiles.

## Token definition matters, without changing the decision
Primary groups retain case, accents, punctuation and single-character strings in
sentence '# text'comments, split only at Unicode whitespace. Every sampled sentence
has that comment, so the predeclared fallback was never used. Their FORM/MISC surface
reconstructions agree exactly. This validates the selected edited source representation,
not original medieval spacing or equality with authorial Voynich words.

The separately predeclared exact integer-ID FORM sensitivity gives:

| Projection | Distinct forms /8000 | Top10count |
|---|---:|---:|
| Old Italian FORM |2168|2143|
| Latin FORM |2357|1750|
| Greek FORM |3072|1413|

Old Italian's syntactic token stream expands multiword tokens and separates punctuation.
Its first8000tokens end at sentence264 rather than primary338. Thus the contrast also
changes the covered source span: do not attribute the full numerical difference to
punctuation alone. Latin/Greek samples are identical under both definitions here.
No secondary joint pass occurs, and no preferred token definition was selected after
results. CoNLL-U distinguishes surface ranges, integer words and nonwritten empty
nodes. [Official format specification](https://universaldependencies.org/format.html).
The old003projection additionally removed single-letter words, casefolded and used
hash samples; its12kfingerprints are not substituted for either present projection.

## Validation, source licenses and decision
The independent validator imports no runner. It reconstructs all48000sample units
across both projections, original sentence/row receipts, frequency tables, source
hashes and every band decision. PASS. The small format fixtures retain multiword
surface forms, empty-node omission, case, punctuation spacing, text priority and
no-comment fallback. This is extraction/accounting verification, not independent
historical or semantic evidence. No source failures or insufficient samples occurred.

Raw files are stored losslessly compressed with receipts and source READMEs. The
Old Italian README specifies CC BY-SA4.0; both PROIELREADMEs specify CC BY-NC-SA3.0.
Source attribution is retained. No source text is represented as our original work.

Close this fixed three-source comparison. No fourth source, casefolding, accent
removal, punctuation regrouping, new band or encoding scheme is selected to obtain
a pass. Existing001/003/605/1202decisions remain unchanged. This is a reference-profile
finding, not a native reading, language verdict, translated word or full writer fit.
No new manuscript source/image/reserve, f84/f84r/f116v, outside contact or public push.
The requested ten-hour research interval continues.
