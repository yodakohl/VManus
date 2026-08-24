# Elf natürliche Recordzusammenfassungen

Die fünf Herbal-Records werden als offene Pflanzenartikel gelesen; B1–B4 als lokale Zellenregister; B5–B6 als technische Nachträge. Jede Zusammenfassung nennt Ausgangsgegenstand, Transformationen und Endzustand.

## H1 — OPEN_HERBAL_ARTICLE

Von der ersten abgebildeten Pflanze wird ein Teil abgenommen, übertragen und in einen Ansatz eingearbeitet. Der Absatz fügt ein Sollmaß hinzu und bleibt als laufende Zubereitung offen.

- Ausgang: sichtbarer Pflanzenteil (`PICTURED_PLANT_MATTER`)
- Verarbeitung: abnehmen, übertragen, Flüssigkeit ablaufen lassen, in einen Ansatz eintragen und nach Sollmaß beschicken
- Ende: offener Pflanzenansatz (`PREPARATION_BATCH`)
- Zellen: 2, davon 0 geschlossen; Resets 1.

## H2 — OPEN_HERBAL_ARTICLE

Ein weiterer Pflanzenteil wird abgezogen und im bestehenden Ansatz weiterbearbeitet. Danach kommt eine gemessene Zugabe hinzu; der Ansatz bleibt offen für die nächste Arbeitsstufe.

- Ausgang: weiterer Teil derselben abgebildeten Pflanze (`PICTURED_PLANT_MATTER`)
- Verarbeitung: abziehen, weiter vorbereiten und eine gemessene Zugabe einarbeiten
- Ende: offener Pflanzenansatz (`PREPARATION_BATCH`)
- Zellen: 3, davon 0 geschlossen; Resets 1.

## H3 — OPEN_HERBAL_ARTICLE

Das Blütenmaterial wird eingetragen, gehalten, ausgewrungen und ziehen gelassen. Die erste lange Folge schließt, danach werden weitere gemessene Mengen in den Pflanzenansatz gegeben; der Artikel endet offen.

- Ausgang: Material der abgebildeten Blütenpflanze (`PICTURED_PLANT_MATTER`)
- Verarbeitung: eintragen, halten, auswringen, ziehen lassen und weitere Mengen zugeben
- Ende: offener Blütenpflanzenansatz (`PREPARATION_BATCH`)
- Zellen: 4, davon 1 geschlossen; Resets 2.

## H4 — OPEN_HERBAL_ARTICLE

Das Pflanzenmaterial wird bis zum Sollmaß beschickt. Eine Portion wird abgemessen und verwahrt, eine weitere temperiert; zuletzt wird Material an einer bildlich bezeichneten Stelle angelegt.

- Ausgang: Material der breitblättrigen Pflanze (`PICTURED_PLANT_MATTER`)
- Verarbeitung: bis Sollmaß beschicken, Portion abmessen, verwahren, temperieren und anlegen
- Ende: offener Ansatz mit Anwendungsportion (`PREPARATION_BATCH`)
- Zellen: 4, davon 2 geschlossen; Resets 3.

## H5 — OPEN_HERBAL_ARTICLE

Aus dem Pflanzenstoff wird ein Ansatz abgezogen. Eine Portion wird angelegt und weitergeführt; danach werden weitere Pflanzenanteile und eine gemessene Portion in den laufenden Ansatz gegeben.

- Ausgang: Material der mehrköpfigen Pflanze (`PICTURED_PLANT_MATTER`)
- Verarbeitung: Ansatz abziehen, Portion anlegen und weiterführen, weitere Pflanzenanteile und Mengen zugeben
- Ende: offener Pflanzenansatz (`PREPARATION_BATCH`)
- Zellen: 6, davon 1 geschlossen; Resets 2.

## B1 — CELLULAR_BASIN_REGISTER

Ein gemeinsames Becken wird in 21 kurzen Arbeitszellen beschrieben. Die Flüssigkeit wird gemessen, geführt, gekühlt, gewaschen, umgeschöpft, stellenweise angewendet und abgesetzt; 17 Zellen schließen, die letzte hält nur eine Zielstelle offen.

