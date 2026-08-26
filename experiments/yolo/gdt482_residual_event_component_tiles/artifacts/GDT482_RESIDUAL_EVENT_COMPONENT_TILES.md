# GDT482 — interne Komponenten-Kacheln der 45 Restevents

Die 45 GDT481-Einzelevent-Resttails werden aus geordneten Bedeutungsfragmenten der Länge eins bis drei neu zusammengesetzt. Ein Fragment zählt nur als wiederkehrend, wenn mindestens ein anderes Event es trägt.

| Ergebnis unter gleichem Grammatikmodell | Events |
|---|---:|
| vollständig durch wiederkehrende Mehrkomponentenfragmente | 14 |
| Mehrkomponentenfragmente plus wiederkehrende Einzelkomponenten | 21 |
| nur wiederkehrende Einzelkomponenten | 4 |
| mindestens ein lokaler Token bleibt | 6 |

Damit sind 39/45 Restevents unter ihrem aktiven Modell vollständig aus anderswo sichtbaren Teilbedeutungen gebaut. Modellfrei steigt die Zahl auf 42/45; diese Zusatzrettungen bleiben als Backoff markiert.

| Interpretation des Restes | Events |
|---|---:|
| im aktiven Modell vollständig wiederkehrend | 39 |
| nur modellfrei vollständig wiederkehrend | 3 |
| nur ein gelernter Name/Familienname bleibt lokal | 2 |
| einmalige Funktionskomponente bleibt | 1 |

Die drei auch nach dem modellfreien Backoff verbleibenden Restevents sind nicht gleichartig. `cheosdy` behält den gelernten Familiennamen `cheo`; `saloiinsheol` behält den dritten gelernten Drogennamen. Nur `sodar` trägt mit `ZWEITE STUFE` und `MARKIEREN` funktionale Bedeutungsbausteine, die in keinem anderen der 183 Events vorkommen.

## Alle 45 Restevents

### P1003-E0598 · `okolar` · INSTRUCTION

- Komponenten: `SETZEN · FORTSETZEN · AUSGANG`
- Kachelung im Modell: `[SETZEN · FORTSETZEN ×2] + [AUSGANG ×12]`
- Klasse: **MIXED_RECURRENT_MULTI_PLUS_ATOMS**; 3/3 Tokens wiederkehrend, davon 2 in Mehrkomponentenfragmenten.
- Modellfreier Backoff: `[SETZEN · FORTSETZEN ×2] + [AUSGANG ×44]` (MIXED_RECURRENT_MULTI_PLUS_ATOMS).
- Resttyp: **MODEL_CONDITIONED_RECURRENT**.
- Arbeitslesung: Weiter setze den Eintrag von der Ausgangsposition. Reihenfolge konkret: OL — Setzen in Ausgang weiterführen.

### P1003-E0600 · `alcphy` · INSTRUCTION

- Komponenten: `ZIELORT · NEHMEN · EINSETZEN · POSTEN`
- Kachelung im Modell: `[ZIELORT ×17] + [NEHMEN ×9] + [EINSETZEN ×1] + [POSTEN ×18]`
- Klasse: **RECURRENT_ATOMS_ONLY**; 4/4 Tokens wiederkehrend, davon 0 in Mehrkomponentenfragmenten.
- Modellfreier Backoff: `[ZIELORT ×47] + [NEHMEN ×9] + [EINSETZEN ×1] + [POSTEN ×39]` (RECURRENT_ATOMS_ONLY).
- Resttyp: **MODEL_CONDITIONED_RECURRENT**.
- Arbeitslesung: Nimm den Positionsposten auf und setze den Positionsposten ein zur Zielposition.

### P1003-E0642 · `otalody` · CATALOGUE

- Komponenten: `DANACH · ZIELORT · {N1}`
- Kachelung im Modell: `[DANACH ×15] + [ZIELORT · {N1} ×2]`
- Klasse: **MIXED_RECURRENT_MULTI_PLUS_ATOMS**; 3/3 Tokens wiederkehrend, davon 2 in Mehrkomponentenfragmenten.
- Modellfreier Backoff: `[DANACH · ZIELORT · {N1} ×1]` (FULL_RECURRENT_MULTI_FRAGMENT_TILE).
- Resttyp: **MODEL_CONDITIONED_RECURRENT**.
- Arbeitslesung: Sternstelle »ody« — Folgevermerk, Zielzuordnung. Reihenfolge konkret: OT — danach Zielort.

### P1003-E0646 · `sholshdy` · INSTRUCTION

- Komponenten: `HALTEN · FORTSETZEN · HALTEN · {N1}`
- Kachelung im Modell: `[HALTEN · FORTSETZEN ×2] + [HALTEN · {N1} ×1]`
- Klasse: **FULL_RECURRENT_MULTI_FRAGMENT_TILE**; 4/4 Tokens wiederkehrend, davon 4 in Mehrkomponentenfragmenten.
- Modellfreier Backoff: `[HALTEN · FORTSETZEN ×2] + [HALTEN · {N1} ×1]` (FULL_RECURRENT_MULTI_FRAGMENT_TILE).
- Resttyp: **MODEL_CONDITIONED_RECURRENT**.
- Arbeitslesung: Weiter halte den Sternstelleneintrag »dy« und halte den Sternstelleneintrag »dy«. Reihenfolge konkret: OL — Halten in Halten weiterführen.

