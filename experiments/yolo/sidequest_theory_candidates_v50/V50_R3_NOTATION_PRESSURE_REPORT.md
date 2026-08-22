# V50 R3 — Notationsdrucktest der sieben aktiven PAGE_HOST-Werte

Status: gebundene kreative Werkstattprüfung, keine Entzifferung und keine
Wortübersetzung des Manuskripts.

## Kurzurteil

Ich habe alle 93 festen Ereignisse der sieben aktiven V49-PAGE_HOST-Kandidaten
und alle 21 zugehörigen exakten Kartentypen geprüft. Das Ergebnis ist:

```text
OK    = SETZEN        BEHALTEN, ausschließlich formaler Operator
OT    = MARKIEREN     BEHALTEN, ausschließlich formaler Operator
L     = VERKNÜPFEN    BEHALTEN, ausschließlich formaler Operator
AL    = UNKNOWN
E     = UNKNOWN
OR    = UNKNOWN
CHEY  = UNKNOWN
```

`OK`, `OT` und `L` überleben gerade deshalb, weil ihre Werte keine
Gegenstände oder Vorgänge der lokalen deutschen Satzexpansion benennen. Sie
sind kurze deutsche Namen für bereits vorhandene formale Dispatchklassen.
`AL`, `E`, `OR` und `CHEY` lassen sich dagegen nicht eindeutig von fehlenden
Argumenten, Wrappern, Stellung oder der bereits kreativ eingesetzten
Lokaldeutung trennen.

## Abgrenzung und Zählregel

- Gezählt wurde ausschließlich nach der festen Spalte `page_host`, nie nach
  sichtbaren Teilstrings. Das ist wesentlich: etwa das sichtbare `chey` in
  `f83r.38` gehört zum PAGE_HOST `y` und ist kein `CHEY`-Vorkommen.
- Die 93 Ereignisse verteilen sich auf sechs Seiten: `f10r`, `f55v`, `f56r`,
  `f81v`, `f82r`, `f83r`. Auf `f11r` und den drei Kreis-Seiten liegt für diese
  sieben Hosts kein festes Vorkommen vor. Es gibt daher für keinen Kandidaten
  einen Kreisregister-Test.
- `FIRST`, `MIDDLE`, `LAST` und `SINGLE` wurden aus `event_index` relativ zum
  jeweiligen festen `page + locus + record` bestimmt.
- Die vollständigen deutschen Defaults dienen nur als Widerspruchstest. Sie
  sind laut V49 lokale kreative Ganzkartenexpansionen und keine Evidenz dafür,
  dass ihr Objekt oder ihre Handlung im PAGE_HOST steckt.
- `RIGHT`, `FRAME` und `CLOSE` bleiben eigene formale Schichten. Kein Wert darf
  einen dieser Beiträge still übernehmen.

## Vollständige Druckmatrix

| Host | Typen / Ereignisse | Register H / B / C | RIGHT-Verteilung | FRAME-Verteilung | CLOSE-Verteilung | Stellung F / M / L / S | V50 |
|---|---:|---:|---|---|---|---:|---|
| `OK` | 5 / 24 | 2 / 22 / 0 | `AIIN 9; AIN 7; AL 6; AIR 1; AR 1` | ohne 24 | nein 24 | 4 / 19 / 1 / 0 | `SETZEN` |
| `OT` | 3 / 7 | 0 / 7 / 0 | `AIIN 3; AL 3; AR 1` | ohne 7 | nein 7 | 0 / 5 / 2 / 0 | `MARKIEREN` |
| `L` | 5 / 26 | 4 / 22 / 0 | ohne 25; `AR 1` | `O 21`; ohne 5 | nein 22; ja 4 | 2 / 18 / 6 / 0 | `VERKNÜPFEN` |
| `AL` | 2 / 11 | 1 / 10 / 0 | ohne 11 | ohne 11 | nein 10; ja 1 | 1 / 7 / 3 / 0 | `UNKNOWN` |
| `E` | 2 / 14 | 0 / 14 / 0 | ohne 14 | ohne 12; `OT 2` | ja 14 | 0 / 11 / 3 / 0 | `UNKNOWN` |
| `OR` | 2 / 8 | 6 / 2 / 0 | ohne 7; `AIN 1` | ohne 8 | nein 8 | 2 / 5 / 1 / 0 | `UNKNOWN` |
| `CHEY` | 2 / 3 | 2 / 1 / 0 | ohne 3 | ohne 1; `OT 2` | nein 3 | 3 / 0 / 0 / 0 | `UNKNOWN` |

