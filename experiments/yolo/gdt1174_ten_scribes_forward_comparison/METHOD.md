# Zehn Schreiber: vollständige Regeln für eine endliche Beispielwelt

Die zehn Verfahren sind erfundene, ausführbare Entwürfe. Sie schreiben
sinntragende Nachrichten innerhalb einer festgelegten kleinen Fachsprache.
Sie sind weder historische Zuschreibungen noch Übersetzungen von Voynich.
Insbesondere sind unten vorkommende Zeichenfolgen **selbst erzeugte Codes**.
Ihre Beispielwerte werden keinem tatsächlich geschriebenen Voynichwort zugewiesen.

Der vollständige Algorithmus steht in [scribes.py](src/scribes.py), der vor
Berechnung der neuen Kennzahlen festgeschrieben wurde. Das Programm definiert
beide Richtungen, die endlichen Zeichentafeln, den Beispielsatz und die gesamte
künstliche Inhaltsfolge. Es enthält keine Liste echter Voynichwörter.

## Gemeinsame Nachricht und Zeichenvorrat

Ein Auftrag enthält Tätigkeit, Pflanze, Pflanzenteil, Zustand, Zusatz, Menge
und Dauer. Beispiel: eine Portion getrocknete Minzblätter für eine Nacht in
Wasser einweichen. Ein zweiter Auftrag kann zwei Portionen verlangen; ein
weiterer ersetzt Minze durch Salbei. Das sind erfundene Arbeitsaufzeichnungen,
keine übernommene Pharmakopöe oder behauptete medizinische Wirksamkeit.
Jeder Auftrag betrifft eine neue Portion. Für eine wirkliche Gebrauchssprache
müssten etwa Ausnahmen, Bedingungen, Gründe und unbekannte Namen hinzukommen.

Pflanze, Teil und Zustand werden in den meisten Entwürfen zu einem Material
zusammengefasst. Dadurch bleiben fünf Felder: Tätigkeit, Material, Zusatz,
Menge, Dauer. **Diese gemeinsame Entscheidung wird im Ergebnis kritisch
bewertet; sie ist keine Beobachtung am Manuskript.**

Der Vorrat besteht aus 22 vorhandenen Formen mit den EVA-Referenznamen
`a o e i n d q y s r l m k t p f ch sh ckh cth cph cfh`. Die lateinischen
Buchstaben sind hier Namen für Schriftformen, keine behaupteten Lautwerte.
Längere Referenznamen werden zuerst erkannt. Seltene oder unklare Formen
außerhalb dieser Arbeitszerlegung bleiben im Original als ausgeschlossene
Gruppen gezählt. Es wird kein vollständiges entziffertes Alphabet behauptet.

64 Pflanzen, acht Teile und acht Zustände ergeben 4096 mögliche Materialwerte.
Die Zahl `64*Pflanze + 8*Teil + Zustand` adressiert eine feste kombinatorische
Tafel. Die Haupttafel besteht aus 32 Vorstücken, acht Köpfen, vier Mittelstücken
und vier Endstücken: 4096 verschiedene Wörter aus 48 Bausteineinträgen.
Der Bedeutungsbestand braucht außerdem seine 64 Pflanzenbezeichnungen und die
kleinen Fachwortlisten. Das ist keine kostenlose Tabelle und kein aus Voynich
gewonnenes Wörterbuch. Die Reihenfolge aller Einträge ist im Programm explizit.
Die endliche Tafel stellt keine Lösung für beliebige neue Wörter bereit.

Die tatsächlichen Zeilen entstehen erst danach durch Umbruch bei 48 Zeichen.
Der Leser erhält nur die sichtbaren Wörter und Absätze. Ein Absatz setzt die
explizit benannten Merkregister zurück. Zeilenwechsel liefern keine versteckte
Satzgrenze; Datensätze werden aus Stelligkeit oder ausgeschriebenem Abschluss
wiedergewonnen. Das Layout ist eine Entwurfsannahme, keine erklärte Voynichregel.

## 1. Silbenwörter — eine vereinbarte Fachsprache

**Gedanke des Schreibers:** Ich gebe den Begriffen kurze, lernbare Namen, die
sich aus wenigen Silben aufbauen lassen. Ein Eingeweihter kennt die Namenstafel.

**Schreiben:** Die fünf Felder bekommen unterschiedliche Nummernbereiche.
Jede Nummer wird in einer 16er-Tafel als Folge von Silben geschrieben; jede
Silbe hat einen von vier Anfängen und eines von vier Mittelstücken. `y`
schließt das Wort. Ein Begriff wird immer vollständig geschrieben.

**Lesen:** Silbenwerte zur Nummer zusammensetzen, Bereich und Begriff bestimmen.
Je fünf Wörter ergeben einen Auftrag. Es gibt keine stillen Auslassungen.
**Zweck:** eine eigenständige Fachsprache oder ein vereinbarter Geheimwortschatz.
**Statistische Verpflichtung:** Die Umbenennung erhält die Häufigkeiten der
zugrunde gelegten Begriffswörter vollständig. Ein zu eintöniger Inhalt bleibt
auch mit einer schönen Silbentafel eintönig.

