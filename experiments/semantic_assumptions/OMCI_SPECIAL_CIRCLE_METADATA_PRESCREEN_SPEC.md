# OMCI special-circle metadata prescreen

## Purpose

Screen the complete public OMCI-INHA item catalogue for a previously unused,
human-described historical relation that could reopen one of three special-
circle acquisition routes:

- f57v: an integrated fourfold circle joining elements/seasons/humours or
  qualities;
- f68r2: a Sun–Moon–star ring with the relevant owned circular registers;
- f67v2: a circular wind scheme with personified faces and readable ownership.

This is a cheap metadata-worth screen, not image comparison or a paper review.
Use only public human-written title and catalogue-description fields.  Do not
open media, thumbnails, canvases, manuscripts, PDFs, OCR, automated visual
output, or decoder claims.

## Frozen source and projection

Fetch exactly:

`https://omci.inha.fr/api/items?per_page=1000&sort_by=id&sort_order=asc&page=1`

Require an HTTP 200 response at the same URL, no `Location`, 917 unique item
IDs in ascending order, and exactly 243 items whose resource-class ID is 365
(OMCI illustrations).  For each illustration, retain only:

- numeric item ID and title;
- literal `dcterms:description`, `dcterms:isPartOf`, `dcterms:provenance`,
  `bibo:locator`, `bibo:number`, and `dcterms:date` values.

Exclude every media, thumbnail, linked motif/theme label, image URL, and other
field before screening.  Canonicalize the 243-row projection as sorted-key,
UTF-8 JSON with one final LF.

## Fixed text filters

Normalize HTML entities/tags, whitespace, and case within title plus literal
description only.  Apply these conjunctions:

1. `F57_FOURFOLD_CIRCLE`: one of `quatre|four`; one of
   `élément|element|saison|season|humeur|humor|qualit|quality`; and one of
   `cercle|circle|roue|wheel|rosace|diagram`.
2. `F68_SUN_MOON_STAR_RING`: one of `soleil|sun`; one of `lune|moon`; one of
   `étoil|star|astre`; and one of
   `cercle|circle|anneau|ring|médaillon|medallion`.
3. `F67_WIND_FACE_CIRCLE`: one of `vent|wind`; one of
   `visage|face|tête|head|personn`; and one of
   `cercle|circle|roue|wheel|rose|diagram`.

These are broad metadata filters, not exhaustive visual predicates.  A zero is
a catalogue-description no-find, not proof that no matching image exists.

## Worth decision

Escalate only a newly surfaced record whose human description states the
target relation with owned readable slots.  A record already consumed by the
active source-family analysis, or a broad relation without target ownership,
does not justify opening its image or bibliography again.

## Ceiling

The result may close OMCI as a current metadata acquisition source and retain
broad comparanda.  It cannot assign any object, direction, season, humour,
quality, element, wind, label, word, sound, language, cipher operation,
plaintext, meaning, or translation to the Voynich manuscript.
