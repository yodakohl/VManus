# V18 R3 — technische Zustandsrekonstruktion der sechs Streitkarten

Date: 2026-08-21

Status: maximal abduktive Werkstatttheorie auf den zehn freigegebenen Seiten;
keine Entzifferungs- oder Lautwertbehauptung.

## Ergebnis

Ich lese die sechs Karten als ein kleines, einem Schreiber um 1420 lehrbares
Arbeitsregister. Das Register hält ein aktives Gefäß, eine Charge, eine
Arbeitsflüssigkeit, einen Weg und einen dargestellten Eigentümer fest. Eine
physische Zeile schließt die Anweisung nicht automatisch. Drei vorher zu stark
zusammengezogene Flüssigkeitskarten erhalten nun verschiedene ausführbare
Handlungen:

```text
OLCHEDY  = geklärte Oberflüssigkeit vorsichtig in den Empfänger abziehen
LCHEDY   = die ganze Flüssigkeit in das untere Empfangsgefäß ablassen
DCHEDY   = Gefäß oder Leitung mit einem einzelnen Durchgang auswaschen
```

Das ist die wichtigste V18-R3-Revision. Sie erklärt, weshalb alle drei Karten
trotz ähnlicher Schlussform im selben Nassprozess benötigt werden.

| Karte | gewählte konkrete Lesung | Konfidenz | V17-R3 |
|---|---|---:|---|
| `OKEEY/QOKEEY` | warmes Wasser in das aktive Gefäß geben | .74 | bestätigt die R3-Abweichung von V17-Auswahl |
| `LCHEDY` | die ganze Flüssigkeit in das untere Empfangsgefäß ablassen | .71 | präzisiert/revidiert „abkühlen“ bzw. „stehen lassen“ |
| `DCHEDY/SCHEDY/TCHEDY` | Gefäß oder Leitung einmal durchwaschen | .66 | bestätigt R3 gegen bloßes Beenden |
| `OLCHEDY/QOLCHEDY` | klare Oberflüssigkeit in den Empfänger abziehen | .78 | bestätigt R3 gegen Aufbewahren |
| `CHAR/DAR/SAR` | dann zum nächsten Arbeitsgang fortfahren | .86 | bestätigt R3 gegen „dieselbe Charge“ |
| `CHO/SHO` auf f56r | was die abgebildete Pflanze selbst betrifft | .59 | bestätigt den Seiten-Eigentümer gegen bloßes „danach“ |

Alle 31 Vorkommen sind in
`V18_R3_31_OCCURRENCE_RECONSTRUCTIONS.tsv` rekonstruiert. Jede Zeile enthält
das ganze Zielfeld, die ganze physische Zeile, Vor- und Folgezeile, alle drei
eingesetzten Rivalen sowie einen expliziten Vorher-Nachher-Prozessgraphen.
`V18_R3_COMPLETE_AFFECTED_PASSAGES.md` schreibt darüber hinaus jeden
betroffenen vollständigen Record/Artikel mit den sechs Entscheidungen neu.

## Ausführbare Rückleseregel

Ein Lehrling führt sechs einfache Registerschritte aus:

```text
OKEEY:
  nimm warmes Wasser aus dem bereitstehenden Wassergefäß;
  gib es zur aktiven Charge; Gefäß und Charge bleiben aktiv.

LCHEDY:
  öffne den unteren Ablauf;
  lasse den gesamten flüssigen Inhalt in das untere Empfangsgefäß;
  nicht nur den klaren oberen Teil.

DCHEDY:
  führe genau einen Waschgang durch das aktive Gefäß oder die aktive Leitung;
  danach ist der Weg für eine neue Charge bereit.

OLCHEDY:
  bewege das Gefäß nicht;
  ziehe nur die klare Oberflüssigkeit in den Empfänger ab;
  der Bodensatz bleibt zurück.

CHAR:
  ändere Stoff, Gefäß und Seiten-Eigentümer nicht;
  setze nur den Arbeitszeiger auf den folgenden Akt.

CHO auf f56r:
  setze den Eigentümer wieder auf die gezeichnete Pflanze;
  hänge den folgenden Teil oder die folgende Zubereitung an diese Pflanze.
```

So bleiben die Karten als Ganzkarten lehrbar. Der Schreiber muss keine
einzelnen EVA-Zeichen als Präfix, Stamm oder Suffix analysieren.

## Kartenentscheidungen

### 1. OKEEY/QOKEEY — warmes Wasser zugeben

Sieben Vorkommen bilden dieselbe Input-Handlung. Besonders stark sind:

- f82r.3: warmes Wasser zugeben → klar seihen → zweiter Kanal → Tuch →
  verbundene Leitungen;
- f83r.20: absetzen → aufbinden → warmes Wasser zugeben → örtlich spülen;
- f83r.25: temperiert baden → Gefäß füllen → warmes Wasser zugeben → spülen →
  rühren → unterer Auslass.

