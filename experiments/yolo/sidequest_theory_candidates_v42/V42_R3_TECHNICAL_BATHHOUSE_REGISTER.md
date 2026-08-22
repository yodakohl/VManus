# V42 R3 — Das Betriebsbuch eines Badehausmeisters

## Auftrag und Ergebnis

Dies ist die stärkste vollständige **nicht-diagnostische technische
Gegenlesung** der elf V41-Prosarecords. Sie behandelt die Karten nicht als
verschlüsselte Prosawörter, sondern als gelernte Arbeitskarten eines
spätmittelalterlichen Badehaus- und Wasserwerkbetriebs.

Der vollständige Durchlauf gelingt:

- 135/135 Felder besitzen eine konkrete technische Defaultfunktion;
- 381/381 Kartenereignisse besitzen eine deutsche Expansion;
- 11/11 Records besitzen einen vollständigen deutschen Werkstatttext;
- keine neue Seite und kein neues Voynich-Zeichen wurde benutzt;
- `f84` und `f84r` blieben versiegelt.

Das ist keine Entzifferung. Es ist ein adversarialer Beweis innerhalb des
Sidequests, dass die bisher erfundene Grammatik nicht zwingend medizinische
Diagnosen verlangt.

## Gewählter historische Zweck

Arbeitstitel des rekonstruierten Hefts:

> **Register der Kräuterwässer, Becken und Wasserläufe eines Badehauses**

Die drei Teile des kleinen Systems wären:

1. **Pflanzenblätter:** Bildadressen für Badezusätze, Kräuterbeutel,
   Duft-/Waschwässer und haltbare Voransätze;
2. **Figuren-/Beckenblätter:** Betriebsfolgen für Badende, Becken, Zuläufe,
   Filter, Rückläufe, Temperatur und Reinigung;
3. **Kreisblätter:** möglicher Kalender für Betrieb, Beschaffung oder
   zulässige Badetermine; dieser dritte Anschluss bleibt schwach, da er in den
   elf GDT327-Prosarecords nicht direkt geprüft werden kann.

