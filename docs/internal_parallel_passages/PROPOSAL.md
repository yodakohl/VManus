# Interne Parallelpassagen mit festem Umsetzer

5. September 2026. Vorschlag auf den ausdrücklichen Wunsch nach einer wesentlich
stärkeren Entzifferungsidee. PROPOSED_UNEXECUTED: keine Manuskript-Paarung gefunden,
keine neue Auswertung, kein Schlüssel und kein GDT-Versuch registriert.

## Idee und möglicher Gewinn

Wir suchen unterschiedlich geschriebene Passagen, zwischen denen eine feste
Zuordnung vollständiger Quellgruppen gilt. Der Suchhinweis ist ihre geordnete
Wiederholungsstruktur: dieselben Wiederkehrpositionen trotz anderer sichtbarer
Gruppen. Eine solche Zuordnung muss anschließend vorher ausgeschlossene
vollständige Textfolgen vorhersagen. Bloße Musterähnlichkeit ist kein Erfolg.

Mögliche Ursachen wären eine systematische Zweitschreibung, eine wiederholte
Vorlage mit konsistent ersetzten Inhalten oder mechanisches Kopieren. Gleicher
Inhalt und unterschiedliche Chiffrierung sind Hypothesen, keine Prämissen.
Auch sinnfreier Text kann systematisch umgeschrieben werden. Der unmittelbare
Erfolg wäre deshalb ein ausführbarer interner Umsetzer mit bestätigten
Parallelstellen, keine Übersetzung und kein Beweis sprachlichen Inhalts.

Das hat potenziell mehr Entzifferungswert als eine Endzeichenbreite: Viele
Schreibgruppen würden durch dieselbe überprüfbare Transformation miteinander
verbunden. Spätere Lesungen müssten das systematische Verhältnis ganzer
Passagen erklären. Die Korrespondenzen dürfen nicht stillschweigend als
Gleichbedeutung oder allgemeine Normalisierungsregel in ein Wörterbuch wandern.

## Ein ausschließlich erfundenes Miniaturbeispiel

```text
Entdeckungsabschnitt A: A B C A D B E C
Entdeckungsabschnitt B: p q r p s q t r
Wiederholungsmuster:    1 2 3 1 4 2 5 3
```

Das erzwingt A→p, B→q, C→r, D→s, E→t, sofern eine bijektive Umbenennung
angenommen wird. Nach dem Einfrieren lautet die konkrete Vorhersage:

```text
Ausgeschlossener Quellabschnitt: D A E B
Vorhergesagte Zielzeichenfolge:  s p t q
```

Die Zielzeichenfolge darf beim Lernen und Auswählen des Umsetzers nicht bekannt
sein. Ein tatsächliches `s p q t` wäre ein Fehler, kein Anlass zur Reparatur.
Die Buchstaben sind Demonstrationsvariablen; keine Zeile stammt aus Voynich.
Eine Folge aus ausschließlich verschiedenen Gruppen liefert praktisch keine
Wiederholungsbeschränkung. Eine Handvoll solcher Beispielgruppen wäre im
Manuskript auch mit Wiederholungen kein ausreichender Beleg.

## Der vorgeschlagene Hauptversuch

1. **Beobachtung erhalten.** Nur den bereits zugelassenen Textbestand nutzen.
   Vollständige rohe Gruppen mit Sonderzeichen, Grenzen und Alternativlesungen
   bewahren. Keine angenommenen Morpheme, deutschen Bedeutungen oder BPE-Einheiten
   vorgeben. ZL3b/IT2a/RF1b sind alternative Lesungen desselben Manuskripts.
   Die Transkriptionsreihenfolge wäre eine explizite räumliche Serialisierung,
   keine neu behauptete Schreibchronologie. Kreistexte werden nicht unbemerkt
   zu gewöhnlichen Absatzfolgen; die erste genaue Registerauswahl bleibt vor
   Ausführung festzulegen.
2. **Ausschluss vor der Suche.** Entdeckung und Bestätigung nach physischen
   Folios beziehungsweise vorher festgelegten disjunkten Bereichen trennen.
   Ein Bestätigungsbereich darf auch nicht als überlappendes Suchfenster oder
   über eine Alternativlesung in die Entdeckung gelangen. Nur die Entdeckung
   liefert Wiederholungsmuster, Kandidaten, Ausrichtung und die feste bijektive
   Abbildung. Längen und Mindestmengen werden vor der realen Suche registriert.
3. **Exakte Vorhersage fordern.** Die eingefrorene Abbildung muss an mehreren
   ausgeschlossenen Stellen gelten, besonders wertvoll wäre Transfer auf
   weitere physische Folios. Nur bereits bestimmte Gruppenwerte zählen als
   Vorhersagen; neue Typen bleiben unbekannt. Nötig sind substanzielle Abdeckung,
   mehrere nichtidentische Typzuordnungen und mehr als häufige Einzelwörter.
   Keine Umordnung, freien Synonyme, paarweisen Schlüsselreparaturen oder
   nachträglichen Gruppenzerlegungen. Eine reine Identitätsabbildung wäre
   gesondert bekannte wörtliche Wiederholung, nicht der neue Hauptbefund.
