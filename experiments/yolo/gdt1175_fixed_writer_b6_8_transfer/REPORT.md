# GDT1175 — zweites Rezept überschreitet die feste Buchstabiergrenze

**Die unveränderte29-Stamm-Fassung wird nicht in den großen Statistiklauf
übernommen.** Im nächsten vollständigen vorhandenen Rezept b6.8 benötigt sie
175 von278 Arbeitszeichen, also62,95%, zum Ausschreiben einzelner Quellwörter.
Die vorher festgelegte Stoppschwelle war **mehr als50%**. Das ist ein
Kostenkriterium dieses Entwurfs, keine gemessene Voynich-Grenze.

Die festgehaltene manuelle Quellfassung lässt sich mit derselben Grammatik
schreiben und rücklesen. Es wurden keine Stämme, Endungen oder Buchstabenwerte
hinzugefügt. Das ist ein begrenztes positives Ergebnis: Bei unbekannten Wörtern
bleibt ein ausgeschriebenes Wort mit seiner gesetzten Anbindung erhalten;
seine Bedeutung muss der Leser aus der Quellsprache kennen. Der Entwurf hat
nicht selbst das Konzept Eigelb, die Zahl zwei oder den Ausdruck durchziehen
aus bekannten Grundbedeutungen hergeleitet.

## Der vollständige Versuch

Die erste geprüfte Einheit nach b6.7 war b6.8: ein gutes Gebackenes aus Lungen,
mit Speck, zwei Eidottern und Gewürzen; kleine Kugeln werden hergestellt,
durch einen nicht nochmals bezeichneten Zusammenhang gezogen und in Schmalz
gebacken. `gesettes`, `starckenn`, `zeyg` und weitere Wörter bleiben im Konto
ausdrücklich ausgeschrieben; der Text wird nicht still philologisch verbessert.
Die Auswahl erfolgte nach sichtbarer Vollständigkeit vor Kodierung und Kosten.
Der Cache war bereits historisch zugänglich und ist kein unabhängiger Holdout.

| Größe | Erstes Beispiel b6.7 | Fester Transfer b6.8 |
|---|---:|---:|
| Manuelle Quellaussagen/-fragmente |17|11|
| Geschriebene Wörter |59|31|
| Arbeitszeichen insgesamt |287|278|
| Davon vollständige Buchstabierpakete |35|175|
| Buchstabieranteil |12,20%|62,95%|
| Mittlere Wortlänge |4,86|8,97|
| Längstes Wort |14|17|

Die beiden Quellen sind unterschiedlich lang und zusammengesetzt. Diese Tabelle
ist kein standardisierter Sprachvergleich. Sie zeigt genau den Aufwand dieser
festgelegten Schreibung bei diesem Transfer. Der zweite Text enthält16
buchstabierte Wortvorkommen, darunter Lungen, Speck, Dotter, Teig, Schmalz sowie
Mengen-, Eigenschafts- und Richtungswörter. Alle sind einzeln ausgewiesen.
Die durchschnittliche Länge wird berichtet, aber nicht gegen eine neue
nachträgliche Schwelle getestet.

- [Ganzer Quelltext, Schrift und Rücklesung](artifacts/FULL_TEXT.md)
- [Vollständiges Quellenkonto und Annahmen](artifacts/SOURCE_ACCOUNT.json)
- [Quellenauszug mit TEI-Markierung](artifacts/SOURCE.xml)
- [Unabhängige Quellenprüfung vor Kenntnis der Kosten](artifacts/SOURCE_REVIEW.md)
- [Vorabvertrag](PREREGISTRATION.md), [Hashfestschreibung](artifacts/REGISTRATION_LOCK.json)
- [Zahlen und jede Buchstabierlast](artifacts/RESULT.json), [Validator](src/validate.py)

## Keine stillen Abkürzungen des Inhalts

