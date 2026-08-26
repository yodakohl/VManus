# GDT441 — Faktorleser statt neues Ganzwort

## Ergebnis

Der Leser kann jetzt eine **sichtbar neu auftauchende Kombination bekannter
Kerne** unmittelbar lesen. Er braucht dafür keinen exakten Eintrag im
1.563-Rezept-Katalog, solange alle Anschlüsse schon zum Werkstattsystem gehören.

Der harte Rücktest ist vollständig:

- 861/861 Rezepte, die jeweils nur auf einer bisherigen Seite vorkommen, sind
  aus den übrigen Seitenfaktoren lesbar;
- 853 sind grün über seitenübergreifende Verbindungen;
- 8 benutzen genau eine alte lokale Ausnahme;
- 0 stoppen;
- alle 4.576 laufenden Ereignisse behalten Zustand, geordnete Kernfolge und
  flüssige GDT440-Lesung bytegleich.

Das ist der fehlende Zwischenweg zwischen „Karte schon im Wörterbuch“ und
„neues Ganzwort erfinden“.

## Was der Leser konkret tut

Eine unbekannte Oberfläche muss weiterhin zuerst sichtbar segmentiert werden.
Danach prüft das Programm:

`bekannte Kerne → alter Scope-Selector → alte Kopf/Fokus-Kanten → alte direkte
Handlungspaare → lizenzierter Schluss → geordnete Kernfolge + flüssiger Satz`

Beispiel einer nicht katalogisierten, aber grünen Karte:

```text
AIIN+AIN+S+Y
WERT · ANTEIL · WÄHLEN · POSTEN
Wähle den Arbeitswert, den Materialanteil und den Pflanzenposten.
```

Alle drei Fokusanschlüsse `S<-AIIN`, `S<-AIN` und `S<-Y` waren bereits
seitenübergreifend belegt. Deshalb braucht diese neue Kombination keine neue
Bedeutung.

Ein roter Gegenfall:

```text
A_ADDR+T+S+OR
```

`S<-OR` ist alt, aber das direkt geschriebene Paar `T>S` ist nicht lizenziert.
Der Leser stoppt und lässt den vorherigen Arbeitszustand unverändert. Die
nächste gültige Karte kann danach normal weiterlesen.

## Warum das mehr als ein Katalog ist

GDT434 konnte nur bekannte 1.563 Schlüssel lesen. GDT441 kann zusätzlich eine
neue Karte aus bekannten Teilen zusammensetzen. Dabei werden nicht bloß Atome
gezählt: Der echte Acht-Selector-Parser entscheidet `AL/AR`, `L/AIR`, `R`,
Besitzerbindung, geerbten Kopf und den begrenzten Vorgriff. Schluss und
Satz-Zustand bleiben getrennte Kanäle.

Die 861 Seiten-Privatrezepte sind dafür der passende Belastungstest: Jedes war
als Ganzrezept außerhalb seiner Seite unbekannt, aber seine inneren Faktoren
waren im übrigen Manuskript vorhanden. Alle 861 gehen durch.

## Wichtige Grenze

Der Faktorleser sagt nicht voraus, **welche** Karte künftig erscheint. Im alten
4.938er Ein-Kern-Raum akzeptiert er selbst 4.303 der 4.566 fehlenden Kandidaten
bedingt. Das ist gut für Durchsatz nach dem Auftreten, aber viel zu breit als
Generator. Daher gilt:

- sichtbare neue Karte mit alten Faktoren: lesen;
- unbekanntes Atom oder neue Verbindung: stoppen;
- niemals aus dem Faktorraum eine Voynich-Oberfläche erfinden.

## Nächster praktischer Schritt

Als Nächstes sollte aus den 269 roten Kandidaten ein kleines **Verboten-Deck**
gebaut werden: Welche fehlende Paar-, Fokus- oder Schlussverbindung löst den
Stopp aus? Dann besitzt der Lehrling neben dem positiven Leser auch eine kurze
Fehlerkarte, die bei den nächsten freigegebenen Seiten sofort sagt, warum eine
Kombination nicht durchgeht.
