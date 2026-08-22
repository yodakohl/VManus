# V63 — Vierrollen-Auswahl: begrenzte Slotgrammatik

Status: kreative Arbeitsgrammatik, kein Bedeutungsdecoder.

## Auswahl

Der deterministische R3-Parser wird als gemeinsame Basis gewählt. Er verbindet
nur:

- elf exakte V60-Mnemonics;
- vier strikte formale V56/V59-Prompts;
- die vier anonymen V62-Register;
- sichtbare Reihenfolge und Feldschluss.

Er nutzt weder PAGE_HOST, Strings, Komponenten noch neue Kartenbedeutungen.

## Deckung

```text
Ereignisse: 119 erkannt, 262 EXEMPLAR_ONLY
Felder:       14 UNIQUE, 56 AMBIGUOUS, 65 UNPARSED
Aussagen:     12 UNIQUE, 49 AMBIGUOUS, 55 UNPARSED
```

Alle 135 Feld- und 116 Aussagefolgen bleiben als opake ID-Reihenfolge
rücklesbar. Das bedeutet nur, dass der Parser keine sichtbaren Ereignisse
verliert; es beweist keine Bedeutung.

## Arbeitsvorlagen

Die stärksten Vorlagen sind Parameterwert/-setzung, Zielwert/-setzung,
aktiven Stand verknüpfen, Ansatz binden, Bereitschaft/Klarheit prüfen,
vorigen Posten oder Anteil wählen, anwenden, temperieren, spülen und ablassen.
Bei mehreren Prompts bleibt ihre Reihenfolge erhalten. Ein Beispiel:

```text
ANTEIL? → TEMPERIEREN? → ANWENDEN?
SELECT_PART → TEMPER_ACTIVE → APPLY_ACTIVE
```

Das Objekt und das Ziel kommen aus anonymen Registern oder dem lokalen
Exemplar. Sie sind kein Bestandteil dieser drei Kartenwerte.

## Warum R3 gewinnt

- R1 findet eine etwas breitere Lehrschicht, bindet aber zusätzliche formale
  Kanäle und erreicht dadurch 126 Ankerereignisse.
- R2 zeigt historisch, dass nur 46/116 Aussagen glatt passen; zwölf belasten
  die Reihenfolge und drei widersprechen der bevorzugten Klausel.
- R4 behandelt jede geordnete Triggerfolge als deterministisch und unterschätzt
  dadurch die 49 mehrdeutigen Aussagen.
- R3 veröffentlicht `UNIQUE`, `AMBIGUOUS` und `UNPARSED` getrennt und gewinnt
  deshalb als ehrlichste ausführbare Fassung.

## Entscheidung

`KEEP` als begrenzter Strukturparser; `WITHDRAW` als vollständiger
Bedeutungsdecoder. V64 und V65 dürfen die zwölf eindeutigen und 49
mehrdeutigen Vorlagen als Gerüst benutzen. Die 55 exemplar-only Aussagen
dürfen nur aus Bild, Record und historischer Arbeitswelt konkret expandiert
werden; ihre Wörter dürfen nicht zurück in das Kartenlexikon fließen.
