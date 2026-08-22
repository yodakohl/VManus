# V60 — Vierrollen-Auswahl der exakten Kartenwerte

Status: kreative Arbeitsedition, keine wissenschaftliche Übersetzung.

Vier voneinander getrennte Schreiberrollen prüften alle 85 Vorkommen der elf
in V59 exponierten exakten Joint-Tuple-Karten. Keine Rolle durfte PAGE_HOST,
sichtbare Teilstrings oder Koordinaten semantisch vererben.

## Ausgewähltes Deck

```text
AIIN    MASS?          Parameter
OKY     ANWENDEN?      Handlung
CTHY    BEREIT?        Zustand
OR      ANSATZ?        Arbeitsstoff
AL      ZIEL?          Relationsargument
EY      KLAR?          Zustand
OLOR    VORIGES?       Rückverweis
OTCHEY  ANTEIL?        Auswahl
OKEEY   TEMPERIEREN?   Handlung
OKE     SPÜLEN?        terminale Handlung
LCHE    ABLASSEN?      terminale Handlung
```

Die Auswahl ist kein Mehrheitsautomat. `ANWENDEN?`, `ANSATZ?`, `ZIEL?` und
`TEMPERIEREN?` gewinnen, weil sie im vollständigen Arbeitsablauf eine
konstantere Quellklasse liefern als die älteren Mischformen. Das Fragezeichen
bleibt überall Teil des Labels.

## Tatsächliche Verbesserung gegenüber V59

- `VERWENDEN?` wird als Handlung enger zu `ANWENDEN?`.
- `BEREITUNG?` wird als Stoff-/Chargennomen zu `ANSATZ?`.
- Die ergänzungsbedürftige Präposition `AN?` wird zum selbständig einsetzbaren
  Zielslot `ZIEL?`.
- Das uneindeutige Adjektiv `WARM?` wird zur ausführbaren Operation
  `TEMPERIEREN?`.
- `ZUVOR?` wird als anaphorischer Wert `VORIGES?`.
- `TEIL?` wird zum ausgewählten `ANTEIL?`.

`MASS?`, `BEREIT?`, `KLAR?`, `SPÜLEN?` und `ABLASSEN?` bleiben. Insbesondere
bedeutet EY **nicht** „bis die Flüssigkeit klar abläuft“: Das Kartenwort ist
höchstens `KLAR?`; die lange Formulierung gehört in die lokale Klausel.

## Bleibende Sollbruchstellen

- OR steht einmal unmittelbar doppelt; `ANSATZ ANSATZ` ist keine glatte
  normale Prosa und kann eine Kategorienwiederholung sein.
- OLOR und OTCHEY haben je nur zwei Vorkommen.
- OKE und LCHE sind 16/16-mal mit zwei bestimmten formalen Schlussfamilien
  konfundiert. Ein anonymes `SCHRITT_A/SCHRITT_B` bleibt daher vollwertiger
  Rivale zu `SPÜLEN/ABLASSEN`.
- Kein Wert ist ein bestätigtes historisches Lexem, Lautwert oder Gloss.

## Ergebnis

Das V60-Deck ist kürzer, wortartstabiler und für den nächsten Pass ausführbar.
Es ändert ausschließlich die elf exakten Kartenidentitäten. Die übrigen 162
Karten und 296 Ereignisse erhalten keinerlei neue Bedeutung. V61 darf dieses
Deck nun benutzen, muss aber Aussagen über physische Zeilengrenzen hinweg
rekonstruieren.
