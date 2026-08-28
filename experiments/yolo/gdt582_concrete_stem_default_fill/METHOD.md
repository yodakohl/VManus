# GDT582 method

## Frage

Kann die vollständige GDT581-Grammatik mit einem kleinen, vorhersagenden
Arbeitscodebuch konkret belegt werden, sodass jeder geschriebene Slot eine
Defaultbedeutung besitzt und ganze Passagen in allen fünf Registern lesbar
bleiben? Gesucht ist ausdrücklich keine Ein-Wort-pro-Oberfläche-Liste, sondern
eine ungefähr zeitgenössisch plausible Mischung aus wiederverwendbaren
Fachkürzeln und gelernten Ganz- oder Namenswörtern. „Vorhersagend“ bedeutet in
diesem Pass nur: Eine bereits von GDT581 segmentierte neue Occurrence einer
bekannten `slot_value×register`-Zelle erhält denselben Default. Neue
Oberflächen, Seiten oder Segmentierungen werden nicht vorhergesagt.

## Eingaben

GDT582 verwendet ausschließlich die bereits zugelassenen, f84-freien
GDT581-Ausgaben:

- 15.889 vollständig gehostete Slots;
- 4.026 geerbte Aliaskanten;
- 5.122 laufende Ereignisse und 793 feste Aussagen;
- dreißig feste Seitenprofile;
- 744 eigenständige lokale Karten;
- 107 exakt abgegrenzte Namensslots.

Keine Seite, Transkription, Atomgrenze, Event-ID, Aussagezuordnung, Karte,
Namensspanne oder GDT581-Hostentscheidung wird verändert. f84 und f84r bleiben
gesperrt.

## 1. Vier Bedeutungsarchitekturen vergleichen

Vier Architekturpakete werden auf demselben Slotuniversum als Scorecard
gegenübergestellt:

1. `REGISTER_HYBRID_CODEBOOK`: kurzer Kern, registerabhängige Ausformulierung,
   owner- oder klassengebundener Name;
2. `UNIVERSAL_APOTHECARY_ONLY`: jede produktive Analyseklasse erhält überall dieselbe
   physische Rezeptbedeutung;
3. `UNIVERSAL_TABLE_ONLY`: jede Analyseklasse erhält überall dieselbe Tabellen- oder
   Positionsbedeutung;
4. `LEARN_EVERY_REGISTER_SURFACE`: jede Register×Oberfläche wird separat
   gelernt.

Nur Pack 1 wird anschließend vollständig gerendert. Es deckt alle 13.702
Inhalts-Slots mit 305 Kartenebenen ab und kann trotzdem bereits segmentierte
Zusammensetzungen aus bekannten Klassen lesen. Die Scorecard markiert bei Pack 2 heuristisch
2.666 produktive Himmels-Slots als fremde Apothekerdomäne; bei Pack 3 liegen
9.490 produktive Pflanzen-, Bad- und Drogen-Slots außerhalb der Tabellendomäne.
Pack 4 benötigt 2.749 gelernte Schlüssel und sagt keine neue Komposition
voraus. Diese drei Rivalen werden nicht als eigene Vollausgaben gerendert; ihre
Zahlen sind Architekturkosten, keine gemessenen Übersetzungsfehler.

## 2. Zwei Stufen des produktiven Arbeitswörterbuchs

Jede der 42 produktiven GDT581-`slot_value`-Klassen erhält genau einen kurzen
invarianten Kern, zum Beispiel:

- `Y = CURRENT_GOOD_OR_BATCH`;
- `CH = TAKE_OR_EXTRACT`;
- `K = TRANSFER_OR_ADD`;
- `SH = HOLD_OR_REST`;
- `T = ADJUST_OR_TEMPER`;
- `AIIN = MEASURE_OR_VALUE`;
- `OR = UNIT_OR_BATCH`;
- `O = FORM_OR_MODE`.

