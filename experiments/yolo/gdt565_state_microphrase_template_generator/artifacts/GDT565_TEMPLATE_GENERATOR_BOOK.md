# GDT565 – kleiner Satzgenerator für alle1.656 Zustandskarten

## Ergebnis

1.655 GDT563-Mikrophrasen werden bytegenau aus42 kleinen Renderer-Karten erzeugt.
Eine einzige alte Doppelargument-Zeile wird von „den Posten und den Posten“ zu „die beiden
Posten“ vereinheitlicht. Die607 verschiedenen Quellphrasen und716 Rezept-Kontext-Lesungen brauchen keine
gelernten Langsätze.

```text
 9 Zustandsrahmen
 9 Handlungsschablonen
 4 Argumentkarten
14 Modifikatorfragmente (für20 geschriebene Modifikatoratome)
 6 Verknüpfungsregeln
──
42 Renderer-Karten
```

## Äußerer Satzbau

Nur11 äußere Muster kombinieren Präfix, Basismodus, Modifikatorblock und Suffix.
Der Basismodus ist Handlungskette, Argumentbezug oder leere Basis. Darin arbeiten7
Handlungstopologien,4 Argumenttopologien und46 Modifikatortypfolgen.

## Wiederkehrende Struktur

Die genaue abstrakte Signatur besitzt168 Varianten. 82 davon wiederholen sich
und tragen1570/1656 Karten. Nur86 Karten stehen auf einer einmaligen Struktur.

| Struktur | Karten | Rezepte | Beispiel |
|---|---:|---:|---|
| `OL || ACTION_CHAIN || A || SINGLE || NONE` | 346 | 25 | Weiter: bearbeite den Anteil. |
| `DY || ACTION_CHAIN || A || SINGLE || GRADE` | 308 | 13 | Gib den Anteil; auf Grad II; abschließen. |
| `OT || ACTION_CHAIN || A || SINGLE || NONE` | 108 | 12 | Danach: bearbeite den Anteil. |
| `OL || ACTION_CHAIN || A || SINGLE || GRADE` | 76 | 17 | Weiter: gib den Posten; auf Grad I. |
| `OT+DY || ACTION_CHAIN || A || SINGLE || GRADE` | 63 | 3 | Danach: bearbeite den Posten; auf Grad I; abschließen. |
| `DY || ACTION_CHAIN || A || SINGLE || RELATION` | 57 | 10 | Bearbeite den Anteil; über die Verbindung; abschließen. |
| `OT || ACTION_CHAIN || A || SINGLE || GRADE` | 53 | 11 | Danach: bearbeite den Posten; auf Grad I. |
| `OT || ACTION_CHAIN || A || SINGLE || RELATION` | 48 | 7 | Danach: bearbeite den Anteil; zum Zielort. |
| `OL || ACTION_CHAIN || A || SINGLE || RELATION` | 35 | 14 | Weiter: bearbeite den Posten; über die Verbindung. |
| `OL+DY || ACTION_CHAIN || A || SINGLE || NONE` | 35 | 4 | Weiter: bearbeite den Posten; abschließen. |
| `OL || ACTION_CHAIN || A || SINGLE || LOCAL_OR_CLASS_SIGN` | 30 | 10 | Weiter: bearbeite den Posten; hier. |
| `OL || ACTION_CHAIN || A+A || SINGLE || NONE` | 30 | 15 | Weiter: gib den Posten und bearbeite den Posten. |

## Expansion statt Langwörterbuch

Neun Handlungswurzeln plus die Kettenregeln erzeugen133 beobachtete Handlungsketten.
Vierzehn Modifikatorfragmente plus die Reihenfolgeregel erzeugen80 beobachtete Modifikatorphrasen.
Die Zustandsrahmen setzen Weiter/Danach/Abschluss außen herum. Genau dort entsteht die
scheinbare Satzkomplexität; sie sitzt nicht in einer einzelnen Voynich-Sequenz.

## Arbeitsregel

1. GDT564 wählt offene Handlung und/oder Argument.
2. GDT565 setzt die Handlungsschablone und das Argument ein.
3. Geschriebene Modifikatoratome bleiben in ihrer Reihenfolge.
4. Der Zustandsrahmen fügt Präfix und Suffix an.

Jede Zeile behält Rezept, Atom-Ausrichtung, Generatorzustand und Quellphrase. Die eine
Normalisierung ändert nur deutsche Glätte, keine Root- oder Argumentstruktur. Keine neue
Seite, Wurzel oder gelernte Ganzsatzkarte wird verwendet.
