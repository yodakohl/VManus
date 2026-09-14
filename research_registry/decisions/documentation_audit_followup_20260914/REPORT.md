# Zweiter Dokumentationsaudit — Befunde, Glossen und tatsächliche Testgrenzen

2026-09-14. Auf ausdrückliche Bitte des Nutzers nach Fortsetzung des ersten
Audits. **Zwölf konkrete Themen sind jetzt mit Primärbefund, verbleibender
Grenze und Folge für Weiterarbeit erschlossen.** Vier zusätzliche operative
Lücken wurden behoben; die übrigen Zuordnungen bewahren bereits vorhandene
Unterscheidungen. Kein neuer Manuskriptbefund und keine neue Übersetzung.

Entscheidung vor Bearbeitung: [DECISION](DECISION.md). Der erste Audit und
sämtliche hier verwendeten alten wissenschaftlichen Quellen bleiben erhalten.

## Tatsächlich ergänzte Korrekturen

1. **GDT616 hatte keinen ausgewerteten Hauptstatus in der kompakten Karte.**
   `ideas show GDT616` zeigte `unreviewed` und den importierten Quellstatus
   `POST_TERMINAL_MINIMUM_GATE_RELAXATION_PASS`. Der ursprüngliche Vertrag
   scheitert laut Primärbericht exakt mit beiden Solvern; eine spätere Diagnose
   erlaubt vier verbotene Kindausgaben. Eine erste, append-only
   [Bewertung](REVIEW.json) klassifiziert ausschließlich den ursprünglichen
   synthetischen Vertrag als `refuted_specific_model`, Scope `method`.
   Der Importstatus bleibt als Historie sichtbar. Keine Veränderung am Versuch,
   keine Wiederberechnung und keine Widerlegung allgemeiner Komposition.
2. **Der neue Einstieg enthielt weiterhin nicht alle zuletzt wirksamen Stopps.**
   W96 parkt die f2v-Mengen-/Gradfassungen; W97 stoppt den festen
   Generationenentwurf. Beide stehen jetzt in der Route und werden über die
   Themenübersicht erschlossen. Das ist keine neue Entdeckung ihrer Fehler.
3. **„Human descriptions only“ widerspricht der späteren Arbeitsvorgabe.**
   HIGH_LEVEL_RESULTS enthält diese historische Regel. Die ausdrückliche
   Nutzerpräzisierung und ausgeführte native Bildbetrachtung stehen unter
   docs/visual_overview und W53. Die neue Anleitung macht sie zugänglich, ohne
   alte OCR-Verfahren zu rehabilitieren oder Modellbeobachtungen zu menschlicher
   Annotation und unabhängiger Bedeutungsprüfung umzubenennen.
4. **Die f77r-Brücke blieb als „strongest current“ in einer alten Synthese stehen.**
   Diese Priorisierung wird als historisch eingeordnet. Der post-hoc
   Strukturbefund, seine schon damals dokumentierten Wortzuordnungsgrenzen und
   der auf einen bestimmten Annotationenbestand begrenzte Kapazitätsstopp
   werden gemeinsam verlinkt. Es wurde keine spätere direkte Widerlegung der
   ursprünglichen fünf Grenzzuordnungen gefunden oder behauptet. Ein neuer
   geeigneter Bildvergleich ist ebenfalls nicht festgestellt.

## Bestehendes Wissen, das jetzt zusammen auffindbar ist

Die [Themen-/Statustabelle K01–K12](../../../docs/VOYNICH_CLAIM_STATUS_MAP.md)
enthält insbesondere:

- **Positive Variantenkenntnis:** GDT787s vollständiges Formenraster und die
  Grenze des dort getesteten additiven Bedeutungsrests. Die starke Formfamilie
  ist weder ein Suffixwörterbuch noch durch den Transferfehlschlag verschwunden.
- **Bedingte Rollenwerte:** GDT748s Übereinstimmung mit übernommenen HOT/END-
  Karten unterscheidet sich von unabhängiger Bedeutungsevidenz. Die alte
  Vollabdeckung und die v0.51-Glossen sind bereits in der Grammatik-Baseline
  eingeschränkt beziehungsweise unter Quarantäne gestellt; keine neue Rücknahme.
- **Genauer Musterumfang:** GDT793 betrifft ganze okal-Formen; GDT854 beobachtet
  e-Stellungsvariation, hat aber keine beidseitige Transferkapazität. GDT889,
  GDT910 und GDT914 prüfen drei andere, jeweils eng definierte Mechanismen.
  „Schon gemacht“ und „sämtliche Formvariation ausgeschöpft“ sind verschieden.
- **Erhaltene Übertragungsbefunde:** GDT858s Fehler bei Blattseiten-Ausschluss
  wurde in GDT865 für zwei primäre Modelle nachgerechnet; deren Schwellen halten.
  Die Korrektur hebt nicht jede Struktur auf und bestätigt nicht alle alten
  Nullmodelle oder Bedeutungen.
