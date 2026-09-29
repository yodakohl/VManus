# GDT1094 — f25v vollständig erfasst, noch keine zusammenhängende Lesung

29. September 2026. Die drei historischen Plantago-Rezepte liefern konkrete
inhaltliche Alternativen. **Keine davon ist bisher eine vollständige Lesung
des Voynich-Absatzes.** Die ausgeführte Arbeit umfasst alle sieben Zeilen in
drei Transkriptionen, ihre Wiederholungen, die vorhandenen unveränderten
Wortstrukturmodelle und die Häufigkeiten im freigegebenen Korpus. Sie ist
explorativ; ein semantischer Kandidatentest wurde nicht erreicht. Das ist
weder eine Widerlegung der Rezepte noch eine Übersetzung.

## Zugriffsfehler berichtigt

f25v steht bereits in Zeile59 der bestehenden GDT631-Textfreigabe mit179
Selektoren. Die vorige Formulierung, vor einem Textzugriff sei eine neue
Zulassung nötig, war falsch. Die spätere reine Bildzulassung widerruft diese
Textfreigabe nicht. Der vollständige Absatz wurde nach der jetzigen
[Registrierung](PREREGISTRATION.md) per Selektorwache geöffnet. Frühere
Projektverarbeitung und das sichtbare Bild machen ihn zu exponierten Daten,
nicht zu einem neuen Prüfblatt. Die Freigabe selbst wurde nicht geändert.

## Alle drei inhaltlichen Alternativen

Die [Quellenkarte](../../../research_registry/decisions/f25v_plantago_source_packages_20260929.md)
nennt Primärstellen und Editionsgrenzen. Ihr Autor wählte keine Voynichwörter
und öffnete den Zieltext nicht. Die historische Pflanzenhypothese und das
Bild waren allerdings bereits bekannt. Die Textpakete sind kein unabhängiger
Nachweis für Plantago.

| Kandidat | Erforderliche vollständige Beziehung | Tatsächlicher Zielbefund | Widerspruch / Restfreiheit |
|---|---|---|---|
| SNAKE | Schlangenbiss; Kraut mit Wein zerstoßen; trinken; Linderung | Kein Textausdruck bindet bislang Wein, Material und orale Aufnahme nach einer erklärten Regel. | Nicht widerlegt; freie Rollenvergabe wäre keine erfolgreiche Lesung. |
| SCORPION | Skorpionstich; Wurzel auswählen und anbinden; Nutzen als überlieferte Überzeugung | Kein Textausdruck unterscheidet bislang Wurzel, Bindung und Berichtshaltung. | Nicht widerlegt; die Behauptungsart darf nicht still zur beobachteten Heilung werden. |
| DOG | Biss eines tollwütigen Hundes; Kraut zerstoßen; örtlich auflegen; Heilung | Kein Textausdruck bindet bislang Hund, Material und örtliche Anwendung. | Nicht widerlegt; bloße Umbenennung der für SNAKE geratenen Rollen entscheidet nichts. |

Unabhängige Bedeutungsbestätigungskapazität ist für alle drei **0**. Der
gesamte historische Plantago-Eintrag enthält26 Anwendungen, darunter viele
ohne Biss. Deshalb wären selbst „trinken“ oder „auflegen“ allein weder ein
Bissnachweis noch ein Pflanzenname. Kein Paket wurde aus seinen günstigen
Teilmerkmalen als Sieger ausgewählt. [Maschinenlesbare Tabelle](artifacts/CANDIDATES.tsv).

## Was der vollständige Text tatsächlich verlangt

| Lesung | Rohgruppen | Verschiedene Rohformen | Exaktes `daiin` | Unmittelbares `daiin daiin` |
|---|---:|---:|---:|---:|
| ZL3b |60|45|11|1|
| IT2a |57|43|11|1|
| RF1b |59|47|9|0|

RF1b fusioniert in Zeile3 `shcfhordaiin` und trennt in Zeile5 `d aiin`.
Das erklärt hier die abweichende exakte Zählung, ohne die Lesung zu reparieren.
Alle Zeichenmarkierungen, Leerstellen und Absatzflags bleiben in der
[Rohprojektion](src/TARGET_RAW.tsv). Die [vollständige Zeilentabelle](artifacts/FULL_PASSAGE.tsv)
und das [Forminventar](artifacts/FORM_INVENTORY.tsv) lassen keine Stelle weg.

Die ZL3b-Folge lautet:

| Zeile | Vollständige Rohgruppen |
|---|---|
|1|`poeeaiin qo ky shy daiin qopchey otchey qofchor sos`|
|2|`dchor cthor chor daiin s okeeaiin daiin ckhey daiin`|
|3|`orcho kchor chol daiin sh[cfh:ckh]o r daiin dshey daiity`|
|4|`qokaiin qokcho shol daiin ckhear ckhol daiin chkear`|
|5|`dar chokeey dshor dshey qochol dol cho daiin daiin`|
|6|`qokcho r ochy qotchy qotoral cho @147; chain deeaiir s`|
|7|`o{c'o} chkey daiiol daiin shckh orchaiin`|

