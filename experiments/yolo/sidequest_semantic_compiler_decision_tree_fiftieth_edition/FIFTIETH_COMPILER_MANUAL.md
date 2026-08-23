# Schreiber-Compiler: vom gemeinten Arbeitsbefehl zur Karte

Der Lehrling prüft immer in derselben Reihenfolge:

1. **Ganze registrierte Karte vorhanden?** Abschreiben.
2. **Basis und Endung einzeln vorhanden?** Als zwei Karten schreiben.
3. **Kontrollierte Umschreibung vorhanden?** Umschreiben und die Zusatzbedeutung mitdenken.
4. **Sonst:** nichts erfinden; die Werkstattvorlage beim Meister anfordern.

Die Entscheidung betrifft nur das feste 12×12-Lehrgitter. Sie erzeugt kein neues Voynich-Wort.

## USE_OBSERVED_FUSED_CARD

Wunsch: **ansetzen am aktuellen Posten** (`OK+Y`).

Ausgabe: `oky`; Arbeitslesung: **ansetzen am aktuellen Posten**.

## USE_ANALYTIC_TWO_CARD_FORM

Wunsch: **fortsetzen mit Sollwert** (`OL+AIIN`).

Ausgabe: `ol aiin`; Arbeitslesung: **fortsetzen mit Sollwert**.

## USE_CONTROLLED_PARAPHRASE

Wunsch: **ansetzen und den Schritt schließen** (`OK+CLOSE`).

Ausgabe: `qokedy`; Arbeitslesung: **ansetzen, kurz ausführen und schließen**.

## REJECT_UNLICENSED_EMPTY_CELL

Wunsch: **fortsetzen bis zur Stufe** (`OL+IIN`).

Ausgabe: `NONE`; Arbeitslesung: **Meister nach einer Vorlage fragen**.