`H/B/C` bedeutet Herbal/Biological/Circle. Die Positionsbreite ist kein
Semantikbeweis; sie prüft nur, ob ein Kandidat an einen einzigen Platz gebunden
ist.

## Einzelprüfung

### `OK`: `SETZEN` bleibt formal

Die fünf festen Typen sind `SET(AIIN)` mit 9, `SET(AIN)` mit 7, `SET(AL)` mit
6 sowie `SET(AIR)` und `SET(AR)` mit je 1 Ereignis. Es gibt kein RIGHT-loses,
kein gerahmtes und kein geschlossenes `OK`. Die Stellung wechselt deutlich
zwischen Anfang, Mitte und einmal Ende.

Die lokalen Defaults reichen von einem neuen Maßposten über Mischen bis zum
Öffnen eines Laufes oder einer bezeichneten Stelle. Daher kann `SETZEN` keine
gemeinsame Sachhandlung sein. Als formaler Opcode ist es hingegen über fünf
RIGHT-Familien unverändert und hat stets ein explizites formales Argument.

Entscheidung: `SETZEN` behalten, Typ `FORMAL_OPERATOR`. Atomare Rivalen:
`EINTRAGEN`, `ZUWEISEN`.

### `OT`: `MARKIEREN` bleibt formal

Alle sieben Ereignisse sind explizit argumentiert: `MARK(AIIN)` 3-mal,
`MARK(AL)` 3-mal und `MARK(AR)` 1-mal. FRAME und CLOSE fehlen. `OT` steht nie
am Anfang, aber sowohl mitten als auch am Ende eines Locus.

Die lokalen Defaults wechseln zwischen Dauer, Richtung und Gebrauch eines
Ablaufs. Kein semantisches Verb deckt sie atomar. Der gemeinsame Nenner ist
nur, dass der Operand formal hervorgehoben wird. `MARKIEREN` bezeichnet daher
den Opcode, nicht die Art des markierten Gegenstands und nicht das historische
Wort.

Entscheidung: `MARKIEREN` behalten, Typ `FORMAL_OPERATOR`. Atomare Rivalen:
`BEZEICHNEN`, `MERKEN`.

### `L`: `VERKNÜPFEN` bleibt formal

Die fünf Typen und ihre 26 Ereignisse sind:

```text
FRAME_O(LINK)          19
LINK                    2
CLOSE(LINK)             2
CLOSE(FRAME_O(LINK))    2
LINK(AR)                1
```

Damit ist `LINK` sowohl mit als auch ohne FRAME, mit als auch ohne CLOSE und
einmal mit RIGHT `AR` belegt. Es erscheint am Anfang, in der Mitte und am Ende.
Die lokalen Defaults sind semantisch unvereinbar: Fortsetzung mit Vorigem,
bereitetes Öl, Ablauf schließen, Abziehen oder Kochen. Genau diese Streuung
erzwingt die formale Lesart.

Das RIGHT-lose `LINK` erhält ausdrücklich kein stilles Objekt. Im Decoder ist
`VERKNÜPFEN` nur der Name des vorhandenen nullstelligen Link-Tags; unbekannte
Endpunkte werden nicht als „vorige Mischung“, „Öl“ oder „Ablauf“ ergänzt.

Entscheidung: `VERKNÜPFEN` behalten, Typ `FORMAL_OPERATOR`. Atomare Rivalen:
`ANSCHLIESSEN`, `VERWEISEN`.

### `AL`: `ZU` fällt aus

Zehn Ereignisse tragen bloß `UNKNOWN_HOST[AL]`, eines trägt
`CLOSE(UNKNOWN_HOST[AL])`. Es gibt weder RIGHT noch FRAME. Die Stellung reicht
von Anfang über Mitte bis Ende, bietet also keine feste Zielposition.