- Ausgang: Flüssigkeit im gemeinsamen Becken (`WORKING_LIQUID`)
- Verarbeitung: beschicken, durchleiten, kühlen, waschen, umschöpfen, anwenden, absetzen und auffangen
- Ende: offene Beckenflüssigkeit an einer Zielstelle (`WORKING_LIQUID`)
- Zellen: 21, davon 17 geschlossen; Resets 18.

## B2 — CELLULAR_MULTI_STATION_REGISTER

Vier sichtbare Stationsgruppen liefern 22 weitgehend selbständige Zellen. Oben wird Flüssigkeit weitergegeben und angelegt, am Handgerät ruht sie, unten wird sie abgeleitet, und an den Randstationen wirkt, kühlt und setzt sie sich ab; 19 Zellen schließen.

- Ausgang: Flüssigkeit in oberem Becken, Handgerät, unterem Becken und Randstationen (`WORKING_LIQUID`)
- Verarbeitung: weitergeben, anlegen, einwirken, ruhen, abführen, umfüllen, kühlen und absetzen
- Ende: geschlossene Zielportion an den Randstationen (`TARGETED_TRANSFER_PORTION`)
- Zellen: 22, davon 19 geschlossen; Resets 22.

## B3 — CELLULAR_VESSEL_APPLICATION_REGISTER

Die 34 Zellen wechseln sichtbar zwischen Fächerstation, zwei Gefäßen, getrenntem Zwischenbereich und Figurenpaar. Sie messen, temperieren, halten, setzen ab und führen Portionen weiter; 31 Zellen schließen. Das Ende ist eine verbuchte Anwendungsladung, kein globaler Kreislauf.

- Ausgang: Arbeitsflüssigkeit, Gefäßansätze, getrennte Portionen und Figurenpaar-Anwendungen (`WORKING_LIQUID`)
- Verarbeitung: auffangen, temperieren, messen, umfüllen, absetzen, weiterleiten und anwenden
- Ende: geschlossene Anwendungsladung (`APPLICATION_CHARGE`)
- Zellen: 34, davon 31 geschlossen; Resets 32.

## B4 — CELLULAR_APPLICATION_AND_STATION_REGISTER

Alle 16 Zellen schließen. Die erste Gruppe behandelt eine Anwendung am Figurenpaar mit Halten, Anlegen und Festbinden; danach folgen zwei technische Stationen mit Messen, Durchlass, Absetzen und Weiterführung zu einer Zielportion.

- Ausgang: Anwendung am Figurenpaar sowie Flüssigkeit an linker und rechter Hauptstation (`APPLICATION_CHARGE`)
- Verarbeitung: einwirken, anlegen, festbinden, durch einen Lauf halten, messen, absetzen und weiterführen
- Ende: geschlossene Zielportion (`TARGETED_TRANSFER_PORTION`)
- Zellen: 16, davon 16 geschlossen; Resets 16.

## B5 — TECHNICAL_APPENDIX

Der linke Nachtrag enthält drei technische Zellen. Zwei führen und schließen Portionen; die letzte lagert eine Flüssigkeit ab, führt sie weiter und beschickt den lokalen Bestand, bleibt aber offen.

- Ausgang: Flüssigkeit der linken Nachtragsstation (`WORKING_LIQUID`)
- Verarbeitung: weiterführen, Portion einfüllen, ablagern und erneut beschicken
- Ende: offene Stationsflüssigkeit (`WORKING_LIQUID`)
- Zellen: 3, davon 2 geschlossen; Resets 3.

## B6 — TECHNICAL_APPENDIX

Der rechte Nachtrag ist eine einzige offene Folge: Flüssigkeit wird aufgefangen, beschickt, temperiert und als Zielportion weitergeführt.

- Ausgang: Flüssigkeit im rechten S-Lauf (`WORKING_LIQUID`)
- Verarbeitung: auffangen, beschicken, temperieren und zur nächsten Stelle führen
- Ende: offene Zielportion (`TARGETED_TRANSFER_PORTION`)
- Zellen: 1, davon 0 geschlossen; Resets 1.
