# V16 R4 — vollständige Kanzlei-Rücklesung der zehn Seiten

Datum: 2026-08-21

Status: **absichtlich maximal konkrete YOLO-Arbeitstheorie**. Dies ist keine
Entzifferung, kein GDT-Ergebnis und keine Behauptung, dass die englischen
Ausdrücke den unbekannten Quelltext wörtlich wiedergeben. Die Aufgabe dieses
Entwurfs ist enger und zugleich radikaler: keine sichtbare Gruppe darf ohne
eine gegenwärtige Standardbedeutung bleiben.

## Entscheidung

Als Kanzleischreiber lese ich die zehn Seiten am besten als **stark gekürztes
iatromedizinisches Werkstattbuch in gewöhnlicher, aber nomenklatorartig
verdichteter Fachprosa**. Die Karte ist häufig die Kürzung eines ganzen
Ausdrucks, nicht eines Lautwortes. Bilder liefern stillschweigend das behandelte
Kraut, Gefäß, Körper-/Anwendungsfeld oder Himmelsdiagramm. Der Schreiber setzt
die knappen Ausdrücke aus einem gemeinsamen Grundstock und seitenlokalen
Exemplarkarten zusammen.

```text
ausformulierter Fachartikel oder Arbeitsgang
  -> im Bild bereits sichtbare Argumente auslassen
  -> häufige Wörter und ganze Formeln durch Ganzkarten kürzen
  -> seltene Pflanzen-, Stoff- und Arbeitsausdrücke aus dem Exemplar kopieren
  -> offene Prosa in Herbal, kurze geschlossene Rubriken in Biological
  -> Diagrammtext an den gezeichneten Ort binden
```

Die Zeile ist dabei nur der verfügbare Schreibraum. Ein Satz darf über eine
physische Zeile weiterlaufen. Ein angehängter DY/B3-Abschluss schließt eine
lokale Rubrik oder Arbeitsanweisung, nicht zwingend einen Satz oder Absatz.

Diese Lesung ist weniger elegant als eine reine technische Tabelle, erklärt
aber besser, warum Herbal große lokale Wortschätze besitzt, Biological viele
kurze Wiederholungsrubriken hat und dieselbe Werkstattkarte an Satzanfang,
Satzmitte oder -ende auftreten kann. Sie lässt außerdem reale Kanzleiphänomene
zu: Kürzungsformeln, *idem/ut supra*-Bezüge, Vorwegnahme am Zeilenende,
Wiederaufnahme am nächsten Zeilenanfang und gelegentliche Dittographie.

## Vollständigkeitsnachweis

Der ausführbare Bau erzeugt:

| Schicht | Umfang | unbelegte Standardbedeutungen |
|---|---:|---:|
| GDT327-Prosa auf sieben Seiten | 381 Ereignisse / 173 exakte Karten | 0 |
| sichtbare ZL3b-Astrogruppen | 395 Gruppen / 142 Loci | 0 |
| gemeinsames Ledger | 776 Zeilen | 0 |
| Lexikon einschließlich räumlicher Astroeinträge und F3 | 569 Zeilen | 0 |

Die vollständige, ereignisweise Rücklesung steht in
`V16_R4_COMPLETE_TRANSLATION_LEDGER.tsv`; die wiederverwendbare
Kartenbelegung in `V16_R4_COMPLETE_DEFAULT_LEXICON.tsv`; alle 199 physischen
Zeilen beziehungsweise Diagrammloci in `V16_R4_FLUENT_LINE_READINGS.tsv`.

Ein Einmaltyp erhält eine konkrete `CONTEXT_DEFAULT`-Lesung mit Konfidenz .16
bis .18. Das ist keine Ausflucht: die Bedeutung ist eingetragen und bleibt der
Default, bis eine andere Lesung mehr der zehn Seiten vereinfacht. Die geringe
Zahl kennzeichnet lediglich die leichte Revidierbarkeit.

## Kleines Lehrlexikon

| Karte/Konstruktion | Standardrücklesung | Konfidenz |
|---|---|---:|
| qokaiin | **nimm den nächsten Eintrag auf** | .68 |
| L/O | **mit ihm; ebenso unter derselben Rubrik** | .59 |
| AIIN | **im angegebenen oder üblichen Maß** | .48 |
| Y | **dieser Anteil / diese Portion** | .43 |
| CTHY | **wenn zubereitet und bereit** | .38 |
| Y–AIIN–Y | **beide Portionen nach demselben angegebenen Standard** | .44 |
| VAL-S | **ordnungsgemäß bereitsetzen; Rubrik schließen** | .34 |
| VAL-QE | **das temperierte warme Medium verwenden; Rubrik schließen** | .31 |
| VAL-Q | **bei der gewöhnlichen Grundeinstellung belassen; schließen** | .30 |
| VAL-L | **an der örtlichen Stelle übergießen/spülen; schließen** | .27 |
| O56 | **danach** | .30 |
| H10_LOCAL_2 | **von demselben** | .29 |
| häufiger CHEDY-Kartentyp | **mischen, bis es gleichmäßig ist** | .31 |
| CKHY-Kartentyp | **durch die verbundenen Leitungen** | .26 |