### P1008-E0127 · `oshodady` · INSTRUCTION

- Komponenten: `{N1} · HALTEN · {N2}`
- Kachelung im Modell: `[{N1} · HALTEN · {N2} ×1]`
- Klasse: **FULL_RECURRENT_MULTI_FRAGMENT_TILE**; 3/3 Tokens wiederkehrend, davon 3 in Mehrkomponentenfragmenten.
- Modellfreier Backoff: `[{N1} · HALTEN · {N2} ×1]` (FULL_RECURRENT_MULTI_FRAGMENT_TILE).
- Resttyp: **MODEL_CONDITIONED_RECURRENT**.
- Arbeitslesung: Halte den Sternstelleneintrag »o« und den Sternstelleneintrag »odady«.

### P1008-E0171 · `ofaralar` · COORDINATE

- Komponenten: `AUSFÜHRUNG · HIER · AUSGANG · ZIELORT · AUSGANG`
- Kachelung im Modell: `[AUSFÜHRUNG ×3] + [HIER ×4] + [AUSGANG · ZIELORT ×3] + [AUSGANG ×10]`
- Klasse: **MIXED_RECURRENT_MULTI_PLUS_ATOMS**; 5/5 Tokens wiederkehrend, davon 2 in Mehrkomponentenfragmenten.
- Modellfreier Backoff: `[AUSFÜHRUNG · HIER ×5] + [AUSGANG · ZIELORT ×3] + [AUSGANG ×44]` (MIXED_RECURRENT_MULTI_PLUS_ATOMS).
- Resttyp: **MODEL_CONDITIONED_RECURRENT**.
- Arbeitslesung: Adressspur: Ausführungspunkt → hier → Ausgangsposition → Zielposition → Ausgangsposition.

### P1008-E0173 · `otchdal` · CATALOGUE

- Komponenten: `DANACH · {N1} · ZIELORT`
- Kachelung im Modell: `[DANACH · {N1} ×10] + [ZIELORT ×17]`
- Klasse: **MIXED_RECURRENT_MULTI_PLUS_ATOMS**; 3/3 Tokens wiederkehrend, davon 2 in Mehrkomponentenfragmenten.
- Modellfreier Backoff: `[DANACH · {N1} ×10] + [ZIELORT ×47]` (MIXED_RECURRENT_MULTI_PLUS_ATOMS).
- Resttyp: **MODEL_CONDITIONED_RECURRENT**.
- Arbeitslesung: Sternstelle »ch« — Folgevermerk, Zielzuordnung. Reihenfolge konkret: OT — danach Sternstelle »ch«.

### P1008-E0176 · `otainy` · COORDINATE

- Komponenten: `DANACH · ANTEIL · POSTEN`
- Kachelung im Modell: `[DANACH · ANTEIL ×1] + [POSTEN ×11]`
- Klasse: **MIXED_RECURRENT_MULTI_PLUS_ATOMS**; 3/3 Tokens wiederkehrend, davon 2 in Mehrkomponentenfragmenten.
- Modellfreier Backoff: `[DANACH · ANTEIL ×1] + [POSTEN ×39]` (MIXED_RECURRENT_MULTI_PLUS_ATOMS).
- Resttyp: **MODEL_CONDITIONED_RECURRENT**.
- Arbeitslesung: Adressspur: danach → Sektoranteil → Positionsposten. Reihenfolge konkret: OT — danach Anteil.

### P1008-E0191 · `oklairdy` · INSTRUCTION

- Komponenten: `SETZEN · {N1} · BAHN · {N2}`
- Kachelung im Modell: `[SETZEN · {N1} ×3] + [BAHN ×3] + [{N2} ×5]`
- Klasse: **MIXED_RECURRENT_MULTI_PLUS_ATOMS**; 4/4 Tokens wiederkehrend, davon 2 in Mehrkomponentenfragmenten.
- Modellfreier Backoff: `[SETZEN · {N1} ×3] + [BAHN ×6] + [{N2} ×14]` (MIXED_RECURRENT_MULTI_PLUS_ATOMS).
- Resttyp: **MODEL_CONDITIONED_RECURRENT**.
- Arbeitslesung: Setze den Sternstelleneintrag »l« und den Sternstelleneintrag »dy« entlang der Ringbahn.

### P1008-E0194 · `okealar` · INSTRUCTION

- Komponenten: `SETZEN · {N1} · ZIELORT · AUSGANG`
- Kachelung im Modell: `[SETZEN · {N1} ×3] + [ZIELORT · AUSGANG ×2]`
- Klasse: **FULL_RECURRENT_MULTI_FRAGMENT_TILE**; 4/4 Tokens wiederkehrend, davon 4 in Mehrkomponentenfragmenten.
- Modellfreier Backoff: `[SETZEN · {N1} ×3] + [ZIELORT · AUSGANG ×4]` (FULL_RECURRENT_MULTI_FRAGMENT_TILE).
- Resttyp: **MODEL_CONDITIONED_RECURRENT**.
- Arbeitslesung: Setze den Sternstelleneintrag »e« zur Zielposition und von der Ausgangsposition.

