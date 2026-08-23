# Zwanzig Werkstattmakros über den Karten

Ein Makro ist eine häufige Abfolge mehrerer Handlungsklauseln. Es ist keine
Wortbedeutung und darf niemals auf eine einzelne sichtbare Form zurückprojiziert
werden. Der Lehrling benutzt es wie einen eingeübten Handgriff.

## Makros

### M01 — `CONTINUE>CONTINUE>CONTINUE`

Sprich: **denselben Gang über drei Teilposten fortführen**. Das Muster steht roh 6× in 2 Records; die längste-gültige Zerlegung verwendet es 3×.

### M02 — `SET>CONTINUE>SETTLE`

Sprich: **ansetzen, im selben Gang weiterführen und absetzen lassen**. Das Muster steht roh 2× in 2 Records; die längste-gültige Zerlegung verwendet es 1×.

### M03 — `TRANSFER>CONTINUE>LEAD_OUT`

Sprich: **umsetzen, weiterführen und am Ende abführen**. Das Muster steht roh 2× in 2 Records; die längste-gültige Zerlegung verwendet es 2×.

### M04 — `READY>DIVIDE`

Sprich: **bereitstellen und einen Teil abtrennen**. Das Muster steht roh 2× in 2 Records; die längste-gültige Zerlegung verwendet es 2×.

### M05 — `CONTINUE>SET`

Sprich: **weiterführen und den nächsten Posten ansetzen**. Das Muster steht roh 3× in 3 Records; die längste-gültige Zerlegung verwendet es 3×.

### M06 — `SET>CONTINUE`

Sprich: **ansetzen und im selben Gang weiterführen**. Das Muster steht roh 6× in 5 Records; die längste-gültige Zerlegung verwendet es 2×.

### M07 — `SET>PASSAGE`

Sprich: **ansetzen und durch den örtlichen Gang führen**. Das Muster steht roh 5× in 4 Records; die längste-gültige Zerlegung verwendet es 4×.

### M08 — `PASSAGE>SET`

Sprich: **durchleiten und am folgenden Posten ansetzen**. Das Muster steht roh 4× in 2 Records; die längste-gültige Zerlegung verwendet es 3×.

### M09 — `SET>READY`

Sprich: **ansetzen und bereitstellen**. Das Muster steht roh 5× in 3 Records; die längste-gültige Zerlegung verwendet es 4×.

### M10 — `SET>SETTLE`

Sprich: **ansetzen und absetzen lassen**. Das Muster steht roh 3× in 3 Records; die längste-gültige Zerlegung verwendet es 3×.

### M11 — `CONTINUE>SETTLE`

Sprich: **weiterführen und absetzen lassen**. Das Muster steht roh 4× in 2 Records; die längste-gültige Zerlegung verwendet es 1×.

### M12 — `READY>SET`

Sprich: **den bereitgestellten Posten ansetzen**. Das Muster steht roh 3× in 2 Records; die längste-gültige Zerlegung verwendet es 2×.

### M13 — `TRANSFER>SET`

Sprich: **umsetzen und neu ansetzen**. Das Muster steht roh 5× in 2 Records; die längste-gültige Zerlegung verwendet es 4×.

### M14 — `SET>TRANSFER`

Sprich: **ansetzen und umsetzen**. Das Muster steht roh 4× in 2 Records; die längste-gültige Zerlegung verwendet es 2×.

### M15 — `TRANSFER>CONTINUE`

Sprich: **umsetzen und weiterführen**. Das Muster steht roh 4× in 3 Records; die längste-gültige Zerlegung verwendet es 2×.

### M16 — `CONTINUE>LEAD_OUT`

Sprich: **weiterführen und abführen**. Das Muster steht roh 3× in 3 Records; die längste-gültige Zerlegung verwendet es 1×.

### M17 — `CONTINUE>TRANSFER`

Sprich: **weiterführen und umsetzen**. Das Muster steht roh 2× in 2 Records; die längste-gültige Zerlegung verwendet es 1×.

### M18 — `WARM>CONTINUE`

Sprich: **erwärmen und im selben Gang weiterführen**. Das Muster steht roh 2× in 2 Records; die längste-gültige Zerlegung verwendet es 2×.

