# GDT477 — OL-Richtungssprachführer

`OL=FORTSETZEN` braucht keine zweite Wortbedeutung. Seine Stellung in der vollständigen Funktion/Namens-Spur bestimmt, wohin die Fortsetzung greift: nach rechts, von links nach rechts oder zurück auf den linken Träger.

| Stellung | Formel | Vorkommen | Ereignisse | konkrete Default-Lesung |
|---|---|---:|---:|---|
| FORWARD_OPEN | `OL · X = weiter mit X` | 9 | 9 | weiter mit dem rechten Träger |
| BRIDGE_LEFT_TO_RIGHT | `X · OL · Y = X in Y weiterführen` | 10 | 10 | den linken Träger in den rechten weiterführen |
| BACKWARD_HOLD | `X · OL = X weiterführen` | 9 | 9 | den linken Träger weiterführen |

Die Teilung ist vollständig: alle neun vorangestellten OL eröffnen eine Funktionskette; alle sechzehn karteninternen OL sind entweder Brücke (8) oder Rückhalt (8). Die elf recordbindenden OL dürfen trotzdem alle drei Richtungen tragen: acht öffnen nach rechts, zwei stehen als Brücke und eines hält einen links stehenden Namen weiter aktiv.

Die ältere Kanalkalibrierung passt dazu: freies linkes `ol-` trifft 54/56 Erweiterungstypen auf 20 Seiten; rechtes `-ol` trifft 102/111 auf 24 Seiten. Beide Richtungen sind alte Karten, keine Notkorrekturen.

## Alle 28 OL-Stellen

### f71v

2 OL-Stellen in 2 Ereignissen: 0 öffnend, 2 Brücken, 0 rückhaltend.

| Form · Locus | markierte Literalfolge | Stellung | OL-Scope | aktive Ereignislesung |
|---|---|---|---|---|
| `okolar` · f71v.4 | SETZEN · ⟦FORTSETZEN⟧ · AUSGANG | BRIDGE_LEFT_TO_RIGHT / NAME_FREE | Setzen in Ausgang weiterführen | Weiter setze den Eintrag von der Ausgangsposition. |
| `sholshdy` · f71v.17 | HALTEN · ⟦FORTSETZEN⟧ · HALTEN · [STERNSTELLENNAME:dy] | BRIDGE_LEFT_TO_RIGHT / PRE_NAME | Halten in Halten weiterführen | Weiter halte den Sternstelleneintrag »dy« und halte den Sternstelleneintrag »dy«. |

### f72r

11 OL-Stellen in 10 Ereignissen: 6 öffnend, 3 Brücken, 2 rückhaltend.

| Form · Locus | markierte Literalfolge | Stellung | OL-Scope | aktive Ereignislesung |
|---|---|---|---|---|
| `ochol` · f72r1.11 | AUSFÜHRUNG · ⟦FORTSETZEN⟧ | BACKWARD_HOLD / NAME_FREE | Ausführung weiterführen | Weiter beziehe den Eintrag, als Ausführung. |
| `otolam` · f72r2.21 | DANACH · ⟦FORTSETZEN⟧ · HIER | BRIDGE_LEFT_TO_RIGHT / NAME_FREE | Folgeschritt in bezeichnete Stelle weiterführen | Adressspur: danach → weiter → hier. |
| `olkalaiin` · f72r3.2 | ⟦FORTSETZEN⟧ · [STERNSTELLENNAME:k] · ZIELORT · WERT | FORWARD_OPEN / PRE_NAME | weiter mit Sternstelle »k« | Weiter beziehe den Sternstelleneintrag »k« und den Positionswert zur Zielposition. |
| `olalsy` · f72r3.3 | ⟦FORTSETZEN⟧ · ZIELORT · POSTEN | FORWARD_OPEN / NAME_FREE | weiter mit Zielort | Adressspur: weiter → Zielposition → Positionsposten. |
| `ofsholdy` · f72r3.11 | AUSFÜHRUNG · HIER · HALTEN · ⟦FORTSETZEN⟧ · [STERNSTELLENNAME:dy] | BRIDGE_LEFT_TO_RIGHT / PRE_NAME | Halten in Sternstelle »dy« weiterführen | Weiter halte den Sternstelleneintrag »dy«, als Ausführung an der bezeichneten Stelle. |
| `ykolairol` · f72r3.13 | [STERNSTELLENNAME:yk] · ⟦FORTSETZEN⟧ · BAHN · FORTSETZEN | BRIDGE_LEFT_TO_RIGHT / POST_NAME | Sternstelle »yk« in Bahn weiterführen | Weiter und weiter beziehe den Sternstelleneintrag »yk« entlang der Ringbahn. |
| `ykolairol` · f72r3.13 | [STERNSTELLENNAME:yk] · FORTSETZEN · BAHN · ⟦FORTSETZEN⟧ | BACKWARD_HOLD / POST_NAME | Bahn weiterführen | Weiter und weiter beziehe den Sternstelleneintrag »yk« entlang der Ringbahn. |
| `olaiin` · f72r3.24 | ⟦FORTSETZEN⟧ · WERT | FORWARD_OPEN / NAME_FREE | weiter mit Wert | Eintrag »olaiin« — Fortsetzungsvermerk, Wertangabe. |
| `olay` · f72r3.24 | ⟦FORTSETZEN⟧ · [STERNSTELLENNAME:ay] | FORWARD_OPEN / PRE_NAME | weiter mit Sternstelle »ay« | Sternstelle »ay« — Fortsetzungsvermerk. |
| `olfsheoral` · f72r3.25 | ⟦FORTSETZEN⟧ · [STERNSTELLENNAME:f] · HALTEN · [STERNSTELLENNAME:eor] · ZIELORT | FORWARD_OPEN / PRE_NAME | weiter mit Sternstelle »f« | Weiter halte den Sternstelleneintrag »f« und den Sternstelleneintrag »eor« zur Zielposition. |
| `oletal` · f72r3.33 | ⟦FORTSETZEN⟧ · [STERNSTELLENNAME:et] · ZIELORT | FORWARD_OPEN / PRE_NAME | weiter mit Sternstelle »et« | Adressspur: weiter → Sternstelle »et« → Zielposition. |

