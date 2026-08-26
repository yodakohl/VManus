# GDT449 — Methode

## Question

Welche GDT447-Nachbarn bleiben über sämtliche in GDT448 belegten realen
Quellkontexte lesbar, welche stoppen überall und welche hängen tatsächlich vom
Kontext ab?

## Inputs

- alle 61.878 GDT448-Kontextproben;
- GDT448s 4.275 Kontextsignaturen;
- GDT447s Mutationsmetadaten und exakte Identitätsroute.

## Method

Zuerst werden alle Proben je gerichteter Quell→Ziel-Kante zusammengefasst.
Danach werden gleiche Zielrezepte über sämtliche erreichbaren Quellkarten
vereinigt. Gleiche Ziel×Kontext-Proben würden dabei dedupliziert, damit viele
Nachbarn kein künstliches Mehrheitsgewicht erzeugen.

Vier Klassen bleiben getrennt:

1. in allen beobachteten Kontexten grün;
2. überall lesbar, aber mindestens einmal gelb;
3. Mischung aus lesbar und Stopp;
4. in allen beobachteten Kontexten Stopp.

Eine dritte Tabelle fasst nur die künstlichen Änderungsoperatoren zusammen;
sie erklärt Häufungen, ist aber keine angenommene Schreiberregel.

## Decision rule and claim ceiling

`ALL_GREEN` und `ALL_READABLE_WITH_AMBER` bedeuten nur „in sämtlichen bisher
beobachteten Quellkontexten“. Bei einem künftigen Auftreten muss der aktuelle
Kontext trotzdem erneut zertifiziert werden. Mischfälle verlangen explizit
Kontext; All-Stopp-Fälle bewahren den Zustand.

Robustheit darf weder Identität noch Auftreten, Oberfläche oder Bedeutung
befördern.