### M19 — `SET>SET`

Sprich: **zwei aufeinanderfolgende Setzungen ausführen**. Das Muster steht roh 13× in 5 Records; die längste-gültige Zerlegung verwendet es 9×.

### M20 — `CONTINUE>CONTINUE`

Sprich: **denselben Gang über zwei Teilposten fortführen**. Das Muster steht roh 10× in 4 Records; die längste-gültige Zerlegung verwendet es 1×.

## Gesamtergebnis

Die 254 Klauseln der 116 Aussagen werden zu 196 Makro- oder Einzelbefehlen.
110 Klauseln liegen innerhalb eines Mehrklauselmakros; die übrigen bleiben
ehrliche Einzelhandlungen. Die ursprüngliche Klauselfolge ist aus jedem Programm
wortgleich rekonstruierbar.

## Der vollständig gearbeitete D2-Auftrag

- `H3-S001`: SINGLE_LEAD_OUT[H3-S001-U01] | SINGLE_SQUEEZE[H3-S001-U02] | SINGLE_HOLD[H3-S001-U03] | SINGLE_STRAIN_AGAIN[H3-S001-U04]
- `H3-S002`: SINGLE_OWNER_ACTION[H3-S002-U01]
- `H3-S003`: SINGLE_PROCESS[H3-S003-U01]
- `H3-S004`: M09[H3-S004-U01+H3-S004-U02]
- `B2-S001`: SINGLE_TRANSFER[B2-S001-U01]
- `B2-S002`: SINGLE_CONTINUE[B2-S002-U01]
- `B2-S003`: M19[B2-S003-U01+B2-S003-U02]
- `B2-S004`: SINGLE_SET[B2-S004-U01] | SINGLE_LEAD_OUT[B2-S004-U02] | SINGLE_LEAD_OUT[B2-S004-U03] | SINGLE_SET[B2-S004-U04] | SINGLE_LEAD_OUT[B2-S004-U05]
- `B2-S005`: SINGLE_SET[B2-S005-U01] | SINGLE_COLLECT[B2-S005-U02] | M08[B2-S005-U03+B2-S005-U04] | M09[B2-S005-U05+B2-S005-U06] | SINGLE_WARM[B2-S005-U07] | SINGLE_LEAD_OUT[B2-S005-U08]
- `B2-S006`: M07[B2-S006-U01+B2-S006-U02] | SINGLE_SET[B2-S006-U03]
- `B2-S007`: SINGLE_SETTLE[B2-S007-U01]
- `B2-S008`: M10[B2-S008-U01+B2-S008-U02]
- `B2-S009`: SINGLE_CONTINUE[B2-S009-U01]
- `B2-S010`: M19[B2-S010-U01+B2-S010-U02] | SINGLE_LEAD_OUT[B2-S010-U03]
- `B2-S011`: M19[B2-S011-U01+B2-S011-U02] | SINGLE_SET[B2-S011-U03]
- `B2-S012`: SINGLE_LEAD_OUT[B2-S012-U01] | M12[B2-S012-U02+B2-S012-U03] | SINGLE_LEAD_OUT[B2-S012-U04] | SINGLE_SET[B2-S012-U05]
- `B2-S013`: SINGLE_LEAD_OUT[B2-S013-U01]
- `B2-S014`: SINGLE_LEAD_OUT[B2-S014-U01]
- `B2-S015`: SINGLE_SET[B2-S015-U01]
- `B2-S016`: SINGLE_LEAD_OUT[B2-S016-U01] | SINGLE_DIVIDE[B2-S016-U02] | M19[B2-S016-U03+B2-S016-U04] | SINGLE_LEAD_IN[B2-S016-U05]
- `B2-S017`: SINGLE_HOLD[B2-S017-U01]
- `B2-S018`: SINGLE_SET[B2-S018-U01]
- `B2-S019`: SINGLE_WASH[B2-S019-U01]
- `B2-S020`: SINGLE_OWNER_ACTION[B2-S020-U01]
- `B2-S021`: SINGLE_SET[B2-S021-U01]
- `B2-S022`: SINGLE_LEAD_OUT[B2-S022-U01]