### P1008-E0243 · `oteeary` · CATALOGUE

- Komponenten: `DANACH · {N1} · AUSGANG · {N2}`
- Kachelung im Modell: `[DANACH · {N1} ×10] + [AUSGANG · {N2} ×6]`
- Klasse: **FULL_RECURRENT_MULTI_FRAGMENT_TILE**; 4/4 Tokens wiederkehrend, davon 4 in Mehrkomponentenfragmenten.
- Modellfreier Backoff: `[DANACH · {N1} ×10] + [AUSGANG · {N2} ×6]` (FULL_RECURRENT_MULTI_FRAGMENT_TILE).
- Resttyp: **MODEL_CONDITIONED_RECURRENT**.
- Arbeitslesung: Sternstelle »ee« / Sternstelle »y« — Folgevermerk, Ausgangszuordnung. Reihenfolge konkret: OT — danach Sternstelle »ee«.

### P1008-E0247 · `okeal` · INSTRUCTION

- Komponenten: `SETZEN · {N1} · ZIELORT`
- Kachelung im Modell: `[SETZEN · {N1} · ZIELORT ×1]`
- Klasse: **FULL_RECURRENT_MULTI_FRAGMENT_TILE**; 3/3 Tokens wiederkehrend, davon 3 in Mehrkomponentenfragmenten.
- Modellfreier Backoff: `[SETZEN · {N1} · ZIELORT ×1]` (FULL_RECURRENT_MULTI_FRAGMENT_TILE).
- Resttyp: **MODEL_CONDITIONED_RECURRENT**.
- Arbeitslesung: Setze den Sternstelleneintrag »e« zur Zielposition.

### P1008-E0251 · `okyd` · INSTRUCTION

- Komponenten: `SETZEN · {N1}`
- Kachelung im Modell: `[SETZEN · {N1} ×3]`
- Klasse: **FULL_RECURRENT_MULTI_FRAGMENT_TILE**; 2/2 Tokens wiederkehrend, davon 2 in Mehrkomponentenfragmenten.
- Modellfreier Backoff: `[SETZEN · {N1} ×3]` (FULL_RECURRENT_MULTI_FRAGMENT_TILE).
- Resttyp: **MODEL_CONDITIONED_RECURRENT**.
- Arbeitslesung: Setze den Sternstelleneintrag »yd«.

### P1008-E0252 · `otolam` · COORDINATE

- Komponenten: `DANACH · FORTSETZEN · HIER`
- Kachelung im Modell: `[DANACH · FORTSETZEN ×3] + [HIER ×4]`
- Klasse: **MIXED_RECURRENT_MULTI_PLUS_ATOMS**; 3/3 Tokens wiederkehrend, davon 2 in Mehrkomponentenfragmenten.
- Modellfreier Backoff: `[DANACH · FORTSETZEN ×5] + [HIER ×26]` (MIXED_RECURRENT_MULTI_PLUS_ATOMS).
- Resttyp: **MODEL_CONDITIONED_RECURRENT**.
- Arbeitslesung: Adressspur: danach → weiter → hier. Reihenfolge konkret: OT — danach Fortsetzung; OL — Folgeschritt in bezeichnete Stelle weiterführen.

### P1008-E0352 · `oraiinam` · CATALOGUE

- Komponenten: `EINHEIT · {N1} · HIER`
- Kachelung im Modell: `[EINHEIT · {N1} ×1] + [HIER ×10]`
- Klasse: **MIXED_RECURRENT_MULTI_PLUS_ATOMS**; 3/3 Tokens wiederkehrend, davon 2 in Mehrkomponentenfragmenten.
- Modellfreier Backoff: `[EINHEIT · {N1} ×1] + [HIER ×26]` (MIXED_RECURRENT_MULTI_PLUS_ATOMS).
- Resttyp: **MODEL_CONDITIONED_RECURRENT**.
- Arbeitslesung: Sternstelle »aiin« — Einheitsangabe, Hier-Vermerk.

### P1008-E0364 · `ofsholdy` · INSTRUCTION

- Komponenten: `AUSFÜHRUNG · HIER · HALTEN · FORTSETZEN · {N1}`
- Kachelung im Modell: `[AUSFÜHRUNG ×6] + [HIER ×10] + [HALTEN · FORTSETZEN ×2] + [{N1} ×26]`
- Klasse: **MIXED_RECURRENT_MULTI_PLUS_ATOMS**; 5/5 Tokens wiederkehrend, davon 2 in Mehrkomponentenfragmenten.
- Modellfreier Backoff: `[AUSFÜHRUNG · HIER ×5] + [HALTEN · FORTSETZEN ×2] + [{N1} ×88]` (MIXED_RECURRENT_MULTI_PLUS_ATOMS).
- Resttyp: **MODEL_CONDITIONED_RECURRENT**.
- Arbeitslesung: Weiter halte den Sternstelleneintrag »dy«, als Ausführung an der bezeichneten Stelle. Reihenfolge konkret: OL — Halten in Sternstelle »dy« weiterführen.

