# Arbeitsplan: ein gemeinsam gebundenes Voynich-System rekonstruieren

9. September 2026. Nutzerauftrag: einen ambitionierten Plan zur Lösung des
Entzifferungsproblems erstellen. Status: **Forschungsplan, keine ausgeführte
Rekonstruktion, keine bestätigte Übersetzung, keine laufende Achtstundensitzung**.
Dieser Plan bestimmt die nächste Arbeitsweise. Die Ergebnisse und Sperren der
bisherigen Versuche bleiben erhalten.

Das Ziel ist eine öffentliche, übertragbare Lesung zusammenhängender Passagen:
ein gemeinsamer Schlüssel, eine explizite Grammatik und ein erklärtes
Schriftverfahren, mit denen ein anderer Leser weitere Stellen entschlüsseln
kann. Eine semantische Notation darf sich dabei als Zielsystem ergeben; eine
Lautsprache wird nicht vorausgesetzt. Die vollständige Handschrift ist das
Fernziel. Der erste entscheidende Durchbruch wäre ein zusammenhängendes,
übertragbares Teilsystem, das zusätzliche reale Inhalte richtig festlegt.

## 1. Die Forschungsaufgabe richtig stellen

Wir behandeln Schriftform, Gruppengrenzen, Konstruktionen, Referenten und
Bedeutungen als zusammenhängendes inverses Problem. Keine dieser Schichten
muss vollständig gelöst sein, bevor die anderen untersucht werden. Mehrere
unsichere Zuordnungen dürfen einander gemeinsam bestimmen. Schon übersetzte
Einzelwörter sind keine Eintrittskarte zur Forschung.

Das verpflichtet uns allerdings zu mehr Genauigkeit: Wenn ein Modell ein
Zeichen, einen Anschluss oder einen Referenten anders interpretiert, muss
dieselbe Regel an allen einschlägigen Stellen gelten. Eine gute Geschichte
über eine Illustration genügt nicht. Die Aufgabe lautet: Welche wenigen
wiederverwendbaren Entscheidungen erklären gleichzeitig die tatsächlich
vorhandenen Formen, ihre Verknüpfung und einen überprüfbaren Inhalt?

Die erste Arbeitspriorität ist eine solche Rekonstruktion. Weitere
Archivprüfungen, isolierte Häufigkeiten oder Decoderkontrollen erhalten nur
Zeit, wenn sie eine konkrete Entscheidung innerhalb dieser Rekonstruktion
ändern. Die Aktenlage wird zu Beginn einmal begrenzt geprüft.

## 2. Was wir übernehmen und worüber wir neu entscheiden

Die bestätigte produktive Formstruktur und die übertragbaren
Nachbarschafts-/Positionsbefunde sind Ausgangswissen. Das bestehende
Rezept-/Feldmodell ist ein nützlicher Vorschlag für die Analyse. Seine
Wortarten, deutschen Wörter und Satzgrenzen werden nicht zu Beobachtungen
umetikettiert. Die Klarstellungen in `docs/STRUCTURAL_KNOWLEDGE.md` gelten.

| Vorgänger | Bereits geleistet | Verpflichtung des neuen Plans |
|---|---|---|
| GDT288 | Generative technische Kurzschrift als ausdrücklich vorläufige Synthese | Eine solche Architektur ist kein neuer Einfall. Sie muss jetzt konkrete, begrenzte Regeln und zusätzliche Vorhersagen erhalten. |
| GDT809 | Vier vollständige Absätze, gemeinsames Wörterbuch mit 16 Einträgen, konkurrierende Bedeutungslesungen | Mehr Absätze und ein gemeinsames Wörterbuch allein bringen keinen methodischen Fortschritt. |
| GDT827 | Transformation, Transport, manuelle Behandlung und Netzwerk als gekoppelte Achtwortmodelle | Gleichzeitig fünf Wörter umzubenennen kann dieselben Beobachtungen erhalten. Diese Mehrdeutigkeit muss explizit untersucht werden. |
| GDT828 | Zwei unmittelbare Anschlussregeln scheitern unter festen MANUAL-Typen; weiterer Geltungsbereich bleibt logisch möglich | Der bekannte `chedy/qokedy`-Konflikt ist kein neuer Test. Keine Fortsetzung durch erfundene Nomen oder einen weiteren Nachbarschaftstest. |
| IDEA000103 | Das alte Weglasskriterium war logisch ungeeignet | Eine echte gemeinsame Identifikation darf beim Weglassen einer notwendigen Bedingung mehrdeutig werden. |
| GDT613, GDT832 | Exakte Architektur-/Zielprobleme und falsche Schlüssel trotz starker Kontrollergebnisse | Kein allgemeiner Decoderbau oder Kontrollmarathon als Ersatz für Manuskriptvorhersagen. |
| GDT838, GDT878–880 | Die konkret untersuchten Parallelpassagen-, Bildkombinations- und Arithmetikeinstiege endeten ohne geeigneten Test | Keine Lockerung ihrer Filter oder Umbenennung als neue gemeinsame Rekonstruktion. |