Der Kern wird danach in seinem Register konkret ausgesprochen. So wird `CH`
im Pflanzen- oder Drogenregister zu „entnehmen oder ausziehen“, im Badregister
zu „entnehmen oder ablassen“ und im Himmelsregister zu „ablesen“. `T` wird
entsprechend „einstellen oder temperieren“, „regulieren“ oder „einstellen“.
Nur tatsächlich belegte Klasse×Register-Zellen werden erzeugt; das ergibt
181 Zellen statt eines künstlichen 42×5-Vollrasters.

Der Kompositionsweg lautet immer:

```text
geschriebene Slot-Occurrence
→ produktive GDT581-Analyseklasse
→ kurzer Kern
→ Registerrealisierung
→ exakter GDT581-Host bzw. Owner
```

`D_ADDR`, `CARRIER_Q`, `LOCAL_CHAR_F` und verwandte Werte sind dabei
Analyseklassen, keine unmittelbar beobachteten Manuskriptwörter. Ein
Wörterbucheintrag darf nur eine kurze Funktion tragen. Lange Sätze
wie „Pflanzenmaterial zeitgebunden beschaffen“ sind ausgeschlossen; ihre
Einzelteile müssten aus mehreren Slots und dem Kontext entstehen.

## 3. Gelernte Namen und konkrete Stoffe

Die 107 GDT581-Namensoccurrences bilden 80 `content_class × raw_name_core`-
Typen. Jede Klasse erhält ein austauschbares Hauslexikon:

- 60 Occurrences für Sternringpositionen;
- 38 Drogen- oder Zutatenoccurrences;
- sieben Bad-, Zulauf- oder Auslassstationen;
- zwei abgebildete ganze Pflanzen.

Die Drogenkarten werden absichtlich konkret gefüllt, etwa `d=Wasser`,
`y=Wein`, `or=Olivenöl`, `s=Salz`, `yd=Honig`, `cheo=Essig`,
`opchor=Safranblüte`, `opor=Pfefferkorn oder Samen`,
`dchos=Ingwerwurzel`, `yt=Salbeiblatt`. Diese Gleichungen gelten nur innerhalb
der ownerbestimmten Klasse `DRUG_OR_INGREDIENT_OBJECT`. Sie sind keine
portablen Laut- oder Stammbedeutungen.

Groß- und Kleinschreibung markieren getrennte Namespaces: die gelernten rohen
Namenskerne `dy`, `e` und `chd` sind nicht die analytischen produktiven Klassen
`DY`, `E` und `CHD`; ebenso wenig sind `d/y/or/s` automatisch
`D_ADDR/Y/OR/S`.

Die zwei laufenden gelernten `LOCAL_X`-Slots bleiben voneinander getrennt:
`RUNNING:G515-E0410@2` erhält „Krankheit oder Beschwerde“,
`RUNNING:G515-E0438@2` „Heilmittel oder Heilwirkung“. Auch diese Werte sind
explorative Ownerdefaults, keine produktiven Wörter.

## 4. Jeden Slot füllen, Steuerung aber getrennt halten

Alle 15.889 Slots werden eins zu eins aus dem GDT581-Ledger übernommen:

- 13.593 produktive Inhaltsoccurrences benutzen die 42-Klassen-/181-Zellen-
  Schicht;
- 107 Namensoccurrences und zwei `LOCAL_X`-Occurrences benutzen gelernte
  Karten;
- 2.187 Kontrollslots erhalten ausschließlich strukturelle Defaults wie
  `OT=danach`, `OL=weiter`, `DY=Schritt schließen` oder lokale Makrokarte.

Die 4.026 geerbten Werte werden separat als Aliase derselben
Klasse×Register-Karte aufgelöst. Sie erzeugen weder einen unsichtbaren Slot noch
ein neues Wort.

## 5. Ereignisse, Aussagen und lokale Karten rendern

Jede Slotbedeutung wird mit Slot-ID und primärem Governor in einer exakten
Klammertrace ausgegeben. Die lesbare Klausel gruppiert Slots nach dem bereits
festen GDT581-Host. Dadurch bleiben insbesondere entfernte oder gemischte
Köpfe wie G515-E0385 und G515-E0379 getrennt.

