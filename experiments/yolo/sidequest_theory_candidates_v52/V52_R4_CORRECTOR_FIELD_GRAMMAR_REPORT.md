# V52 R4 — Korrektorischer Feldgrammatikentscheid

## Vorabentscheid

Die 135 Felder wurden vor dem Lesen der anderen V52-Berichte nach einer
einfachen Priorität klassifiziert. Das Ergebnis ist eine brauchbare
Kopiergrammatik, aber keine deutsche Satzgrammatik.

```text
FIELD := NONCLOSE* TERMINAL?
TERMINAL := CLOSE(CARD) | CLOSE_B3(CARD)
```

Alle 90 Abschlüsse stehen genau einmal am Feldende; 45 Felder bleiben offen.
Die ausgewählte V50/V51-Schicht benennt 145/381 Ereignisse. 236 Ereignisse und
52/135 ganze Felder bleiben ohne ausgewählten Wert.

## Vier Leseweisen

Mit der festen Priorität `SET/MARK > LINK/AN/ZUVOR > selected whole card >
opaque` ergeben sich:

```text
FORMAL_ASSIGNMENT       27 Felder
RELATION_OR_RESUME      24 Felder
STATE_VALUE_OR_ACTION   32 Felder
OPAQUE_PAYLOAD          52 Felder
```

Diese Klassen sind Werkstatt-Hilfen. Sie sagen weder Subjekt, Prädikat noch
Objekt. Insbesondere bilden `VERWENDEN? | MASS?` oder `WARM? | SPÜLEN?` noch
keinen Satz; die Relation zwischen den Karten bleibt unbekannt.

## Harte Korrekturen

1. `CLOSE` ist nicht das ausgesprochene Deutsch „und beende den Schritt“.
2. `<ARG_AIIN>` ist nicht die exakte Ganzkarte `AIIN=MASS?`; dasselbe gilt für
   jede RIGHT-Klasse.
3. Ein formal bekannter `SET`, `MARK` oder `LINK` regiert keine benachbarte
   opake Karte, sofern diese Bindung nicht bereits in derselben Formel steht.
4. Lange Herbal-Felder dürfen mehrere Quellphrasen enthalten; ein Feld und
   erst recht eine physische Zeile ist kein Satz.
5. Die vollständigen V49-Sätze bleiben kreative Gesamtlesungen, nicht
   kompositionell aus den 145 benannten Ereignissen abgeleitete Übersetzungen.

## Konsequenz

Für die nächsten Inhaltsrunden gilt eine zweistöckige Rücklesung:

```text
strikte Ebene: formale Kartenfolge mit UNKNOWN
kreative Ebene: vollständige historisch plausible Feld-/Artikelparaphrase
```

Die kreative Ebene darf vollständig bleiben. Sie darf aber keinen einzelnen
Host oder eine Ganzkarte rückwirkend beweisen. `f84` und `f84r` blieben
versiegelt.
