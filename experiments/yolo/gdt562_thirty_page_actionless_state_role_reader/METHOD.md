# GDT562 method

## Question

Sind die706 GDT561-Zustandskarten ohne sichtbares Handlungsatom tatsächlich
unvollständig, oder führen `OT/OL/DY` eine bereits aktive Handlung und ein
bereits aktives Argument weiter? Kann jede Karte eine kurze ownerfreie
Mikrophrase und eine begrenzte praktische Rolle erhalten, ohne ein
unsichtbares Schriftatom oder einen neuen Stamm zu erfinden?

## Inputs

- `GDT416` —4.576 alte Kontextklauseln mit sichtbarer und geerbter Handlung
  und sichtbarem/geerbtem Argument;
- `GDT539` —546 aktuelle Kontextklauseln mit denselben Feldern plus exakten
  Quellereignis-IDs;
- `GDT561` —1.656 vollständig typisierte Zustandskarten und das aktive
  36-Atom-Wörterbuch.

## Method

1. Aus GDT561 werden genau die Karten mit null geschriebenen Handlungsatomen
   ausgewählt. Rezept, Oberfläche, Atomspur und Kontextzeile bleiben fest.
2. In jeder Aussage werden die letzte sichtbare Handlung und das letzte
   sichtbare Argument getrennt fortgeschrieben. Stimmt ein geerbter Root mit
   dem letzten sichtbaren Root überein, wird dessen Ereignis und Kartendistanz
   gespeichert. Liegt noch kein sichtbarer Root vor, bleibt der bereits in
   GDT416 gesetzte Besitzer-/Abschnittsdefault explizit als solcher markiert.
3. Die54 aktuellen aktionslosen Karten werden zusätzlich gegen GDT539s
   gespeicherte Quellereignis-IDs geprüft. GDT416 enthält diese IDs nicht; dort
   wird ihre Abwesenheit ausgewiesen und nicht fingiert.
4. Das effektive Argument kommt zuerst aus einem sichtbaren Kartenatom, sonst
   aus dem geerbten Argumentzustand, sonst bleibt der Slot offen.
5. Handlung und Argument ergeben sechs Vollständigkeitsrollen: vollständige
   geerbte Operation, objektlose geerbte Operation, Argumentbezug,
   formaler/relationaler Vorspann, abgestufter Abschluss und reine Fortsetzung.
6. Die sieben tatsächlich vorkommenden Zustandsfolgen erhalten kurze
   Operatorrahmen. In sie werden nur die bereits aktive Handlung, das
   effektive Argument und die sichtbaren GDT561-Modifikatoren eingesetzt.
7. Eine Atompositionszeile hält jeden geschriebenen Bestandteil separat fest.
   Kontextuell ergänzte Verben und Argumente werden nie als geschriebene Atome
   dargestellt.
8. Der Validator rekonstruiert Quellen, Distanzen, Rollen, Wurzeln,
   Zustandsfolgen und alle19 Nicht-Volloperationen unabhängig und prüft einen
   bytegleichen Neubau.

## Decision rule and claim ceiling

Der Leser gilt als geschlossen, wenn alle706 Karten eine explizite Herkunft
für Handlung und Argument, eine Vollständigkeitsrolle, eine nichtleere
Mikrophrase und eine vollständige Schriftatom-Ausrichtung besitzen. Karten ohne
effektive Handlung-plus-Argument-Paarung müssen als kleine benannte Restrollen
lesbar bleiben und dürfen keinen unbekannten Stamm voraussetzen.

Das Ergebnis ist eine kreative Ellipsen- und Zustandslesung bereits gesetzter
Arbeitswerte. Es bestätigt weder Klartext noch historische Sprache, Syntax,
Codebuch oder Gegenstand. Besitzerdefaults sind redaktioneller Kontext, keine
unsichtbaren Manuskriptzeichen. Keine Seite, Oberfläche, Segmentierung, Rezept,
Wurzelbedeutung oder Aussagegrenze ändert sich.
