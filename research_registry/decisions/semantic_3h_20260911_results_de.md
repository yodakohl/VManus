# Ergebnisse des Forschungsfensters am 11. September 2026

Angefordertes Arbeitsfenster: 14:27:58–17:27:58 UTC (16:27:58–19:27:58 Wien).
Letzte beobachtete aktive Uhrzeit am 11. September: 17:27:41 UTC. Fortsetzung
am 12. September ab 10:19:42 UTC; die Nachtpause zählt nicht als Forschungszeit.
**Bestätigte Übersetzungen: 0.**

## Zwei konkrete Ergebnisse, die erhalten bleiben

**1. Bekannte Wortpaare wechseln ihre Endungen gemeinsam.**
GDT915 bestimmte auf ungeraden physischen Blättern 22 geordnete Stammpaare und
prüfte dieselbe vollständige Liste auf geraden Blättern. Dort stehen in ZL3b
43 Paarvorkommen mit gleicher r/l-Endung 21 gemischten gegenüber, verteilt auf
25 Blätter. Beispielsweise erscheinen `cheor chor` und `cheol chol`. Der
blattweise gewichtete Wert beträgt 0,0293135 gegenüber durchschnittlich
0,0055632 im festgelegten bedingten Vergleich. Drei von 1024 Vergleichswelten
erreichen den beobachteten Wert; in jeder wird auch die Kandidatenauswahl neu
berechnet. Das ist keine Signifikanzbehauptung über die gesamte Projektsuche.

Die vollständige Tabelle enthält auch fünf Kandidaten ohne Übertragung und
alle gemischten Formen. In GDT916 zeigt sich keine belastbare Verallgemeinerung
auf neue Kombinationen: 468 Vorkommen von 411 zuvor nicht gesehenen Paaren,
255 gleiche gegenüber 213 gemischten Endungen; 449 von 1024 Vergleichswelten
erreichen das Ergebnis. Deshalb bleiben „grammatische Übereinstimmung“,
„Einzahl/Mehrzahl“, „Kasus“ und andere Bedeutungen unbestätigt.

Quellen und vollständige Tabellen:
[GDT915](../../experiments/yolo/gdt915_terminal_lr_phrase_transfer/REPORT.md),
[GDT916](../../experiments/yolo/gdt916_unseen_lr_stem_pair_transfer/REPORT.md).

**2. Ein vollständiger Absatz ist mit zwei unveränderten lateinischen Wortwerten vereinbar.**
GDT923 behielt alle 26 bedingten Wortwerte aus GDT893 unverändert und prüfte
sämtliche nach der alten Regel zulässigen vollständigen Absätze auf geraden
physischen Blättern. Es wurden keine unbekannten Wortwerte ergänzt, Quellen
gewechselt oder Regeln für die Transkription verändert.

In ZL3b auf **f106v.26–27** bleibt genau ein 17-Wort-Fenster im alten
Quellenbestand vereinbar mit:

| Voynich-Form | Unveränderter lateinischer Kandidatenwert | Position im Absatz, ab 1 gezählt |
|---|---|---:|
| `lchedy` | `sed` | 6 |
| `qokeey` | `de` | 16 |

Die übrigen 15 Wörter bleiben unübersetzt. Der Vergleichsort ist
`ALIM:213:segment:0002`, Start18 bei Zählung ab null. Die Eindeutigkeit gilt
nur innerhalb dieses Quellenbestands und der festgelegten Annahmen. Eine
unabhängige Bedeutungsbestätigung fehlt. Die anschließende vollständige Bildprüfung
GDT924 bestätigt zudem nicht alle17Schriftformen: sechs stimmen in beiden
Lesungen überein, elf bleiben unsicher, darunter lchedy. Es wird keine Ersatzlesung eingesetzt.