Die bisherige Schuldzuweisung allein an fehlende Bedeutungsanker war zu eng.
Umgekehrt bedeutet die gemeinsame Rekonstruktion nicht, dass Semantik aus
beliebigen formalen Regelmäßigkeiten zwingend identifizierbar wird.

## 3. Eine Architektur mit drei miteinander prüfbaren Schichten

**Inhalt:** Ein endliches System von Gegenständen, Eigenschaften, Beziehungen
und gegebenenfalls Vorgängen. Es enthält konkrete konkurrierende Bedeutungen,
aber noch keine als wahr geschützten Wörter. Ein Gegenstand darf über mehrere
Sätze erhalten bleiben; sein Wechsel benötigt eine allgemeine Regel.

**Konstruktion:** Welche Einheiten werden verbunden, worauf bezieht sich eine
Eigenschaft, wie wird eine Operation eingebettet, wie sind Wiederholungen und
Auslassungen geregelt? Alternative Analysen müssen dieselben vollständigen
Passagen behandeln. Ein bloß unbekanntes Nachbarwort erfüllt keinen benötigten
Anschluss.

**Schrift:** Wie werden diese Einheiten in vollständige geschriebene Formen
umgesetzt? Wiederkehrende Bestandteile dürfen bedeutungstragend, grammatisch
oder reine Schreibkonvention sein. Die Entscheidung wird im gemeinsamen Modell
getroffen. EVA-Zeichen werden nicht ungeprüft zu Lauten. Unterschiedliche
Transkriptionen bilden Unsicherheit über eine Handschrift ab.

Der Rechenweg führt vom vermuteten Inhalt über die Konstruktion zur erwarteten
Schrift. Der Analyseweg läuft zurück. Eine Umkehrprobe allein bestätigt keine
Bedeutung: Ein Kopierprogramm kann ebenfalls exakt zurückschreiben. Entscheidend
sind eingeschränkte zusätzliche Vorhersagen und die Kosten des gesamten Modells.

Zwei inhaltliche Architekturklassen erhalten zunächst gleiche Arbeitszeit:
(a) beschreibende/katalogisierende Aussagen mit Eigenschaften und Beziehungen,
(b) Anweisungen mit Zuständen, Voraussetzungen und Ergebnissen. Eine vorhandene
formale Textbaseline bleibt der Vergleich ohne behauptete Bedeutungen. Diese
Klassen sind Arbeitsrivalen, keine erschöpfende Liste aller möglichen Systeme.
Der bekannte hybride Kurzschriftgedanke darf in beiden dieselbe Schriftfunktion
übernehmen; er erhält keinen Erfolg allein durch seine Flexibilität.

## 4. Ein zusammenhängendes Problemfeld bearbeiten

Die erste Rekonstruktion verwendet die vier bereits vollständig publizierten
GDT809-Absätze `f17r.4–6`, `f21r.8–12`, `f32v.7–11`, `f29v.1–4` und das
publizierte GDT827-Paket. Diese Stellen sind vollständig exponiertes
Entdeckungsmaterial. Der Zweck ist, über die früheren frei formulierten
Lesungen hinaus verbindliche Modelle zu konstruieren. Sie dienen nicht als
neue Bestätigung derselben alten Hypothesen.

