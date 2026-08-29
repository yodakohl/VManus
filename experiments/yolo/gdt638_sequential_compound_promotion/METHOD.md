# GDT638 method

## Question

Welche konkreten Ganzoberflächen aus den GDT637-Ein-Loch-Zeilen können einzeln
in das ausführbare Wörterbuch aufgenommen werden, wenn vor jeder Aufnahme alle
Vorkommen derselben Oberfläche sichtbar gemacht werden und jede Aufnahme
mindestens eine neue vollständige Passage liefern muss?

## Eingaben und Umfang

- byte-fixiertes V14-Wörterbuch mit 259 Zeilen und 212 ausführbaren
  Oberflächen;
- GDT637s 30 strikte Ein-Loch-Zeilen, 64 Lochvorschläge und vollständige
  4.128-Zeilen-Abdeckung;
- unveränderte 179-Seiten-Auswahl;
- ZL3b-Token und ZL3b/IT2a/RF1b-Zeilen nur über geschützte, explizit
  seitenbegrenzte Projektionen;
- GDT622, GDT634 und GDT595 nur zur Architektur-, Bedeutungs- und
  Routendoppelungsprüfung.

`f1r` bleibt ausgeschlossen. `f84` und `f84r` bleiben verboten. Keine neue
Seite und kein Bild werden geöffnet.

## Kandidatendeck

Das Deck enthält fünfzehn vollständige Oberflächen aus leserstabilen
GDT637-Ein-Loch-Zeilen. Zwölf waren dort schon manuell komponiert. Drei
automatisch zu flach gelesene Formen werden genauer:

```text
cthey    cth+e+y      CTH-Drogenmaterial, Form I
chkaiin  ch+k+aiin    heiß-trocken, Grad III
chtain   ch+t+ain     kalt-trocken, Grad II
```

Die Reihenfolge beginnt mit engen Drogen-/Formzellen, geht über explizite
Qualitätskomposita zu den häufigeren Maß-/Materialformen und setzt `qoky` mit
138 Vorkommen ans Ende. `keechy` und `chokshy` werden ebenfalls vollständig
geprüft, aber nicht vorab als erfolgreich behandelt.

## Sequenzieller Lauf

In jeder Runde wird genau eine vollständige Oberfläche probeweise zum
aktuellen Glossar gelegt. Substrings, nackte GDT636-Restkörper und die acht
unbelegten GDT637-Leiterzellen bleiben unberührt. Danach werden alle 4.128
Zeilen erneut gelesen und alle realen Vorkommen des Kandidaten ausgegeben.

Jedes Vorkommen erhält einen der Zustände:

- `CONSISTENT_CONCRETE`: genügend bereits konkrete Nachbarn, kein sichtbarer
  Gegenwert;
- `OPAQUE_CONTEXT`: zu viele andere Löcher für eine Prosalese;
- `READER_BOUNDARY_WARNING`: die Zieloberfläche ist nicht in allen Lesungen
  identisch abgegrenzt;
- `HARD_CONTRADICTION`: sichtbare interne oder äußere Bedeutungen kollidieren;
- `NONSENSE`: eine konkrete manuelle Passageprüfung findet keine brauchbare
  Fachlesung.

Opake oder leserinstabile Kontexte widerlegen einen Wert nicht, bleiben aber
gezählt. Eine Aufnahme verlangt eine leserstabile Quelle, die vollständige
Prüfung aller Vorkommen, mindestens eine marginal neue vollständige Zeile,
keine harte Kollision, keinen Unsinn, keine offene Kompositionsbarriere und
keine Änderung eines bereits gelesenen anderen Tokens.

Jede Runde bindet Präfix- und Nachher-Hash des Wörterbuchs. Eine angenommene
Runde hängt genau eine `EXACT_WHOLE_SURFACE_PROMOTION`-Zeile an. Eine gehaltene
Runde verändert weder Zeilenzahl noch Hash.

## Bedeutungsgrenze

GDT622 belegt historisch nur die Mischarchitektur aus gelerntem Ganzwert und
kurzem Fachcode. Seine alte Orientierung `ch=feucht` wurde nach GDT623 ersetzt
und wird nicht wieder importiert. GDT634 liefert die aktuelle Stoff-,
Qualitäts-, Träger- und Wertschicht. GDT595 ist ein anderer Aktionsparser;
seine Zerlegung `qoky=OK+Y` bleibt ein Rivalenmodell außerhalb dieses
179-Seiten-Lesers.

Eine angenommene Karte ist damit ein konkreter, wiederverwendbarer
Arbeitsdefault für exakt diese ganze Oberfläche. Sie ist kein bestätigtes
Wort, kein Lautwert und kein bewiesener Klartext.
