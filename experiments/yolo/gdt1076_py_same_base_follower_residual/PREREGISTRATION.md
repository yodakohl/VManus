# GDT1076 preregistration — do pX and yX retain a shared follower frame?

## Decision before reading follower content

GDT1075 found a pX>yX physical paragraph-opening tendency within section
and hand, but it cannot tell whether pX/yX share a content base or merely
look similar. GDT757/756 tested historical formula roles for `chor`, not a
same-base versus different-base follower comparison across the five fixed
bases. GDT920 tested a different p/f↔k/t own-paragraph bridge and failed;
its decision stands. Unknown: whether an identical X predicts local follower
content after conditioning on section and hand. A positive would prioritize
explicit positional normalization of pX/yX as a *working* grammar candidate;
a failure would bar that move from this evidence. Neither outcome identifies
any morpheme or word meaning.

Freeze GDT1075 `EVENTS.tsv` SHA256
`6c0b9fd422054a7ece186506d06aa3fa4558a77ac75eefa40424a5b4560a594d`.
Primary strata are its three informative ZL3b cells: B/hand2/`chedy`,
H/hand1/`cheol`, H/hand1/`chor`. IT2a/RF1b corresponding informative cells
are sensitivity only. No base, page, threshold or event may be added after
reading followers. All 214 fixed event rows stay in the output, including
forms with no usable follower. Query only GDT631's 179 admitted page selectors
through `query-tsv`, rejecting `f84*` in the selector before row content is
materialized. No new image, reserve or sealed page.

For each event, take source-group positions 2–5 on that same physical line.
Retain an exact complete follower only when its own left and right source
separators are `DEFINITE_SPACE`/`LINE_START` and `DEFINITE_SPACE`/`LINE_END`,
respectively; do not slide past an uncertain or missing position. Compare
sets of retained exact forms by Jaccard similarity; empty union scores zero.
Only cross-folio p-to-y event pairs count. For each p event in a named stratum,
compute mean similarity to all same-base y events in that section/hand and
to each other y-base separately, then average the latter base means equally.
The p event is eligible only if it has at least one cross-folio same-base y
and at least one cross-folio other-base y from two distinct physical folios.
Average the eligible p-event same-minus-other differences within each stratum.

The registered gate requires at least two eligible p events in each of the
three primary strata and a *strictly positive* difference in all three.
Any nonpositive stratum fails the common-base follower lead; insufficient
capacity is reported separately. IT/RF readers are alternate transcriptions,
not independent replications. Retain every event and all candidate-pair
counts and scores; no hand-picked examples or post hoc follower features.
This descriptive control is not a whole-search null, so do not claim
significance or translation. Preparation, implementation, validation and
publication budget: 35 wall minutes; stop expansion at the limit.
