# GDT787 — `keedy` ist eine starke Formenfamilie, aber kein frei übertragbarer Bedeutungsrest

## Ergebnis

Die gute Nachricht ist formal: `…keedy` gehört zu den saubersten bisher
gefundenen Oberflächenfamilien. Im zugelassenen Cache stehen **601 rohe Token
in 38 Formen**. Davon sind **370 Token in 27 Formen** als vollständige Wörter
in ZL3b, IT2a und RF1b zugleich lesbar. Ohne das nackte `keedy` bleiben 348
exakte Token in 26 längeren Formen auf 58 Seitenlabels und 34 physischen
Folios.

Die wichtigere semantische Nachricht ist negativ: Der Sinn von `keedy` lässt
sich daraus **nicht zuverlässig in beliebige `Xkeedy`-Wörter übertragen**.
Neun verschiedene X besitzen das vollständige Quadrat
`Xkey/Xkeey/Xkedy/Xkeedy`. Ein target-maskiertes Modell sagt die vierte Zelle
aus den drei Schwestern voraus. Es schlägt den freien X-Vergleich in 5/9, einen
unabhängig formgewählten Ganzwortvergleich in 4/9 und beide gleichzeitig nur
in **3/9** Fällen. Diese drei Fälle `cho/l/o` bilden keine kohärente Schale:
die natürlichen Partner `qo`, `ol` und `y` halten nicht mit.

Die Arbeitsentscheidung lautet deshalb:

```text
FORM:       starke *keedy-Ganzwortfamilie
TRANSFER:   WHOLE_ONLY
keedy:      heißer Endzustand                 [eigenes Ganzwort]
HOT+END:    darf in belegten Ganzwortkarten bleiben
CLOSED:     kein automatischer gesprochener Zusatz
EXPORT:     kein Wert aus keedy in beliebige Xkeedy-Formen
```

Das ist kein Rückfall zu leerem Text. Im Gegenteil: 38 kurze
Ganzwortanzeigen ersetzen die falsche Universalzerlegung. Sie verwenden
bewusst denselben HOT+END-**C0-Familienprior**, damit keine beobachtete Form
leer bleibt. Das sind nicht 38 unabhängig gestützte Bedeutungen und keine
verdeckte `keedy`-Kompositionsregel. GDT787 erteilt **null neue
Renderer-Lizenzen**; ältere Lizenzen behalten ausschließlich ihren früheren
Scope. Die alten, aus modernen EVA-Initialen abgeleiteten Patienten **Holz,
Wurzel, Samen und Saat** sowie der automatische q-Imperativ werden aus den
betroffenen Hauptwerten entfernt.

## Das vollständige Formenraster

Die zehn vollständig belegten Reihen sind das nackte Feld und neun X:

```text
          START       MIDDLE      END         MIDDLE+D    END+D
bare      ky          key         keey        kedy        keedy
che       cheky       chekey      chekeey     chekedy     chekeedy
cho       choky       chokey      chokeey     chokedy     chokeedy
l         lky         lkey        lkeey       lkedy       lkeedy
o         oky         okey        okeey       okedy       okeedy
ol        olky        olkey       olkeey      olkedy      olkeedy
qo        qoky        qokey       qokeey      qokedy      qokeedy
qol       qolky       qolkey      qolkeey     qolkedy     qolkeedy
sol       solky       solkey      solkeey     solkedy     solkeedy
y         yky         ykey        ykeey       ykedy       ykeedy
```

Alle 50 Zellen sind reader-exakte vollständige Wörter. Das ist starke Evidenz
für eine absichtlich erzeugte formale Leiter. Es beweist aber noch nicht, dass
jede sichtbare Teilfolge ein frei gesprochenes Wort ist. Genau diese Trennung
hat das Neun-Familien-Modell geprüft.

## Der Neun-Familien-Test

Der Score ist eine Jensen-Shannon-Profilähnlichkeit zwischen 0 und 1, keine
Wahrscheinlichkeit. Höher ist ähnlicher. Jede Oberfläche wird zuerst je
physischem Folio ausgeglichen, danach hat jedes X genau eine Stimme. Sämtliche
`*keedy`-Zielbedeutungen und alle 172 GDT754-Source-Prosaformen sind als
semantische Nachbarn maskiert.