### P1008-E0409 · `oralkam` · CATALOGUE

- Komponenten: `EINHEIT · ZIELORT · {N1} · HIER`
- Kachelung im Modell: `[EINHEIT ×7] + [ZIELORT · {N1} ×2] + [HIER ×10]`
- Klasse: **MIXED_RECURRENT_MULTI_PLUS_ATOMS**; 4/4 Tokens wiederkehrend, davon 2 in Mehrkomponentenfragmenten.
- Modellfreier Backoff: `[EINHEIT ×10] + [ZIELORT · {N1} ×4] + [HIER ×26]` (MIXED_RECURRENT_MULTI_PLUS_ATOMS).
- Resttyp: **MODEL_CONDITIONED_RECURRENT**.
- Arbeitslesung: Sternstelle »k« — Einheitsangabe, Zielzuordnung, Hier-Vermerk.

### P1008-E0412 · `ory` · COORDINATE

- Komponenten: `EINHEIT · POSTEN`
- Kachelung im Modell: `[LOCAL:EINHEIT] + [POSTEN ×11]`
- Klasse: **LOCAL_TOKEN_REMAINS**; 1/2 Tokens wiederkehrend, davon 0 in Mehrkomponentenfragmenten.
- Modellfreier Backoff: `[EINHEIT · POSTEN ×1]` (FULL_RECURRENT_MULTI_FRAGMENT_TILE).
- Resttyp: **MODEL_FREE_RECURRENT_BACKOFF**.
- Arbeitslesung: Adressspur: Positionseinheit → Positionsposten.

### P1008-E0454 · `oraiiral` · CATALOGUE

- Komponenten: `EINHEIT · {N1} · ZIELORT`
- Kachelung im Modell: `[EINHEIT · {N1} ×1] + [ZIELORT ×17]`
- Klasse: **MIXED_RECURRENT_MULTI_PLUS_ATOMS**; 3/3 Tokens wiederkehrend, davon 2 in Mehrkomponentenfragmenten.
- Modellfreier Backoff: `[EINHEIT · {N1} ×1] + [ZIELORT ×47]` (MIXED_RECURRENT_MULTI_PLUS_ATOMS).
- Resttyp: **MODEL_CONDITIONED_RECURRENT**.
- Arbeitslesung: Sternstelle »aiir« — Einheitsangabe, Zielzuordnung.

### P1008-E0457 · `octho` · INSTRUCTION

- Komponenten: `{N1} · NEHMEN · EINSTELLEN · {N1}`
- Kachelung im Modell: `[{N1} · NEHMEN · EINSTELLEN ×1] + [{N1} ×26]`
- Klasse: **MIXED_RECURRENT_MULTI_PLUS_ATOMS**; 4/4 Tokens wiederkehrend, davon 3 in Mehrkomponentenfragmenten.
- Modellfreier Backoff: `[{N1} · NEHMEN · EINSTELLEN ×1] + [{N1} ×88]` (MIXED_RECURRENT_MULTI_PLUS_ATOMS).
- Resttyp: **MODEL_CONDITIONED_RECURRENT**.
- Arbeitslesung: Nimm den Sternstelleneintrag »o« und den Sternstelleneintrag »o« auf und stelle den Sternstelleneintrag »o« und den Sternstelleneintrag »o« ein.

### P1003-E0083 · `otedy` · COORDINATE

- Komponenten: `DANACH · GRAD I · SCHLUSS`
- Kachelung im Modell: `[DANACH ×20] + [LOCAL:GRAD I] + [LOCAL:SCHLUSS]`
- Klasse: **LOCAL_TOKEN_REMAINS**; 1/3 Tokens wiederkehrend, davon 0 in Mehrkomponentenfragmenten.
- Modellfreier Backoff: `[DANACH ×40] + [GRAD I ×5] + [SCHLUSS ×4]` (RECURRENT_ATOMS_ONLY).
- Resttyp: **MODEL_FREE_RECURRENT_BACKOFF**.
- Arbeitslesung: Adressspur: danach → Grad I → Endpunkt. Reihenfolge konkret: OT — danach Grad I.

### P1003-E0085 · `otol` · COORDINATE

- Komponenten: `DANACH · FORTSETZEN`
- Kachelung im Modell: `[DANACH · FORTSETZEN ×3]`
- Klasse: **FULL_RECURRENT_MULTI_FRAGMENT_TILE**; 2/2 Tokens wiederkehrend, davon 2 in Mehrkomponentenfragmenten.
- Modellfreier Backoff: `[DANACH · FORTSETZEN ×5]` (FULL_RECURRENT_MULTI_FRAGMENT_TILE).
- Resttyp: **MODEL_CONDITIONED_RECURRENT**.
- Arbeitslesung: Adressspur: danach → weiter. Reihenfolge konkret: OT — danach Fortsetzung; OL — Folgeschritt weiterführen.

### P1003-E0088 · `dotedy` · CATALOGUE

