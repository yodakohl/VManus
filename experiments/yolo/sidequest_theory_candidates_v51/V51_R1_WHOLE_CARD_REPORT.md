# V51 R1 — Drucktest der neun wiederkehrenden Ganzkarten

Status: begrenzte kreative Schreibwerkstatt-Arbeit, keine Entzifferung und
keine historische Wortidentifikation.

## Entscheidung

Alle 70 festen V49-Ereignisse der neun wiederkehrenden exakten Ganzkarten
wurden geprüft. Das kleinste R1-Merkinventar lautet:

| exakte Ganzkarte | V49 | V51-R1 | Entscheidung |
|---|---|---|---|
| `AIIN` | `MASS` | `MASS` | behalten |
| `EY` | `FERTIG` | `KLAR` | ersetzen |
| `OKY` | `NUTZEN` | `VERWENDEN` | ersetzen |
| `LCHE` | `ABLASS` | `ABLASSEN` | ersetzen |
| `OKE` | `SPÜLEN` | `SPÜLEN` | behalten |
| `CTHY` | `BEREIT` | `BEREIT` | behalten |
| `OKEEY` | `LAUWARM` | `LAUWARM` | behalten |
| `CKHY` | `VERBINDUNG` | `DURCH` | ersetzen |
| `OLOR` | `VORIGES` | `VORHER` | ersetzen |

Keines dieser Merkwörter ist eine bestätigte Übersetzung. Sie dienen nur
dem Rücklesen einer **ganzen exakten Kartenidentität**. Kein sichtbarer Teil
der Oberfläche erbt einen Wert, und aus keinem Merkwort darf eine Oberfläche
gebaut werden. Insbesondere werden die V50-Hostwerte nicht in diese neun
Ganzkarten hineinkomponiert.

`VERWENDEN`, `ABLASSEN` und `SPÜLEN` haben in der deutschen Merkhilfe eine
offene Ergänzungsstelle. Der jeweilige Gegenstand ist nicht im Wort verborgen.
`DURCH` ist eine offene Relation; Lauf, Gefäß oder Material gehören nicht zu
ihr. `VORHER` markiert nur Rückwärtsbezug und enthält kein stilles „Ding“.

## Vollständigkeits- und Stellungsabgleich

Gezählt wurde innerhalb von `page + locus + record`. Eine physische Zeile ist
kein angenommener Satz. Wiederholungen derselben Tuple-ID bestätigen die
Wiederverwendung der Karte, nicht mehrfach unabhängig ihre kreative Bedeutung.

| Karte | Ereignisse | Seiten | Datensätze | Oberflächen | Anfang | innen | Ende |
|---|---:|---:|---:|---:|---:|---:|---:|
| `AIIN` | 20 | 7 | 18 | 5 | 4 | 11 | 5 |
| `EY` | 4 | 3 | 4 | 2 | 1 | 2 | 1 |
| `OKY` | 10 | 5 | 10 | 3 | 0 | 7 | 3 |
| `LCHE` | 8 | 2 | 8 | 1 | 0 | 7 | 1 |
| `OKE` | 8 | 2 | 6 | 1 | 1 | 7 | 0 |
| `CTHY` | 7 | 3 | 7 | 3 | 0 | 6 | 1 |
| `OKEEY` | 7 | 3 | 7 | 2 | 1 | 6 | 0 |
| `CKHY` | 4 | 2 | 4 | 2 | 0 | 4 | 0 |
| `OLOR` | 2 | 2 | 2 | 2 | 1 | 1 | 0 |

Keines der 70 Ereignisse ist ein Ein-Karten-Datensatz. Die Seitenverteilung
ist:

| Seite | AIIN | EY | OKY | LCHE | OKE | CTHY | OKEEY | CKHY | OLOR |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| `f10r` | 3 | 0 | 1 | 0 | 0 | 2 | 0 | 0 | 1 |
| `f11r` | 1 | 1 | 0 | 0 | 0 | 1 | 0 | 0 | 0 |
| `f55v` | 3 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| `f56r` | 2 | 0 | 2 | 0 | 0 | 0 | 0 | 0 | 0 |
| `f81v` | 2 | 0 | 1 | 0 | 3 | 0 | 1 | 3 | 1 |
| `f82r` | 2 | 2 | 2 | 1 | 0 | 0 | 3 | 1 | 0 |
| `f83r` | 7 | 1 | 4 | 7 | 5 | 4 | 3 | 0 | 0 |
| `f67r2` | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| `f68r1` | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| `f69v` | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |

Die vier Seiten ohne Vorkommen liefern keine Gegenprobe und erlauben keine
neue Karte.

## Alle neun Karten und ihre lokalen Defaults

| Karte | feste Oberflächen mit Zahl | n | unveränderte lokale V49-Expansion |
|---|---|---:|---|
| `AIIN` | `aiin` 3; `chaiin` 1; `daiin` 11; `saiin` 4; `taiin` 1 | 20 | Ein vorgeschriebenes Maß |
| `EY` | `cheey` 2; `shey` 2 | 4 | Bis die Flüssigkeit klar abläuft |
| `OKY` | `choky` 2; `oky` 1; `qoky` 7 | 10 | Die aktive Portion verwenden |
| `LCHE` | `lchedy` 8 | 8 | lasse die verbrauchte Flüssigkeit in das untere Auffanggefäß ablaufen und beende den Schritt |
| `OKE` | `qokedy` 8 | 8 | spüle die bezeichnete Stelle einmal und beende den Schritt |
| `CTHY` | `checthy` 2; `cthy` 3; `shcthy` 2 | 7 | Sobald die Zubereitung gebrauchsfertig ist |
| `OKEEY` | `okeey` 1; `qokeey` 6 | 7 | temperiere die Arbeitsflüssigkeit und halte sie lauwarm |
| `CKHY` | `chckhy` 3; `shckhy` 1 | 4 | durch die verbundenen Läufe |
| `OLOR` | `cholor` 1; `olor` 1 | 2 | Aus dem vorigen Ansatz entnehmen |

Diese neun Expansionen sind Ganzkarten-Defaults. Ihre Wiederholung in allen
Ereignissen derselben Tuple-ID ist Konsistenz der Ausgabe, keine unabhängige
semantische Bestätigung.

## Einzelentscheidungen

### `AIIN = MASS` — behalten

- **Lehrregel:** Der Lehrling zeigt die ganze AIIN-Karte und sagt nur `MASS`.
  Einheit, Stoff, Gefäß, Anzahl und vorgeschriebene Größe bleiben offen.
- **Vollvorkommensdruck:** 20 Ereignisse auf sieben Seiten wechseln frei
  zwischen Anfang (4), Innerem (11) und Ende (5). Zweimal steht die Karte im
  selben Datensatz (`f55v.5`, `f81v.7`); ein wiederholbarer Mengenmerker bleibt
  lehrbar.
- **Stärkster Widerspruch:** Eine nackte Maßangabe ist an Anfang oder Ende
  grammatisch unvollständig, und der identische lokale Default wurde aus dem
  Kartenwörterbuch wiederholt. Weder konkrete Einheit noch Dosis ist belegt.
  `MASS` bleibt deshalb nur ein breites Merkwort.
- **Einwort-Rivalen:** `MENGE`; `DOSIS`.

### `EY = KLAR` — `FERTIG` ersetzen

- **Lehrregel:** Die ganze EY-Karte wird als Zustandsmerker `KLAR` gelernt.
  Flüssigkeit, Ablauf und die Relation *bis* werden nicht mitgelernt.
- **Vollvorkommensdruck:** Vier Ereignisse stehen einmal am Anfang, zweimal
  innen und einmal am Ende. `KLAR` kann Bedingung oder Zustand bleiben, ohne
  die Stellung umzudeuten.
- **Stärkster Widerspruch:** `cheey` beginnt `f82r.23`, endet aber `f82r.7`.
  `FERTIG` als Abschlusswert widerspricht diesem Wechsel; auch der lokale Satz
  sagt genauer *klar* als *fertig*.
- **Einwort-Rivalen:** `FERTIG`; `ABFLUSS`.

### `OKY = VERWENDEN` — `NUTZEN` ersetzen