| X | exakte `Xkeedy` / Folios | additiv | freies X | formgewähltes Ganzwort | gewinnt gegen beide |
|---|---:|---:|---:|---:|---|
| `che` | 3 / 3 | .546 | .483 | .585 | nein |
| `cho` | 2 / 2 | .632 | .497 | .522 | ja |
| `l` | 23 / 10 | .721 | .706 | .701 | ja, knapp |
| `o` | 49 / 21 | .900 | .841 | .885 | ja |
| `ol` | 25 / 15 | .789 | .849 | .817 | nein |
| `qo` | 201 / 26 | .895 | .819 | .918 | nein |
| `qol` | 5 / 3 | .672 | .701 | .459 | nein |
| `sol` | 3 / 2 | .226 | .590 | .372 | nein |
| `y` | 19 / 16 | .718 | .824 | .818 | nein |
| **Makromittel** | **9 Typen** | **.678** | **.701** | **.675** | **3 / 9** |

Auch die Schutzvarianten helfen nicht. Mit nur strukturellen Feldern verliert
additiv `.794` gegen `.846/.823`; ohne Registerfelder verliert es `.668` gegen
`.717/.692`. Gegen den absichtlich zu starken besten Außenprofilspender gewinnt
es nur bei `o` und `qo`. Das Ergebnis hängt somit weder an `qokeedy`'s großer
Häufigkeit noch an einer bestimmten Featuregruppe.

## Welche Teile der alten Bedeutung noch tragen

Die drei Bestandteile wurden getrennt geprüft:

- **END** ist der beste, aber noch nicht allein exportfähige Lead. Der streng
  bereinigte Außenkontext ist bei Radius 1 nur in 6/9 Typen informativ: fünf
  positiv, einer negativ, drei `NA` (exakter Vorzeichenflip p=.09375). Bei
  Radius 3 sind 8/9 informativ: fünf positiv und drei negativ. In der sauberen
  Schwestersemantik ist END nur viermal messbar, dort aber viermal
  gleichgerichtet.
- **HOT** bleibt für die bereits etablierten Qualitäts- und
  Zubereitungsganzwörter plausibel. Gegen `Xteedy` ist die Richtung jedoch
  nicht stabil genug, um alle linken Familien zu erfassen.
- **CLOSED** scheitert. Bei Radius 1 sind nur 2/16 und bei Radius 3 nur 3/16
  Typen überhaupt informativ; die übrigen Fälle sind korrekt `NA`, nicht
  scheinbare Gleichstände. Diese winzige Restdeckung exportiert keinen Wert.
  Das passt zu GDT689: Ein bereits terminaler Schwesterwert muss nicht ein
  zweites Mal „abgeschlossen“ sprechen.

Darum wird `keedy` selbst knapp zu **heißer Endzustand**. `okeedy` bleibt
**heißer Ansatz an der Endstufe**, `qokeedy` **heiß am Gradende**. Das sind
Ganzwortkarten mit eigener Familiengeschichte, kein jetzt freigesetztes
Suffixwörterbuch.

## Grenzen: fusioniert, getrennt und Stolfi

Alle 348 reader-exakten längeren Zielvorkommen sind in den drei aktuellen
Lesungen fusionierte vollständige Wörter. Daneben stehen **20 andere exakte
Sequenzen `X keedy` mit 18 verschiedenen X**. Nur fünf X sind sowohl fusioniert
als auch getrennt belegt: `al`, `cheol`, `chol`, `ol`, `sol`.

Diese 20 Sequenzen sind keine zwanzig alternativen Trennungen derselben Stelle.
Bei den 542 rohen längeren Zieltoken liefern andere aktuelle Leser nur vier
interne Splitkandidaten. Stolfi besitzt für 60 der exakten Zielstellen dieselbe
Locuszeile: 59 bleiben fusioniert, genau `sol,keedy` auf f78r.31 wird getrennt.
Das trägt **gelegentliche Grenzbeweglichkeit**, aber keine automatische
Bedeutungsaddition. Die Splitfälle gingen bewusst nicht als Semantikstimmen in
den Profiltest ein. Die dazugehörigen fusionierten Rasterreihen helfen dennoch
nicht: `ol` verliert gegen beide Nullmodelle, `sol` deutlich. Die Grenze hebt
das `WHOLE_ONLY`-Ergebnis daher nicht auf.

## Konkrete Reparaturen am Wörterbuch

