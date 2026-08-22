# Richtungs- und Mediengrammatik des technischen Zeichners

Status: schnelle kreative Zehn-Seiten-Werkstatttheorie, keine behauptete
Entzifferung.

## Ergebnis

Die Richtungsfamilien lassen sich als kleine Quelle--Medium--Ziel-Grammatik
lesen, ohne aus f81v--f83r eine einzige Flussmaschine zu machen:

```text
AR          aus/von; Quellseite oder Ausgangsargument
AIR         fliessende Fluessigkeit; ein Medium im Lauf
AL          an/bei/zu der bezeichneten Stelle; Zieladresse

CHD~CHED    einen Posten umsetzen oder fuehren, richtungsneutral
L+CHED      aus dem lokalen Posten herausnehmen oder abfuehren
P+CHED      in einen lokalen Empfaenger einbringen oder einfuellen
```

`AR` und `AL` sind also keine gezeichneten Pfeile. Sie verhalten sich wie eine
Quell- und eine Zieladresse im Werkstattcode. `AIR` bezeichnet dagegen primaer
das bewegte Medium, nicht bloss die Linie, auf der es sich bewegen koennte.

## Umfang

Geprueft wurden **51 Richtungsereignisse in 24 exakten Kartenidentitaeten**:

- 10 AR-Ereignisse in sechs Karten;
- vier AIR-Ereignisse in vier Karten;
- 26 AL-Ereignisse in zehn Karten;
- zwoelf L+CHED-Ereignisse in fuenf Karten;
- zwei P+CHED-Ereignisse in zwei Karten.

Die Ueberlappungen `lchedar`, `lchedal` und `pchedal` werden dabei jeweils nur
einmal als Ereignis gezaehlt. Zusaetzlich wurden `chokcheo` und `qokylddy` als
zwei Bildbesitzer-Grenzfaelle aufgenommen. Alle 53 Einzelereignisse stehen in
`DRAUGHTSMAN_DIRECTION_PARADIGM.tsv`; `OWNER_DIRECTION_MAP.tsv` buendelt sie
ueber 19 lokale Bildbesitzer.

## Entscheidung zu `AIR`

`AIR` wird als **FLIESSENDE FLUESSIGKEIT / LAUFWASSER**, nicht als blosser
Weg, geschlossen.

Die vier Karten liefern zusammen den entscheidenden Kontrast:

| Karte | Besitzer | neue Lesung | was gestrichen wird |
|---|---|---|---|
| `chair` | f10r, ganze Pflanze; keine gezeichnete Leitung | frische oder laufende Fluessigkeit, lokal plausibel Wasser | kein Bildbeweis fuer Quellwasser |
| `kair` | f81v, gemeinsames gruenes Beckenfeld | laufende Becken-/Waschfluessigkeit | kein sicherer Rueckstrom |
| `okair` | f83r, korbartige Gefaessstation mit offenen Strichen | Fluessigkeit in Lauf bringen | weder `oben` noch gezeichnete Richtung |
| `schedair` | f83r, tatsaechlich bogenverbundenes Paar | fliessende Fluessigkeit fuehren/umsetzen | weder `klar` noch sicher abziehen |

Waere `AIR` nur `Weg/Rohr`, waere `chair` im bildlosen Pflanzenartikel der
schwaechste Beleg. Als bewegtes Medium passt es dort nach einem gelernten
Gefaesswert und vor einem Auszugsschritt ebenso gut wie bei Becken, Gefaess und
Bogenpaar. Umgekehrt waere `AIR = Wasser` zu eng: In Biological kann das Medium
Badewasser, Waschfluessigkeit, Auszug oder verbrauchte Flotte sein. Der
uebertragbare Wert ist daher `fliessende Fluessigkeit`; `Wasser` bleibt der
haeufigste lokale Default.

Ein sichtbarer Strich ist nicht Voraussetzung fuer AIR. Der Code kann einem
Schreiber sagen, dass ein Stoff im Lauf benutzt wird, auch wenn das Bild nur
die Pflanze oder den lokalen Besitzer zeigt. Wo ein Bogen oder Lauf sichtbar
ist, zeigt er Kontakt, aber nirgends Quelle, Senke oder Pfeilrichtung.

## `AR`: Quellseite, nicht Stoffname

Die nackte exakte AR-Karte erscheint als `char|dar|sar` auf Herbal und
Biological. Da dieselbe Karte sowohl bei einer ganzen Pflanze als auch bei
Becken-, Faecher- und sogar ungelosten Besitzern steht, kann sie kein
bestimmtes Gefaess oder Wasserwort sein. Die einfache Lesung ist `davon,
daraus, aus dem laufenden Posten`.

