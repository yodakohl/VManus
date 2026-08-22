# V53 R2 — historischer Drucktest einer vollständigen Herbal-Ausgabe

**Rolle:** handschriftenkundiger Arzt- und Herbal-Schreiber, Arbeitshorizont
um 1420.
**Status:** kreative historische Rekonstruktion, **keine** Entzifferung und
keine Behauptung von Wortbedeutungen.
**Umfang:** die fünf vorgegebenen Artikel auf vier Folien: f10r, Record 1 und
Record 2; f11r; f55v; f56r. Zusammen sind dies 20 Felder und sämtliche 100
V49-Ereignisse dieser Artikel.

## Ergebnis in einem Satz

Die historisch tragfähigste Ausgabe liest f10r als zwei Rezepte zu
Skabiose/Teufelsabbiss (Wurzelwasser und Blütenkrautöl), f11r als
Veilchenwein mit äußerlichem Veilchenöl, f55v als Allium-/Bärlauchwein für
eine äußerliche Arznei und f56r als hochriskanten Sonnentau-Brusttrank. Nur
der erste f10r-Artikel besitzt eine fast zeitgleiche, pflanzenspezifische
deutsche Quellenanalogie; alle anderen Texte sind zunehmend freie
Artikelrekonstruktionen.

## Editionsregel: vier Schichten, die nicht vermischt werden dürfen

1. **Formale Schicht:** Die Kartenfolge und jeder vorhandene Formelbaum
   bleiben unverändert. `CLOSE` und `CLOSE_B3` sind ausschließlich formale
   Feldschlüsse.
2. **Ausgewählte Merkwörter:** Nur V50/V51 darf erscheinen:
   `SETZEN`, `MARKIEREN`, `VERKNÜPFEN`, `AN?`, `BEREITUNG?`, `TEIL?`,
   `MASS?`, `KLAR?`, `VERWENDEN?`, `BEREIT?`, `ZUVOR?`. Das V50-`E` bleibt
   `UNBEKANNT`. Fragezeichen sind Teil des epistemischen Status.
3. **Bildschicht:** Der Pflanzenbesitzer ist eine stumme Seitenannahme. Kein
   Voynich-String wird zum Pflanzennamen.
4. **Historisch-kreative Schicht:** Pflanzenteil, Wasser oder Wein,
   Zubereitung, Gefäß und Gebrauch werden erst für das ganze Feld bzw. den
   ganzen Artikel ergänzt. Die Ergänzung ist keine rückwirkende Kartenglosse.

Insbesondere erbt ein eingebettetes `<ARG_AIIN>` niemals das Merkwort der
exakten Ganzkarte `AIIN=MASS?`. Ebenso wird `CHEY` nicht als Teilstring in
einer sonst unbekannten Karte gelesen. Ein physischer Zeilenumbruch ist kein
Satzende. Der einzige feste Feldbau bleibt `FIELD := NONCLOSE* TERMINAL?`.

### Protokollabweichung bei der Bildzuordnung

Bei der anfänglichen Zuordnung von PDF-Seiten zu Folien wurden versehentlich
nur Bild-Thumbnails von f54v, f55r, f56v und f57r geöffnet. Es wurden daraus
keine Text- oder Tabellendaten erhoben, keine Pflanzen- oder Strukturaussage
übernommen und keine der Eindrücke in diese Ausgabe einbezogen. Die
Bildargumente dieses Berichts stammen ausschließlich aus f10r, f11r, f55v und
f56r. Der Scope-Fehler ist damit offengelegt, nicht nachträglich als erlaubte
Evidenz behandelt.

### Vollständigkeitskontrolle

| Artikel | Felder | Ereignisse | Schlussfelder |
|---|---:|---:|---:|
| f10r-R1 | 2 | 14 | 0 |
| f10r-R2 | 3 | 24 | 0 |
| f11r | 4 | 17 | 1 |
| f55v | 4 | 18 | 3 |
| f56r | 7 | 27 | 1 |
| **Summe** | **20** | **100** | **5** |

`U[...]` bedeutet im Folgenden ausdrücklich **unbekannt**. Die rechte
Spalte der Feldtabellen ist jeweils eine unsegmentierte Ganzfeld-Expansion;
sie darf nicht Wort für Wort an die links stehenden Karten angelegt werden.
`FRAME_OT(X)` bewahrt die Formelbaum-Schreibweise und realisiert darin den
ausgewählten formalen Operator `OT=MARKIEREN`; `FRAME_O(X)` bleibt ein
unübersetzter äußerer Rahmen.

