# GDT488 — Einmal gelockerte Aktionsendpunkte

GDT488 lockert am GDT486-Paarbau immer nur eine Sache: entweder darf das Register wechseln, während der komplette Recordrahmen gleich bleibt, oder zwei einzelne Events dürfen aus ihrem größeren Recordrahmen heraus verglichen werden. Modell, Eventseparatoren, Komponentenpositionen und alle nicht gewechselten Komponenten bleiben fest.

- Register-only-Paare an den zwei Endpunkten: **1**.
- Exakte Event-Minimalpaare: **5**, davon **3** neu gegenüber GDT486.
- `HALTEN`: **Zyklus geschlossen**; `EINSTELLEN`: **weiter kapazitätsbegrenzt**.

## Der neue HALTEN-Zyklus

`HALTEN —G488 REGISTER_ONLY→ BAHN —G486 RECURRENT→ ZIELORT —G486 SINGLETON→ HALTEN`

Die neue Kante `G475-R035~G475-R129` hält aktives Modell, Satzrahmen, Eventform und alle übrigen Komponenten fest. Nur das Register und damit die Besitzerart wechseln. Die Kante `BAHN~ZIELORT` ist bereits 2fach wiederkehrend.

### Register-only-Paar

| Records | Register | Rahmen | Wechsel | Lesungen |
|---|---|---|---|---|
| `G475-R035 ↔ G475-R129` | CELESTIAL → PHARMA | `INSTRUCTION_SETZEN` | `BAHN ↔ HALTEN` | Setze den Sternstelleneintrag »y« entlang der Ringbahn. / Setze den Drogeneintrag »dchos« als Ansatz an und halte ihn. |

### Neue Eventprojektionen

| Events | Ort | Wechsel | Wildcard-Rahmen |
|---|---|---|---|
| `G485-E022 ↔ G485-E023` | f71v / f71v | `DANACH ↔ HALTEN` | `* · AUSGANG` |
| `G485-E041 ↔ G485-E050` | f72r / f72r | `HALTEN ↔ SETZEN` | `* · AUSGANG · HIER` |
| `G485-E169 ↔ G485-E168` | f89r / f89r | `HALTEN ↔ SETZEN` | `* · FORTSETZEN` |

Damit erscheint HALTEN außer gegen ZIELORT nun auch gegen BAHN sowie auf Eventebene gegen DANACH und SETZEN. Die Eventpaare sind zusätzliche Redaktionskontraste; für den geschlossenen Weg genügt bereits das sauberere Register-only-Paar BAHN ↔ HALTEN.

## Warum EINSTELLEN offen bleibt

EINSTELLEN kommt in den 183 Events genau zweimal vor:

| Event | Seite / Register | Rezept | Kontext | GDT428-Rahmen |
|---|---|---|---|---|
| `G485-E118` | f72r / CELESTIAL | `CH+T` | `CH+@ACTION` | `CH+@ACTION` |
| `G485-E133` | f88v / PHARMA | `CH+T+Y` | `CH+@ACTION+Y` | `NONE` |

Der pharmazeutische Träger ist die bekannte GDT486-Kante EINSTELLEN ↔ HIER. Der celestialische Träger wiederholt NEHMEN→EINSTELLEN und trifft mit `CH+@ACTION` sogar einen exakten GDT428-T/R-Rahmen. Er liefert aber keinen zweiten lokalen Austauschpartner. Unter den beiden einmaligen Lockerungen entstehen daher **null** neue EINSTELLEN-Kontraste.

Das ist kein Bedeutungsproblem: Die Lesung „einstellen“ bleibt zweimal lokal sichtbar und elf externe T/R-Rahmen trennen sie von MARKIEREN. Es fehlt lediglich ein zweiter lokaler Ersatzrahmen.

## Endstand

| Endpunkt | lokale Events | strikte GDT486-Kante | neue Kanten | Ergebnis |
|---|---:|---|---|---|
| `EINSTELLEN` | 2 | `HIER` | `NONE` | `CAPACITY_LIMITED_ENDPOINT_RETAINED` |
| `HALTEN` | 12 | `ZIELORT` | `BAHN|DANACH|SETZEN` | `FULL_ALTERNATE_CYCLE_CLOSED` |

## Nächster Schritt

HALTEN braucht keine weitere Lockerung. Für EINSTELLEN sollte der Ersatzgraph nicht nochmals verbreitert werden. Stattdessen ist sein bereits vorhandenes Kompositionsumfeld auszubauen: die elf GDT428-T/R-Rahmen nach ihren stabilen Nachbarn WERT, ANTEIL, ZIELORT, FORTSETZEN und POSTEN ordnen und prüfen, welche davon in den 183 lokalen Events bereits als unveränderte Teilrahmen auftauchen.
