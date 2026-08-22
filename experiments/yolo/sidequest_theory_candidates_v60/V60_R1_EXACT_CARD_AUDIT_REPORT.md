# V60 R1 — Audit der elf kanonischen Exact-Card-Mnemonics

Status: vollständiger kreativer Werkstattaudit, keine Entzifferung. Bestätigte
Lexeme und bestätigte Klartextklauseln bleiben null.

## Endentscheidung

Alle elf Mnemonics bleiben explorativ aktiv. Keine Karte ist durch ihre
Vorkommen unmöglich geworden; fünf Benennungen werden jedoch kürzer oder
quellnäher präzisiert:

```text
BEREITUNG?  → ZUBEREITUNG?   OR
AN?         → DORTHIN?       AL
ZUVOR?      → VOM VORIGEN?   OLOR
TEIL?       → ANTEIL?        OTCHEY
WARM?       → LAUWARM?       OKEEY
```

Sechs Benennungen bleiben unverändert: `MASS?`, `VERWENDEN?`, `BEREIT?`,
`KLAR?`, `SPÜLEN?`, `ABLASSEN?`. Die Revision ändert genau 5/173
Wörterbuchzellen und 28/381 Ereigniszellen. Formalwert, Oberfläche,
Quellprosa, Rivale, Scope und Status bleiben überall bytegleich zu V59.

## Elf Karten

| Exact-Card | Default | Klasse | zwei atomare Rivalen | n H/B | Confidence | Revisionskosten |
|---|---|---|---|---:|---:|---|
| AIIN | Maß | Parameter | Portion · Vorgabe | 9/11 | 0.78 | 0 |
| OKY | verwenden | Verb | anwenden · fortsetzen | 3/7 | 0.68 | 0 |
| CTHY | bereit | Zustand | fertig · reif | 3/4 | 0.62 | 0 |
| OR | Zubereitung | Nomen | Ansatz · Flüssigkeit | 5/2 | 0.55 | 1 Karte + 7 Events |
| AL | dorthin | Relation | hinein · weiter | 1/9 | 0.60 | 1 Karte + 10 Events |
| EY | klar | Zustand | rein · fertig | 1/3 | 0.53 | 0 |
| OLOR | vom Vorigen | Relation | daraus · zuvor | 1/1 | 0.42 | 1 Karte + 2 Events |
| OTCHEY | Anteil | Nomen | Portion · Probe | 1/1 | 0.45 | 1 Karte + 2 Events |
| OKEEY | lauwarm | Zustand | warm · temperiert | 0/7 | 0.58 | 1 Karte + 7 Events |
| OKE | spülen | Verb | reinigen · beenden | 0/8 | 0.35 | 0 |
| LCHE | ablassen | Verb | sammeln · beenden | 0/8 | 0.36 | 0 |

`H/B` zählt Herbal-/Biological-Vorkommen, nicht unabhängige Belege. Das
Wörterbuch bindet jeden Wert ausschließlich an die vollständige
`joint_tuple_id`. Die in der Vorkommenstabelle mitgeführten Oberflächen und
Formelbäume heißen ausdrücklich `audit_only`; weder sie noch PAGE_HOST oder
sichtbare Komponenten dürfen einen Wert auf eine andere Tuple-ID übertragen.

## Vollständiger Kontextdruck

Die Datei `V60_R1_85_OCCURRENCE_AUDIT.tsv` listet jedes der 85 Ereignisse genau
einmal mit Seite, Record, Feld, Record- und Feldposition, Schlussstatus,
unmittelbarem Vorgänger und Nachfolger, beiden lokalen Ganzexpansionen sowie
dem kartenspezifischen Widerspruch.

Gesamtverteilung:

- 85 Ereignisse in 57/135 Feldern, allen 11 Prosarecords und allen sieben
  Prosaseiten;
- 24 Herbal- und 61 Biological-Vorkommen;
- 20× FIRST, 36× MIDDLE, 19× LAST, 10× ONLY;
- 69× NONCLOSE und 16× TERMINAL;
- die 16 terminalen Fälle sind vollständig OKE oder LCHE.

Der Druck je Karte lautet:

1. **AIIN — Maß.** 20 Fälle erreichen alle 11 Records und alle Feldpositionen
   außer ONLY; zwei Folgen `OKY→AIIN`. Lehrregel: nur „Maß“ sagen, Zahl und
   Einheit aus dem Exemplar übernehmen. Stärkster Widerspruch: keine Karte
   zeigt selbst Zahl oder Einheit; die 20 Maßexpansionen sind geerbt.
2. **OKY — verwenden.** Zehn Fälle bilden einen breiten Handlungspivot;
   `OKEEY→OKY` und `OKY→AIIN` erscheinen je zweimal. Lehrregel: kein Material
   oder Ziel mitsprechen. Widerspruch: ONLY- und Feldendfälle erlauben ebenso
   „fortsetzen“ oder eine Freigabeformel.
3. **CTHY — bereit.** Sechs von sieben Fällen stehen feldmittig, alle vor einem
   Schluss. Lehrregel: Zustand, nicht Befehl. Widerspruch: Nur einmal folgt OR;
   der eine offene Feldendfall trägt keine Zubereitungsfolge.
