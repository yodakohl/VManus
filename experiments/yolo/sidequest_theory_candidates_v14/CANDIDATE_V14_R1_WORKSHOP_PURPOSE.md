# Sidequest V14 R1 — Werkstattbuch fuer Stoff, Anwendung und Zeitpunkt

Date: 2026-08-21

Status: **explorative Arbeitshypothese, kein GDT-Ergebnis und keine
Uebersetzung**. Perspektive R1: Lehrmeister einer Schreibwerkstatt um 1420.

## Entscheidung vorweg

Die einfachste lehrbare Gesamtfunktion der zehn Seiten ist ein
**iatromedizinisches Auswahl- und Arbeitsbuch**. Seine drei Register beantworten
nicht dieselbe Frage in derselben Form, sondern drei aufeinanderfolgende
Werkstattfragen:

```text
HERBAL A/B   WAS steht zur Verfuegung?
             bebilderter Artikel zum einfachen Stoff und seiner Zurichtung

BIO B        WIE wird es angesetzt oder angewandt?
             bebilderte Konfigurationskarte mit kurzen bestaetigten Werten

ASTRO        WANN / UNTER WELCHER LAGE gilt die Auswahl?
             drei getrennte raeumliche Nachschlageinstrumente
```

Der gemeinsame Zweck ist **nicht** eine moderne relationale Datenbank und auch
nicht eine bewiesene Eins-zu-eins-Verknuepfung jedes Krauts mit jedem Bad und
jedem Himmelsort. Es ist ein praktischer Sammelband, in dem Stoffdossiers,
Anwendungsformulare und Zeit-/Prognosehilfen mit derselben erlernten
Kartenkonvention gefuehrt werden. Ein Benutzer kann nur eines der drei Register
aufschlagen; ein ausgebildeter Praktiker kann sie als `WAS / WIE / WANN`
kombinieren.

Meine Konfidenz fuer diesen Gesamtzweck ist **0.61**. Fuer die engere Behauptung,
dass die drei Astro-Seiten tatsaechlich medizinische Zeitwahl statt allgemeine
Astronomie enthalten, gebe ich **0.43**. Diese Werte sind Rangierungen
innerhalb des absichtlich spekulativen Zehn-Seiten-Modells, keine
Beweiswahrscheinlichkeiten.

Der staerkste Rivale ist ein **allgemeines illustriertes Muster- und Lehrbuch
fuer Karten, Formulare und Diagramme**: Herbal uebt offene Artikel, Bio kurze
abgeschlossene Zellen, Astro verschiedene Beschriftungsgeometrien. Konfidenz
**0.36**. Dieser Rivale erklaert die wechselnden Stencils und mehrere Haende
sehr gut, aber die aufwendigen, inhaltlich verschiedenen Bilder und die
ausgepraegten registerlokalen Decks schlechter: Ein reines Schreibexemplar
braucht weder vier verschiedene Pflanzen noch mehrere Bad-/Koerperbilder noch
drei fachlich erkennbare Kreiswerkzeuge.

## Evidenzgrenze

Verwendet wurden ausschliesslich die festgelegten Seiten:

```text
Herbal:       f10r, f11r, f55v, f56r
Biological:   f81v, f82r, f83r
Kreis/Astro:  f67r2, f68r1, f69v
```

Die GDT327- und ZL3b-Sichten wurden nur mit `./vmanus-exp query-tsv`, expliziten
Locus-Allow-Werten und `--forbid-prefix f84` gelesen. `f84` und `f84r` blieben
versiegelt. ZL3b ist eine Oberflaechenlesung; IT2a und RF1b waeren alternative
Lesungen derselben Handschrift und wurden nicht als Wiederholungen gezaehlt.
Die drei Astro-Seiten besitzen keine GDT327-Ereignisse. Auf sie wird deshalb
keine Prosa-Kartenidentitaet uebertragen. Es wurden keine Teilstrings, Laute,
Sprachen oder neuen Voynich-Seiten benutzt und keine V14-Geschwisterberichte
gelesen.

## Die eine Werkstattregel

Ein Lehrling muss keinen grossen Chiffrieralgorithmus beherrschen. Er lernt
vier materielle Hilfen:

