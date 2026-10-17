# Drei historische Formen, ein Teilschreiber, weiterhin keine Lesung

**IDEA001116 bleibt eine rohe Quellkonstruktion. Kein Wortwert wird bevorzugt.**
Eine einzige partielle Schreibtabelle erzeugt drei vorhandene Voynichformen aus
dem neuen historischen Variantenbeleg. Das prüft die gemeinsame Konstruktion;
es identifiziert weder eine Sprache noch einen Lautwert oder eine Übersetzung.
Die Tabelle wurde nach Kenntnis der Zielgestalten gewählt. Die drei Quellformen
gehören zu einem Eintrag und sind keine drei unabhängigen Bedeutungsanker.

## Die gemeinsame Regel

Die dargestellten Quellbuchstaben sind normalisierte Transliterationen:
Kleinschreibung, ḳ→k und ı→i. Ausgegeben werden EVA-Zeichenbezeichnungen,
keine behaupteten historischen Lautwerte. Sieben Fälle genügen:

| Quellzeichen und Position | Ausgabe |
|---|---|
|k am Wortanfang|q|
|k sonst|k|
|o|o|
|s|e|
|d oder t|d|
|u oder i am Wortende|y|
|u oder i sonst|e|

Alle anderen Quellzeichen bleiben unzugewiesen. Es gibt keine Nullzeichen,
wortweisen Ausnahmen oder stillschweigende Alphabetvervollständigung.

| Eingabe | Ausgabe | Status des historischen Inputs |
|---|---|---|
|kokudı|qokedy|Haupttextalternative|
|koksudı|qokeedy|Haupttextalternative desselben Eintrags|
|koktı|qokdy|nur editionsgestützte Zwischenzeilenform|

Die vollständigen Quellgrenzen stehen im [Originalbefund](TUHFET_ORIGINAL_VARIANTS_20261017.md).
Keine Variante wurde aus der Quelle gelöscht, um die Tabelle zu retten.
Die Regel erzeugt außerdem koku→qoky und koksu→qokey. Das sind hier konstruierte
Stammzeichenfolgen, keine zusätzlich belegten Imperative oder eigenständigen
historischen Wörter. Ihre weiteren Ausgaben sind exponierte Folgen, keine
blinden Vorhersagen. Die [Vorwärtsdatei](TZ3_FORWARD_20261017.py) liefert alle
fünf Ausgaben; ein separater Leser hat sie ohne diesen Code manuell geprüft.

## Was die tatsächlichen Wortprofile verlangen

Vor einer Präferenz wurden die vorhandenen exact-wholeform-Profile abgerufen:
Häufigkeit, Abschnitte, Selektoren, Positionen, Wiederholungen, Nachbarn und
Vorevidenz getrennt je Leser. Ganze Wörter bleiben von eingebetteten Strings
getrennt. Die [vollständigen Werkzeugprofile](TZ3_EXISTING_PROFILES_20261017.json)
bleiben maßgeblich.

| Ganze Form | ZL3b | IT2a | RF1b |
|---|---:|---:|---:|
|qokdy|4|4|1|
|qokedy|248|246|164|
|qokeedy|291|288|209|
|qoky|135|138|124|
|qokey|95|94|90|
|dy|225|221|170|

IT2a qokedy hat14unmittelbare gleiche Paare, qokeedy17. Ihre breiten
Verteilungen bevorzugen das konkrete historische Geruchsverb nicht; ebenso
wenig wählen sie automatisch ein Funktionswort. Die drei Leser bestätigen
nicht drei verschiedene Manuskripte. Freies dy erhält aus dem eingebetteten
String keine Vergangenheitsfunktion.

## Die ganze vorhandene Passage bleibt sichtbar

Dieselben120 IT2a-Gruppen f75r.32–46 wurden vollständig aus dem alten1386Cache
übernommen. Es ist keine neue Abfrage, Bilddeutung oder unabhängige Prüfpassage.
Die drei angepassten Ausgabetypen treffen14Positionen:8qokedy,6qokeedy,0qokdy.
Die zwei zusätzlichen Stammstrings treffen4Positionen:1qoky und3qokey.
Das sind **keine18übersetzten Wörter**; alle120Bedeutungen bleiben unzugewiesen.
102andere Positionen liegen außerhalb dieser fünfteiligen Ausgabeliste.
Auch die18Treffer werden durch den Code nicht eindeutig zurückgelesen.

