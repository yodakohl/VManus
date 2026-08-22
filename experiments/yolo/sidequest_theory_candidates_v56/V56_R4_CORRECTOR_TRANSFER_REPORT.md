# V56 R4 — korrekturischer Herbal↔Biological-Phrasentransfer

Status: unabhängiger Quellenphrasen-Pass vor Sichtung der anderen
V56-Berichte. Kreative Werkstattdefaults, keine Entzifferung.

## Datenbasis

Genau 17 exakte GDT327-Ganzkarten kommen sowohl auf mindestens einer Herbal-
als auch einer Biological-Seite vor. Sie tragen 136 der 381 Prosaereignisse.
Die Kandidaten wurden ausschließlich über exakte gemeinsame Joint-Tuple-
Identität gebildet; PAGE_HOST, sichtbare Substrings und Edit-Distanz wurden
nicht benutzt.

## Entscheidung

Eine kleine gemeinsame **Prompt- und Relationsschicht** überträgt, aber keine
gemeinsame medizinische Satzsprache:

```text
MASS?              vorgeschriebenes Maß / Standard
LINK               unter demselben Bezug weiter
SET                neuen Posten einsetzen
USE?               aktiven Posten verwenden
READY?             Posten ist bereit
AT?                an den markierten Bezug/Slot
PREPARATION?       vorbereiteter Arbeitsstand
CURRENT_SLOT?      aktueller Formularposten
```

`MIX/WORK?`, `SAME_SOURCE?`, `CLEAR?`, `PREVIOUS?`, `WARM?` und
`INDICATED_PART?` dürfen als schwächere gemeinsame Quellenmnemonics stehen.
Sie werden nicht zu Kartenstämmen. `LINK+CLOSE` trägt nur formale Komposition,
keine zusätzliche gesprochene Phrase.

## Registerlokale Expansion

Ein und derselbe Prompt erhält sein Objekt erst aus Bild und laufendem Record:

| invariant | Herbal | Biological |
|---|---|---|
| `MASS?` | Maß Wurzel, Blatt, Saft oder Auszug | Maß Bad, Charge oder Anwendung |
| `SET` | neue Pflanzenzubereitung ansetzen | neue Becken-/Stationscharge einsetzen |
| `LINK` | mit dem vorigen Pflanzenansatz fortfahren | Vorlauf/Rücklauf oder vorige Behandlung weiterführen |
| `USE?` | Arzneianteil gebrauchen | Bad-/Spül-/Stationsposten ausführen |
| `READY?` | Zubereitung gebrauchsfertig | Charge oder Station arbeitsbereit |
| `AT?` | an eine örtliche Anwendung binden | an Öffnung, Figur oder Station anschließen |

Das invariant bleibende Stück ist kurz. Pflanze, Wasser, Körperteil, Becken,
Wein, Rohr, Krankheit und Richtung sind lokale stille Argumente.

## Warum kein gemeinsamer Rezepttext gewonnen ist

- Nur 17/173 exakte Karten überschneiden sich überhaupt.
- Einige scheinbar konkrete Paare haben nur 1 Herbal- und 1 Bio-Vorkommen.
- `CLEAR?`, `DRAIN?`, `RINSE?` und ähnliche Werte sind mit Feldschluss oder
  dem wasserreichen Bio-Kontext konfundiert.
- Der gleiche formale Prompt kann in Herbal einen Stoff und in Bio eine
  Station besitzen; das ist Funktionsübertragung, keine Lexemübersetzung.
- Die vollständigen V53/V54-Sätze enthalten weit mehr Kontextwörter als die
  gemeinsame Kartenschicht.

## Lehrregel

Ein Lehrling lernt die gemeinsame Karte zuerst als kurze Frage:

```text
Wieviel?  Welcher Posten?  Mit welchem Vorbezug?
Einsetzen?  Verbinden?  Verwenden?  Bereit?  An welchen Slot?
```

Danach setzt er die registerlokale Antwort aus Bild und Record ein. Er darf
nie aus „Maß“ auf eine bestimmte Substanz oder aus „an“ auf einen Körperteil
schließen. Ein Terminal wird zuletzt kopiert, aber nicht gesprochen.

Die 17 Entscheidungen stehen in `V56_R4_17_SHARED_CARDS.tsv`.
`f84` und `f84r` wurden nicht geöffnet.
