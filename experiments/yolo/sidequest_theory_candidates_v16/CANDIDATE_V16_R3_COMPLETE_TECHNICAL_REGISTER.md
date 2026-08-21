# V16 R3 — vollständiges konkretes Werkstattregister

Datum: 2026-08-21

Status: unabhängiger, maximal explorativer Sidequest-Kandidat. Dies ist eine
absichtlich vollständige Arbeitsübersetzung, kein GDT-Ergebnis und keine
Entzifferungsbehauptung. Die V16-Ausgaben der anderen Rollen wurden nicht
gelesen. `f84` und `f84r` blieben versiegelt.

## Ergebnis

Ich wähle als einfachste vollständig ausführbare Lesung ein
**iatromedizinisches Kartenregister**:

```text
Herbal: Bild-Simple + Name/Eigenschaft/Standort/Zubereitung/Gebrauch
Bio:    Bild-Apparat oder Körper + kurze Wasser/Bad/Anwendungs-Buchungen
Astro:  gezeichneter Himmelslocus + lokale Zeit-/Behandlungsregel
```

Das System ist kein moderner Datensatz. Ein Meister führt ein kleines
allgemeines Kartenblatt, Registerblätter und Seitenexemplare. Häufige
Quellphrasen werden durch eine ganze Karte vertreten; seltene Pflanzennamen,
Eigenschaften und technische Anweisungen werden als eigene Ganzkarten aus dem
Exemplar kopiert. Das bereits gezeichnete Bild liefert ausgelassene Subjekte
und Operanden. Wrapper und angefügte Schlüsse passen die Karte an Hand,
Zeilenanfang und lokale Zelle an.

V16 erzwingt eine konkrete Belegung auch dort, wo der Befund sie nicht
identifiziert. Deshalb ist die entscheidende Änderung gegenüber V15:

```text
keine Karte bleibt leer;
Unsicherheit steht in confidence, nicht im Bedeutungsfeld.
```

## Vollständigkeit

Die maschinenlesbaren Ergebnisse sind:

- `V16_R3_COMPLETE_DEFAULT_LEXICON.tsv`: 568 Lexikoneinträge;
- `V16_R3_COMPLETE_TRANSLATION_LEDGER.tsv`: 776 sichtbare Gruppen;
- davon 381 GDT327-Prosaereignisse in 173 exakten Kartentypen;
- dazu 395 ZL3b-Gruppen auf 142 Astro-Zeilen;
- f67r2 190, f68r1 65, f69v 140 Astro-Gruppen;
- kein leeres Bedeutungsfeld und kein neutraler Restwert.

Die Astro-Zählung benutzt genau eine primäre Lesung, ZL3b. IT2a und RF1b sind
alternative Lesungen desselben Textes und werden nicht als zusätzliche Belege
gezählt. Jede Gruppe eines Mehrgruppenlabels besitzt im Ledger eine eigene
Rolle.

## Ausführbare Schreib- und Rückleseregel

Der Schreiber führt vier Gedächtnisplätze:

```text
R = HERBAL | BIO | ASTRO
H = durch Bild oder laufenden Absatz gesetzter Hauptbezug
P = derzeitige Portion, Pflanzenteil, Gefäßstation oder Himmelslocus
M = zuletzt genannte Menge, Flüssigkeit oder Relation
```

Schreiben:

1. Das vorgezeichnete Bild setzt `R` und `H`.
2. Eine häufige Quellphrase wird als gelehrte Ganzkarte gewählt.
3. Eine seltene Fachphrase wird als lokale Ganzkarte aus dem Seitenexemplar
   kopiert; der Lehrling muss ihre Buchstaben nicht phonetisch analysieren.
4. In Herbal dürfen mehrere Karten und Aussagen über physische Zeilen laufen.
5. In Bio wird eine kurze Handlung, Relation, Menge oder Ergebnislage gebucht;
   ein angefügter DY/B3-Schluss bestätigt die lokale Anweisung.
6. In Astro ersetzt der gezeichnete Locus die ausgeschriebene Adresse. Die
   sichtbare Gruppe liefert Stationsbezeichnung, Eigenschaft oder Regelwort.
7. Erst danach wählt der Renderer Wrapper, JOIN/SPACE und Zeilenform.

Rücklesen:

1. Rekonstruiere die exakte Ganzkarte und ignoriere den Wrapper als
   Bedeutungswechsel.
