# V56 R3 — Exakter Herbal↔Bio-Prompttransfer

Status: technische Sidequest-Arbeitsanalyse, keine Entzifferung. Geprüft wurden
nur vollständige exakte Kartenoberflächen und vollständige exakte formale
Konstruktionen auf `f10r`, `f11r`, `f55v`, `f56r`, `f81v`, `f82r` und
`f83r`. PAGE_HOST, Wrapperähnlichkeit, Teilstrings und sichtbare
Segmentierung waren keine Features. `f84` und `f84r` wurden nicht geöffnet.

## Ergebnis

Die 17-zeilige Matrix in `V56_R3_HERBAL_BIO_TRANSFER_MATRIX.tsv` lässt nur
vier generische Promptregeln passieren:

```text
daiin                 -> PROMPT_LOAD(STANDARD_PARAMETER?)
SET(<ARG_AIIN>)       -> CTRL_SET(STANDARD_SLOT)
SET(<ARG_AL>)         -> CTRL_SET(LOCAL_RELATION_SLOT)
FRAME_O(LINK)         -> CTRL_LINK(ACTIVE_STATE)
```

Nur `daiin` trägt dabei überhaupt einen schwachen Quellenprompt. Die anderen
drei Regeln sind formale Steuerwerte, keine Kartenbedeutungen. „Maß“ ist bei
`daiin` absichtlich zu `STANDARD_PARAMETER?` verbreitert: Herbal darf lokal
eine Dosis oder Stoffmenge, Bio eine Charge, Dauer oder Einstellung einsetzen.

Entscheidungsbilanz:

| Entscheidung | Matrixzeilen | Bedeutung |
|---|---:|---|
| KEEP | 4 | eine schwache Vollkartenphrase plus drei formale Kontrollen |
| LOCAL_ONLY | 10 | exakte Karten geteilt, Inhalt aber nur registerlokal belastbar |
| WITHDRAW | 3 | CLOSE-konfundierter Inhalt oder keine gemeinsame Vollkarte |

## Ausführbarer Decoder

```text
decode(event, register, local_state):
    require exact visible surface and exact complete formal tree

    if formal_tree == SET(<ARG_AIIN>):
        emit CTRL_SET(STANDARD_SLOT)
    elif formal_tree == SET(<ARG_AL>):
        emit CTRL_SET(LOCAL_RELATION_SLOT)
    elif formal_tree == FRAME_O(LINK):
        emit CTRL_LINK(ACTIVE_STATE)
    elif exact_surface == "daiin":
        emit PROMPT_LOAD(STANDARD_PARAMETER?)
    else:
        emit NO_CROSS_REGISTER_PROMPT

    if root(formal_tree) == CLOSE:
        annotate STRUCT_COMMIT separately

    fill omitted objects only after decoding:
        Herbal -> pictured part / preparation / dose / use
        Bio    -> basin / charge / flow / station / duration
```

Die Reihenfolge verhindert, dass `ARG_AIIN` das Merkwort von `daiin` erbt.
Ein RIGHT-Wert bleibt ein formaler Slot. `CLOSE` emittiert niemals „beende“,
„bis“, „fertig“, „kochen“ oder eine andere Quellenphrase.

## Coverage

Die sieben Seiten enthalten 381 Ereignisse in 135 Feldern:

| Register | KEEP-Ereignisse | alle Ereignisse | Felder mit KEEP | alle Felder |
|---|---:|---:|---:|---:|
| Herbal | 11 | 100 | 9 | 20 |
| Bio | 34 | 281 | 26 | 115 |
| **Gesamt** | **45 (11,8 %)** | **381** | **35 (25,9 %)** | **135** |

Die reine Vollkarten-Schnittmenge umfasst 14 Typen und 58 Vorkommen
(22 Herbal, 36 Bio). Davon nehmen 21 Vorkommen an KEEP-Regeln teil, 35 bleiben
LOCAL_ONLY und zwei `oldy`-Vorkommen werden als Quellenphrase zurückgezogen.
Die drei exakten formalen Konstruktionen erfassen zusätzlich 24 Ereignisse mit
anderen vollständigen Oberflächen; zusammen ergibt das die 45 KEEP-Ereignisse.

## Drucktest der verlangten Phrasefamilien

- **Maß:** `daiin` bleibt als `STANDARD_PARAMETER?` (6 Herbal, 5 Bio).
  `aiin` bleibt wegen nur 1+2 Belegen eine getrennte lokale Karte.
- **Setup:** `qokaiin` darf `SET(<ARG_AIIN>)` realisieren; invariant ist nur
  „Standard-Slot setzen“, nicht „nächste Dosis nehmen“.
- **Link:** `FRAME_O(LINK)` überträgt als formale Verknüpfung (3/16), aber
  weder ein Vorobjekt noch „zuvor“.
- **Current batch:** `dy`, `chedy`, `or`, `char` und `dar` bleiben getrennte
  LOCAL_ONLY-Karten. Ihre Gegenstände kommen aus Record und Bild.
- **Prior batch:** kein gemeinsames exaktes `OLOR`; `ZUVOR` wird entzogen.
- **Use, warm, ready, clear:** Die ausgewählten OKY-, OKEEY-, CTHY- und
  EY-Karten besitzen keine identische vollständige Oberfläche in beiden
  Registern. Die geteilten `cheeky` und `shey` sind nur eigene 1+1-Lokalwetten.
- **CLOSE:** `oldy` ist in beiden Registern exakt
  `CLOSE(FRAME_O(LINK))`; die bisherige Kochphrase fällt vollständig aus.

## Stärkste Widersprüche

1. Alle 14 geteilten Vollkartentypen behalten zwar registerübergreifend ihren
   formalen Baum, doch die deutschen V49-Kontexte wurden aus derselben
   Arbeitshypothese erzeugt und sind keine unabhängige Replikation.
2. `qokaiin` ist stark Entry-/Reset-lastig und hat nur einen Herbal-Beleg.
   Deshalb überlebt nur SET, keine Quellhandlung.
3. `daiin` besitzt keine sichtbare Skala, Einheit oder extern identifizierte
   Größe. Selbst `STANDARD_PARAMETER?` bleibt eine Merkhypothese.
4. Die flüssigen V53/V54-Sätze benötigen weiterhin Pflanzen, Wasser, Becken,
   Körper, Leitung und Station als stille Registerfüller. Kein KEEP-Prompt
   benennt eines dieser Objekte.

## Arbeitsurteil

Es existiert ein kleines übertragbares **Kontrollphrasebook**, aber kein
registerübergreifendes semantisches Wörterbuch. Die belastbare Gemeinsamkeit
ist: Standard-Slot setzen, lokalen Relations-Slot setzen, aktiven Zustand
verknüpfen und möglicherweise einen Vorgabeparameter laden. Alles Konkretere
bleibt Herbal- beziehungsweise Bio-lokal.
