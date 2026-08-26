# GDT489 — Methode

## Question

Welche Nachbarkomponenten der elf exakten GDT428-T/R-Rahmen sind in den 183
lokalen Events bereits vorhanden, und welche Rahmen werden dort tatsächlich
von `T=EINSTELLEN` berührt?

## Inputs

- GDT428: 104 Aktionsersatzrahmen, davon elf exakte T/R-Rahmen;
- GDT485: 183 feste Eventrückprojektionen;
- GDT486: 29 Kontrastregeln;
- GDT487: dreizehn wiederkehrende lokale Ersatzkanten;
- GDT488: die zwei lokalen EINSTELLEN-Träger.

## Method

1. Aus jedem T/R-Rahmen wird `@ACTION` entfernt. Die verbleibende geordnete
   Wurzelfolge ist der Nachbarkontext; `@ACTION` allein erhält keinen Kontext.
2. Jeder nichtleere Kontext wird als zusammenhängende Folge gegen jedes der
   183 festen Eventrezepte gehalten. Pro Rahmen×Event entsteht höchstens ein
   Zeuge, der sämtliche Trefferpositionen mitzählt.
3. Separat wird `@ACTION` durch T ersetzt. Nur wenn diese vollständige
   T-Teilfolge in einem lokalen Event zusammenhängend vorkommt, entsteht ein
   lokaler T-Rahmenkontakt. Ein ganzer Event und ein Präfix/Suffix werden
   unterscheidbar ausgegeben.
4. Ein Kompositionsnachbar wird nur aus einem solchen T-Kontakt gebildet, nie
   aus einem bloß vorhandenen Kontext. GDT428s exakte T/R-Ersetzung bleibt als
   Herkunft am Rahmen sichtbar.
5. Kompositionskanten und GDT486-Ersatzkanten behalten verschiedene Typen. Ein
   gemischter Alternativweg wird nicht als reiner Ersatzzyklus gezählt.
6. Für den letzten Singleton wird geprüft, ob ein lokaler T-Nachbar über eine
   wiederkehrende GDT487-Ersatzkante zu `HIER` führt.

## Decision rule and claim ceiling

Ein vorhandener Nachbarkontext zeigt nur lokale Kapazität. Erst ein
zusammenhängender T-Teilrahmen erlaubt die Kompositionskante. Der letzte
Singleton gilt als typisiert verbunden, wenn sein alternativer Weg vollständig
ist und jede Kante ihre Herkunft und ihren Typ behält.

GDT489 ordnet feste Arbeitsbedeutungen und Lesungen; es bestätigt sie nicht
unabhängig. Keine Bedeutung, Formulierung, Modellfolge, Recordgrenze,
Oberfläche, Rezeptfolge, Event- oder Seitenzuordnung darf geändert werden.
