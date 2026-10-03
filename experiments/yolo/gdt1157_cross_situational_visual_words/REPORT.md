# GDT1157 — stabile Bildmerkmalsprädiktoren reichen im vollständigen Suchvergleich nicht

**Entscheidung: NO_SUPPORTED_VISUAL_WORD_LEAD.** Das feste probabilistische Modell verbessert bei sechs ganzen Wortformen die Vorhersage auf jeweils vollständig ausgeschlossenen Blättern gegenüber beiden Vergleichsmodellen. Diese sechs erfüllen auch die Stabilitäts- und Mindestabdeckungskriterien. Trotzdem übersteht keine die registrierte Kontrolle der gesamten Suche: Schon zufällig neu zugeordnete Bildpakete liefern in dieser Wortauswahl regelmäßig stärkere Spitzenwerte.

Damit wurde gemeinsame mehrdeutige Bild-/Textevidenz tatsächlich berechnet, nicht wegen eines fehlenden einzelnen „Zeigeworts“ verworfen. Das Ergebnis rechtfertigt aber weder eine Wortübersetzung noch eine nachträgliche Kombination von Merkmalen zur Rettung der Kandidaten.

## Fixierte Daten und Modell

38 zuvor kodierte Bildseiten auf32 physischen Blättern; alle169 vollständigen Wortformen aus GDT1090; sechs Merkmale, jeweils zwei Beobachter. Wortpräsenz ist ZL3b auf der Bildseite, keine Häufigkeit oder Bildbeschriftungszuweisung. Die Merkmalsnamen stehen für Beobachterkategorien, nicht für angenommene Wortbedeutungen. Alle Seiten haben dieselben vorhandenen Metadaten H/A/1; die Hintergrundkorrektur nach Hand/Currier bleibt unverändert im Verfahren.

Jeweils ein gesamtes physisches Blatt blieb bei der Anpassung ausgeschlossen. Ein gemeinsames64-Zustandsmodell lernte die Verteilung der sechs binären Bildmerkmale ausschließlich aus vollständig übereinstimmend kodierten Trainingsseiten, mit vorab fester Glättung. In den32 Faltungen liefern21–23 solche Seiten die Zustandshäufigkeiten. Unsichere oder widersprüchliche Merkmale bleiben unbekannt; die Vorhersage integriert über die damit verträglichen gemeinsamen Zustände. Die Merkmale wurden nicht als unabhängig behandelt.

Die sechs logistischen Einzelmerkmalmodelle wurden mit unverändertem Koeffizientengitter und quadratischer Strafe angepasst. Ein separates Modell der Gesamtzahl sichtbarer Merkmale (COUNT) dient als begrenzter generischer Konkurrent. Beide Vorhersagegewinne müssen mindestens0.01Bit je gleichgewichtetem Blatt erreichen. Mindestens80% aller32 Faltungen müssen dasselbe Merkmal eindeutig mit positivem Koeffizienten wählen; mindestens drei verschiedene Blätter müssen Wortpräsenz und eindeutig bejahte Merkmalskodierung gemeinsam besitzen. Alle Kriterien und die Behandlung von Gleichständen stehen in [PREREGISTRATION.md](PREREGISTRATION.md).

## Alle sechs Kandidaten vor der vollständigen Suchkontrolle

|Ganze Form|Gewähltes Bildmerkmal|Gewinn gegen Hintergrund|Gewinn gegen COUNT|Eindeutig positive Faltungen|Gemeinsame Wort-/JA-Blätter|Suchreferenzrang|
|---|---|---:|---:|---:|---:|---:|
|chodaiin|HORIZONTAL_BEADS|+0.095541|+0.046188|32/32|3|1.000|
|dol|MULTI_UNIT_SPIKE|+0.177769|+0.159352|32/32|5|0.755|
|dy|SPINY_ROUND_HEAD|+0.110475|+0.129229|32/32|5|0.940|
|kol|MULTI_UNIT_SPIKE|+0.032808|+0.031109|32/32|3|1.000|
|oky|MULTI_UNIT_SPIKE|+0.065436|+0.084841|32/32|4|0.990|
|sho|HORIZONTAL_BEADS|+0.020613|+0.080590|32/32|4|1.000|

Die Namen in Spalte2 sind statistische Prädiktoren innerhalb dieses Modells, **keine Übersetzungen** der Formen in Spalte1. Alle169 geprüften Formen, einschließlich aller Gegenbefunde, stehen in [CANDIDATE_TABLE.md](CANDIDATE_TABLE.md) und `artifacts/CANDIDATES.json`. Es wurde nicht nur die beste Einzelstelle ausgewählt.

## Ganze Bildpakete zufällig zugeordnet, gesamte Suche erneut angepasst