Die tatsächlichen schwierigen Stellen bleiben im Zentrum: wiederholte Gruppen,
wechselnde Anschlüsse und alternative Wortgrenzen. Beispielsweise müssen
`cthy chor shor`, `chor chol daiin` und die vollständigen Nachbarschaften mit
derselben Analyse vereinbar sein. Kein Modell darf `daiin daiin` stillschweigend
verkürzen. Die unsichere Grenze `ctho daiin`/`cthodaiin` bleibt sichtbar.
Der bereits geprüfte f81r-Anschlusskonflikt dient als Gegenbeispiel gegen zu
freie Rettungen, nicht als ausgewähltes Nachfolgeexperiment.

Für einen begrenzten gemeinsam vorkommenden Kern werden konkurrierende Werte
und Regeln **zusammen** formuliert. Die komplette Passage wird dokumentiert;
Lücken zählen als Lücken. Es gibt keinen künstlichen Zwang, jedes Zeichen sofort
mit einem deutschen Wort zu versehen. Neue Kernregeln müssen aber über ihre
motivierende Fundstelle hinaus gelten. Anschließend werden sämtliche
zugelassenen Vorkommen dieses Kerns im festgelegten Prüfungsteil berücksichtigt,
nicht nur hübsche Beispiele.

Der zulässige Textumfang bleibt die bestehende 179-Selektor-Liste. Konkrete
Entdeckungs-, Entwicklungs- und Prüfungseinheiten werden vor einer Extraktion
festgelegt. Die Trennung erfolgt auf physischen Blättern einschließlich beider
Seiten; bereits exponierte Ausgangsblätter gehören zur Entwicklung. Innerhalb
historisch bereits untersuchten Materials heißt das prospektiver Test einer
neuen Vorhersage, nicht jungfräuliches Manuskriptmaterial. Zusätzlich wird die
Übertragung auf Konstruktionen geprüft, die nicht zur Regelanpassung dienten.
Diese Trennung ersetzt keine Bedeutungsprüfung.

## 5. Regeln explizit machen und die Modelle ernsthaft angreifen

Jedes Modell liefert eine gemeinsame Tabelle aus vollständigen Formen,
möglichen Bedeutungen, Konstruktionen und Schreibregeln. Dazu kommen
Referentenverfolgung, alle Ausnahmen und eine nachvollziehbare Analyse der
vollständigen Entwicklungspassagen. Regeln dürfen nicht auf Seiten- oder
Ereignisnamen zugreifen. Ein Registerwechsel darf eine allgemeine, überprüfbare
Schreibregel auslösen; eine neue Bedeutung für jedes Vorkommen ist keine Lösung.

Ein kleiner ausführbarer Prüfer enumeriert oder durchsucht den **deklarierten**
endlichen Kandidatenraum. Er prüft Quellenabdeckung, Widersprüche und mögliche
Fortsetzungen. Wenn die Suche heuristisch oder abgeschnitten ist, werden weder
Vollständigkeit noch Einzigartigkeit behauptet. Ein Solver wird nur eingesetzt,
wenn diese Aufgabe konkret feststeht; kein allgemeines Entzifferungsframework.

Wir bewerten mindestens vier getrennte Größen: nicht erklärte Quelldaten,
prüfbare Vorhersagefehler, Modellaufwand einschließlich Ausnahmen und
inhaltlich belegte Zuordnungen. Für den Modellaufwand kann eine vorab definierte
Beschreibungslänge dienen. Das ist ein Schutz gegen Beliebigkeit, kein
Bedeutungsbeweis. Auch Nachrichteninhalte und Restdaten müssen bezahlt werden;
ein verstecktes Inhaltsfeld darf nicht einfach den gesamten Quelltext speichern.
Gewichte und Kodierung werden vor dem Vergleich bestimmt, nicht passend zum
gewünschten Sieger eingestellt. Ein großer Parameterraum allein gilt nicht als
ambitionierteres Modell.

