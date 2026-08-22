# V53 R3 — Vollständige technische Herbal-Registeredition

Status: kreative Fünf-Artikel-Edition über den 20 festen Herbal-Feldern und
100 Ereignissen. Kein Kartenwert, Pflanzenname oder deutscher Satz gilt als
entziffert.

## Kurzurteil

Die vier Seiten enthalten technisch nicht fünf gleichartige Rezepte. Die beste
R3-Lesung ist ein kleines Bündel verwandter Werkstattregister:

```text
f10r / record 1  medizinisches Material- und Betriebsregister
f10r / record 2  saisonales Chargen- und Betriebsregister
f11r / record 1  Teileinventar mit Anwendungsmustern
f55v / record 1  formales Chargen- und Betriebsregister
f56r / record 1  Teileinventar mit Zubereitungs-/Anwendungsmustern
```

Die medizinische Lesung bleibt in allen fünf Fällen ein zulässiger lokaler
Inhalt. Sie ist aber nicht die Feldgrammatik. Insbesondere erklären Inventar
und Musterregister die vielen Teilelisten und offenen Felder besser, während
das Betriebsregister die SET/LINK- und Schlussstruktur von f55v am besten
erfasst.

## Harte Trennung der Ebenen

Für jedes Feld stehen drei Schichten getrennt:

1. **strikte Ankerfolge:** exakte Formelreihenfolge mit ausschließlich den
   V50/V51-Namen; jeder andere Wert bleibt `UNKNOWN[id]`;
2. **stille Bildlieferung:** der abgebildete Eigentümer und sichtbare
   Pflanzenteile dürfen als redaktioneller Kontext ergänzt werden;
3. **kreative Ganzfeldexpansion:** Bild, technische Registerroutine und die
   ältere Herbal-Arbeitshypothese dürfen einen vollständigen deutschen
   Registereintrag liefern.

RIGHT bleibt von gleich geschriebenen Ganzkarten getrennt. So ist
`ARG_AIIN` niemals `AIIN=MASS?`, und `ARG_AL` niemals `AL=AN?`. `CLOSE` wird
als `[Feldschluss]` notiert, nicht als gesprochenes „beende“. Sichtbare Karten
werden nicht neu zerlegt.

Nur 32/100 Herbal-Ereignisse tragen überhaupt einen ausgewählten Anker: 6
formale Operatorereignisse und 26 schwache Atome/Ganzkarten. 68 Ereignisse
bleiben opak. Die folgenden vollständigen Texte sind deshalb absichtlich
Expansionen, keine kompositionellen Übersetzungen.

## Registervergleich

Die Werte 0–3 sind ein transparenter kreativer Passungstest, keine
Wahrscheinlichkeit und kein Beweis.

| Artikel | Medizinartikel | Inventar | Musterregister | Betriebsregister | ausgewählte technische Form |
|---|---:|---:|---:|---:|---|
| `F10-A` | 3 | 2 | 1 | 3 | medizinisches Material-/Betriebsregister |
| `F10-B` | 2 | 2 | 2 | 3 | saisonales Chargen-/Betriebsregister |
| `F11-A` | 3 | 3 | 3 | 1 | Teileinventar mit Anwendungsmustern |
| `F55-A` | 3 | 2 | 2 | 3 | Chargen-/Betriebsregister |
| `F56-A` | 2 | 3 | 3 | 1 | Teileinventar mit Zubereitungsmustern |

## Artikel F10-A — f10r, Record 1

Bildhypothese: Skabiose/Teufelsabbiss-Typ. Das Bild liefert still den
Pflanzeneigentümer und den unteren Wurzelteil.

Formales Profil: 2 Felder, 14 Ereignisse, 5 benannte Anker, 9 opake Ereignisse;
ein `NONOP_CHAIN`, ein offener `LINK_CHAIN`, kein Feldschluss.

### Feld f10r.2/1

Strikte Ankerfolge:

```text
TEIL? | UNKNOWN[CTHOOR] | UNKNOWN[AR] | UNKNOWN[TY] | UNKNOWN[OS] |
UNKNOWN[AIR] | UNKNOWN[OTYTCHOL] | VERWENDEN? | MASS? | UNKNOWN[ETYD]
```

Kreative technische Expansion:

> Wurzelposten des abgebildeten Simplex: den faserigen unteren Teil reinigen,
> aus demselben Vorrat gleichmäßig grob bereiten und mit Rotwein führen; bei
> Magenbeschwerden verwenden, maßweise ausgeben und den Rest trocken lagern.

### Feld f10r.5/1

Strikte Ankerfolge:

```text
UNKNOWN[OKCHY] | FRAME_OT(UNKNOWN[CHOL]) | FRAME_O(VERKNÜPFEN) | BEREIT?
```

Kreative technische Expansion:

> Anwendungsstand: die bereitete Ware warm auflegen, mit dem vorigen
> Arbeitsposten verknüpfen und als bereit führen.

### Vollständiger Artikel

> Registerposten A zum abgebildeten Skabiose-/Teufelsabbiss-Typ. Der untere
> Wurzelteil wird gereinigt, grob bereitet, mit Rotwein geführt und bei
> Magenbeschwerden maßweise verwendet; der Rest bleibt trocken im Vorrat. Ein
> warmer Anwendungsansatz wird an den vorigen Arbeitsstand angeschlossen und
> als bereit vermerkt.

Revision gegenüber V19/V31: V19s medizinischer Inhalt bleibt als
Ganzfeldexpansion, wird aber aus einer fließenden Rezeptklausel in zwei offene
Registerposten überführt. V31s Bildbesitzer ersetzt keinen Kartenwert.

Stärkster Widerspruch: Wein, Magenbeschwerde, Reinigung und Lagerung liegen in
9/14 opaken Ereignissen; weder der medizinische Zweck noch der Pflanzenname ist
ein ausgewählter Anker.

## Artikel F10-B — f10r, Record 2

Bildhypothese: derselbe Skabiose-/Teufelsabbiss-Typ. Das Bild liefert still den
Eigentümer; Standort, Blütenzustand und Chargenroutine sind kreative
Registerexpansionen.

Formales Profil: 3 Felder, 24 Ereignisse, 10 benannte Anker, 14 opake
Ereignisse; zwei `NONOP_CHAIN`, ein offener `LINK_CHAIN`, kein Feldschluss.

### Feld f10r.6/1

Strikte Ankerfolge:

```text
UNKNOWN[YCHEOR] | BEREIT? | BEREITUNG? | UNKNOWN[CTH]+ARG_AIIN |
UNKNOWN[OCTHOLY] | UNKNOWN[Y] | UNKNOWN[Y] | MASS? | UNKNOWN[Y]
```

Kreative technische Expansion:

> Standort-/Herstellposten: Material vom feuchten Wiesengrund; bei
> Bereitmeldung den ausgepressten Saft als Bereitung führen, sanft erhitzen,
> in Teilposten verteilen und nach Maß buchen.

### Feld f10r.8/1

Strikte Ankerfolge:

```text
FRAME_OT(UNKNOWN[CHOR]) | BEREITUNG? | FRAME_OT(UNKNOWN[OL]) |
FRAME_O(VERKNÜPFEN) | ZUVOR? | FRAME_O(VERKNÜPFEN) | MASS? | UNKNOWN[AR]
```

Kreative technische Expansion:

> Vorblüten-Charge: Bereitung und Handvollposten anlegen, zweimal mit dem
> vorigen Arbeitsstand verknüpfen, das Maß notieren und die Herkunft aus
> demselben Vorrat festhalten.

### Feld f10r.9/1

Strikte Ankerfolge:

```text
UNKNOWN[OYKCHOR] | BEREITUNG? | BEREITUNG? | UNKNOWN[Y] |
UNKNOWN[KAIIIN] | UNKNOWN[Y] | FRAME_O(UNKNOWN[D]+ARG_AIIN)
```

Kreative technische Expansion:

> Blütenöffnungs-Charge: zwei Bereitungsposten mit Zwischenportionen führen,
> bis zum bitteren Kontrollzustand arbeiten und den verbleibenden Teil unter
> Öl lagern.

### Vollständiger Artikel

> Registerposten B desselben Bildbesitzers. Ein Wiesengrund-Posten führt
> bereiten Presssaft, Wärme, Teilposten und Maß. Eine Charge vor der Blüte wird
> über zwei Verknüpfungen an frühere Arbeit angeschlossen; eine zweite Charge
> bei geöffneter Blüte wird bis zum bitteren Kontrollzustand geführt und unter
> Öl gelagert.

