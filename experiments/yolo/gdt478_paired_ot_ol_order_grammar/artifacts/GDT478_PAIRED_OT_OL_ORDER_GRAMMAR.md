# GDT478 — gepaarte OT/OL-Reihenfolgegrammatik

Die beiden Reihenfolgestämme sind jetzt als unterschiedliche Zustandsoperationen lesbar: `OT=DANACH` eröffnet den nächsten Träger; `OL=FORTSETZEN` hält den aktuellen Träger aktiv und führt ihn je nach Stellung weiter.

| Stamm | Kernoperation | Richtungsformen | Slots |
|---|---|---|---:|
| OT / DANACH | neuen Geschwisterträger beginnen | 40 vorwärts + 1 Namensbrücke + 0 rückwärts | 41 |
| OL / FORTSETZEN | aktiven Träger beibehalten | 9 vorwärts + 10 Brücken + 9 rückwärts | 28 |

## Die fünf ausführbaren Stellungsregeln

| Stamm | Stellung | Formel | Operation | Vorkommen |
|---|---|---|---|---:|
| OT | FORWARD_OPEN | `OT · X = nächster Träger: X` | START_FRESH_SIBLING | 40 |
| OT | BRIDGE_LEFT_TO_RIGHT | `X · OT · Y = nach X folgt Y` | START_FRESH_SIBLING | 1 |
| OL | FORWARD_OPEN | `OL · X = weiter mit X` | KEEP_ACTIVE_UNIT | 9 |
| OL | BRIDGE_LEFT_TO_RIGHT | `X · OL · Y = X in Y weiterführen` | KEEP_ACTIVE_UNIT | 10 |
| OL | BACKWARD_HOLD | `X · OL = X weiterführen` | KEEP_ACTIVE_UNIT | 9 |

## Die sieben gemeinsamen OT+OL-Ereignisse

In allen sieben steht OT vor OL: zuerst wird der neue Träger eröffnet, danach wird genau dieser Träger weitergeführt. Damit liest sich `otol` nicht als kompliziertes Ganzwort, sondern als zwei aufeinanderfolgende Steuerkarten.

| Seite · Locus | Form | Wurzelfolge | Zustandsfolge | konkrete Reihenfolgelesung |
|---|---|---|---|---|
| f72r · f72r2.21 | `otolam` | OT\|OL | START_FRESH_SIBLING\|KEEP_ACTIVE_UNIT | OT: danach Fortsetzung; OL: Folgeschritt in bezeichnete Stelle weiterführen |
| f77r · f77r.5 | `otol` | OT\|OL | START_FRESH_SIBLING\|KEEP_ACTIVE_UNIT | OT: danach Fortsetzung; OL: Folgeschritt weiterführen |
| f77r · f77r.50 | `otolaiin` | OT\|OL | START_FRESH_SIBLING\|KEEP_ACTIVE_UNIT | OT: danach Fortsetzung; OL: Folgeschritt in Wert weiterführen |
| f88v · f88v.5 | `otokol` | OT\|OL | START_FRESH_SIBLING\|KEEP_ACTIVE_UNIT | OT: danach Setzen; OL: Setzen weiterführen |
| f89r · f89r1.4 | `otoldy` | OT\|OL | START_FRESH_SIBLING\|KEEP_ACTIVE_UNIT | OT: danach Fortsetzung; OL: Folgeschritt in Droge »dy« weiterführen |
| f89r · f89r2.9 | `otold` | OT\|OL | START_FRESH_SIBLING\|KEEP_ACTIVE_UNIT | OT: danach Fortsetzung; OL: Folgeschritt in Droge »d« weiterführen |
| f89r · f89r2.34 | `otolarol` | OT\|OL\|OL | START_FRESH_SIBLING\|KEEP_ACTIVE_UNIT\|KEEP_ACTIVE_UNIT | OT: danach Fortsetzung; OL: Folgeschritt in Ausgang weiterführen; OL: Ausgang weiterführen |

## Alle 41 OT-Stellen

### f17r

1 OT-Stellen; 1 vorwärts und 0 als Brücke.

| Form · Locus | markierte Literalfolge | Nameposition | OT-Scope | aktive Ereignislesung |
|---|---|---|---|---|
| `oteeeon` · f17r.13 | ⟦DANACH⟧ · [PFLANZENNAME:eeeon] | PRE_NAME | danach Pflanze »eeeon« | Pflanzenname »eeeon« — Folgevermerk. |

### f71v

6 OT-Stellen; 6 vorwärts und 0 als Brücke.

