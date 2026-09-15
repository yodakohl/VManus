# GDT962 — der feste BPE-Parser liefert keine vollständige Pflanzenlesung

**Alle176 vollständig geprüften Fälle widersprechen der registrierten Lesung.**
Das gilt sowohl für die fertigen98 Parser-Einheiten als auch für ihre tatsächlich
gebildeten inneren Baumknoten. In jedem Fall fehlt mindestens einem verlangten
Pflanzennamen bereits eine einzelne mögliche Einheit; auch die großzügige
Ergänzung unbekannter Textstücke reicht dafür nicht aus. Kein Pflanzenname und
keine neue Wortbedeutung werden übernommen.

Der [öffentliche Folgeversuch](PREREGISTRATION.md), Commit3ae9f3636, bindet
vor der neuen Zerlegung sämtliche5808 Pflanzennamen-Vorhersagen. GDT960/961,
ihre Quellen, Fenster und Ergebnisse bleiben unverändert. Frühere vollständige
Projektexposition ist offengelegt; der Test ist explorativ, keine blinde Bestätigung.

## Was konkret geprüft wurde

Die vollständige Quelle enthält43 Nennungen in15 Stern-Einträgen, mit32
Pflanzenidentitäten beziehungsweise34 getrennten Materialbezeichnungen. Alle22
bereits festgelegten vollständigen15-Absatz-Fenster wurden in beiden Richtungen,
unter beiden Quellenmodellen und beiden Parserdarstellungen geprüft. Keine
Pflanze, kein Absatz und kein Gegenbeleg wurde nach Ergebnis ausgewählt.

Die einzige neue Annahme lautet: ein Pflanzenname entspricht genau einer der
vorher festgelegten98 GDT605-Einheiten. Der bestehende Parser verbindet unsichere
kleine Zwischenräume und bildet seine64 unveränderten Merges. Daher kann eine
sichtbare Zeichenfolge je nach Umgebung eine selbständige Einheit sein oder in
einer größeren Einheit aufgehen. GDT961s kontextfreie Teilzeichenfolgen hatten
diese Möglichkeit nicht erschöpft. Der Parser wird hier als formale Hypothese
verwendet, ohne bestätigte Morpheme oder alte Wortglossen vorauszusetzen.

Im Rohdatenadapter bleiben unlesbare Gruppen und unaufgelöste äußere Grenzen
UNKNOWN. Im Unterschied zur früheren Ganzwortregel werden unsichere kleine
Zwischenräume nach GDT605 vor der Zerlegung verbunden. Die
[582 Änderungen der Lesbarkeit](artifacts/CHANGED_KNOWNNESS.tsv.gz) sind einzeln
dokumentiert; das sind keine rückwirkenden Transkriptionskorrekturen.

## Vorhersagen, Beobachtungen und Widersprüche

|Darstellung|vollständige Fälle|mit vollständig passender beobachteter Namensbelegung|mit noch möglicher oberer Belegung|widersprochen|
|---|---:|---:|---:|---:|
|FINAL_UNITS: fertige Parser-Einheiten|88|0|0|88|
|ALL_TREE_NODES: alle tatsächlich gebildeten Baumknoten|88|0|0|88|

Die [Kandidaten-/Ergebnistabelle](artifacts/CANDIDATE_TABLE.tsv) enthält jede
Fenster-, Quellen-, Richtungs- und Parserkombination samt fehlenden Namen und
maximaler Zahl verschieden zuweisbarer Einheiten. Selbst die großzügige obere
Zuordnung verfehlt eine vollständige Belegung um mindestens10 Namen bei
FINAL_UNITS und mindestens11 bei ALL_TREE_NODES.