- Komponenten: `{N1} · DANACH · {N2}`
- Kachelung im Modell: `[{N1} ×59] + [DANACH ×15] + [{N2} ×8]`
- Klasse: **RECURRENT_ATOMS_ONLY**; 3/3 Tokens wiederkehrend, davon 0 in Mehrkomponentenfragmenten.
- Modellfreier Backoff: `[{N1} ×88] + [DANACH ×40] + [{N2} ×14]` (RECURRENT_ATOMS_ONLY).
- Resttyp: **MODEL_CONDITIONED_RECURRENT**.
- Arbeitslesung: Badstation »d« / Badstation »edy« — Folgevermerk. Reihenfolge konkret: OT — nach Badstation »d« folgt Badstation »edy«.

### P1003-E0410 · `otchdy` · INSTRUCTION

- Komponenten: `DANACH · BEARBEITEN · SCHLUSS`
- Kachelung im Modell: `[DANACH ×3] + [BEARBEITEN · SCHLUSS ×1]`
- Klasse: **MIXED_RECURRENT_MULTI_PLUS_ATOMS**; 3/3 Tokens wiederkehrend, davon 2 in Mehrkomponentenfragmenten.
- Modellfreier Backoff: `[DANACH ×40] + [BEARBEITEN · SCHLUSS ×1]` (MIXED_RECURRENT_MULTI_PLUS_ATOMS).
- Resttyp: **MODEL_CONDITIONED_RECURRENT**.
- Arbeitslesung: Danach bearbeite den Eintrag, und schließe den Schritt. Reihenfolge konkret: OT — danach Bearbeiten.

### P1003-E0414 · `cheocthy` · INSTRUCTION

- Komponenten: `{N1} · NEHMEN · EINSTELLEN · POSTEN`
- Kachelung im Modell: `[{N1} · NEHMEN · EINSTELLEN ×1] + [POSTEN ×18]`
- Klasse: **MIXED_RECURRENT_MULTI_PLUS_ATOMS**; 4/4 Tokens wiederkehrend, davon 3 in Mehrkomponentenfragmenten.
- Modellfreier Backoff: `[{N1} · NEHMEN · EINSTELLEN ×1] + [POSTEN ×39]` (MIXED_RECURRENT_MULTI_PLUS_ATOMS).
- Resttyp: **MODEL_CONDITIONED_RECURRENT**.
- Arbeitslesung: Nimm den Drogeneintrag »cheo« und den Drogenposten und stelle den Drogeneintrag »cheo« und den Drogenposten ein.

### P1003-E0418 · `otokol` · INSTRUCTION

- Komponenten: `DANACH · SETZEN · FORTSETZEN`
- Kachelung im Modell: `[DANACH ×3] + [SETZEN · FORTSETZEN ×2]`
- Klasse: **MIXED_RECURRENT_MULTI_PLUS_ATOMS**; 3/3 Tokens wiederkehrend, davon 2 in Mehrkomponentenfragmenten.
- Modellfreier Backoff: `[DANACH ×40] + [SETZEN · FORTSETZEN ×2]` (MIXED_RECURRENT_MULTI_PLUS_ATOMS).
- Resttyp: **MODEL_CONDITIONED_RECURRENT**.
- Arbeitslesung: Danach und weiter setze den Eintrag als Ansatz an. Reihenfolge konkret: OT — danach Setzen; OL — Setzen weiterführen.

### P1003-E0458 · `otoram` · CATALOGUE

- Komponenten: `DANACH · {N1} · HIER`
- Kachelung im Modell: `[DANACH · {N1} · HIER ×1]`
- Klasse: **FULL_RECURRENT_MULTI_FRAGMENT_TILE**; 3/3 Tokens wiederkehrend, davon 3 in Mehrkomponentenfragmenten.
- Modellfreier Backoff: `[DANACH · {N1} · HIER ×1]` (FULL_RECURRENT_MULTI_FRAGMENT_TILE).
- Resttyp: **MODEL_CONDITIONED_RECURRENT**.
- Arbeitslesung: Droge »or« — Folgevermerk, Hier-Vermerk. Reihenfolge konkret: OT — danach Droge »or«.

### P1003-E0460 · `cheosdy` · CATALOGUE

- Komponenten: `{F1}:NAMENSFAMILIE · {N1}`
- Kachelung im Modell: `[LOCAL:{F1}:NAMENSFAMILIE] + [{N1} ×59]`
- Klasse: **LOCAL_TOKEN_REMAINS**; 1/2 Tokens wiederkehrend, davon 0 in Mehrkomponentenfragmenten.
- Modellfreier Backoff: `[LOCAL:{F1}:NAMENSFAMILIE] + [{N1} ×88]` (LOCAL_TOKEN_REMAINS).
- Resttyp: **LEARNED_LEXICAL_SLOT_ONLY**.
- Arbeitslesung: Droge »cheosdy« — Drogenfamilie »cheo«.

### P1003-E0555 · `otydary` · CATALOGUE

