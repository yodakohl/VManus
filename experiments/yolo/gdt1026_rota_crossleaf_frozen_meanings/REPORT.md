# GDT1026: vollständiger anderer Blattkontext mit71 festen Musikbedeutungen

Die verneinende Fassung des vollständigen Absatzes f76v.37–41 ist mit beiden
bisherigen Absätzen f83r.25–30 und .31–44 unter allen zwölf festgehaltenen
Aufführungsbedingungen vereinbar. **18 alte Worttypen an32 neuen Positionen**
behalten dabei ihre Bedeutungen. Zusammen sind150 Positionen mit91 geratenen
Wortwerten beschrieben. Das ist eine vollständige bedingte Arbeitslesung über
zwei physische Blätter, keine bestätigte Musikübersetzung.

Die positive Schlussfassung widerspricht bei N3/N4 den ersten Einsätzen und
der bereits vorher im neuen Absatz angenommenen Prohibition. Bei N2 ist der
betroffene Quantor leer: vier rechnerisch verträgliche Fälle ohne Trennkraft.
Die zweite Transkription hat einen festen alten Wortkonflikt und ein unbekanntes
zusammengeschriebenes Wort; diese Fehler werden nicht als Varianten zugelassen.

[Alle150 Positionen mit Bedeutungen](artifacts/ALL_POSITIONS.tsv),
[alle18 wiederverwendeten Wörter samt Kontexten](artifacts/REUSED_WORDS.tsv),
[alle24 Kandidaten und Beobachtungen](artifacts/CANDIDATES.tsv),
[vorher veröffentlichte Vorhersagen](artifacts/PREDICTIONS.tsv),
[vollständige Klauselergebnisse](artifacts/ROWS.json),
[konkrete Ereignisreferenzen](artifacts/ENTRY_REFERENCES.tsv).

## Die vollständige neue Arbeitslesung

Die folgenden elf Aussagen entsprechen allen55 Wortpositionen, ohne ausgelassene
Zwischenstücke. Satzgrenzen, Wortwerte und Bezugsbindungen sind Hypothesen:

1. Für jeden nachfolgenden Sänger gilt das genannte Einsatzzeichen; nach Abschluss
   seines vollständigen Melodieumlaufs wiederholt er diesen unmittelbar.
2. Noch nicht eingetretene Kanonsänger schweigen.
3. Die obere Begleitstimme gehört zu den beiden Begleitstimmen.
4. Die obere Begleitstimme beginnt beim anfänglichen Einsatz des führenden Sängers.
5. Die untere Begleitstimme läuft bei den Einsätzen der späteren Nachfolger weiter.
   Ein solcher Sänger und sein unmittelbarer Vorgänger setzen nicht erstmals gemeinsam ein.
6. Erinnert sei an den gemeinsamen anfänglichen Beginn des Leiters und beider Begleitstimmen.
7. Das Einsatzzeichen gehört jeweils zur Melodie des unmittelbaren Vorgängers.
8. Die anfänglich wartenden Sänger schweigen bis zu ihrem jeweiligen ersten Einsatz.
9. Wenn der Leiter das Zeichen erreicht, schweigen die weiterhin wartenden Sänger.
10. Leiter und späterer Nachfolger dürfen keinen gemeinsamen ersten Einsatzzeitpunkt haben.
11. Beim Zeichen in der Melodie des Leiters gilt nochmals: kein gemeinsamer erster
    Einsatz des späteren Nachfolgers mit dem hier ausdrücklich bezeichneten Leiter.

Fassung V_POSITIVE verändert ausschließlich die Reichweite der geschriebenen
Negation: Der letzte Satz **fordert** dann den gemeinsamen ersten Einsatz.
Alle Wörter, Rollen, Ereignisse und Quellenbedingungen bleiben gleich.
Die Varianten wurden vor der Ausführung vollständig festgehalten.

## Tatsächliche Konsequenzen