[Alle5808 Einzelvorhersagen](artifacts/PREDICTIONS.tsv) nennen die konkreten
geforderten Absatzpositionen. Die [vollständigen Namensdomänen](artifacts/PLANT_DOMAINS.json.gz)
liefern dazu sämtliche beobachteten und oberhalb der Unsicherheit noch möglichen
Einheiten, vorhandene Positionen, fehlende Positionen und den Widerspruchsstatus.
[Alle4312 Einheitenmasken](artifacts/UNIT_MASKS.tsv.gz) enthalten auch Nullvorkommen;
[identische Vorhersagen](artifacts/IDENTICAL_UNIT_PREDICTIONS.json.gz) sind in3213
Klassen gruppiert. Unterschiede zwischen Einheiten derselben Klasse kann dieser
Inzidenztest nicht unterscheiden. Es wird kein bevorzugtes Lexikon ausgewählt.

Für **Mugwort** verlangt die Quelle in ursprünglicher Reihenfolge die Absätze
1,4,5,7,8,10,15 und kein Vorkommen in den übrigen acht Absätzen. Keine der98
Einheiten erfüllt diese beobachtete Maske. Von176 Mugwort-Fällen widersprechen172
bereits einzeln; vier bleiben nur durch unbekannte Stücke offen. Alle vier
betreffen dasselbe ZL3b-Fenster ab f106v.1–4 in ursprünglicher Reihenfolge:
`a` oder `lk` bei FINAL_UNITS, nur `lk` bei ALL_TREE_NODES. Ihre beobachteten
Vorkommen decken jeweils nur drei der sieben verlangten Positionen ab; vier
müssten ergänzt werden. Zudem fehlen im selben Fenster weitere vorgeschriebene
Namen, darunter Fumitary, Matry-silva, Milky Thistle, Penyroial, Plantain und
Succory. Auch diese vier Fälle ergeben somit keine vollständige Lesung.

Die alten `tc/tch`-Treffer werden nicht repariert: Sie sind keine Einheiten des
festen Inventars; ihr dokumentierter Rohtext-Gegenbeleg f113r.40 bleibt bestehen.
Die Zerlegung enthält keine außerhalb des98er-Inventars erzeugte Einheit.

## Aussagegrenze und Entscheidung

Dies widerlegt die konkrete Verbindung aus Quellenroster, vollständigen
Absatzfenstern und **einer festen Parser-Einheit je Pflanzenname**. Es widerlegt
weder alle zusammengesetzten Pflanzennamen noch BPE als formale Zerlegung oder
jede medizinische Lesung. Die98 Einheiten werden nicht als wahres Alphabet
bezeichnet. Keine nachträglichen Merges, Endungsregeln oder Pflanzenaliase folgen.
Die Behenian-Namensroute wird für diese Darstellung geschlossen.

Auch eine volle obere Zuordnung wäre nur eine notwendige Bedingung gewesen:
Unbekannte Stücke erhalten hier unbegrenzte abstrakte Einheitenkapazität, ohne
dass eine gemeinsame, tatsächlich parsebare Ergänzung behauptet wird. Die
vollständigen [Zuordnungen und Hall-Gegenbelege](artifacts/ALL_CASES.json.gz)
verhindern, dass einzeln passende Namen als gemeinsames Wörterbuch ausgegeben
werden. Alle176 Fälle scheitern schon an mindestens einer leeren Einzeldomäne.

Die Fenster umfassen acht Seitenansichten auf fünf bereits exponierten
physischen Blättern; Fenster und Transkriptionen sind voneinander abhängig.
Jeder Kandidat hat **null unabhängige Bestätigungsblätter**. Keine neue Seite,
Abbildung oder Reserve wurde geöffnet; f84/f84r bleiben versiegelt. Ohne eine
geeignete Gegenkontrolle der gesamten Suche gibt es keine Signifikanzbehauptung,
keinen neuen GDT388-Score und keine bestätigte Pflanzenbedeutung.

Der getrennte Validator rekonstruiert Quelle, Rohdaten-Zerlegung, Einheitenmasken,
alle Domänen und vollständigen Zuordnungsgrenzen unabhängig vom Runner.
Sein Ergebnis steht in [VALIDATION.json](artifacts/VALIDATION.json); es betrifft
Rechen- und Datenkorrektheit, keine unabhängige semantische Bestätigung.