Revision: V19s „zweiter Block“ wird als selbständiger zweiter Record ernst
genommen. Die beste technische Lesung ist eine Folge saisonal unterschiedener
Chargen, nicht ein angehängter Prosasatz des ersten Arzneiartikels.

Stärkster Widerspruch: Die ganze Vorblüte-/Blütenöffnung-Achse hängt an den
opak gebliebenen Karten `CHOR` und `OYKCHOR`. Alle drei Felder sind offen; die
saisonale Zweiteilung ist daher eine kreative Expansion, kein formaler Gate.

## Artikel F11-A — f11r, Record 1

Bildhypothese: Veilchen. Diese V31-Hypothese ersetzt V19s
Wildkarotten-/Umbelliferenbesitzer nur auf Bildebene. Das Bild darf still
Wurzel, Krone und Blatt als drei Teile liefern.

Formales Profil: 4 Felder, 17 Ereignisse, 3 benannte Anker, 14 opake
Ereignisse; drei `NONOP_CHAIN`, ein `SINGLETON`, ein Feldschluss und kein
formaler Operator.

### Feld f11r.1/1

Strikte Ankerfolge:

```text
UNKNOWN[SHOL] | UNKNOWN[CHO]+ARG_AL | UNKNOWN[CFHY] |
UNKNOWN[FYD]+ARG_AIIN | UNKNOWN[CPHY] | KLAR? | CLOSE(UNKNOWN[CHO])
```

Kreative technische Expansion:

> Wurzel-/Pressmuster des Bildbesitzers: im Frühjahr am schattigen Standort
> vor Öffnung der Krone gewinnen, die gequetschte Wurzel durch Tuch pressen,
> nachseihen bis klar und offen abkühlen. [Feldschluss]

### Feld f11r.1/2

Strikte Ankerfolge:

```text
UNKNOWN[OYTY]
```

Kreative technische Expansion:

> Die Blütenkrone als getrennten Vorrat zurückhalten.

### Feld f11r.4/1

Strikte Ankerfolge:

```text
UNKNOWN[CHOL] | UNKNOWN[Y] | UNKNOWN[KCHY] | UNKNOWN[Y] | MASS?
```

Kreative technische Expansion:

> Eigentümer-/Anwendungsmuster: eine Teilcharge auf die geschwollene Stelle
> binden und den vorgeschriebenen Maßposten notieren.

### Feld f11r.7/1

Strikte Ankerfolge:

```text
FRAME_OT(UNKNOWN[CHY]) | UNKNOWN[OKCHOL] | BEREIT? | UNKNOWN[Y]
```

Kreative technische Expansion:

> Blattmuster: einen warmen Umschlag bereiten und auflegen; bei Bereitstatus
> die vorgesehene Teilcharge führen.

### Vollständiger Artikel

> Teile- und Anwendungsmuster zum abgebildeten Veilchen: Die Wurzel wird als
> Press- und Klärposten geführt, die Blütenkrone getrennt zurückbehalten. Ein
> weiterer Eigentümerposten beschreibt eine maßweise Auflage an einer
> geschwollenen Stelle; das Blatt erhält ein eigenes warmes Umschlagmuster.

Revision: Der Artikel wird nicht länger als eine einzige lineare
Wildkarottenrezeptur gelesen. V31s Veilchen bleibt ein stiller Bildbesitzer;
die vier Felder bilden ein Teileinventar mit unabhängigen Arbeitsmustern.

Stärkster Widerspruch: V19 und V31 widersprechen sich beim Besitzer, und 14/17
Ereignisse bleiben opak. Weder Schwellung noch Pressen noch die Teilidentitäten
werden von den drei ausgewählten Ankern `KLAR?`, `MASS?`, `BEREIT?` erzwungen.

## Artikel F55-A — f55v, Record 1

Bildhypothese: Bärlauch/Allium. V19s Breitwegerich bleibt wegen der breiten
Blatt- und Wundanwendung ein starker Besitzer-Rivale.

Formales Profil: 4 Felder, 18 Ereignisse, 8 benannte Anker, 10 opake
Ereignisse; zwei `SET_CHAIN`, ein `LINK_CHAIN`, ein `NONOP_CHAIN`, drei
Feldschlüsse. Dies ist der formal stärkste Betriebsregister-Artikel.

