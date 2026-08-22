# V51 R3 — Notationsdrucktest der neun wiederkehrenden Ganzkarten

Status: gebundene kreative Werkstattprüfung. Die Werte sind technische
Merkwörter für exakte Kartenidentitäten, keine gelesenen Wörter.

## Kurzurteil

Alle 70 V49-Ereignisse der neun wiederkehrenden exakten Ganzkarten wurden
geprüft. R3 setzt:

```text
AIIN   = MASS        behalten; schwaches technisches Parametermerkwort
EY     = UNKNOWN
OKY    = GEBRAUCH   ersetzt NUTZEN; schwaches technisches Handlungsmerkwort
LCHE   = UNKNOWN
OKE    = UNKNOWN
CTHY   = BEREIT     behalten; schwaches technisches Zustandsmerkwort
OKEEY  = WÄRME      ersetzt LAUWARM; schwaches technisches Parametermerkwort
CKHY   = UNKNOWN
OLOR   = BEZUG      ersetzt VORIGES; schwaches formales Verweismerkwort
```

`MASS` und `BEZUG` sind dabei am ehesten formal: Sie nennen einen anonymen
Registerparameter beziehungsweise einen Verweis, nicht einen Stoff oder eine
Handlung. `GEBRAUCH`, `BEREIT` und `WÄRME` bleiben bloße technische
Werkstattmerker. Keines der fünf Wörter ist als Quelllexem identifiziert.

## Exakte Auswahlregel

- Die Einheit ist der feste `joint_tuple_id` der ganzen Karte. Sichtbare
  Varianten wie `aiin`, `daiin`, `saiin`, `okeey` oder `qokeey` werden weder
  zerlegt noch mit einer freien Bedeutung versehen.
- Die V49-Ganzkartenexpansion wird als ein bereits gewählter lokaler Satz
  behandelt. Ihre Wiederholung bei demselben exakten Typ ist keine neue
  unabhängige Bedeutungsprobe.
- Direkte Nachbarn wurden innerhalb desselben festen
  `page + locus + record` über `event_index ± 1` gezählt. `BOUNDARY` bedeutet,
  dass auf dieser Seite kein Ereignis im Locus steht.
- Stellung wurde relativ zu demselben Locus als `FIRST`, `MIDDLE`, `LAST` oder
  `SINGLE` gezählt.
- Keine der neun Karten trägt ein eigenes RIGHT oder FRAME. Nur `LCHE` und
  `OKE` tragen ausnahmslos den separaten Wrapper `CLOSE`.

## Vollständige Ereignismatrix

| Karte | Ereignisse / Seiten | H / B / C | Stellung F / M / L / S | CLOSE | verschiedene linke / rechte Nachbarn | stärkste Nachbarhäufung | V51 |
|---|---:|---:|---:|---:|---:|---|---|
| `AIIN` | 20 / 7 | 9 / 11 / 0 | 4 / 11 / 5 / 0 | 0 | 13 / 13 | linker Rand 4; rechter Rand 5 | `MASS` |
| `EY` | 4 / 3 | 1 / 3 / 0 | 1 / 2 / 1 / 0 | 0 | 4 / 4 | keine Wiederholung | `UNKNOWN` |
| `OKY` | 10 / 5 | 3 / 7 / 0 | 0 / 7 / 3 / 0 | 0 | 9 / 7 | links `OKEEY` 2; rechts Rand 3 | `GEBRAUCH` |
| `LCHE` | 8 / 2 | 0 / 8 / 0 | 0 / 7 / 1 / 0 | 8 | 8 / 7 | rechts `OK` 2 | `UNKNOWN` |
| `OKE` | 8 / 2 | 0 / 8 / 0 | 1 / 7 / 0 / 0 | 8 | 7 / 7 | links `OKEEY` 2; rechts `OK` 2 | `UNKNOWN` |
| `CTHY` | 7 / 3 | 3 / 4 / 0 | 0 / 6 / 1 / 0 | 0 | 6 / 7 | links `OK` 2 | `BEREIT` |
| `OKEEY` | 7 / 3 | 0 / 7 / 0 | 1 / 6 / 0 / 0 | 0 | 7 / 5 | rechts `OKE` 2 und `OKY` 2 | `WÄRME` |
| `CKHY` | 4 / 2 | 0 / 4 / 0 | 0 / 4 / 0 / 0 | 0 | 4 / 4 | keine Wiederholung | `UNKNOWN` |
| `OLOR` | 2 / 2 | 1 / 1 / 0 | 1 / 1 / 0 / 0 | 0 | 2 / 1 | rechts `L` 2 | `BEZUG` |

