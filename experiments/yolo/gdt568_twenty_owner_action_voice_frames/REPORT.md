# GDT568 — 20 Verbrahmen tragen alle 45 Registerzellen

Status:
`PASS_20_OWNER_ACTION_FRAMES__45_REGISTER_CELLS__763_STATE_CLAUSES_HARMONIZED__866_SHARED_ACTION_CONTACTS__FULL_FRAME_517_TO_866__HEAD_730_TO_866__ZERO_ROOT_CHANGE`

## Der konkrete Fortschritt

Die neun Handlungswurzeln bleiben unverändert. Ihre bereits in GDT415 und
GDT498 vorhandenen 45 Registerzellen brauchen aber nicht 45 unabhängige
Ganzphrasen: Sie lassen sich als 20 kleine Verbrahmen schreiben.

| Wurzel | breiter Arbeitswert | verschiedene Rahmen | ownergebundene Realisierungen |
|---|---|---:|---|
| OK | SETZEN | 5 | `trage … ein`; `setze … im Arbeitsgang an`; `setze …`; `setze … im Stationsgang an`; `setze … als Ansatz an` |
| CH | NEHMEN | 3 | `entnimm …`; `nimm …`; `nimm … auf` |
| SH | HALTEN | 2 | `halte … fest`; `halte …` |
| K | GEBEN | 3 | `ordne … zu`; `gib … zu`; `führe … zu` |
| S | WÄHLEN | 1 | `wähle …` |
| CHD | BEARBEITEN | 1 | `bearbeite …` |
| T | EINSTELLEN | 2 | `lege … fest`; `stelle … ein` |
| R | MARKIEREN | 2 | `kennzeichne …`; `markiere …` |
| P | EINSETZEN | 1 | `setze … ein` |

Das ist ein brauchbares Modell für die gesuchte Mischung: Die kurze Wurzel
trägt einen breiten, wiederverwendbaren Handlungskern; das Register wählt den
gelernten Fachrahmen. `K` muss deshalb nicht plötzlich drei verschiedene
Wörterbuchbedeutungen erhalten. `GEBEN` bleibt die gemeinsame Arbeitsbedeutung,
während Text/Himmel `zuordnen`, Pflanzen/Pharma `zugeben` und Stationen
`zuführen` als konkrete Lesestimmen benutzen.

## Anwendung auf die vollständige Ausgabe

Von 1.656 Zustandskarten tragen 1.643 mindestens eine Handlung. Darin liegen
1.851 Handlungsvorkommen beziehungsweise 1.834 verschiedene
Ereignis×Wurzel-Verwendungen. Für jede einzelne Verwendung enthält die
ownergebundene Kontrollzeile bereits den Ziel-Verbkopf.

Der 20-Karten-Adapter ändert 763 Zustandszeilen und 479 Aussagen auf 27 Seiten.
893 Zustandszeilen waren schon passend oder handlungslos. `f4r` ist die einzige
der 28 Seiten mit Zustandsprosa, auf der kein Verbrahmen geändert werden muss;
die beiden lokalen Null-Prosa-Seiten bleiben ohnehin sichtbar. Alle 3.466
Nichtzustandszeilen bleiben bytegleich.

Fünf kurze Vorher/Nachher-Beispiele zeigen, dass nicht der Wurzelwert, sondern
seine fachliche Realisierung wechselt:

```text
Text:       Weiter: halte den Kennwert.
         → Weiter: halte den Kennwert fest.

Pflanzen:   Weiter: setze den Pflanzenposten.
         → Weiter: setze den Pflanzenposten im Arbeitsgang an.

Himmel:     Danach: gib den Positionsposten.
         → Danach: ordne den Positionsposten zu.

Stationen:  Nimm den Stationsposten und gib den Stationsposten …
         → Entnimm den Stationsposten und führe den Stationsposten zu …

Pharma:     Weiter: gib die Ansatzeinheit; auf Grad I.
         → Weiter: gib die Ansatzeinheit zu; auf Grad I.
```

## Die Anschlüsse werden wirklich einheitlicher

An 854 gemischten Zustands/Nichtzustands-Anschlüssen teilen beide Seiten
mindestens eine Handlungswurzel; zehn davon teilen zwei, insgesamt also 866
Handlungskontakte. Vor dem Adapter waren 517/866 vollständige Verbrahmen und
730/866 Verbköpfe identisch. Danach sind es jeweils 866/866.

Der größte einzelne Gewinn liegt bei `K`:

```text
114 gemeinsame K-Kontakte
  0/114 voller ownergebundener Rahmen vorher
 33/114 passender Verbkopf vorher
114/114 voller Rahmen und Verbkopf nachher
```

`OK` steigt beim vollen Rahmen von 31 auf 169 Kontakte, `CH` von 97 auf 160.
`S`, `CHD` und `P` waren bereits in allen Registern gleich. Das Muster ist also
nicht freie Stilverschönerung: Nur die Wurzeln mit beobachteter
Registerrealisierung werden erweitert.

## Was jetzt als Arbeitstheorie steht

Die aktuelle deutsche Leseschicht benötigt für Handlungen keine Sammlung langer
Wörterbuchdefinitionen. Sie benötigt neun breite Aktionswerte plus 20 kurze,
registergebundene Verbrahmen. Zusammen mit GDT567s 39 Argument-, Relations-,
Orts- und Abschlusskarten ergibt das eine kleine Kompositionssprache, die die
gesamte 30-Seiten-Ausgabe erreicht.

Das ist eine konkrete Verbesserung der Arbeitsübersetzung, keine neue
Entzifferungsbehauptung. Geschriebene Atome, Rezepte, Grenzen, Seiten und die
neun Wurzelwerte bleiben unangetastet. Die 49 unabhängigen Prüfungen bestehen.

## Nächster Arbeitsweg

Der nächste hörbare Rest liegt nicht mehr in Substantiven, Relationen oder
Handlungen, sondern in kleinen Kontextmarkern wie `[wie zuvor]`, `im laufenden
Gang`, `Weiter:` und `Danach:`. Als Nächstes wird geprüft, ob auch diese Reste
auf wenige wiederkehrende ownergebundene Satzrahmen zurückgehen. Keine neue
Seite und keine neue Wurzel ist dafür nötig.