„Lauwarm halten“ kollidiert auf f82r.7 unmittelbar mit der schon ausdrücklich
als Warmhalten gelesenen Schlusskarte `SOLSHEDY`. Es verwischt außerdem die
bereits getrennten Karten für mäßiges Erwärmen, einmaliges Erhitzen und sanfte
Hitze. „Gründlich mischen“ dupliziert `CHEDY` und erscheint mehrfach neben
`QOKAL` oder `CHEDY`. Das warme Wasser ist zwar ein stilles Routineargument,
aber seine Zuführung ist in allen sieben Folgen eine unterschiedliche und
nützliche Operation.

### 2. LCHEDY — die ganze Flüssigkeit nach unten ablassen

Die acht Stellen teilen eine Richtungsökologie:

- f82r.23: vollständig eintauchen → ablassen → unteren Auslass schließen;
- f83r.11: oberen Kanal öffnen → einmal waschen → ablassen → unteren Auslass
  schließen;
- f83r.37: zweimal waschen → ablassen → neue Mischung einlassen → stehen
  lassen;
- f83r.41: oberen Kanal öffnen → ablassen → unteres Becken → gezeichneter Ort.

„Abkühlen“ ist auf f83r.6 vor der Anwendung attraktiv, erklärt aber die
Auslass- und Kanalfolgen nicht. „Im unteren Gefäß stehen lassen“ erklärt das
Gefäß, dupliziert jedoch `SHEDY/OLKEEDY` und macht die Folge „stehen lassen →
Mischung einlassen“ auf f83r.37 unnötig schwer. Das vollständige Ablassen ist
von `OLCHEDY` getrennt: hier bewegt sich die ganze Flüssigkeit, dort nur die
geklärte obere Fraktion.

### 3. DCHEDY/SCHEDY/TCHEDY — einmal durchwaschen

Vier Vorkommen sind mit einem einzelnen Waschgang lesbar:

- f81v.7: Maß → eingetauchter Teil → verbundene Leitungen → einmal
  durchwaschen;
- f82r.2: einmal durchwaschen → klare Oberflüssigkeit abziehen → neue Portion
  einfüllen;
- f83r.6: einmal durchwaschen → warmes Wasser eingießen → mischen → abziehen;
- f83r.16: einmal durchwaschen → einmal erhitzen → Person am Becken ansetzen.

„Seihen“ passt lokal, würde aber die dreimal belegte Tuchkarte `SHCKHEDY`
verdoppeln. „Behandlung beenden“ kann einen aus der Vorzeile getragenen Schritt
abschließen, erzeugt jedoch vor den neuen Lade- und Heizfolgen keinen
technischen Zustand. Der Waschgang erklärt zugleich die alleinstehenden
Felder: die vollständige Karte bezeichnet schon Handlung plus einen Durchgang.

### 4. OLCHEDY/QOLCHEDY — klare Oberflüssigkeit abziehen

Alle drei Vorkommen führen unmittelbar zu einer neuen Charge oder deren Weg:

- f81v.17: rühren → stehen lassen → klare Flüssigkeit abziehen → neue Portion
  einfüllen → Leitungen;
- f82r.2: durchwaschen → klare Flüssigkeit abziehen → neue Portion einfüllen;
- f83r.6: warmes Wasser → zwei Portionen mischen → klare Flüssigkeit abziehen
  → nächste Portion → rühren → temperieren.

Bloßes Aufbewahren oder Zurückhalten erklärt den stets unmittelbar folgenden
Neustart schlechter. Das Abziehen ist nicht Tuchseihen und nicht vollständiges
Ablassen. Die Arbeitskarte erhält deshalb einen präzisen Anteil: die klare
obere Flüssigkeit, während der Satz zurückbleibt.

### 5. CHAR/DAR/SAR — dann fortfahren

f82r.19 ist die stärkste Buchung:

```text
eine gemessene Portion eingeben
→ dann fortfahren
→ eine gemessene Portion eingeben
→ temperiert baden/erwärmen
→ klare Flüssigkeit abziehen
```

„Aus derselben Charge“ ist daneben möglich, scheitert aber in der Herbalfolge
„bedecktes Gefäß → Karte → gleichmäßig verbinden → pulverisieren“ und an den
beiden zeilenletzten Vorkommen. Die Karte schiebt ausschließlich den
Arbeitszeiger weiter; aktive Stoffe bleiben verfügbar. Damit kann sie am
Zeilenende wie ein Fortsetzungszeichen arbeiten, ohne dass die Aussage dort
enden muss.

### 6. CHO/SHO auf f56r — abgebildete Pflanze wieder als Eigentümer setzen

