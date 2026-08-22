# V64 R2 — Historische Herbal-Zweitausgabe

Status: vollständige kreative Quellenedition, **keine Entzifferung**.

## Ergebnis

Die historisch brauchbarste Fünf-Record-Ausgabe bleibt materia-medizinisch,
aber nur als stark exemplarabhängige Kompilation:

| Record | Bildbesitzer | stärkster Pflanzenrivale | konkrete Artikelhandlung | V63 erkannt / gesamt |
|---|---|---|---|---:|
| H1 | Teufelsabbiss (*Succisa pratensis*) | Skabiose | gebranntes Wurzelwasser, kleine innere Gabe | 4/14 |
| H2 | dieselbe Bildpflanze | Skabiose | zwei recordlokale Blüten-/Blattfraktionen als Salbenansatz | 10/24 |
| H3 | Duftveilchen (*Viola odorata*) | Gundermann | klarer Veilchenwein und getrenntes Veilchenöl | 3/17 |
| H4 | Bärlauch/Allium (*Allium ursinum*) | Breitwegerich | Weinansatz, Wundwäsche, warmer Blattumschlag | 6/18 |
| H5 | Rundblättriger Sonnentau (*Drosera rotundifolia*) | Venushaarfarn | kurze Hautauflage und getrockneter Brusttrank | 6/27 |

Alle 100 Ereignisse, 20 Felder und 19 reflowten V61-Statements sind in den
TSVs ausgegeben. V63 erkennt im Herbal-Slice nur 29/100 Ereignisse; 71/100
sind `UNPARSED_EXEMPLAR`. Auf Feldniveau gibt es **0 UNIQUE**, 15 AMBIGUOUS
und 5 UNPARSED, auf Statementniveau 0/14/5. Die flüssige Ausgabe ist somit
eine historische Quellenwette, keine aus den Karten ableitbare Übersetzung.

## Editionsvertrag

- `CARD` bezeichnet ausschließlich eines der ausgewählten V60-Mnemonics.
- `FORMAL` bleibt stumme Kontrolle ohne Wortbedeutung; auch `CLOSE` wird
  nicht ausgesprochen.
- `REGISTER` ist eine anonyme recordlokale V62-ID.
- Jede Pflanze, jeder Pflanzenteil, jedes Medium, Leiden, Körperziel, jede
  Zahl und jede nicht ausdrücklich lizenzierte Handlung steht unter `IMAGE`,
  `GENRE` oder `EXEMPLAR`.
- Keine sichtbare Teilform, kein Klang und keine lateinische oder deutsche
  Buchstabenähnlichkeit wurde benutzt.