| Form · Locus | markierte Literalfolge | Nameposition | OT-Scope | aktive Ereignislesung |
|---|---|---|---|---|
| `otchody` · f71v.5 | ⟦DANACH⟧ · [STERNSTELLENNAME:chody] | PRE_NAME | danach Sternstelle »chody« | Sternstelle »chody« — Folgevermerk. |
| `otaiin` · f71v.7 | ⟦DANACH⟧ · WERT | NAME_FREE | danach Wert | Adressspur: danach → Positionswert. |
| `otar` · f71v.9 | ⟦DANACH⟧ · AUSGANG | NAME_FREE | danach Ausgang | Adressspur: danach → Ausgangsposition. |
| `otalody` · f71v.14 | ⟦DANACH⟧ · ZIELORT · [STERNSTELLENNAME:ody] | PRE_NAME | danach Zielort | Sternstelle »ody« — Folgevermerk, Zielzuordnung. |
| `otalaiin` · f71v.15 | ⟦DANACH⟧ · ZIELORT · WERT | NAME_FREE | danach Zielort | Adressspur: danach → Zielposition → Positionswert. |
| `otar` · f71v.16 | ⟦DANACH⟧ · AUSGANG | NAME_FREE | danach Ausgang | Danach beziehe den Eintrag von der Ausgangsposition. |

### f72r

17 OT-Stellen; 17 vorwärts und 0 als Brücke.

| Form · Locus | markierte Literalfolge | Nameposition | OT-Scope | aktive Ereignislesung |
|---|---|---|---|---|
| `otaraldy` · f72r1.8 | ⟦DANACH⟧ · AUSGANG · ZIELORT · POSTEN | NAME_FREE | danach Ausgang | Adressspur: danach → Ausgangsposition → Zielposition → Positionsposten. |
| `otaiin` · f72r1.9 | ⟦DANACH⟧ · WERT | NAME_FREE | danach Wert | Adressspur: danach → Positionswert. |
| `otain` · f72r1.9 | ⟦DANACH⟧ · ANTEIL | NAME_FREE | danach Anteil | Adressspur: danach → Sektoranteil. |
| `otalef` · f72r1.10 | ⟦DANACH⟧ · ZIELORT · [STERNSTELLENNAME:ef] | PRE_NAME | danach Zielort | Danach beziehe den Sternstelleneintrag »ef« zur Zielposition. |
| `otchoshy` · f72r1.14 | ⟦DANACH⟧ · [STERNSTELLENNAME:cho] · POSTEN | PRE_NAME | danach Sternstelle »cho« | Sternstelle »cho« — Folgevermerk, Postenangabe. |
| `otchdal` · f72r1.15 | ⟦DANACH⟧ · [STERNSTELLENNAME:ch] · ZIELORT | PRE_NAME | danach Sternstelle »ch« | Sternstelle »ch« — Folgevermerk, Zielzuordnung. |
| `otainy` · f72r1.17 | ⟦DANACH⟧ · ANTEIL · POSTEN | NAME_FREE | danach Anteil | Adressspur: danach → Sektoranteil → Positionsposten. |
| `otaraldy` · f72r2.7 | ⟦DANACH⟧ · AUSGANG · ZIELORT · POSTEN | NAME_FREE | danach Ausgang | Adressspur: danach → Ausgangsposition → Zielposition → Positionsposten. |
| `oteeary` · f72r2.13 | ⟦DANACH⟧ · [STERNSTELLENNAME:ee] · AUSGANG · [STERNSTELLENNAME:y] | PRE_NAME | danach Sternstelle »ee« | Sternstelle »ee« / Sternstelle »y« — Folgevermerk, Ausgangszuordnung. |
| `otair` · f72r2.14 | ⟦DANACH⟧ · BAHN | NAME_FREE | danach Bahn | Adressspur: danach → Ringbahn. |
| `otar` · f72r2.17 | ⟦DANACH⟧ · AUSGANG | NAME_FREE | danach Ausgang | Adressspur: danach → Ausgangsposition. |
| `otolam` · f72r2.21 | ⟦DANACH⟧ · FORTSETZEN · HIER | NAME_FREE | danach Fortsetzung | Adressspur: danach → weiter → hier. |
| `otal` · f72r2.23 | ⟦DANACH⟧ · ZIELORT | NAME_FREE | danach Zielort | Adressspur: danach → Zielposition. |
| `otalshy` · f72r2.26 | ⟦DANACH⟧ · ZIELORT · POSTEN | NAME_FREE | danach Zielort | Adressspur: danach → Zielposition → Positionsposten. |
| `otam` · f72r2.29 | ⟦DANACH⟧ · HIER | NAME_FREE | danach bezeichnete Stelle | Adressspur: danach → hier. |
| `oto` · f72r3.6 | ⟦DANACH⟧ · AUSFÜHRUNG | NAME_FREE | danach Ausführung | Adressspur: danach → Ausführungspunkt. |
| `oteey` · f72r3.9 | ⟦DANACH⟧ · GRAD II · POSTEN | NAME_FREE | danach Grad II | Adressspur: danach → Grad II → Positionsposten. |