| Fassung | N2, vier Rhythmusfälle | N3/N4, acht Rhythmusfälle | Entscheidung |
|---|---|---|---|
| V_PROHIBITIVE | übrige Bedingungen erfüllt; Schlussquantor leer | alle elf Klauseln erfüllt | bedingte Lesung erhalten |
| V_POSITIVE | übrige Bedingungen erfüllt; Schlussquantor leer | F11 widerspricht in allen acht Fällen | diese nichtleere positive Fassung verworfen |

Die konkrete Ereignisfolge bleibt R0 bei0, R1 bei12, R2 bei24 und R3 bei36
Brevis-Einheiten. Das ist die festgelegte relative Quellenrechnung, kein neu
gelesenes Zahlwort. Bei R2 liefert `r` im neuen Satz zuerst dessen Ereignis bei24,
danach das Ereignis seines Vorgängers R1 bei12; das spätere `r` mit ausdrücklich
genanntem Leiter liefert dessen Ereignis bei0. Alle drei Vorkommen benutzen
dieselbe Funktion FIRST_ENTRY_EVENT mit unterschiedlichen geschriebenen Argumenten.
`qokaiin` liefert die Zeit genau dieses Ereignisses, einmal für den Leiter und
einmal punktweise für das geschriebene Rollenpaar. Kein freier zweiter Zeitpunkt.

Die Begleitstimmen laufen unverändert weiter. In C0/C1/C3 beginnt der eigene
24er-Umlauf der unteren Stimme zufällig beim R2-Einsatz erneut; beim R3-Einsatz
steht er auf Phase12. Im unveränderten C2-Gegenfall hat die Begleitstimme eine
23er-Periode und steht an denselben Einsätzen auf Phase1 beziehungsweise13.
Beides ist mit CONTINUE vereinbar: Die eigene Uhr bleibt erhalten. Ein natürlicher
Umlaufwechsel darf nicht fälschlich als verbotener Einsatz-bedingter Reset gelten.
Alle Noten- und Pausenintervalle wurden vollständig geprüft, nicht nur diese Beispiele.

Die drei neuen `qoky`-Vorkommen bezeichnen dieselbe Gruppe noch nicht eingetretener
Kanonsänger. Beim Leiterzeichen ist R1 bereits eingetreten und gehört nicht mehr
zu dieser Gruppe. Die angenommene zeitliche Auswertung nach dem gemeinsamen
Ereignisstapel ist ausdrücklich eine neue Bindungsannahme; kein Wort wurde umgedeutet.

Bei N2 ist NEXT_FOLLOWER=R2.. leer. F05, F10 und F11 haben dann jeweils null
Instanzen. Diese Grenze wurde vor der Ausführung aus der ursprünglichen C08-Regel
übernommen. Sie ist keine nachträglich erfundene Leiter-Ausnahme. Die beiden
Endfassungen bleiben dort ununterscheidbar. In den übrigen Fällen ist F11 der
einzige neue Widerspruch der positiven Fassung. Weil bereits F10 dieselbe
Ereignisgleichheit verbietet, ist diese Trennung teilweise eine interne
Konsistenzprüfung unserer geratenen Grammatik; sie bestätigt die Musikquelle nicht.

## Reale Textgrenzen und Kosten

Die ZL-Zeilen37–40 behalten ihre vier unsicheren Zulässigkeitsflags; nur Zeile41
ist im alten Absatzpaket vollständig anchor-eligible. Die tatsächlichen IT-Zeilen
bilden ebenfalls einen ganzen Absatz, jedoch mit54 Gruppen:

- IT.38 schreibt `lolsaiiin` statt `lol saiiin`. Der geschlossene91-Wort-Vorrat
  enthält diese ganze Form nicht. Es gibt keine neue Zerlegungsregel.
- IT.39 schreibt `sar` statt `sor`. `sar` bedeutet im **festen hypothetischen**
  alten Wörterbuch ANY_ROTA_SINGER, `sor` INITIALLY. Die neue F08-Konstruktion
  verlangt INITIALLY und nimmt den anderen alten Wert nicht an.

