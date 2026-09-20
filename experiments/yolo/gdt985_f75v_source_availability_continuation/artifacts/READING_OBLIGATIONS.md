# Complete raw context and conditional effect obligations

No function table is a translated word. All raw groups retained; separators/flags and source IDs remain in SOURCE_PACKET.json. A/B are hypothetical locations of the same hypothetical portion.

## IT2a

f75v.38: `tol | sheor | qokal | dar | olked | orol | kchey | otain | olchey | okar | sheky | dedy | kedy`

f75v.39: `qoqokeey | olkain | qol | sheedy | qokeor | sheedy | qokal | or | chey | qokar | ol | aiin`

f75v.40: `dlshedy | qokain | dal | qol | qol | ol | sheedy | cheey | dal | ol | sheey | qokain | olol`

f75v.41: `sal | shedy | qokain | shey | qoin | ol | shey | ol | shey | qoky | qol | cheey | chl | or | sheolo`

f75v.42: `ol | sheey | qolshey | qokain | okaiin | charor`

## RF1b

f75v.38: `tolsheor | qokal | dar | olked | orol | kchey | okain | olchey | okar | sheky | dedy | ke@152;y`

f75v.39: `qoqokeey | olkain | qol | sheedy | qokeor | {ch'}eedy | qokal | or | chey | qokar | ol | aiin`

f75v.40: `dlshe@152;y | qokain | dal | qol | qol | ol | shee@152;y | cheey | @152;@221;l | ol | sheey | qokain | olol`

f75v.41: `s@221;l | she@152;y | qokain | she@222; | qoin | ol | she@222; | ol | she@222; | qoky | qol | chee@222; | chl | @221;r | sheolo`

f75v.42: `ol | {ch'}ee@222; | qol{ch'}ey | qokain | okaiin | charor`

## ZL3b

f75v.38: `tolsheor | qokal | dar | olked | orol | kchey | okain | olchey | okar | sheky | dedy | kedy`

f75v.39: `qoqokeey | olkain | qol | sheedy | qokeor | sheedy | qokal | or | chey | qokar | ol | aiin`

f75v.40: `dlshedy | qokain | dal | qol | qol | ol | sheedy | cheey | dol | ol | sheey | qokain | olol`

f75v.41: `sal | shedy | qokain | shey | qoin | ol | shey | ol | shey | qoky | qol | cheey | chl | or | sheolo`

f75v.42: `o | l | sheey | qolshey | qokain | okaiin | charor`

## Every unknown whole and both entry states

Codes are defined below. Domains are marginals: arbitrary choices from different rows need not form one joint solution. Complete joint witnesses are in QUERIES.json.

| Whole | Enter from A | Enter from B |
|---|---|---|
| charor | 0, 1, 2, 3, 4, 5, 6, 7 | 0, 1, 2, 3, 4, 5, 6, 7 |
| cheey | 0, 1, 2, 3, 4, 5 | 0, 1, 2, 3, 4, 5 |
| chl | 1, 3, 4, 5, 7 | 1, 3, 4, 5, 7 |
| dal | 0, 1, 2, 3, 6 | 0, 1, 2, 3, 6 |
| dlshedy | 0, 1, 2, 3, 4, 5 | 0, 1, 3, 4, 6, 7 |
| okaiin | 0, 1, 2, 3, 4, 5, 6, 7 | 0, 1, 2, 3, 4, 5, 6, 7 |
| olol | 0, 1, 2, 3, 4, 5, 6, 7 | 0, 1, 2, 3, 4, 5, 6, 7 |
| qoin | 0, 1, 2, 3, 6 | 0, 1, 2, 3, 6 |
| qokain | 0, 1, 2, 3, 4, 5, 6, 7 | 0, 1, 2, 3, 4, 5, 6, 7 |
| qoky | 0, 1, 2, 3, 4, 5 | 0, 1, 2, 3, 4, 5 |
| qolshey | 0, 1, 2, 3, 4, 5, 6, 7 | 0, 1, 2, 3, 4, 5, 6, 7 |
| sal | 0, 1, 2, 3, 4, 5, 6, 7 | 0, 1, 2, 3, 4, 5, 6, 7 |
| shedy | 0, 1, 2, 3, 4, 5, 6, 7 | 0, 1, 2, 3, 4, 5, 6, 7 |
| sheey | 0, 1, 2, 3, 4, 5 | 0, 1, 2, 3, 4, 5 |
| sheolo | 0, 3, 6 | 0, 3, 6 |
| shey | 0, 1, 2 | 0, 1, 2 |

## Exact code definitions

- 0: A→A;B→A
- 1: A→A;B→B
- 2: A→A;B→undef
- 3: A→B;B→A
- 4: A→B;B→B
- 5: A→B;B→undef
- 6: A→undef;B→A
- 7: A→undef;B→B
- 8: A→undef;B→undef

## All inherited candidates

| Reading | Candidate | New status | sheolo tables | Final places |
|---|---|---|---|---|
| ZL3b | THEN_REPEAT | NO_CAPACITY | — | — |
| ZL3b | THEN_ONCE | NO_CAPACITY | — | — |
| ZL3b | NOT_REPEAT | NO_CAPACITY | — | — |
| ZL3b | NOT_ONCE | NO_CAPACITY | — | — |
| ZL3b | DESCRIPTION | NO_CAPACITY | — | — |
| IT2a | THEN_REPEAT | CONTINUATION_SAT | [0, 3, 6] | [0, 1] |
| IT2a | THEN_ONCE | CONTINUATION_SAT | [0, 3, 6] | [0, 1] |
| IT2a | NOT_REPEAT | INHERITED_CONTRADICTION | — | — |
| IT2a | NOT_ONCE | CONTINUATION_SAT | [0, 3, 6] | [0, 1] |
| IT2a | DESCRIPTION | DESCRIPTION_UNSCORED | — | — |
| RF1b | THEN_REPEAT | NO_CAPACITY | — | — |
| RF1b | THEN_ONCE | NO_CAPACITY | — | — |
| RF1b | NOT_REPEAT | NO_CAPACITY | — | — |
| RF1b | NOT_ONCE | NO_CAPACITY | — | — |
| RF1b | DESCRIPTION | NO_CAPACITY | — | — |
