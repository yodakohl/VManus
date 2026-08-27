# GDT551 context-contract book

## Der korrigierte Vergleich

GDT543 verglich die **tatsächlich angetroffenen** Eingangszustände einer alten Stammkarte mit denen der neuen Karte. Ein disjunkter Modussatz war deshalb noch keine andere Wortbedeutung und auch keine andere Satzregel. Der GDT540-Leser kennt nur zwei Steckplätze: sichtbare oder offene Handlung sowie sichtbares oder offenes Argument. Ein offener Platz darf aus dem laufenden Satz gefüllt werden; beim Argument ist auch die objektlose Lesung erlaubt, ohne Handlung bleibt eine nichtverbale Fragmentlesung.

```text
Vertrag = (HANDLUNG sichtbar/offen, ARGUMENT sichtbar/offen)
beobachteter Modus = genau der Zustand, der an diesem einzelnen Vorkommen anlag
```

## Die vier Vertragsklassen im 145er-Leser

| Vertrag | Oberflächen | erlaubte beobachtete Modi |
|---|---:|---|
| `ACTION_VISIBLE/ARGUMENT_VISIBLE` | 74 | `SELF_CONTAINED` |
| `ACTION_VISIBLE/ARGUMENT_OPEN` | 55 | `SELF_CONTAINED|REQUIRES_ACTIVE_ARGUMENT` |
| `ACTION_OPEN/ARGUMENT_VISIBLE` | 4 | `SELF_CONTAINED|REQUIRES_ACTIVE_ACTION` |
| `ACTION_OPEN/ARGUMENT_OPEN` | 12 | `SELF_CONTAINED|REQUIRES_ACTIVE_ARGUMENT|REQUIRES_ACTIVE_ACTION|REQUIRES_ACTIVE_ACTION_AND_ARGUMENT` |

## Rückblick auf die zwölf scheinbar disjunkten Fälle

Alle 12 früheren disjunkten Instanzvergleiche liegen innerhalb ihrer jeweiligen Steckplatzverträge. 11 behalten exakt denselben Vertrag; nur `kody` schließt durch das hinzugefügte `K` den vorher offenen Handlungsplatz. Kein Fall braucht einen lexikalischen Kontextumschalter.

| Oberfläche | alter Stamm | volle Karte | Vertrag | Erklärung |
|---|---|---|---|---|
| `chady` | `CH+A_ADDR` | `CH+A_ADDR+DY` | `IDENTICAL_SLOT_CONTRACT` | `NORMALIZED_SAME_CONTRACT_DIFFERENT_INCOMING_STATE` |
| `chap` | `CH+A_ADDR` | `CH+A_ADDR+P` | `IDENTICAL_SLOT_CONTRACT` | `NORMALIZED_SAME_CONTRACT_DIFFERENT_INCOMING_STATE` |
| `chckhedy` | `K+E+DY` | `CH+CH+K+E+DY` | `IDENTICAL_SLOT_CONTRACT` | `NORMALIZED_SAME_CONTRACT_DIFFERENT_INCOMING_STATE` |
| `chepos` | `CH+E+P` | `CH+E+P+O+S` | `IDENTICAL_SLOT_CONTRACT` | `NORMALIZED_SAME_CONTRACT_DIFFERENT_INCOMING_STATE` |
| `folchol` | `OL+OL` | `LOCAL_CHAR_F+OL+OL` | `IDENTICAL_SLOT_CONTRACT` | `NORMALIZED_SAME_CONTRACT_DIFFERENT_INCOMING_STATE` |
| `kody` | `O+DY` | `K+O+DY` | `TARGET_CONTRACT_NARROWER_BY_VISIBLE_EXTENSION` | `NORMALIZED_EXTENSION_FILLS_OPEN_SLOT` |
| `qoekedy` | `K+E+DY` | `CARRIER_Q+O+E+K+E+DY` | `IDENTICAL_SLOT_CONTRACT` | `NORMALIZED_SAME_CONTRACT_DIFFERENT_INCOMING_STATE` |
| `qokshd` | `OK+SH` | `OK+SH+D_ADDR` | `IDENTICAL_SLOT_CONTRACT` | `NORMALIZED_SAME_CONTRACT_DIFFERENT_INCOMING_STATE` |
| `qoteeod` | `OT+EE+O` | `OT+EE+O+D_ADDR` | `IDENTICAL_SLOT_CONTRACT` | `NORMALIZED_SAME_CONTRACT_DIFFERENT_INCOMING_STATE` |
| `saiis` | `S+A_ADDR` | `S+A_ADDR+IIN+S` | `IDENTICAL_SLOT_CONTRACT` | `NORMALIZED_SAME_CONTRACT_DIFFERENT_INCOMING_STATE` |
| `shokaiir` | `OK+IIN+R` | `SH+OK+IIN+R` | `IDENTICAL_SLOT_CONTRACT` | `NORMALIZED_SAME_CONTRACT_DIFFERENT_INCOMING_STATE` |
| `tosheo` | `O+SH+E+O` | `T+O+SH+E+O` | `IDENTICAL_SLOT_CONTRACT` | `NORMALIZED_SAME_CONTRACT_DIFFERENT_INCOMING_STATE` |