Weglassanalysen zeigen, welche Bedingungen welche Mehrdeutigkeiten auflösen.
Sie verlangen nicht, dass der Schlüssel ohne seine notwendigen Belege eindeutig
bleibt. Nach jedem wesentlichen Modellstand wird aktiv die kleinste andere
Lesung gesucht, die dieselben Beobachtungen erklärt.

## 6. Der zentrale Schritt: Bedeutungsmehrdeutigkeit gezielt brechen

Zuerst unterscheiden wir drei Fälle: Modelle machen verschiedene sichtbare
Vorhersagen; Modelle sind derzeit empirisch gleichauf; Modelle unterscheiden
sich lediglich durch systematische Umbenennung ihrer ungebundenen Bedeutungen.
Die letzte Möglichkeit wird ausdrücklich als Äquivalenz dargestellt. Wir
verkaufen die Auswahl eines Etiketts aus dieser Klasse nicht als Übersetzung.

Aus den überlebenden Modellen entsteht eine Liste konkreter Streitfragen:
Welche zusätzliche vollständige Konstruktion erlauben sie unterschiedlich?
Welchen Referenten oder welchen sichtbaren Zustand müsste dieselbe Lesung an
einer anderen Stelle bezeichnen? Welche historische Wortform oder Flexion müsste
bei derselben Laut-/Abkürzungsregel auftreten? Die Auswahl richtet sich nach
unterschiedlichen Antworten und tatsächlich zugänglichen Beobachtungen.

Für jede ausgewählte Frage werden Stelle, erlaubte Quelle, Vorhersagen aller
betroffenen Modelle, Messung und Entscheidung vor Betrachtung des Ergebnisses
festgehalten. Eine nicht beobachtete seltene Form ist nur dann ein Gegenbeleg,
wenn das Modell mit einer vorab bestimmten Expositionswahrscheinlichkeit ihr
Auftreten erwartet; bloße grammatische Erlaubtheit genügt nicht. Werden Fragen
adaptiv aus Modellen ausgewählt, bleibt ein abschließender Prüfungsteil von
**allen** solchen Auswahlrunden getrennt. Er wird nur einmal ausgewertet.

Reine Textfortsetzung kann eine Grammatik unterscheiden, aber keine beliebige
Umbenennung ihrer Bedeutungen aufheben. Für eine Bedeutung kommt mindestens
inhaltliche Bindung hinzu: eine unabhängig beobachtbare Beziehung, eine
quellenbelegte sprachliche Konstruktion mit festem Schriftweg oder mehrere
solche Bedingungen, die erst gemeinsam den Inhalt festlegen. Bereits
übersetzte Voynich-Wörter sind dafür weiterhin nicht vorausgesetzt.

Die vorhandenen manuellen Bildbeobachtungen und historischen Vergleichstexte
werden hier als begrenzte Bedingungen eingesetzt. Ein Bild ist nicht die
Gesamtbedeutung seines Absatzes. Themenähnlichkeit, eine Pflanze mit Blättern
oder eine Badewanne identifizieren kein bestimmtes Wort. Der Plan verlangt
auch keinen neuen blind bestätigten Bildanker, bevor überhaupt rekonstruiert
werden darf. Sollten die überlebenden Deutungen mit den vorhandenen Daten
inhaltlich ununterscheidbar bleiben, wird genau diese Restmehrdeutigkeit
angegeben und die konkret fehlende Beobachtung abgeleitet. Ein neuer Blick
auf bereits erfolglos geprüfte Bildkombinationen ersetzt sie nicht.

## 7. Vom semantischen System zum Schrift- und Sprachschlüssel

Sobald eine Kandidatenfamilie Beziehungen oder Aussagen wirklich festlegt,
prüfen wir, ob ein wiederverwendbarer sprachlicher oder notationaler
Ausdrucksmechanismus dieselben Aussagen trägt. Sprachhypothesen werden nach
vollständigen Konstruktionen und belegbaren Schrift-/Abkürzungsregeln ausgewählt,
nicht nach dem ähnlichsten Wort. Ein gemeinsamer Schlüssel muss auch neue
Flexionsformen, Wortkombinationen und verschiedene Abschnitte erklären.