2. Ergänze das stumme Subjekt aus Pflanze, Gefäß/Körper oder Kreisposition.
3. Lies die Karte mit dem festen Werkstattgloss.
4. Bei einer geschlossenen Bio-Karte führe die Anweisung aus und markiere sie
   als erledigt.
5. An einer physischen Zeile bleibt `H/P/M` aktiv; Zeilenende ist nicht
   Satzende.

Das ist um 1420 lehrbar: der Lehrling memoriert ungefähr fünfzig häufige
Karten, erkennt vier Grundkonstruktionen und kopiert die seltene lokale
Schwanzmenge aus einem Exemplar. Er braucht weder eine moderne Chiffre noch
eine vollständige botanische Ausbildung.

## Kernwörterbuch

| Objekt | konkrete Default-Lesung | Konfidenz |
|---|---|---:|
| qokaiin | **nimm die nächste Portion** | .64 |
| L/O | **mit derselben Zubereitung** | .61 |
| AIIN | **die übliche abgemessene Portion** | .58 |
| Y | **diese gegenwärtige Portion** | .52 |
| CTHY | **wenn vollständig zubereitet** | .46 |
| FORMULA_F3 = Y–AIIN–Y | **beide Portionen nach demselben üblichen Maß** | .44 |
| VAL-Q = qokedy | **Standardeinstellung beibehalten und bestätigen** | .50 |
| VAL-QE = qokeedy | **temperierte Flüssigkeit verwenden und bestätigen** | .48 |
| VAL-S = shedy/cheedy/tedy | **fertig eingestellt belassen** | .45 |
| VAL-L = lchedy | **örtlich gießen oder spülen und bestätigen** | .43 |

Weitere wiederkehrende Karten erhalten ebenfalls feste Bedeutungen, etwa:

```text
OKEEY       erwärme die Arbeitsflüssigkeit
OKAIN       miss die Arbeitsflüssigkeit ab
OKAL        in sauberem Wasser
CKHY        teile es zwischen den beiden Kanälen
OR          aus der genannten Quelle
AL          in das untere Gefäß
CHAR/DAR    fahre dann fort
OKY         wende es an der bezeichneten Stelle an
OLCHEDY     führe es durch den Kanal und bestätige
OLKEEDY     lasse die Flüssigkeit stehen und bestätige
QOKCHDY     verbinde den bezeichneten Kanal und bestätige
```

Bei den 122 nicht im gemeinsamen Kernblatt festgelegten Karten ist die
Bedeutung ausdrücklich `CONTEXT_DEFAULT`: eine eigene konkrete Phrase aus dem
Herbal- oder Bio-Seitenexemplar, mit Konfidenz .24. Das ist keine Behauptung,
dass Hash oder EVA-Form diese Phrase verrät. Es ist die kleinste vollständige
Codebuchannahme: seltene ganze Karten können Namen oder ganze Fachwendungen
speichern.

## Durchgehende Übersetzung f10r

### Record 1, f10r.2–5

> **Für das abgebildete Simple:** Wende das zerstoßene Blatt auf eine
> Schwellung. Es wächst an fließendem Wasser; fahre dann fort. Seine trockene
> Beschaffenheit dient zur Winteraufbewahrung der Wurzel; es trocknet im ersten
> Grad. Nimm davon morgens einen kleinen Löffel, wende ihn an der bezeichneten
> Stelle an, gebrauche die übliche Portion und koche die Flüssigkeit auf die
> Hälfte ein. Verwende die Blütenspitze, nicht den Samen, zusammen mit derselben
> Zubereitung, sobald sie vollständig bereitet ist.

### Record 2, f10r.6–9

> Das Mittel ist warm im zweiten Grad und soll vollständig bereitet sein. Aus
> dem genannten Pflanzenteil erweicht es harte Schwellungen und reinigt eine
> unreine Wunde. **Beide Portionen stehen unter demselben üblichen Maß.** Führe
> den zweiten Gebrauch aus derselben Quelle mit derselben Zubereitung fort;
> ebenso nimm denselben Teil mit derselben Zubereitung und der üblichen Portion,
> dann fahre fort. Weiche zuletzt die Blütenspitze in Wein ein; aus derselben
> Quelle kommt die gegenwärtige Portion, und die Pflanze hat einen gebüschelten
> Blütenkopf und breite gezähnte Blätter.

