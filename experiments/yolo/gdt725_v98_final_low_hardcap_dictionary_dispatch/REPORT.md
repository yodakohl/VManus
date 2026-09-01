# GDT725 — V98 schließt die letzte Hardcap-Auditliste

Status: PASS_V98_16_FINAL_LOW_HARDCAP_READINGS_AUDITED__21_POSITIONS__9_CORE_OR_STRUCTURAL_REPAIRS_PLUS_7_RETAINED__5_STRUCTURAL_READINGS_SEPARATED__4_ACTION_WHOLES_RETAINED__72_EVIDENCE_BINDINGS__0_UNAUDITED_HARDCAP__NO_COMPONENT_EXPORT_NO_SCORE_CREDIT__ALL_H0_NONE

## Ergebnis

Die letzte offene Auditliste ist bearbeitet: 16 Lesarten an **21** Stellen in
18 Zeilen. Die frühere Nebenrechnung mit 20 Stellen war falsch; `oror` kommt
dreimal, `dy#2` zweimal und `y#2` dreimal vor. Neun Wörterbuchdefaults oder
Strukturangaben werden repariert, sieben konkrete Ganzwortwerte bleiben.

| Form | V98-Wörterbuchdefault | lokale Ausgabe | Entscheidung |
|---|---|---|---|
| aiijy | in drei Bündel abfüllen und schließen | den vorstehenden Anteil in drei Bündel abfüllen und schließen | bestätigt |
| chpcheey | nachgetrocknetes Pulver, Form II | gleich | bestätigt |
| cpheesy | vollständig bereitetes und abgeschlossenes Kompositum | vollständig bereitetes und abgeschlossenes Arzneikompositum | revidiert |
| da | eine Teilmenge abmessen | vom vorstehenden heißen Material eine Teilmenge abmessen | bestätigt |
| dy#1 | [STRUKTUR: SATZSCHLUSS] | `.` | revidiert |
| dy#2 | [STRUKTUR: ARBEITSSCHRITT-TRENNER] | `;` | revidiert |
| kodeey | vollständig erhitzte und abgeschlossene Dosis | vollständig erhitzte und abgeschlossene Zubereitungsdosis | revidiert |
| oror | zwei Portionen | gleich an drei Stellen | bestätigt |
| otytchol | nachgekühlter Trockenstoff | nachgekühlter Trockenstoff im Ansatz | revidiert |
| qy | hiervon nehmen | gleich | bestätigt |
| taiky | kalt angesetzte Charge, leicht angewärmt | gleich | bestätigt |
| tail | kaltgestellter Materialanteil II | kaltgestellte Rohdroge II | revidiert |
| y#1 | [STRUKTUR: SATZSCHLUSS] | `.` | revidiert |
| y#2 | [STRUKTUR: ANSCHLUSS AN FOLGENDEN POSTEN] | `Hierzu:` bei Zugabe, `Anschließend:` vor einem Folgezustand | revidiert |
| yey | [STRUKTUR: FORTSETZUNG DES VORSTEHENDEN POSTENS] | `anschließend:` | revidiert |
| ypchesy | hiervon Samenpulver bis zur Mittelstufe trocknen | gleich | bestätigt |

## Warum die vier Aktionswerte nicht entleert wurden

Ein pauschales Kürzen aller Verben wäre hier falsch gewesen. `da` stammt aus
einer elf Kontexte umfassenden Teilungs-/Dosisfunktion, `qy` aus vier
Entnahme-/Referenzkontexten. `aiijy` und `ypchesy` sind zwar Einzelbelege, ihre
GDT681-Ganzkarten sind aber ausdrücklich aktionslizenziert. Deshalb bleiben
die konkreten Verben im exakten Ganzwortdefault. Verboten bleibt nur der
Schritt von diesen Ganzwörtern zu freien Werten wie `q = nehmen` oder
`y = schließen`.

## Was bei y und dy jetzt wirklich im Wörterbuch steht

Punkt und Semikolon sind Renderer, nicht angeblich gesprochene Wörter. V98
speichert darum eine eigene Funktionsebene:

- `dy#1` und `y#1`: `[STRUKTUR: SATZSCHLUSS]`, Ausgabe `.`
- `dy#2`: `[STRUKTUR: ARBEITSSCHRITT-TRENNER]`, Ausgabe `;`
- `y#2`: `[STRUKTUR: ANSCHLUSS AN FOLGENDEN POSTEN]`, Ausgabe `Hierzu:` oder
  vor einem reinen Folgezustand `Anschließend:`
- `yey`: `[STRUKTUR: FORTSETZUNG DES VORSTEHENDEN POSTENS]`, Ausgabe
  `anschließend:`

Damit erhält jede Sequenz einen Default, ohne Satzzeichen als deutsche
Lexeme zu verkaufen. Die fünf Werte bleiben W0 und positionsgebunden.

## Stärkste und schwächste konkrete Aussagen

`oror = zwei Portionen` ist die stärkste Invariante dieser Runde: drei aktive
Stellen auf drei Seiten plus die ältere Quellkarte. `da = eine Teilmenge
abmessen` und `qy = hiervon nehmen` besitzen breitere Quellkontexte, aber
Leser- und Imperativ/Etikett-Rivalen bleiben offen.

Am schwächsten bleiben `taiky`, die Leserpolarität von `tail`, die genaue
Gebindeart bei `aiijy` und Samen gegen Wurzel bei `ypchesy`. Sie behalten
dennoch einen praktischen Default, weil die Gegenmodelle sie nicht klar
unmöglich machen.

## Renderer-Nachprüfung

Die manuelle Zeilenprüfung fand drei Darstellungsfehler, ohne einen neuen
Wortwert zu benötigen. Auf f86v3.13 und f86v6.5 werden die schon in V97
gebundenen Spannen B001 und B002 nun tatsächlich je einmal ausgeführt:
`drei Portionen des Anteils I des heißen Holzansatzes` beziehungsweise
`Anteil I des heißen Holzansatzes; drei Portionen davon`. Die beiden
Spanmitglieder erscheinen nicht noch einmal einzeln.

Auf f76v.10 war der ältere lokale GDT686-Kopf auf das unbrauchbare Fragment
`drei` reduziert worden. Die Zeile gibt nun wieder `drei Portionen des
vorstehenden eingeweichten Arzneikompositums` aus. Das ist ausdrücklich eine
einmalige Zeilenausgabe: `daiin#6` bleibt im Wörterbuch `Wert III`, Score und
Confidence bleiben unverändert und weder `Portion` noch `Arzneikompositum`
werden als Komponentenwert exportiert. Die 72 primären Zielbindungen und die
eine zusätzliche Companion-Quellbindung werden getrennt gezählt.

## Bestand

- 16 Lesarten / 21 Stellen / 18 Zeilen / 17 Seiten
- 9 Revisionen / 7 geprüfte Beibehaltungen
- 5 getrennte Strukturlesarten / 4 exakte Aktionsganzwörter
- 72 replaybare primäre Evidenzbindungen plus 1 Companion-Quellbindung / 48 Rivalenreihen
- 2 bestehende gebundene Spannen in Zielzeilen einmalig ausgeführt / 1 reine Zeilenreparatur
- 324 aktive Lesarten / 479 Positionsausgaben
- 1.586 Wörterbuchlesungen / 1.582 Oberflächen
- Confidence unverändert: 7 W0 / 135 W1 / 163 W2 / 19 W3
- **0 unaudierte Hardcap-Lesarten**, aber weiterhin 16 niedrige W0/W1-Werte
- 0 neue Komponentenexporte / 0 Scorepunkte / alle H0_NONE

Keine neue Seite, kein Bild, keine Transkription und weder f84 noch f84r
wurden verwendet. Das Ergebnis ist die derzeit vollständig auditierte
Arbeitsausgabe, keine identifizierte historische Übersetzung.

## Nächste Route

Nicht noch einmal dieselben 16 Karten kürzen. Als Nächstes muss der Renderer
die 18 betroffenen Zeilen und anschließend die vollständigen 51 Arbeitszeilen
aus Strukturmarken, Aktionsganzwörtern und Nominalblöcken zu lesbaren
Abschnitten setzen. Dabei bleiben alle V98-Defaults fest; geändert werden nur
Satzgrenzen, Bezugsauflösung und die einmalige lokale Einfügung sichtbarer
Patienten.