`H/B/C` bedeutet Herbal/Biological/Circle. Keine der neun Karten kommt auf den
drei festen Kreis-Seiten vor; dort ist kein Registertransfer prüfbar.

## Einzelprüfung

### `AIIN`: `MASS` bleibt als Parametermerker

`AIIN` hat mit 20 Ereignissen auf sieben Seiten die breiteste Probe. Es steht
am Anfang, in der Mitte und am Ende und ist mit 9 Herbal- und 11
Biological-Ereignissen als einzige Karte nahezu registerausgeglichen. Dreizehn
verschiedene linke und dreizehn verschiedene rechte Nachbarwerte schließen
eine feste Satzposition oder feste Partnerkarte aus.

Das spricht nicht für ein gelesenes Maßwort, wohl aber für einen häufig
einsetzbaren technischen Parameterplatz. `MASS` bleibt deshalb nur als
Registermerker: keine Einheit, Zahl, Portion oder Substanz wird im Wort
mitgeführt.

Stärkster Widerspruch: Es gibt weder eine feste Einheit noch einen festen
Zahlen-, RIGHT- oder Nachbarträger; `MASS` ist gegenüber einem allgemeinen
Wert nicht identifiziert.

Entscheidung: `MASS`. Einwort-Rivalen: `WERT`, `MENGE`.

### `EY`: `FERTIG` fällt aus

Die vier Ereignisse besetzen einmal Anfang, zweimal Mitte und einmal Ende.
Keines trägt CLOSE. Alle vier linken und alle vier rechten Nachbarn sind
verschieden. Damit funktioniert `EY` nicht als wiederholbares Commit- oder
Abschlusszeichen.

Ein Zustandswort könnte theoretisch auch am Anfang oder mitten stehen, doch die
feste Ganzkartenexpansion „bis die Flüssigkeit klar abläuft“ liefert allein
keine Entscheidung zwischen fertig, klar, Grenze oder einem opaken Status.

Stärkster Widerspruch: drei von vier Ereignissen sind nicht am Locusende, und
es fehlt jeder CLOSE-Kontrast.

Entscheidung: `UNKNOWN`. Einwort-Rivalen: `FERTIG`, `KLAR`.

### `OKY`: `NUTZEN` wird zu `GEBRAUCH`

`OKY` steht nie am Anfang, siebenmal in der Mitte und dreimal am Ende. Zweimal
folgt es auf `OKEEY`; dreimal endet der Locus nach ihm. Die übrigen acht linken
beziehungsweise vier nichtterminalen rechten Kontexte streuen breit. Ein
einmaliger Endgebrauch ist daher zu eng.

`GEBRAUCH` ist als technisches Ganzkartenmerkwort kleiner als die lokale
Expansion „die aktive Portion verwenden“: Es setzt weder eine aktive Portion
noch einen Imperativ oder einen endgültigen Anwendungsschritt in die Karte.
Der Wert ist ein schwacher Inhaltsmerker, kein formaler Opcode.

Stärkster Widerspruch: sieben von zehn Ereignissen sind nicht terminal, und
neun verschiedene linke Nachbartypen liefern keinen festen Gegenstand des
Gebrauchs.

Entscheidung: `GEBRAUCH`. Einwort-Rivalen: `NUTZEN`, `EINSATZ`.

### `LCHE`: `ABLASS` fällt wegen CLOSE-Konfundierung aus

Alle acht Ereignisse sind `CLOSE(UNKNOWN_HOST[LCHE])`, alle liegen im
Biological-Register. Sieben stehen mitten im Locus und nur eines am Ende. Alle
acht linken Nachbarn sind verschieden; rechts wiederholt sich nur `OK` zweimal.

Der Wrapper ist also kein bloßes Locusende, aber von `LCHE` dennoch nie
getrennt. Die Handlung Ablassen, das untere Gefäß und die verbrauchte
Flüssigkeit stammen vollständig aus der lokalen Satzexpansion.

Stärkster Widerspruch: 8/8 CLOSE ohne offene Gegenform; zugleich sind 7/8
Karten nicht terminal.

Entscheidung: `UNKNOWN`. Einwort-Rivalen: `ABLASS`, `AUSLAUF`.

### `OKE`: `SPÜLEN` fällt ebenfalls wegen CLOSE-Konfundierung aus