`ZU` ist ohne Komplement keine ausführbare Relation. V49s Expansion „an die
bezeichnete Zielstelle“ liefert dieses Komplement nur aus dem lokalen Satz;
der einzige geschlossene Typ wird stattdessen als Wiederholung an einer
zweiten Öffnung expandiert. `ZIEL` wäre ein möglicher Registername, doch kein
formales Adressfeld oder Operand unterscheidet ihn von anderen Lesungen.

Entscheidung: `UNKNOWN`. Atomare Rivalen: `ZIEL`, `WEITER`.

### `E`: `BIS` fällt wegen vollständiger CLOSE-Konfundierung aus

Alle 14 Ereignisse sind geschlossen: 12-mal `CLOSE(UNKNOWN_HOST[E])`, 2-mal
`CLOSE(FRAME_OT(UNKNOWN_HOST[E]))`. Ein einziges ungeschlossenes `E` fehlt.
Zugleich stehen 11 dieser geschlossenen Karten mitten im Locus und nur 3 am
Ende. CLOSE ist daher keine schlichte Locus-Endposition, bleibt aber bei `E`
dennoch ausnahmslos vorhanden.

`BIS` benötigt außerdem eine Schwelle, für die kein RIGHT-Operand vorliegt.
„Bereitschaft“ und „Klarheit“ stammen aus den zwei lokalen Ganzkartenwerten.
Weder Grenze noch Warten lässt sich vom CLOSE-Beitrag unabhängig dem Host
zuweisen.

Entscheidung: `UNKNOWN`. Atomare Rivalen: `GRENZE`, `WARTEN`.

### `OR`: `ANSATZ` ist konsistent klingend, aber nicht identifiziert

Sieben Ereignisse gehören zu demselben nackten Typ `UNKNOWN_HOST[OR]`; nur ein
Ereignis hat zusätzlich RIGHT `AIN`. Die Stellung wechselt zwischen Anfang,
Mitte und Ende, FRAME und CLOSE fehlen. Sechs Ereignisse sind Herbal, zwei
Biological.

Die sieben Wiederholungen des einen exakten Typs wiederholen zwangsläufig auch
dessen eine Wörterbuchexpansion „bereitete Arbeitsflüssigkeit“; sie sind keine
sieben unabhängigen Bedeutungsproben. Der zweite Typ wird als Gebrauch einer
fertigen Flüssigkeit expandiert. `ANSATZ` ist damit möglich, aber gegenüber
einem anonymen Posten oder einer Mischung formal nicht unterscheidbar. Es gibt
auch keinen eigenen Opcode, den R3 stattdessen benennen könnte.

Entscheidung: `UNKNOWN`. Atomare Rivalen: `POSTEN`, `MISCHUNG`.

### `CHEY`: `ANTEIL` ist mit Anfangsstellung konfundiert

Das nackte `UNKNOWN_HOST[CHEY]` kommt einmal vor; das gerahmte
`FRAME_OT(UNKNOWN_HOST[CHEY])` zweimal. Alle drei Ereignisse stehen ausnahmslos
an erster Stelle. Die FRAME-Variation widerspricht `ANTEIL` nicht, doch es gibt
weder Positionswechsel noch RIGHT-Operand oder CLOSE-Kontrast.

Die beiden exakten Typen werden lokal als Wurzelteil beziehungsweise
bezeichneter Anteil expandiert. Daraus lässt sich Auswahl oder Teilmenge
ablesen, aber ebenso gut eine bloße Anfangs-/Einsatzkarte. Weil der Inhalt nicht
von der festen Startrolle getrennt werden kann, ist ein Inhaltsnomen zu stark.

Entscheidung: `UNKNOWN`. Atomare Rivalen: `AUSWAHL`, `TEIL`.

## Widerspruchs- und Abhängigkeitsledger