- Komponenten: `DANACH · {N1} · HIER · AUSGANG · {N1}`
- Kachelung im Modell: `[DANACH · {N1} · HIER ×1] + [AUSGANG · {N1} ×5]`
- Klasse: **FULL_RECURRENT_MULTI_FRAGMENT_TILE**; 5/5 Tokens wiederkehrend, davon 5 in Mehrkomponentenfragmenten.
- Modellfreier Backoff: `[DANACH · {N1} · HIER ×1] + [AUSGANG · {N1} ×6]` (FULL_RECURRENT_MULTI_FRAGMENT_TILE).
- Resttyp: **MODEL_CONDITIONED_RECURRENT**.
- Arbeitslesung: Droge »y« / Droge »y« — Folgevermerk, Hier-Vermerk, Ausgangszuordnung. Reihenfolge konkret: OT — danach Droge »y«.

### P1003-E0557 · `dararda` · CATALOGUE

- Komponenten: `{N1} · AUSGANG · AUSGANG · {N2}`
- Kachelung im Modell: `[{N1} · AUSGANG ×8] + [AUSGANG · {N2} ×6]`
- Klasse: **FULL_RECURRENT_MULTI_FRAGMENT_TILE**; 4/4 Tokens wiederkehrend, davon 4 in Mehrkomponentenfragmenten.
- Modellfreier Backoff: `[{N1} · AUSGANG ×9] + [AUSGANG · {N2} ×6]` (FULL_RECURRENT_MULTI_FRAGMENT_TILE).
- Resttyp: **MODEL_CONDITIONED_RECURRENT**.
- Arbeitslesung: Droge »d« / Droge »da« — Ausgangszuordnung, Ausgangszuordnung.

### P1008-E1042 · `ararchodaiin` · CATALOGUE

- Komponenten: `AUSGANG · AUSGANG · {N1} · WERT`
- Kachelung im Modell: `[AUSGANG · AUSGANG ×2] + [{N1} · WERT ×3]`
- Klasse: **FULL_RECURRENT_MULTI_FRAGMENT_TILE**; 4/4 Tokens wiederkehrend, davon 4 in Mehrkomponentenfragmenten.
- Modellfreier Backoff: `[AUSGANG · AUSGANG ×2] + [{N1} · WERT ×3]` (FULL_RECURRENT_MULTI_FRAGMENT_TILE).
- Resttyp: **MODEL_CONDITIONED_RECURRENT**.
- Arbeitslesung: Droge »cho« — Ausgangszuordnung, Ausgangszuordnung, Wertangabe.

### P1008-E1175 · `ykocfhy` · INSTRUCTION

- Komponenten: `{N1} · NEHMEN · HIER · POSTEN`
- Kachelung im Modell: `[{N1} · NEHMEN ×2] + [HIER ×10] + [POSTEN ×18]`
- Klasse: **MIXED_RECURRENT_MULTI_PLUS_ATOMS**; 4/4 Tokens wiederkehrend, davon 2 in Mehrkomponentenfragmenten.
- Modellfreier Backoff: `[{N1} · NEHMEN ×2] + [HIER · POSTEN ×1]` (FULL_RECURRENT_MULTI_FRAGMENT_TILE).
- Resttyp: **MODEL_CONDITIONED_RECURRENT**.
- Arbeitslesung: Nimm den Drogeneintrag »yko« und den Drogenposten an der bezeichneten Stelle.

### P1008-E1176 · `saldam` · CATALOGUE

- Komponenten: `{N1} · ZIELORT · {N2} · HIER`
- Kachelung im Modell: `[{N1} · ZIELORT ×10] + [{N2} ×8] + [HIER ×10]`
- Klasse: **MIXED_RECURRENT_MULTI_PLUS_ATOMS**; 4/4 Tokens wiederkehrend, davon 2 in Mehrkomponentenfragmenten.
- Modellfreier Backoff: `[{N1} · ZIELORT · {N2} ×1] + [HIER ×26]` (MIXED_RECURRENT_MULTI_PLUS_ATOMS).
- Resttyp: **MODEL_CONDITIONED_RECURRENT**.
- Arbeitslesung: Droge »s« / Droge »d« — Zielzuordnung, Hier-Vermerk.

### P1008-E1177 · `sydarary` · CATALOGUE

- Komponenten: `{N1} · HIER · AUSGANG · AUSGANG · {N2}`
- Kachelung im Modell: `[{N1} · HIER · AUSGANG ×1] + [AUSGANG · {N2} ×6]`
- Klasse: **FULL_RECURRENT_MULTI_FRAGMENT_TILE**; 5/5 Tokens wiederkehrend, davon 5 in Mehrkomponentenfragmenten.
- Modellfreier Backoff: `[{N1} · HIER · AUSGANG ×1] + [AUSGANG · {N2} ×6]` (FULL_RECURRENT_MULTI_FRAGMENT_TILE).
- Resttyp: **MODEL_CONDITIONED_RECURRENT**.
- Arbeitslesung: Droge »sy« / Droge »y« — Hier-Vermerk, Ausgangszuordnung, Ausgangszuordnung.

### P1008-E1178 · `yddy` · COORDINATE