Auch `OKE` ist in allen acht Ereignissen geschlossen und ausschließlich
Biological. Es steht einmal am Anfang, siebenmal in der Mitte und niemals am
Ende. In `f81v.18` wiederholt sich `OKE` sogar unmittelbar. Links häuft sich
nur `OKEEY` zweimal, rechts nur `OK` zweimal.

Damit lässt sich ein eigener Spülvorgang nicht von einem gelernten
geschlossenen Kartentyp unterscheiden. Das in V49 eingesetzte „einmal“ ist
besonders nicht atomar und darf aus der Doppelung nicht wegdiskutiert werden.

Stärkster Widerspruch: 8/8 CLOSE, 0/8 terminal und eine direkte
`OKE`–`OKE`-Doppelung.

Entscheidung: `UNKNOWN`. Einwort-Rivalen: `SPÜLEN`, `WASCHEN`.

### `CTHY`: `BEREIT` bleibt als Zustandsmerker

Die sieben Ereignisse teilen sich auf 3 Herbal und 4 Biological. `CTHY` steht
nie am Anfang, sechsmal in der Mitte und einmal am Ende; CLOSE fehlt. Zweimal
geht `OK` voraus, doch alle sieben rechten Nachbarn sind verschieden.

Gerade die verschiedenen Folgekarten sind mit einem allgemeinen
Bereitschaftsstatus vereinbar: Der Merker kann unterschiedliche nächste
Einträge freigeben. Er bezeichnet aber keine nachgewiesene Gate-Operation und
keine bestimmte fertige Zubereitung.

Stärkster Widerspruch: Ein Ereignis ist terminal und alle sieben Nachfolger
sind verschieden; eine notwendige Freigabewirkung ist daher nicht gezeigt.

Entscheidung: `BEREIT`. Einwort-Rivalen: `FERTIG`, `FREIGABE`.

### `OKEEY`: `LAUWARM` wird zu `WÄRME`

Alle sieben Ereignisse liegen im Biological-Register. Eines steht am Anfang,
sechs in der Mitte, keines am Ende. Sämtliche sieben linken Nachbarn sind
verschieden. Rechts folgen je zweimal `OKE` und `OKY`, in drei weiteren Fällen
andere Typen.

Das Muster ist mit einem Temperaturparameter vor weiteren Arbeitsschritten
vereinbar, bestimmt aber keinen Wärmegrad. `WÄRME` entfernt daher die in V49
stille Spezifikation „lauwarm“ und die ganze Handlung „temperieren und halten“.
Es bleibt ein schwacher technischer Parametermerker.

Stärkster Widerspruch: nur ein Register, sieben verschiedene Vorgänger und
kein formaler Grad- oder Einheitenträger.

Entscheidung: `WÄRME`. Einwort-Rivalen: `LAUWARM`, `TEMPERATUR`.

### `CKHY`: `VERBINDUNG` fällt aus

Alle vier Ereignisse sind Biological und stehen mitten im Locus. Jeder linke
und jeder rechte Nachbar ist verschieden. Nur einmal folgt der in V50 bereits
formal definierte `L`-Operator.

`VERBINDUNG` würde damit ohne eigene formale Signatur die Funktion von `L`
doppeln oder die in der lokalen Expansion genannten Läufe still zum Objekt
machen. Weder eine Leitung noch eine Kopplung wird durch Stellung oder Nachbar
stabilisiert.

Stärkster Widerspruch: 4/4 auf zwei Biological-Seiten, 4/4 verschiedene
Nachbarpaare und keine wiederkehrende Link-Kombination.

Entscheidung: `UNKNOWN`. Einwort-Rivalen: `VERBINDUNG`, `LEITUNG`.

### `OLOR`: `VORIGES` wird zum formalen `BEZUG`

`OLOR` kommt nur zweimal vor, einmal Herbal und einmal Biological. Einmal steht
es am Locusanfang, einmal in der Mitte. In beiden Fällen folgt unmittelbar der
formale `L=VERKNÜPFEN`-Operator; in `f10r.8` steht zusätzlich auch davor `L`.

Das erlaubt den kleinen formalen Merker `BEZUG`. Er behauptet weder, dass der
Bezug rückwärts läuft, noch welches frühere Objekt gemeint ist. `VORIGES`
brauchte dagegen ein stilles Bezugswort und eine nicht gezeigte Richtung.