```text
f75r.32  polshy dal shedy qokain das chsdy shedy qokar shedy ldy
f75r.33  qokeey lshedy qol chedy qokain chcthedy ltedy darom
f75r.34  solkedy okal dar oty otar otar ol kain olkedy
f75r.35  qokain sheety qokain dar dar shedy qokar ol dy
f75r.36  sol keedy qokeedy qokey okar otar dar dar dy
f75r.37  qokedy dy sheety qokedy qokchdy qokechdy lol
f75r.38  qokeedy qokeedy qokedy qokedy qokeedy ldy
f75r.39  yshedy qokeedy qokchdy olkeedy otey koldy
f75r.40  dar shedy qokain shedy dal keedy rshedy
f75r.41  sokeedy qokeedy oteedy qoky dykeedy sy
f75r.42  dshedy qokedy c qoteey qoteedy dar
f75r.43  yshedy chekar oldy qokain chkar otar oldy
f75r.44  dchedy sain okedy qokedy otedy okoldy otar otam olaiin chdar dy
f75r.45  sshedy shckhy qokey okedy sorol oty otedy qotedy otedy okaiin
f75r.46  qokey qokedy sheol qokedy dain shedy otol chedy olor
```

Der bekannte Fünferanfang .38 ist besonders wichtig. Wählt man ZUSÄTZLICH zu
der Tabelle genau die drei angepassten historischen Rückbilder als Lesung,
erhält man dort fünf Formen desselben vergangenen Verbeintragstyps:

    VarianteB VarianteB VarianteA VarianteA VarianteB

**Der Code allein erzwingt diese Wortauswahl nicht.** s und die hohen Vokale
fallen auf e zusammen; d/t ebenfalls. Weitere Rückbilder und die unzugewiesenen
Quellzeichen sind nicht bezahlt. Die konkrete historische Wortwahl ist also
eine zusätzliche, unbestätigte lexikalische Bindung.

Unter jener Bindung verlangt die Wiederholung eine tatsächliche Inhaltsfunktion.
Eine Liste erwähnter Formen, Iteration oder andere Textfunktionen sind möglich;
es gibt keinen Grammatik- oder Sprachausschluss. Aber eine zusammenhängende
gewöhnliche Lesung ist hier noch nicht erklärt. Bloß daneben geschriebene
unbekannte Wörter oder zusätzliche freie Schnittstellen würden sie nicht liefern.

## Entscheidung

Der vorhandene Wortprüfer meldet NOT_READY_FOR_PREFERENCE und
NO_TESTABLE_PREDICTIONS. Das ist seine Kontrolle deklarierter fehlender Accounts
und leerer Vorhersagen, kein semantischer Test und keine Widerlegung der Tabelle.
Die unabhängige manuelle Prüfung bestätigt die fünf Vorwärtsausgaben und genau
diese begrenzte Aussage. Die tatsächliche Vorwärtsregel ist neu als rohe
Konstruktion; die allgemeine Methode ist schon aus German14bekannt.

Die positionsabhängigen k-Werte und die s/Vokal- beziehungsweise d/t-Zusammenfälle
sind angepasste Parameter, keine identifizierten Schriftwerte. Ein vollständiges
Alphabet, ein Quellwortschatz, eindeutige oder kontextuell bezahlte Rücklesung und
eine Inhalts-/Wortverteilungsbegründung fehlen. Andere QOKformen und die DALfamilie
bekommen keine neuen Werte. Kein größerer Decoder oder neues Korpus wird daraus
automatisch begonnen. Eine begründete lokale Folge darf später untersucht werden;
ein bereits bestätigtes Wort ist dafür keine pauschale Voraussetzung.

GDT1342s feste frühere-Seitenreferenz bleibt gescheitert. GDT787s begrenzter
Formenvergleich bleibt bestehen; drei Anpassungen erzeugen keinen universellen
Bausteinsinn. GDT1388s ursprüngliche Ergebnisse bleiben unverändert: Hier wird
nur dessen schon bekannter Kontext verwendet, kein alter Solver gerettet.
IDEA1108s andere historische Suffixpaarbedingung bleibt offen. Ein nicht eindeutiger
Rohcode ist weder eine Sprachwiderlegung noch eine neue allgemein gültige Grammatik.

Reproduktion: TZ3_FORWARD_20261017.py; vorhandenes words-profile-Werkzeug mit den
sechs Tabellenformen; words review TZ3_WORD_REVIEW_CONTRACT_20261017.json.
Das120er-Quellenkonto erhält jede ID, Rohform und Grenze. Kein neuer GDT,
keine Bild- oder Datenzulassung, Reserve, rohe gemischte TSV oder Relationswertung.
**0bestätigte übersetzte Wörter.** Arbeitsblock16:21:48–17:01:48UTC umfasst
Vorbereitung, Quellkonstruktion, vorhandene Werkzeugprüfung und Veröffentlichung.
Kein präreregistrierter semantischer Versuch wird behauptet.