### f77r

6 OT-Stellen; 5 vorwärts und 1 als Brücke.

| Form · Locus | markierte Literalfolge | Nameposition | OT-Scope | aktive Ereignislesung |
|---|---|---|---|---|
| `otedy` · f77r.3 | ⟦DANACH⟧ · GRAD I · SCHLUSS | NAME_FREE | danach Grad I | Adressspur: danach → Grad I → Endpunkt. |
| `otork` · f77r.4 | ⟦DANACH⟧ · [BADSTATIONSNAME:ork] | PRE_NAME | danach Badstation »ork« | Badstation »ork« — Folgevermerk. |
| `otol` · f77r.5 | ⟦DANACH⟧ · FORTSETZEN | NAME_FREE | danach Fortsetzung | Adressspur: danach → weiter. |
| `dotedy` · f77r.8 | [BADSTATIONSNAME:d] · ⟦DANACH⟧ · [BADSTATIONSNAME:edy] | BETWEEN_NAMES | nach Badstation »d« folgt Badstation »edy« | Badstation »d« / Badstation »edy« — Folgevermerk. |
| `otchdy` · f77r.49 | ⟦DANACH⟧ · BEARBEITEN · SCHLUSS | NAME_FREE | danach Bearbeiten | Danach bearbeite den Eintrag, und schließe den Schritt. |
| `otolaiin` · f77r.50 | ⟦DANACH⟧ · FORTSETZEN · WERT | NAME_FREE | danach Fortsetzung | Adressspur: danach → weiter → Stationswert. |

### f88v

6 OT-Stellen; 6 vorwärts und 0 als Brücke.

| Form · Locus | markierte Literalfolge | Nameposition | OT-Scope | aktive Ereignislesung |
|---|---|---|---|---|
| `otar` · f88v.4 | ⟦DANACH⟧ · AUSGANG | NAME_FREE | danach Ausgang | Eintrag »otar« — Folgevermerk, Ausgangszuordnung. |
| `otokol` · f88v.5 | ⟦DANACH⟧ · SETZEN · FORTSETZEN | NAME_FREE | danach Setzen | Danach und weiter setze den Eintrag als Ansatz an. |
| `otoram` · f88v.11 | ⟦DANACH⟧ · [DROGENNAME:or] · HIER | PRE_NAME | danach Droge »or« | Droge »or« — Folgevermerk, Hier-Vermerk. |
| `otora` · f88v.12 | ⟦DANACH⟧ · [DROGENNAME:ora] | PRE_NAME | danach Droge »ora« | Droge »ora« — Folgevermerk. |
| `otydary` · f88v.28 | ⟦DANACH⟧ · [DROGENNAME:y] · HIER · AUSGANG · [DROGENNAME:y] | PRE_NAME | danach Droge »y« | Droge »y« / Droge »y« — Folgevermerk, Hier-Vermerk, Ausgangszuordnung. |
| `otdordy` · f88v.29 | ⟦DANACH⟧ · [DROGENNAME:dordy] | PRE_NAME | danach Droge »dordy« | Droge »dordy« — Folgevermerk. |

### f89r

5 OT-Stellen; 5 vorwärts und 0 als Brücke.

| Form · Locus | markierte Literalfolge | Nameposition | OT-Scope | aktive Ereignislesung |
|---|---|---|---|---|
| `otoldy` · f89r1.4 | ⟦DANACH⟧ · FORTSETZEN · [DROGENNAME:dy] | PRE_NAME | danach Fortsetzung | Droge »dy« — Folgevermerk, Fortsetzungsvermerk. |
| `otorain` · f89r1.13 | ⟦DANACH⟧ · [DROGENNAME:or] · ANTEIL | PRE_NAME | danach Droge »or« | Droge »or« — Folgevermerk, Anteilsangabe. |
| `otold` · f89r2.9 | ⟦DANACH⟧ · FORTSETZEN · [DROGENNAME:d] | PRE_NAME | danach Fortsetzung | Droge »d« — Folgevermerk, Fortsetzungsvermerk. |
| `otalsy` · f89r2.32 | ⟦DANACH⟧ · ZIELORT · POSTEN | NAME_FREE | danach Zielort | Adressspur: danach → Zielgefäß → Drogenposten. |
| `otolarol` · f89r2.34 | ⟦DANACH⟧ · FORTSETZEN · AUSGANG · FORTSETZEN | NAME_FREE | danach Fortsetzung | Adressspur: danach → weiter → Ausgangsgefäß → weiter. |
