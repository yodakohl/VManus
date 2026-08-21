# V16 R2 — vollständige medizinisch-praktische Default-Lesung

Status: **maximal-abduktive Werkstatttheorie, keine Entzifferung und kein
kanonisches GDT-Ergebnis**. Diese Fassung erfüllt absichtlich die Forderung,
dass keine sichtbare Gruppe ohne eine konkrete Default-Bedeutung bleibt.

## Ergebnis in einem Satz

Die zehn Seiten lesen sich am kohärentesten als ein dreiteiliges
iatromedizinisches Nachschlagewerk: vier Pflanzenartikel liefern Stoff und
Heilkraft, drei Bad-/Leitungsseiten liefern Zubereitung und Anwendung, und drei
Kreisseiten liefern astrologische Auswahlbedingungen für Zeitpunkt und
Körperregion.

```text
HERBAL WHAT   -> welche Pflanze, welcher Teil, welche Qualität und Tugend?
BIO HOW       -> welches Bad, welche Leitung, welche Wärme und Anwendung?
ASTRO WHEN    -> unter welchem Zeichen, Planeten oder Mondhaus anwenden/meiden?
```

Der Text ist dabei keine gewöhnliche Buchstabenschrift. Ein Schreiber lernt
Ganzkarten und feste Kurzformeln, lässt Bildargumente aus und schreibt offene
Herbalprosa beziehungsweise kurze abgeschlossene Bio-Zellen. Die englischen
Ausdrücke im Ledger sind Rücklese-Defaults dieses erfundenen Systems; sie sind
nicht als erkannte Lautwerte gemeint.

## Vollständigkeit

| Ebene | belegte Einheiten | Bedeutungsleer |
|---|---:|---:|
| GDT327-Prose-Ereignisse auf sieben Seiten | 381 | 0 |
| exakte GDT327-Kartentypen | 173 | 0 |
| ZL3b-Primärgruppen auf drei Kreisseiten | 395 | 0 |
| Astro-seitenlokale Oberflächentypen | 328 | 0 |
| gemeinsames Übersetzungsledger | 776 | 0 |

Die vollständige Zuordnung steht in
`V16_R2_COMPLETE_TRANSLATION_LEDGER.tsv`; das 501-zeilige Kartenbuch steht in
`V16_R2_COMPLETE_DEFAULT_LEXICON.tsv`. `V16_R2_FLUENT_TRANSLATIONS.md` gibt
jedes belegte Locus fortlaufend wieder. ZL3b ist die einzige Astro-Primärlesung;
IT2a und RF1b wurden nicht als zusätzliche Belege gezählt.

## Einfach lernbare Quellgrammatik

```text
HERBAL_ARTICLE := [PICTURED_SIMPLE]
                  NAME_OR_ALIAS?
                  QUALITY_OR_HABITAT*
                  PART_OR_PREPARATION+
                  VIRTUE_OR_APPLICATION+

BIO_RECORD     := [PICTURED_APPARATUS_OR_BODY]
                  TAKE_NEXT?
                  MEDIUM_OR_MEASURE?
                  (ACTION | RELATION | DURATION)*
                  COMMITTED_APPLICATION_OR_RESULT+

ASTRO_LOOKUP   := GOVERNOR_OR_SIGN
                  + DRAWN_STATION
                  + LOCAL_ELECTION_RULE
```

Ein physischer Zeilenbruch beendet keinen Satz. Herbal-Zeilen sind um die
vorher gezeichnete Pflanze herum umbrochene Artikelfragmente. Ein Bio-`DY`
schließt dagegen gewöhnlich die unmittelbar vorherige Anwendungszelle ab. Die
Astro-Geometrie trägt die Adresse; deshalb kann ein kurzes Radialwort bereits
eine vollständige Vorschrift wie „für warmes Bad günstig“ tragen.

## Konkretes Kernkartenbuch

