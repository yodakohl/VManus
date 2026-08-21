# V16 R1 — vollständige Default-Lesung des Werkstatt-Lehrmeisters

Datum: 2026-08-21

Status: **maximal abduktive Sidequest-Arbeitstheorie**. Das ist eine bewusst
vollständige Rücklesung, keine Entzifferungsbehauptung und kein kanonisches
GDT-Ergebnis.

## Ergebnis

Ich nehme ein kleines medizinisch-astrologisches Schreibatelier um 1420 an.
Seine zehn Seiten gehören zu einem illustrierten Arbeitsbuch:

```text
HERBAL  = welche Pflanze und welche Eigenschaft/Zubereitung?
BIO     = wie wird Bad, Flüssigkeit oder örtliche Anwendung ausgeführt?
ASTRO   = unter welchem Himmelsabschnitt wird die Anwendung gewählt?
```

Die Schreiber schreiben keine normale fortlaufende Rede Buchstabe für
Buchstabe. Sie lernen ganze Kürzungskarten. Ein sichtbares Wort ist die
jeweilige Schreiberform einer Karte. Die Abbildung liefert häufig das
ausgelassene Subjekt, der Absatz die laufende Vorschrift und ein kurzer
Bio-Eintrag nur die noch fehlende Handlung oder Auswahl.

V16 macht daraus erstmals ein **lückenloses Arbeitswörterbuch**:

| Schicht | vollständig belegte Einheiten |
|---|---:|
| GDT327-Prosaereignisse auf 7 Seiten | 381/381 |
| konkrete Bedeutungen für exakte Prosakarten | 173/173 |
| sichtbare ZL3b-Gruppen auf 3 Kreis-Seiten | 395/395 |
| übersetzte Feld-, Absatz- und Astro-Konstruktionen | 288/288 |
| Gesamtzahl sichtbarer Gruppen | 776/776 |

Kein Eintrag bleibt semantisch leer. Wo der Befund keine eindeutige Expansion
erzwingt, steht ein absichtlich konkreter `CONTEXT_DEFAULT` mit niedriger
Sicherheit. Das ist besser als Scheingenauigkeit zu verstecken: jede Karte
kann jetzt durch weitere Iterationen verbessert oder verdrängt werden.

Vollständige Dateien:

- `V16_R1_COMPLETE_DEFAULT_LEXICON.tsv` — 173 exakte Prosakarten, 395 lokale
  Astro-Gruppen und 10 wichtige Konstruktionen;
- `V16_R1_COMPLETE_TRANSLATION_LEDGER.tsv` — alle 776 sichtbaren Gruppen;
- `V16_R1_COMPLETE_CONSTRUCTION_READINGS.tsv` — jedes Prosa-Feld, jeder ganze
  Absatz über physische Zeilen hinweg und jede Astro-Beschriftung;
- `V16_R1_LINE_READINGS.tsv` — kompakte Rücklesung aller 199 sichtbaren loci.

## Die einfache Lehrregel

Ein Lehrling braucht vier Tafeln, keine komplizierte Chiffre.

1. **Gemeine Kartentafel.** Etwa zwanzig oft gebrauchte Karten bedeuten
   *nimm den nächsten Eintrag*, *mit demselben Ansatz*, *im üblichen Maß*,
   *gegenwärtige Portion*, *zubereitet*, *wiederhole* und ähnliche
   Werkstattanweisungen.
2. **Herbal-Tafel.** Seltene Karten werden aus dem Artikel-Exemplar übernommen:
   Pflanzenname, Blatt, Stängel, Wurzel, feuchter Standort, Gradqualität,
   Sammelzeit, Zubereitung, Anwendung, Wirkung oder Warnung.
3. **Bad-/Anwendungstafel.** Kurze B-Zellen wählen Wasserführung, Erwärmung,
   Eintauchen, Übergießen, Maß, Dauer, Auslass oder fertige Zubereitung. Ein
   angehängter Schluss bestätigt die lokale Auswahl.
4. **Kreis-Tafeln.** Eine Beschriftung wird immer zusammen mit ihrem gezeichneten
   Ort gelernt: Herrscher-, Tierkreis-, Stern- oder Mondhausplatz. Gleiche
   Striche auf einer anderen Kreisseite brauchen keine gleiche Expansion.

Der Schreiber geht praktisch vor:

```text
Bild/Absatz erkennen
→ laufende Vorschrift im Exemplar finden
→ passende Ganzkarten kopieren
→ ausgelassene Bildargumente nicht wiederholen
→ Bio-Auswahl lokal abschließen
→ Text um das vorher gezeichnete Bild umbrechen
```