Die harte Wiederholung in f10r.6 ist kein Fehler: sie ist die ausgeschriebene
Default-Lesung von F3. Eine spätere Theorie darf `portion` durch zwei
symmetrische andere Operanden ersetzen, muss aber die Doppelstruktur erklären.

## Durchgehende Übersetzung f56r

Der ganze sichtbare Block ist ein Record; die Aussage läuft über alle sieben
physischen Zeilen:

> **Für das abgebildete stachlige Simple:** Grabe die Wurzel im Herbst und
> verwende das stachlige Blatt zerstoßen auf einer Schwellung in der üblichen
> Portion. Das Blatt wächst an fließendem Wasser; beim zweiten Gebrauch wende
> es an der bezeichneten Stelle in einem unteren Gefäß an. Dieses abgebildete
> Simple reinigt eine unreine Wunde; wende es dort an und koche die Wurzel in
> Wasser. Mische das Pulver mit Honig; vom stachligen Blatt wird das größere
> bevorzugt, besonders bei Pflanzen vom Wasserstandort. Verwende außerdem die
> Blütenspitze; sie ist warm im zweiten Grad und die getrocknete Wurzel wird für
> den Winter bewahrt. Wiederhole Blattanwendung und Blütenspitze, grabe die
> Wurzel im Herbst und bewahre sie trocken. Für das Hauptmittel weiche die
> Blütenspitze in Wein ein und gib die übliche Portion.

Die Übersetzung endet nicht künstlich an jeder Zeile. Das Bild erklärt die
kurzen Zeilen als Reflow; die Wiederholungen werden als listenartige
Rezeptfortsetzung gelesen.

## Vollständige Übersetzung des Bio-Records f82r

Alle acht sichtbaren Buchungspakete gehören in der GDT327-Sicht zu einem
laufenden Record. `//` trennt nur die physischen Pakete:

> **f82r.2:** Mische gründlich und bestätige; führe die Mischung durch den
> Kanal und bestätige. Miss die Arbeitsflüssigkeit ab, nimm die gegenwärtige
> Portion, verwende die temperierte Flüssigkeit und bestätige. Arbeite in
> sauberem Wasser; lasse abkühlen und stehen, bis es klar wird.
>
> **f82r.3:** Erwärme die Arbeitsflüssigkeit. Wiederhole die Waschung zweimal,
> nimm sie an der vorigen Station wieder auf, teile sie zwischen den beiden
> Kanälen und nimm die nächste Portion.
>
> **f82r.4:** Nimm die nächste Portion, halte sie mäßig warm, verwirf die erste
> Waschung und führe die Flüssigkeit weiter. Nach der zweiten Waschung arbeite
> in sauberem Wasser, lasse die Flüssigkeit hinab und wende sie an der
> bezeichneten Stelle an.
>
> **f82r.7:** Öffne den oberen Einlass; gib das doppelte übliche Maß. Öffne den
> Einlass, lasse die Einstellung fertig stehen, lasse die Flüssigkeit hinab,
> erwärme sie und wende sie an. Belasse die letzte Portion bereit, bis sie
> lauwarm ist.
>
> **f82r.19:** Miss die Arbeitsflüssigkeit; fahre fort, miss sie nochmals,
> verwende die temperierte Flüssigkeit und bestätige die vollendete Anwendung.
>
> **f82r.23:** Solange der Kanal offen ist, erwärme die Flüssigkeit und führe
> sie in das zweite Becken. Nimm die übliche gegenwärtige Portion, tauche den
> bezeichneten Teil ein, gieße oder spüle örtlich und ziehe die klare
> Flüssigkeit ab.
>
> **f82r.26:** Gib eine zweite kleine Portion, verwende temperierte Flüssigkeit
> und leite sie in das untere Gefäß. Nimm die Arbeit an der vorigen Station
> wieder auf, bade den bezeichneten Körper, verwende die übliche Portion und
> nimm nach der zweiten Waschung die nächste Portion an der nächsten markierten
> Station.
>
> **f82r.27:** Lasse abkühlen, lasse die Flüssigkeit hinab und verwirf die erste
> Waschung. Verwende die temperierte Flüssigkeit und bestätige; halte sie mäßig
> warm, verwende und bestätige die stärkere Zubereitung, verwende nochmals die
> temperierte Flüssigkeit und halte sie mäßig warm.