| exakte Karte | Ereignisse | ausgewaehlte Werkstattlekture |
|---|---:|---|
| `4d4559019a961b834aa1` (`char|dar|sar`) | 5 | davon/daraus; aus dem aktuellen Quellposten |
| `3ae9a121ba0045b913e8` (`qokar`) | 1 | von dort in Arbeit nehmen; daraus anwenden |
| `807591efc3d3f7ddbfab` (`cheoar`) | 1 | aus der Auszugs- oder Traegerfluessigkeit |
| `883a6708116c342cb10b` (`skar`) | 1 | aus der Station entnehmen oder ausgiessen |
| `b6b654722e55729cc947` (`otar`) | 1 | danach herausnehmen/auslassen |
| `0f15effeca7ab10bb026` (`lchedar`) | 1 | aus dem bezeichneten Quellposten abfuehren |

`AR` gibt damit die logische Quellseite an. Ob der lokale Vollzug schoepfen,
abgiessen, abziehen, entnehmen oder aus einem Pflanzenansatz nehmen heisst,
liefert der Besitzer oder eine andere Karte.

## `AL`: Zieladresse, nicht unterer Ablauf

AL ist die breiteste und sauberste Richtungsfamilie. Die nackte exakte Karte
hat die sichtbaren Huellen `al|chal|cheal|dal|sal|tal` und erscheint zehnmal
bei einer Pflanzen-Anwendungsstelle, im gemeinsamen Becken, an Randstationen,
in einer ungelosten Bildluecke und am rechten Mehrarmknoten. Damit kann AL
weder `unteres Becken` noch `Ablauf` fest bedeuten.

Die gemeinsame Lesung lautet:

```text
AL = an/bei/zu der bezeichneten Stelle; Zieladresse
```

Die zehn exakten Karten bleiben unterscheidbar:

| exakte Karte | Ereignisse | ausgewaehlte Werkstattlekture |
|---|---:|---|
| `dd0ecaf5e27d81befffc` (`al|chal|cheal|dal|sal|tal`) | 10 | an/bei der bezeichneten Stelle |
| `308e8ea2d5d190c498e8` (`okal|qokal`) | 6 | an der Zielstelle einsetzen/anwenden |
| `4a7a6326ac95a8809302` (`qokaly`) | 1 | diesen Posten an der Zielstelle einsetzen |
| `93f69c38fdedee1598e9` (`qokeedal`) | 1 | an der Stelle anhaltend in Kontakt halten |
| `90bcf0a9ec0ef56399e6` (`otal|qotal`) | 3 | danach zur/bei der naechsten Stelle |
| `00d8ebe3c68294eeac39` (`chdal`) | 1 | den Posten an der Stelle umsetzen |
| `433713294b25b0a12f66` (`lchedal`) | 1 | Entnahme- oder Uebergabestelle |
| `ba540da978ea132f6da5` (`pchedal`) | 1 | Einfuell-/Empfangsstelle |
| `7811a7daff25d476e28d` (`olsaly`) | 1 | die bezeichnete lokale Stelle; Ganzkartenrest bleibt |
| `97ddca78c9ebcc956d04` (`ldalor`) | 1 | an der bezeichneten Stelle; Ganzkartenrest bleibt |

Besonders wichtig sind die Besitzer ohne sichere Leitung: Auch dort bleibt AL
sinnvoll als Adresse. `Zum unteren Ablauf` wird deshalb aus den drei
`OT+AL`-Defaults gestrichen; der Schreiber sagt nur `danach zur naechsten oder
bezeichneten Stelle`.

## Die gerichtete CHED-Paarung

### `L+CHED`: herausnehmen oder abfuehren

`lched`, `lchedal`, `lchedar`, `lchedy` und `lochedy` verteilen sich ueber
obere Becken, gemeinsames Feld, Randgefaesse, offene Endmotive, eine bildlich
ungeloeste Zone sowie linke und rechte Lokalstationen. Nicht alle besitzen ein
gezeichnetes Rohr. Der gemeinsame Wert darf daher weder `nach unten` noch
`durch den linken Ablauf` sein.

Die einfache Werkstattaktion ist:

```text
L+CHED = aus dem lokalen Posten herausnehmen / quellseitig abfuehren
```

`lchedy` fuegt den gelernten lokalen Abschluss hinzu. `lchedar` nennt die
Quelle ausdruecklich, `lchedal` die Entnahme-/Uebergabestelle, und das `O` in
`lochedy` bleibt unbekannt. Das Arbeitsgut kann Fluessigkeit, Tuch, Rueckstand
oder ein anderer Posten sein; L+CHED ist nicht selbst ein Wasserwort.

### `P+CHED`: in den Empfaenger einbringen

Die zwei P-Karten liegen an empfaengerfaehigen Besitzern:

- `pchedy` am f82r-Beckenrand mit Gefaess-/Figurenposten;
- `pchedal` an der direkt sichtbaren korbartigen Gefaessstation auf f83r.

Damit bleibt die bereits gewaehlte Gegenrichtung zu L+CHED bestehen:

```text
P+CHED = in einen Empfaenger einbringen / einfuellen
```

Die Bilder liefern keine Pfeile, aber die korbartige Station macht
`Empfaengerseite` konkreter als das alte widerspruechliche `abziehen`.
`pchedy` heisst daher `in den Empfaenger einbringen; Schluss`, `pchedal`
`Einfuell-/Empfangsstelle`. P wird weiterhin nicht ausserhalb dieser beiden
Karten verallgemeinert.

## Was die Besitzer wirklich zeigen

Die 19 Besitzer teilen sich in vier Klassen:

1. Herbal-Ganzpflanzen ohne gezeichnete Fluessigkeit oder Geraet: Sie stuetzen
   nur textinterne Quelle, Medium und Anwendungsstelle.
2. Gemeinsame gruene Felder: Fluessigkeit oder Bad ist plausibel, aber keine
   Reihenfolge oder Ruecklaufrichtung sichtbar.
3. Lokale Gefaess-, Rand- und Mehrarmstationen: Einfuellen, Entnehmen und
   Umsetzen sind konkrete Werkstattdefaults, doch die Arme bleiben ungerichtet.
4. Zwei echte Bogenpaare: Kontakt ist sichtbar, Quelle und Senke fehlen.

Zwischen diesen Besitzern stehen harte Resets. Insbesondere sind die
f83r-Randstationen nicht aneinander angeschlossen, die Bildluecke traegt keine
Leitung, und linke Fransenstation und rechter S-Lauf duerfen nicht als ein
Kreislauf gelesen werden. Die Grammatik kann eine lokale Richtung kodieren;
das Bild beweist keine globale Hydraulik.

## `CHEO` und `LDDY`

### Provisorische Schliessung von `CHEO`

Der Bildbesitzer allein zeigt bei `chokcheo` auf f56r weder Wasser noch Wein.
Der feste Pflanzenartikel und die Kartenfolge liefern aber eine brauchbare
zweiteilige Familie:

```text
OK+CHEO     eine Auszugs-/Traegerfluessigkeit einsetzen
CHEO+AR     aus dieser Auszugsfluessigkeit nehmen
```

`chokcheo` steht zwischen `den laufenden Posten in Arbeit nehmen` und `durch
ein Tuch`; `cheoar` steht auf einer zweiten Pflanzen-Seite in einem
Anwendungs-/Warmhalteschritt. Deshalb wird `CHEO` provisorisch als
**AUSZUGS- ODER TRAEGERFLUESSIGKEIT** gelesen. Wasser, Wein, Oel oder ein
fertiger Pflanzenauszug bleiben lokale Fuellungen. `ycheor` bleibt als eigene
Ganzkarte unzerlegt und ist kein Gegenbeweis durch blossen Zeichenueberlapp.

### `LDDY` bleibt eine Abschlusskarte

`qokylddy` gehoert zum ungerichteten B4-Bogenpaar. Der Besitzer zeigt weder
Tuch noch warme Hautstelle noch eine Quelle/Senke. Er kann daher zwischen
`auflegen`, `abnehmen` und `Leitung oeffnen` nicht entscheiden. Die ausgewaehlte
Lesung bleibt:

```text
OK+Y+LDDY = diesen Posten lokal anwenden und den Schritt abschliessen
```

LDDY wird nicht allein wegen des `L` in die L+CHED-Richtung gezogen.

## Lehrregel fuer den Zeichner

Ein Schreiber oder Zeichner muss nur folgende Adressen lernen:

```text
AR  Woher?       aus/von diesem Quellposten
AIR Was laeuft?  die bewegte Fluessigkeit
AL  Wohin/wo?    an/bei der bezeichneten Stelle
L+CHD Wohin aus? aus dem Posten heraus
P+CHD Wohin ein? in den Empfaenger hinein
```

Die Zeichnung liefert den lokalen Besitzer. Die Karte liefert die
Arbeitsrelation. Nirgends ist dafuer eine seitenweite Rohrmaschine noetig.

## Grenze

Diese Schliessung ist die kreativ beste gemeinsame Lesung der festen zehn
Seiten. Sie identifiziert keine historische Sprache und keinen bestaetigten
Voynich-Wortwert. Die drei Astro-Seiten liefern in dieser Prosa-Ausgabe keine
Richtungskarten. Keine weitere Seite und kein versiegeltes Material wurde
benutzt; `f84` und `f84r` blieben vollständig versiegelt.
