# GDT448 — Methode

## Question

Welche neutral gelesenen oder gestoppten GDT447-Nachbarformen ändern ihren
Status, wenn sie den realen eingehenden Handlungskopf, das reale Argument, den
Aussagescope und die unmittelbar folgende Karte ihrer Quellvorkommen erhalten?

## Inputs

- GDT441: geordnete 4.576-Ereignis-Wiedergabe mit realem Vorzustand;
- GDT446: getrennter Identitäts-/Ausführungszertifizierer;
- GDT447: 30.763 gerichtete Katalognachbarn.

## Method

Die 4.576 Ereignisse werden zuerst auf 4.275 verschiedene Kontextsignaturen
reduziert:

```text
Quellrezept × Handlung davor × Argument davor × Aussagekopf × nächste Karte
```

Jeder Nachbar eines tatsächlich vorkommenden Quellrezepts wird in jede reale
Signatur dieses Rezepts eingesetzt. Das ergibt 61.878 verschiedene lokale
Wiedergaben; wiederholte identische Kontexte bleiben über ihre Ereignislisten
und ein Vorkommensgewicht vollständig erhalten.

Dies ist eine Ein-Karten-Sonde. Der Nachbar darf seinen ausgehenden Zustand
setzen, aber der restliche reale Strom wird nicht mit einer künstlich
veränderten Vergangenheit neu simuliert. Identität wird weiterhin allein am
vollständigen Zielschlüssel entschieden.

## Decision rule and claim ceiling

Ein Kontext darf einen neutralen Stopp retten oder eine neutrale Lesung
verschärfen, wenn der unveränderte GDT446-Zertifizierer dies aus den sichtbaren
Scopefaktoren ergibt. Er darf niemals die Identitätsroute ändern, die
Quellidentität übertragen oder einen neuen Faktor erfinden.

Der Test bewertet lokale Ausführbarkeit bekannter Atome. Er erzeugt keine
Oberfläche, kein Vorkommen und keine neue Bedeutung.