Die maßgebliche RF-Lesung liefert keinen Absatz mit mehreren vereinbaren
bekannten Wortwerten. Ihr einziger Absatz mit mindestens zwei bekannten
Worttypen hat bereits vor Anwendung der Werte kein passendes
Wiederholungsmuster im Quellenbestand; das kann den Wortschlüssel nicht
isoliert widerlegen. Der RF-Absatz f108r.35–36 mit nur `chedy → et` passt zu
**250 verschiedenen geschriebenen Quelltexten**. IT2a hat 34 Absätze mit
mindestens zwei bekannten Worttypen und passenden Wiederholungsmustern;
keiner davon übersteht den unveränderten Schlüssel. Die Lesungen sind keine
unabhängigen Manuskripte. Kein Kandidat erhält eine Bestätigung über beide
vorher festgelegten geraden Blattgruppen hinweg.

[Alle 26 Kandidaten und alle Absatzfälle](../../experiments/yolo/gdt923_fixed_word_key_even_paragraph_compatibility/CANDIDATE_TABLE.md),
[Vorhersage an jeder Wortposition](../../experiments/yolo/gdt923_fixed_word_key_even_paragraph_compatibility/artifacts/PREDICTIONS.tsv),
[Bericht mit Auswertung und Grenzen](../../experiments/yolo/gdt923_fixed_word_key_even_paragraph_compatibility/REPORT.md).

## Alle zehn abgeschlossenen Versuche

| Versuch | Tatsächlich geprüft | Ergebnis und Entscheidung |
|---|---|---|
| [GDT915](../../experiments/yolo/gdt915_terminal_lr_phrase_transfer/REPORT.md) | Alle 22 zuvor bestimmten r/l-Paare auf anderen physischen Blättern | Bedingte Kopplung bekannter Wortpaare bleibt erhalten; keine Wortbedeutung. |
| [GDT916](../../experiments/yolo/gdt916_unseen_lr_stem_pair_transfer/REPORT.md) | Neue Paarungen bereits bekannter Stämme | Verallgemeinerung nicht bestätigt; feste r/l-Testfolge beendet. |
| [GDT917](../../experiments/yolo/gdt917_diminishing_charm_complete_chain/REPORT.md) | Vollständige elfgliedrige Verkürzung von „abracadabra“, zwei festgelegte Anordnungen | Kein vollständiger Treffer in einer der drei Lesungen; keine Teilketten nachträglich ausgewählt. |
| [GDT918](../../experiments/yolo/gdt918_reciprocal_center_serial_transfer/REPORT.md) | Umkehrbare Dreiergruppen als Kandidaten für verknüpfende Wörter | Kein Kandidat erfüllt die primäre Mindestabdeckung; Übertragungsinhalte nicht ausgewertet. |
| [GDT919](../../experiments/yolo/gdt919_complete_sator_word_equations/REPORT.md) | Alle vollständigen fünfteiligen Sator-Gleichungen unter den festen Regeln | Keine Lösung in einer der drei Lesungen; Formelzweig beendet. |
| [GDT920](../../experiments/yolo/gdt920_paragraph_gallows_wholeform_bridge/REPORT.md) | Zwei feste p/f→k/t-Abbildungen zwischen Absatzanfang und Absatzkörper | Beide Effekte in allen Lesungen negativ gegenüber dem Vergleich; keine Wortidentität bestätigt. |
| [GDT921](../../experiments/yolo/gdt921_royal_seasons_two_register_topology/REPORT.md) | Historische Vergleichszeichnung Royal19CI54v: vier Jahreszeitenfiguren und zwei Beschriftungsreihen | Zwei Beobachter bestätigen die Anordnung. Vollständige mutmaßliche Datumswerte und eindeutige Zuordnung der Speichen bleiben offen. Kein Voynich-Wort getestet. |
| [GDT922](../../experiments/yolo/gdt922_identical_remainder_chsh_order/REPORT.md) | Reihenfolge benachbarter chR/shR-Formen bei identischem Rest R, ohne die bekannten or/ol-Fälle | 49 primäre Paare, sieben vorwärts/acht rückwärts; keine Reihenfolgeregel bestätigt. |
| [GDT923](../../experiments/yolo/gdt923_fixed_word_key_even_paragraph_compatibility/REPORT.md) | Alle unveränderten 26 Wortwerte gegen vollständige Absätze anderer Blätter und denselben Quellenbestand | Ein bedingter ZL-Vergleich bleibt erhalten; keine informative RF-Übertragung und kein bestätigtes Wort. |
| [GDT924](../../experiments/yolo/gdt924_f106v_fixed_candidate_native_audit/REPORT.md) | Direkte Bildprüfung aller17Wörter des f106v-Kandidaten durch zwei getrennte Leser | Beide finden11+6Gruppen; sechs gemeinsam passend, elf unsicher, keine gemeinsame Gegenlesung. qokeey passend, lchedy unsicher; vollständiger Kandidat bleibt nativ unbestätigt. |

