# Vorwissen vor Wortbedeutung

Stand: 2026-09-27. Ergebnis: **benutzbare Auswahlhilfe und rückblickendes
Kandidatenaudit; keine neue Übersetzung**. Die
[vor Implementierung registrierte Entscheidung](WORD_SELECTION_DECISION.md)
grenzt diesen Arbeitsblock ab.

## Was sich praktisch ändert

Vor einer neuen Wortbelegung steht jetzt ein automatisch erzeugtes Wortprofil
mit Häufigkeit, Verbreitung, Textbereich, Currier-/Handmetadaten, physischen
Zeilenpositionen, Wiederholungen und Nachbarn. Dazu kommen geprüfte frühere
Befunde mit Geltungsbereich und Voraussetzungen sowie Suchtreffer aus dem
bestehenden Register. Dadurch kann eine lokal passende Glosse nicht mehr als
bevorzugte Lesung geführt werden, ohne ihre übrigen Erklärungspflichten sichtbar
zu machen. Das Tool ersetzt die fachliche Beurteilung der Begründung nicht.

```bash
./vmanus-work words profile daiin dar aiin
./vmanus-work words evidence WE006
./vmanus-work words review research_registry/proposals/laufenberg_f85r2_20260926/WORD_SELECTION_WINTER.json --fail-unready
```

`profile --json` enthält vollständige beschreibende Kennzahlen und begrenzte
Beispieltabellen; die normale Ausgabe ist eine kompakte Vorschau. Mit `--limit`
werden Beispiele und Suchtreffer begrenzt, nicht die ausgewerteten Vorkommen.
`evidence` öffnet den vollständigen kuratierten Eintrag mit seinen Primärlinks.
Suchtreffer und Vorschauen ersetzen das Lesen dieser Primärberichte nicht.

Die lokale SQLite-Datei ist ein automatisch erneuerbarer Cache im bereits
ignorierten Cache-Verzeichnis. Sie ist keine zweite Forschungsdatenbank und
wird nicht veröffentlicht. Eingabe-, Code- und Allowlist-Prüfsummen verhindern
stille Veraltung; eine geänderte Zulassungsliste erfordert explizite Anpassung.
Auch beim Aufbau werden ausgeschlossene Zeilen durch den bestehenden Guard
verworfen, bevor ihr übriger Inhalt materialisiert wird.

## Konkrete erste Anwendung

Die folgenden exakten Rohformen wurden über **alle 179 zugelassenen Selektoren**
gezählt, einschließlich f85r2. Längere Formen zählen nicht als Vorkommen ihres
Teilstrings. Die drei Transkriptionen werden niemals addiert.

| Form | ZL3b | IT2a | RF1b | ZL-Selektoren mit Form |
|---|---:|---:|---:|---:|
| daiin | 717 | 740 | 618 | 169 |
| dar | 243 | 242 | 223 | 110 |
| aiin | 423 | 390 | 436 | 100 |
| dain | 191 | 188 | 158 | 89 |
| dair | 73 | 77 | 71 | 57 |
| qodaiin | 41 | 40 | 36 | 25 |
| qo | 46 | 26 | 47 | 35 |

Das vollständige Ergebnis steht in [WORD_SELECTION_RESULT.json](WORD_SELECTION_RESULT.json).
Es enthält getrennte Nenner pro Leser, Stratum und Wortform sowie die
Widerspruchsbeispiele. Eine Zeilenposition in der Gesamttabelle umfasst auch
Labels/Kreiszeilen; die folgenden Kontrollregeln wurden ausdrücklich auf
`kind=P` beschränkt. Deshalb unterscheiden sich einzelne Positionszahlen von
reinen Fließtextzahlen. Selektoren sind keine unabhängigen physischen Blätter.

Die zwei ursprünglichen Grundbedeutungen wurden unverändert aus dem
hashgebundenen IDEA595-Paket übernommen: `daiin=WINTER`, `dar=SUMMER`.
Der [Auditvertrag](WORD_SELECTION_WINTER.json) enthält keine erfundene
Häufigkeitsschwelle. Seine maschinelle Entscheidung lautet:

- **NO_TESTABLE_PREDICTIONS:** Das lokale Quellenmodell liefert keine hier
  prüfbaren notwendigen Bedingungen für die Verteilung im übrigen Manuskript.
- **NOT_READY_FOR_PREFERENCE:** Verteilung, Wiederholungen/Positionen,
  übergreifende Konstruktionen und Bedeutungsunterscheidung sind unbegründet.
  Lokale Formen- und Grammatikbehauptungen bleiben ausdrücklich Hypothesen.