- Alle 5.122 Ereignisse werden aus ihren festen Slots gerendert.
- Alle 793 Aussagen werden ausschließlich aus ihren festen Event-IDs
  zusammengesetzt.
- Alle 744 lokalen Karten bleiben owner- und locusgebunden.
- Der unveränderte GDT581-Wortlaut bleibt als Rückkanal neben jeder neuen
  Ereignis- und Aussageausgabe stehen.

Fünfundzwanzig vollständige Ereignisse – fünf pro Register – und zwanzig
vollständige Aussagen – vier pro Register – bilden das kompakte
Hausverstandsdeck. Die Auswahl und `KEEP_REGISTER_HYBRID`-Disposition werden
deterministisch erzeugt; ein anschließender unabhängiger manueller Audit las
alle 45 Karten sowie die gesamte lokale Namensschicht und fand keinen
materiellen Fehler. Sein Protokoll steht in
`artifacts/GDT582_MANUAL_SENSE_AUDIT.md`. Eine Deutung darf als Arbeitswert
bestehen bleiben, solange sie nicht eine ganze Passage deutlich schlechter
macht als die vorhandene Alternative.

## 6. Historische Plausibilitätsschicht

Historische Rezeptbücher dienen nur zur Auswahl eines plausiblen
Hausvokabulars, nicht zur Identifikation einer Voynich-Form. Die Palette aus
Wasser, Wein, Öl, Essig, Honig, Salz, Blättern, Blüten, Samen, Wurzeln,
Gefäßen und wiederholten Handgriffen passt unter anderem zu:

- Meister Eberhards fünfzehntem-Jahrhundert-Rezeptbuch:
  <https://www.uni-giessen.de/de/fbz/fb05/germanistik/absprache/sprachverwendung/gloning/tx/feyl.htm>
- der mittelalterlichen Rezept- und Destillationstradition um Rupescissa:
  <https://wellcomecollection.org/works/mervmpw3>
- einer vierzehntes-Jahrhundert-Tintenrezepttradition mit Wasser, Wein,
  Vitriol, Gummi, Einweichen, Kochen, Seihen und Zugeben:
  <https://www.persee.fr/doc/bec_0373-6237_1925_num_86_1_460583>

Das historische Material macht lediglich den verwendeten Werkstattwortschatz
und die Trennung wiederholter Operationen von wechselnden Stoffnamen
plausibel. Es belegt weder eine abgekürzte Operationssprache noch einen
Nomenklator und beweist keine einzelne Gleichung.

## Entscheidung und Claim ceiling

Der Pass gilt, wenn jeder der 15.889 festen GDT581-Slots genau einmal und mit
nichtleerem Default erscheint, die 13.702/2.187-Grenze erhalten bleibt, alle
42 produktiven Analyseklassen und 181 belegten Registerzellen vollständig sind,
die 109 gelernten Inhaltsoccurrences getrennt bleiben, Aliase keinen neuen Slot
erzeugen, alle Ereignisse/Aussagen/lokalen Karten ihre Identität bewahren und
die 25+20 Sinnchecks alle fünf Register gleichmäßig abdecken.

GDT582 liefert eine vollständige **explorative Arbeitsübersetzung** und ein
innerhalb der festen GDT581-Segmentierung wiederverwendbares Hauswörterbuch
für die gegenwärtigen dreißig Seiten. Es
bestätigt kein Voynich-Lexem, keinen Klartext, keine Sprache, keinen historischen
Codebuchschlüssel und keine objektive Identität eines Stoffes oder Verfahrens;
es enthält keinen Held-out-Test, keinen Parser neuer Oberflächen und keinen
Nachweis auf neuen Seiten.
Seine Defaults dürfen stehen bleiben, bis eine konkrete Passage sie unmöglich
macht oder ein besseres kompositionelles Pack sie ersetzt.