Die vollständige 38er-Tabelle steht in
`artifacts/GDT787_38_WORKING_DICTIONARY.tsv`. Die wichtigsten Änderungen sind:

| Form | alter problematischer Wert | neuer kurzer Default |
|---|---|---|
| `keedy` | heiß am Gradende, abgeschlossen | **heißer Endzustand** |
| `okeedy` | heißer Ansatz am Gradende, abgeschlossen | **heißer Ansatz an der Endstufe** |
| `qokeedy` | teils doppelt abgeschlossen | **heiß am Gradende** |
| `lkeedy` | Drogenholz, heiß, abgeschlossen | **erhitzte Droge, Endstufe** |
| `olkeedy` | Holzansatz vollständig erhitzt | **vollständig erhitzter Ansatz** |
| `qolkeedy` | gib … Drogenmaterial hinzu | **erhitztes Drogenmaterial, Endstufe** |
| `rolkeedy` | erhitze den Wurzelauszug | **erhitztes Materialergebnis, Form II** |
| `sokeedy` | heißer Samenansatz | **erhitzte Zubereitung, Endstufe** |
| `solkeedy` | Saatgutansatz vollständig erhitzt | **erhitzter Stoffansatz, Endstufe** |
| `ykeedy` | Eintrag: heiß … abgeschlossen | **heißes Endstufenfeld** |

`salkeedy=erhitzte Fertigdroge` bleibt als GDT786-Ganzwortkarte erhalten. Die
elf nur roh belegten Formen erhalten ebenfalls konkrete C0-Arbeitsanzeigen und
sind als `RAW_READER_WARNING_ONLY` markiert. Auch die 27 reader-exakten
Anzeigen werden durch GDT787 nicht neu in den Renderer befördert. Ihre
0--100-Konfidenz ist ein redaktionelles Evidenzgewicht aus Rekurrenz,
Leserübereinstimmung, älterer Ganzwortlinie und Gegenbelegen, keine Formel und
keine Wahrscheinlichkeit. Jede Karte führt außerdem zwei voneinander
verschiedene konkrete Bedeutungsrivalen und, getrennt davon, eine echte
Speicher-/Kompositionsalternative.

## Praktischer Zeileneffekt

Die dichte f114r.30-Folge zeigt, was die Korrektur leistet:

```text
y chedar okeedy lkeedy aiin oeedaiin qoaiin ykedy
okair olkeedy qoain ain okeey ram
```

Für die drei `*keedy`-Wörter steht in der fokussierten Arbeitsanzeige nun knapp:

```text
okeedy    heißer Ansatz an der Endstufe
lkeedy    erhitzte Droge, Endstufe
olkeedy   vollständig erhitzter Ansatz
```

Das ist informativer und ehrlicher als dreimal automatisch Holz, Samen oder
„abgeschlossen“ zu erzeugen. Die übrigen Wörter der Zeile behalten ihre je
eigenen Karten; GDT787 erfindet daraus keinen flüssigen Klartext.

## Historische Passform und Grenze

Der 1415-Komparator aus Tadhg Ó Cuinn trägt weiterhin die Architektur von
heiß/kalt, trocken/feucht und Anfang/Mitte/Ende innerhalb nummerierter Grade.
Spätmittelalterliche Arzneiregister erlauben außerdem gelernte Stoffnamen neben
kompakten Fachfeldern. Das erklärt, warum ein formales Raster und gelernte
Ganzwörter nebeneinander plausibel sind. Kein historisches Zeugnis identifiziert
EVA `keedy`, `k`, `ee`, `d` oder `y` als mittelalterliches Wort, Kürzel oder
Lautwert.

## Nächster Hebel

Der nächste Rest ist `dal`, danach `ar` und `ol`, genau wie nach GDT786
vorgesehen. GDT787 liefert dafür eine wichtige Regel: dichte Formenparadigmen
reichen nicht. Jeder Rest muss die Bedeutung gegen dieselben linken Familien,
typenbalancierte Ganzwortnullen und tatsächlich getrennte Sequenzen vorhersagen.
Wenn er scheitert, bleiben kurze Ganzwortkarten statt einer künstlichen
Universalgrammatik.

GDT787 öffnet keine neue Seite, kein Bild, keine OCR und keine Transkription;
`f84/f84r` bleiben gesperrt. Es bestätigt kein Lexem, keine konkrete Substanz,
keine Sprache und keinen EVA-Zeichenwert.
