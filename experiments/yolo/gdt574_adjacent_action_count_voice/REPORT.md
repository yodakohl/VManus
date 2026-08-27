# GDT574 — „zweimal“ gilt nur für wirkliche Nachbarn

Status:
`PASS_105_REPEAT_ACTION_EVENTS__43_RAW_ADJACENT_PAIRS__5_COUNT_CARDS__36_NEW_PLUS_7_RETAINED_TWICE__62_INTERRUPTED_ORDER_EXPLICIT__5122_EXACT_ROUNDTRIPS__ZERO_ROOT_CHANGE`

## Der entscheidende Schnitt

In der vollständigen Ausgabe wiederholt sich in 105 Karten mindestens eine
Handlungswurzel. Diese Zahl allein reicht nicht für `zweimal`. Nur 43 Karten
enthalten zwei identische Handlungsatome unmittelbar nebeneinander im
geschriebenen Rezept. Die anderen 62 sind unterbrochene Folgen wie CH–P–CH,
K–CH–K oder längere ABA/ABCA-Folgen. Sie bleiben vollständig ausgeschrieben,
weil eine Zählform ihre Reihenfolge zerstören würde.

```text
CH+CH+T  → Nimm den Pflanzenposten zweimal und stelle ihn ein.
CH+P+CH  → Nimm den Pflanzenposten, setze ihn ein und nimm ihn.
```

Die zweite Zeile ist absichtlich nicht verdichtet.

## Fünf kleine Karten decken alle 43 Paare

Die 43 echten Nachbarpaare bestehen aus 42 CH+CH-Fällen und einem OK+OK-Fall.
Sie benötigen nur fünf bereits vorbereitete Besitzerstimmen:

| Karte | Form | Fälle |
|---|---|---:|
| C01 | `Entnimm X zweimal` | 28 |
| C02 | `Nimm X zweimal` | 12 |
| C03 | `Nimm X zweimal auf` | 1 |
| C04 | `Nimm zweimal` | 1 |
| C05 | `Setze X im Arbeitsgang zweimal an` | 1 |

Sieben Zustandskarten trugen die GDT500-Stimme schon. GDT574 lässt sie
bytegleich stehen und ergänzt 36 bisher mechanisch doppelte Nichtzustandskarten:

```text
alt: Entnimm den Stationsposten, entnimm ihn und stelle ihn ein.
neu: Entnimm den Stationsposten zweimal und stelle ihn ein.

alt: Nimm denselben Positionswert auf, nimm ihn auf und wähle ihn.
neu: Nimm denselben Positionswert zweimal auf und wähle ihn.

alt: Setze den Pflanzenposten im Arbeitsgang an, setze ihn im Arbeitsgang an
     und nimm ihn.
neu: Setze den Pflanzenposten im Arbeitsgang zweimal an und nimm ihn.
```

Auch die eine objektlose Form bleibt wörtlich klein:

```text
Nimm, nimm und wähle. → Nimm zweimal und wähle.
```

## Kein Handlungsslot verschwindet

Jede der 43 Zählformen speichert die beiden rohen Atompositionen und eine
vollständige Zweischlitzexpansion. Das gilt auch für die sieben schon vorher
verdichteten Karten:

```text
Lesestimme: Entnimm denselben Stationsanteil zweimal und stelle ihn ein.
Expansion:  Entnimm denselben Stationsanteil, entnimm ihn und stelle ihn ein.
Atome:      CH | CH
```

Zusätzlich stellt der Quellkanal jede der 5.122 GDT573-Klauseln bytegenau
wieder her. Die 36 neuen Änderungen liegen in 33 Aussagen auf 17 Seiten. Alle
Zustandskarten bleiben unverändert. Nach dem Pass stehen genau 43 `zweimal` im
vollständigen Buch; alle 55 unabhängigen Prüfungen bestehen.

## Bedeutung für die Arbeitstheorie

Die alte Idee aus GDT500 trägt also über das ganze aktuelle Buch, aber nur mit
einer wichtigen Grenze: gezählt wird rohe Nachbarschaft, nicht bloß dasselbe
Verb irgendwo später. Dadurch bleibt die Aktionsreihenfolge weiterhin
vorhersagbar und sichtbar. `zweimal` ist Werkstattdeutsch für zwei vorhandene
Slots, kein vorgeschlagener Voynich-Zahlwert.

## Nächster Arbeitsweg

Als Nächstes wird der verbleibende Relations- und Modifikatorrest inventarisiert:
wörtlich doppelte Orts-, Grad- und Ausführungsphrasen versus bewusst
verschiedene Außen-/Innen-Scopepaare. Nur echte identische Nachbarn dürfen eine
Zähl- oder Koordinationsstimme erhalten; neue Seiten und Wurzelwerte bleiben
geschlossen.