- **Lehrregel:** Die ganze OKY-Karte ruft versuchsweise die Handlung
  `VERWENDEN` auf. Was verwendet wird und wozu, bleibt eine offene Stelle.
- **Vollvorkommensdruck:** Zehn Ereignisse auf fünf Seiten stehen siebenmal
  innen und dreimal am Ende. Der Handlungswert verlangt weder Start noch
  Abschluss und bleibt in beiden Stellungen gleich.
- **Stärkster Widerspruch:** Auf `f10r.2` folgen nach OKY noch eine Maßkarte und
  eine Aufbewahrungsexpansion; die Karte kann also nicht „Endgebrauch“ heißen.
  `VERWENDEN` ist lediglich die eindeutigere Verbform von V49s mehrdeutigem
  `NUTZEN` und enthält keine „aktive Portion“.
- **Einwort-Rivalen:** `NUTZEN`; `GEBRAUCHEN`.

### `LCHE = ABLASSEN` — `ABLASS` ersetzen

- **Lehrregel:** Die exakte ganze LCHE-Karte heißt als Arbeitsruf
  `ABLASSEN`. Welche Substanz wohin läuft und ob danach ein Schritt endet,
  steht nicht im Merkwort.
- **Vollvorkommensdruck:** Acht Ereignisse stehen siebenmal innen und nur
  einmal am Ende. Die Karte bleibt eine lokale Handlung und ist kein
  Datensatzabschluss.
- **Stärkster Widerspruch:** Auf mehreren f83r-Datensätzen folgen nach LCHE
  weitere Karten; die ganze Defaultphrase „... und beende den Schritt“ darf
  daher nicht zu `ABSCHLUSS` verkürzt werden. `ABLASSEN` bewahrt nur die
  wiederkehrende Kernhandlung und ist als Verb eindeutiger als `ABLASS`.
- **Einwort-Rivalen:** `ABLASS`; `ENTLEEREN`.

### `OKE = SPÜLEN` — behalten

- **Lehrregel:** Die ganze OKE-Karte erhält den Arbeitsruf `SPÜLEN`. Stelle,
  Wasser, Anzahl und Beendigung werden nicht hineingelesen.
- **Vollvorkommensdruck:** Acht Ereignisse liegen in sechs Datensätzen;
  einmal am Anfang und siebenmal innen. In `f81v.18` steht OKE zweimal direkt
  hintereinander, in `f83r.20` zweimal mit Abstand.
- **Stärkster Widerspruch:** Die direkte Doppelung widerspricht der lokalen
  Formulierung „einmal“, wenn dieses Zahlwort als Karteninhalt gelten sollte.
  Sie widerlegt nicht den kleineren Vorgang `SPÜLEN`; Zahl und Ziel müssen aus
  dem Ganzkontext verschwinden.
- **Einwort-Rivalen:** `WASCHEN`; `REINIGEN`.

### `CTHY = BEREIT` — behalten

- **Lehrregel:** Die ganze CTHY-Karte wird als Zustands- oder Schwellenruf
  `BEREIT` gelernt. Zubereitung, Gebrauch und das Satzwort *sobald* bleiben
  außerhalb.
- **Vollvorkommensdruck:** Sieben Ereignisse auf drei Seiten stehen sechsmal
  innen und einmal am Ende. Derselbe Wert kann eine lokale Schwelle markieren,
  ohne das physische Zeilenende zu behaupten.
- **Stärkster Widerspruch:** Auf `f10r.6` steht CTHY schon an Position 2 vor
  sieben weiteren Karten. `BEREIT` darf daher nicht „das ganze Verfahren ist
  fertig“ bedeuten, sondern höchstens einen lokalen Bereitschaftszustand.
- **Einwort-Rivalen:** `FERTIG`; `REIF`.

### `OKEEY = LAUWARM` — behalten

- **Lehrregel:** Die ganze OKEEY-Karte erhält nur den Zustandsruf `LAUWARM`.
  Temperieren, Halten und Arbeitsflüssigkeit gehören zur lokalen Expansion.
- **Vollvorkommensdruck:** Sieben biologische Ereignisse stehen einmal am
  Anfang und sechsmal innen, nie am Ende. Das Adjektiv verlangt keine feste
  Satzposition.