Ein Satz darf deshalb ohne Weiteres über ein physisches Zeilenende laufen.
Der Umbruch ist primär Platzverwaltung; Absatzkontinuität und lokaler Abschluss
sind für die Rücklesung wichtiger.

## Festes Default-Wörterbuch der wichtigsten Karten

| Karte/Konstruktion | konkrete Default-Rücklesung | Sicherheit |
|---|---|---:|
| `qokaiin` | **nimm den nächsten Eintrag** | .57 |
| `L/O` | **mit ihm; ebenso unter derselben Überschrift** | .59 |
| `AIIN` | **im angegebenen oder üblichen Maß** | .61 |
| `Y` | **die gegenwärtige vorgeschriebene Portion** | .52 |
| `CTHY` | **zubereitet und gebrauchsfertig** | .44 |
| `Y–AIIN–Y` | **beide Portionen unter demselben angegebenen Maß** | .44 |
| `VAL-Q` / `qokedy` | **verwende die gewöhnliche Bad-Einstellung** | .50 |
| `VAL-QE` / `qokeedy` | **verwende die temperierte umlaufende Flüssigkeit** | .48 |
| `VAL-S` / `shedy`-Familie | **lasse die Zubereitung ruhen, bis sie fertig ist** | .45 |
| `VAL-L` / `lchedy` | **gieße die Flüssigkeit über die örtliche Stelle** | .43 |

Rendererformen erben die Bedeutung der exakten Karte. So bleiben etwa
`AIIN/DAIIN/SAIIN/...` dieselbe Werkstattanweisung und `Y/DY/CHY/...` dieselbe
Portionskarte, sofern GDT327 sie als dieselbe exakte Karte führt. Das ist keine
Laut- oder Buchstabenlesung.

Für die 163 übrigen Prosakarten gilt ebenfalls je eine feste Default-Bedeutung
im TSV. Nur seiten- oder registergebundene Seltenheiten benutzen die
ausdrücklich begrenzte `CONTEXT_DEFAULT`-Regel. Es gibt keine attraktive
Einzelstellen-Sonderübersetzung.

## Fortlaufende Rücklesung: f10r

Der Absatz ist die Sinneinheit; die fünf sichtbaren Zeilen sind nur sein
räumlicher Umbruch.

### Absatz 1

> Die abgebildete Heilpflanze wächst in feuchtem Schatten. Seiht die gewonnene
> Flüssigkeit ab und fügt sie dem laufenden Ansatz zu; setzt dieselbe Vorschrift
> fort und seiht erneut. Sie öffnet eine Verstopfung. Bewahrt das getrocknete
> Kraut auf. Trinkt eine kleine Tasse; der Samen ist schwächer. Verwendet es
> ebenso unter derselben Überschrift, sobald es zubereitet ist.

### Absatz 2

> Wendet es warm und gebrauchsfertig im üblichen Maß an. Zerstoßt die bittere,
> faserige Wurzel. Nehmt die gegenwärtigen Portionen unter demselben angegebenen
> Maß. Trinkt eine kleine Tasse im üblichen Maß; zerstoßt sie, mischt sie ebenso
> mit dem laufenden Ansatz und wiederholt die vorige Anweisung. Die Pflanze hat
> ein schmales geteiltes Blatt. Bewahrt die verbleibenden Portionen des
> getrockneten Krauts auf.

Jede der 38 Karten ist im Ereignisledger einzeln dieser Rücklesung zugeordnet.

## Fortlaufende Rücklesung: f56r

> Verwendet nur die innere Rinde; wiederholt die Waschung drei Tage im
> angegebenen Maß. Die Pflanze wächst an fließendem Wasser. Trinkt eine kleine
> Tasse und verbindet sie mit dem laufenden Ansatz. Ihr Blatt ist breit und
> weich; wendet die Zubereitung warm an. Vermeidet eine übermäßige Dosis,
> sammelt vor der Blüte und verwendet wieder nur die innere Rinde. Die Pflanze
> ist kühlend im zweiten Grad. Ihr Stängel ist blass und hohl; mischt die
> Portion mit Honig. Setzt die Vorschrift im üblichen Maß fort.

Das ist eine zusammenhängende Anweisung über sieben physische Zeilen. Alle 27
Karten stehen zusätzlich in exakter Reihenfolge im Ledger.

## Vollständige Bio-Rücklesung: f82r

f82r bildet im GDT327-Ausschnitt einen fortgesetzten Absatz mit acht
physischen Zeilen und vielen kurzen Zellen:

- **f82r.2:** Beendet die gewöhnliche warme Badanwendung; die Zubereitung ist
  fertig. Nehmt die gegenwärtige Portion der temperierten umlaufenden
  Flüssigkeit, setzt fort, öffnet den oberen Auslass und wechselt zum nächsten
  Becken.
