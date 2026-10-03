# GDT1156 — keine ausreichende Kapazität für den festen Blattseitenvergleich

**Entscheidung: NO_CAPACITY.** Der registrierte Vergleich braucht mindestens acht geeignete Doppelblätter aus mindestens drei Lagen. In jeder Transkription bleiben nur vier Doppelblätter einer einzigen Lage. Deshalb gibt es keine Nominierung und keine Aussage, dass ein entsprechender Herstellungszusammenhang fehlt.

Untersucht wurde ausschließlich ein begrenzter Zusammenhang zwischen l/m-Endungsresiduen auf den beiden Seiten zusammengehöriger Blätter. Das ist kein Test, der Herstellungsfolge und Lesereihenfolge voneinander unterscheiden könnte. Der wichtigste Unterschied zum vorigen Zeichenfolgenvergleich: Die Paarbildung kommt aus der materiellen Kollation, nicht aus nachträglich gesuchten Textähnlichkeiten.

## Tatsächlich geprüfte Daten

Die Geometrie umfasst 35 nominelle Doppelblätter mit 140 nominellen Seiten in den Lagen1–7 und20. Grundlage ist die publizierte Kollation von [Lisa Fagin Davis, 2025](https://manuscriptroadtrip.wordpress.com/2025/01/19/voynich-codicology/). Die Paarung der gegenüberliegenden Enden dieser Lagen sowie ar/bv und av/br als gemeinsame Blattseiten ist eine geometrische Ableitung, keine Datierung des Schreibvorgangs.

Verwendet wurden ausschließlich die bereits exponierten GDT1155-END/SPACE-Ereignisse aus dem freigegebenen915-Bestand und die unveränderten155 exakten l/m-Stammpaare. Ganze Formen bleiben getrennt; kein neues Wort und keine Bedeutung wurde eingesetzt. f84/f84r, f116v und die Reserven wurden nicht geöffnet.104/115 sind aus Anpassung und Prüfung ausgeschlossen. Das unvollständige Doppelblatt103/116 ist kein Prüfobjekt; seine bereits zugelassenen Seiten dürfen außerhalb der zurückgehaltenen Lage als Anpassungsdaten dienen.

|Leser|Seiten mit erfüllten Einzelbedingungen|Doppelblätter vor Blockbedingung|Endgültige Doppelblätter|Lagen|Ereignisse auf Prüfseiten|
|---|---:|---:|---:|---:|---:|
|IT2a, primär|63/140|7/35|4|1|901|
|ZL3b, Sensitivität|49/140|5/35|4|1|712|
|RF1b, Sensitivität|51/140|5/35|4|1|791|

In allen drei Lesern bleiben ausschließlich Lage20: **105/114,106/113,107/112,108/111**. IT2a hat zusätzlich die zunächst geeigneten Paare3/6,34/39,44/45; ZL3b und RF1b nur3/6. Jedes dieser zusätzlichen Paare ist jedoch allein in seinem Lage×Stratum-Block. Die vorab verlangten mindestens zwei geeigneten Doppelblätter pro Block fehlen. Diese Bedingung wurde nicht gelockert.

Seiten-Ausschlussgründe, überlappend gezählt:

|Grund|IT2a|ZL3b|RF1b|
|---|---:|---:|---:|
|Nicht zugelassen|12|12|12|
|Keine END/SPACE-Ereignisse|15|15|14|
|Weniger als10 Ereignisse|70|84|82|
|Kein einzelnes bekanntes Stratum|16|16|15|
|Explizit ausgeschlossenes unvollständiges Doppelblatt|4|4|4|
|Expliziter Mischhand-Ausschluss104/115|4|4|4|

Bei28/30/30 Doppelblättern (IT/ZL/RF) scheitert mindestens eine Seite. Zwei weisen zusätzlich verschiedene Strata auf; diese Gründe sind nicht disjunkt.3/1/1 weitere Doppelblätter scheitern erst an der Blockgröße. Alle einzelnen Begründungen stehen in `artifacts/ELIGIBILITY.json`.

## Fester Vergleich und beobachtete Werte

Das vorab festgelegte Endungsmodell wurde außerhalb der gesamten jeweils geprüften Lage angepasst: globale Jeffreys-Glättung, danach unveränderte Stratum- und Stammgewichte20 und10. Für jede Seite ist das Residuum der Mittelwert aus beobachtetem m-Indikator minus Modellwahrscheinlichkeit unter der tatsächlich vorliegenden END/SPACE-Kategorie. Aus recto-minus-verso-Residualen folgt der registrierte Doppelblattbeitrag. Es wurde kein Parameter anhand dieser Ergebnisse verändert.

Alle24 möglichen Neuverpaarungen der vier oberen Partnerblätter in Lage20 wurden vollständig berechnet. Die Werte bleiben wegen der Kapazitätslücke diagnostisch:

|Leser|Beobachteter Mittelwert|Exakter Nullmittelwert|Zentrierter Wert|Referenzrang, inklusiv|
|---|---:|---:|---:|---:|
|IT2a|−0.000878291808|−0.000015195930|−0.000863095878|20/24 =0.833333|
|ZL3b|−0.000732533905|−0.000051389647|−0.000681144258|22/24 =0.916667|
|RF1b|−0.000465094515|+0.000033208831|−0.000498303346|24/24 =1|

Auch die Richtung ist hier nicht positiv. Daraus wird aber keine globale Abwesenheit eines Effekts abgeleitet. Die feste Kapazitätsentscheidung hat Vorrang. Alternative Leser sind keine unabhängigen Handschriften oder Bestätigungen. Die registrierten Spearman-Diagnostiken stehen vollständig in `artifacts/DIAGNOSTICS.json`; sie liefern keine Rettungsregel. Selbst ein positives Ergebnis könnte durch serielle Gradienten, Inhalt, Materialeigenschaften oder unbeobachtete Schreibvariation entstehen.

## Nachvollziehbarkeit und Konsequenz

Die Vorregistrierung wurde am2026-10-03 um03:01:41UTC lokal fixiert, bevor diese Zielstatistiken berechnet wurden; ein öffentlicher Vorabzeitstempel wird nicht behauptet. Alle Eingabepins wurden vor dem Lauf geprüft. Der unabhängige Validator bestätigt14/14 Prüfgruppen, darunter sämtliche5284 Ereignisvorhersagen, alle nominalen Seiten und Doppelblätter, beide Ausschlussstufen sowie die vollständigen24-elementigen Referenzorbits je Leser. `PREDICTIONS.json` enthält jede angepasste Wahrscheinlichkeit samt Zählern und ursprünglicher Quell-ID. Zusätzliche nominelle Seiten außerhalb der endgültigen Prüfmenge sind ausdrücklich `diagnostic_only`; sie ändern weder Auswahl noch Ergebnis.

[CANDIDATE_TABLE.md](CANDIDATE_TABLE.md) enthält jedes behaltene Doppelblatt; `PAGE_RESIDUALS.json`, `SHEETS.json`, `QUIRES.json` und `NULL_SCORES.json` enthalten alle Beiträge. Der Lauf lässt GDT1155 sowie die früheren negativen Paralleltextbefunde unverändert. Ein Wiederaufnehmen braucht echte zusätzliche geometrisch und quellenmäßig geeignete Abdeckung oder einen eigenständig begründeten anderen Test; weniger Ereignisse pro Seite oder das Zusammenlegen ungleicher Strata wären nachträgliche Reparaturen.

**Keine Wortübersetzung, keine l=m-Gleichsetzung, keine kausale Herstellungserklärung und keine Signifikanzbehauptung.**
