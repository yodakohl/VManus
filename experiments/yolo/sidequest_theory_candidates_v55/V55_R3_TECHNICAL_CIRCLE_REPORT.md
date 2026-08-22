# V55 R3 — Unabhängige technische Kreisnotation

Status: kreative technische Arbeitsausgabe für `f67r2`, `f68r1` und `f69v`;
keine Entzifferung. Es wurden keine GDT327-Prosa-Kartenwerte auf Kreisformen
übertragen. `f84` und `f84r` wurden nicht geöffnet.

## Ergebnis

Die drei Diagramme arbeiten am sparsamsten als **drei lokale
Nachschlageinstrumente mit getrennten Namensräumen**:

```text
f67r2  SELECT(P7, Z12, C8) -> lokaler Tabellenwert
f68r1  LOCATE(CENTER, ANCHOR, plotted_position) -> räumlicher S28-Schlüssel
f69v   READ(ordered_position, exact_complete_entry) -> lokale technische Regel
```

Diese Notation ist ausführbar, ohne einem sichtbaren Wort „Planet“, „Körper“,
„Mondstation“, „Bad“ oder „Monat“ zuzuschreiben. Diagrammrolle, Slotadresse und
Inhalt bleiben getrennt. Die drei vollständigen Regeln stehen in
`V55_R3_THREE_DIAGRAM_TECHNICAL_SUMMARIES.tsv`.

## Abdeckungsnachweis

V16/V22 liefern bereits eine vollständige 395-Gruppen-Ausgabe. V55 druckt
diese Gruppen nicht redundant neu, sondern ordnet jede durch eine erschöpfende
Adressregel einem lokalen Default zu.

| Seite | Gruppen | erschöpfende Partition |
|---|---:|---|
| f67r2 | 190 | Z12-Köpfe 12 + Erweiterungen 16 + P7-Gruppen 9 + Z12-Werte 17 + C8-Gruppen 10 + Rubrik 126 |
| f68r1 | 65 | Rubrik 28 + Anker 3 + Zentrum 1 + räumliches S28-Inventar 28 + Zentrallegende 5 |
| f69v | 140 | drei Rubrikbänder 107 + 28 Radialeinträge mit 33 Gruppen |
| **Gesamt** | **395** | **jede primäre ZL3b-Gruppe genau einer Rolle zugeordnet** |

Die 28 f69-Einträge bestehen aus 23 einteiligen und fünf zweiteiligen
Einträgen. Ein mehrteiliger Eintrag erhält erst als vollständige sichtbare
Folge seinen Regelwert; seine Einzelgruppen bleiben adressierte Fragmente.

## Die drei Maschinen

### f67r2: 7×12-Wahltafel

Die zwölf Loci 1–12 bilden `Z12[01..12]`; ihr erstes Gruppenstück ist der
Slotkopf, die übrigen Stücke vervollständigen seine lokale Beschriftung. Die
sieben Schlüsselplätze liegen an den Loci 15, 22, 28, 31, 34, 37 und 47 und
heißen neutral `P7[01..07]`. Die Loci 52–63 liefern ein zweites
Zwölferinventar `VALUE[Z12]`. Die acht zentralen Plätze 64–71 werden als
separate Bedingungen `C8[01..08]` geführt, nicht heimlich in das Siebenerdeck
eingerechnet.

Ausführung:

```text
p := choose(P7)
z := choose(Z12)
c := active(C8)
result := lookup(p, z, c, VALUE[z])
return result under local rubric
```

Das ist eine technische 7×12-Wahltafel. Die medizinische Melothesie-Lesung
bleibt ein sinnvoller Inhaltsrivale, ist aber keine Kartenübersetzung.

### f68r1: Zentrum plus 28 räumliche Adressen

Loci 1–4 sind Bedienrubrik, 5–7 drei Orientierungsanker, Locus 8 das Zentrum,
Loci 9–36 genau 28 geplottete Ein-Gruppen-Adressen und Locus 37 eine
fünfteilige Zentrallegende.

```text
frame := orient(CENTER, ANCHOR[1..3])
s := choose_visible_plotted_position(frame)
return SPATIAL[s]
```

`s=01..28` ist nur eine editorische Adresse. Ohne sichtbaren Start und ohne
Richtung wird kein Kreisumlauf erfunden. f68 ist damit ein räumlicher Katalog,
nicht von selbst ein Kalender.

### f69v: geordneter 28er-Regelkatalog

Die drei äußeren Bänder bleiben Bedienrubrik. Loci 4–31 sind 28 geordnete
Slots. Der Slot liefert die Adresse; der vollständige ein- oder zweiteilige
Eintrag liefert eine registerlokale `RULE_ID`.