### Feld f55v.5/1

Strikte Ankerfolge:

```text
SETZEN[ARG_AIIN] | MASS? | UNKNOWN[YK]+ARG_AIN | UNKNOWN[YKAN] |
CLOSE(UNKNOWN[O])
```

Kreative technische Expansion:

> Charge I: einen formalen AIIN-Rechtsposten setzen, danach einen getrennten
> Maßposten führen; das breite Blatt sanft in Weißwein erhitzen und bis klar
> ziehen lassen. [Feldschluss]

### Feld f55v.5/2

Strikte Ankerfolge:

```text
MASS? | VARIANT_D(UNKNOWN[Y]) | CLOSE_B3(UNKNOWN[ALA])
```

Kreative technische Expansion:

> Kontroll-/Waschposten: Maß notieren, gleichmäßig mischen und die wunde Stelle
> einmal waschen. [B3-Feldschluss]

### Feld f55v.11/1

Strikte Ankerfolge:

```text
UNKNOWN[YK]+ARG_AIIN | UNKNOWN[O]+ARG_AR | UNKNOWN[EKY] |
CLOSE(FRAME_O(VERKNÜPFEN))
```

Kreative technische Expansion:

> Zweiter Arbeitsgang: zweiten Gebrauch und Weißweinzusatz führen, warm halten
> und mit dem vorigen Arbeitsstand verknüpfen. [Feldschluss]

### Feld f55v.11/2

Strikte Ankerfolge:

```text
MASS? | SETZEN[ARG_AL] | UNKNOWN[OLTCHY] | BEREITUNG? | UNKNOWN[Y] |
BEREITUNG?+ARG_AIN
```

Kreative technische Expansion:

> Charge II: Maß buchen, den formalen AL-Rechtsposten setzen, die Ware im
> bedeckten Gefäß halten und die Bereitung als frischen Gebrauchsposten führen.

### Vollständiger Artikel

> Chargenblatt zum abgebildeten Bärlauch-/Allium-Typ. Charge I setzt einen
> formalen Rechtsposten, führt das Maß und verarbeitet das breite Blatt in
> Weißwein; ein eigener Waschposten folgt. Ein zweiter warmer Weingang wird an
> den vorigen Arbeitsstand verknüpft. Charge II setzt einen anderen
> Rechtsposten, hält die Bereitung bedeckt und führt sie frisch weiter.

Revision: V19s flüssiger Wundheilartikel wird als zwei formal gebuchte Chargen
mit Kontroll-/Waschposten und Wiederanknüpfung neu gesetzt. Der V31-Besitzer
bleibt austauschbar; er verändert keinen SET- oder LINK-Baum.

Stärkster Widerspruch: V31s Bärlauch/Allium und V19s Breitwegerich konkurrieren
direkt. Die drei Feldschlüsse und formalen Operatoren stützen Betriebsführung,
nicht aber Wunde, Wein, Wärme oder eine bestimmte Pflanzenart; 10/18
Ereignisse bleiben opak.

## Artikel F56-A — f56r, Record 1

Bildhypothese: Sonnentau; dies ist V31s stärkster, aber weiterhin nur
provisorischer Besitzer. Das Bild darf still Wurzel, Blatt, Kopf und Blüte
liefern.

Formales Profil: 7 Felder, 27 Ereignisse, 6 benannte Anker, 21 opake
Ereignisse; sieben `NONOP_CHAIN`, nur ein Feldschluss und kein SET/MARK/LINK.
Das spricht stärker für Teileinventar und Musterkarten als für einen einzigen
ausgeführten Prozess.

### Feld f56r.5/1

Strikte Ankerfolge:

```text
FRAME_O(UNKNOWN[CHOR]) | UNKNOWN[O] | UNKNOWN[ODALY] | MASS?
```

Kreative technische Expansion:

> Beschaffungsposten: im Frühjahr den nächsten Bildteil und die dünne untere
> Wurzel gewinnen; Maß notieren.

### Feld f56r.7/1

Strikte Ankerfolge:

```text
UNKNOWN[O] | UNKNOWN[KCHOL] | FRAME_OT(UNKNOWN[CHOR]) | VERWENDEN? | AN?
```

Kreative technische Expansion:

> Weinmuster: den nächsten Teil vor der Blüte in Weißwein ziehen, verwenden
> und an der vorgesehenen Stelle führen.

### Feld f56r.8/1

Strikte Ankerfolge:

```text
UNKNOWN[CHOL] | FRAME_O(UNKNOWN[Y]) | VERWENDEN? | CLOSE(UNKNOWN[ECKHO])
```

Kreative technische Expansion:

> Eigentümer-/Standortmuster: das abgebildete Simplex vom feuchten schattigen
> Heidestand verwenden und als unbedecktes Trockenpflaster führen.
> [Feldschluss]

### Feld f56r.12/1

Strikte Ankerfolge:

```text
UNKNOWN[H] | UNKNOWN[O] | UNKNOWN[KCHEY] | UNKNOWN[OKOKCHY]
```

Kreative technische Expansion:

> Teileinventar: kleinen Samen- oder Knospenkopf, nächsten Bildteil und
> getrocknetes schmales Blatt getrennt führen; im Schatten trocknen.

### Feld f56r.13/1

Strikte Ankerfolge:

```text
UNKNOWN[OKCHY] | UNKNOWN[OKCHEO] | UNKNOWN[KCH]+ARG_AL
```

Kreative technische Expansion:

> Gebrauch-/Lagerungsmuster: bereitete Ware bei Magenbeschwerden geben und den
> Rest trocken im Schatten lagern.

### Feld f56r.18/1

Strikte Ankerfolge:

```text
UNKNOWN[O] | UNKNOWN[OKCHY] | UNKNOWN[KCHO]+ARG_AR | UNKNOWN[OTODAN]
```

Kreative technische Expansion:

> Honigvariante: nächsten Teil und bereitete Ware mit Honig mischen und frisch
> verwenden.

### Feld f56r.19/1

Strikte Ankerfolge:

```text
FRAME_OT(TEIL?) | UNKNOWN[KEOL] | MASS?
```

Kreative technische Expansion:

> Blütenposten: den ausgewählten Teil als helle geöffnete Blüte führen und das
> Maß notieren.

### Vollständiger Artikel

> Teileinventar und Anwendungsmuster zum abgebildeten Sonnentau. Ein
> Wurzelposten erhält Beschaffungszeit und Maß; ein weiterer Teil wird vor der
> Blüte in Wein geführt und örtlich verwendet. Standort und Trockenpflaster,
> Samen-/Knospenkopf, schmales Blatt, Magengebrauch mit Lagerrest,
> Honigvariante und ein maßweiser Blütenposten stehen als getrennte Muster.

Revision: V19/V31s Sonnentau-Lead bleibt der stärkste stille Eigentümer, aber
der Text wird nicht mehr zu einem einzigen Rezept geglättet. Sieben
nichtoperatorische Felder werden als Teileinventar mit unabhängigen
Zubereitungs- und Gebrauchsmustern ediert.

Stärkster Widerspruch: 21/27 Ereignisse sind opak, es gibt keinen formalen
Operator und nur einen Feldschluss. Wein, Honig, Magenbeschwerde und selbst die
Teilnamen sind Bild-/Prosaexpansionen; das medizinische Gesamtbild ist daher
nicht strukturell erzwungen.

## Editionsregel und Scheitern

Ein Schreiber kann diese Ausgabe reproduzieren:

1. kopiere Oberfläche und exakten Formelbaum unverändert;
2. schreibe die strikte Ankerfolge mit `UNKNOWN[id]` aus;
3. trage den Bildbesitzer und sichtbare Teile in eine getrennte Randspalte ein;
4. wähle pro Record genau einen Registertyp;
5. expandiere jedes ganze Feld, ohne deutsche Wörter auf opake Einzelkarten
   zurückzuverteilen;
6. kennzeichne `CLOSE` nur als formalen Feldschluss.

Die Edition scheitert, sobald ein Besitzer zum gelesenen Pflanzennamen, eine
lokale Zutat zum Kartenatom, ein RIGHT zum gleich geschriebenen Ganzkartenwert
oder eine der fünf Ganzartikelübersetzungen zu plaintext erklärt wird. Die
maschinell vollständige Fassung steht in `V53_R3_FIVE_ARTICLES.tsv`; die fünf
Revisionen und stärksten Widersprüche stehen in `V53_R3_REVISIONS.tsv`.