| Karte/Konstruktion | Default-Rücklesung | Konfidenz |
|---|---|---:|
| `qokaiin` | NIMM DIE NÄCHSTE PORTION | .57 |
| L/O | MIT IHR; EBENSO UNTER DERSELBEN ÜBERSCHRIFT | .62 |
| AIIN | NACH DEM ANGEGEBENEN MASS ODER DER DAUER | .58 |
| Y | DIE GEGENWÄRTIGE PORTION | .56 |
| CTHY | WENN SIE ZUBEREITET IST | .42 |
| `Y–AIIN–Y` | BEIDE PORTIONEN NACH DEMSELBEN ANGEGEBENEN MASS | .46 |
| `VAL-Q` / `shedy`-Familie | VERWENDE DAS GEWÖHNLICHE LAUWARME BAD | .38 |
| `VAL-QE` / `qokeedy` | VERWENDE DAS TEMPERIERTE KRÄUTERBAD | .41 |
| `VAL-S` / `chedy` | HALTE ES ZUBEREITET UND BEREIT | .40 |
| `VAL-L` / `lchedy` | GIESSE ODER SPÜLE ES ÖRTLICH | .39 |
| `qoky` | TRAGE ES AUF DIE BETROFFENE STELLE AUF | .43 |
| `qokain` | GIB DIE ABGEMESSENE ZUTAT HINZU | .39 |
| `qokeey` | MISCHE ES GRÜNDLICH | .40 |
| `qokal` | MIT ERWÄRMTEM WASSER | .39 |
| CKHY | HALTE ES EINGETAUCHT | .37 |
| `qokedy` | ERWÄRME ES SANFT | .38 |
| `qokchdy` | ERHITZE ES SANFT | .38 |
| `olkeedy` | BADE BEIDE ZUSAMMEN | .36 |
| `shckhedy` | LASS ES ZIEHEN, BIS ES BEREIT IST | .38 |
| `otaiin` | FÜR DIE ANGEGEBENE ZEIT | .38 |
| `qotal` | BEI MÄSSIGER WÄRME | .37 |
| f56r-O56 | SEINE BLAUEN BLÜTENSPITZEN | .35 |

Die durch verschiedene Wrapper sichtbaren Formen bleiben dieselbe Karte. So
werden etwa `aiin/daiin/saiin/taiin/chaiin` nicht fünf Wörter, sondern fünf
Schreiblagen derselben Maß-/Referenzkarte. Die genaue Quellsprache bleibt offen.

### Korrektur einer bisherigen lokalen Bezeichnung

`4d455901…` wurde im kompakten Arbeitsstand noch als `H10_LOCAL_2` mit zwei
f10r-Vorkommen geführt. Der aktuelle, seitenbewacht gelesene GDT327-Ausschnitt
zeigt tatsächlich fünf Ereignisse auf f10r, f81v, f82r und f83r, sichtbar als
`char/dar/sar`. Die V16-R2-Lesung ersetzt daher den lokalen Pflanzenträger durch
das portable **DANN WEITER** (.35). Das ist eine formale Bestandskorrektur,
nicht bloß eine schönere Übersetzung.

## Fortlaufende Kernübersetzungen

### f10r, beide Artikelabschnitte

> **[Abgebildete skabiosenartige Pflanze.]** Wasche die wunde Stelle; bewahre
> den Rest trocken; fahre dann fort. Fein getrocknet, nimm einen kleinen Trank
> von der frischen Wurzel und trage ihn nach dem angegebenen Maß auf. Zerstoße
> die breiten unteren Blätter; verwende sie ebenso, wenn sie zubereitet sind.
>
> Bereite eine warme Waschung aus dem ausgepressten Saft; nimm die gegenwärtige
> Portion nach dem angegebenen Maß. Koche den Saft mit dem Saft derselben
> Pflanze und fahre fort. Der Artikel nennt nochmals Pflanze, Saft, Portion,
> Blätter und die örtliche Benennung.

Das zweite Stück ist bewusst nicht am Zeilenende abgebrochen: f10r.6, .8 und
.9 werden als fortlaufende Artikelpassage gelesen.

### f56r, vollständiger belegter Artikel

> **[Abgebildete borage-/buglossartige Pflanze.]** Die breiten unteren Blätter
> und die blauen Blütenspitzen werden nach dem angegebenen Maß verwendet. Koche
> die Spitzen, lege sie auf die betroffene Stelle und verwende auch den zarten
> Stängel. Die Anwendung erweicht harte Schwellungen. Die kühle Qualität gehört
> zu den Blütenspitzen. Zerstoße sie gut, mische sie mit Honig und öffne damit
> den verstopften Gang. Verwende zuletzt die getrocknete Wurzel nach der
> gewöhnlichen Regel und dem angegebenen Maß.

