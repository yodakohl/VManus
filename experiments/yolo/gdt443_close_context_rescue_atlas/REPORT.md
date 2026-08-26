# GDT443 — Der Kopf rettet die Schlusskarte

## Ergebnis

Die 52 neutralen Stopps aus GDT442 sind fast vollständig Kontextlücken, keine
fehlenden Kartenbedeutungen.

Über alle neun eingehenden Handlungsköpfe und beide Scope-Lagen ergeben sich
936 Kombinationen:

- 841 grün;
- 93 gelb über eine bereits bekannte lokale Kante;
- 2 rot;
- insgesamt 934/936 gerettet.

51 der 52 Rezepte funktionieren in sämtlichen 18 Kontexten. Nur
`OL+EEE+DY` hat zwei rote Lagen.

## Die zwei Scope-Lagen

### Neuer Aussage-Scope, Besitzerzustand lebt weiter

Hier trägt die Besitzerbank den alten Handlungskopf, aber die neue Aussage hat
noch keinen Scope-Kopf. Alle 468 Kombinationen gehen durch:

- 387 grün;
- 81 gelb;
- 0 rot.

Die 81 gelben Zellen sind neun `AIR`-haltige Rezepte unter neun Köpfen. Ohne
laufenden Scope bindet `AIR` an den Besitzer; `OWNER<-AIR` ist die bekannte
lokale Besitzerkante. Der Schluss selbst ist immer lizenziert.

### Derselbe Aussage-Scope läuft weiter

Hier bindet der Fokus direkt an den geerbten Handlungskopf:

- 454 grün;
- 12 gelb;
- 2 rot.

Beide roten Zellen gehören zur selben Karte:

```text
OL+EEE+DY nach CHD -> FOCUS:CHD<-EEE fehlt
OL+EEE+DY nach R   -> FOCUS:R<-EEE fehlt
```

Das ist genau die GDT442-Grenze. `DY` darf beide Köpfe schließen; verboten ist
nicht der Schluss, sondern die vorher nicht belegte Bindung von Grad III an
`CHD` beziehungsweise `R`.

## Reale Gegenprobe

Sechs der 52 Rezepte sind bereits in der laufenden Ausgabe vorhanden:

`AL+DY`, `L+DY`, `OL+O+DY`, `OT+AL+DY`, `OT+AR+DY`, `OT+O+DY`.

Sie haben zusammen 17 Vorkommen auf acht Seiten. Alle 17 besitzen im echten
linken Kontext einen Handlungskopf, alle 17 sind grün und keines hat eine
Blockregel. Damit ist der scheinbare Widerspruch aus dem neutralen
Kandidatenraum vollständig erklärt.

## Praktische Lehrregel

```text
Schlusskarte ohne sichtbaren eigenen Kopf:
1. Besitzerbank nach laufendem Kopf fragen.
2. Bei neuem Aussage-Scope Fokus nach Besitzerregel lesen.
3. Bei laufendem Scope Fokus an denselben Kopf binden.
4. Nur CHD/R + EEE bleiben rot.
5. Dann DY schließen lassen.
```

Damit ist „Schluss ohne Kopf“ kein eigener Kartentyp mehr, sondern eine klare
Zustandsfrage.

## Nächster Schritt

Die größere offene Fläche sind nun die 44 direkten Handlungspaar-Lücken.
GDT422 hat bereits gezeigt, dass sichtbare Slots lange Ketten trennen können.
Der nächste sinnvolle Atlas setzt deshalb jeden der elf Fokuskerne zwischen
jeden roten Paaranfang und jedes rote Paarende: 44×11 = 484 getrennte
Mikroketten. So sehen wir, welche rote Direktnachbarschaft mit einem sichtbaren
Argument-, Relations- oder Gradslot sauber lesbar wird, ohne das direkte Paar
zu promovieren.