## 2. Stamm und Rollenendung — kenntliche Satzrollen

**Gedanke:** Derselbe Gegenstand soll erkennbar bleiben; kleine Zusätze sagen,
welche Aufgabe sein Wort im Satz übernimmt.

**Schreiben:** Ein Wort besteht obligatorisch aus Rollenanfang, Stamm und
Rollenende. Fünf feste Anfang/Ende-Paare unterscheiden die fünf Felder.
Materialstämme stammen aus der gemeinsamen Tafel. Keine neue Ausnahme pro Wort.
**Lesen:** Rolle abtrennen, Stamm auflösen, genau ein Wort je Rolle zuordnen.
**Zweck:** eindeutige Arbeitsanweisungen mit wiedererkennbaren Wortfamilien.
**Verpflichtung:** Viele ähnliche Formen entstehen regelhaft, aber die
zusätzlichen Zeichen müssen mit der tatsächlichen Wortlänge vereinbar sein.

## 3. Innere Rollenbeugung — die Wortmitte trägt Grammatik

**Gedanke:** Ich verändere einen Teil im Wort, statt immer ein weiteres
selbständiges grammatisches Wort zu schreiben.

**Schreiben:** Hinter die erste vollständige Schriftform des Stamms tritt
je nach Rolle `e`, `a`, `o`, `ee` oder `ii`; `n` schließt die Form. Eine Bankform
wie `ch` wird dabei nicht in ihre lateinischen Referenzbuchstaben zerlegt.
**Lesen:** Das feste innere Muster identifiziert die Rolle; die übrigen Teile
geben den Stamm. Die gesamte endliche Tafel ist auf Eindeutigkeit geprüft.
**Zweck:** kompakte Grammatik mit deutlich verwandten Formen.
**Verpflichtung:** Das Verfahren behauptet nicht, dass echte Voynich-e-Folgen
bereits eine solche Flexion darstellen. Ihre tatsächliche Häufigkeit zählt.

## 4. Begriffshierarchie — vom Gegenstand zum Teil und Zustand

**Gedanke:** Ich halte auseinander, welches Gewächs, welcher Teil und welcher
Zustand gemeint sind. Verwandte Begriffe bekommen verwandte Namen.

**Schreiben:** Pflanze, Teil und Zustand erhalten hier drei getrennte Wörter
mit festen Klassenanfängen; die übrigen vier Felder bleiben rollenmarkiert.
Es entstehen sieben Wörter je Auftrag. Jede Klasse besitzt ihre feste Tafel.
**Lesen:** Klassen erkennen und ihre Werte zu einem vollständigen Material
zusammensetzen. Kein Bild muss dem Leser einen fehlenden Wert verraten.
**Zweck:** eine systematische Beschreibung von Vorräten oder Arbeitsmaterial.
**Verpflichtung:** Die vielen wiederkehrenden Klassenwörter dürfen den Text
nicht stärker dominieren, als es im Original beobachtet wird.

## 5. Fachkürzel und Vollformen — Schreibarbeit sparen

**Gedanke:** Was ich dauernd brauche, bekommt eine kurze Form; den Rest kann
ich mit demselben Vorrat vollständig schreiben.

**Schreiben:** Für die ersten bis zu sechs Werte jeder Rolle gelten feste
Kurzformen. Alle anderen Werte erhalten `qo` als Vollformkennzeichnung und
danach die vollständige Silbennummer aus System1. Die Wahl ist obligatorisch.
**Lesen:** Kurztafel oder vollständige Silbenauflösung benutzen. Es gibt keine
unmarkierte Entscheidung zwischen zwei Lesarten.
**Zweck:** kürzere häufige Fachwörter bei erhaltenen seltenen Werten.
**Grenze:** Das ist eine vollständige Schreibung innerhalb der endlichen
Nummerntafel, keine bereits implementierte offene Lautschrift für neue Namen.
Abkürzen ändert Wortlängen, aber noch nicht die Wortfrequenzen.

## 6. Feste Satzstellen — Grammatik durch Reihenfolge

**Gedanke:** Wenn jeder Auftrag dieselbe Reihenfolge hat, brauche ich seine
Feldnamen nicht jedes Mal auszuschreiben.

**Schreiben:** Fünf unverzierte Werte stehen in festgelegter Reihenfolge.
Dieselbe Zeichenfolge darf je nach Stelle einen anderen Wertetyp bezeichnen.
**Lesen:** Ab Absatzanfang in Fünfergruppen lesen; die Stelle wählt die Tafel.
Zeilenwechsel spielen keine Rolle. Der vollständige Auftrag bleibt eindeutig.
**Zweck:** kurze geordnete Aufzeichnungen, ähnlich einem vereinbarten Formular.
**Verpflichtung:** Gleich nummerierte Werte verschiedener Felder werden gleich
geschrieben; dadurch entstehen besonders viele gleiche Wörter und Doppelungen.

## 7. Ausdrückliche Rückverweise — zuletzt Genanntes wiederaufnehmen

**Gedanke:** Ich spare Wiederholungen, indem ich ausdrücklich auf den letzten
Wert derselben Art verweise.