Die Nullzuordnungen bewegen immer die vollständigen sechs A/B-Kodierungen eines physischen Blatts gemeinsam; recto/verso, Beobachterunsicherheit und passende Hand-/Currier-Signaturen bleiben erhalten.32 Blätter können tatsächlich andere beobachtbare Pakete erhalten. Nach Abzug identischer ternärer Merkmalsmasken umfasst der beobachtbare Zuordnungsraum417585409700659200000 Kombinationen: Die festgelegte Kapazitätsgrenze ist erfüllt.

Für alle199 festen Zufallszuordnungen wurden Zustandsmodell, Wort-/Merkmalsanpassung, COUNT-Konkurrent, sämtliche169 Wörter und alle Auswahlbedingungen neu berechnet. Alle199 Zuordnungen waren sowohl als rohe Beobachterpakete als auch als beobachtbare Masken verschieden. Es gab keine adaptive Wiederholung oder nachträgliche Auswahl des Nullmodells.

Jede der199 Nullwelten hat mindestens einen Kandidaten, der die Vorbedingungen passiert. Ihre jeweils besten Werte reichen von0.052015 bis0.372217Bit; der Median beträgt0.194665Bit. Der stärkste beobachtete Kandidat `dol` erreicht nur0.159352Bit für den schlechteren seiner beiden Vergleiche.150 der199 Nullmaxima sind mindestens so groß, entsprechend dem vorab festgelegten Plus-eins-Rang151/200=0.755. Keine Form erreicht die verlangten0.05.

Die positiven Vorhersagegewinne bleiben reale Ergebnisse dieses festen Modells. Sie sind in diesem bereits ausgewählten Suchraum aber nicht ungewöhnlich genug, um einen Wort-/Bildhinweis zu nominieren. Insbesondere ist32/32-fache Modellauswahl hier kein Nachweis einer eindeutigen Bedeutung.

## Mehrdeutigkeit, Grenzen und nächste Entscheidung

Es gibt keine zwei vollkommen identischen ternären Merkmalsmasken auf dem ursprünglichen38-Seiten-Bestand. Alle objektiv gleichen Modellentscheidungen bleiben dennoch in den Faltungsdateien erhalten, einschließlich Gleichständen mit dem Hintergrundmodell. Auch eine eindeutige Auswahl unter diesen sechs Prädiktoren schließt nicht kodierte, korrelierte Bildeigenschaften, Themen oder generische Textfunktionen nicht aus.

Der Hintergrund modelliert Seitenpräsenz, aber weder gesamte Textmenge noch Zeilenposition. Der COUNT-Konkurrent deckt nur einen begrenzten generischen Einfluss ab. Diese Einschränkungen rechtfertigen keine Uminterpretation des negativen Suchergebnisses und wurden nicht nachträglich korrigiert. Wortinventar und Bildseiten waren bereits ausgewählt und exponiert; die Referenzränge sind keine projektweite Signifikanz oder unabhängige Bestätigung.

Dieser feste Modellversuch ist damit geschlossen. Keine nachträgliche Merkmalsunion, Wortlängenanpassung, Teilmengenauswahl oder Frequenzglosse wird daraus übernommen. Ein anderer Ansatz braucht eine eigenständige Begründung und neue Vorregistrierung. Die vorherige GDT1090-Entscheidung bleibt unverändert.

## Reproduzierbarkeit und Zugang

Lokal fixiert am2026-10-03 um03:16:49UTC, vor den neuen Statistiken. Ein öffentlicher Vorabzeitstempel wird nicht behauptet. Alle Eingabepins wurden vor dem Lauf kontrolliert. Der unabhängige Validator besteht14/14 Prüfgruppen: sämtliche32 Faltungen,169 Wörter,199 Nullwelten mit33631 Wortkandidaten und63 zusätzliche direkte64-Zustands-Gitterprüfungen stimmen überein (numerische Toleranz1e-11). Keine neuen Bilder, Transkriptionen oder Kontakte; f84/f84r, f116v und die Reserven bleiben geschlossen.

`INPUT.json` enthält den vollständigen begrenzten Modellinput. `OBSERVED_FOLDS.json.gz` enthält alle32 Faltungen,6422 Wort-/Seitenvorhersagen, Anpassungszahlen, gemeinsame Zustandsverteilungen, Modellwahlen und Gleichstände. `NULL_RESULTS.json.gz` enthält alle199 vollständigen Suchergebnisse mit allen169 Wörtern und unveränderten Paketzuordnungen. Beide Dateien verwenden deterministisches gzip ohne Zeitstempel.

**Bestätigte Wörter:0. Keine Autorenzuordnung, Pflanzennamen oder Bedeutungen übernommen.**