```text
GEMEINES KARTENBLATT   etwa zwanzig oft gebrauchte Ganzkarten und Formeln
REGISTEREXEMPLAR       offene Artikel | geschlossene Wertzellen | Kreislabels
LOKALES BEIBLATT       seltene Pflanzen-, Anwendungs- oder Himmelskarten
HANDREGEL              Wrapper, Anschluss, Zeilenanfang und Abschlussform
```

Die Vorwaertsproduktion lautet:

1. Der Zeichner oder leitende Schreiber legt Pflanze, Figuren/Behaelter oder
   Kreisgeruest zuerst an. Das Bild bestimmt Seitentyp und groben Gegenstand.
2. Der Textschreiber waehlt danach das Registerexemplar. Er darf Argumente
   auslassen, die Bild, aktuelle Rubrik oder Werkstattroutine bereits liefern.
3. Im Herbal-Register schreibt er einen offenen, abgekuerzten Artikel. Seltene
   Inhaltskarten kopiert er aus dem lokalen Stoffexemplar; die physische Zeile
   passt er um Stengel, Blatt und freien Raum. Zeilenende ist kein
   Satzschluss.
4. Im Bio-Register fuellt er kurze Zellen der gezeigten Konfiguration. Die
   Frage bzw. der Slot kann aus Bild und Stencil geerbt sein; eine exakte
   Nutzlastkarte traegt den Wert und die angehaengte DY-Realisierung bestaetigt
   die Zelle.
5. Im Astro-Register beschriftet er Positionen eines lokalen Diagramms. Die
   geometrische Stelle ist dort Teil der Adresse; dieselben Labelkarten muessen
   nicht ausserhalb dieses Diagramms gelten.
6. Wo das Exemplar einen neuen Eintrag verlangt, verwendet er `qokaiin` als
   `ITEM / NEXT / ACTIVATE CURRENT SLOT`. Wo eine Verbindung weitergefuehrt
   wird, setzt er L/O nach der Nachbarschafts- und Randregel. Wo die feste
   Formel verlangt ist, kopiert er `FORMULA_F3 = Y–AIIN–Y` als unzerlegte
   Ganzkartenfolge.
7. Erst am Ende rendert er die Karten gemaess Hand, Register und Position. Die
   sichtbaren EVA-Gruppen sind deshalb weniger stabil als die exakten Karten.
8. Ein zweiter Schreiber korrigiert Kartenidentitaet, Reihenfolge, offenen oder
   geschlossenen Feldstatus und Bildumfluss getrennt. Er korrigiert nicht nach
   einer vermuteten Lautung.

So erklaert eine einzige Lehre gleichzeitig Bildzuerst-Produktion, mehrere
Haende, gemeinsame Formeln und registerlokale Woerter. Die Register sind keine
drei Sprachen; sie sind drei Bedienweisen desselben Buchs.

## Warum die Register verschieden aussehen muessen

### Herbal: offener Artikel und grosser lokaler Schwanz

Ein Pflanzenartikel muss Namen/Identifikation, Merkmale, Ort, Qualitaet,
Zurichtung und Gebrauch nicht in identischen Spalten wiederholen. Ein
Stoffexemplar bringt daher viele seltene Karten mit. Das passt zu f10r
(38 Ereignisse, 25 exakte Typen, davon 19 Singletons, keine angehaengten
Abschluesse in den fuenf bewerteten Zeilen) und f56r (27/21/17, nur ein
Abschluss in sieben Zeilen). Nur vier exakte Typen kreuzen zwischen diesen
beiden Seiten. Die kleine gemeinsame Grammatik traegt den Artikel; der grosse
lokale Schwanz traegt wahrscheinlich den Stoffinhalt.

f55v ist die sinnvolle Bruecke: Es zeigt noch einen bebilderten einfachen Stoff,
arbeitet aber bereits stark im B-Modus. Acht seiner sechzehn exakten Typen
erscheinen auch auf den festen Bio-B-Seiten, nur drei auf den festen
Herbal-A-Seiten. Das ist genau die Stelle, an der ein offener Stoffartikel in
eine zugerichtete, festgehaltene Produktions- oder Anwendungskarte uebergeht.

### Biological: kurze Zellen und Wertdeck

