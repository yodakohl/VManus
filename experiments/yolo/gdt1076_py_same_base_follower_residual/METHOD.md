# GDT1076 method

The [preregistration](PREREGISTRATION.md) freezes GDT1075's 214 events,
five complete-form bases and the three informative ZL3b section/hand strata
before follower content is read. The task is to determine whether pX and yX
with the same X have more similar immediate followers than pX and other-base
yY in the same section and hand. This is a test of a possible shared formal
base, not of a meaning.

`src/run.py` queries the 179 admitted page selectors through the guarded
`query-tsv`, rejecting `f84*` before fields are materialized. Positions 2–5
after each fixed head are inspected on the same source line. A retained
follower needs definite token boundaries and only literal lowercase letters;
internally uncertain bracketed/source alternatives are excluded, with no
replacement from later positions. Pairwise Jaccard scores use the sets of
retained complete forms, with empty union scored zero. Only cross-folio p-y
pairs count. The other-base comparison averages yY forms within each other
base, then averages those base scores equally. An eligible p needs same-base
y and other-base y on at least two distinct folios. The three registered
ZL3b strata each need at least two eligible p and strictly positive mean
same-minus-other similarity. IT2a/RF1b are sensitivity readings.

The executable writes the full 214-event follower roster, every eligible
p-event score, all 57 section/hand/base strata and a summary. Independent
`src/validate.py` replays source extraction, the pair arithmetic and the
registered capacity decision. Execute the manifest commands from repository
root. The report preserves the original diagnostic extraction correction:
the first local run admitted internally uncertain raw groups; it was fixed to
match the preregistered exact-form rule before validation and publication.