4. **OR — Zubereitung.** Fünf mittlere und zwei feldinitiale Fälle; einmal
   `CTHY→OR`, einmal `OR→OR`. Lehrregel: Stoff, Gefäß und Zustand nicht in das
   Nomen packen. Widerspruch: Das Doppeltuple würde bei Satzkomposition
   „Zubereitung Zubereitung“ ergeben; deshalb bleibt das Feld Exemplar, nicht
   aus Karten zusammengesetzte Prosa.
5. **AL — dorthin.** Zehn Fälle verteilen sich über FIRST/MIDDLE/LAST/ONLY;
   fünf beginnen ein Feld. Lehrregel: Der Lehrling zeigt auf den aktiven
   Exemplarbesitzer und sagt nur „dorthin“. Widerspruch: Kein Zielreferent ist
   unabhängig identifiziert.
6. **EY — klar.** Vier NONCLOSE-Fälle auf drei Seiten erlauben einen echten
   Zwischenzustand. Lehrregel: weder Flüssigkeit noch Ergebnis mitsprechen.
   Widerspruch: Transparenz, Reinheit und Fertigsein sind nicht getrennt.
7. **OLOR — vom Vorigen.** Zwei registerübergreifende Fälle werden jeweils von
   einer lokalen Weiterführung gefolgt. Lehrregel: Antezedent im Recordregister
   suchen, keine Entnahmehandlung ergänzen. Widerspruch: Zwei Fälle trennen
   anaphorisch, räumlich und zeitlich nicht.
8. **OTCHEY — Anteil.** Beide Fälle sind feldinitial, je einer in Herbal und
   Bio. Lehrregel: „nimm“ gehört zur Lokalexpansion, nicht zur Karte.
   Widerspruch: Zwei Fälle trennen Anteil, Probe und Abschnittsanfang nicht.
9. **OKEEY — lauwarm.** Sieben Bio-Fälle bilden mit je zwei Anschlüssen an OKY
   und OKE einen Zustands-Pivot. Lehrregel: Erwärmen und Halten nicht als
   stille Verben ergänzen. Widerspruch: kein unabhängiger Heiß/Kalt-Kontrast;
   der technische Rivale zeigt keine einheitliche Temperatur.
10. **OKE — spülen.** Acht Bio-Fälle; zweimal `OKEEY→OKE`, einmal folgt die
    Karte einer lokal so gelesenen Erstspülung. Lehrregel: Prompt und formalen
    Schluss getrennt ausführen. Widerspruch: 8/8 sind TERMINAL; „beenden“ ist
    die sparsamere reine Positionslesung.
11. **LCHE — ablassen.** Acht Bio-Fälle; einer folgt AL, ein technischer
    Ganzdefault lautet ebenfalls „unten ablassen“. Lehrregel: Gefäß und
    Richtung nur aus dem Exemplar beziehen. Widerspruch: 8/8 sind TERMINAL,
    fünf davon ONLY; die Abgrenzung von OKE ist nicht unabhängig geerdet.

## Lehr- und Korrekturverfahren

1. Der Meister zeigt eine vollständige Tuple-ID-Karte, nicht eine sichtbare
   Teilform.
2. Der Lehrling nennt genau den kurzen Default und seine Quellklasse.
3. Er nennt beide Rivalen; bei OKE und LCHE muss „beenden“ ausdrücklich fallen.
4. Er prüft FIRST/MIDDLE/LAST/ONLY und NONCLOSE/TERMINAL getrennt vom Wort.
5. Erst danach liest er die bereits publizierte lokale Expansion des
   bezeichneten Feldexemplars; sie darf das Mnemonic weder verlängern noch
   beweisen.
6. Beim Rücklesen muss dieselbe vollständige Tuple-ID entstehen. Ähnliche
   Oberfläche, gemeinsamer Bestandteil oder gleicher Host sind ein Fehler.

Typische Lehrlingsfehler sind `AL = dorthin + Becken`, `OTCHEY = nimm Anteil`,
`OKEEY = warm halten`, das Sprechen von CLOSE bei OKE/LCHE und die Übertragung
eines Mnemonics auf eine ähnlich aussehende andere Karte. Die Reparatur ist
immer dieselbe: zum Exact-Tuple zurückkehren, nur den kurzen Default sprechen
und alle Gegenstände oder Handlungen in die lokale Exemplarzeile zurücklegen.

## Artefakte und Schluss

- `V60_R1_11_CARD_DECISIONS.tsv`: alle elf Defaults, je zwei Rivalen,
  Quellklasse, vollständige Drucksummen, Lehrregeln, Widersprüche, Confidence
  und Revisionskosten;
- `V60_R1_85_OCCURRENCE_AUDIT.tsv`: vollständige Ereignisliste mit lokalem
  Vor-/Nachkontext und beiden Ganzexpansionen;
- `V60_R1_REVISED_173_CARD_DICTIONARY.tsv`: striktes Vollwörterbuch;
- `V60_R1_REVISED_381_EVENT_LEDGER.tsv`: striktes vollständiges Eventledger;
- `V60_R1_BUILD_EXACT_CARD_AUDIT.py` und `V60_R1_VALIDATION.json`:
  reproduzierbare Ableitung und Prüfprotokoll.

Validierung: `PASS` für 11/85/173/381/135. Der Audit verbessert die
Lehrsprache, nicht den wissenschaftlichen Status: Alle elf Werte bleiben
explorative Exact-Card-Mnemonics, lokale Ganzprosa bleibt Exemplar und kein
Wert ist ein bestätigtes Lexem.
