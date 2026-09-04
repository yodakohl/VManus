# GDT806 — Drei-Kanal-Ganzwortkontexte

Status: `PASS__652_GLOBAL__577_RESIDUAL__967_TARGET_EVENTS__0_CONDITIONAL__0_CROSS_DENOMINATOR__6_UNRESOLVED__0_NEW_ROLES__ZERO_LEXEMES`

## Ergebnis

Der offizielle exakte Lauf bestätigt die transparent vorab offengelegte Korrektur:
Keines der sechs Ganzwörter passiert zugleich K12-Spezifität, Deckbreite,
Folio-Robustheit und den ungefilterten All-Opportunity-Test. Deshalb wird keine
neue Rolle, Wortbedeutung oder Renderer-Lizenz installiert.

Die Globalmenge wurde fail-closed als 652 Oberflächen rekonstruiert; nach Abzug
des engen N75-Decks bleiben 577 disjunkte Residualoberflächen. C1/C2/C3
partitionieren auf den sechs Zielen exakt 454/462 rohe und 320/304
paarsequenzstabile L1/R1-Kontakte.

## Rivalen

| Form | C2 zentriert roh/stabil | C3 zentriert roh/stabil | Rang C2 | Rang C3 | Entscheidung |
|---|---:|---:|---:|---:|---|
| `cheol` | -0.0627074314574 / -0.0575396825397 | -0.0123844409559 / 0.0308474142345 | 5/6 | 7/7 | `UNRESOLVED_RIVAL` |
| `otal` | 0.143353174603 / 0.0984126984127 | -0.00512391512392 / 0.0113373228079 | 4/5 | 7/7 | `UNRESOLVED_RIVAL` |
| `okal` | 0.0777777777778 / 0.203174603175 | 0.156570512821 / 0.238791937774 | 6/4 | 1/1 | `UNRESOLVED_RIVAL` |
| `ol` | 0.0153886554622 / -0.111111111111 | -0.0213774989056 / -0.0453673345477 | 7/6 | 5/3 | `UNRESOLVED_RIVAL` |
| `qokeol` | NA / NA | -0.0276612276612 / -0.137175324675 | NA/NA | 5/3 | `UNRESOLVED_RIVAL` |
| `qokol` | -0.172916666667 / -0.0720238095238 | -0.0289686745569 / -0.0907467532468 | 5/6 | 6/4 | `UNRESOLVED_RIVAL` |

## Einordnung

Die Runde ersetzt einen basisratengetriebenen Ganzwortvergleich durch zwölf
zielspezifische Kontrollganzwörter. `okal` bleibt im Residualdeck sichtbar,
aber C2 scheitert an der gefrorenen Rang-/All-Opportunity-Kette; die übrigen
Rivalen scheitern früher an Richtung, Marge oder Deckübereinstimmung.

Alle Werte und Schwellen wurden als exakte Brüche gerechnet. LOFO entfernt
synchron ein physisches Folio aus Ziel und Kontrollen, LOCO genau eine
Kontrolloberfläche; Null, Gleichstand und fehlende Kapazität zählen dagegen.
Die sieben Rahmen und zwölf Passagekarten tragen null Entscheidungs-, Semantik-
und Renderergewicht. Die Achsen stammen aus verwandten deutschen Arbeitsrenderern
und sind keine unabhängige semantische Replikation.

Bestätigte Lexeme/Klartextsätze: 0/0. Neue Seiten, Bilder oder Transkriptionen: 0.
f84/f84r-Zeilen: 0. Der GDT388-Einlass bleibt wegen Formalzugriff nicht score-ready.

## Reproduktion

```bash
python3 experiments/yolo/gdt806_three_channel_whole_context_replication/src/run.py
python3 experiments/yolo/gdt806_three_channel_whole_context_replication/src/validate.py
```
