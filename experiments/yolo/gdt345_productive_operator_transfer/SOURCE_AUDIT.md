# GDT345 source and capacity audit

Date: 2026-08-19

Before scoring, the f84-free GDT327/GDT278 join contains 8,448 source groups on
91 physical folios and 180 pages. Forming only within-page adjacency yields
8,268 operator occurrences. The frozen formal state has six coordinates and
the descriptive full inventory has 138 source states, 137 target states, 707
registered operators, 2,186 source-state×operator combinations, and 1,633
atomic exact source tuples.

In preliminary count-only leave-one-folio capacity accounting, 7,966 events
have source state and full operator individually seen in training, and 1,004 of
those have an unseen source-state×operator combination. These counts establish
recombination capacity but are not scores.

Section event counts are H=3,116, S=2,573, B=1,809, T=388, P=253, C=129.
Register counts are HERBAL_A=2,415, STARS_RECIPE_B=2,407, OTHER_B=2,314,
HERBAL_B=701, OTHER_A=431. Hand counts are 2=2,692, 1=2,680, 3=2,672,
5=143, @=81. These are held-transfer strata, not semantic labels.

No f84 selector was retained or parsed during this capacity audit. No target
formal delta, held score, semantic comparator, token string, or PAGE_HOST
factor was inspected to choose the models, smoothing, gates, or null.