Die 115 Bio-Felder haben im Mittel nur 2.44 Karten; 85 schliessen mit einer
angehaengten Realisierung. Die vier fuehrenden exakten Terminalfamilien treten
12/10/8/8-mal auf, wandern aber ueber Feldordnungen und Feldlaengen. Das passt
nicht zu vier starren Spalten oder einer einfachen Skala. Es passt zu einem
**slotabhaengigen kategorischen Wertdeck**: Das Bild bzw. der lokale Stencil
stellt die Frage, die exakte Karte waehlt Antwort, Zustand oder Operation, und
der angehaengte Abschluss bestaetigt den Eintrag.

Die wahrscheinlichste inhaltliche Klasse ist eine Bad-, Medium-, Gefaess- oder
Anwendungskonfiguration. Figuren, Becken, Leitungen und Auslaeufe liefern
sichtbare Argumente; deshalb darf der Text kurz sein. Frauenheilkunde bleibt
moeglich, ist aber fuer die Werkstattregel unnoetig eng.

### Astro: drei lokale Nachschlageinstrumente

Ein raeumliches Diagramm benoetigt nicht die Prosa-Feldgrammatik. Der Ort eines
Labels kann seinen Slot bereits festlegen. Deshalb haben f67r2, f68r1 und f69v
getrennte lokale Namensraeume und drei verschiedene Bedienweisen:

- f67r2 kombiniert einen Siebener- und einen Zwoelfersatz um ein Zentrum;
- f68r1 zeigt ein Zentrum plus 28 nichtzentrale beschriftete Sterne, aber keine
  vom Autor markierte zyklische Reihenfolge;
- f69v zeigt 28 radial angeordnete, abwechselnd lange und kurze Loci, aber
  keinen sichtbaren Start und keine sichere Laufrichtung.

Der gemeinsame Inhaltstipp ist **Himmelslage als Selektor fuer Zeitwahl oder
Prognose**. Die drei Seiten muessen dabei nicht drei Ansichten derselben Liste
sein. Sie koennen drei Instrumente sein: Kombination waehlen, Station
identifizieren, Ergebnis-/Zeitklasse nachschlagen.

## Die tragenden Karten im Unterricht

### `qokaiin`

Sieben von neun Vorkommen sind feldinitial, fuenf folgen auf eine bereits
bestaetigte Zelle, die neun rechten Nachbarn sind verschieden, und der
f82r-Uebergang wiederholt dieselbe exakte Karte am Zeilenende und am Anfang der
naechsten Zeile. Die beste Lehrfunktion bleibt:

```text
qokaiin := ITEM / NEXT / ACTIVATE CURRENT SLOT
```

In fluenter Ruecklesung kann das `nimm`, `als naechstes`, `trage ein` oder
`fahre fort mit` ergeben. Es ist keine identifizierte Vokabel und insbesondere
kein WATER.

### L/O

Die 19 Vorkommen werden mit einer Regel behandelt:

```text
A — L/O — B              verbinde A mit B unter der aktiven Beziehung
A — L/O — B — L/O — C   fuehre dieselbe Beziehungsart kettenweise fort
L/O am Feldanfang        erbe den linken Teilnehmer
L/O am Feldende          halte den rechten Teilnehmer fuer die Fortsetzung offen
L/O allein               wiederhole/halte die aktive Beziehung
```

Die Quellklasse ist `MIT DEM AKTUELLEN EINTRAG / EBENSO / WIE OBEN VERBUNDEN`.
Auf Herbal entstehen laengere offene Verbindungen, auf Bio kurze geerbte und
oft bestaetigte Verbindungen. Die Funktion wechselt nicht mit dem Register.

### `FORMULA_F3 = Y–AIIN–Y`

Die einzige exakte Dreierfolge, die auf zwei festen Prosaseiten wiederkehrt,
wird als Ganzformel gelehrt. Die fuehrende Ruecklesung bleibt
`SHARED_ACTIVE_REFERENCE`: zwei markierte Eintraege stehen unter demselben
aktiven Standard/Bezug. Auf f10r steht sie am Ende eines offenen Herbal-Feldes,
auf f83r am Anfang einer Bio-Zelle vor einer anderen abschliessenden Karte.
Darum gehoert weder feste Feldposition noch Abschluss zu F3. Gleichmenge oder
*ana* ist zu eng; gewoehnliche formelhafte Prosa und ein dyadischer Rahmen
bleiben Rivalen.