```text
i := choose_ordered_slot(1..28)
entry := concatenate(all visible groups at slot i)
rule := exact_entry_lookup(entry)
execute(rule)
```

Die im TSV ausgeschriebene technische Palette ist eine konkrete
Werkstatt-Defaultwelt aus Freigeben, Sperren, Spülen, Zuführen, Ablassen,
Temperieren, Filtern und Halten. Diese Handlungen sind lokale Expansionen des
ganzen Slots, keine Wörterbuchwerte der Einzelgruppen.

Der vollständige Eintrag `okeod` steht an den Arbeitsplätzen 11, 15 und 24 und
erhält dreimal denselben Default „Beckenlauf freigeben“. Damit bleibt V22s
Identitätskorrektur erhalten: LONG/LONG/SHORT kann nicht „günstig/günstig/
ungünstig“ oder irgendeine feste Polarität bedeuten. LONG/SHORT ist nur
Layoutkapazität.

## Direkter f68↔f69-Test

Eine indexweise Verbindung ist mechanisch formulierbar, aber nicht lizenziert:

- beide Inventare besitzen 28 Slots;
- f68 besitzt 28 einteilige räumliche Labels, f69 33 Gruppen in 28 Regeln;
- unter den 28 möglichen Gleichindexpaaren gibt es **0 exakte
  Vollflächenübereinstimmungen**;
- auch über alle 28×28 Kombinationen gibt es **0 exakte
  Vollflächenübereinstimmungen**;
- f68 besitzt keinen festgestellten Autorenstart und keine festgestellte
  Richtung.

Deshalb gilt:

```text
JOIN(F68.SPATIAL[s], F69.ORDERED[s]) = UNLICENSED
```

Ein erlernter konventioneller Index könnte beide Instrumente verbinden. Bis
ein sichtbarer oder externer Schlüssel vorliegt, werden sie als zwei getrennte
28er-Werkzeuge benutzt.

## Fairer Modellvergleich

| Modell | Gewinn | stärkster Verlust |
|---|---|---|
| Kalender | erklärt 7/12/28 als gewöhnliche astronomische Kardinalitäten | identifiziert weder Datum noch Phase, Start oder Richtung |
| medizinische Wahltafel | verbindet 7×12 und 28 historisch plausibel mit Wahlzeit und Körper-/Behandlungsregeln | keine Gruppe bezeichnet unabhängig Körperteil, Leiden oder Behandlung |
| Stationskatalog | liefert die klarste ausführbare Adress-/Lookup-Notation und respektiert lokale Namensräume | Stations- und Bedieninhalt bleibt kreativ ergänzt |
| Musterbuch | erklärt Kopierform, Mehrgruppenlabels, Ringe und Wiederholung mit minimaler Semantik | erklärt nicht, warum oder wie ein Benutzer eine Auswahl ausführt |

Der **Stations-/Lookup-Katalog** gewinnt für R3. Die medizinische Wahltafel ist
der stärkste Inhaltsrivale; das Musterbuch ist der stärkste konservative Null.
Ein Kalender bleibt als Quellenfamilie möglich, aber nicht als gelesene Skala.

## Revision gegenüber der bisherigen Kreisfassung

- Die V16/V22-Vollabdeckung und alle sichtbaren Reihenfolgen bleiben erhalten.
- Medizinische oder kalendarische Wörter werden aus den Einzelgruppen
  entfernt und nur noch als konkurrierende ganze Diagrammwelten geführt.
- f67 trennt sieben Schlüsselplätze, zwölf Auswahlplätze, zwölf Werte und acht
  Zentralbedingungen, statt benachbarte Inventare still zusammenzuwerfen.
- f68 behält Zentrum plus 28 räumliche Labels ohne erfundenen Zyklusstart.
- f69 bindet Regeln an vollständige Eintragsidentität; Positionsparität erhält
  keinen Inhalt.
- Die f68↔f69-Paarung wird nicht aus gleicher Kardinalität erzwungen.

## Stärkster Gesamtwiderspruch

Eine Slotmaschine kann jede opake Gruppe als Adress- oder Regelfragment führen,
ohne ihren Inhalt zu kennen. Vollständigkeit beweist deshalb gerade keine
Semantik. V55 liefert eine saubere, lernbare technische Benutzungsweise für
395/395 Gruppen; Kalender, medizinische Wahltafel, Stationskatalog und
Musterbuch bleiben mit denselben Oberflächen weitgehend unterbestimmt.
