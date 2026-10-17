# TZ3: eine belegte Nominalreihe bei unveränderter Teilregel

Status: begrenzte Quellfortsetzung, keine ausgewählte Voynichlesung.
IDEA001116 bleibt raw/inconclusive. Alle nativen Bedeutungen bleiben unzugewiesen.

## Entscheidungsnotiz und Grenzen

Arbeitsbeginn16:51:26UTC; inklusiver Kontrollpunkt17:26:26UTC für Vorgängerprüfung,
Quellvergleich, kleinen unveränderten Vorwärtsaufruf, separate Prüfung und Publikation.
Die positive Grundlage sind zwei Tuhfet-Haupttextvarianten mit einer
editionsgestützten dritten Form und die bereits gelesene1556er Nominalquelle. Eine tatsächlich belegte
zusätzliche Quellform ist etwas anderes als ein nach modernen Regeln erfundener
Stamm. Die stärksten Gegenfälle bleiben die mehrdeutige Rückrichtung, die breite
Verteilung und Wiederholung der nativen ganzen Wörter sowie f75r.38 AABBA.

Die kleine Frage lautet: Liefert die vorhandene Nominalquelle konkrete vollständige
Wortformen, die die eingefrorene Tabelle ohne neue Werte verarbeiten kann?
Ein positives Ergebnis erweitert nur die quellbelegte Eingabeliste. Ein negatives
Ergebnis würde keine neue Schreibtabelle rechtfertigen. Beide Ergebnisse allein
wählen keine Bedeutung oder Sprache; daher kein größerer Decoder, neues Korpus,
Solver oder allgemeines Alphabetprojekt. Der Prüfcode ruft nur die alte Funktion
auf und erhält eine nicht schreibbare Form ausdrücklich als UNASSIGNED.
Dies ist explorative Quellarbeit nach Kenntnis der Zielgestalten, keine blinde
Vorhersage oder nachträglich registrierte Bestätigungsprüfung.

## Quelle und vollständige Formen