### f82r, vollständiger belegter Bio-Abschnitt

> **[Die gezeichneten Leitungen und Becken liefern die stillen Gegenstände.]**
> Siebe die Zubereitung ab; spüle damit; gib die abgemessene Zutat in die
> gegenwärtige Portion und verwende das temperierte Kräuterbad. Mische
> gründlich, halte das Glied eingetaucht und nimm die nächste Portion. Lass sie
> in der Leitung fließen, versiegle den Einlass, verwende erwärmtes Wasser und
> trage die Mischung auf. Halte sie für die angegebene Zeit im gewöhnlichen
> lauwarmen Bad. Wiederhole und setze die Anwendung fort.
>
> Gib die Zutat hinzu, mische bis zur sanften Wärme, spüle örtlich und nimm die
> nächste Portion. Der Abschlussdatensatz f82r.27 lautet in sieben Zellen:
> **Einlass schließen / nach dem Bad salben und einmal spülen / temperiertes
> Kräuterbad / eingetaucht halten / sanft warm halten / dasselbe Kräuterbad /
> eingetaucht halten.**

## Astro als medizinische Wahlhilfe

### f67r2

Default: eine medizinische Tierkreis-/Mondtafel. Die ersten zwölf lokalen
Beschriftungen werden provisorisch Aries bis Pisces gelesen. Die zwölf
Abschnitte sagen jeweils: Wenn der Mond im Zeichen steht, schütze die vom
Zeichen regierte Körperregion, vermeide dort Schneiden oder Aderlass und wähle
nur eine sanfte warme Anwendung. Die Siebenergruppe f67r2.64–70 ist Saturn,
Jupiter, Mars, Sonne, Venus, Merkur, Mond; f67r2.71 ist die gemeinsame Regel.
Die drei unteren Zeilen sind die Bedienanweisung. Diese Reihenbelegung ist der
Default der R2-Theorie, kein erkannter historischer Startwert.

### f68r1

Default: räumlicher Identifikationskatalog der Mondstationen. f68r1.5–7 gehört
zur Sonne; die 29 Sternbeschriftungen f68r1.8–36 werden ausschließlich durch
ihren sichtbaren räumlichen Locus identifiziert. Es wird ausdrücklich keine
zyklische Autorreihenfolge erfunden. f68r1.37 ist die Mondlegende: Mond,
Mondhaus, gegenwärtige Bedingung, anzuwendende Regel, Abschluss.

### f69v

Default: die praktische 28-Stellen-Folge. Der gezeichnete Radialplatz liefert
das Mondhaus; die Schrift liefert die Wahlregel. Beispiele:

| Locus | Default |
|---|---|
| f69v.4 | für ein warmes Bad günstig, besonders nach Sonnenuntergang |
| f69v.6 | Aderlass vermeiden |
| f69v.9 | ruhen und nicht purgieren |
| f69v.12 | heißes Bad vermeiden |
| f69v.14/.18/.27 | für Baden günstig |
| f69v.23 | eine zweite Anwendung vermeiden |
| f69v.28 | Kräutersud abseihen |
| f69v.31 | Mondhaus beachten; Behandlung bei Schwäche aussetzen |

Die Wiederholung `okeod` an drei Radien ist in dieser Lesung kein dreimaliger
Stationsname, sondern dieselbe Wahlaussage an drei verschiedenen gezeichneten
Stationen. Alle 28 Radien und alle Wörter der drei Außenbänder stehen einzeln im
Ledger und in der vollständigen Übersetzungsdatei.

## Ganze Seiten in je einem Satz

