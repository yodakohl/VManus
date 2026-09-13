# W55 — Vier ältere Körperpräferenzen auf unterscheidende Folgen geprüft

**Keine der vier vollständigen GDT590-Passagen liefert einen unabhängig gebundenen menschenspezifischen Zustand.** Ein konkreter zusätzlicher Befund betrifft den hervorgehobenen lokalen Wortvergleich: `cheey` gegen `lsheey` isoliert auf der gespeicherten Zeichenebene nicht den Beitrag von `l`. Zwei Änderungen sind nötig: `l` hinzufügen und `c` durch `s` ersetzen (also `ch` zu `sh`) (Zeichen-Levenshtein 2). Ein reiner Präfixvergleich wäre `cheey/lcheey` oder `sheey/lsheey`; ein solcher Vergleich wird hier nicht als gefunden behauptet.

Das widerspricht nicht der technischen GDT590-Zerlegung, die verschiedene ganze Formen über gesetzte Aktions-/Gradklassen vergleicht. Es begrenzt ihre Verwendung als unabhängigen Beleg für die Bedeutung eines Bausteins. Der alte Bericht nennt den Kontrast ein lokales Minimalpaar; auf der unveränderten Ganzwort-Zeichenebene ist er kein reiner l-Kontrast. Keine Transkriptionsregel oder historische Datei wurde geändert.

| Stelle | Bisherige Körperbegründung | Ebenfalls mögliche Stationsfolge | Was zur Unterscheidung fehlt |
|---|---|---|---|
| f77r.10, E2404 | Nach Stationsvorbereitung kann das Badeobjekt zum Körper wechseln. | Derselbe Stationsansatz wird weiter behandelt. | Ein unabhängig geschriebener Teilnehmerwechsel; vorhandene Analoga tragen schon gesetzte Körperglossen. |
| f77r.39, E2637 | `cheey` gilt als Körper, späteres `lsheey` als Station. | Verschiedene Operations-/Relationsformen am Stationsansatz. | Reiner Bausteinkontrast und davon unabhängige Identifikation des Trägers. `cheey/lsheey` verändert zwei Bestandteile. |
| f77r.41, E2652 | Bloßes `sh` mit entferntem AIIN/Y erlaubt Körperwechsel. | Station bleibt Objekt. | Laut Primärbericht kein exaktes bloßes-SH-Körperminimalpaar; Wechsel nur erlaubt, nicht verlangt. |
| f82r.1, E3182 | Körperbad Grad II, dann Grad I ergibt eine zweistufige Folge. | Dieselben beiden Grade am Stationsansatz. | Eine körperexklusive Folge und gesicherte Gradbedeutung. Grad II/I ist hier nicht unabhängig als Temperatur erkannt. |

PASSAGES.tsv enthält alle vier vollständigen gespeicherten Oberflächen und die einzeln beurteilten Voraussetzungen. Die vollständigen deutschen Modellpassagen bleiben in GDT590_FOUR_BATH_READER.md, per Hash gebunden. Kein Ziel ist laut Primärbericht ein explizites Figurenlabel. GDT590 bevorzugte drei der vier Wortpositionen bildlich sogar eher bei Station/Apparat; diese Nähe war ausdrücklich kein Wortbeleg.

## Entscheidung

GDT590s Körper-first-Regel bleibt eine historische Arbeitspräferenz. Ihre 52/92 Körperzuweisungen sind kein unabhängiger Körpernachweis, weil die Klassifikation aus dieser Regel entsteht. Sie liefern keinen neuen Grund, P07 oder W41 unverändert zu wiederholen. Alle vier Alternativen bleiben offen; keine Körperempfindung, Reaktion oder Heilung wurde identifiziert.

Für die vom Nutzer gewünschte Bausteinsuche ist die konkrete Konsequenz: Aus diesem lokalen Paar darf kein isolierter Wert für `l` abgeleitet werden. Ein kontrollierter Vergleich müsste die jeweils anderen Änderungen ebenfalls abdecken und seine Rollenbindung unabhängig prüfen. W55 hat einen solchen Korpusvergleich nicht ausgeführt und behauptet weder sein Fehlen im gesamten Manuskript noch seine Neuheit gegenüber allen früheren Mustertests. Es wird kein automatischer Folge-Decoder gestartet.

## Umfang und Reproduktion

2026-09-13. Nach Exposition deklarierter Audit, kein blinder Versuch. Ausschließlich GDT590s vier bereits exponierte vollständige Modellpassagen sowie REPORT/METHOD geprüft. Keine neuen Bilder, gemischten Transkriptionsquellen oder reservierten Seiten geöffnet. f84/f84r geschlossen. Der frühere Projektkontakt mit diesen Seiten und der dokumentierte, damals verworfene GDT674-Guard-Vorfall verbieten einen projektweiten Blindheitsanspruch.

`audit.py` erzeugt die vollständige Vierer-Tabelle und den exakten Zeichenvergleich. Die semantischen Einschätzungen darin sind manuell verfasst. `validate.py` prüft Abdeckung, Quellenhashes und den Zeichenvergleich; keine automatische Bedeutungsvalidierung. Kein Signifikanzanspruch und kein bestätigtes Wort. Dies ist ein Befund über die Tragfähigkeit vorhandener Hypothesen, keine neue Entzifferung.

Validierung: Register PASS. Global unverändert acht bekannte Altfehler (sieben GDT600-Dateibindungen, veralteter Index); nicht in diesem Audit repariert.