Dieser Weg ist keine zwingende Einbahnstraße. Eine konkrete historische
Sprachregel kann bereits während der gemeinsamen Rekonstruktion zwei
Inhaltsmodelle unterscheiden. Sie bleibt dabei eine überprüfbare externe
Bedingung; derselbe Sprachmodellwert darf nicht erst den Schlüssel wählen und
anschließend dessen Bedeutung bestätigen. Sprachliche Vorhersagen werden an
anderen belegten Formen und in zurückgehaltenen Manuskriptstellen geprüft.

Eine mögliche Chiffren-/Codebucharchitektur wird nicht ausgeschlossen. Ihre
Ausführung bleibt an die dokumentierten Wiederaufnahmebedingungen gebunden;
der allgemeine Lösungsplan startet keinen geparkten Decoder. Ebenso bleiben
CDA001 und GDT616 geschlossen. Historische Quellen beginnen mit vorhandenen
Primärmaterialien. Es sind weder öffentliche Entzifferungsansätze noch fremde
LLM-APIs oder neue externe Daten für die erste Phase vorgesehen.

## 8. Arbeitsphasen und überprüfbare Lieferungen

Die erste Phase umfasst **acht Stunden aktive Forschungsarbeit**, beginnend
erst bei ihrer Ausführung. Das ist ein Arbeitsbudget, keine Lösungszusage und
kein heute gestarteter Hintergrundauftrag.

| Zeitbudget | Arbeit | Konkrete Lieferung |
|---|---|---|
| 0–1 h | Einmaliger Vorgängervergleich; gemeinsam verwendbare Quellen und vollständige Entwicklungsfälle festlegen | Endlicher Kandidatenvertrag, Quellenumfang, Expositionsliste; keine neue allgemeine Bestandsaufnahme |
| 1–4 h | Zwei zusammenhängende Rekonstruktionen mit gemeinsamem Kern; einfachsten ausführbaren Prüfer erstellen | Wort-/Regeltabellen, vollständige quellenausgerichtete Analysen, explizite Lücken und Widersprüche |
| 4–6 h | Modelle gegeneinander prüfen, verbleibende Umbenennungen identifizieren, tatsächliche abweichende Vorhersagen festlegen | Liste der Modellunterschiede; mindestens ein konkret prüfbarer Vertrag als Ziel, bei Nichterreichen explizit verfehlt |
| 6–8 h | Nur geeignete neue Vorhersage prüfen; unabhängige Gegenprüfung und Veröffentlichung | Modelle, Quellenauszüge, Vorhersagen, alle Ergebnisse und ihre Bedeutung für den nächsten Schritt |

**Checkpoint vor größerer Implementierung, spätestens nach 90 Minuten:**
Die neuen Regeln müssen bereits eine Konsequenz haben, die über dieselbe
freie Interpretation der GDT809/827-Passagen hinausgeht. Ohne diese Konsequenz
wird kein großer Suchapparat gebaut. Die verbleibende Zeit dient der expliziten
Rekonstruktion konkurrierender Systeme und ihres identifizierten Unterschieds;
sie wird nicht auf eine Folge weiterer Metadatenprüfungen umgebucht.

**Nach acht Stunden:** entweder eine an realen Daten getestete neue Vorhersage,
ein dokumentierter Gegenbeleg gegen ein genau bestimmtes System oder ein offen
verfehltes Auswahlziel mit konkret formulierter Restmehrdeutigkeit. Die bloße
Anzahl geprüfter Modelle ist kein Erfolg. Fehlende Zielerreichung wird als solche
berichtet; es folgt kein automatischer Reparaturmarathon.

**Zweite Phase, höchstens 16 weitere aktive Stunden und nur bei tragfähigem
Modellunterschied:** den gemeinsamen Kern über sämtliche vorgesehenen
Vorkommen prüfen, die Modellwahl einfrieren und die getrennte Abschlussprüfung
durchführen. Liefert sie nur Struktur, bleibt der Bedeutungsstatus offen.
Bei inhaltlich erfolgreichem Transfer entsteht das erste begrenzte Wörterbuch
mit vollständigen Passagen, Gegenbelegen und verbleibenden Alternativen.

