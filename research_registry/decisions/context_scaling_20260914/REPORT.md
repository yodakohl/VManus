# Wiedereinstieg mit begrenztem Kontext

14. September 2026. Ausgeführte Verbesserung der Arbeitsweise auf ausdrücklichen
Nutzerauftrag. [Entscheidung vor Umsetzung](DECISION.md), [Ausgangsstand](BASELINE.json),
[konkrete Prüfwerte und Befehle](RESULT.json).

Der Einstieg ist jetzt fest begrenzt. `./vmanus-work context start` liefert
die aktuelle Route mit **3714 statt zuvor 15346 UTF-8-Bytes** verpflichtender
Route-plus-Wissenseinstieg-Lektüre. Diese Messung betrifft nur diese
Projektdokumente, nicht Tokens, Systemanweisungen oder den gesamten Gesprächskontext.
Themen- und Primärbelege kommen gezielt hinzu; ihre Prüfung bleibt erforderlich.

| Aufgabe | Umgesetzt und geprüft |
|---|---|
| Wiederaufnahme | Eine einzige aktuelle Route; acht obligatorische Felder für Phase, Status, Auftrag, letzte Entscheidung, Arbeitsdateien, Annahmen, konkreten nächsten Schritt und laufende Arbeit. Maximal 4096 Bytes/80 Zeilen; bisherige positive Struktur und aktuelle Stopps bleiben im Einstieg. |
| Fachwissen abrufen | `context topic Wortzusammensetzung` und 14 weitere Themen wählen vollständige Zeilen oder Blöcke der bestehenden Live-Dokumente. Größter aktueller Ausschnitt: 2520 Bytes; Grenze: 6000. Quellenzeile und Dateihash sind beigefügt. Keine zweite Sammlung wissenschaftlicher Zusammenfassungen. |
| Größenbegrenzung | `context topics` listet höchstens acht Themen pro Seite. Fehlende/mehrdeutige Abschnitte, zu große Ausgaben und nicht zugelassene Quellen scheitern sichtbar ohne Teilausgabe. `context check` prüft diese Verträge. |
| Ergebnisse behalten | Der Abschluss im bestehenden Dossier hält Prüfvertrag, beobachtete Konsequenz, Annahmen, verbleibende Alternativen, Entscheidungsfolge und Wiederöffnungsbedingung fest. `context topic closure` ruft diese Vorlage ab. Ledger und bewertete Registereinträge bleiben die vorhandenen Ablagen. |
| Fortschreiben | Die Route wird ersetzt, nicht chronologisch erweitert. Sachliche Änderungen gehen in das betroffene Dossier und gegebenenfalls die passende Wissenszeile; keine pauschale Migration aller Altversuche. Vor Kontextwechsel wird die genaue Übergabe aktualisiert. |

**Prüfung:** 19 Tests bestanden. Darunter ist eine isolierte Probe mit 1000
zusätzlichen künstlichen Archiv-/Registereinträgen: Einstieg und ausgewählter
Themenausschnitt bleiben bytegleich; ein Lesezugriff außerhalb der benötigten
Dokumente würde den Test scheitern lassen. Der vorhandene Test mit 10000
künstlichen Karten prüft weiterhin begrenzte, indexierte Registerseiten.
Weitere Fälle prüfen Quelländerungen, verwaiste Tabellenköpfe, doppelte oder
fehlende Selektoren, Übergabefelder, UTF-8-Grenzen, verbotene Pfade und Symlinks.
Das sind keine 1000 ausgeführten Manuskriptversuche und kein Test künftiger
wissenschaftlicher Entscheidungen.

Der alte Routentest erwartete überholte Formulierungen und großzügigere Grenzen.
Er wurde an den aktuellen Einstieg angepasst: kleinere Ausgabegrenzen;
Nullstand bestätigter Wörter, Sperren, aktuelle Stopps und Legacy-Schutz bleiben
geprüft. Ausführliche Zugangsinformationen werden im vorhandenen Scope-Dokument
geprüft. Die Wissens-Tabellenzeilen von Brief und Statuskarte sind unverändert;
ihre Einleitungen erklären nur den gezielten Abruf. Alte Experimente, die
Registerimplementierung und `vmanus-exp` wurden nicht verändert.

**Grenze und Entscheidung:** Die Abrufhilfe wird als regulärer Einstieg genutzt.
Sie validiert weder Wahrheit noch Vollständigkeit oder die richtige Bewertung
von Abhängigkeiten. 15 Themen sind eine Navigation, kein vollständiger Katalog
aller Versuche; weitere Themen werden über das vorhandene Register und ihre
Primärbelege erschlossen. Ein Dateihash beweist Quellenidentität, keine Bedeutung.
Es gab keine neue Lesung, wissenschaftliche Neubewertung, Manuskript-/Bildöffnung,
Reservefreigabe oder Außenkontakte. Kein Forschungskandidat wurde vorgewählt.

Reproduktion: `./vmanus-work context check` und der Testbefehl in `RESULT.json`.
Für spätere Stände benennt dieser Prüfbericht seinen Ausgangscommit und die
geprüften Dateihashes. Der Abschluss umfasst genau einen Ledger-Eintrag, einmalige
Metadatenaktualisierung und deren Prüfung. Veröffentlichung erfolgt erst nach
Prüfung des genau deklarierten Staging-Umfangs auf sensible/private Inhalte.
Der Aufgabencheck ist keine globale Freigabe anderer laufender Arbeiten.
