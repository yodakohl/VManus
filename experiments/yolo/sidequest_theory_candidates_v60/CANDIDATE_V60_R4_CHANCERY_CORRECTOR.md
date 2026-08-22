# V60 R4 — Korrektorprüfung der elf konkreten Ganzkarten

Status: unabhängiger kreativer Sidequest-Pass, keine Entzifferung. Ich las nur
die kanonische V59-R1-Ausgabe, das V60-Protokoll und mein festes Rollenprofil;
keine andere V60-Kandidatur. `f84` und `f84r` blieben versiegelt.

## Entscheidung

Die elf Karten bleiben als **vorläufiges Werkstattvokabular** erhalten. Ich
ändere aber vier Dinge:

1. `VERWENDEN?` wird zum ausführbaren `ANWENDEN?`;
2. `BEREITUNG?` wird zum kürzeren Stoffnomen `ANSATZ?`;
3. `AN?` wird zum selbständig lesbaren Relationsargument `ZIEL?`;
4. `WARM?` wird zur Operation `TEMPERIEREN?`.

`KLAR?` bleibt genau ein Zustandswort. Die alte Expansion „bis die Flüssigkeit
klar abläuft“ war keine Wortbedeutung, sondern eine ganze lokale Klausel. Weder
„bis“, „Flüssigkeit“ noch „ablaufen“ gehört in den Kartenwert.

## Revidiertes Kurzdeck

| Karte | Quellklasse | V60-R4-Wert | härtester Rivale |
|---|---|---|---|
| AIIN | Parameter-Nomen | `MASS?` | `STANDARD?` |
| OKY | Handlung | `ANWENDEN?` | `AUSFÜHREN?` |
| CTHY | Zustand | `BEREIT?` | `FERTIG?` |
| OR | Arbeitsstoff | `ANSATZ?` | `BEREITUNG?` |
| AL | Relationsargument | `ZIEL?` | `STELLE?` |
| EY | Zustand | `KLAR?` | `ENDE?` |
| OLOR | Rückverweis | `VORIGES?` | `DARAUS?` |
| OTCHEY | Auswahl-Nomen | `ANTEIL?` | `AUSWAHL?` |
| OKEEY | Handlung | `TEMPERIEREN?` | `WARM?` |
| OKE | terminale Handlung | `SPÜLEN?` | `DURCHGANG?` |
| LCHE | terminale Handlung | `ABLASSEN?` | `AUSLAUF?` |

Das Fragezeichen gehört zum Wert. Es verhindert, dass ein kreativer Default
später als bestätigtes historisches Lexem zitiert wird.

## Wesentliche Druckproben

- AIIN ist zwanzigmal und registerübergreifend. `MASS?` ist konkret und kurz,
  doch keine Zahl ist unabhängig sichtbar. Das stärkste abstrakte Gegenwort
  bleibt `STANDARD?`.
- OKY verbindet Herbal-Gebrauch und Bio-Ausführung. `ANWENDEN?` ist als
  Werkstattanweisung konkreter als „verwenden“, bleibt aber weit genug für
  Körper, Stoff, Gefäß und Kanal.
- OR steht einmal verdoppelt. Ein gewöhnliches wiederholtes Nomen wäre dort
  ungelenk; eine kopierte Kategorienkarte oder zwei parallele Ansätze bleiben
  möglich.
- AL kann ein ganzes Feld allein besetzen und steht wiederholt vor LCHE.
  Deshalb ist `ZIEL?` besser rücklesbar als die Präposition `AN?`.
- EY kommt an Anfang, Mitte und Ende von Feldern vor. Die Karte bezeichnet
  daher nicht einfach Satzende. `KLAR?` ist nur die riskante Zustandswette.
- OKE und LCHE sind ausnahmslos mit ihren jeweiligen Schlussformen verbunden.
  `SPÜLEN?` und `ABLASSEN?` bleiben nützliche Bio-Hypothesen, aber ein
  kategoriales „Schritt A/B“ erklärt dieselbe Oberfläche billiger.

## Arbeitsregel für einen Lehrling

Lerne diese elf Formen als unteilbare Karten. Sprich niemals sichtbare Teile
einzeln aus. Setze pro Karte höchstens das kurze Tabellenwort ein; ergänze
Objekt, Medium, Ziel, Horizont und Ergebnis erst aus Bild, Record und Exemplar.
Damit wird etwa:

```text
QOKEEY  QOKEDY
TEMPERIEREN?  SPÜLEN?
lokal: Temperiere den aktiven Ansatz; spüle den bezeichneten Lauf und schließe.
```

Die dritte Zeile ist Quellenexpansion, nicht Wörterbuch.

## Ergebnis

V60 verbessert das Wörterbuch nur auf der **Quellklassen- und
Granularitätsebene**. Es bestätigt keine Bedeutung. Alle 85 Vorkommen stehen in
`V60_R4_85_OCCURRENCE_PRESSURE.tsv`; das revidierte 173/381-Paar ist rein
mechanisch aus V59 abgeleitet und in `V60_R4_VALIDATION.json` geprüft.