| Host | überlebender Invariant | Druckstelle | Auflösung |
|---|---|---|---|
| `OK` | `SET` über fünf RIGHT-Werte | Sachhandlungen der Defaults widersprechen einander | nur formales `SETZEN` |
| `OT` | `MARK` über drei RIGHT-Werte | Dauer, Richtung und Gebrauch sind keine gemeinsame Bedeutung | nur formales `MARKIEREN` |
| `L` | `LINK` über FRAME/CLOSE/Stellung | Sachobjekte und Handlungen wechseln; Endpunkte bleiben opak | nur formales `VERKNÜPFEN` |
| `AL` | kein Opcode | `ZU` hat keinen Operand; der geschlossene Zweittyp wechselt die Expansion | `UNKNOWN` |
| `E` | kein vom Wrapper gelöster Hostwert | 14/14 mit CLOSE; Schwelle fehlt | `UNKNOWN` |
| `OR` | zwei formal opake Typen | sieben Wiederholungen stammen aus nur einem Typ; Inhalt nicht unterscheidbar | `UNKNOWN` |
| `CHEY` | FRAME-unabhängig in nur drei Fällen | 3/3 am Anfang; Inhalt gegen Startrolle nicht testbar | `UNKNOWN` |

## Ausführbare Kodier- und Dekodierregel

Die Regel operiert nur auf der bereits festen formalen Formel. Sie behauptet
keine produktive Morphologie und keine historische Bedeutung.

```text
D(SET(x))                 = SETZEN[x]
D(MARK(x))                = MARKIEREN[x]
D(LINK)                   = VERKNÜPFEN
D(LINK(x))                = VERKNÜPFEN[x]
D(FRAME_t(z))             = FRAME_t(D(z))
D(CLOSE(z))               = CLOSE(D(z))
D(UNKNOWN_HOST[h])        = UNKNOWN[h]
```

Der inverse Kodierer darf nur einen bereits belegten exakten Typ wählen. Er
darf aus den beobachteten RIGHT-, FRAME- und CLOSE-Werten kein kartesisches
Produkt neuer Karten erzeugen. `VERKNÜPFEN` ohne Argument bleibt ein
nullstelliges formales Tag; es erhält kein erfundenes Ziel.

Beispielbuchungen aus den festen Ereignissen:

```text
qokar     SET(AR)                         -> SETZEN[AR]
sotaiin   MARK(AIIN)                      -> MARKIEREN[AIIN]
oldy      CLOSE(FRAME_O(LINK))            -> CLOSE(FRAME_O(VERKNÜPFEN))
otedy     CLOSE(FRAME_OT(UNKNOWN_HOST[E]))-> CLOSE(FRAME_OT(UNKNOWN[E]))
otchey    FRAME_OT(UNKNOWN_HOST[CHEY])     -> FRAME_OT(UNKNOWN[CHEY])
orain     UNKNOWN_HOST[OR] + ARG_AIN       -> UNKNOWN[OR] + ARG_AIN
```

Zwei kurze belegte Folgen zeigen den Nutzen der Trennung:

```text
f82r.7:  MARKIEREN[AIIN] ; SETZEN[AR] ; CLOSE(UNKNOWN[E])
f83r.22: MARKIEREN[AIIN] ; CLOSE(FRAME_OT(UNKNOWN[E])) ; CLOSE(VERKNÜPFEN)
```

Diese Folgen sind als Notationsbäume ausführbar, ohne „Dauer“, „Ablauf“,
„Klarheit“ oder einen anderen stillen Gegenstand in einen Host zu schreiben.

## Harte Ausfallbedingungen

Das R3-Modell scheitert und darf nicht erweitert werden, wenn man

1. einen neuen Host×RIGHT×FRAME×CLOSE-Typ aus den beobachteten Teilen erzeugt;
2. `E` ohne einen künftigen ungeschlossenen Kontrast wieder als Grenze liest;
3. `CHEY` ohne Positionswechsel oder unabhängigen Inhaltstest als Anteil liest;
4. `AL` ohne sichtbaren/formalen Zieloperanden als Relation ausführt;
5. `OR` allein aus den wiederholten kreativen Defaults zum Stoffnamen macht;
6. sichtbare Teilstrings statt der festen PAGE_HOST-Identität zählt; oder
7. die Ergebnisse auf die hier unbelegten Kreis-Seiten überträgt.

Damit ist V50 für R3 vollständig: drei formale Merkwörter bleiben, vier
semantische Arbeitsglossen werden auf `UNKNOWN` zurückgesetzt.