Damit existiert keine vollständige IT-Lesung unter dieser festen Grammatik.
RF1b liefert im bereits gebundenen Paket keine eigenen Absätze. Die vier älteren
diplomatischen GDT1024-Lücken und dessen tatsächlicher IT-`solchedy`-Konflikt
bleiben zusätzlich bestehen. [Vollständiger Variantenbefund](artifacts/DIPLOMATIC_SCOPE.json).

Zwanzig neue Werte belegen23 Stellen;18 dieser neuen Werte kommen nur einmal vor.
Elf neue Konstruktionen und zehn Bindungskonventionen wurden an den exponierten
Absatz angepasst. Darunter fallen dieselbe Aufführung über zwei Blätter ohne
eindeutiges Bindewort, mehrere neue Synonyme, unausgeschriebene Mitgliedschaft
beziehungsweise Begleitstimmen-Startfunktionen, die Übernahme des Rollenquantors,
eine vorwärts gerichtete Leiterreferenz und die ausgedehnte Negation. CO_ONSET
und TOGETHER wiederholen hier dieselbe Aussage; das sind keine zwei unabhängigen
Belege. Die konkreten Kosten stehen unverändert in src/SOURCE.json.

Der Absatz wurde über die vorher getrennt festgelegte RAW490-Anteilsrangliste
gefunden:649 andere Blattabsätze,153 zulässige Kandidaten auf49 Blättern, vollständige
Top12 unabhängig nachgerechnet. Der frühere RAW489-Sieger f111r mit207 unbekannten
Typen bleibt als eigener Auswahl- und Lückenbefund erhalten. Es wurde nicht aus
den24 Resultaten ein günstiger Absatz gewählt. Inhaltlich blind war die neue
Lesung dennoch nicht: Der Entwurf wurde nach Sichtung der bereits exponierten
Wörter erstellt. Verschiedene Blätter allein machen diese Auswahl nicht unabhängig.

## Prüfung und nächste Entscheidung

Die öffentliche Registrierung `ab17e8c15` lag vor der Ausführung am2026-09-21
um05:42:47UTC. Alle24 Vorhersagen stimmen. Beide alten vollständigen Absätze
wurden mit unveränderten Werten erneut gebunden. Die zwölf ganzen ursprünglichen
Aufführungsspuren wurden durch den alten unabhängigen arithmetischen Codepfad
regeneriert; alle27775 Intervalle stimmen. Ein separater neuer Prüfer kontrolliert
die Relationen und eine umgekehrte Erkennung alle55 Positionen. Beide Prüfer
stammen vom selben Autor. Die Zahl der Intervalle ist Prüfungsumfang, keine
Zahl neuer Manuskriptbeobachtungen.

Vor Registrierung bestanden24 erfundene Modellfälle, elf ausgelassene Produktionen
und sechs Typprüfungen. Eine anfänglich falsche synthetische Erwartung zu einem
Reset bei leerem N2-Bereich wurde vor Sperrung korrigiert; wissenschaftliche
Werte und Ergebnisdateien wurden damit nicht repariert. Nach der Ausführung
blieben sämtliche gesperrten wissenschaftlichen Dateien unverändert.

Die bedingte150-Gruppen-Lesung erhalten; diese konkrete positive Schlussfassung
für N3/N4 verwerfen. Kein Rhythmuszweig wird gewählt. Es fehlen weiterhin eine
eigenständige Bedeutungsbindung, eine Kontrolle der gesamten Suche und eine
manuskripteigene Verbindung zur angenommenen Notenquelle. **Bestätigte Wörter0,
unabhängige Bedeutungsbestätigungskapazität0.** Keine Signifikanzbehauptung.
Keine neue Seite, Quelle, Abbildung oder Reserve wurde geöffnet, niemand kontaktiert.
f84/f84r bleiben versiegelt und f116v unzugelassen.

Ein nächster Ausbau muss die zusätzliche Bedeutung mit weniger freien
Konstruktionen tragen oder eine andere vollständige Lesung auf ebenso feste
Wortwiederverwendung prüfen. Noch eine frei formulierte Wiederholung derselben
Musikregeln hätte wenig zusätzlichen Erkenntniswert.