### f77r

3 OL-Stellen in 3 Ereignissen: 1 öffnend, 1 Brücken, 1 rückhaltend.

| Form · Locus | markierte Literalfolge | Stellung | OL-Scope | aktive Ereignislesung |
|---|---|---|---|---|
| `olkchs` · f77r.2 | ⟦FORTSETZEN⟧ · [BADSTATIONSNAME:kchs] | FORWARD_OPEN / PRE_NAME | weiter mit Badstation »kchs« | Badstation »kchs« — Fortsetzungsvermerk. |
| `otol` · f77r.5 | DANACH · ⟦FORTSETZEN⟧ | BACKWARD_HOLD / NAME_FREE | Folgeschritt weiterführen | Adressspur: danach → weiter. |
| `otolaiin` · f77r.50 | DANACH · ⟦FORTSETZEN⟧ · WERT | BRIDGE_LEFT_TO_RIGHT / NAME_FREE | Folgeschritt in Wert weiterführen | Adressspur: danach → weiter → Stationswert. |

### f88v

1 OL-Stellen in 1 Ereignissen: 0 öffnend, 0 Brücken, 1 rückhaltend.

| Form · Locus | markierte Literalfolge | Stellung | OL-Scope | aktive Ereignislesung |
|---|---|---|---|---|
| `otokol` · f88v.5 | DANACH · SETZEN · ⟦FORTSETZEN⟧ | BACKWARD_HOLD / NAME_FREE | Setzen weiterführen | Danach und weiter setze den Eintrag als Ansatz an. |

### f89r

11 OL-Stellen in 10 Ereignissen: 2 öffnend, 4 Brücken, 5 rückhaltend.

| Form · Locus | markierte Literalfolge | Stellung | OL-Scope | aktive Ereignislesung |
|---|---|---|---|---|
| `qkol` · f89r1.2 | [DROGENNAME:qk] · ⟦FORTSETZEN⟧ | BACKWARD_HOLD / POST_NAME | Droge »qk« weiterführen | Weiter beziehe den Drogeneintrag »qk«. |
| `oldam` · f89r1.3 | ⟦FORTSETZEN⟧ · [DROGENNAME:d] · HIER | FORWARD_OPEN / PRE_NAME | weiter mit Droge »d« | Weiter beziehe den Drogeneintrag »d« an der bezeichneten Stelle. |
| `otoldy` · f89r1.4 | DANACH · ⟦FORTSETZEN⟧ · [DROGENNAME:dy] | BRIDGE_LEFT_TO_RIGHT / PRE_NAME | Folgeschritt in Droge »dy« weiterführen | Droge »dy« — Folgevermerk, Fortsetzungsvermerk. |
| `chol` · f89r1.12 | ⟦FORTSETZEN⟧ | FORWARD_OPEN / NAME_FREE | im aktiven Eintrag weiter | Weiter beziehe den Eintrag. |
| `doly` · f89r2.2 | [DROGENNAME:d] · ⟦FORTSETZEN⟧ · POSTEN | BRIDGE_LEFT_TO_RIGHT / POST_NAME | Droge »d« in Posten weiterführen | Droge »d« — Fortsetzungsvermerk, Postenangabe. |
| `saloiinsheol` · f89r2.4 | [DROGENNAME:s] · ZIELORT · [DROGENNAME:oiin] · HALTEN · [DROGENNAME:e] · ⟦FORTSETZEN⟧ | BACKWARD_HOLD / POST_NAME | Droge »e« weiterführen | Weiter halte den Drogeneintrag »s«, den Drogeneintrag »oiin« und den Drogeneintrag »e« zum Zielgefäß. |
| `otold` · f89r2.9 | DANACH · ⟦FORTSETZEN⟧ · [DROGENNAME:d] | BRIDGE_LEFT_TO_RIGHT / PRE_NAME | Folgeschritt in Droge »d« weiterführen | Droge »d« — Folgevermerk, Fortsetzungsvermerk. |
| `okol` · f89r2.10 | SETZEN · ⟦FORTSETZEN⟧ | BACKWARD_HOLD / NAME_FREE | Setzen weiterführen | Weiter setze den Eintrag als Ansatz an. |
| `shol` · f89r2.10 | HALTEN · ⟦FORTSETZEN⟧ | BACKWARD_HOLD / NAME_FREE | Halten weiterführen | Weiter halte den Eintrag. |
| `otolarol` · f89r2.34 | DANACH · ⟦FORTSETZEN⟧ · AUSGANG · FORTSETZEN | BRIDGE_LEFT_TO_RIGHT / NAME_FREE | Folgeschritt in Ausgang weiterführen | Adressspur: danach → weiter → Ausgangsgefäß → weiter. |
| `otolarol` · f89r2.34 | DANACH · FORTSETZEN · AUSGANG · ⟦FORTSETZEN⟧ | BACKWARD_HOLD / NAME_FREE | Ausgang weiterführen | Adressspur: danach → weiter → Ausgangsgefäß → weiter. |

## Ereignisebene

Die 28 Stellen gehören zu 26 Ereignissen. Zwei Formen (`ykolairol`, `otolarol`) enthalten je zwei OL-Slots; ihre beiden Richtungslesungen bleiben getrennt und werden nicht zu einem angeblich komplexen Einzelwort zusammengeschoben.