- **Mengen und Identitäten:** W94–W96 trennen eine algebraische Konsequenz der
  gesetzten Identitätsregeln von einem gelesenen Wert „eins“. Eine zusätzliche
  Modellfassung oder ein weiterer bekannter Selbstbezug ist nicht automatisch
  neue Forschungserkenntnis.
- **Begrenzte Kontrollleistungen:** GDT832 und GDT837 besitzen echte, konkret
  ausgewiesene Wiedergewinnungsleistungen auf Kontrolltexten. Ihre registrierten
  Gesamtentscheidungen bleiben negativ; jeweils bevorzugt das Optimierungsziel
  eine bekannte falsche Abbildung. Ein pauschales „Kontrollen brachten nichts“
  wäre ebenso falsch wie „98% Voynich übersetzt“.

Die Map ersetzt keine Primärberichte. Insbesondere enthält sie keine pauschale
Neuprüfung aller historischen Renderer-Lizenzen und keine nachträgliche
semantische Zulassung ihrer Stoff-, Temperatur- oder Tätigkeitswerte.

## Arbeitsweise, Prüfumfang und Grenzen

Gelesen wurden zuerst die aktuelle Route und der neue Wissenseinstieg;
begrenzte Registersuche, ausgewählte Karten und `lookup` führten zu den
Primärberichten. Root prüfte die in K01–K10 benannten Berichte und die
maßgeblichen Stellen von GDT616s Methode/Registrierung. Der
[begrenzte Zweitaudit](PEER_AUDIT.md) prüfte die f77r-/Bildregeln; Root las
anschließend die entsprechenden Primärberichte ebenfalls.

Die Prüfung verwendete vorhandene Berichte mit bereits publizierten Beispielen,
keine neuen Textprojektionen, Roh-TSV-Abfragen, Bilder, reservierten Absätze,
Decoderläufe oder Netzrecherchen. Historische Atlasberichte enthalten auch
Metadaten zu heute gesperrten Selektoren; diese Nennungen sind keine Öffnung
der zugrunde liegenden Manuskriptinhalte oder neue Zulassung. Keine Kontakte.

Der begrenzte interne Zweitaudit ist keine externe Fachbegutachtung und kein
unabhängiger Bedeutungsbeleg. Die Quellen enthalten mehrere abhängige
Transkriptionen und Wiederholungsrechnungen; deren Zahl wird nicht zu
unabhängigen Bestätigungen addiert. Die zwölf Themen sind ein ausgewählter
Prüfumfang, kein vollständiges oder zufälliges Registersample. Weitere
Dokumentationsfehler können verbleiben.

Die aktive Route bleibt unter 80 Zeilen/6000 Bytes; die große Zustandsdatei
wird für diesen Navigationsauftrag nicht erweitert. Bestehende Zulassungen,
Sperren und experimentelle Quellen ändern sich nicht. Ein kurzer Ledger-Eintrag
dokumentiert die Reparatur; der Import wird danach einmal aktualisiert.

## Nachprüfbarkeit

[BASELINE.json](BASELINE.json) bindet den Ausgangscommit und den alten
Bewertungspräfix; [PRESERVATION.json](PRESERVATION.json) bindet 41 unverändert
zu erhaltende Dateien, einschließlich des ersten Audits. Die neue Bewertung
wird angehängt, kein alter Registereintrag entfernt oder überschrieben.

`python research_registry/decisions/documentation_audit_followup_20260914/validate.py`
prüft Quellerhaltung, lokale Links, Routenumfang, die zwölf Themen-IDs und den
angehängten GDT616-Review. [VALIDATION.json](VALIDATION.json) dokumentiert
das Ergebnis; `ideas check` prüft anschließend die Metadatenkonsistenz.
Diese technischen Prüfungen bestätigen weder die wissenschaftliche Wahrheit
aller Quellen noch eine Manuskriptbedeutung. Der vorherige Audit wird nicht
erneut ausgeführt oder sein historischer Prüfbeleg überschrieben.

Ausgeführt: Dokumentationsprüfung PASS für 41 erhaltene Dateien, alle zwölf
Themenzeilen, 97 lokale Verweise und genau eine angehängte Bewertung.
Nach einer Ledgerergänzung und einem Importrefresh besteht `ideas check`;
`ideas show GDT616` zeigt den ursprünglichen Fehlschlag zusammen mit dem
unveränderten historischen Diagnose-PASS. Kein veralteter Review gemeldet.

Veröffentlichung erfolgt nur nach Prüfung der genau vorgemerkten Dateien auf
private Inhalte und Aufgabenbezug. Alte GDT600-Bindungsprobleme und fremde
unversionierte Arbeitsdateien gehören nicht zu dieser Änderung; kein global
fehlerfreier Repositoryzustand wird behauptet.
