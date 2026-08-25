# Pass 746 — vier weitere Kopierachsen

Y bleibt aktiv. OL, AL, AIIN und OK wurden jeweils einzeln als zweite kopierbare Achse getestet. Eine Achse durfte nur dann erscheinen, wenn die erweiterte Bedeutungsmenge exakt eine vorhandene Deckkarte bildet.

## Ergebnis

- **OL:** 3 Kopien; 0 neue exakte Aussage, 0 Schaden.
- **OK:** 1 Kopie; 0 neue exakte Aussage, 0 Schaden.
- **AL:** 4 Kopien; 0 Gewinn, aber B2-S006 wird falsch.
- **AIIN:** 1 Kopie; 0 Gewinn, aber B1-S014 wird falsch.

Keine Achse wird uebernommen. OL und OK sind zwar unschaedlich, aber sie erklaeren keine einzige zusaetzliche Kartenfolge. AL und AIIN zeigen, warum atomweise Kopie zu grob ist: eine Adresse oder ein Sollmass darf nicht einfach in jede kompatible Karte hineingezogen werden.

## Konsequenz fuer das Schreibsystem

Y ist besonders, weil es der aktive Gegenstandslot einer Karte ist. OL, AL, AIIN und OK sind keine vergleichbaren frei propagierenden Register. Ihre Wiederholung muss als **ganze gelernte Kartenfolge oder gebundener Ausdruck** gelernt werden. Das historische Mischmodell wird dadurch praeziser:

1. Produktive kurze Bedeutungsfamilien.
2. Ein echter aktiver Y-Slot.
3. Keine allgemeinen Kopierregister fuer Weiter/Ziel/Mass/Ansetzen.
4. Wiederholungen dieser Werte gehoeren zum Kartenexemplar oder zu einer groesseren Formel.

## Nächster Hebel

Suche nun wiederkehrende Zwei- und Drei-Karten-Formeln in den32 Restfehlern. Statt Einzelwerte zu kopieren, lernt der Lehrling ganze Mini-Formeln wie `Adresse | Handlung+Y` oder `Sollmass | OK+Grad+Y`.