**Ausbau:** weitere Abschnitte und die größtmögliche zusammenhängende Edition
erschließen; für jede neue Regel zusätzliche Vorhersagen verlangen. Dafür wird
nach dem ersten echten Transfer ein eigenes Budget gesetzt. Ein Termin für die
vollständige Lösung wäre gegenwärtig unbegründet.

## 9. Arbeitsteilung, Daten und Veröffentlichung

Root trägt die gemeinsame Rekonstruktion und die Entscheidung. Ein begrenzter
Ideenproduzent sucht parallel rivalisierende Systeme und aussagekräftige
Streitfälle. Eine unabhängig durchgeführte Prüfung bekommt später ein fixes
Paket und untersucht, ob die behauptete Vorhersage aus den Regeln folgt und
ob die Quellen sie tatsächlich entscheiden. Ein anderer Agent allein macht
vorher exponiertes Material nicht blind. Es läuft nichts unbeaufsichtigt
zwischen Nutzerturns.

Vorhandene Transkriptionen und Leser werden wiederverwendet. Gemischte TSVs
werden nur mit dem Selektor-zuerst-Guard und expliziten Spalten abgefragt.
Bis zu 32 CPU-Arbeiter sind verfügbar; eine GPU wird nur bei einer konkreten
passenden Rechenaufgabe eingesetzt. Forschungsideen und Modelle kommen von
uns, nicht aus automatischer OCR oder aus erfundenen Bildbezeichnungen.

Aktueller Bildumfang: 47 Schlüssel/53 Selektoren, drei verbleibende Zulassungen.
Der erste Arbeitsblock braucht keine neue Bildzulassung. `f84` und `f84r`
bleiben versiegelt; `f116v` ist nicht zugelassen. Neue Relationspakete passieren
vor einem Score die bestehenden ausführbaren GDT388-Gates. Eine geplante
Modellprüfung ersetzt keines dieser Gates.

Jeder materielle Versuch erhält vor Ausführung seinen Quellen-/Vorhersagevertrag,
Manifest und geeigneten Validator. Bedeutungs-, Struktur- und Kontrollbefunde
werden getrennt berichtet. Veröffentlichung erfolgt mit reproduzierbaren
kompakten Artefakten und der Prüfung des exakten Staging-Bestands. Reine
Planung erhält keine erfundene Experimentnummer oder Ergebniszeile.

## 10. Woran die Lösung erkennbar wäre

Ein anderer Leser kann mit denselben Regeln zusätzliche echte Passagen lesen;
wiederkehrende Formen behalten ihre begründete Funktion; neue Kombinationen
werden vorhergesagt; Behauptungen über dargestellte oder historische Inhalte
bestehen unabhängige Prüfungen. Schwierige Wiederholungen und Gegenbeispiele
bleiben erklärt oder begrenzen ausdrücklich den Schlüssel. Eine konkurrierende
gleich einfache Inhaltslesung darf nicht dieselben Belege ebenso gut erklären.

Die Ergebnisse dürfen gestuft sein: identifizierte Struktur, übertragbare
Bedeutungsregeln, gelesene Absätze und gegebenenfalls ein Sprach-/Lautschlüssel.
Erst die tatsächlich erreichte Stufe wird behauptet. Das Ziel bleibt die Lösung;
Arbeitsdisziplin soll sie ermöglichen und nicht durch kleinteilige Ersatzaufgaben
verdrängen.

Primärquellen: die oben genannten GDT-Berichte sind über `vmanus-work lookup`
gebunden; zusätzlich `research_registry/decisions/qa7_root_raw_design_review.json`,
`docs/STRUCTURAL_KNOWLEDGE.md` und `docs/WORKFLOW.md`. Ein begrenzter paralleler
Produzent hat zwei Architekturvorschläge geliefert. Root ergänzte insbesondere
die GDT828-Grenze und die Trennung zwischen formaler Vorhersage und semantischer
Identifikation. Für diesen Plan wurden keine neuen Manuskriptdaten geöffnet.