- **Stärkster Widerspruch:** Der lokale Default verbindet drei Behauptungen
  — Handlung, Gegenstand und Temperaturhaltung. Die Vorkommen unterscheiden
  nicht, welcher Teil wirklich zur Karte gehört. `LAUWARM` ist lediglich der
  kleinste einwortige Rest, keine gesicherte Temperaturangabe.
- **Einwort-Rivalen:** `WARM`; `TEMPERIEREN`.

### `CKHY = DURCH` — `VERBINDUNG` ersetzen

- **Lehrregel:** Die ganze CKHY-Karte wird als offene Durchgangsrelation
  `DURCH` gelernt. Was hindurchgeht und welcher Lauf verbunden ist, bleibt
  ungesagt.
- **Vollvorkommensdruck:** Alle vier Ereignisse auf zwei Seiten stehen innen.
  Der Relationswert passt zu dieser Stellung, ohne eine konkrete Vorrichtung
  zu erfinden.
- **Stärkster Widerspruch:** In `f82r.3` steht unmittelbar zuvor bereits eine
  andere Karte mit der lokalen Expansion „durch ein Tuch“. Durchgang ist also
  nicht exklusiv für CKHY, und `VERBINDUNG` würde die unbewiesenen Läufe zum
  Wortinhalt machen. `DURCH` bleibt bewusst klein und schwach.
- **Einwort-Rivalen:** `VERBINDUNG`; `DURCHLEITEN`.

### `OLOR = VORHER` — `VORIGES` ersetzen

- **Lehrregel:** Die ganze OLOR-Karte zeigt mit `VORHER` nur zurück. Es gibt
  kein stilles Objekt; Ansatz und Entnahme bleiben Teil der lokalen Expansion.
- **Vollvorkommensdruck:** Die zwei Ereignisse liegen auf zwei Seiten, einmal
  am Anfang und einmal innen. Ein bloßer Rückwärtsbezug kann beide Stellungen
  abdecken.
- **Stärkster Widerspruch:** Am Anfang von `f81v.7` muss der Bezug außerhalb
  des aktuellen Datensatzes liegen, während `f10r.8` einen inneren Vorgänger
  zulässt. Die Reichweite wechselt, und zwei Belege sind schwach. `VORIGES`
  versteckt zusätzlich ein ungenanntes Ding; `VORHER` tut das nicht.
- **Einwort-Rivalen:** `VORIGES`; `RÜCKBEZUG`.

## Werkstattregel und Fehleraudit

Der Lehrling erhält neun Vorzeigekarten. Er lernt Vorderseite und Tuple-ID als
unteilbare Einheit, spricht beim Rücklesen genau ein Merkwort und schlägt erst
danach die vollständige lokale Defaultlesung nach. Bei wechselnder sichtbarer
Oberfläche kopiert er die belegte Form aus dem Exemplar; das Merkwort darf
keine Schreibvariante erzeugen.

Die erwartbaren Fehler sind:

1. aus sichtbaren Ähnlichkeiten kleinere deutsche Bestandteile zu gewinnen;
2. `MASS` zu einer bestimmten Einheit oder Dosis auszubauen;
3. `KLAR` wieder mit Abschluss gleichzusetzen;
4. bei `VERWENDEN`, `ABLASSEN` oder `SPÜLEN` das lokale Objekt im Wort zu
   verstecken;
5. die Zahl „einmal“ in OKE zu legen, obwohl die Karte direkt doppelt steht;
6. `BEREIT` als Ende des ganzen Datensatzes zu behandeln;
7. `LAUWARM` um Flüssigkeit, Temperieren und Halten zu erweitern;
8. aus `DURCH` eine konkrete Leitungsanlage zu machen;
9. hinter `VORHER` automatisch einen Ansatz anzunehmen.

## Schluss

V51-R1 behält vier kurze V49-Merkwörter und ersetzt fünf durch eindeutigere,
kleinere Werkstattwerte. Keine lokale Expansion geht verloren. Die Revision
macht vor allem Abschluss, Gegenstand und Vorrichtung explizit zu Kontext und
nicht zum Inhalt der Ganzkarte.
