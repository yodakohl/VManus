# GDT639 method

## Question

Welche strikten V15-Ein-Loch-Oberflächen wurden vom automatischen Vorschlag
zu flach gelesen, und welche können als exakte Ganzoberflächen aufgenommen
werden, wenn jedes sichtbare Stoff-, Qualitäts-, Form- und Mengenfeld erhalten
bleibt und sämtliche Vorkommen vor der Aufnahme gerendert werden?

## Inputs

- das bytegebundene V15-Wörterbuch mit 272 Zeilen und 225 ausführbaren
  Oberflächen;
- GDT638s vollständige 4.128-Zeilen-Abdeckung, 30 vollständige Zeilen und 62
  Ein-Loch-Zeilen;
- die gebundenen Rollen aus GDT627/GDT628 für Wert, Maß, `ol/or` und
  Qualitätsgrade;
- GDT633s CTH-, Zubereitungs- und attributive E-Schicht;
- GDT635s explizite `shy/shey/sheey`-Zustandsleiter und sein Verbot einer
  initialen `s`-Kopfzerlegung vor `h`;
- GDT636s nur lokal zugelassene Restkörperklassen;
- dieselbe 179-Seiten-Auswahl wie GDT638.

ZL3b/IT2a/RF1b bleiben alternative Lesungen derselben Handschrift. `f1r` ist
ausgeschlossen, `f84` und `f84r` sind verboten. Keine Seite und kein Bild wird
neu geöffnet.

## Method

Zuerst wird die vollständige Menge der 24 strikten V15-Lochoberflächen
ausgegeben. Jede erhält einen kurzen Default, auch wenn sie noch nicht
wörterbuchfähig ist. Ein Hold bedeutet deshalb nicht „bedeutungslos“, sondern
nennt die konkrete Lesung und genau das noch ungebundene Feld.

Acht Kandidaten besitzen bereits gebundene Komponenten:

```text
qotchor   qo+t+ch+or     kalt-trockene Drogenportion
dchol     d+ch+ol        Maß trockenen Materials
chotaiin  ch+o+t+aiin    trockene Zubereitung: kalt, Grad III
cthar     cth+ar         CTH-Drogenfraktion I
chear     ch+e+ar        trockene Fraktion I
odaiim    o+d+aiim       Ansatzmaß III
okeey     o+k+ee+y       heißer Ansatz, Bindungsstufe II
shy       sh+y           feucht, Grundform
```

`cthar` und `chear` benutzen `ar` nur innerhalb dieser exakten
Ganzoberfläche. `odaiim` globalisiert weder `aiim` noch Schluss-`m`. `shy` wird
ausdrücklich nicht als `s+hy` behandelt: Der gebundene GDT635-Parser schließt
alle `sh…`-Formen aus der initialen Samen-Kopfregel aus.

In jeder Runde wird genau ein Kandidat zum aktuellen Leser gelegt. Danach
werden alle 4.128 Zeilen neu berechnet und jedes reale Vorkommen des Kandidaten
mit seinen Nachbarn und allen drei Lesungen ausgegeben. Wörterbuchpräfix und
Nachherzustand sind in einer Hashkette gebunden.

Die Aufnahme verlangt:

- alle Vorkommen der vollständigen Oberfläche wurden auditiert;
- mindestens ein reader-exakter Anker existiert;
- die benannte strikte Quellzeile wird tatsächlich vollständig;
- kein bereits bekanntes Token ändert Bedeutung oder Scope;
- keine harte Komponentenkollision und kein generischer Fülltext entsteht;
- die Karte gilt nur für die exakte Oberfläche, nicht für Substrings,
  nackte Restkörper, Wrapper oder vorhergesagte Zellen.

## Decision rule and claim ceiling

Die acht Karten sind konkrete, wiederverwendbare V16-Arbeitsdefaults. Die 16
gehaltenen Formen behalten ebenfalls einen Default, bleiben aber außerhalb des
ausführbaren Glossars. Der Befund identifiziert weder Klartext noch Lautwerte,
historische Wörter oder eine Sprache. Er prüft ein ersetzbares technisches
Codebuchmodell und seine konkreten Passagefolgen.
