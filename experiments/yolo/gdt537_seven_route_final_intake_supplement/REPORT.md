# GDT537 — Die vollständige 159er-Ausgabe ist jetzt der aktive Leser

## Ergebnis

`PASS_SEVEN_ROUTE_FINAL_INTAKE_SUPPLEMENT`.

Die endgültige Arbeitsausgabe besteht aus **159 aufgelösten Prosaflächen**.
Ein neuer Overlay-Leser gibt für jede davon das GDT536-Rezept und die konkrete
Arbeitslesung zurück, bevor der ältere GDT517-Compiler zum Zug kommt. Der
vollständige Rücklauf ergibt 159/159 richtige Rezepte und 159/159 richtige
Routenklassen.

Das verhindert eine reale Regression: GDT517 kennt noch die ursprünglichen
GDT516-Ereignisrezepte und würde sechs spätere Rezeptkorrekturen bei einem
exakten Treffer wieder überschreiben.

## Korrektur: sieben statt vier Sonderkarten

Der kurze nächste-Routen-Text nach GDT536 nannte vier Sondermechanismen. Für
einen vollständigen Leser sind es **sieben**, weil auch drei frühere
Rang-1-Korrekturen erhalten bleiben müssen:

| Oberfläche | Endrezept | Rang | Route | Arbeitslesung |
|---|---|---:|---|---|
| `chekchy` | `CH+K+Y` | 1 | linker Superform-Peel | Nehmen, geben und posten. |
| `saiis` | `S+A_ADDR+IIN+S` | 1 | rechter Block-Peel | Wählen; hier die Stufe wählen. |
| `dsholdaiir` | `D_ADDR+SH+OL+DA+IIN+R` | 6 | `d|shol|daiir` plus lokaler Träger | Hier halten und fortsetzen; Stufe II markieren. |
| `dairykodas` | `D_ADDR+AIR+Y+K+O+DA+S` | 1 | verschachtelte Ganzkarte `odas` | Hier entlang der Bahn posten; zur Ausführung geben und Stufe II wählen. |
| `dalcheeeky` | `AL+CH+K+EEE+Y` | außerhalb | dritte K-Gradstufe | Am Zielort nehmen und geben; auf Grad III posten. |
| `qef` | `E+LOCAL_CHAR_F` | 2 | lokale q-Rolle im Satz | Hier auf Grad I. |
| `aiicthy` | `AIIN+CH+T+Y` | 1 | `aii`-Quadrat plus `cthy` | Den Wert nehmen, einstellen und posten. |

Sechs Karten ändern das ursprüngliche Rezept. `qef` behält sein Rezept und
ändert nur seinen Status von offen zu lokal entschieden. Die übrigen 152
Oberflächen sind gewöhnliche exakte Endkarten.

## Ausführbare Reihenfolge

Der neue Befehl ist:

```bash
python3 experiments/yolo/gdt537_seven_route_final_intake_supplement/src/intake_surface.py \
  --surface aiicthy --domain PROSE_STREAM --page f31r
```

Er antwortet direkt mit:

```text
AIIN+CH+T+Y
WERT · NEHMEN · EINSTELLEN · POSTEN
Den Wert nehmen, einstellen und posten.
```

Die Reihenfolge ist jetzt:

1. exakte GDT537-Prosafläche → endgültiges Rezept und Lesung;
2. bei einer der sieben Karten → zusätzlich benannte Herleitung und Geltungsbereich;
3. unbekannte oder ältere Oberfläche → unverändert an GDT517;
4. lokale Namens-/Adressdomäne → immer an den rollenbewussten GDT517-Zweig.

Damit wird eine Prosalesung nicht versehentlich auf ein älteres Ereignisrezept
zurückgesetzt, aber eine gleich geschriebene lokale Namenskarte auch nicht
blind als Prosa gelesen.

## Was eingefroren ist

- 159 exakte `PROSE_STREAM|surface`-Schlüssel;
- 152 gewöhnliche Endkarten;
- sieben benannte Revisionskarten aus GDT530–GDT536;
- sechs wirkliche Rezeptänderungen und eine reine Kontextauflösung;
- Rangverteilung 156×Rang 1, einmal Rang 2, einmal Rang 6, einmal bewusst
  außerhalb des alten Kandidatenraums.

Neue Oberflächen werden nicht blockiert: Sie laufen weiterhin durch den
produktiven Compiler und bleiben dort vorläufig, bis eine passende Familie
gefunden ist. Die sieben Spezialrouten werden nicht automatisch auf ähnlich
aussehende Formen übertragen.

## Nächster Schritt

Diese Ausgabe ist nun eine saubere Basis für neue Seiten. Vor deren Öffnung
kann noch ein kompakter Bedeutungs-Stresstest prüfen, ob die 159 kurzen
deutschen Lesungen innerhalb ihrer wiederkehrenden Rezeptfamilien wirklich
gleichartig formuliert sind; Rezept und Wurzeln bleiben dabei unverändert.