## Durchgehende Ruecklesung 1: vollständiger Herbal-Absatz f10r.6–12

Die vollstaendige ZL3b-Oberflaeche des zweiten Absatzes lautet:

```text
f10r.6  ycheor cthy chor cthaiin qoctholy dy chy taiin shy
f10r.7  dchy qokchol y kchaiin yty daiin cth dain dair am
f10r.8  qotchor chor otol chol cholor chol daiin dar
f10r.9  oykchor shor chor chy kaiiin dy chodaiin
f10r.10 oqotor otor cfhy cthor osain ytoiin
f10r.11 otchoshor qoty qotor cthyd otar
f10r.12 odaiin daiin qotchy qotor
```

Das ist ein Absatz, nicht sieben bewiesene Saetze. Der Stengel bzw. freie
Schreibraum hat die physische Reihung bestimmt. Eine konkrete, absichtlich
source-class-hafte Ruecklesung ist:

> **Zum abgebildeten einfachen Stoff:** Nenne zuerst seine kennzeichnende
> Beschaffenheit und den Zustand, in dem er gebraucht wird; fuehre die zwei
> markierten Angaben unter dem gleichen geltenden Bezug. Nimm als naechstes
> den zuzurichtenden Teil, setze ihn mit dem Arbeitsmedium oder Traeger an und
> halte das angegebene Mass beziehungsweise den Standard fest. Fuehre unter
> derselben Beziehung die weiteren Teil- oder Zustandsmerkmale auf und notiere
> die zugehoerige Anwendung. Danach gib die zweite Beschaffenheit, die
> alternative Zurichtung und ihren Gebrauch an. Schließe den Artikel mit
> Zeitpunkt/Grad und der letzten Anwendungsvariante.

Diese Lesung ist kontinuierlich und erklaert, warum derselbe Absatz sowohl
seltene Inhaltskarten als auch `L/O`, `AIIN`, `Y` und F3 fuehrt. Sie behauptet
nicht, welche einzelne Gruppe `Teil`, `Medium`, `Mass` oder `Anwendung`
bedeutet. Die Quellklassen sind auf Absatzebene eingesetzt:

- `Beschaffenheit/Zustand`: **0.50**;
- `Zurichtung mit Medium/Traeger`: **0.47**;
- `Anwendung/Gebrauch`: **0.45**;
- `Mass/Grad/Standard`: **0.36**;
- `Zeitpunkt` bereits im Herbal-Absatz: **0.25**.

Der staerkste alternative Absatzinhalt ist botanisch-deskriptiv—Identifikation,
Habitat und mehrere morphologische Merkmale—ohne Rezept oder Anwendung. Er
passt zur offenen Form, erklaert aber F3/L/O nicht schlechter oder besser;
deshalb bleibt er fuer einzelne Klauseln voll live.

## Durchgehende Ruecklesung 2: vollständiger Bio-Record f82r.27

Die reale Zeile besitzt sieben bestaetigte Felder:

```text
Oberflaeche:
pchedy // rsheal | daldy // qokeedy // rshedy // qoteedy // qokeedy // lochedy

Kartenlaengen:
1C | 2C | 1C | 1C | 1C | 1C | 1C

anonyme Werte:
A | (B,b) | C | D | E | C | F
```

Das gleiche exakte `qokeedy` in Feld 3 und Feld 6 ist derselbe formale Wert C;
es ist nicht bloss zweimal derselbe Punkt. Als Konfigurationskarte fuer das
abgebildete Bad/Gefaess bzw. die Anwendung lautet die konkrete Ruecklesung:

> **Fuer die bereits gezeigte Anwendung:** Bestaetige im ersten geerbten Slot
> das Medium oder den Grundzustand A. Setze im zweiten Slot die qualifizierte
> Zurichtung B mit Zusatz b. Trage fuer den naechsten Weg oder Zustand C ein,
> fuer Dauer/Grad den Wert D und fuer Einsatzstelle oder Wirkungsklasse E.
> Verwende beim korrespondierenden zweiten Weg nochmals genau Zustand C und
> bestaetige zuletzt den Endzustand bzw. die Freigabeklasse F.

