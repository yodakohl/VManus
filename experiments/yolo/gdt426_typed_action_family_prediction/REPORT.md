# GDT426 — Die neun lokalen Karten werden vorhersagbar

## Das kleine Klassenmodell

Die neun Handlungen werden für den Lehrling in vier grobe Familien gelegt:

- **SELECT:** NEHMEN/CH und WÄHLEN/S;
- **MOVE_SET:** GEBEN/K, SETZEN/OK und EINSETZEN/P;
- **HOLD_PROCESS:** HALTEN/SH und BEARBEITEN/CHD;
- **CONTROL:** EINSTELLEN/T und MARKIEREN/R.

Dazu kommen drei Randfamilien: **GRADE** (E/EE/EEE), **ITEM**
(Y/AIIN/AIN/OR) und **RELATION** (AL/AR/L/AIR).

## Was mit den neun Karten geschieht

Keine bleibt unverbunden:

- `OK>S` und `SH>T` kommen auf anderen Seiten als dasselbe geordnete Paar mit
  sichtbaren Zwischenslots vor;
- `CH>OK`, `CHD>S`, `K>OK` und `R>T` folgen einer auf anderen Seiten belegten
  Handlungsklassen-Transition;
- `R<-AIR` und `S<-EEE` schließen ein Rechteck: derselbe Kopf nimmt andere
  Mitglieder der Familie, und derselbe Fokuswert steht an anderen Köpfen;
- `R<-EE` folgt der bereits belegten Kombination CONTROL←GRADE über T.

Damit stehen **9 gelbe Vorhersagen und 0 unerklärte lokale Karten**. Gelb ist
wichtig: Die genaue Form wird nicht nachträglich grün genannt. Sie ist nur aus
dem bereits bekannten Typensystem erwartbar.

## Warum das nicht beliebig ist

Alle 16 möglichen Übergänge zwischen den vier Handlungsklassen kommen im
vorhandenen Bestand vor. Ebenso sind alle 12 Kombinationen aus vier
Handlungsklassen und drei Fokusfamilien belegt. Auf der feineren Ebene der 81
exakten Handlungspaare sind 49 mehrseitig, 15 einseitig und 17 noch gar nicht
belegt; diese 17 liegen aber ausnahmslos in einer bereits belegten
Klassen-Transition.

## Regel für spätere Seiten

Eine neue exakte Paar- oder Fokuskarte wird so behandelt:

1. exakt anderswo belegt → grün;
2. altes exaktes Paar mit Zwischenslot oder altes Typenrechteck → gelb;
3. nur alte Klassen-Transition → gelb, schwächer;
4. neue Klasse, leere Klassen-Transition oder neuer Fokusfamilientyp → rot.

So steigt der Durchsatz, ohne dass ein unbekanntes Paar automatisch eine neue
Wortbedeutung bekommt.