Die vier Stellen stehen vor unterer Wurzel, einer Wein-/Ernteangabe, trockenem
Blatt und frischer Honigzubereitung. „Blütenspitzen“ kann deshalb nicht eine
einheitliche Lesung sein. „Danach folgt“ ist dreimal flüssig, aber mitten in
„ihr Same ist — Karte — das trockene Blatt“ schwach. Eine einzige
Seiteneigentümer-Regel funktioniert sowohl am Feldanfang als auch medial:

```text
CHO/SHO = was diese gezeichnete Pflanze selbst betrifft
```

Das ist keine Behauptung, der Text sei nach dem Bild geschrieben worden, um
semantische Teile geometrisch zu codieren. Das Bild kann schlicht zuerst auf
dem Blatt gestanden haben und der Text musste den verfügbaren Raum benutzen.
Die Karte reaktiviert nur den Seitengegenstand in der Rücklesung.

## Vollständiger Prozess nach V18 R3

```text
nächste Portion nehmen
→ Portion ins Gefäß geben
→ zwei Portionen verbinden
→ warmes Wasser zugeben                         OKEEY
→ gleichmäßig rühren / temperiert erwärmen
→ stehen und Satz absinken lassen
→ klare Oberflüssigkeit vorsichtig abziehen     OLCHEDY
→ durch Tuch seihen, wenn verlangt
→ durch verbundene Leitungen führen
→ Gefäß oder Leitung einmal durchwaschen        DCHEDY
→ ganze Flüssigkeit ins untere Gefäß ablassen   LCHEDY
→ örtlich spülen oder anwenden
→ zum nächsten Akt fortfahren                   CHAR
```

Diese Kette ist konkreter als V17, weil „zurückhalten“, „beenden“ und ein
zweites „stehen lassen“ durch drei verschiedene beobachtbare Werkstatthandlungen
ersetzt werden.

## Historische Plausibilität, eng begrenzt

Der historische Vergleich identifiziert keine Karte. Er zeigt nur, dass der
rekonstruierte Arbeitsvorrat um 1420 nicht anachronistisch ist.

- Wellcome MS 709 ist eine spätfünfzehnteljahrhundertliche norditalienische
  Abschrift von Rupescissas um 1351–52 entstandenem Werk über medizinische
  Extraktion und Destillation von Wein, Pflanzen und Mineralien:
  <https://wellcomecollection.org/works/p6gbv6sn>.
- Ein italienischer medizinischer Sammelband des 14./15. Jahrhunderts zeigt
  einen Alembik aus zwei durch ein Rohr verbundenen Gefäßen; solche Geräte
  machen die Unterscheidung von aktivem Gefäß, Leitung und Empfänger
  zeitgenössisch plausibel:
  <https://histmed.collegeofphysicians.org/medieval-monday-19/>.
- Spätere ausführliche Destillationsrezepte benutzen genau die hier nur als
  generische Operationsfamilie benötigte Abfolge von sanfter Hitze,
  Stehenlassen, Abziehen klarer Flüssigkeit, erneutem Eingießen und Reinigen.
  Sie werden nicht als Beleg für eine konkrete Voynich-Bedeutung gewertet.

## Kosten und Schwächen

- `OKEEY` verlangt siebenmal stilles Wasser und meist ein stilles Gefäß. Das
  ist im Bild-/Routineellipsis-Modell erlaubt, bleibt aber eine echte Kostenstelle.
- `LCHEDY` ist auf f83r.6 als „abkühlen“ sprachlich glatter als „ablassen“.
  Die drei starken Kanal-/Auslassfolgen entscheiden trotzdem für Ablassen.
- `DCHEDY` am Anfang von f83r.16 benötigt einen aus der Vorzeile oder aus dem
  Apparat geerbten Waschgegenstand.
- `OLCHEDY` auf f83r.6 besitzt kein ausdrücklich vorausgehendes
  Sedimentationswort. Dort muss das Absetzen im geschlossenen Mischschritt
  enthalten oder sehr kurz sein.
- `CHO` bleibt seitenlokal und ist deshalb die schwächste der sechs
  Entscheidungen. Seine konkrete Defaultbedeutung bleibt dennoch fest und
  nicht leer.

## Dateien, Abdeckung und Versiegelung

- `V18_R3_SIX_CARD_DECISIONS.tsv`: 6 Karten × 3 eingefrorene Rivalen = 18
  bewertete Lesungen, einschließlich stiller Argumente und Reparaturkosten;
- `V18_R3_31_OCCURRENCE_RECONSTRUCTIONS.tsv`: 31/31 Vorkommen mit vollständigem
  Kontext und Prozessgraphen;
- `V18_R3_COMPLETE_AFFECTED_PASSAGES.md`: alle lokalen Fenster und sämtliche
  betroffenen vollständigen Records/Artikel;
- `build_v18_r3_process_reconstruction.py`: reproduzierbarer, bewachter Builder.

Es wurden ausschließlich die freigegebenen Seiten und die bestehende
V17-Arbeitsübersetzung benutzt. f84 und f84r blieben vollständig versiegelt.