Ömer Yağmur2014, *Kitâb-ı ‘İlâc-nâme (1556) Adlı Bir Kemâliyye Nüshası ve Eserin
Dili Üzerine*,35–75, [offizielles PDF](https://dergipark.org.tr/en/download/article-file/143308).
Datei und Locatorbindung stehen bereits in OAT_SOURCE_RECEIPT_20261017.json.
1556 ist das berichtete Kopierdatum dieses Zeugen; es ist keine Datierung der
Voynichschrift und kein direkt von uns gesehenes Originalmanuskript.

Die Nominalanalyse aufp50 ist von der fortlaufenden Transkription aufp61–62
zu unterscheiden. Das dort zitierte ḳoḳu ist ein analysierter Nominalstamm;
an der verwiesenen Stelle14b/4 steht im Fließtext die längere Form ḳoḳusı.
Ein analysierter Stamm belegt deshalb nicht automatisch einen exakt so
freistehenden vollständigen Token. Der frühere OAT-Bericht bleibt eingefroren;
diese Präzisierung verhindert seine Wiederverwendung als Standalone-Beleg.

Die fortlaufende Transkription liefert insbesondere:

| Vollständige Form | Locator | Quellenstatus |
|---|---|---|
|ḳoḳı|15a/5, gedrucktp62/PDF28|tatsächlich ganzer nominaler Token|
|ḳoḳusı|15a/4, gedrucktp62/PDF28|tatsächlich ganze längere Nominalform, kein bloßer Wörterbuchstamm|
|ḳoḳa|15a/7 und15b/4, gedrucktp62/PDF28|verbaler Gebrauch im Wunsch-/Ergebniszusammenhang; keine neue Vergangenheitsvariante|

Die konkrete Inhaltsfolge auf15a/4–6 unterscheidet eine gewünschte Abwesenheit,
eine genannte Handlung und deren behauptete Wirkung. Der anschließende Text
verwendet das Verb für einen gewünschten und einen erwarteten Körperzustand.
Diese Zusammenhänge gehören zur Quelle und sind keine Voynichübersetzung.
Eine vollständige Aorist-/Partizipreihe oder Übertragbarkeit zwischen dem
1556er medizinischen Zeugen und den Tuhfet-Varianten folgt daraus nicht.
Die Suchstrings kokar/kokan/kokgan/kokugan werden nicht zu historischen Belegen.

## Feste Tabelle und native Verpflichtungen

Die originale TZ3_FORWARD_20261017.py bleibt byte-unverändert. Es gibt keine
zusätzlichen a/r/n-Werte, Lautangleichungen, Nullzeichen oder wortweisen Ausnahmen.
Die oben genannten drei vollständigen Eingaben werden im Begleitprogramm
explizit verarbeitet. Die Ergebnisdatei hält auch den erwarteten Fehler für
das unzugewiesene a fest; dieser ist eine Reichweitengrenze des Teilcodes,
kein allgemeiner Sprach- oder Mechanismusausschluss.

## Ergebnis und Einordnung

| Historische Ganzform | Unveränderte Ausgabe | Bedeutung im Manuskript |
|---|---|---|
|ḳoḳı|qoky|UNASSIGNED|
|ḳoḳusı|qokeey|UNASSIGNED|
|ḳoḳa|keine vollständige Ausgabe: a unzugewiesen|UNASSIGNED|

Der Nominalbeleg erklärt eine echte Lücke der alten Quellenliste: Zur vorhandenen
konstruierten Stammzeichenfolge gibt es jetzt eine genau belegte ganze nominale
Form mit derselben Ausgabe. Er macht koku oder koksu nicht nachträglich zu
attestierten Imperativen. Die längere Nominalform liefert qokeey ohne eine neue
Tabellenzelle. Die verbale Nichtpastform liefert dagegen gerade KEINE vollständige
Ausgabe. Es wurde weder qoka noch ein erfundenes kokar/kokan erzeugt.

Das neue vorhandene qokeey-Wortprofil wurde vollständig über das bestehende
Werkzeug abgerufen. Ganze Formen, eingebettete Strings und Leser bleiben getrennt:

| Leser | Ganze qokeey | Selektoren | Anfang/Mitte/Ende | gleiche Nachbarpaare |
|---|---:|---:|---|---:|
|ZL3b|280|70|28/242/10|12|
|IT2a|280|69|28/242/10|12|
|RF1b|269|69|27/230/12|10|

Positionen sind Zeilenpositionen, keine bestimmten Satzpositionen.
Es verteilt sich über alle sechs vorhandenen Abschnittstags. Diese Breite und die
Wiederholungen bevorzugen weder einen engen Geruchsbegriff noch automatisch ein
Funktionswort. Das genaue Profil und WE009 bleiben maßgeblich. GDT822s ältere
Feuerhypothese ist ein unbestätigter historischer Versuch, kein wiederverwendbarer
Wortwert. GDT1124s fehlender Absatzanfangs-Unterscheider entscheidet ebenfalls
keine nominale Bedeutung. GDT1298s ungelöste Abstandslücke bleibt ungelöst.

Im bereits vollständig erhaltenen120er-Absatz gibt es ein qokeey, ITf75r.33G001.
Die neue Ergebnisdatei zeigt dessen rohe Form und Grenzen, ausdrücklich ohne
Rückbildauswahl oder Bedeutung. Der Satz erhält damit keine zusätzliche bestimmte
Inhaltsaussage. Die alten14+4Überlappungen bleiben korrekt für ihre damalige
fünfteilige Liste; das Hinzufügen eines Ausgabetreffers ist keine übersetzte
Position und kein Beleg für eine vollständige Lesung. Alle120Bedeutungen bleiben
unzugewiesen. f75r.38 AABBA bleibt nur unter zusätzlicher Wortwahl eine Fünferfolge
vergangener Varianten. Die neue Nominalreihe löst deren Inhaltsproblem nicht.

latin_syntax_review bestätigte die genannten vollständigen Formen, Locator und
Stamm/Token-Unterscheidung separat im Druckbild. discriminating_test_review prüfte
die drei Ausgaben manuell ohne Programmausführung und bestätigte den offenen
a-Fall. Das sind methodische Quellen-/Rechenprüfungen, keine unabhängigen
historischen Zeugen oder Bestätigung einer Voynichlesung.

## Weiterarbeit

IDEA001116 erhält eine additive Quellenfolgerung, bleibt aber inconclusive.
Keine konkrete native Bedeutung, kein neues Alphabetstück und keine Sprache wird
bevorzugt. Eine nächste Auswahl braucht eine begründete gemeinsame Inhalts- oder
Schreibfolge, die mehr entscheidet als das Vorhandensein einer passenden Wortform.
Nicht automatisch weitere moderne Paradigmen, freie a/r/n-Werte oder ein Decoder.
Die reale Nichtpastform und der Stamm/Token-Unterschied bleiben dabei im Kontext.
Der anfängliche Eindruck einer reinen Vergangenheitsreihe darf nicht zur einzigen
Quellgrundlage werden; eine native gemeinsame Lemmafamilie ist trotzdem unbewiesen.

Reproduktion: TZ3_BRANCH_FORWARD_20261017.py importiert die unveränderte alte
TZ3_FORWARD_20261017.py, bindet ihren SHA und erhält den unbekannten a-Fall.
Die drei Quellformen, Beleggrenzen, manuelle Prüfung und neue vollständige
Profilabfrage sind beigelegt. Keine ganze moderne Edition wird publiziert.
Kein neuer GDT, native Auswahl, Voynichbildzugang, Reserve oder Relationsscore.
**0bestätigte übersetzte Wörter.**