Die sieben konkreten Inhaltsklassen sind nicht gleich sicher. Wichtig ist die
ausfuehrbare Kernaussage: sieben geerbte Fragen erhalten sieben bestaetigte
kategorische Antworten, wobei Antwort C in zwei Slots identisch ist.

- `Medium/Grundzustand`: **0.46**;
- `Zurichtungs- oder Prozesszustand`: **0.51**;
- `Weg/Auslass/Anwendungsrichtung`: **0.40**;
- `Dauer/Grad`: **0.35**;
- `Einsatzstelle/Wirkungsklasse`: **0.31**.

Eine reine Checkliste (`vorhanden / ausgefuehrt / Exemplarvariante`) kann
dasselbe Formmuster erzeugen. Sie verliert in der Gesamtwertung erst durch die
integrierte Bio-Ikonographie, nicht durch diesen Record allein.

## Durchgehende Ruecklesung 3: die drei Astro-Diagramme

### f67r2 — Sieben mal Zwoelf als Kombinationswaehler

Whole-diagram reading:

> Waehle aus dem Siebenerkranz den derzeit herrschenden Himmelsgeber oder die
> Wochen-/Planetenklasse. Stelle ihn zum passenden der zwoelf Abschnitte. Das
> Zentrum bezeichnet den aktuellen Fall oder die daraus zu lesende
> Prognoseklasse. Benutze die Kombination als Zeit- oder Bedingungsschluessel
> fuer den praktischen Eintrag.

Der konkrete Tipp `sieben Planeten/Tagherrscher × zwoelf Tierkreisabschnitte`
hat **0.48**. Er ist historisch und numerisch attraktiv, aber die lokale
Topologie ist kein nachgewiesenes bekanntes Schema. Ein Kalender-/Rechenrad
ohne Medizin ist der staerkste Seitenrivale.

### f68r1 — Zentrum plus 28 als Identifikationsfeld

Whole-diagram reading:

> Nimm das Zentrum als Bezugskoerper, laufenden Fall oder Hauptschluessel.
> Suche unter den 28 umgebenden beschrifteten Sternorten die gegenwaertige
> Station und uebernimm deren lokale Kategorie. Die raeumliche Anordnung hilft
> beim Finden, ist aber keine bewiesene Rundfolge.

Der konkrete Tipp `28 Mondstationen um den Mond/Bezugskoerper` hat **0.45**.
Gerade weil keine autorielle Reihenfolge sichtbar ist, lese ich die Seite als
Katalog oder Gedächtnisfeld, nicht als automatisch zu durchlaufenden Kalender.
Ein allgemeines Sternnamenverzeichnis bleibt gleichwertig fuer diese Seite.

### f69v — 28 alternierende Loci als Ablauf- oder Prognosetafel

Whole-diagram reading:

> Bestimme den geltenden der 28 radialen Orte nach einer ausserhalb der
> Zeichnung gelernten Start- und Laufrichtung. Lies dann die dort eingetragene
> Zeit-/Prognoseklasse. Lange und kurze Loci markieren zwei abwechselnde
> Darstellungs- oder Antwortklassen—beispielsweise guenstig/unguenstig,
> handeln/ruhen oder zwei Arten von Eintrag—nicht notwendig zwei verschiedene
> Laengenwerte.

`28 Mondtage oder Mondstationen mit prognostischer Klasse` erhaelt **0.47**;
die speziell medizinische `Behandeln/Meiden`-Lesung **0.34**. Da Start und
Richtung nicht autorensichtbar sind, darf kein externer 28er-Donor direkt auf
die Positionen gelegt werden. Die Bedienfolge kann durch Unterricht,
Randwissen oder die Labels selbst bekannt gewesen sein.

### Gemeinsame Astro-Ruecklesung

Zusammengenommen entsteht ein plausibler Dreischritt:

```text
f67r2  kombiniere Herrscher/Bereich
f68r1  identifiziere eine von 28 Stationen
f69v   lies fuer eine 28er-Stelle Zeit- oder Prognoseklasse
```