Der Zweck passt prinzipiell in die Zeit um 1420. Öffentliche Badstuben waren im
spätmittelalterlichen städtischen Leben verbreitet; die Tätigkeit umfasste
Erhitzen, Dampf, Spülung und weitere Dienstleistungen. Bjerregaards Überblick
beschreibt Schwitzbäder, kalte Schluss-Spülungen und spezialisiertes Personal
([Kuml 57](https://doi.org/10.7146/kuml.v57i57.24661)). Eine Rekonstruktion
spätmittelalterlicher deutscher Praxis sammelt Quellenbelege für erwärmtes
Wasser, Kräuter im Bad, Öl, Gefäße, Abkühlung und die Arbeit von Badeknechten
und -mägden
([Wienische Hantwërcliute](https://wh1350.at/en/hygiene-and-cosmetics/a-late-14th-century-german-bathhouse/)).
Das macht die einzelnen Tätigkeiten historisch möglich; es beweist nicht, dass
das Voynich-Manuskript ein solches Register ist.

## Technische Grammatik

Die V41-Grammatik bleibt unverändert. Nur ihre fachliche Ausfüllung wechselt:

```text
PICTURED_OWNER
  = Pflanze, Badender, Becken oder markierte Arbeitsstation

FIELD
  = Rohstoff/Teil
  + Maß/Voransatz
  + Wärme/Ruhe/Filterung
  + Wasserweg/Zielstation
  + inhaltstragender Zellschluss

HERBAL_RECORD
  = Vorrats- oder Badezusatzartikel mit offenen Klauseln

BIO_RECORD
  = Kette kurzer Bedien- und Reinigungszellen
```

Die zwölf gemeinsamen Karten lesen sich in diesem Modell besonders natürlich:

| Karte | technische Defaultlesung |
|---|---|
| `daiin` | vorgeschriebenes Maß |
| `chol` | mit dem vorigen Ansatz weiterarbeiten |
| `dy` | dieser aktive Arbeitsposten |
| `dal` | zur bezeichneten Station führen |
| `oky` | aktive Portion im laufenden Arbeitsgang verwenden |
| `chor` | bereitete Arbeitsflüssigkeit |
| `cthy` | Ansatz ist arbeitsbereit |
| `char` | daraus, aus demselben Ansatz |
| `shey` | bis die Flüssigkeit klar abläuft |
| `cholor` | aus dem vorigen Ansatz entnehmen |
| `chty` | Ansatz gleichmäßig bearbeiten |
| `otchey` | bezeichneten Anteil nehmen |

Diese Lesungen verlangen weder Körperteil noch Krankheit. Sie funktionieren
als gemeinsames Deck für Pflanzenvorrat und Beckenbetrieb.

## Vollständige elf-Record-Edition

### f10r, Record 1 — Rotwurzel-Badansatz

> Nimm die faserige untere Wurzel, wasche sie in fließendem Wasser, zerstoße
> sie grob und setze sie mit Rotwein an. Prüfe eine kleine Probe auf Stärke und
> Verträglichkeit; verwende die vorgeschriebene Portion frisch und warm im
> Badelauf und bewahre die übrige Wurzel trocken für den nächsten Ansatz.

### f10r, Record 2 — Wiesenkraut-Saft und Vorrat

> Verarbeite das auf feuchtem Wiesengrund gewachsene Kraut, sobald der Ansatz
> bereit ist: gib den ausgepressten Saft in die Arbeitsflüssigkeit, siede sanft
> und teile gemessene Posten ab. Sammle vor der Blüte eine Handvoll für den
> Voransatz; nach dem Öffnen der Blüte arbeite bis zur bitteren Prüfqualität
> weiter und bewahre einen Anteil unter Öl.

### f11r — Frühjahrswurzel und Kräuterbeutel

> Sammle die Wurzel im Frühjahr im schattigen Wald vor dem Öffnen der
> Blütenkrone. Presse sie durch Tuch, seihe zweimal und lasse die Flüssigkeit
> offen abkühlen; behalte die Blütenkrone zurück. Fülle den abgebildeten Zusatz
> in einen Kräuterbeutel, binde ihn über den bezeichneten Einlass und lege ihn
> arbeitsbereit warm an.

### f55v — Breitblatt-Weinextrakt

> Siede die vorgeschriebene Menge des breiten Blatts in Weißwein und lasse sie
> bis zur Klarheit ausziehen. Rühre einen zweiten gemessenen Posten gleichmäßig
> und spüle damit die zu reinigende Stelle. Bereite für den zweiten Gebrauch
> einen weiteren warmen Weißweinansatz; vereinige beide Teile, bewahre sie
> bedeckt und verwende die fertige Flüssigkeit frisch.

### f56r — Siebenteiliger Badezusatz-Vorrat

> Sammle die Pflanze im Frühjahr. Nimm die dünne untere Wurzel in
> vorgeschriebenem Maß, lasse sie vor der Blüte in Weißwein ausziehen und führe
> die Portion zur bezeichneten Badestation. Trockne den Kräuterpack, den Samen-
> oder Knospenkopf und das schmale Blatt im Schatten. Prüfe den frischen Ansatz,
> bewahre den Rest trocken, mische einen weiteren Teil mit Honig als Bindemittel
> und bemesse zuletzt die blasse offene Blüte.

### f81v — Erster Wasserlauf und Rücklauf

> Spüle zuerst die bezeichnete Arbeitsstelle. Setze aus Rücklauf und Voransatz
> gemessene Portionen im unteren Becken an, gib bereitetes Öl zu und führe sie
> durch die verbundenen Wasserläufe. Spüle Gefäße und Leitungen, halte den
> Ansatz warm, rühre, lasse ihn stehen und stelle ihn bedeckt zurück. Fülle
> nach, erhitze einmal, kühle, wiederhole die Spülung und leite die geklärte
> Flüssigkeit über die erste Öffnung zur bezeichneten Station.

### f82r — Vollständiger Bade- und Spülzyklus

> Spüle Gefäß und Wasserlauf, stelle die Mischung bedeckt zurück und gib eine
> gemessene Portion zu. Bade im temperierten Wasser; wechsle danach über zweite
> Öffnung, Tuch und verbundenen Lauf zum nächsten Becken. Ziehe über das breite
> Gefäß ab, gib Öl und klares Wasser zu, halte den Ansatz warm und lasse ihn
> ruhen. Führe weitere Portionen ein, tauche vollständig, lasse unten ab und
> schalte anschließend die Öffnungen für Spülung, Warmwasser, Bad, Prüfportion
> und festgebundenen Kräuterbeutel der Reihe nach.

### f83r, Record 1 — Langer Becken-, Klär- und Ablasslauf

> Lasse die Flüssigkeit absetzen, führe sie zum unteren Auslass und tauche die
> gemessene Portion vollständig ein; lasse den verbrauchten Anteil in das
> Auffanggefäß ab. Beginne mit Warmwasser und Voransatz neu, spüle, mische,
> temperiere, kühle, siede und kläre in den bezeichneten Gefäßen. Öffne und
> schließe obere und untere Läufe, führe die Arbeitsflüssigkeit zu den markierten
> Stationen, behalte den Rückstand und wiederhole Bad, Spülung, Filterung und
> Ablass bis zum klaren Endlauf.

### f83r, Record 2 — Zweiter Becken- und Filterlauf

> Bade im temperierten Wasser, fülle das Gefäß und spüle die Arbeitsstelle.
> Rühre zum unteren Auslass, nimm den bezeichneten Anteil, halte ihn lauwarm und
> binde den Kräuterbeutel an der Station fest. Seihe den Ansatz zweimal durch
> Tuch, benutze die vorgeschriebene warme Menge an der ersten Öffnung, siede
> sanft und spüle das breite Gefäß zweimal. Lasse unten ab, führe einen neuen
> Posten sofort ein, öffne den oberen Lauf und fülle Warmwasser nach.

### f83r, Record 3 — Kurzer Wiederholungslauf

> Ziehe die Flüssigkeit ab, erhitze sie einmal und halte einen Arbeitszeitraum
> ein. Führe sie dann mit der vorigen Mischung in vorgeschriebenem Maß zur
> bezeichneten Station und rühre am zweiten Wasserlauf gleichmäßig weiter.

### f83r, Record 4 — Ungesottener Direktlauf

> Setze den Badenden ohne Sieden an das Becken und führe den Voransatz über die
> erste Öffnung. Nimm die vorgeschriebene aktive Portion, leite sie durch Tuch
> und bringe sie an der bezeichneten Arbeitsstation ein.

Die vollständige kartengenaue Rechnung aller 135 Felder steht in
`V42_R3_135_FIELD_BATHHOUSE_EDITION.tsv`; die kompakte Recordedition in
`V42_R3_ELEVEN_RECORD_BATHHOUSE_EDITION.tsv`.

## Wo diese Lesung besser ist als das medizinische Modell

1. **Die Biological-Wiederholung braucht keine 115 einzelnen Therapiesätze.**
   Wiederkehrende Zellen für Füllen, Temperieren, Spülen, Seihen, Öffnen und
   Ablassen sind im täglichen Anlagenbetrieb erwartbar.
2. **Die gemeinsamen Karten bleiben wirklich allgemein.** `dy`, `chol`,
   `chor`, `dal` und `cthy` müssen keine Körperteile, Leiden oder Arzneien
   benennen.
3. **Die Figuren können echte Badende sein.** Man muss sie weder zu allegorischen
   Organen noch die Röhren zu Anatomie erklären.
4. **Kräuter, Öl, warmes und kaltes Wasser, Tücher und Rückstände gehören in
   einen Badestubenbetrieb.** Die Kombination ist nicht exklusiv medizinisch.
5. **Mehrere Schreiber lernen das System leicht:** gemeinsames
   Bedienkarten-Deck, lokale Rohstoffkarten und kurze Zellschlüsse.

## Wo sie verliert

1. **Ein überliefertes Badehaus-Betriebsbuch dieser exakten Form ist nicht
   belegt.** Die historische Praxis ist plausibel, die konkrete Buchgattung
   erfunden.
2. **Rot- und Weißwein, Honig sowie präzise Pflanzenteile** passen ebenso gut
   oder besser in Arzneirezepturen. Einige technische Umdeutungen — besonders
   die Geschmacksprobe und der festgebundene Kräuterbeutel — wurden allein zur
   Herstellung der Gegenlesung gewählt.
3. **Die Herbal-Bilder sind zu ausgearbeitet**, wenn sie nur fünf lokale
   Badezusätze eines Betriebs adressieren; ein allgemeines Herbarium oder
   Arzneibuch erklärt ihren Umfang leichter.
4. **Der Astro-Anschluss ist schwächer.** Ein Badekalender ist möglich, doch das
   medizinische WHAT/HOW/WHEN-Modell besitzt dafür die gewöhnlichere
   iatromathematische Brücke.
5. **Die Feldbedeutungen stammen weiterhin aus V25/V40.** Diese Edition zeigt
   semantische Elastizität, keine unabhängige Bestätigung.

## Ehrliches Urteil

```text
interne Formular-/Anlagengrammatik:  Badehausmodell leicht besser
Pflanzen- und Stoffinhalt:            medizinisches Modell besser
Figuren/Becken/Wasserläufe:           Badehausmodell mindestens gleich gut
Astro-Integration:                    medizinisches Modell besser
Gesamt auf den zehn Seiten:           medizinisches Modell knapper vorn
```

Das R3-Modell **ersetzt** die medizinische Arbeitstheorie daher nicht. Es wird
aber zum stärksten nichtmedizinischen Rivalen erhoben:

> **Ein erheblicher Teil dessen, was bisher als Therapie gelesen wurde, könnte
> bloß Bedienung, Reinigung, Temperaturführung und Rohstoffverwaltung eines
> Badebetriebs sein.**

Der wichtigste Gewinn ist negativ und konkret: Aus den 135 Feldern allein
folgt kein Beschwerdelexikon. Krankheit darf künftig nur dort in der
medizinischen Lesung stehen bleiben, wo Bild, Recordzusammenhang oder eine
stärkere Kartenopposition sie verlangt; die allgemeine Verfahrensgrammatik
trägt sie nicht.