4. **Suchaufwand und Gegenmodelle ernst nehmen.** Die komplette Suche inklusive
   aller Orte, Abbildungen und Auswahlentscheidungen auf entsprechenden
   Gegenkontrollen durchführen. Häufigkeiten, lokale Wiederholungen und
   Schablonen müssen passende Kontrollen erhalten. Unverbundene Texte mit
   ähnlicher Wiederholungsdichte dürfen keinen scheinbar übertragbaren Umsetzer
   erzeugen. Echte künstliche Umbenennungen müssen hingegen rekonstruierbar
   sein. Auch umbenannter sinnfreier Text sollte als Umbenennung erkannt werden;
   das demonstriert die semantische Grenze des Verfahrens.
5. **Fundstellen selbst am Bild prüfen.** Ich betrachte gefundene Kandidaten im
   Original und prüfe Grenzen, Schriftformen und die Bild-/Textumgebung.
   Bilder dürfen eine bereits gefundene Korrespondenz erläutern, aber keine
   schlecht passende Textabbildung durch eine plausible Geschichte retten.
   Nicht visuell zugelassene Fundseiten müssten vor Bildzugriff separat
   aufgenommen werden; der Vorschlag nimmt keine neue Seite auf.

Ein späteres Relationsevidenzpaket muss die vorhandene GDT388-Prüfung durchlaufen;
eine formale Vorhersage wird dadurch nicht automatisch score-ready Semantik.
Eine zusätzliche unabhängige Kette A→B→C wäre ein besonders starker Folgetest:
Ihre zusammengesetzte Abbildung müsste weitere A→C-Stellen vorhersagen. Das ist
kein Ersatz, falls schon die erste feste Abbildung nicht überträgt.

## Worin der gezielte Duplikatabgleich die Unterschiede sieht

- GDT829 suchte unveränderte lange Literalumgebungen um l/m. Hier gibt es
  weder l/m-Ziel noch gekürzte Flanken: die neue Hypothese ist eine feste
  nichtidentische Abbildung vieler vollständiger Gruppen über ganze Passagen.
- GDT342 anonymisierte bereits bekannte Konzeptidentitäten in externen
  Parallelrezepten und verglich graphbasierte Ähnlichkeit. Die realen
  Identitäten beziehungsweise Referenzen waren dort Teil des Vergleichsaufbaus.
  Der jetzige Gegenstand wäre ein exakter aus Text abgeleiteter Umsetzer mit
  ausgeschlossenem Vorhersagetest.
- GDT343 prüfte zusätzlichen Prozessfluss bei bereits global bekannten,
  anonymisierten Identitäten. Das liefert keine hier benötigte Zuordnung.
- GDT374 suchte lokale atomare Umschreibungsoperatoren. Sein Negativbefund
  betrifft diese Repräsentation und deren Test, nicht den vorgeschlagenen
  globalen Vollgruppen-Umsetzer.
- GDT001 prüfte viele Chiffren und Sprach-/Kompressionsmodelle. Eine verbesserte
  Sprachbewertung allein wäre daher kein neuer Ansatz. Hier wird keine Sprache
  optimiert; Ziel ist konkrete ausgeschlossene Textrekonstruktion aus einer
  einzigen intern gewonnenen Abbildung.

Die einschlägigen Primärberichte sind GDT829 REPORT, GDT342/343 COMPARATOR_REPORT,
GDT374 REPORT und GDT001_CURRENT_SUMMARY. Ein weiterer unabhängiger interner
Reviewer verglich PP001 und GDT807. In dieser gezielten Prüfung wurde kein
identischer abgeschlossener Test gefunden; vollständige Neuheit im teils
kuratierten Archiv oder in der öffentlichen Forschung wird nicht behauptet.
Es wurde nicht nach öffentlichen Entzifferungsansätzen gesucht.

## Entscheidung und Grenzen

Dies ist der empfohlene neue Hauptkandidat. Die Aussicht beruht auf dem möglichen
Erkenntnisgewinn eines übertragbaren Umsetzers; die Wahrscheinlichkeit, dass das
Manuskript dafür genügend passende Passagen enthält, wurde nicht geschätzt.
Es liegt noch kein realer Kandidat vor. Ein Scheitern würde diese feste Art der
Zweitschreibung treffen, nicht Sprache, Bedeutung oder Chiffren insgesamt.
Keine nachträgliche Lockerung auf freie Synonyme oder beliebige Segmentierung.

Die gekreuzte Wiederverwendung gezeichneter Pflanzenteile wurde als zweite
Idee erwogen. Ein hinreichend eindeutiges, textunabhängig erfasstes Viererpaket
ist bisher nicht nachgewiesen; deshalb wird daraus kein verfügbarer Anker
behauptet. Historische Kräuterplaintexts besitzen weiterhin keine gesicherte
Voynich-Überlieferungsbindung.