Das ist die fuehrende Funktionskette, keine festgestellte Crosspage-Verweisung.
Die drei lokalen Layouts bleiben getrennt; eine direkte f68↔f69-Listenidentitaet
wird nicht behauptet.

## Gerankte konkrete Inhaltsannahmen

Die V14-Pflicht, Inhalt nicht vollstaendig hinter `OPAQUE` zu verstecken, fuehrt
zu folgender Rangliste. Keine Annahme wird allein wegen fehlenden Beweises
verworfen:

| Rang | Inhaltsannahme | Konfidenz | Traegt welche Seiten? |
|---:|---|---:|---|
| 1 | einfache Stoffe plus Qualitaet/Zustand und Zurichtung | .55 | Herbal, besonders offener lokaler Schwanz |
| 2 | Bad-, Medium-, Gefaess- oder Anwendungskonfiguration | .51 | Bio-B und die bebilderten stillen Argumente |
| 3 | kategorialer Prozess-/Ergebniszustand im 12/10/8/8-Deck | .49 | alle drei Bio-Seiten |
| 4 | astrologischer Zeitpunkt oder Prognosekategorie | .46 | alle drei Astro-Instrumente |
| 5 | Grad, Dauer, Dosis oder aktiver Standard | .38 | AIIN/F3 und Bio-Slots; nicht als AIIN-Wortgloss |
| 6 | Anwendungsweg, Auslass oder Koerperstation | .35 | Bio-Ikonographie und wiederholte Werte |

Die Annahmen sind kompatibel, aber nicht alle muessen zugleich wahr sein. Eine
bessere Idee ersetzt sie erst, wenn sie mehr der zehn Seiten mit weniger
Zusatzregeln erklaert.

## Warum exakte Karten wichtiger sind als naive EVA-Woerter

Die Werkstatt kopiert erkennbare Kartenkerne und rendert sie lokal. Darum fallen
sichtbar verschiedene Gruppen auf dieselbe exakte Karte:

```text
AIIN / DAIIN / SAIIN / CHAIIN / TAIIN  -> eine AIIN-Karte
Y / DY / CHY / SHY / SY / CHEY         -> eine Y-Karte
CHOL (Herbal) / OL (Bio)                -> dieselbe L/O-Karte moeglich
```

F3 bleibt als exakte Folge erhalten, obwohl seine sichtbaren Wrapper auf f10r
`CH–T–SH` und auf f83r `CHE–D–CHE` sind. Ein Lehrling, der nur EVA-Woerter
zaehlt, haelt dieselbe Formel fuer zwei verschiedene Phrasen. Ein Lehrling, der
nur Kartenkerne kopiert, macht dagegen einen anderen Fehler: Er kann die
positions- und registergerechte Huelle vergessen. Die zweistufige Korrektur
`Karte zuerst, Renderer danach` erklaert beides.

Die 17 Herbal/Bio-gemeinsamen Karten tragen 44/100 gedeckte Herbal- und 92/281
Bio-Ereignisse. Sie bilden den tragbaren Kern. Dass genaue Kartenidentitaet
staerker ist als eine vermeintliche Wortaehnlichkeit, folgt gerade aus der
grossen seltenen lokalen Restmenge: Registerwissen wird durch lokale
Exemplare, nicht durch freie Buchstabenkomposition erweitert.

## Bildzuerst und Reflow

Die Bilder sind Seitenadressen und Arbeitsgerueste, keine Garantie, dass jede
benachbarte Zeile genau das beruehrte Blatt, Rohr oder Sternchen benennt. Ein
plausibler Produktionsgang ist:

```text
1. Layout und Bild werden festgelegt.
2. Der Schreiber setzt Artikel, Zellen oder Labels in den verbleibenden Raum.
3. Herbal-Saetze duerfen ueber physische Zeilengrenzen weiterlaufen.
4. Bio-Zellen schliessen formal, auch wenn mehrere auf einer Zeile stehen.
5. Astro-Labels gehoeren primaer zu Positionen des Diagramms.
```

Das erklaert, warum Bildnaehe zugleich inhaltlich wichtig und als
Wort-Objekt-Zuordnung unzuverlaessig sein kann. Der Gegenstand ist vom Bild
geerbt; die physische Umbrechung entsteht aus Platz.