**Schreiben:** Für jede der fünf Rollen wird der zuletzt genannte Wert gemerkt.
Ist der neue gleich, schreibt man `y` plus Rollenanfang; sonst die volle Form
von System2. Am Absatzanfang sind alle Register leer. Fünf Wörter bleiben Pflicht.
**Lesen:** Dasselbe Register führen. Ein Verweis ohne vorherigen Wert ist illegal.
Der Verweis bezeichnet einen Begriffswert, keine unveränderte physische Charge.
**Zweck:** repetitive Fachtexte kürzen, ohne zu raten, was ausgelassen wurde.
**Verpflichtung:** Die kurzen Rückverweise werden selbst häufige Wörter und
müssen in der Wortverteilung mitgezählt werden.

## 8. Änderungsprotokoll — nur die Abweichung zum vorigen Auftrag

**Gedanke:** Ähnliche Aufträge schreibe ich einmal vollständig und danach nur
noch mit den jeweils geänderten Angaben.

**Schreiben:** Der erste Auftrag nennt alle fünf Felder. Danach werden nur
geänderte Felder als vollständige rollenmarkierte Wörter geschrieben. `dy`
schließt jeden Auftrag. Nur der Schlusscode allein bedeutet: derselbe Auftrag
für eine neue Portion. Der Absatzanfang setzt den Vergleichszustand zurück.
**Lesen:** Den vorigen Fünferdatensatz kopieren und ausdrücklich genannte Felder
ersetzen. Vor dem ersten vollständigen Datensatz ist ein Abschluss ungültig.
**Zweck:** Varianten, Wiederholungsversuche und ähnliche Einträge knapp notieren.
**Verpflichtung:** Der Abschlusscode und die kleinen Feldvorräte können den
Text beherrschen; die Ersparnis darf nicht bloß als fehlende Information gelten.

## 9. Stellenschrift mit Operatoren — Handlungen zusammensetzen

**Gedanke:** Ich schreibe zuerst die benötigten Angaben, dann, was der Leser
daraus bilden soll. So brauche ich wenige verbindende Wörter.

**Schreiben:** Pflanze, Teil, Zustand, dann `ckhy` zur Materialbildung;
danach Zusatz, Menge, Dauer, Tätigkeit und `cthy` zur vollständigen Anweisung.
Beide Operatoren haben eine feste Zahl von Argumenten. Die Wertwörter selbst
stammen aus der unveränderten Haupttafel.
**Lesen:** Werte auf einer kleinen Merkliste ablegen; ein Operator entnimmt
seine Argumente und setzt das Ergebnis ein. Ein vollständiger Auftrag muss
genau ein Ergebnis hinterlassen. Fehlende Argumente dürfen nicht ergänzt werden.
**Zweck:** ein knapper, vereinbarter Arbeitskalkül mit eindeutiger Auswertung.
**Verpflichtung:** Zwei feste Operatorwörter pro neun Wörtern sind bereits
über22% der Ausgabe. Eine technische Notation ist nicht automatisch Voynich-nah.

## 10. Definition und Aufruf — benannte Materialbeschreibungen wiederverwenden

**Gedanke:** Einen längeren Materialausdruck definiere ich einmal und gebe ihm
für den folgenden Abschnitt einen kurzen Namen.

**Schreiben:** Bei erster Nennung: Definitionswort, laufender Name,
Materialbeschreibung, Abschluss. Ein Auftrag nennt dann Aufrufwort, Namen,
Tätigkeit, Zusatz, Menge, Dauer und Abschluss. Definitionen stehen vor Gebrauch,
sind unveränderlich und zählen vollständig zum geschriebenen Text.
**Lesen:** Eine kleine lokale Namenstafel führen, den Materialausdruck beim
Aufruf einsetzen und die übrigen Felder lesen. Jeder Aufruf betrifft eine neue
Portion. Ein Absatz beginnt mit einer leeren Tafel.
**Zweck:** wiederholte komplexe Benennungen verkürzen. Dieser Prototyp definiert
Materialausdrücke, noch keine frei verschachtelten vollständigen Rezepte.
**Verpflichtung:** Definition, Aufruf und Abschluss erzeugen viel Zusatztext.
Eine hinter den Kulissen bereitgestellte Namenstafel wäre eine versteckte Kostenersparnis.

## Was gemeinsam überprüft wird

Alle Programme schreiben dieselben5120 Aufzeichnungen. Aufzeichnungen samt
sichtbarem Layout werden gespeichert und exakt zurückgelesen. Zusätzlich wird
jeder einzelne mögliche Feldwert geprüft; unterschiedliche Zeilenumbrüche
müssen die Nachricht unverändert lassen. Diese Prüfungen zeigen lediglich,
dass unsere erfundenen Systeme funktionieren.

Danach folgen die zehn in der [Registrierung](PREREGISTRATION.md) festgelegten
Statistikvergleiche bei jeweils8000 Wörtern. Die Zieltranskriptionen werden
getrennt gerechnet. Der vollständige Ergebnisbericht erklärt Auslassungen,
Abweichungen, gemeinsame Schwächen der Inhaltsquelle und Grenzen der Auswahl.