| Seite | Default-Paraphrase |
|---|---|
| f10r | Skabiosenartige Pflanze: Teile trocknen oder zerstoßen, Saft abkochen und nach üblichem Maß äußerlich oder als kleinen Trank gebrauchen. |
| f11r | Büschelige, kleinblütige Pflanze: Stängel, Blätter und Wurzel sammeln, im Schatten trocknen, auspressen und wiederholt anwenden. |
| f55v | Große breitblättrige Pflanze: abgemessene Pflanzenteile waschen, erwärmen, eintauchen und als zubereitete Waschung anwenden. |
| f56r | Borage-/buglossartige Pflanze: blaue Spitzen, Blätter, Stängel und Wurzel gegen Schwellung und verstopfte Gänge mit Wasser oder Honig bereiten. |
| f81v | Großes grünes Becken: Leitung füllen, Teile verbinden, warmes Bad halten, betroffene Stelle eintauchen, ablassen und örtlich spülen. |
| f82r | Mehrere verbundene Becken: temperierten Kräutersud mischen, durch Leitungen führen, Glied eintauchen, spülen, salben und Zellen abschließen. |
| f83r | Variantenblatt: Mengen, Wärme, Einlass, Bad, Eintauchen, Ausgießen und Wiederholung für verschiedene lokale Anwendungen einstellen. |
| f67r2 | Unter Planet, Tierkreiszeichen und Mondbedingung die regierte Körperregion schützen und invasive Behandlung vermeiden. |
| f68r1 | Unter Sonne und Mond die räumlich markierte Mondstation identifizieren und ihre Regel aufsuchen. |
| f69v | Für jedes der 28 Mondhäuser eine kurze Bade-, Ruhe-, Salb-, Spül- oder Meidevorschrift nachschlagen. |

## Historische Plausibilität

Diese konkrete Kombination ist keine moderne Datenbankphantasie. Die schon im
Projekt quellengebunden geprüften Vergleichshandschriften zeigen genau die
nötige Buchökologie:

- [British Library Add MS 29301](https://searcharchives.bl.uk/catalog/032-002020783),
  ca. 1420–30, vereinigt illustrierte Chirurgie, Rezepte, Arzneipflanzen,
  *Circa instans*, Regimen und Zodiac Man.
- [British Library Harley MS 1736](https://searcharchives.bl.uk/catalog/040-002047567),
  1446 mit Nachträgen, vereinigt Chirurgie, Wässer/Rezepte, sieben Planeten und
  medizinische Astrologie.
- [Wellcome MS.9280](https://wellcomecollection.org/works/b5k4wa4d), 1489,
  bewahrt die ältere Sammelpraxis aus Diätetik, Tierkreis, Mondprognostik,
  Rezepten und Herbaltexten.
- Die Warburg-Ausgabe der lateinischen
  [*Picatrix*-Tradition](https://resources.warburg.sas.ac.uk/pdf/fbh295b2205454.pdf)
  belegt ein reales technisches 28-Mondhaus-Inventar mit hausweisen
  Operationen. Das stützt die Quellklasse, nicht die konkrete Voynich-Lesung.

## Kosten und nächste Revision

Die Theorie erkauft Vollständigkeit mit 122 niedrig gestützten
Prose-Singletons und 328 seitenlokalen Astro-Oberflächentypen. Für diese gilt
ein explizites `CONTEXT_DEFAULT`: ihre Bedeutung stammt aus Seite, Bild und
Satzplatz, nicht aus externer Identifikation. Die stärksten falsifizierbaren
Punkte der Arbeitsfassung sind:

1. Wiederkehrende Bio-Karten müssen dieselbe Handlung auch in neuen
   Konstruktionen ertragen; besonders `qokeedy`, `shedy`, `chedy`, `lchedy`.
2. `Y–AIIN–Y` muss weiterhin eine zwei-Portionen/ein-Maß-Lesung zulassen.
3. f69v-Wiederholungen müssen eher wiederholte Wahlregeln als Stationsnamen
   sein.
4. Die f67r2-Zwölfersätze müssen mit Körperregionen und Meideregeln lesbar
   bleiben; scheitert das, fällt zuerst die medizinische Astro-Spezialisierung,
   nicht das ganze Kartenmodell.
5. Ein einfacheres vollständiges Lexikon mit weniger Polysemie ersetzt diese
   Fassung sofort. Bloße Ungewissheit entfernt dagegen keinen Default.

Die R2-Fassung hat damit eine vollständige, lehrbare und konkret rücklesbare
Arbeitsbedeutung für jede belegte Gruppe. Ihr Nutzen ist, die Konsequenzen einer
medizinischen Lesung sichtbar zu machen; ihre niedrigen Konfidenzen bleiben
Teil der Theorie, nicht semantische Leerstellen.