- Komponenten: `POSTEN · HIER · POSTEN`
- Kachelung im Modell: `[POSTEN ×11] + [HIER ×4] + [POSTEN ×11]`
- Klasse: **RECURRENT_ATOMS_ONLY**; 3/3 Tokens wiederkehrend, davon 0 in Mehrkomponentenfragmenten.
- Modellfreier Backoff: `[POSTEN · HIER ×1] + [POSTEN ×39]` (MIXED_RECURRENT_MULTI_PLUS_ATOMS).
- Resttyp: **MODEL_CONDITIONED_RECURRENT**.
- Arbeitslesung: Adressspur: Drogenposten → hier → Drogenposten.

### P1008-E1181 · `opchosam` · CATALOGUE

- Komponenten: `{N1} · HIER`
- Kachelung im Modell: `[{N1} · HIER ×5]`
- Klasse: **FULL_RECURRENT_MULTI_FRAGMENT_TILE**; 2/2 Tokens wiederkehrend, davon 2 in Mehrkomponentenfragmenten.
- Modellfreier Backoff: `[{N1} · HIER ×8]` (FULL_RECURRENT_MULTI_FRAGMENT_TILE).
- Resttyp: **MODEL_CONDITIONED_RECURRENT**.
- Arbeitslesung: Droge »opchos« — Hier-Vermerk.

### P1008-E1182 · `saloiinsheol` · INSTRUCTION

- Komponenten: `{N1} · ZIELORT · {N2} · HALTEN · {N3} · FORTSETZEN`
- Kachelung im Modell: `[{N1} · ZIELORT ×4] + [{N2} ×5] + [HALTEN ×10] + [LOCAL:{N3}] + [FORTSETZEN ×13]`
- Klasse: **LOCAL_TOKEN_REMAINS**; 5/6 Tokens wiederkehrend, davon 2 in Mehrkomponentenfragmenten.
- Modellfreier Backoff: `[{N1} · ZIELORT · {N2} ×1] + [HALTEN ×11] + [LOCAL:{N3}] + [FORTSETZEN ×25]` (LOCAL_TOKEN_REMAINS).
- Resttyp: **LEARNED_LEXICAL_SLOT_ONLY**.
- Arbeitslesung: Weiter halte den Drogeneintrag »s«, den Drogeneintrag »oiin« und den Drogeneintrag »e« zum Zielgefäß. Reihenfolge konkret: OL — Droge »e« weiterführen.

### P1008-E1183 · `opcheor` · INSTRUCTION

- Komponenten: `AUSFÜHRUNG · EINSETZEN · NEHMEN · GRAD I · EINHEIT`
- Kachelung im Modell: `[AUSFÜHRUNG ×6] + [EINSETZEN ×1] + [NEHMEN · GRAD I ×4] + [EINHEIT ×1]`
- Klasse: **MIXED_RECURRENT_MULTI_PLUS_ATOMS**; 5/5 Tokens wiederkehrend, davon 2 in Mehrkomponentenfragmenten.
- Modellfreier Backoff: `[AUSFÜHRUNG ×16] + [EINSETZEN ×1] + [NEHMEN · GRAD I ×4] + [EINHEIT ×10]` (MIXED_RECURRENT_MULTI_PLUS_ATOMS).
- Resttyp: **MODEL_CONDITIONED_RECURRENT**.
- Arbeitslesung: Setze die Ansatzeinheit ein und nimm die Ansatzeinheit, als Ausführung und auf Grad I.

### P1008-E1233 · `opchoroiin` · CATALOGUE

- Komponenten: `{N1} · AUSFÜHRUNG · STUFE`
- Kachelung im Modell: `[{N1} ×59] + [AUSFÜHRUNG ×5] + [LOCAL:STUFE]`
- Klasse: **LOCAL_TOKEN_REMAINS**; 2/3 Tokens wiederkehrend, davon 0 in Mehrkomponentenfragmenten.
- Modellfreier Backoff: `[{N1} · AUSFÜHRUNG · STUFE ×1]` (FULL_RECURRENT_MULTI_FRAGMENT_TILE).
- Resttyp: **MODEL_FREE_RECURRENT_BACKOFF**.
- Arbeitslesung: Droge »opchor« — Ausführungsvermerk, Stufenvermerk.

### P1008-E1296 · `korainy` · INSTRUCTION

- Komponenten: `GEBEN · EINHEIT · ANTEIL · POSTEN`
- Kachelung im Modell: `[GEBEN ×1] + [EINHEIT ×1] + [ANTEIL ×3] + [POSTEN ×18]`
- Klasse: **RECURRENT_ATOMS_ONLY**; 4/4 Tokens wiederkehrend, davon 0 in Mehrkomponentenfragmenten.
- Modellfreier Backoff: `[GEBEN ×1] + [EINHEIT ×10] + [ANTEIL · POSTEN ×2]` (MIXED_RECURRENT_MULTI_PLUS_ATOMS).
- Resttyp: **MODEL_CONDITIONED_RECURRENT**.
- Arbeitslesung: Gib die Ansatzeinheit, den Drogenanteil und den Drogenposten zu.