- **f82r.3:** Erwärmt sanft; beendet den Gang nach einem Eintauchen; setzt die
  dargestellte Person in das untere Becken und nehmt den nächsten Eintrag.
- **f82r.4:** Schließt den unteren und öffnet den oberen Auslass; haltet das
  übliche Maß bis zur Bereitschaft, bewahrt dasselbe Verhältnis und setzt im
  nächsten Becken fort.
- **f82r.7:** Haltet das übliche Maß, wendet vor dem Schlaf an, öffnet den
  oberen Auslass und lasst die Zubereitung ruhen. Verschließt nach dem Seihen,
  erwärmt sanft und bewahrt das übliche Maß.
- **f82r.19:** Die Zubereitung ist fertig; verbindet sie mit dem laufenden
  Ansatz, verwendet die temperierte Flüssigkeit und bestätigt die Bereitschaft.
- **f82r.23:** Taucht die Glieder im üblichen Maß ein, erwärmt sanft und wendet
  vor dem Schlaf an. Bewahrt die Flüssigkeit für die nächste Waschung, gießt
  sie über die örtliche Stelle und bleibt unter der markierten Höhe.
- **f82r.26:** Lasst die Flüssigkeit durch den Seitenkanal zurücklaufen,
  verwendet die temperierte Flüssigkeit und setzt fort. Bewahrt Maß und
  Verhältnis, nehmt den nächsten Eintrag und taucht die Glieder ein.
- **f82r.27:** Schließt bei vollem Becken den unteren Auslass, verwendet zweimal
  dieselbe temperierte Umlaufflüssigkeit, vollendet die örtliche Spülung,
  beendet nach einem Eintauchen und verschließt nach dem Seihen.

Die letzte Lesung nutzt die wichtigste interne Wiederholung: `VAL-QE` erscheint
in Zelle 3 und 6 als dieselbe konkrete Einstellung, nicht als zweimal neu
erfundene Handlung.

## Astro: vollständige lokale Leseregel

Die 395 sichtbaren ZL3b-Gruppen werden nur einmal gezählt. IT2a/RF1b bleiben
alternative Lesungen derselben Schrift. Jede Gruppe besitzt im Ledger eine
lokale Expansion; jede vollständige Beschriftung steht in
`V16_R1_COMPLETE_CONSTRUCTION_READINGS.tsv`.

### f67r2

- die sieben M1-Plätze heißen provisorisch **planetarische Herrscher 1–7**;
- die zwölf M2-Plätze heißen **Tierkreisabschnitte 1–12**;
- die sieben M3-Plätze heißen **innere Himmelsbedingungen 1–7**;
- nicht katalogisierte Randbeschriftungen benennen am jeweiligen gezeichneten
  locus Einfluss, günstige Waschanwendung, Tierkreiszuordnung oder Herrscher;
- die langen loci 72–74 lauten fortlaufend: Wähle für den gegenwärtigen
  Tierkreisabschnitt seinen Herrscher, lies die entsprechende innere Bedingung,
  trage dieselbe Regel weiter und wähle für Bad oder Anwendung die günstige,
  nicht die gegenteilige Stunde.

### f68r1

Die 29 Sterne erhalten **keine erfundene zyklische Nummernsemantik**. Jeder
Eintrag lautet stattdessen konkret „der benannte Stern an [sichtbarer
Lage]“, etwa südlich der Sonne, östlich der Sonne, nahe dem Zentrum oder
nordöstlich des Mondes. Damit ist jede Beschriftung rücklesbar, ohne einen
Autorstart oder universelle Gradkoordinate zu erfinden. Die Textzeilen erklären
in der Default-Lesung, den zur verlangten Leuchte nächstgelegenen Sternplatz zu
wählen und dessen Regel auf den Fall zu übertragen.

### f69v

Die 28 abwechselnd langen und kurzen Speichen sind **Mondhäuser/-stationen in
einem geordneten Paarlauf**. Die langen und kurzen Texteingänge erläutern, die
jeweilige Station, das günstige Intervall und die zugehörige Bad- oder
Aderlassregel zu wählen und die Reihenfolge nicht ohne neue Beobachtung
umzukehren. Jede der 140 sichtbaren Gruppen besitzt eine eigene Wortrolle.

## Ganze-Seiten-Paraphrasen

