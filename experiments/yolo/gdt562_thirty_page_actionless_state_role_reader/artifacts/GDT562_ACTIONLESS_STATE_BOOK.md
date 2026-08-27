# GDT562 – die aktionslosen Karten sind fast alle Ellipsen

## Kernergebnis

Von706 Zustandskarten ohne sichtbares Handlungsatom besitzen693 bereits eine aktive Handlung im Kontext und692 ein sichtbares oder geerbtes Argument. 687 Karten –97,31% – ergeben damit eine vollständige Handlung-plus-Argument-Operation. Das fehlende Verb ist überwiegend Ellipse, kein unbekannter Wortstamm.

## Herkunft der ergänzten Slots

```text
aktive Handlung: 544 frühere sichtbare Handlung derselben Aussage
                 149 Besitzer-/Abschnittsdefault
                  13 keine aktive Handlung
Argument:        233 sichtbar in der Karte
                 355 früher sichtbar in derselben Aussage
                 104 Besitzer-/Abschnittsdefault
                  14 kein aktives Argument
```

Von den544 innerhalb derselben Aussage übernommenen Handlungen stehen376 unmittelbar davor;168 bleiben über zwei bis acht Karten aktiv. Bei Argumenten sind238/355 unmittelbar und117 über zwei bis fünf Karten verzögert. Die Auslassung ist damit nicht nur ein Nachbartrick, sondern ein kurzer Satzspeicher.

## Sechs Vollständigkeitsrollen

| Rolle | Karten | Arbeitslesung |
|---|---:|---|
| `FULL_INHERITED_OPERATION` | 687 | geerbte Handlung mit sichtbarem oder geerbtem Argument |
| `OBJECTLESS_INHERITED_OPERATION` | 6 | geerbte objektlose Handlung |
| `ARGUMENT_REFERENCE_INITIALIZER` | 5 | Argumentbezug ohne ausgesprochene Handlung |
| `FORMAL_RELATION_PROLOGUE` | 4 | formaler oder relationaler Vorspann |
| `STANDALONE_GRADED_CLOSE` | 3 | selbständiger abgestufter Abschluss |
| `PURE_CONTINUATION` | 1 | reine Fortsetzungssteuerung |

## Die19 Nicht-Volloperationen

Sie sind kein gemeinsamer Rest, sondern fünf kleine, vollständig lesbare Rollen: sechs objektlose geerbte Handlungen, fünf Argumentbezüge, vier formale/relative Vorspänne, drei selbständige abgestufte Abschlüsse und eine reine Fortsetzung. Keine verlangt einen neuen Stamm.

Beispiele:

```text
OL                    Weiter: halte den Posten.
OT+EE+Y               Danach: Bezug auf den Posten; auf Grad II.
OT+E+DY               Danach: auf Grad I; abschließen.
OT+E+O+D_ADDR+AR      Danach: auf Grad I; zur Ausführung; hier; vom Ausgang.
```

## Bedeutung für die Arbeitstheorie

Eine Karte muss kein sichtbares Verb tragen, um eine vollständige Anweisung zu sein. OT, OL und DY operieren auf einem bereits aktiven Handlungs- und Argumentzustand. Der Wortstamm liefert den neuen Wert; der Satzspeicher liefert ausgelassene Slots. Dies ist genau die erwartete Ökonomie eines knappen Werkstattcodebooks.

Die ownerfreie Mikrophrase ist eine praktische Arbeitszeile. Daneben bleiben die exakte Atomspur und die ältere Besitzer-Kontextzeile sichtbar. Kein kontextuell ergänztes Verb wird als neues geschriebenes Atom ausgegeben.
