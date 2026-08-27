# GDT559 — Argument-Trägerbuch

Die vier kurzen Werte bleiben unverändert: `Y=POSTEN`, `AIIN=WERT`, `AIN=ANTEIL`, `OR=EINHEIT`. OT, OL und DY bestimmen, was mit diesem Wert geschieht. Jede der390 Argumentstellen und jede der24 geschriebenen Argument-Steuerfolgen hat unten bzw. in den TSV-Artefakten eine Standardlesung.

## Sechs vollständige Hüllen

| Hülle | Stellen | Y | AIIN | AIN | OR | Standard |
|---|---:|---:|---:|---:|---:|---|
| `OT>A<END` | 185 | 118 | 28 | 18 | 21 | DANACH · ARG |
| `OL>A<END` | 156 | 105 | 26 | 15 | 10 | FORTSETZEN · ARG |
| `START>A<DY` | 31 | 28 | 0 | 1 | 2 | ARG · ABSCHLIESSEN |
| `START>A<OL` | 16 | 15 | 0 | 0 | 1 | ARG · FORTSETZEN |
| `OL>A<OL` | 1 | 1 | 0 | 0 | 0 | FORTSETZEN · ARG · FORTSETZEN |
| `OT>A<OL` | 1 | 1 | 0 | 0 | 0 | DANACH · ARG · FORTSETZEN |

## Elf echte Austauschfamilien

| Familie | Rezept | Varianten | Karten | Seiten | Standard |
|---|---|---|---:|---:|---|
| G559-F01 | `OT+ARG` | Y|AIIN|AIN|OR | 88 | 19 | danach ARG als nächsten Träger eröffnen |
| G559-F02 | `OL+ARG` | Y|AIIN|AIN|OR | 59 | 19 | weiter mit ARG als aktuellem Träger |
| G559-F03 | `OT+E+ARG` | Y|AIIN|OR | 24 | 13 | danach ARG als nächsten Träger eröffnen |
| G559-F04 | `OL+K+ARG` | Y|AIIN|AIN | 11 | 8 | weiter mit ARG als aktuellem Träger |
| G559-F05 | `OT+AL+ARG` | Y|AIN|OR | 5 | 5 | danach ARG als nächsten Träger eröffnen |
| G559-F06 | `OT+EE+ARG` | Y|OR | 24 | 9 | danach ARG als nächsten Träger eröffnen |
| G559-F07 | `OT+CH+ARG` | Y|OR | 8 | 7 | danach ARG als nächsten Träger eröffnen |
| G559-F08 | `OL+SH+E+ARG` | Y|OR | 3 | 3 | weiter mit ARG als aktuellem Träger |
| G559-F09 | `S+OT+ARG` | Y|AIIN | 3 | 3 | danach ARG als nächsten Träger eröffnen |
| G559-F10 | `D_ADDR+OL+K+ARG` | Y|AIN | 2 | 1 | weiter mit ARG als aktuellem Träger |
| G559-F11 | `SH+E+OL+ARG` | Y|AIIN | 2 | 1 | weiter mit ARG als aktuellem Träger |

Die nackten Rahmen `OT+ARG` (88 Karten) und `OL+ARG` (59 Karten) tragen jeweils alle vier Werte. Jedes der sechs Argumentpaare teilt beide Rahmen und mindestens einen weiteren state-spezifischen Austauschweg. Die elf Familien decken229 Karten; die übrigen161 Argumentstellen behalten dieselbe kurze Hüllenregel, ohne zu einer neuen Ganzwortbedeutung zu werden.

## Nachfolgerregel

Für341 Karten setzt OT oder OL das letzte sichtbare Argument als rechten Träger. In157/157 Fällen ohne neues sichtbares Argument übernimmt die nächste Karte genau diesen Wert. In173 Fällen schreibt die nächste Karte einen neuen Wert und ersetzt ihn; elf Karten enden die Aussage. Es gibt null falsche oder leere Übernahmen.

```text
OT + ARG   nächsten Träger als ARG eröffnen
OL + ARG   mit ARG als aktuellem Träger fortfahren
ARG + OL   ARG weiter aktiv halten
ARG + DY   ARG führen, dann den Schritt schließen
```

