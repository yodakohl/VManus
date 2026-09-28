# GDT1070 method

## Question

Is f9v `fochor`'s exact first-head uniqueness distinctive enough to help the
plant-name versus opaque-entry-address dispute?

## Inputs

GDT1059's already published `HEAD_CONTACTS.tsv`: one ZL3b first
paragraph-opening group on each of 89 admitted Herbal-A pages. GDT1069
established `fochor` as exact and definitely bounded in all three readings.
No new manuscript source was opened.

## Method

`src/run.py` counts exact complete `head_surface` values without edit-distance
clustering. It writes every type, multiplicity and page set, then repeats the
singleton summary after removing the already selected `kooiin` pair.
`src/validate.py` independently reconstructs all type rows and unordered
repeat pairs from the GDT1059 table. The fixed rules are in
`PREREGISTRATION.md`.

## Decision rule and claim ceiling

Singleton predominance means `fochor` uniqueness has no distinguishing
capacity; scarcity would make it noteworthy only as a formal observation.
The comparison cannot decide whether `fochor` names Viola, another plant,
or an entry. The data are post-selected and descriptive, with no p-value or
confirmed meaning.