Für die ausgeführten Textprüfungen wurden die vollständigen Ergebnisse unabhängig
nachgerechnet. GDT921 hat zwei getrennte Bildbeobachtungen und eine Prüfung der
Quellen- und Ergebnisdateien; diese Dateiprüfung bestätigt keine unsicheren
Bildlesungen. Alle materiellen Ergebnisse, Registrierungen, Programme und
kompakten Reproduktionsdaten sind veröffentlicht. GDT923 bewahrt auch sämtliche
90.891 verbleibenden Quellstellen, einschließlich der wenig einschränkenden
Fälle mit null oder einem bekannten Worttyp.

## Überprüfung noch offener Zugänge

Die letzten Prüfungen der Forschungsnotizen ergaben keinen weiteren ausführbaren
Bedeutungstest. Das ist keine Behauptung, alle möglichen Ansätze erschöpft zu haben.

- Die f1r-Randnotiz enthält in den gespeicherten unabhängigen Lesungen keine
  bestätigte mittlere EVA-Zuordnung; daraus lässt sich derzeit auch kein sicherer
  Teilschlüssel gewinnen. GDT912 bleibt unverändert.
- f37v–f102r1 ist bereits in FPR001/GDT152/GDT169 geprüft worden. Die vermeintlich
  übrigen Pflanzenpaare besitzen entweder keine einzelne zugehörige Beschriftung
  oder keine wiedergefundene Primärquelle. Eine gezielte Suche in der Git-Historie
  brachte die fehlende Quelle zu f43r–f101v nicht zurück.
- Bei den geprüften Ideen zu ausgelassenen Argumenten, Instrument/Endpunkt und
  Blütenmaterial fehlt der unabhängig beobachtete Bedeutungsunterschied. Alte
  Bedeutungsannotation und deren erneute Wiedergabe wären keine Bestätigung.

Die Entscheidung aus diesem Fenster lautet: die beiden konkreten Befunde oben
beibehalten, die negativen Konsequenzen nicht umdeuten, **keinen Wortwert als
übersetzt ausgeben**. f84/f84r blieben geschlossen. Für die abschließende Prüfung wurde f106v neu zugelassen: 49 Bildschlüssel/55
Selektoren, eine Bildzulassung verbleibt. Der separate globale Repository-Check behält seine
acht bekannten GDT600/Index-Fehlergruppen; die Aufgabenprüfungen für die
veröffentlichten Änderungen bestanden.

## Fortsetzung am 12. September

Die zusätzliche begrenzte Prüfung möglicher Folgeansätze ergab keinen neuen
ausführbaren Bedeutungstest. Geprüft wurden Verbotsformen, erklärende Fremdwörter,
kalibrierte Mengen, die senkrechte Zeichenfolge auf f76r und arithmetische
Beziehungen. Es kam kein neuer unabhängiger Bedeutungsunterschied hinzu.
Das ist eine Prüfung vorhandener Ansätze, kein neues Manuskriptergebnis und
keine Behauptung, alle denkbaren Lösungen ausgeschöpft zu haben. GDT925 wurde
nicht angelegt; die veröffentlichten Versuche bleiben unverändert.