Das ist für eine kleine Werkstatt lehrbar. Ein Lehrling lernt zuerst etwa
zwanzig häufige Ganzkarten und vier Schließformeln. Seltene Pflanzenwörter und
spezielle Anwendungen muss er nicht frei erzeugen; er kopiert ihre Karte aus
dem Fach- oder Seitenexemplar. Hüllen wie `ch-`, `sh-`, `d-`, `q-` ändern in
diesem Modell meist den Schreibanschluss, nicht die Kernbedeutung.

## Durchgehende Herbal-Rücklesungen

Die eckige Klammer bezeichnet das vom bereits gezeichneten Pflanzenbild
gelieferte, im Text nicht wiederholte Subjekt.

### f10r, Absatz 1

> [Die abgebildete Pflanze] heißt in diesem Exemplar **Lokname 65F32**. Sie
> wird in einem bedeckten Gefäß aufbewahrt; hiervon wird der rotstielige Teil
> zu Pulver gestoßen und bei Magenbeschwerden im üblichen Maß verwendet. Die
> frische Zubereitung wird warm aufgelegt, ebenso unter derselben Rubrik,
> sobald sie bereit ist.

Die wörtliche Kartenfolge der beiden erhaltenen Zeilen ist vollständig im
Ledger; insbesondere sind `of the same`, `with it/likewise` und
`when prepared and ready` keine leeren Strukturwörter, sondern feste
Standardexpansionen.

### f10r, Absatz 2

> [Die Pflanze] findet sich am angegebenen Standort. Sobald sie bereit ist,
> nimmt man die zubereitete Flüssigkeit und den ausgepressten Saft, kocht ihn
> sanft und setzt **diese Portion, diese Portion, im üblichen Maß, diese
> Portion** an. Vor der Blüte gesammelt, wird die Flüssigkeit mit einer
> Handvoll derselben unter demselben Bezug verwendet; die bittere Portion wird
> in Öl aufbewahrt.

Die auffällige Folge `Y–AIIN–Y` bleibt hier ganz bewusst explizit: **zwei
Portionen unter demselben Maß**. Das vorangestellte zusätzliche Y kann eine
dreigliedrige Dosis, eine Abschreibwiederholung oder einen übernommenen
Formelvorlauf darstellen; es wird nicht gelöscht.

### f56r, einziger Absatz über sieben physische Zeilen

> [Die abgebildete Pflanze] wird im Frühling gesammelt. Danach wird die untere
> Wurzel im üblichen Maß genommen. Danach fügt man Weißwein hinzu, nimmt den
> vor der Blüte gesammelten kleineren Anteil und bringt ihn an die angegebene
> Stelle. **Lokname D6655** wächst im Schatten; von ihm wird der kleinere Anteil
> entnommen und die Zubereitung am Ausgang offen gelassen. Der Same, danach das
> getrocknete Blatt, wird im Schatten getrocknet. Die frische Zubereitung wird
> bei Magenbeschwerden verwendet und nochmals im Schatten getrocknet. Danach
> kommen frische Zubereitung und Honig hinzu; sie werden frisch gebraucht. Zum
> Schluss wird der bezeichnete Anteil der blassen Blüte im üblichen Maß
> genommen.

Diese Rücklesung zwingt eine echte Wasser-/Feuchtigkeitsmöglichkeit nicht auf
O56. Wasser kann hier als stilles Lösungsmittel oder in einer der lokalen
Einmalkarten vorkommen; die konkrete Seite nennt in diesem Default stattdessen
Wein, Honig, Schatten und eine offen gelassene Ableitung.

### Die übrigen Herbal-Seiten

- **f11r:** Artikel über einen zweiten einfachen Arzneistoff: Blüte, Blatt und
  Zubereitungsmaß werden beschrieben; das einzelne geschlossene Stück gibt die
  abgeschlossene Aufbewahrungsanweisung.
- **f55v:** kompakter B-geschriebener Pflanzenartikel: nächsten Eintrag nehmen,
  zwei Portionen ansetzen, mischen, bereiten und die örtlichen Anwendungen in
  geschlossenen Rubriken festhalten.

Jede einzelne Karte dieser beiden Seiten ist im Ledger konkret ausgebaut; die
Paraphrase lässt keine zusätzliche unsichtbare Textzeile entstehen.

