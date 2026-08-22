# V44 R4 — Karten-zu-PAGE_HOST-Bedeutungsaudit

## Verfahren

Der Korrektor verbindet ausschließlich bereits vorhandene Artefakte:

- 173 deutsche V43-Prosakartendefaults;
- die f84-freie GDT327-Joint-Tuple-Atlaszuordnung;
- die deterministische GDT327-Hashregel für PAGE_HOST;
- die vorhandene f84-freie GDT278-Hostschreibweise.

Keine neue Zeichenfolge und keine neue Seite wurde semantisch durchsucht. Der
vollständige Join steht in `V44_R4_CARD_TO_HOST_MEANINGS.tsv`.

## Zentrale Rechnung

Die 173 bedeutungsbelegten V43-Karten verteilen sich auf **136 verschiedene
PAGE_HOSTs**. Das ist bereits ein starkes Warnsignal gegen ein kleines
klassisches Stammlexikon: Die meisten Hosts besitzen in unserem Zehnseiten-
Panel nur eine einzige bedeutungsbelegte Joint-Tuple-Karte.

Eine einzelne scheinbar saubere Zuordnung wie

```text
ey -> „bis die Flüssigkeit klar abläuft“
```

ist deshalb kein Paradigma. Korrekt lautet sie:

```text
PAGE_HOST ey
  + eine bestimmte formale Koordinate
  + Renderer shey/cheey
  -> eine V43-Karte mit dem Default „bis die Flüssigkeit klar abläuft“
```

Ob andere `ey`-Koordinaten denselben Bedeutungsraum tragen, wurde in V42 nicht
gezeigt.

## Beste wirkliche Mehrkarten-Kandidaten

### 1. `chor` — SAMMEL-/JAHRESZEITRAHMEN

- `otchor/qotchor`: vor der Blüte gesammelt;
- `chochor`: Pflanze im Frühjahr sammeln.

Gemeinsame Schnittmenge: **Sammelzeit beziehungsweise Beschaffung des
Bildbesitzers**. Zwei Karten, drei Panelereignisse. Das ist der sauberste
inhaltliche Stammkandidat, aber noch klein.

### 2. `ch` — KLÄREN/ABZIEHEN

- `otchdy`: abziehen und Schritt schließen;
- `dchdy`: klar seihen und Schritt schließen.

Gemeinsame Schnittmenge: **Flüssigkeit trennen/klären und die Zelle
abschließen**. Zwei Karten, zwei Ereignisse.

### 3. `chy` — WARME ZUBEREITUNG/ANWENDUNG

- `chedchy`: erwärmtes Wasser eingießen;
- `qotchy`: warmen Blattumschlag bereiten.

Gemeinsame Schnittmenge: **warmes Medium für eine Anwendung bereitstellen**.
Zwei Karten, zwei Ereignisse.

### 4. `or` — BEREITETE ARBEITSFLÜSSIGKEIT/OUTPUT

- `chor/or/shor/sor`: bereitete Arbeitsflüssigkeit;
- `orain`: fertige Flüssigkeit frisch gebrauchen.

Gemeinsame Schnittmenge: **bereiteter flüssiger Arbeitsbestand**. Zwei Karten,
acht Ereignisse. Das ist der stärkste Kandidat nach Vorkommenszahl.

### 5. `chey` — AUSGEWÄHLTER MATERIALANTEIL

- `dchey`: faserige untere Wurzel nehmen;
- `otchey`: bezeichneten Anteil nehmen.

Gemeinsame Schnittmenge: **einen bestimmten Material-/Pflanzenteil
selektieren**. Zwei Karten, drei Ereignisse.

### 6. `olk` — TRANSFERHILFSMITTEL/EMPFÄNGER

- `solkaiin`: durch ein Tuch;
- `olkain/qolkain`: unteres Becken.

Gemeinsame Schnittmenge: **Transferpfad oder empfangende Apparatur**. Formal
interessant, semantisch noch breit.

## Mögliche grammatische Achsen, keine guten Inhaltsstämme

### `ok`

Fünf V43-Karten: abgemessenen Anteil zugeben, zwei Anteile mischen, örtliche
Stelle, oberen Lauf öffnen, nächsten Messposten beginnen. Gemeinsamer Nenner
ist höchstens **aktiven Arbeitsgang instanziieren/ausführen**. Das sieht eher
wie eine produktive Konstruktionsachse als wie ein Gegenstandsstamm aus.

### `ot`

Dauer wie zuvor, unterer Ablauf, unteren Ablauf benutzen. Möglicher Nenner:
**markierter Bezug/gewählte Route oder Parameter**. Zu heterogen für eine
konkrete lexikalische Bedeutung.

### `l`

Voransatz, Öl, Abziehen, unteren Ablauf schließen, Kochen und Zellschluss.
Keine belastbare Inhaltsintersection. Wahrscheinlicher Verbindungs-,
Empfänger- oder Schlussachse, deren genaue Funktion erst mit der Koordinate
entsteht.

### `y`

Aktiver Posten, gleichmäßiges Rühren und feucht-schattiger Standort teilen
keinen ehrlichen konkreten Wert. `y = current item` ist daher nicht als
allgemeine Stammbedeutung haltbar.

### `o`

Folgender Pflanzenteil, Weißwein und Ziehen bis klar. Das ist im aktuellen
Wörterbuch keine semantisch kohärente Stammfamilie.

## Saubere Einzelkarten, aber noch keine Stammfamilien

| PAGE_HOST | einzige V43-Karte im Panel | aktueller Default |
|---|---|---|
| `aiin` | `aiin/chaiin/daiin/saiin/taiin` | vorgeschriebenes Maß |
| `ey` | `shey/cheey` | bis Flüssigkeit klar abläuft; besser breiter Endzustand |
| `ar` | `char/dar/sar` | daraus, aus demselben Ansatz |
| `cthy` | `cthy/shcthy/checthy` | gebrauchsfertig |
| `oky` | `oky/qoky/choky` | aktiven Posten verwenden |
| `okeey` | `okeey/qokeey` | Arbeitsflüssigkeit lauwarm halten |
| `oke` | `qokedy` | einmal spülen und schließen |
| `lche` | `lchedy` | unten ablaufen lassen und schließen |
| `ckhy` | `ckhy/shckhy` | durch verbundene Läufe |

Diese Zuordnungen sind gute **Kartenwerte**, aber keine nachgewiesenen
Stammbedeutungen: Innerhalb des Panels fehlt eine zweite Koordinate desselben
Hosts, die dieselbe semantische Schnittmenge unabhängig bestätigt.

## R4-Urteil

Die beste vorläufige Hierarchie ist:

```text
wahrscheinliche Inhaltsfamilien:
  chor  -> Sammelzeit/Beschaffung
  or    -> bereitete Arbeitsflüssigkeit
  chey  -> ausgewählter Materialanteil
  ch    -> Klären/Abziehen
  chy   -> warme Zubereitung/Anwendung

wahrscheinliche Konstruktionsachsen:
  ok    -> Arbeitsgang instanziieren/ausführen
  ot    -> markierter Bezug/Route/Parameter
  l     -> Verbindung/Empfänger/Schluss

aktuell widerlegte einfache Stammglossen:
  y = aktiver Posten
  o = ein bestimmtes Material

Einzelkarten ohne Paradigmenbeweis:
  aiin, ey, ar, cthy, oky, okeey, oke, lche, ckhy
```

Das ist eine explorative Stammhypothese auf den festen zehn Seiten. Sie weist
keine Lautung, Sprache, Morphologie oder historische Wortbedeutung nach. f84
und f84r blieben versiegelt.