## Mehrere Haende, Wartung und typische Lehrlingsfehler

Mehrere Schreiber koennen dieses System stabil halten, wenn sie gemeinsame
Karten und Formeln aus einem Musterblatt lernen, seltene Inhalte jedoch aus dem
jeweiligen Registerexemplar kopieren. Erwartbare Fehler sind:

1. **Falscher Registermodus:** Ein Lehrling schliesst jede Herbal-Zeile wie
   eine Bio-Zelle oder laesst Bio-Werte offen.
2. **Zeile als Satz:** Er beginnt nach einem Stengel-bedingten Umbruch einen
   neuen Herbal-Gedanken und verliert die laufende Beziehung.
3. **Bildwort-Zwang:** Er weist jeder Zeile das naechste Blatt/Rohr zu, obwohl
   das Bild nur den Dossierbesitzer liefert.
4. **EVA-Wortkopie:** Er kopiert eine sichtbare Huelle aus dem falschen
   Register und verkennt, dass der Kartenkern gleich bleiben soll.
5. **Wrapperharmonisierung:** Er macht die drei Karten von F3 aeusserlich
   gleich oder uebernimmt die Herbal-Huellen in Bio.
6. **L/O-Reset:** Er vergisst am Feld- oder Zeilenrand den geerbten
   Relationsteilnehmer; besonders f83r.52→54 wird dann unanschliessbar.
7. **qokaiin-Dittographie:** Er streicht eine der beiden f82r-Grenzkopien als
   Fehler, obwohl die erste den kommenden Eintrag ankündigen und die zweite ihn
   am Zeilenanfang realisieren kann. Der umgekehrte echte Dittographiefehler
   bleibt moeglich und wird am Exemplar entschieden.
8. **Commit als Punkt:** Er sieht in der Terminalkarte nur Interpunktion und
   verliert deren exakte A/B/C/D-Nutzlast.
9. **Astro-Prosaimport:** Er sucht AIIN, L/O oder qokaiin allein nach
   Oberflaechenaehnlichkeit in den Kreislabels und zerstoert deren lokalen
   Positionsschluessel.
10. **Liste ohne Startwissen:** Er behandelt f68r1 als geordnete 28er-Folge
    oder erfindet fuer f69v einen sichtbaren Start. Korrektur: Katalog und
    Ablauf bleiben verschiedene Stencils.

## Historische Plausibilitaet um 1420

