# GDT112 — O/OT external-association preservation

## Question

When the same PAGE_HOST occurs under O and OT, does it preserve broad external
page association while the frame changes? This directly tests HPR2 hypothesis
2 after the exact-locus GDT059 panel had zero cross-frame capacity.

## Population and outcomes

Use unique `(page, PAGE_HOST, O-or-OT)` units from the complete f84r-free
GDT062 inventory and the existing human page-role matrix. Leave one physical
folio out. Use every page tag occurring on at least ten positive and ten
negative eligible pages; do not select a tag by the model result.

Because a page can contain many PAGE_HOSTs but only one external tag vector,
weight each target unit by the reciprocal of the number of eligible units on
its page. Thus each page contributes at most one total unit of loss.

## Models

The nuisance probability is estimated from training pages in the same HPR2
register. With shrinkage 4, compare exact PAGE_HOST-associated training pages
under:

1. the opposite O/OT frame (`CROSS_FRAME`);
2. the same frame (`SAME_FRAME`);
3. either frame (`ANY_FRAME`).

All training pages on the held physical folio are excluded. A model is scored
only when the exact PAGE_HOST has at least one qualifying training page;
coverage and weighted page mass are reported.

The primary prediction is positive held gain for `CROSS_FRAME`. Same-frame and
any-frame models diagnose whether a failure is specific to O/OT or to exact
PAGE_HOST page association generally.

## Limits

The page tags are broad archive categories, not semantic labels for individual
groups. Register control can absorb much of their variation, and host units on
one page remain correlated despite weighting. This is an exposed page-catalogue
sensitivity, not prospective confirmation.

f84r is filtered before the page/formal join and is not opened, parsed,
retained, queried, joined, scored, or targeted. No semantic role, gloss, word,
morpheme, POS, sound, language, plaintext, meaning, or translation is assigned.