## Y ist nicht DY

Im exakten Atomstrom stehen235 Karten mit Y ohne DY,677 mit DY ohne Y und28 mit beiden. In allen28 gemeinsamen Karten steht Y vor dem getrennten DY. Die Lesung ist deshalb kompositionell: `Y` liefert POSTEN; `DY` schließt später den Schritt. 27 Karten schließen die Aussage, während `Y+DY+D_LABEL` nur einen lokalen Schritt schließt und danach sein sichtbares Etikett fortsetzt.

## Alle24 geschriebenen Steuerfolgen

| Folge | Karten | final | wörtliche Arbeitslesung |
|---|---:|---:|---|
| `OT+Y` | 117 | 0 | NÄCHSTEN TRÄGER ERÖFFNEN → POSTEN |
| `OL+Y` | 96 | 6 | TRÄGER FORTSETZEN → POSTEN |
| `OT+AIIN` | 28 | 0 | NÄCHSTEN TRÄGER ERÖFFNEN → WERT |
| `Y+DY` | 28 | 27 | POSTEN → SCHRITT ABSCHLIESSEN |
| `OL+AIIN` | 22 | 0 | TRÄGER FORTSETZEN → WERT |
| `OT+OR` | 21 | 1 | NÄCHSTEN TRÄGER ERÖFFNEN → EINHEIT |
| `OT+AIN` | 18 | 1 | NÄCHSTEN TRÄGER ERÖFFNEN → ANTEIL |
| `OL+AIN` | 15 | 0 | TRÄGER FORTSETZEN → ANTEIL |
| `OL+OR` | 9 | 1 | TRÄGER FORTSETZEN → EINHEIT |
| `Y+OL` | 8 | 0 | POSTEN → TRÄGER FORTSETZEN |
| `Y+OL+Y` | 5 | 2 | POSTEN → TRÄGER FORTSETZEN → POSTEN |
| `OR+DY` | 2 | 2 | EINHEIT → SCHRITT ABSCHLIESSEN |
| `OT+OL+Y` | 2 | 0 | NÄCHSTEN TRÄGER ERÖFFNEN → TRÄGER FORTSETZEN → POSTEN |
| `AIN+DY` | 1 | 1 | ANTEIL → SCHRITT ABSCHLIESSEN |
| `OL+AIIN+Y` | 1 | 0 | TRÄGER FORTSETZEN → WERT → POSTEN |
| `OL+OL+Y` | 1 | 0 | TRÄGER FORTSETZEN → TRÄGER FORTSETZEN → POSTEN |
| `OL+OR+AIIN` | 1 | 0 | TRÄGER FORTSETZEN → EINHEIT → WERT |
| `OL+OT+Y` | 1 | 0 | TRÄGER FORTSETZEN → NÄCHSTEN TRÄGER ERÖFFNEN → POSTEN |
| `OL+Y+OL` | 1 | 0 | TRÄGER FORTSETZEN → POSTEN → TRÄGER FORTSETZEN |
| `OR+OL` | 1 | 1 | EINHEIT → TRÄGER FORTSETZEN |
| `OT+OL+AIIN` | 1 | 0 | NÄCHSTEN TRÄGER ERÖFFNEN → TRÄGER FORTSETZEN → WERT |
| `OT+Y+OL` | 1 | 0 | NÄCHSTEN TRÄGER ERÖFFNEN → POSTEN → TRÄGER FORTSETZEN |
| `Y+OL+AIIN` | 1 | 0 | POSTEN → TRÄGER FORTSETZEN → WERT |
| `Y+OL+OL` | 1 | 0 | POSTEN → TRÄGER FORTSETZEN → TRÄGER FORTSETZEN |

## Arbeitsgrenze

Das ist eine vollständige Werkstattbelegung vorhandener Komponenten, keine bestätigte Übersetzung. Sie ändert keinen Stamm, kein Rezept, keine Seite und keine Aussagegrenze. Entscheidend für die nächste Seite ist die Vorhersage: Ein bekanntes Argument darf im sichtbaren OT/OL/DY-Rahmen seinen kurzen Wert wechseln, ohne dass der Kontrolloperator mitwechselt.