Stärkster Widerspruch: nur zwei Ereignisse; das perfekte `OLOR -> L`-Muster hat
keine unabhängige dritte Probe, und das initiale Vorkommen könnte nur auf einen
außerhalb des Locus liegenden Zustand zeigen.

Entscheidung: `BEZUG`, ausschließlich formaler Lead. Einwort-Rivalen:
`VORIGES`, `RÜCKVERWEIS`.

## Kompakter Widerspruchsledger

| Karte | stärkster Druck | formaler Status | Auflösung |
|---|---|---|---|
| `AIIN` | keine Einheit oder fester Partner | allgemeiner Parameterlead | `MASS` |
| `EY` | kein CLOSE; alle Stellungen und Nachbarn | kein Commit nachweisbar | `UNKNOWN` |
| `OKY` | 7/10 nichtterminal; Gegenstand wechselt | kein Opcode | `GEBRAUCH` |
| `LCHE` | 8/8 CLOSE; nur Biological | vom Wrapper untrennbar | `UNKNOWN` |
| `OKE` | 8/8 CLOSE, 0/8 terminal, direkte Doppelung | vom Wrapper untrennbar | `UNKNOWN` |
| `CTHY` | alle sieben Nachfolger verschieden | schwacher Statuslead | `BEREIT` |
| `OKEEY` | Grad und Einheit fehlen; nur Biological | schwacher Parameterlead | `WÄRME` |
| `CKHY` | keine Nachbarwiederholung; Konkurrenz zu `L` | kein Link-Opcode | `UNKNOWN` |
| `OLOR` | nur zwei Belege | schwacher Referenzlead | `BEZUG` |

## Ausführbare Ganzkartenregel

Der Decoder schlägt ausschließlich den exakten gemeinsamen Tuple-Schlüssel
nach. Er durchsucht oder zerlegt die sichtbare Karte nicht:

```text
D(2f1c5e56e8f0ff459065) = MASS
D(276a7c2d74d1143446f4) = GEBRAUCH
D(e0b630cb1b5df5e7105b) = BEREIT
D(0275fbf14e07935b0a45) = WÄRME
D(dec401773c1f0347793d) = BEZUG
D(b5df9126607030b95175) = UNKNOWN[EY]
D(de7321bface5628e35d6) = CLOSE(UNKNOWN[LCHE])
D(7db18b2f0fb7ed0fcfd3) = CLOSE(UNKNOWN[OKE])
D(2cc8bb3c2af19607888f) = UNKNOWN[CKHY]
```

Der Kodierer darf umgekehrt nur einen bereits belegten exakten Tuple-Schlüssel
aufrufen. Er darf aus `q`, `ch`, `s`, `d`, `t`, `dy` oder sichtbaren
Teilfolgen keine neuen Karten bauen und darf keine Oberflächenvariante frei
wählen.

Drei feste Folgen zeigen die knappe Arbeitsweise:

```text
f10r.8:  VERKNÜPFEN ; BEZUG ; VERKNÜPFEN ; MASS
f83r.20: WÄRME ; CLOSE(UNKNOWN[OKE]) ; ... ;
          CLOSE(UNKNOWN[OKE]) ; GEBRAUCH ; MASS
f82r.7:  WÄRME ; GEBRAUCH ; ... ; UNKNOWN[EY]
```

Die Regel ist als Registerumschrift ausführbar. Sie ist keine Übersetzung der
lokalen Sätze und lizenziert keine ungesehene Kombination.

## Ausfallbedingungen

Die R3-Lesung darf nicht fortgeschrieben werden, wenn man

1. eine sichtbare Oberfläche in angebliche Bestandteile zerlegt;
2. `LCHE` oder `OKE` ohne offenen Gegenbeleg vom CLOSE-Wrapper trennt;
3. `MASS`, `WÄRME` oder `BEREIT` zu Einheit, Grad oder konkretem Stoff
   erweitert;
4. `GEBRAUCH` um eine stille aktive Portion oder Endanwendung ergänzt;
5. aus zwei `OLOR -> L`-Fällen einen produktiven Rückverweisoperator macht;
6. `CKHY` neben `L` ohne unterscheidbare Signatur als zweite Verbindung liest;
7. die fünf Merkwörter auf die hier unbelegten Kreis-Seiten überträgt.

Damit sind alle 70 festen Ereignisse erfasst, ohne die neun Ganzkarten sichtbar
zu zerlegen oder lokale Prosa in ihre Werte einzuschmuggeln.