## Die vier bisher offenen Karten

Ihre sichtbaren Zerlegungen und vollständigen Arbeitslesungen bleiben unverändert. Geschlossen wird nur die unnötige Forderung, der alte Stamm müsse in einem anderen Satz denselben konkreten Eingangszustand zeigen.

### `folchol`

- sichtbar: `f→LOCAL_CHAR_F | ol→OL | chol→OL`
- Rezept: `LOCAL_CHAR_F+OL+OL`
- Vertrag: `ACTION_OPEN/ARGUMENT_OPEN`; erlaubt `SELF_CONTAINED|REQUIRES_ACTIVE_ARGUMENT|REQUIRES_ACTIVE_ACTION|REQUIRES_ACTIVE_ACTION_AND_ARGUMENT`
- Instanzen: Stamm `REQUIRES_ACTIVE_ACTION_AND_ARGUMENT`, Ziel `REQUIRES_ACTIVE_ACTION`
- neutral: Hier; zweimal fortsetzen.
- im bekannten Satz: Im laufenden Satz halte; an der bezeichneten Stelle; führe 2-mal fort.

### `qoteeod`

- sichtbar: `qot→OT | eeod→EE+O+D_ADDR`
- Rezept: `OT+EE+O+D_ADDR`
- Vertrag: `ACTION_OPEN/ARGUMENT_OPEN`; erlaubt `SELF_CONTAINED|REQUIRES_ACTIVE_ARGUMENT|REQUIRES_ACTIVE_ACTION|REQUIRES_ACTIVE_ACTION_AND_ARGUMENT`
- Instanzen: Stamm `SELF_CONTAINED`, Ziel `REQUIRES_ACTIVE_ACTION_AND_ARGUMENT`
- neutral: Danach; auf Grad II; zur Ausführung; hier.
- im bekannten Satz: Danach: im laufenden Satz halte den laufenden Eintrag [wie zuvor] fest; auf Grad II und zur Ausführung; an der bezeichneten Stelle.

### `saiis`

- sichtbar: `s→S | aiis→A_ADDR+IIN+S`
- Rezept: `S+A_ADDR+IIN+S`
- Vertrag: `ACTION_VISIBLE/ARGUMENT_OPEN`; erlaubt `SELF_CONTAINED|REQUIRES_ACTIVE_ARGUMENT`
- Instanzen: Stamm `REQUIRES_ACTIVE_ARGUMENT`, Ziel `SELF_CONTAINED`
- neutral: Zweimal wählen; hier; auf der bezeichneten Stufe.
- im bekannten Satz: Wähle und wähle; auf der bezeichneten Stufe; an der bezeichneten Stelle.

### `shokaiir`

- sichtbar: `sh→SH | okaiir→OK+IIN+R`
- Rezept: `SH+OK+IIN+R`
- Vertrag: `ACTION_VISIBLE/ARGUMENT_OPEN`; erlaubt `SELF_CONTAINED|REQUIRES_ACTIVE_ARGUMENT`
- Instanzen: Stamm `REQUIRES_ACTIVE_ARGUMENT`, Ziel `SELF_CONTAINED`
- neutral: Halten, setzen und markieren; auf der bezeichneten Stufe.
- im bekannten Satz: Halte fest, trage ein und kennzeichne; auf der bezeichneten Stufe.

## Aktive Restliste

Es bleiben 5 echte direkte Grenzflächenfragen: `aiicthy:AIIN>CH`, `chap:A_ADDR>P`, `ofaram:AR>AM_ADDR`, `rotaiin:R>OT`, `shso:SH>S`.

Das ist eine Normalisierung innerhalb des bestehenden Arbeitslesers. Sie bestätigt weder Klartext noch Lexeme, Sprache, Chiffre oder historische Identität und ändert keine Stammwerte.