Die nominale Zutatenfolge bekommt kein erfundenes „nimm“ oder „gib hinzu“.
`darvnter` wird deshalb als ausgeschriebenes Quellprädikat mit der erklärten
Anbindung erhalten; das gewöhnliche Referenzkürzel allein konnte diese Anbindung
nicht darstellen. „Zwei“ bezieht sich auf Dotter, nicht auf ganze Eier. Das
innere EGG/PLURAL erhält hier den geschriebenen Bestandteil eir und behauptet
keine unabhängige Zahl individueller Eier oder einen Dotter je Ei. Diese
Wortzusammensetzungslesart ist eine erklärte Annahme, keine neue allgemeine
Regel über Pluralreferenten.

`wintzigs` bleibt eine Mengenbestimmung; `gar klein` wird nicht zu bloß klein;
`starckenn` wird nicht zu HARD. `durch` erhält keinen erfundenen Teigbezug.
`back` wird nicht durch Sieden ersetzt. Pronomen bleiben unaufgelöst. Das
übersalz-Verbot bleibt NOT(EXCESS(SALT)), kein Verbot jeder Salzzugabe.
MAKE verlangt weiterhin seinen zweiten Platz; beim Teig steht dort UNSAID.
Diese konkrete Quellinterpretation und untypisierte QUOTE-Anbindung wurden
vor dem Lauf offengelegt und gegengelesen. Ein anderer Quellbaum könnte andere
Zahlen liefern; er wird hier nicht nachträglich ausgewählt.

## Prüfung und Entscheidungsgrenze

Die eingefrorenen zehn Eingabedateien einschließlich der alten Schreibregel,
der Quellfassung und des Runners blieben unverändert. Rücklesung und Schreiben
rekonstruieren die festgelegten Bäume; Zeilenumbrüche sind dabei unerheblich.
Die Zeichen- und Buchstabierkosten wurden zusätzlich direkt auf der erzeugten
Schrift mit einem getrennten Scanner gezählt. Der vollständige Quellext ist
lückenlos durch die elf aufeinanderfolgenden Ausschnitte abgedeckt. Ein erster
Validatorvergleich stolperte über ganzzahlige Wörterbuchschlüssel, die JSON als
Zeichenketten speichert; der Validator normalisiert jetzt seine Vergleichsseite
über JSON. Quelle, Runner, Grammatik, Ausgabe und Zahlen wurden nicht verändert.
Das ist eine technische Vergleichskorrektur, kein zweiter wissenschaftlicher Lauf.

**Entscheidung: STOP für den großen Lauf dieser festen Fassung.** Die kleine
Stammtafel trägt das zweite Rezept nach unserem vorher erklärten Kostenkriterium
zu schlecht. Kein nachträgliches Einbauen kurzer Wörter für Lunge, Speck oder
Eigelb rettet dieses Ergebnis. Ein geänderter Entwurf wäre ein neuer Kandidat
mit vorab bestimmtem Lern-/Wortschatzaufwand und einem neuen Falsifikationsplan;
er hätte dieses Rezept bereits gesehen. Ein anderer Zeichenschlüssel allein
behebt die fehlenden kurzen Begriffe nicht.

Das widerlegt weder sinntragende mittelalterliche Schriftsysteme noch
Abkürzungen, Wortbildung oder größere Wörterbücher allgemein. GDT1174s zehn
festen Statistikfehlschläge bleiben bestehen. Es wurde kein Manuskriptwort
übersetzt und keine Voynich-Statistik neu erhoben. Die gewünschte Sammlung von
zehn statistisch passenden Systemen bleibt unerreicht. Nächster Arbeitspunkt
ist die Auswahlprüfung der [zehn manuellen Konstruktionen](../../../research_registry/proposals/production_origin_supply_20261003/B6_7_MANUAL_DESIGN.md),
beginnend mit ihrem Wörterbuch-/Lernaufwand; kein automatischer Reparaturlauf dieses Modells.

Quelle: vorhandener CoReMA-B6-Cache, Zentrum für Informationsmodellierung,
Universität Graz, CC BY4.0. Keine neue Datenaufnahme oder Reservenöffnung.
Lokaler Konstruktionscheckpoint gemäß aktueller Route; nicht gepusht.
