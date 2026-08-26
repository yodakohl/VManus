# GDT447 — Methode

## Question

Bleibt die in GDT446 getrennte Identität über zehntausende nahe Rezeptnachbarn
wirklich exakt, oder schleicht sich durch Ähnlichkeit, Quelle oder
Kollisionsdichte ein unscharfer Katalogtreffer ein?

## Inputs

- GDT434: alle 1.563 geordneten Katalogschlüssel und Ränge;
- GDT413: 46 sichtbare Komponenten und ihre Faktorfamilien;
- GDT446: getrennter Identitäts- und Ausführungsleser.

## Method

Pro Quellschlüssel werden drei sichtbare Änderungen gebildet:

1. jedes Atom einmal löschen;
2. jedes ungleiche Nachbarpaar einmal tauschen;
3. jedes portable Handlungs-, Argument-, Relations-, Reihenfolge- oder
   Gradatom durch jedes andere Atom derselben Klasse ersetzen.

Formalkontrollen und lokale Zeichen werden nicht semantisch substituiert. Nach
gleichen Zielrezepten innerhalb derselben Quellkarte und Mutationsfamilie wird
dedupliziert; alle auslösenden Positionen bleiben verzeichnet.

Für jedes Ziel wird zuerst eine exakte Katalogmitgliedschaft geprüft. Nur wenn
das Ziel selbst ein Schlüssel ist, darf es eine exakte Identität erhalten.
Davon unabhängig läuft der GDT446-Faktorkanal in neutralem Kontext.

## Decision rule and claim ceiling

Jedes nicht katalogisierte Ziel muss `IDENTITY_NEW_VISIBLE_RECIPE` behalten,
auch wenn es aus vielen Katalogquellen erreichbar oder faktorisch lesbar ist.
Keine Quellidentität darf mitgetragen werden; kein unscharfer Matcher ist
zulässig.

Der Atlas ist kein Generator: Er bewertet nur künstlich vorgelegte bekannte
Komponentenfolgen und sagt weder Oberfläche noch Auftreten voraus.