Die vorgeschlagene Inhaltsmischung ist nicht anachronistisch. Der etwa
1420–30 datierte [British Library Add MS 29301](https://searcharchives.bl.uk/catalog/032-002020783)
vereinigt illustrierte Chirurgie, Heilpflanzen, Herbal- und Rezeptmaterial mit
einem Zodiac Man. Der etwas spaetere
[Harley MS 1736](https://searcharchives.bl.uk/catalog/040-002047567)
vereinigt Chirurgie, Waesser/Distillation, medizinische Rezepte, medizinische
Astrologie, Planeten und Tierkreistafeln. Diese Vergleiche belegen weder einen
Voynich-Donor noch die Kartenkonvention; sie zeigen nur, dass ein praktischer
medizinischer Sammelband mit astrologischem Anhang fuer die Zeit eine
sparsamere Annahme ist als drei zufaellig zusammengebundene, voellig fremde
Projekte.

Auch die Herstellung ist historisch schlicht: Der Meister besitzt
Inhaltsexemplare und Musterkarten, der Zeichner disponiert die Seite, mehrere
Schreiber fuellen sie in ihren Haenden, und ein Korrektor prueft gegen das
Registerexemplar. Kein moderner Codebuchapparat, keine universelle Tabelle und
keine phonetische Geheimschrift sind fuer den Ablauf erforderlich.

## Konkurrenz, Spannungen und Wertung

| Kriterium | Punkte | Begruendung |
|---|---:|---|
| Abdeckung aller zehn Seiten | 23/25 | erklaert Artikel, Bruecke, Zellen, Wertdeck und alle drei Kreislayouts; keine direkte Crosspage-Verweisung |
| eine lernbare Mehrschreiber-Regel | 19/20 | vier Hilfen, drei Registerstencils, gemeinsamer Karten-/Renderer-Ablauf |
| Registerdifferenzierung | 15/15 | WAS/offen, WIE/committed, WANN/raeumlich |
| konkrete Ruecklesungen | 13/15 | kompletter Herbal-Absatz, Bio-Record und drei Diagramme; Kartenglossen bleiben offen |
| Plausibilitaet um 1420 | 13/15 | reale medizinisch-astrologische Sammelcodices; keine Voynich-spezifische Kartenparallele |
| Rivale und Vorhersagen | 9/10 | Musterbuch erklaert Form stark; fester Bild-Wert-Test trennt die Modelle |
| **Summe** | **92/100** | fuehrender V14-R1-Entwurf |

Die groessten Spannungen sind offen benannt:

- Keine feste Seite zeigt einen expliziten Herbal→Bio→Astro-Pointer.
- Der medizinische Inhalt der Bio-Bilder ist plausibel, aber eine allgemeinere
  naturphilosophische oder technische Apparatur bleibt moeglich.
- f68r1 hat keine autorielle 28er-Reihenfolge, f69v keinen sichtbaren Start;
  beide duerfen nicht als dieselbe Liste zwangsvereinigt werden.
- Das 12/10/8/8-Deck liefert Kategorien, aber keine identifizierten Werte.
- Der Herbal-Absatz traegt konkrete Quellklassen, jedoch keine Wort-fuer-Wort-
  Zuordnung.

Nichts davon macht die fuehrende Theorie unmoeglich. Der Musterbuchrivale wird
erst fuehrend, wenn Bildinhalt und wiederholte Wertkarten innerhalb der festen
Seiten systematisch voneinander unabhaengig sind.

## Die eine Beobachtung, die das Ranking am staerksten aendern wuerde

Innerhalb der bereits festen Seiten ist der entscheidende naechste Schritt ein
**bildzuerst eingefrorener Bio-Wert-Test**:

1. Vor Einsicht in Kartenidentitaeten werden auf f81v, f82r und f83r alle
   wiederholbaren visuellen Rollen markiert: Behaeltertyp, Ein-/Auslass,
   Figurenlage, Verbindung, Station und korrespondierender Gegenweg.
2. Danach wird nur geprueft, ob die vier 12/10/8/8-Terminalfamilien bei
   derselben visuellen Rolle ueber mehrere Bilder/Seiten wiederkehren.
3. Ein stabiler Zusammenhang—besonders wenn derselbe Wert C in f82r.27 an zwei
   visuell korrespondierenden Wegen steht—wuerde die Anwendungs-/Konfigurations-
   theorie deutlich ueber **0.70** heben.
4. Gleich gute Kartenverteilung nach Seitenplatz, Schreibrhythmus oder
   Exemplarzeile ohne Bildrollen wuerde das allgemeine Muster-/Lehrbuch zum
   Sieger machen.

Dieser Test erweitert weder Seiten noch Lexikon und benoetigt keine
Substring-Suche. Er entscheidet genau die offene Konkurrenz zwischen
inhaltlichem Arbeitsformular und formalem Schreibexemplar.

## R1-Schluss

Als Lehrmeister wuerde ich das Buch so erklaeren:

> **Das Bild setzt den Gegenstand. Im Pflanzenregister schreibst du den offenen
> Stoffartikel und passt ihn um die Zeichnung. Im Anwendungsregister fuellst du
> die kurzen geerbten Fragen mit exakten Werten und bestaetigst jede Zelle. Im
> Himmelsregister suchst du die Lage raeumlich nach. Verwende qokaiin fuer den
> naechsten Eintrag, L/O fuer die fortgesetzte Beziehung und Y–AIIN–Y als feste
> gemeinsame Bezugsformel. Kopiere zuerst die genaue Karte, dann ihre lokale
> Huelle.**

Damit erhalten alle zehn Seiten einen Zweck, ohne ihre unterschiedlichen
Register zu nivellieren. Die beste Gesamtlesung ist ein praktisches
iatromedizinisches `WAS / WIE / WANN`-Arbeitsbuch. Das allgemeine Musterbuch
bleibt der ernsthafte Rivale, aber es erklaert vorlaeufig weniger vom Aufwand
und von der fachlichen Gliederung der Bilder.