Das passt am ehesten zu einer kompilierten Werkstatthandschrift, in der ein
illustrierter Simplex-Artikel und Rezeptwissen nebeneinanderstehen. Ein reales
Vergleichsbeispiel ist British Library Egerton MS 747: derselbe Codex enthält
den illustrierten *Tractatus de herbis*, ein *Antidotarium*, Dosislehre,
Substitutionen, Gewichte/Maße und Pflanzensynonyme. Das belegt die historische
Mischbarkeit solcher Textsorten, nicht die Voynich-Gattung oder unsere
Reihenfolge. [British Library, Egerton MS 747](https://searcharchives.bl.uk/catalog/032-001983805)

## Fünf fortlaufende Quelltexte

Die vollständigen geschichteten Texte stehen in
`V64_R2_FIVE_RECORD_EDITIONS.tsv`; hier folgt jeweils die knappe
Quellenfassung.

### H1 — Teufelsabbiss-Wurzelwasser

> `[IMAGE:Vom Teufelsabbiss.] [GENRE:Nimm] [IMAGE:den unteren Wurzelstock], [GENRE:säubere und zerschneide ihn], [GENRE:gib ihn mit Quellwasser in den Brennhafen und fange den ersten Lauf in einem Glas auf]. [CARD:ANWENDEN?=Wende den aktiven Lauf an] [GENRE:innerlich] [CARD:MASS?=nach Maß] [EXEMPLAR:in kleiner Gabe] [GENRE:gegen Stechen im Leib]; [GENRE:verwahre den Rest verschlossen]. [EXEMPLAR:Nimm für frischen Gebrauch den ersten Lauf], [GENRE:erwärme ihn gelinde], [FORMAL:AKTIVEN_ARBEITSSTAND_VERKNÜPFEN; ohne Wortbedeutung] [REGISTER:H1:I001 fortgeführt], [CARD:BEREIT?=bis bereit] [EXEMPLAR:nach örtlichem Kriterium].`

Frankfurt Ms. germ. qu. 17 ist offiziell in das erste Viertel des 15.
Jahrhunderts datiert; der erlaubte V53-Bericht identifiziert auf 340v und
342v `Abis`/`Dufelbis` als gebrannte Wasser gegen inneres Geschwür oder
Stechen. Das macht Destillation und innere Gabe zu unserer engsten
zeitgleichen Gattungsanalogie. [Handschriftenmetadaten](https://sammlungen.ub.uni-frankfurt.de/msma/content/titleinfo/3654949),
[Digitalisat 340v](https://sammlungen.ub.uni-frankfurt.de/i3f/v20/3655638/full/full/0/default.jpg),
[Digitalisat 342v](https://sammlungen.ub.uni-frankfurt.de/i3f/v20/3655642/full/full/0/default.jpg)

Gegenbeleg: Die rote, doppelt verdickte Bildwurzel besitzt gerade nicht den
namengebenden stumpfen „Abbiss“. Brennhafen, Wasser, Glas und Krankheit sind
nicht kartengestützt.

### H2 — zwei Blütenfraktionen

> `[IMAGE:Von derselben Teufelsabbiss-Pflanze.] [GENRE:Nimm] [IMAGE:Blütenköpfe und junge Blätter] [CARD:BEREIT?] [EXEMPLAR:wenn sie eben aufgehen], [CARD:ANSATZ?=führe sie als frischen Ansatz], [GENRE:zerstoße sie und presse den Saft durch ein Tuch]. [EXEMPLAR:Fange die erste Fraktion auf], [GENRE:gib Olivenöl hinzu], [CARD:MASS?=nach Maß] [EXEMPLAR:in örtlicher Menge] [GENRE:und erwärme gelinde]. [IMAGE:Nimm vor voller Blüte eine zweite Portion], [CARD:VORIGES?=nimm den vorigen H2-Posten wieder auf] [REGISTER:H2:I001], [CARD:MASS?=in gleichem örtlichem Maß], [GENRE:und verbinde beide Fraktionen]. [CARD:ANSATZ?] [CARD:ANSATZ?] [REGISTER:H2:I003 mit sichtbarer Doppelbelegung], [GENRE:rühre bei kleinem Feuer und bewahre die weiche Salbe bedeckt]; [GENRE:lege sie äußerlich auf ein Geschwür oder eine harte Schwellung].`

Wichtigste Revision: V53 ließ `VORIGES?` auf H1s Wurzelwasser weisen. V62
setzt die Register aber in H2 neu; der Rückgriff kann nur H2:I001 aufnehmen.
H2 ist daher ein eigener Zwei-Fraktionen-Artikel. Das doppelte `ANSATZ?` in
F005 bleibt als Konflikt stehen; Dittographie oder zwei Materialklassen sind
gleichwertige Gegenlesungen. Kein Feld besitzt einen formalen Schluss.

### H3 — Veilchenwein und Veilchenöl

> `[IMAGE:Vom Duftveilchen.] [GENRE:Nimm im ersten Frühjahr] [IMAGE:Blüten und junge Blätter], [GENRE:koche sie in reinem Wein, wringe sie durch ein feines Tuch, lasse den Auszug stehen und seihe ihn nochmals] [CARD:KLAR?=bis klar] [EXEMPLAR:nach örtlicher Prüfung], [GENRE:dann lasse ihn abkühlen]. [EXEMPLAR:Behalte einen Teil der Blüten zurück]. [GENRE:Gib den ersten Auszug als Trank] [GENRE:bei bedrücktem Gemüt und beschwerter Brust] [CARD:MASS?=in einem Maß] [EXEMPLAR:kleiner örtlicher Größe]. [GENRE:Erwärme die zurückbehaltenen Blüten in Olivenöl] [CARD:BEREIT?=bis bereit] [EXEMPLAR:nach örtlichem Kriterium], [GENRE:und streiche das Öl äußerlich um die Lider, ohne das Auge zu berühren].`

*Physica* I.103 bietet ungewöhnlich nahe, aber ältere Verfahren: Veilchen in
reinem Wein, durch Tuch geseiht und bei Melancholie/Lungenbeschwerden
getrunken; daneben Veilchen in erhitztem Öl zur äußeren Anwendung um die
Augen. [Hildegard, *Physica* I.103](https://www.monumenta.ch/latein/text.php?domain=&hide_apparatus=&inframe=1&lang=1&level=4&links=&rumpfid=Hildegardis+Abbatissa%2C+Physica%2C+1%2C++103&tabelle=Hildegardis_Abbatissa)

Revision: Die V61-Wurzelernte entfällt, und V53s unspezifisches Geschwür wird
durch die enger belegte Lideranwendung ersetzt. Gegenbeleg: Gundermann passt
zu gekerbten Blättern und blauviolettem Kriechwuchs; die drei langen
Bildwurzeln passen weder ihm noch Viola.

### H4 — Alliumwein und Blattumschlag

> `[IMAGE:Vom breiten Lauch.] [CARD:MASS?=Nimm nach Maß] [EXEMPLAR:ein örtliches Maß] [IMAGE:breiter Blätter], [GENRE:zerstoße sie, füge Weißwein hinzu, verschließe das Gefäß und lasse es kühl stehen]. [CARD:MASS?=Miss eine Portion ab], [GENRE:wringe sie durch Leinwand, lasse sie klar absetzen und verwahre den Auszug]. [GENRE:Wasche damit eine unreine äußere Wunde] [EXEMPLAR:einmal oder nach örtlicher Vorschrift]. [CARD:MASS?=Nimm nach Maß] [EXEMPLAR:eine zweite Blattportion], [GENRE:erwärme sie], [CARD:ANSATZ?=führe sie als zweiten Ansatz], [GENRE:mische sie mit Honig und lege den warmen Umschlag frisch auf].`

Balds Augensalbe ist zeitlich und regional fern, belegt aber die robuste
Verfahrenskette Allium-Arten zerstoßen, Wein/Galle zufügen, neun Tage im
Metallgefäß stehen lassen, durch Tuch klären und äußerlich gebrauchen. Unsere
Edition übernimmt bewusst weder Galle, neun Tage noch Auge. [Harrison et al.,
*mBio* 2015](https://journals.asm.org/doi/10.1128/mBio.01129-15)

Der stärkste Rivale ist Breitwegerich: *Physica* I.101 nennt ausgepressten,
durch Tuch filtrierten Saft mit Wein oder Honig sowie warme Blätter auf einer
schmerzenden Stelle. [Hildegard, *Physica* I.101](https://monumenta.ch/latein/text.php?nf=1&rumpfid=Hildegardis+Abbatissa%2C+Physica%2C+1%2C++101&tabelle=Hildegardis_Abbatissa)
V64 verschiebt deshalb die Wundwäsche aus F011 in das vollständig unparsed
F012: F011 bildet nun Maß → Filtration → Lagerung, F012 den offen
exemplarischen Gebrauch. F013 bleibt ohne Schluss.

### H5 — Sonnentau, bewusst höchste Risikostufe

> `[IMAGE:Vom rundblättrigen Sonnentau.] [GENRE:Sammle] [IMAGE:das ganze oberirdische Kraut im feuchten Moor] [EXEMPLAR:zu Beginn der Blüte] [CARD:MASS?=in einem Maß] [EXEMPLAR:nur eine kleine Menge]. [GENRE:Zerstoße die frischen klebrigen Blätter und lege sie auf] [EXEMPLAR:eine einzelne Warze oder ein Hühnerauge]; [CARD:ANWENDEN?=wende sie an] [EXEMPLAR:nur kurz] [CARD:ZIEL?=an der Zielstelle] [EXEMPLAR:der bezeichneten Haut]. [GENRE:Nimm die Auflage ab und wasche die Stelle]; [CARD:ANWENDEN?=wiederhole den Gebrauch] [EXEMPLAR:nur falls vertragen]. [GENRE:Trockne die übrigen blühenden Stiele im Schatten]. [GENRE:Setze daraus mit mildem Wein einen schwachen Auszug an, seihe ihn durch Tuch, füge Honig hinzu und gib ihn als Brusttrank] [GENRE:bei trockenem Husten]. [CARD:ANTEIL?=Wähle einen Anteil] [EXEMPLAR:je Gabe] [CARD:MASS?=nach Maß] [EXEMPLAR:in kleiner Menge].`

Die erste `ANWENDEN? → ZIEL? → ANWENDEN?`-Folge wird nun als kurze äußere
Hautanwendung instanziiert; Wein, Honig und Husten stehen erst in den drei
unparsed Vorrats-/Rezeptfeldern. Damit werden sie nicht mehr scheinbar aus den
Aktionskarten gewonnen. Historisch bleibt der Artikel prekär: Eine
botanische Fachinstitution nennt erste Drosera-Illustrationen erst 1583.
[Botanische Staatssammlung München](https://bsm.snsb.de/botanical-detective-work-carnivorous-plant-from-hamburg-rediscovered-in-munich-herbarium-after-220-years/)

Venushaarfarn ist deshalb der stärkste Rival: Die eingerollte Achse und seine
alte pektorale Tradition tragen den Brusttrank besser, die runden
drüsenhaarigen Bildblätter dagegen schlechter. Die Behauptung einer sicheren
Drosera-Arznei um 1420 wird im Annahmenledger ausdrücklich `WITHDRAW_AS_EVIDENCE`.

## Referenten- und Reflow-Audit

- H1 und H2 setzen getrennte `OWNER`-/`ACTIVE`-Register; zwischen ihnen wird
  nichts getragen.
- H2s `VORIGES?` nimmt depth-one H2:I001 auf; die Doppelkarte in F005 bleibt
  ungelöst.
- H3:F007 führt H3:I002 als zurückbehaltenen Posten nur exemplarisch ein;
  F009 beginnt H3:I003.
- H4:F012 wechselt H4:I001 → H4:I002; F013 führt diesen zweiten Posten weiter.
- H5-S001 läuft als einziges Herbal-Statement über F014 und F015 hinweg. Die
  späteren Zellen führen H5:I002, I003 und schließlich den ausgewählten
  H5:I004, ohne daraus Pflanzenteile abzuleiten.

Damit bleibt „physische Zeile = Satz“ verworfen. Die kontinuierlichen Texte
folgen V61s Statementreflow, nicht den Zeilenenden.

## Gesamtrevision und Gegenmodell

Die Zweitausgabe verbessert V53 an vier Stellen:

1. kein H1→H2-Rückgriff mehr;
2. H3 benutzt Blüten/Blätter statt der awkward Wurzelprosa und erhält den
   enger belegten Veilchenöl-Gebrauch;
3. H4 trennt Filtration und Wundgebrauch prozesslogisch;
4. H5 trennt sichtbare Zielanwendung von völlig exemplarischem Hustenwein.

Der stärkste Gesamtrivale bleibt eine nichtmedizinische Pflanzenrohstoff- und
Werkstattkompilation. Sie kann Ernte, Fraktionen, Maße, Ansatz, Ziel und
Schlüsse ebenso tragen. Nur die historischen Artikelanalogien machen die
medizinische Ausgabe flüssiger; keine Pflanze, kein Medium und keine
Indikation ist durch eine Karte exklusiv gewonnen.

## Validierung

`V64_R2_VALIDATION.json` meldet `PASS`: 100/100 Ereignisse genau einmal,
20/20 Felder, 19/19 Statements, fünf Records mit 2/3/4/4/7 Feldern und
14/24/17/18/27 Ereignissen. V60↔V63 Tuple, Oberfläche, Formel, Schluss,
Formalprompt und Mnemonic stimmen exakt. Alle konkreten Segmente und alle
Feld-/Recordtexte sind vollständig geschichtet; 69 Annahmen werden separat
geführt. Kein neuer Kartenwert, keine neue Seite und keine Lautzuweisung wurde
eingeführt.
