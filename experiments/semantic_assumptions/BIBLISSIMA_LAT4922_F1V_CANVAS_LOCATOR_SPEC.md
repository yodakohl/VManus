# Biblissima Latin 4922 f1v canvas locator

## Purpose

Resolve the positive Biblissima metadata lead to an exact Gallica canvas for
qualified human inspection without opening any image pixels.  Bind the prior
worth result, the official Gallica IIIF Presentation manifest, and the official
Gallica Pagination service.

## Gate

An exact canvas locator requires a human-authored or repository-authored
logical label, range, legend, or pagination entry that maps physical `f.1v` to
one canvas.  Sequential scan order alone is not sufficient, because covers,
flyleaves, substitutions, and omitted leaves can shift the offset.

Do not request any canvas image resource, thumbnail, image-service info, OCR,
PDF, or manuscript pixels.  If the APIs expose only `NP`, stop and require
manual navigation in the official Gallica viewer.  Never guess an offset.

## Ceiling

This locator may produce an exact human-review URL or a documented navigation
stop.  It cannot establish the diagram's visual topology and licenses no
Voynich age, humour, season, element, person, slot, label, word, sound,
language, cipher, plaintext, meaning, or translation.