- **NO_AUTOMATIC_MEANING_PREFERENCE:** Winter ist nicht allein durch seine
  Häufigkeit widerlegt. Ebenso wird keine andere Bedeutung automatisch gewählt.

Dies prüft die Begründung dieser zwei Belegungen, nicht nachträglich alle 113
freien Ganzwortwerte oder den vollständigen alten Parser. Originalpaket,
ursprüngliche Entscheidungen, Mängel und Alternativen bleiben unverändert.

## Was Grammatikprüfung hier tatsächlich leistet

Der Prüfer kann ausdrücklich formulierte notwendige Oberflächenbedingungen
vollständig auswerten: zulässige Zeilentypen/Positionen, maximale Vorkommen je
physischem Locus, verbotene nächste Formen und verlangte unmittelbare Nachbarn.
Jede Bedingung muss ihre Grundlage und Annahmen nennen. Derselbe Abgleich als
weiche Erwartung erzeugt lediglich eine Abweichung, keinen harten Ausschluss.

Die drei folgenden Kontrollen waren absichtlich **nach Kenntnis der Daten**
ausgewählte Funktionstests. Sie sind keine neuen Forschungsentdeckungen und
keine unabhängig begründeten Grammatikmodelle:

| Explizite Kontrollregel für daiin | ZL3b | IT2a | RF1b | Ergebnis |
|---|---:|---:|---:|---|
| Nur am physischen Zeilenende, alle P-Zeilen | 601/715 | 620/737 | 518/615 | Regel widersprochen |
| Höchstens einmal je physischer P-Zeile, gesamter Bestand | 77 Zeilen | 80 Zeilen | 62 Zeilen | Regel widersprochen |
| Dieselbe Einmalregel, nur f85r2-P-Zeilen | 0/2 | 0/2 | 0/2 | lokal verträglich |

Die erste Zeile zählt widersprechende Vorkommen; die zweite zählt verschiedene
Zeilen mit Mehrfachvorkommen. Der dritte Fall hat zwei P-Vorkommen pro Leser;
das weitere daiin auf f85r2 gehört laut Quellmetadaten zu einer Kreiszeile.
Gerade dieser Kontrollvergleich demonstriert das ursprüngliche Problem:
Eine lokal verträgliche Regel kann außerhalb ihrer gewählten Passage scheitern.

Eine Widerlegung betrifft immer Regel **und** Annahmen gemeinsam. Ein
Zeilenrand ist keine gelesene Satzgrenze, ein Nachbar kein identifiziertes
Argument. Die Software kann deshalb nicht ohne weiteres „Substantiv“, „und“
oder „nimm“ verbieten. Typisierte vollständige Grammatikmodelle benötigen
weiterhin ihre eigenen eingefrorenen Parser und Auswertungen.

Neue Verträge können den saisonalen Auditvertrag als Formatvorlage verwenden.
`assignments` bindet Form und vorgeschlagene Bedeutung; `scope` nennt die
zugelassenen Seiten, Leser und gegebenenfalls Zeilentypen. Die sechs
`accounts`-Felder erfassen Verteilung, Wiederholung/Position, Konstruktionen,
Formbeziehungen, Grammatik und Bedeutungsunterscheidung. `source_supported`
verlangt Quellen mit Pfad und Hash, bestätigt deren Interpretation aber nicht.
`reviewed_evidence_ids` dokumentiert die tatsächlich gelesenen Katalogeinträge.
Jede `prediction` enthält ID, Form, `rule`, `strength` (`necessary` oder
`expectation`), `basis`, `assumptions` und entweder `values` oder `maximum`.
Die [Kontrollverträge](WORD_SELECTION_CONTROLS.json) zeigen konkrete Syntax;
ihre nachträglich gewählten Regeln dürfen nicht als Forschungsprior kopiert
werden. Explorative Hypothesen ohne vollständige Begründung bleiben erlaubt;
der Prüfer verhindert ihre automatische Beförderung zur bevorzugten Lesung.

## Vorwissen und seine Grenzen

[WORD_EVIDENCE.json](WORD_EVIDENCE.json) enthält zunächst **12 kuratierte
Einträge mit 25 hashgebundenen Primärverweisen**. Darunter sind Formenreihen,
f22r-Konstruktionen, sichere Dreierfolgen, die verworfene daiin-Nachbarregel,
die bedingten W94/W96- und GDT1040-Widersprüche sowie die bekannte gerichtete
Wortstruktur mit verbleibenden Ganzformeffekten.