f82r.27 erhält damit eine konkrete, nicht bloß formale Lesung. Die zweimalige
VAL-QE-Karte bedeutet beide Male exakt dieselbe temperierte Anwendung.

## Vollständige Astro-Lesung

### f67r2

Die zwölf Loci f67r2.1–12 sind die **Tierkreisabteilungen A–L**; zusätzliche
Gruppen bezeichnen jeweils herrschende Qualität und Körperregion. Die zwölf
Loci f67r2.52–63 sind die **medizinischen Tierkreissektoren 1–12** mit
erlaubter beziehungsweise verbotener Behandlung. f67r2.64–70 tragen in der
Arbeitslesung Saturn, Jupiter, Mars, Sonne, Venus, Merkur und Mond;
f67r2.71 ist die zentrale Herrschaftsregel. Die übrigen lokalen Labels sind
benannte Wahlstellen, die Prosa erklärt:

> Für den gegenwärtigen Fall wähle den herrschenden Planeten, finde seine
> Tierkreisabteilung, notiere Körperregion und Qualität, lies erlaubte und
> verbotene Behandlung und das richtige Maß; kehre dann zum praktischen Record
> zurück.

Jedes einzelne Wort dieser Legende und jedes Mehrgruppenlabel ist im Ledger
belegt. Die Buchstaben A–L sind Arbeitsadressen, keine behaupteten
mittelalterlichen Zeichen- oder Monatsnamen.

### f68r1

f68r1.8 bezeichnet den **zentralen Mondbezug**. f68r1.9–36 bezeichnen 28
einzeln geplottete **Mondstationen**. Ihre Ledgernamen lauten bewusst
`lunar station at plotted locus 01..28`: Das ist eine konkrete räumliche
Identität, aber keine erfundene Umlaufrichtung und kein behaupteter Start des
Autors. Drei zusätzliche Einzellabel werden als östlicher Lichtanker,
westlicher Mondanker und zentraler Bezugsstern gelesen. Die Prosa lautet:

> Unter dem zentralen Mond finde die markierten Sterne an ihren gezeichneten
> Orten und verwende die Station der gegenwärtigen Nacht, bevor du die
> Behandlung wählst.

### f69v

Die 28 Radialloci sind ein Behandlungswahlkalender. Die Default-Regeln laufen
vom im Transkript so bezeichneten Locus 01 bis 28: günstig zum Baden; Aderlass
meiden; Heilblätter sammeln; warmes Mittel bereiten; Reinigung beginnen; Reise
verschieben; Salbe auf Schwellung legen; Wunde waschen; Wurzelabsud nehmen;
Schneiden/Brennen meiden; kühlenden Trank bereiten; nur leicht zur Ader lassen;
Blüten bei Tagesanbruch sammeln; Stärkung beginnen; von Reinigung ruhen;
untere Glieder baden; Arzneien abseihen und lagern; starke Hitze meiden;
vorheriges Mittel wiederholen; zweite Zubereitung nehmen; Seitenschmerz
behandeln; alte Wunde reinigen; kleinere Dosis geben; Abenddosis auslassen;
Baden wiederaufnehmen; Aderlass vorbereiten; Behandlung abschließen; Patienten
ruhen lassen.

Mehrgruppenloci besitzen als zweite Gruppe die feste Lesung **„wende diese
Regel auf den gegenwärtigen Fall an“**. Die drei äußeren Textbänder erklären,
wie Station und Fall gewählt, die Regeln gelesen und fortgeführt werden. Das
Ledger übersetzt alle 107 Bandgruppen und alle 33 Gruppen der 28 Radialloci.
`Locus 01` ist eine editorische Arbeitsadresse, keine Behauptung über den
historischen Zyklusbeginn.

## Ganze-Seiten-Paraphrasen