### P1008-E1297 · `sodar` · INSTRUCTION

- Komponenten: `WÄHLEN · AUSFÜHRUNG · ZWEITE STUFE · MARKIEREN`
- Kachelung im Modell: `[WÄHLEN ×4] + [AUSFÜHRUNG ×6] + [LOCAL:ZWEITE STUFE] + [LOCAL:MARKIEREN]`
- Klasse: **LOCAL_TOKEN_REMAINS**; 2/4 Tokens wiederkehrend, davon 0 in Mehrkomponentenfragmenten.
- Modellfreier Backoff: `[WÄHLEN ×4] + [AUSFÜHRUNG ×16] + [LOCAL:ZWEITE STUFE] + [LOCAL:MARKIEREN]` (LOCAL_TOKEN_REMAINS).
- Resttyp: **UNIQUE_FUNCTIONAL_COMPONENT_REMAINS**.
- Arbeitslesung: Wähle den Eintrag und markiere den Eintrag, als Ausführung und auf der zweiten Stufe.

### P1008-E1299 · `cheody` · INSTRUCTION

- Komponenten: `NEHMEN · GRAD I · AUSFÜHRUNG · POSTEN`
- Kachelung im Modell: `[NEHMEN · GRAD I ×4] + [AUSFÜHRUNG ×6] + [POSTEN ×18]`
- Klasse: **MIXED_RECURRENT_MULTI_PLUS_ATOMS**; 4/4 Tokens wiederkehrend, davon 2 in Mehrkomponentenfragmenten.
- Modellfreier Backoff: `[NEHMEN · GRAD I ×4] + [AUSFÜHRUNG ×16] + [POSTEN ×39]` (MIXED_RECURRENT_MULTI_PLUS_ATOMS).
- Resttyp: **MODEL_CONDITIONED_RECURRENT**.
- Arbeitslesung: Nimm den Drogenposten, auf Grad I und als Ausführung.

### P1008-E1301 · `okshdchos` · INSTRUCTION

- Komponenten: `SETZEN · HALTEN · {N1}`
- Kachelung im Modell: `[SETZEN ×29] + [HALTEN · {N1} ×1]`
- Klasse: **MIXED_RECURRENT_MULTI_PLUS_ATOMS**; 3/3 Tokens wiederkehrend, davon 2 in Mehrkomponentenfragmenten.
- Modellfreier Backoff: `[SETZEN ×29] + [HALTEN · {N1} ×1]` (MIXED_RECURRENT_MULTI_PLUS_ATOMS).
- Resttyp: **MODEL_CONDITIONED_RECURRENT**.
- Arbeitslesung: Setze den Drogeneintrag »dchos« als Ansatz an und halte den Drogeneintrag »dchos«.

### P1008-E1410 · `ofakal` · CATALOGUE

- Komponenten: `AUSFÜHRUNG · HIER · {N1} · ZIELORT`
- Kachelung im Modell: `[AUSFÜHRUNG · HIER ×3] + [{N1} · ZIELORT ×10]`
- Klasse: **FULL_RECURRENT_MULTI_FRAGMENT_TILE**; 4/4 Tokens wiederkehrend, davon 4 in Mehrkomponentenfragmenten.
- Modellfreier Backoff: `[AUSFÜHRUNG · HIER ×5] + [{N1} · ZIELORT ×17]` (FULL_RECURRENT_MULTI_FRAGMENT_TILE).
- Resttyp: **MODEL_CONDITIONED_RECURRENT**.
- Arbeitslesung: Droge »ak« — Ausführungsvermerk, Hier-Vermerk, Zielzuordnung.

### P1008-E1413 · `otolarol` · COORDINATE

- Komponenten: `DANACH · FORTSETZEN · AUSGANG · FORTSETZEN`
- Kachelung im Modell: `[DANACH · FORTSETZEN ×3] + [AUSGANG ×10] + [FORTSETZEN ×5]`
- Klasse: **MIXED_RECURRENT_MULTI_PLUS_ATOMS**; 4/4 Tokens wiederkehrend, davon 2 in Mehrkomponentenfragmenten.
- Modellfreier Backoff: `[DANACH · FORTSETZEN ×5] + [AUSGANG ×44] + [FORTSETZEN ×25]` (MIXED_RECURRENT_MULTI_PLUS_ATOMS).
- Resttyp: **MODEL_CONDITIONED_RECURRENT**.
- Arbeitslesung: Adressspur: danach → weiter → Ausgangsgefäß → weiter. Reihenfolge konkret: OT — danach Fortsetzung; OL — Folgeschritt in Ausgang weiterführen; OL — Ausgang weiterführen.

Die Kacheln ändern keine Lesung. `{N1}` bleibt ein gelernter Namensplatz; wiederkehrend ist seine Position im Bauplan, nicht die Identität des Namens. Ein modellfreier Treffer darf eine seltene Kombination beschreiben, aber niemals das aktive Koordinaten-, Anweisungs- oder Katalogmodell überschreiben. Auch die drei lokalen Reste sind nicht bedeutungslos: Ihre GDT479-Defaultbedeutungen bleiben vollständig erhalten.