## Bildbefund und Besitzerentscheidungen

Die Bildgrundlage ist das offizielle digitale Faksimile von [Yale,
Beinecke MS 408](https://beinecke.library.yale.edu/beinecke/collections/beinecke-cipher-voynich-manuscript).

| Folio | Sichtbarer Befund | Arbeitsbesitzer | stärkste Bildgegenrede |
|---|---|---|---|
| f10r | Ein großer blauer, köpfchenartiger Blütenstand mit hellem Zentrum und Strahlenhaaren; gegenständige, breit gezähnte Blätter; langer waagerechter Wurzelstock mit zwei roten Verdickungen. | **Skabiose/Teufelsabbiss** (*Succisa/Scabiosa*-Umkreis), nur familiennah. | Der wirkliche Teufelsabbiss besitzt den namensgebend stumpf „abgebissenen“ Wurzelstock, nicht zwei rote endständige Knollen; Blattbänder und Blütenkopf sind stark synthetisch. |
| f11r | Dichtes Polster aus kleinen gekerbten Blättern und vielen blauen Blüten; mehrere helle Stiele gehen in drei überlange, stachelige Wurzelkörper über. | **Veilchen**, als ikonographische Gesamtidee. | Die dreifache baumartige Achse und die langen gezähnten Wurzeln sind für *Viola* unvereinbar; eine Dolden-/Wurzelpflanze bleibt Rivalin. |
| f55v | Ein mächtiger Schopf aus breiten, einfachen Blättern; zentraler Schaft mit vielstrahligem, doldigem Kopf; unten eine phantastische tierähnliche Wurzel. | **Allium/Bärlauch**, ohne sichere Artbestimmung. | Es fehlt eine eindeutige Zwiebel; Blattbreite und Wundgebrauch passen ebenso zu Wegerich, dessen Blütenstand jedoch nicht doldig wäre. |
| f56r | Zwei dunkle rundliche Blätter mit langen radialen Haaren; eine eingerollte Achse mit tropfenförmigen Anhängen; weiße/blaue Blüten. | **Sonnentau** (*Drosera*), stärkster reine Bildtreffer. | Reale *Drosera* ist eine kleine bodennahe Rosette mit schlankem Blütenschaft, nicht eine große zweiblättrige Spiralpflanze; das Bild kann eine synthetische oder ganz andere „klebrige“ Arzneipflanze sein. |

## Historische Kalibrierung

Die wichtigste Nahquelle ist Frankfurt, UB, **Ms. germ. qu. 17, Buch von der
Gesundheit**, Elsaß, erstes Viertel des 15. Jahrhunderts; die Bibliothek
datiert und beschreibt den Codex offiziell und stellt ihn gemeinfrei bereit
([Metadaten](https://sammlungen.ub.uni-frankfurt.de/msma/content/titleinfo/3654949)).
Auf fol. 340v steht im Register der gebrannten Wasser ein Eintrag zu
`Abis wasser`: getrunken gegen Geschwür um das Herz, Herzleiden, verletzte
Därme und geronnenes Blut; derselbe Folio erklärt die unten „abgebissene“
Wurzel ([Digitalisat 340v](https://sammlungen.ub.uni-frankfurt.de/i3f/v20/3655638/full/full/0/default.jpg)).
Fol. 342v nennt `Dufelbis wasser` zum Trinken gegen Geschwür und Stechen
([Digitalisat 342v](https://sammlungen.ub.uni-frankfurt.de/i3f/v20/3655642/full/full/0/default.jpg)).
Das ist keine Übersetzung von f10r, wohl aber eine außerordentlich nahe
Gebrauchs- und Gattungsanalogie.

Für Veilchen bietet Hildegards *Physica* I.103 zwei klare ältere
Verfahrensmuster: Veilchen in heißem Öl, anschließend im Glas verwahrt und
äußerlich gebraucht; sowie Veilchen in reinem Wein gekocht, durch ein Tuch
geseiht und getrunken ([lateinischer Text und Apparat](https://www.monumenta.ch/latein/text.php?domain=&hide_apparatus=&inframe=1&lang=1&level=4&links=&rumpfid=Hildegardis+Abbatissa%2C+Physica%2C+1%2C++103&tabelle=Hildegardis_Abbatissa)).
Eine südwestdeutsche Veilchenabbildung aus der Konrad-von-Megenberg-/Hartlieb-
Überlieferung um 1460 zeigt ebenfalls ein niedriges, blau blühendes Kraut
([LEO-BW/Universitätsbibliothek Heidelberg](https://www.leo-bw.de/en-GB/detail/-/Detail/details/DOKUMENT/ubh_grafik/605e28b3-a3ce-4be3-ac4b-f3266c16adf3/Kr%C3%A4uterpflanze%20Viola%20Viola%20odorata%20-%20Violaceae%20-%20Veilchen%3B%20aus%20Konrads%20von%20Megenberg%20%22Buch%20der%20Natur%22%20Kr%C3%A4uterbuch)).

Für Allium ist Balds angelsächsische Augensalbe wesentlich älter und
regional fern, aber verfahrensgeschichtlich präzise: zwei Allium-Arten werden
zerstoßen, mit Wein und Ochsengalle gemischt, neun Nächte in einem
Messing-/Bronzegefäß stehen gelassen, durch Tuch gewrungen, geklärt und
äußerlich angewandt. Eine peer-reviewte Rekonstruktion gibt Handschrift,
Text und Übersetzung wieder ([Harrison et al., *mBio* 2015,
doi:10.1128/mBio.01129-15](https://journals.asm.org/doi/10.1128/mbio.01129-15)).
Als pflanzen- und verfahrensbezogener Rivale ist Wegerich wichtig:
*Physica* I.101 lässt Wegerichsaft durch Tuch seihen und mit Wein oder Honig
mischen; warme, in Wasser gekochte Blätter werden örtlich aufgelegt
([Text](https://monumenta.ch/latein/text.php?nf=1&rumpfid=Hildegardis+Abbatissa%2C+Physica%2C+1%2C++101&tabelle=Hildegardis_Abbatissa)).

Beim Sonnentau ist die Lage widersprüchlich. Eine museale Beschreibung eines
aus dem späten 15. Jahrhundert stammenden französischen *Liber de simplici
medicina* identifiziert
zwei dort abgebildete Pflanzen als *Drosera intermedia* und
*D. rotundifolia* ([Tsinghua University Science Museum](https://tsm.tsinghua.edu.cn/?p=7287)).
Das stützt eine spätmittelalterliche Bildtradition, nicht aber den hier
erdichteten Wein-Honig-Trank. Zudem setzt eine aktuelle pharmaziehistorische
Darstellung die ersten sicheren schriftlichen Nennungen erst 1568 an
([Thieme, Pflanzenmonographie](https://natuerlich.thieme.de/therapieverfahren/phytotherapie/detail/drosera-rotundifolia-l-der-rundblaettrige-sonnentau-4654)).
Die oft wiederholte Zuweisung einer `herba sole` gegen Husten an Platearius
bleibt ohne überprüften Editionslocus zu unsicher, um eine Verwendung um 1420
zu beweisen.

---

## Artikel 1 — f10r, Record 1: Abiss-Wurzelwasser

**Entscheidung:** Skabiose/Teufelsabbiss; innerlich gebrauchtes gebranntes
Wasser aus dem unteren Pflanzenteil. Historische Konfidenz **mittel**, weil
die Nahquelle stark, die botanische Zeichnung aber widersprüchlich ist.

### Strikte Ankerfolge

| Feld | sichtbare Karten in Reihenfolge | ausgewählte Anker in derselben Reihenfolge | kreative Ganzfeld-Expansion |
|---|---|---|---|
| f10r.2/1 | `dchey cthoor char chty os chair otytchol oky daiin etyd` | `TEIL? → U[CTHOOR] → U[AR] → U[TY] → U[OS] → U[AIR] → U[OTYTCHOL] → VERWENDEN? → MASS? → U[ETYD]` | ⟦Vom unteren Pflanzenteil wird Material gesäubert, klein geschnitten und mit Wasser in den Brennhafen gegeben; das aufgefangene Wasser wird in kleinem Maß gebraucht und verschlossen verwahrt.⟧ |
| f10r.5/1 | `qokchy qotchol chol cthy` | `U[OKCHY] → FRAME_OT(U[CHOL]) → FRAME_O(VERKNÜPFEN) → BEREIT?` | ⟦Für den frischen Gebrauch wird die Ausbeute mit dem ersten klaren Lauf verbunden und nur gelinde erwärmt; die Arznei gilt dann als bereit.⟧ |

### Flüssige Ausgabe

> **Von Abiss, dem Teufelsabbiss.** Nimm von dem unteren, wie abgebissen
> erscheinenden Wurzelstock einen Teil, säubere und zerschneide ihn und gib ihn
> mit gutem Wasser in den Brennhafen. Fange das gebrannte Wasser in einem
> sauberen Glas auf. Verwende davon ein kleines Maß gegen Geschwür oder
> stechenden Schmerz im Leib und verwahre das Gefäß wohl verschlossen. Soll
> die Arznei frisch gereicht werden, so verbinde den guten Lauf mit dem zuerst
> gewonnenen Wasser und erwärme ihn nur gelinde; dann ist sie bereit.

### Quellenanalogie, Revision, Widerspruch

- **Quellenanalogie:** Frankfurt Ms. germ. qu. 17, fol. 340v und 342v, ist
  nahezu zeitgleich, nennt Abiss/Teufelsbiss ausdrücklich als gebranntes
  Wasser und nennt inneres Geschwür und Stechen als Gebrauch. Der
  Brennhafen, das verschlossene Glas und die konkrete Indikation stammen aus
  dieser historischen Artikelschicht, nicht aus einzelnen Karten.
- **Revision gegen V49:** `laufendes Wasser`, `gleichmäßig stampfen`, `roter
  Wein`, `Magenweh` und `Rest trocken lagern` werden als Kartenglossen
  gestrichen. Die Nahquelle rechtfertigt stattdessen versuchsweise ein
  gebranntes Wasser und inneres Geschwür/Stechen auf Artikelebene.
- **Stärkster Widerspruch:** f10r zeigt zwei rote endständige Verdickungen;
  gerade die historische Signatur des Teufelsabbisses wäre dagegen ein unten
  abgestorbener bzw. „abgebissener“ kurzer Wurzelstock. Auch `TEIL?`,
  `VERWENDEN?`, `MASS?`, `VERKNÜPFEN` und `BEREIT?` kodieren weder Pflanze
  noch Destillation oder Krankheit.

---

## Artikel 2 — f10r, Record 2: Abiss-Blütenkrautöl

**Entscheidung:** zweite Zubereitung derselben Bildpflanze; Saft aus
blühenden Spitzen, mit einer vorigen Zubereitung und Öl zu einer äußerlichen
Arznei verbunden. Konfidenz **niedrig bis mittel**: die Feldfolge bietet
`BEREIT?`, mehrfach `BEREITUNG?`, `ZUVOR?`, Verknüpfungen und `MASS?`, aber
keinen Stoff und keinen Gebrauch.

### Strikte Ankerfolge

| Feld | sichtbare Karten in Reihenfolge | ausgewählte Anker in derselben Reihenfolge | kreative Ganzfeld-Expansion |
|---|---|---|---|
| f10r.6/1 | `ycheor cthy chor cthaiin qoctholy dy chy taiin shy` | `U[YCHEOR] → BEREIT? → BEREITUNG? → U[CTH]+<ARG_AIIN> → U[OCTHOLY] → U[Y] → U[Y] → MASS? → U[Y]` | ⟦Wenn das Kraut zur beginnenden Blüte bereit ist, wird aus Blütenköpfen und jungen Blättern eine Bereitung gemacht; ihr ausgepresster Saft wird portionsweise aufgefangen.⟧ |
| f10r.8/1 | `qotchor chor otol chol cholor chol daiin dar` | `FRAME_OT(U[CHOR]) → BEREITUNG? → FRAME_OT(U[OL]) → FRAME_O(VERKNÜPFEN) → ZUVOR? → FRAME_O(VERKNÜPFEN) → MASS? → U[AR]` | ⟦Vor voller Blüte wird diese Bereitung mit der zuvor gewonnenen Wurzelarznei verbunden, von beiden je ein Maß, und bei kleinem Feuer eingedickt.⟧ |
| f10r.9/1 | `oykchor shor chor chy kaiiin dy chodaiin` | `U[OYKCHOR] → BEREITUNG? → BEREITUNG? → U[Y] → U[KAIIIN] → U[Y] → FRAME_O(U[D]+<ARG_AIIN>)` | ⟦Die beiden Flüssigkeiten werden mit gutem Öl zu einer weichen Salbe bereitet und im glasierten Gefäß bewahrt; sie wird nur äußerlich auf ein Geschwür gelegt.⟧ |

### Flüssige Ausgabe

> **Die andere Arznei von demselben Kraut.** Wenn die blauen Köpfe eben
> aufgehen und das Kraut bereit ist, nimm die oberen Blüten und jungen
> Blätter, zerstoße sie und presse den Saft aus. Vor der vollen Blüte verbinde
> ein Maß davon mit einem Maß des zuvor gewonnenen Wurzelwassers. Gib gutes
> Öl hinzu und erwärme alles bei kleinem Feuer, bis eine weiche Arznei wird.
> Bewahre sie in einem glasierten Gefäß und lege sie äußerlich auf ein
> Geschwür oder eine harte Schwellung.

### Quellenanalogie, Revision, Widerspruch

- **Quellenanalogie:** Der Abiss-Eintrag der Frankfurter Handschrift trägt die
  Pflanzen- und Geschwürassoziation. Die Verbindung von Pflanzensaft und Öl
  zu einer äußerlichen Arznei ist im mittelalterlichen Materia-medica-Repertoire
  gewöhnlich; Hildegards Veilchenkapitel bietet ein konkretes, aber
  pflanzenfremdes Ölverfahren.
- **Revision gegen V49:** Feuchtwiese, Presssaft, Sammeln vor der Blüte,
  gleiche Teile und Öl werden nicht mehr auf Einzelkarten verteilt. Nur die
  grobe Folge `BEREIT → BEREITUNG → ... → ZUVOR → ... → MASS` wird als
  Merkhilfe behalten; der ganze Salbenartikel ist freie Expansion.
- **Stärkster Widerspruch:** Für ein Abiss-Öl um 1420 liegt hier keine ebenso
  nahe pflanzenspezifische Quelle wie für das Wasser vor. Keines der drei
  Felder besitzt einen formalen Schluss; selbst die Artikelgrenze ist daher
  nicht durch `CLOSE` gestützt.

---

## Artikel 3 — f11r: Veilchenwein und Veilchenöl

**Entscheidung:** Veilchenkraut; zuerst klar geseihter Wein für innerlichen
Gebrauch, dann ein Öl aus zurückbehaltenen Blüten für äußerlichen Gebrauch.
Konfidenz **mittel**, vor allem wegen der ungewöhnlich genauen
Verfahrensparallele in *Physica* I.103.

### Strikte Ankerfolge

| Feld | sichtbare Karten in Reihenfolge | ausgewählte Anker in derselben Reihenfolge | kreative Ganzfeld-Expansion |
|---|---|---|---|
| f11r.1/1 | `tshol schoal cfhy shfydaiin cphy shey tchody` | `U[SHOL] → U[CHO]+<ARG_AL> → U[CFHY] → U[FYD]+<ARG_AIIN> → U[CPHY] → KLAR? → CLOSE(U[CHO])` | ⟦Im ersten Frühjahr werden Blüten und junge Blätter in reinem Wein gekocht, durch ein Tuch geseiht, klar werden gelassen und abgekühlt.⟧ |
| f11r.1/2 | `shoyty` | `U[SHOYTY]` | ⟦Ein Teil der frischen Blüten wird für die zweite Arznei zurückbehalten.⟧ |
| f11r.4/1 | `dchol chy kchy dy daiin` | `U[DCHOL] → U[Y] → U[KCHY] → U[Y] → MASS?` | ⟦Vom klaren Veilchenwein wird nur ein kleines Maß als Trank gereicht.⟧ |
| f11r.7/1 | `qotchy okchol cthy dy` | `FRAME_OT(U[CHY]) → U[OKCHOL] → BEREIT? → U[Y]` | ⟦Die zurückbehaltenen Blüten werden in gutem Öl gelinde erwärmt; die fertige Arznei wird in einem Tuch äußerlich aufgelegt.⟧ |

### Flüssige Ausgabe

> **Vom Veilchen.** Wenn im ersten Frühjahr die blauen Blüten aufgehen, nimm
> Blüten und junge Blätter und koche sie gelinde in reinem Wein. Wring sie
> durch ein feines Tuch, lasse den Wein klar werden und dann erkalten. Behalte
> einige frische Blüten zurück. Von dem klaren Wein gib
> ein kleines Maß bei schwerem Gemüt und beschwerter Brust. Die
> zurückbehaltenen Blüten erwärme in gutem Öl; wenn die Arznei bereit ist,
> lege sie in einem Tuch auf ein äußeres Geschwür.

### Quellenanalogie, Revision, Widerspruch

- **Quellenanalogie:** *Physica* I.103 nennt sowohl Veilchen in reinem Wein,
  durch Tuch geseiht und bei Melancholie/Lungenbeschwerden getrunken, als
  auch Veilchen in heißem Öl, im Glas verwahrt und äußerlich gebraucht. Die
  V53-Ausgabe verbindet diese zwei belegten Rezeptfamilien zu einem Artikel;
  genau diese Verbindung selbst ist nicht belegt.
- **Revision gegen V49/V31:** Die V19-Wildmöhre und die V49-Lesung einer im
  Frühjahr gegrabenen Wurzel werden aufgegeben. V31s Veilchen bleibt als
  Bildbesitzer, doch verarbeitet werden Blüten und junge Blätter. `EY` ist nur
  `KLAR?`, nicht `FERTIG`; `<ARG_AIIN>` bleibt opak und ist kein Maß.
- **Stärkster Widerspruch:** Die Illustration besitzt drei überlange,
  gezähnte Wurzelkörper und eine baumartige Mehrfachachse, die ein Veilchen
  nicht hat. Außerdem stehen Wein, Tuch, Blüte, Brust und Geschwür sämtlich
  in der historischen Ganzartikel-Expansion, nicht in den fünf ausgewählten
  Ankern `KLAR?`, `MASS?`, `BEREIT?` und Schluss.

---

## Artikel 4 — f55v: Bärlauchwein als äußerliche Arznei

**Entscheidung:** Allium, am ehesten ein breitblättriger Lauch wie Bärlauch;
zerstoßene Blätter in Wein, bedeckt stehen gelassen, geklärt und äußerlich
gebraucht. Konfidenz **mittel** für Allium, **niedrig bis mittel** für den
konkreten Wundgebrauch.

### Strikte Ankerfolge

| Feld | sichtbare Karten in Reihenfolge | ausgewählte Anker in derselben Reihenfolge | kreative Ganzfeld-Expansion |
|---|---|---|---|
| f55v.5/1 | `qokaiin chaiin ykain ykan ody` | `SETZEN(<ARG_AIIN>) → MASS? → U[YK]+<ARG_AIN> → U[YKAN] → CLOSE(U[O])` | ⟦Setze die Arznei an: Nimm ein Maß frischer breiter Blätter, zerstoße sie, befeuchte sie mit Wein und verschließe das Gefäß.⟧ |
| f55v.5/2 | `daiin chedy talam` | `MASS? → U[CHEDY] → CLOSE_B3(U[TALAM])` | ⟦Nach dem Stehen wird ein Maß durch Tuch gewrungen und klar abgesetzt; der erste Ansatz wird wieder verschlossen.⟧ |
| f55v.11/1 | `ykaiin cheoar cheeky oldy` | `U[YK]+<ARG_AIIN> → U[CHEO]+<ARG_AR> → U[CHEEKY] → CLOSE(FRAME_O(VERKNÜPFEN))` | ⟦Mit einem Teil der geklärten Flüssigkeit wird eine unreine Wunde gewaschen; anschließend wird das Gefäß geschlossen.⟧ |
| f55v.11/2 | `aiin okal oltchy or y orain` | `MASS? → SETZEN(<ARG_AL>) → U[OLTCHY] → BEREITUNG? → U[Y] → BEREITUNG?+<ARG_AIN>` | ⟦Miss für die zweite Verwendung eine Portion ab, setze sie neu an und bereite daraus mit warmen Blättern und wenig Honig einen frischen Umschlag.⟧ |

### Flüssige Ausgabe

> **Vom breiten Lauch.** Setze die Arznei so an: Nimm ein Maß frischer
> breiter Blätter, zerstoße sie gut und befeuchte sie mit weißem Wein. Gib
> alles in ein sauberes Gefäß und verschließe es. Nach dem Stehen wringe ein
> Maß durch ein feines Tuch und lasse die Flüssigkeit klar werden. Wasche
> damit eine unreine äußere Wunde und verschließe den Vorrat wieder. Für eine
> zweite Arznei miss eine Portion ab, setze sie frisch an und lege die
> erwärmten Blätter mit wenig Honig als Umschlag auf.

### Quellenanalogie, Revision, Widerspruch

- **Quellenanalogie:** Balds Augensalbe bestätigt die historische
  Verfahrenskette Allium zerstoßen → Wein → geschlossen im Metallgefäß
  stehen lassen → durch Tuch wringen → klären → äußerlich anwenden. V53
  übernimmt weder Ochsengalle, neun Nächte, Auge noch Feder. Hildegards
  Wegerichkapitel bietet für den botanischen Rivalen die ebenso passende
  Kette Saft/Tuch/Wein oder Honig sowie warme Blätter auf einer schmerzenden
  Stelle.
- **Revision gegen V19/V31/V49:** V19s Großer Wegerich wird zum
  therapeutisch starken Rivalen herabgestuft; V31s Allium bleibt wegen des
  doldigen Schaftes vorn. Weißwein, Wundwäsche und Honig sind nur
  Ganzartikel-Ergänzungen. `OK` bedeutet formal `SETZEN`, nicht „beginne
  einen gemessenen Ansatz“, und die Argumente `<ARG_AIIN>`/`<ARG_AL>` erben
  weder `MASS?` noch `AN?`.
- **Stärkster Widerspruch:** Die Pflanze zeigt keine sichere Zwiebel, sondern
  eine phantastische tierähnliche Wurzel. Der historische Allium-Vergleich
  betrifft ein Augenmittel in einer rund vierhundert Jahre älteren englischen
  Quelle; der V53-Wundumschlag ist daher plausible Rezepttechnik, kein
  pflanzen- oder seitenidentischer Nachweis.

---

## Artikel 5 — f56r: Sonnentauwein gegen trockenen Husten

**Entscheidung:** Sonnentau als Bildbesitzer; eine kleine Menge des ganzen
Krauts in Wein und Honig als Brusttrank. Ikonographische Konfidenz **mittel
bis hoch**, historische Konfidenz für einen solchen Artikel um 1420
**niedrig**.

### Strikte Ankerfolge

| Feld | sichtbare Karten in Reihenfolge | ausgewählte Anker in derselben Reihenfolge | kreative Ganzfeld-Expansion |
|---|---|---|---|
| f56r.5/1 | `chochor cho chodaly daiin` | `FRAME_O(U[CHOR]) → U[CHO] → U[CHODALY] → MASS?` | ⟦Auf feuchtem Heide- oder Moorgrund wird zur Blüte eine kleine Menge des ganzen klebrigen Krauts gesammelt.⟧ |
| f56r.7/1 | `sho kchol otchor choky dal` | `U[SHO] → U[KCHOL] → FRAME_OT(U[CHOR]) → VERWENDEN? → AN?` | ⟦Die runden Blätter werden frisch zerstoßen und vor voller Blüte in mildem Wein angesetzt; der Gebrauch wird auf den Brusttrank bezogen.⟧ |
| f56r.8/1 | `schol choy choky cheeckhody` | `U[SCHOL] → FRAME_O(U[CHOY]) → VERWENDEN? → CLOSE(U[CHEECKHODY])` | ⟦Mit wenig Honig wird die Flüssigkeit nur gelinde erwärmt, gebraucht und danach gut verschlossen.⟧ |
| f56r.12/1 | `sh cho kchey qokokchy` | `U[SH] → U[CHO] → U[KCHEY] → U[QOKOKCHY]` | ⟦Blütenstiel und noch geschlossene Köpfe werden getrennt im Schatten getrocknet.⟧ |
| f56r.13/1 | `okchy chokcheo kchal` | `U[OKCHY] → U[CHOKCHEO] → U[KCHAL]` | ⟦Aus dem trockenen Kraut kann später ein neuer, schwächerer Weinauszug gemacht und kühl bewahrt werden.⟧ |
| f56r.18/1 | `sho chokchy kchoar sotodan` | `U[SHO] → U[CHOKCHY] → U[KCHOAR] → U[SOTODAN]` | ⟦Der frische Auszug wird mit Honig gemildert und bei trockenem Husten oder enger Brust gereicht.⟧ |
| f56r.19/1 | `otchey keol daiin` | `FRAME_OT(TEIL?) → U[KEOL] → MASS?` | ⟦Von dem bezeichneten Teil wird je Gabe nur ein kleines Maß genommen.⟧ |

### Flüssige Ausgabe

> **Vom Sonnentau oder Himmelstau.** Suche das kleine klebrige Kraut auf
> feuchter Heide oder im Moor, wenn der Blütenschaft aufgeht. Nimm nur ein
> kleines Maß des ganzen Krauts, besonders der runden, betauten Blätter, und
> zerstoße es frisch. Übergieße es mit mildem Wein, gib wenig Honig hinzu,
> erwärme es nur gelinde und verschließe das Gefäß. Blütenschaft und
> geschlossene Köpfe können getrennt im Schatten getrocknet und später
> schwächer ausgezogen werden. Verwende von dem frischen Auszug ein kleines
> Maß bei trockenem Husten und enger Brust.

### Quellenanalogie, Revision, Widerspruch

- **Quellenanalogie:** Die *Liber-de-simplici-medicina*-Bildtradition aus dem
  späten 15. Jahrhundert stützt, dass *Drosera* überhaupt in einem spätmittelalterlichen
  Bilderherbal stehen konnte. Wein und Honig sind gewöhnliche mittelalterliche
  Arzneimedien. Eine ausreichend nahe Primärstelle für genau diesen
  Sonnentau-Brusttrank um 1420 wurde jedoch nicht gesichert.
- **Revision gegen V19/V31/V49:** V31s Sonnentau bleibt der Bildgewinner.
  V49s `untere Wurzel`, `schmaler Teil`, `Magenweh`, `offene blasse Blüte`
  und tokenweise Wein-/Honigwerte werden aufgegeben. Die Verarbeitung des
  ganzen Krauts und die Hustenindikation sind neue, offen ausgewiesene
  historische Artikelwetten. Die zwei `OKY` bleiben nur `VERWENDEN?`; `AL`
  bleibt nur `AN?` ohne still ergänztes Objekt.
- **Stärkster Widerspruch:** Die sichere Arzneigeschichte kann wesentlich
  später einsetzen, als die häufig wiederholte Platearius-Erzählung vermuten
  lässt. Anatomisch besitzt die Zeichnung zudem nur zwei übergroße
  Fangblatt-ähnliche Organe und eine unrealistische Spiralachse. Damit ist
  dies gerade kein historischer Identifikationsbeweis, sondern der bewusst
  schärfste kreative Drucktest.

## Vergleichende Entscheidung

| Rang | Artikel | Bildpassung | Quellenpassung um 1420 | Gesamturteil |
|---:|---|---|---|---|
| 1 | f10r-R1 Abiss-Wurzelwasser | mittel | hoch | **behalten**, beste historische Rekonstruktion |
| 2 | f11r Veilchenwein/-öl | mittel | mittel bis hoch, aber ältere Quelle | **behalten**, Verfahren auffallend passend |
| 3 | f55v Alliumwein | mittel bis hoch | mittel, regional/zeitlich ferne Analogie | **behalten mit Wegerich-Rivale** |
| 4 | f10r-R2 Abiss-Blütenkrautöl | mittel | niedrig bis mittel | **behalten als zweite, klar freie Zubereitung** |
| 5 | f56r Sonnentauwein | hoch relativ zu den anderen Bildern | niedrig | **nur als Hochrisiko-Ausgabe behalten** |

## Schluss

Eine historisch klingende vollständige Ausgabe ist möglich, aber nicht aus
den Karten allein komponierbar. Die 100 Ereignisse liefern in dieser
Auswahl nur einen dünnen parataktischen Ankerrahmen. Pflanzenname,
Pflanzenteil, Medium, Gerät, Krankheit und Gebrauch stammen überwiegend aus
Bild und Vergleichsquellen. Gerade die drei stärksten Quellenanalogien —
Abiss-Wasser, Veilchenwein/-öl und Allium-Wein — zeigen, wie leicht ein
plausibler Artikel mit vielen unbekannten Karten gefüllt werden kann. Die
Ausgabe ist deshalb als falsifizierbare historische Inszenierung brauchbar,
nicht als semantische Lesung.

**Lokale Validierung: PASS.** Fünf Artikel, 20 Felder und 100 Ereignisse sind
in der TSV vollständig gezählt; jede der fünf strikten Ankerfolgen stimmt in
Feld- und Ereigniszahl, alle 20 Revisionszeilen und alle TSV-Zellen sind
nichtleer. Der Bild-Scope-Fehler ist oben dokumentiert und aus der Evidenz
ausgeschlossen.