`chor daiin`, `chol daiin`, `shol daiin` stehen in Zeile2–4 in allen drei
Lesungen. Das erlaubt einen parallelen formalen Rahmen, aber keine
Benennung als Schlange/Skorpion/Hund. Unter bloßer Vergabe dieser drei
Namen blieben sechs Zuordnungen möglich; keine liefert von selbst die
übrigen Gruppen oder die unterschiedlichen Zubereitungswege. Dieser
Gedanke wurde deshalb nicht als sechs erfolgreich geprüfte Lesungen gezählt.

`qokcho`, `dshey` und `cho` wiederholen sich je zweimal. Eine vorgeschlagene
Zubereitungshandlung müsste beide Vorkommen mit derselben Regel erklären.
Ein einfaches universelles `daiin` als Trenner ausschließlich nichtleerer
Felder hätte zudem das bekannte Problem der unmittelbaren Doppelung.
Das ist eine Anforderung an eine künftige Konstruktion, kein neuer Test
gegen sämtliche grammatischen Lesarten. GDT764 und IDEA53 enthalten bereits
verwandte Feldfragen; ihre hypothetischen Werte werden nicht als Wissen geerbt.

Die [Profile](artifacts/PROFILE_SUMMARY.tsv) berücksichtigen den gesamten
freigegebenen179-Seiten-Korpus: `daiin` ist in ZL3b717-mal auf169 Seiten
belegt; `chor`189-mal auf97, `chol`338-mal auf124 und `shol`161-mal auf86.
Diese Zahlen beweisen keine Wortart. Sie verhindern aber, die Formen nur
wegen dieser einen Abbildung als seltene Tier- oder Pflanzennamen zu bevorzugen.
`ckhear` und `chkear` kommen dagegen jeweils nur einmal vor; sie besitzen
keine zusätzlichen exakten Vorkommen zur Prüfung einer geratenen Bedeutung.

## Vorhandene Wortgrammatik ausgeführt

Die unveränderten GDT1051-Funktionen wenden GDT012/062 und die64 eingefrorenen
GDT605-Merges auf alle176 Gruppen an:169 reine Gruppen sind formal zerlegbar;
aus169 harten Chunks bleiben162 ohne editorielle Unsicherheit. Keine der
beiden Zerlegungen wird zum universellen Morphemparser erklärt.

| Form | GDT012/062: äußerer Teil; verbleibender Host; rechte Familie |
|---|---|
|`chor`|`ch`; `or`; NONE|
|`chol`|`ch`; `ol`; NONE|
|`shol`|`sh`; `ol`; NONE|
|`qokcho`|`q`; `okcho`; NONE|
|`cho`|`ch`; `o`; NONE|
|`ckhear`|NONE; `ckhe`; `ar`|
|`chkear`|`ch`; `ke`; `ar`|

Gleiche sichtbare Endstücke oder ähnliche Schreibungen erlauben somit keine
stille Gleichsetzung. Insbesondere wird aus `qokcho` nicht durch eine alte
unveränderte Regel einfach `cho`. Diese Ausführung ist Nutzung vorhandenen
Wissens, kein neu entdecktes Bedeutungsmodell. Alle Ergebnisse stehen im
[formalen Replay](artifacts/FORMAL_REPLAY.json).

## Entscheidung

Den Ansatz „Bildvergleich plus eines dieser kurzen Rezepte“ vorerst als C0
behalten, aber nicht weiter durch frei erfundene Glossen ausbauen. Die
erforderliche ganze Lesung wurde nicht gefunden. Wiederaufnahme verlangt
eine explizite, zusammenhängende Konstruktion mit Argumenten und unveränderten
Wortwerten, oder eine Quelle mit einem zusätzlichen unterscheidbaren Verhältnis.
Eine bestätigte Anfangsglosse ist dafür weiterhin keine Voraussetzung.

Als nächste aktive Frage eignen sich die konkurrierenden Beziehungen zwischen
Tier und Pflanze: erkrankter Mensch nach Tierbiss, schützender Pflanzenverzehr
des Tiers oder schädliche Wirkung auf einen anderen Empfänger. Diese Rivalen
ändern die erwartete Handlung, nicht nur den geratenen Tiernamen. Die neuen
RAW-Karten744–746 enthalten Quellenansätze; vor Auswahl sind ihre Primärstellen
und die bestehenden Versuche gezielt zu prüfen.

Der Validator bestätigt vollständige Buchführung und deterministische
Wiedergabe, keine Bedeutung. Keine Signifikanzbehauptung; alle drei Leser
bezeugen dieselbe Handschrift. GDT1092/1093 bleiben unverändert negativ nach
ihren ursprünglichen Regeln. f84/f84r und Reserven bleiben geschlossen.

Arbeitszeit dieses Teilstücks: Beginn06:17:46UTC, Ergebnis und Validierung
um06:41UTC vorbereitet (rund24Minuten einschließlich Quellenarbeit,
Implementierung und Dokumentation). Veröffentlichung folgt im zugehörigen
Commit innerhalb des120-Minuten-Budgets. Das beendet weder den verlangten
20-Stunden-Zeitraum noch behauptet es dessen Ablauf.