## Durchgehende Biological-Rücklesung: f82r

Hier liefern Becken, Leitungen und Gefäße die stillen Argumente. Die acht
physischen Zeilen werden nicht als acht Sätze erzwungen.

| Locus | fortlaufende Arbeitslesung |
|---|---|
| f82r.2 | Anwendung abschließen; die zusammengesetzte Mischung halten; dann einsetzen; diese Portion; warmes temperiertes Medium verwenden; beide Portionen verbinden; an der zweiten Öffnung fortfahren. |
| f82r.3 | Sanft warm halten; klar abseihen; am zweiten Leitungsstück fortfahren; durch ein Tuch und durch die verbundenen Leitungen führen; den nächsten Eintrag aufnehmen. |
| f82r.4 | Den am vorigen Zeilenende vorweggenommenen Eintragskopf wieder aufnehmen; unter derselben Einstellung in das breite Gefäß geben; abziehen; das vorbereitete Öl mit beiden Portionen verbinden und örtlich auftragen. |
| f82r.7 | Reines Wasser zusetzen; für dieselbe Dauer am örtlichen Platz arbeiten; ordnungsgemäß bereitsetzen; warm halten; sanft erwärmen; die erste Öffnung benutzen, bis die Flüssigkeit klar wird. |
| f82r.19 | Dann einsetzen, von demselben nochmals einsetzen, das temperierte Medium verwenden und die klare Flüssigkeit abziehen. |
| f82r.23 | Bis zur Klärung unter gleicher Einstellung erwärmen; den eingetauchten Teil im üblichen Maß behandeln; vollständig eintauchen; danach bei Grundeinstellung belassen und den unteren Ausgang schließen. |
| f82r.26 | Mit dem Spülen beginnen; warmes Medium an der angegebenen Stelle verwenden; kühles Wasser zu gleichen Teilen und das angegebene Maß mit vorbereitetem Öl verbinden; den nächsten Eintrag aufnehmen und warmes Wasser verwenden. |
| f82r.27 | Abziehen; warmes Wasser eingießen und an der zweiten Öffnung wiederholen; warmes Medium verwenden; die angegebene Portion einnehmen; am Platz verbinden; warmes Medium nochmals verwenden; schließlich gleiche Anteile mischen. |

Die zweimalige exakte VAL-QE-Auswahl in f82r.27 bedeutet in dieser konkreten
Lesung: **derselbe temperierte Mediumzustand wird in Zelle 3 und Zelle 6
erneut gewählt**. Das ist kein bloßes Satzzeichen. Es kann dennoch eine
kopierte Stencilantwort sein; die Bedeutung bleibt bis zu einer besseren
Gesamtlesung stehen.

## Vollständige Astro-Rücklesung

Hier gilt eine getrennte Kartenwelt. Keine Prosa-Tupelidentität wird in die
Diagramme importiert.

### f67r2

> Wähle einen der sieben Himmelsregenten **Saturn, Jupiter, Mars, Sonne, Venus,
> Merkur, Mond**; ordne ihn einer der zwölf Tierkreisabteilungen **Widder bis
> Fische** und einer der zwölf Häuserfunktionen **Leben, Güter, Geschwister,
> Haus, Kinder, Krankheit, Ehe, Tod, Reise, Amt, Freunde, Gefangenschaft** zu.
> Lies anschließend die dazwischen geschriebene Anwendungsregel und die
> zentrale warm/kalt–trocken/feucht-Bedingung.

Die sieben Planetennamen und Häuserfunktionen sind konkrete R4-Defaults, keine
Lautlesungen. Sämtliche 190 sichtbaren Gruppen, einschließlich der drei langen
Prosazeilen f67r2.72–74, sind einzeln als Auswahl-, Anwendungs-, Verbots-, Maß-
oder Fortsetzungswort ausgebaut.

### f68r1

> Der Mittelpunkt bedeutet **der Mond als Besitzer des Katalogs**. Die 28
> nichtzentralen Sterne bedeuten jeweils **die räumliche Mondstation an genau
> diesem gezeichneten Quelllocus**. Die ersten vier Prosazeilen erklären, dass
> man eine Station nach ihrem Platz identifiziert und danach ihre Regel
> nachschlägt. Die fünf Zentrumskarten lesen: **der Mond – regiert – den ganzen
> Kreis – von achtundzwanzig – Mondstationen**.

Es wird ausdrücklich keine Startstelle und keine Rundlaufrichtung erfunden.
`f68r1.9` bis `.36` sind räumliche Identitäten, keine behauptete Reihenfolge
1–28. So erhält jedes Wort Bedeutung, ohne die bekannte topologische Grenze zu
verletzen.

### f69v