Ein eigener Eintrag korrigiert für die weitere Verwendung die zu starke alte
GDT686-Behauptung, Formfolgen allein widerlegten „und/nimm/führe aus“. Der alte
Bericht bleibt unverändert. Unbestätigte Zahlen- und Eigenschaftsglossen werden
nicht als Grammatikregeln installiert.

Dieser kleine kuratierte Index ist **nicht vollständig**. Für andere Wörter
funktionieren die beschreibenden Profile und die vorhandene Registersuche
sofort; fehlende kuratierte Einträge sind keine Behauptung fehlender Forschung.
Der separate historische `priorities`-Snapshot war beim Audit bereits veraltet
(`VOYNICH_ACTIVE_STATE.md`-Bindung). Er wurde nicht als leerer Befund benutzt und
ist keine Abhängigkeit dieses Werkzeugs; die aktuelle `ideas`-Suche bleibt der
eingebundene Navigator. Keine automatische Reparatur weiterer Altbestände.

Es gibt absichtlich keine unkalibrierte Übersetzungswahrscheinlichkeit und
keine Gewichtesumme aus Häufigkeit und sprachlicher Gefälligkeit. GDT611 zeigt
Bedeutungspermutationen trotz gleicher Formbefunde; GDT612 zeigt, dass ein
ungeeignetes Zielmaß falsche Schlüssel vor eine bekannte Wahrheit setzen kann.
Für eine probabilistische Bedeutungsrangfolge fehlen hier noch begründete,
unterschiedliche Vorhersagen der konkurrierenden Lesungen und eine geeignete
Kalibrierung. Häufigkeit wird als zu erklärender Befund benutzt, nicht als
automatische Übersetzung.

## Reproduktion und Prüfungen

```bash
python -m unittest tests.test_word_profiles tests.test_word_evidence tests.test_work_context tests.test_work_preflight
python -m tools.word_selection_audit --check
./vmanus-work context check
./vmanus-work ideas check
```

Der Reproduktionslauf prüft sieben Formen in drei getrennten Lesungen durch
eine **zweite, direkte guardierte Zählung ohne die Profil-SQL-Abfragen**:
231 Vergleiche einschließlich Rang, Verteilung, Position und Wiederholung.
Er prüft zusätzlich die Kontrollausgänge, Gegenbeispielzahlen und die
unveränderten ursprünglichen saisonalen Belegungen. Der veröffentlichte
Ergebnis-JSON muss vollständig übereinstimmen.

Die funktionalen Tests behandeln unter anderem giftige ausgeschlossene
Zeilen, Cache-Veraltung, unzulässige Scope-Erweiterung, alternative Leser,
Teilstringverwechslung, vollständige Gegenbeispiele trotz gekürzter Anzeige,
weiche gegenüber harten Bedingungen und leere Prüfumfänge. Kein erfolgreicher
Test bestätigt eine Bedeutung. `review --fail-unready` liefert Exitcode1 bei
fehlenden Auswahlvoraussetzungen; der normale Exitcode0 besagt lediglich,
dass ein Bericht korrekt erzeugt wurde.

## Forschungsentscheidung

Neue bevorzugte Lesungen müssen das verfügbare Wortprofil, die einschlägigen
Primärbefunde, ihre Annahmen und unterscheidbare Konsequenzen gemeinsam
darlegen. Fehlende Begründungen bleiben sichtbar; passende Einzelstellen
können sie nicht ersetzen. Die saisonalen Grundbelegungen von IDEA595 bleiben
frei gesetzte Annahmen ohne Vorrang. Keine neue Bedeutung wird hier ausgewählt.

Alle Eingaben waren bereits exponiert. Keine Reserve, kein Bild, keine neue
Quelle und kein externer Kontakt wurde benutzt; f84/f84r bleiben geschlossen.

Prüfstand: 60 funktionale/Integrationsprüfungen bestanden; unabhängige Zählung
und exakte Ergebnisreproduktion bestanden. Der globale Repository-Check hat
weiterhin die acht vorher bekannten Befunde: sieben ungebundene GDT600-Dateien
und GDT953s fehlende Begründung für ein großes Artefakt. Kein globales PASS und
keine Änderung dieser fremden Altbestände. Die aufgabenspezifische
Veröffentlichungsprüfung kontrolliert den exakt gestagten Baum separat.

Zeitnachweis: Registrierung der Implementierung um14:14UTC; Implementierung,
Anwendung und abschließende Reproduktionsprüfung um14:35UTC erledigt, vor dem
registrierten60-Minuten-Prüfpunkt. Die Vorbereitung vor der Registrierung wurde
nicht separat gestoppt. Veröffentlichung schließt diesen Arbeitsblock ab;
kein weiterer Infrastrukturzweig wurde begonnen.