| Seite | konkrete Default-Paraphrase |
|---|---|
| f10r | Wassernahes blühendes Simple; Blätter/Wurzel/Blütenspitze, warme und trocknende Qualität, Wund- und Schwellungsgebrauch, Portion und Einkochen. |
| f11r | Dichtes blühendes Simple; Pflanzenpartien und Zubereitungszustand, danach Gebrauch in der üblichen Portion. |
| f55v | Breitblättriges Simple; Portionen, sauberes Wasser, abgeseihte Zubereitung und Anwendung um den vorgezeichneten Stamm herum. |
| f56r | Stachliges Simple; Herbstwurzel, Blatt- und Blütenspitzengebrauch, Wasserabsud, Honigpulver und übliche Portion. |
| f81v | Großes Becken-/Kanalsystem; Flüssigkeit messen, verteilen, erwärmen, spülen und in fertigen Zuständen bestätigen. |
| f82r | Mehrstufiges warmes Bad-/Spülverfahren mit zwei Kanälen, Waschungen, Portionen, Abkühlung und lokaler Anwendung. |
| f83r | Variantenblatt für Gefäß- und Körperanwendungen; Standard-, starke, lokale und paarige Ausgänge werden eingestellt und bestätigt. |
| f67r2 | Sieben Planetenherrscher gegen zwölf Tierkreis-/Körpersektoren als medizinischer Wahlzeiger. |
| f68r1 | Räumlicher Katalog eines zentralen Mondbezugs und 28 geplotteter Mondstationen. |
| f69v | 28-stellige Mondstationsfolge mit konkreten günstigen, ungünstigen und fortsetzenden Behandlungsvorschriften. |

## Was diese Lesung erklärt

1. **Mehrere Schreiber:** Sie teilen Kartenidentitäten und Registerblätter,
   nicht notwendigerweise dieselbe Oberflächenform.
2. **Currier A/B:** offener Herbal-Artikel versus kurze bestätigte Bio-Zellen.
3. **Bild vor Text:** das Bild spart Subjekte und zwingt Reflow, ohne dass jede
   benachbarte Karte einen sichtbaren Pflanzenteil bezeichnet.
4. **qokaiin-Mobilität:** „nimm die nächste Portion“ kann eröffnen, einen
   Untereintrag einleiten und am Zeilenwechsel anticipatorisch wiederholt
   werden.
5. **L/O-Mobilität:** „mit derselben Zubereitung“ darf medial, anfangs mit
   geerbtem linken Operand, allein als Ditto oder am Ende mit offenem rechten
   Operand stehen.
6. **F3:** zwei sichtbare Portionen teilen den üblichen Maßbezug.
7. **Bio-Wertdeck:** vier häufige exakte Schlüsse sind echte verschiedene
   Anwendungslagen und nicht nur Satzzeichen.
8. **Astro 7/12/28:** drei lokale Nachschlageinstrumente liefern Bedingungen
   für die praktische Medizin, ohne ein gemeinsames Wort-für-Wort-Lexikon zu
   verlangen.

## Schwierigkeiten und Revisionsregeln

- Viele Einmalkarten sind frei aus einem plausiblen Registerdeck belegt. Ihre
  .24-Konfidenz ist ehrlich: Vollständigkeit ist hier stärker als Evidenz.
- Die Wasser-/Bad-Lesung erklärt f81v/f82r gut, kann aber f83r auch zu eng
  machen; dort bleibt Salben-, Dampf- oder Apparatanwendung ein Rivale.
- AIIN ist positionsmobiler als ein gewöhnliches Mengenwort. Wenn eine bessere
  Theorie alle 20 Belege als Referenz/Norm statt Portion liest, soll die ganze
  Karte global ersetzt werden.
- Y kann ein technischer Zeiger statt einer Portion sein. Eine Revision muss
  F3 und alle 18 Belege gemeinsam ändern.
- Die konkreten Mondstationsregeln sind nicht aus den Strings gewonnen. Sie
  sind ein vollständiges seitenlokales Default-Codebuch und werden ersetzt,
  sobald eine bessere gemeinsame Ordnung mehr der drei Astro-Seiten erklärt.
- f68r1 besitzt weiterhin keinen behaupteten Autorenstart. Alle Nummern sind
  nur stabile Ausgabekoordinaten.

## Warum dieser Kandidat als neue Basis brauchbar ist

Er ist wahrscheinlich an vielen Einzelstellen falsch, aber er ist erstmals
**vollständig falsifizierbar**. Jede Karte hat genau eine Default-Lesung, jede
Wiederholung erzwingt dieselbe Phrase, jedes Bildargument ist explizit
vererbt, und jede seltene Karte steht als lokale Codebuchannahme sichtbar im
TSV. Die nächste Iteration kann nun Bedeutungen ersetzen, statt wieder 90 %
des Textes hinter neutralen Klassen zu verstecken.