> Die drei Kreistextbänder geben die Benutzungsregel: **wenn der Mond die
> Station erreicht, prüfe den bezeichneten Eintrag; bei günstiger Bedingung
> führe die Anwendung aus, bei widriger unterlasse sie; halte das übliche Maß
> ein und gehe zur nächsten Station weiter**. Die 28 Radialstellen bilden die
> Arbeitstafel. Ungerade Stellen erhalten als Default „führe die bezeichnete
> Anwendung aus“, gerade Stellen „unterlasse die bezeichnete Anwendung“.

Die LONG/SHORT-Alternation wird damit konkret als positive/negative
Wahlrubrik gelesen. Jedes zusätzliche Wort einer zweigliedrigen Radialstelle
bedeutet „wiederhole die Stationsregel“. Diese Entscheidung ist schwach, aber
vollständig und leicht durch eine bessere Interpretation ersetzbar.

## Ganze Seiten in einem Satz

| Seite | jetziger Default |
|---|---|
| f10r | Pflanzenmonographie mit Lokalname, Aufbewahrung, Magenmittel, Saft, Maß und Ölzubereitung. |
| f11r | Pflanzenmonographie mit sichtbarer Blüte/Blattbeschreibung und geschlossener Konservierungsanweisung. |
| f55v | kompakte Pflanzenzubereitung in B-Rubriken mit Mischen, Portionieren und örtlicher Anwendung. |
| f56r | Pflanzenmonographie über Frühjahrslese, Wurzel/Blatt, Wein, Honig, Schatten und Dosierung. |
| f81v | Bad-/Spülregister mit wiederholter Grundeinstellung und zwei benachbarten lokalen Spülungen. |
| f82r | Becken-/Leitungsregister mit Wärme, Wasser, Öl, Klärung, Öffnungen und wiederholtem temperierten Medium. |
| f83r | umfangreiches Anwendungsregister mit Portionen, Leitungswegen, Setzen, Spülen, Abziehen und vielen geschlossenen Teilschritten. |
| f67r2 | Selektor aus sieben Regenten, zwölf Tierkreisabteilungen, zwölf Häusern und zentralen Qualitäten. |
| f68r1 | räumlicher Mondkatalog: ein zentraler Besitzer und 28 nichtzyklisch geordnete Stationen. |
| f69v | 28-stellige Wahltafel mit wechselnder Ausführen-/Unterlassen-Rubrik und kreisförmiger Gebrauchsanweisung. |

## Abschreib- und Nullaudit

1. **f82r.3→4 qokaiin:** beste Werkstattlektüre ist vorweggenommener
   Eintragskopf plus Wiederaufnahme; einfache Dittographie bleibt ein echter
   Rivale. Beide Kopien bedeuten trotzdem „nächsten Eintrag aufnehmen“.
2. **benachbarte gleiche Schließkarten:** können gleiche Slotbelegung oder
   Dittographie sein. Die Rücklesung verdoppelt den Arbeitsgang nicht heimlich,
   sondern schreibt beide Auswahlereignisse aus.
3. **Zeilenfüllung:** erklärt Stellung und Wiederaufnahme, aber nicht die 173
   stabilen Kartenidentitäten allein. Deshalb bleibt normale gekürzte Prosa
   stärker als bedeutungsloses Füllmaterial.
4. **Kopiertes Exemplar:** erklärt den großen seltenen Herbal-Bestand. Eine
   seltene Karte kann eine ganze Fachphrase repräsentieren und von mehreren
   Händen richtig kopiert werden, ohne produktiv zerlegt zu werden.
5. **Polysemiekosten:** der vorliegende Schlüssel benutzt für jede exakte
   Prosakarte genau eine englische Standardphrase. Registerkontext liefert
   stille Bildargumente, aber keine ad-hoc zweite Bedeutung.

## Was diese konkrete Lesung ersetzen würde

Eine neue Deutung gewinnt, wenn sie auf denselben 776 sichtbaren Gruppen
weniger Bildargumente einsetzen muss, wiederholte exakte Karten gleichmäßiger
liest und f10r/f56r/f82r in besseres fortlaufendes Fachdeutsch überführt. Bis
dahin bleiben auch die schwachen Einmalzuweisungen stehen. Kein Ereignis fällt
auf „unbekannt“ zurück; es bekommt entweder eine bessere konkrete Lesung oder
behält den jetzigen Default.

## Seal und Unabhängigkeit

Verwendet wurden ausschließlich die zehn freigegebenen Seiten, der f84-freie
GDT327-Interlinear und vor dem Materialisieren seitengefilterte
Transkriptionszeilen. f84 und f84r wurden weder geöffnet noch abgefragt. Die
V16-Ausgaben von R1, R2 und R3 wurden nicht gelesen.