| Seite | Default-Inhalt |
|---|---|
| f10r | feucht wachsendes Heilmittel; Abseihen, Zerstoßen, Portionieren, innerlich und warm äußerlich anwenden |
| f11r | weiche breitblättrige Sumpfpflanze mit bitterer Wurzel; feuchte/kühlende Qualität; mit Honig gegen Fieber und Verstopfung |
| f55v | frische Stängel schneiden, Wasser zufügen, warmen Auszug im üblichen Maß auf eine wunde Stelle geben |
| f56r | wassernahe Pflanze; innere Rinde und Blatt verwenden; dreitägige Waschung, kleine Trinkmenge und warme Honiganwendung |
| f81v | Grundbad herstellen, Wasser führen, Maß und Verhältnis halten, eintauchen/spülen und einzelne Zellen abschließen |
| f82r | temperierte Umlaufflüssigkeit durch Becken führen, Person einsetzen, Auslässe bedienen, spülen und erneut verwenden |
| f83r | umfangreicher Bad-/Anwendungsplan mit Wasserzufuhr, Eintauchen, Übergießen, Ruhezeiten, Wiederholung und Abschluss |
| f67r2 | planetarischen Herrscher, Tierkreisabschnitt und innere Bedingung zu einer Wahlregel verbinden |
| f68r1 | räumliches Sternverzeichnis zur Wahl eines lokalen Himmelsplatzes, ohne festgelegten Zyklusstart |
| f69v | 28-teiliger langer/kurzer Mondstationsplan für aufeinanderfolgende günstige und ungünstige Intervalle |

## Historische Passung

Die Arbeitstheorie verlangt keinen modernen Datenbankautor. Zeitnahe
Sammelhandschriften verbinden genau die benötigten Stoffwelten:

- [British Library Add MS 29301](https://searcharchives.bl.uk/catalog/032-002020783)
  ist um 1420–1430 illustriert und verbindet medizinische Bildpraxis mit einem
  Umfeld, zu dem auch ein Zodiac-Man und astronomische Tafeln gehören.
- [British Library Harley MS 1736](https://searcharchives.bl.uk/catalog/040-002047567)
  enthält medizinisch-chirurgische Texte und Rezepte sowie sieben Planeten,
  Tierkreiszeichen und astrologische Tafeln.
- [British Library Harley MS 1735](https://searcharchives.bl.uk/catalog/040-001980286)
  zeigt, dass Prognostik, Kochrezepte, Medizin und Alchemie in einem praktischen
  Sammelbuch nebeneinander stehen konnten.
- [British Library Harley MS 2390](https://searcharchives.bl.uk/catalog/040-002048221)
  bewahrt ein tatsächlich imperativisches fünfzehntes-Jahrhundert-Rezept mit
  Waschen, Stampfen und Kochen; gerade solche häufigen Handlungen können zu
  kurzen Werkstattkarten werden.

Diese Vergleiche stützen den **Buchtyp und die Handlungsgrammatik**, nicht die
einzelnen Voynich-Zuordnungen.

## Wo die Theorie absichtlich riskant ist

1. Viele einmalige Herbal-Karten haben nur Bild- und Artikelkontext. Ihre
   konkrete Blatt-, Standort-, Zubereitungs- oder Wirkungslesung ist ein
   austauschbarer Startwert mit .18 Sicherheit.
2. Die Bio-Karten können teilweise Apparate-, Frauenheilkunde- oder bloße
   Exemplarformeln statt Badhandlungen kodieren. V16 entscheidet trotzdem für
   Bad/örtliche Anwendung, weil das über alle drei Seiten den lesbarsten
   Arbeitsgang ergibt.
3. `AIIN = übliches Maß` ist enger als seine formale Mobilität verlangt. Der
   Default bleibt, bis eine Dauer-, Grad- oder bloße Verweislesung mehr
   vollständige Stellen vereinfacht.
4. Die f67r2-Schichten können andere Siebener- und Zwölferreihen sein. Die
   Herrscher-/Tierkreislesung bleibt, weil sie um 1420 lehrbar, diagrammgerecht
   und mit der 7/12-Topologie sparsam ist.
5. f69v kann ein anderer 28er-Katalog sein. „Mondstation“ ist die beste
   konkrete Default-Klasse, nicht ein identifizierter historischer Name.

## Nächste produktive Revision

Der entscheidende Fortschritt ist nicht, dass diese englischen Wörter bewiesen
wären. Es gibt nun für **jede** sichtbare Einheit eine widerrufbare Bedeutung
und für jede längere Konstruktion eine Rücklesung. Die nächste Iteration kann
deshalb präzise fragen:

```text
Welche einzelne Kartenbedeutung macht ihre sämtlichen Wiederholungen
und die meisten vollständigen Sätze gleichzeitig besser?
```

Ein Lehrling könnte das vorliegende System bereits lernen und die zehn Seiten
ohne semantische Lücke rücklesen. Ein Korrektor könnte jede konkrete schlechte
Zuordnung einzeln ersetzen, ohne die gesamte Werkstattgrammatik zu verlieren.

`f84` und `f84r` wurden weder geöffnet noch abgefragt.
