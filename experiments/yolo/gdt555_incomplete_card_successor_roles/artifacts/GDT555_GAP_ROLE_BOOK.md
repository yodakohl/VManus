# GDT555 — Arbeitsbuch der scheinbar unvollständigen Karten

Die 16 aktionslosen und 57 argumentlosen Mengen überlappen in neun Ereignissen. Das gemeinsame Deck enthält deshalb 64, nicht 73, Kartenereignisse.

## Exakte Initialisierungslinks

- **ACTION_STATE · Abstand 1:** `G515-E0003` → `G515-E0004` — Halte; auf Grad I; führe fort. → Im laufenden Satz halte; führe fort.
- **ACTION_STATE · Abstand 1:** `G515-E0065` → `G515-E0066` — Wähle; auf der bezeichneten Stufe; an der bezeichneten Stelle. → Im laufenden Satz wähle; vom Ausgangsmaterial.
- **ACTION_STATE · Abstand 1:** `G515-E0099` → `G515-E0100` — Stelle ein und halte; führe fort. → Im laufenden Satz halte; an der bezeichneten Stelle; führe 2-mal fort.
- **ACTION_STATE · Abstand 2:** `G515-E0099` → `G515-E0101` — Stelle ein und halte; führe fort. → Danach: im laufenden Satz halte die Arbeitseinheit.
- **ACTION_STATE · Abstand 1:** `G515-E0162` → `G515-E0163` — Wähle. → Im laufenden Satz wähle den Arbeitswert.
- **ACTION_STATE · Abstand 1:** `G515-E0193` → `G515-E0194` — Wähle. → Im laufenden Satz wähle den Arbeitswert.
- **ACTION_STATE · Abstand 2:** `G515-E0193` → `G515-E0195` — Wähle. → Im laufenden Satz wähle den Arbeitswert [wie zuvor]; zur Zielstelle.
- **ACTION_STATE · Abstand 1:** `G515-E0243` → `G515-E0244` — Wähle und wähle; auf der bezeichneten Stufe; an der bezeichneten Stelle. → Im laufenden Satz wähle die Arbeitseinheit.
- **ARGUMENT_STATE · Abstand 1:** `G515-E0336` → `G515-E0337` — Danach: Bezug: den laufenden Eintrag; auf Grad I. → Ordne den laufenden Eintrag [wie zuvor] zu; führe fort.
- **ARGUMENT_STATE · Abstand 2:** `G515-E0336` → `G515-E0338` — Danach: Bezug: den laufenden Eintrag; auf Grad I. → Im laufenden Satz ordne den laufenden Eintrag [wie zuvor] zu; von der Ausgangszeile.
- **ACTION_STATE · Abstand 1:** `G515-E0383` → `G515-E0384` — Halte fest, trage ein und kennzeichne; auf der bezeichneten Stufe. → Im laufenden Satz kennzeichne den laufenden Eintrag.
- **ACTION_STATE · Abstand 2:** `G515-E0383` → `G515-E0385` — Halte fest, trage ein und kennzeichne; auf der bezeichneten Stufe. → Im laufenden Satz kennzeichne den laufenden Eintrag [wie zuvor]; von der Ausgangszeile; an der bezeichneten Stelle [außen] und an der bezeichneten Stelle [innen].
- **ACTION_STATE · Abstand 1:** `G515-E0460` → `G515-E0461` — Wähle; entlang der Lesebahn. → Im laufenden Satz wähle; führe fort.
- **ACTION_STATE · Abstand 2:** `G515-E0460` → `G515-E0462` — Wähle; entlang der Lesebahn. → Im laufenden Satz wähle den Kennwert.
- **ACTION_STATE · Abstand 3:** `G515-E0460` → `G515-E0463` — Wähle; entlang der Lesebahn. → Im laufenden Satz wähle den Kennwert.
- **ACTION_STATE · Abstand 4:** `G515-E0460` → `G515-E0464` — Wähle; entlang der Lesebahn. → Im laufenden Satz wähle den Kennwert [wie zuvor]; zur Zielspalte.
- **ACTION_STATE · Abstand 5:** `G515-E0460` → `G515-E0465` — Wähle; entlang der Lesebahn. → Im laufenden Satz wähle den Kennwert [wie zuvor]; an der bezeichneten Stelle; führe fort.
- **ARGUMENT_STATE · Abstand 1:** `G515-E0491` → `G515-E0492` — Bezug: den laufenden Eintrag; zur Zielspalte. → Wähle den laufenden Eintrag [wie zuvor] und kennzeichne den laufenden Eintrag [wie zuvor]; auf der bezeichneten Stufe.
- **ARGUMENT_STATE · Abstand 2:** `G515-E0491` → `G515-E0493` — Bezug: den laufenden Eintrag; zur Zielspalte. → Entnimm den laufenden Eintrag [wie zuvor]; über die Eintragsverbindung; auf Grad I und zur Ausführung.
- **ARGUMENT_STATE · Abstand 3:** `G515-E0491` → `G515-E0494` — Bezug: den laufenden Eintrag; zur Zielspalte. → Ordne den laufenden Eintrag [wie zuvor] zu; zur Zielspalte.
- **ARGUMENT_STATE · Abstand 1:** `G515-E0563` → `G515-E0564` — Bezug: den Kennwert. → Halte den Kennwert [wie zuvor] fest; auf Grad II; führe fort.
- **ARGUMENT_STATE · Abstand 2:** `G515-E0563` → `G515-E0565` — Bezug: den Kennwert. → Halte den Kennwert [wie zuvor] fest; über die Eintragsverbindung; auf Grad I; schließe den Schritt.

## Alle 64 eindeutigen Lückenereignisse

### G515-E0003 · `sheol` · ACTION_INITIALIZER

Halte; auf Grad I; führe fort. → Im laufenden Satz halte; führe fort.

Rezept: `SH+E+OL` · Makro: `A:SH;X:-;C:GRADE:I>CONTINUE`

### G515-E0004 · `ol` · CARRIED_ACTION_OBJECTLESS_CONTROL

Im laufenden Satz halte; führe fort.

Rezept: `OL` · Makro: `A:^SH;X:-;C:CONTINUE`

### G515-E0048 · `daiin` · NOMINAL_CONTROL_PROLOGUE

Bezug: den Arbeitswert.

Rezept: `AIIN` · Makro: `A:-;X:AIIN;C:-`

### G515-E0065 · `faiis` · ACTION_INITIALIZER

Wähle; auf der bezeichneten Stufe; an der bezeichneten Stelle. → Im laufenden Satz wähle; vom Ausgangsmaterial.

Rezept: `LOCAL_CHAR_F+IIN+S` · Makro: `A:S;X:-;C:LOCAL:F>STAGE`

### G515-E0066 · `ar` · CARRIED_ACTION_OBJECTLESS_CONTROL

Im laufenden Satz wähle; vom Ausgangsmaterial.

Rezept: `AR` · Makro: `A:^S;X:-;C:REL:AR`

### G515-E0099 · `tshol` · ACTION_INITIALIZER

Stelle ein und halte; führe fort. → Im laufenden Satz halte; an der bezeichneten Stelle; führe 2-mal fort.

Rezept: `T+SH+OL` · Makro: `A:T+SH;X:-;C:CONTINUE`

### G515-E0100 · `folchol` · CARRIED_ACTION_OBJECTLESS_CONTROL

Im laufenden Satz halte; an der bezeichneten Stelle; führe 2-mal fort.

Rezept: `LOCAL_CHAR_F+OL+OL` · Makro: `A:^SH;X:-;C:LOCAL:F>CONTINUE>CONTINUE`

### G515-E0161 · `qokees` · OBJECTLESS_ACTION_BEFORE_EXPLICIT_RESET

Setze im Arbeitsgang an und wähle; auf Grad II.

Rezept: `OK+EE+S` · Makro: `A:OK+S;X:-;C:GRADE:II`

### G515-E0162 · `s` · ACTION_INITIALIZER

Wähle. → Im laufenden Satz wähle den Arbeitswert.

Rezept: `S` · Makro: `A:S;X:-;C:-`

### G515-E0190 · `qotedy` · CLOSURE_BOUNDARY

Danach: auf Grad I; schließe den Schritt.

Rezept: `OT+E+DY` · Makro: `A:-;X:-;C:THEN>GRADE:I>CLOSE`

### G515-E0191 · `chepos` · OBJECTLESS_ACTION_BEFORE_EXPLICIT_RESET

Nimm, setze ein und wähle; auf Grad I und zur Ausführung.

Rezept: `CH+E+P+O+S` · Makro: `A:CH+P+S;X:-;C:GRADE:I>EXEC`

### G515-E0192 · `cheda` · OBJECTLESS_ACTION_BEFORE_EXPLICIT_RESET

Bearbeite; an der bezeichneten Stelle.

Rezept: `CHD+A_ADDR` · Makro: `A:CHD;X:-;C:ADDR:A`

### G515-E0193 · `s` · ACTION_INITIALIZER

Wähle. → Im laufenden Satz wähle den Arbeitswert.

Rezept: `S` · Makro: `A:S;X:-;C:-`

### G515-E0204 · `shedy` · OBJECTLESS_CLOSURE_OR_STATEMENT_BOUNDARY

Halte; auf Grad I; schließe den Schritt.

Rezept: `SH+E+DY` · Makro: `A:SH;X:-;C:GRADE:I>CLOSE`

### G515-E0205 · `qokedy` · OBJECTLESS_CLOSURE_OR_STATEMENT_BOUNDARY

Setze im Arbeitsgang an; auf Grad I; schließe den Schritt.

Rezept: `OK+E+DY` · Makro: `A:OK;X:-;C:GRADE:I>CLOSE`

### G515-E0206 · `cheol` · OBJECTLESS_ACTION_BEFORE_EXPLICIT_RESET

Nimm; über die Verbindung im Pflanzenartikel; auf Grad I und zur Ausführung.

Rezept: `CH+E+O+L` · Makro: `A:CH;X:-;C:GRADE:I>EXEC>REL:L`

### G515-E0207 · `cheod` · OBJECTLESS_ACTION_BEFORE_EXPLICIT_RESET

Nimm; auf Grad I und zur Ausführung; an der bezeichneten Stelle.

Rezept: `CH+E+O+D_ADDR` · Makro: `A:CH;X:-;C:GRADE:I>EXEC>ADDR:D`

### G515-E0215 · `tol` · OBJECTLESS_ACTION_BEFORE_EXPLICIT_RESET

Stelle ein; führe fort.

Rezept: `T+OL` · Makro: `A:T;X:-;C:CONTINUE`

### G515-E0216 · `shso` · OBJECTLESS_ACTION_BEFORE_EXPLICIT_RESET

Halte und wähle; zur Ausführung.

Rezept: `SH+S+O` · Makro: `A:SH+S;X:-;C:EXEC`

### G515-E0217 · `okedy` · OBJECTLESS_CLOSURE_OR_STATEMENT_BOUNDARY

Setze im Arbeitsgang an; auf Grad I; schließe den Schritt.

Rezept: `OK+E+DY` · Makro: `A:OK;X:-;C:GRADE:I>CLOSE`

### G515-E0218 · `okedy` · OBJECTLESS_CLOSURE_OR_STATEMENT_BOUNDARY

Setze im Arbeitsgang an; auf Grad I; schließe den Schritt.

Rezept: `OK+E+DY` · Makro: `A:OK;X:-;C:GRADE:I>CLOSE`

### G515-E0219 · `qokedy` · OBJECTLESS_CLOSURE_OR_STATEMENT_BOUNDARY

Setze im Arbeitsgang an; auf Grad I; schließe den Schritt.

Rezept: `OK+E+DY` · Makro: `A:OK;X:-;C:GRADE:I>CLOSE`

### G515-E0220 · `qokeedy` · OBJECTLESS_CLOSURE_OR_STATEMENT_BOUNDARY

Setze im Arbeitsgang an; auf Grad II; schließe den Schritt.

Rezept: `OK+EE+DY` · Makro: `A:OK;X:-;C:GRADE:II>CLOSE`

### G515-E0221 · `dar` · PRE_ACTION_SCOPE_PROLOGUE

Vom Ausgangsmaterial; an der bezeichneten Stelle.

Rezept: `D_ADDR+AR` · Makro: `A:-;X:-;C:ADDR:D>REL:AR`

### G515-E0240 · `otedy` · CLOSURE_BOUNDARY

Danach: auf Grad I; schließe den Schritt.

Rezept: `OT+E+DY` · Makro: `A:-;X:-;C:THEN>GRADE:I>CLOSE`

### G515-E0242 · `dals` · OBJECTLESS_ACTION_BEFORE_EXPLICIT_RESET

Wähle; zur Zielstelle.

Rezept: `AL+S` · Makro: `A:S;X:-;C:REL:AL`

### G515-E0243 · `saiis` · ACTION_INITIALIZER

Wähle und wähle; auf der bezeichneten Stufe; an der bezeichneten Stelle. → Im laufenden Satz wähle die Arbeitseinheit.

Rezept: `S+A_ADDR+IIN+S` · Makro: `A:S+S;X:-;C:ADDR:A>STAGE`

### G515-E0302 · `opchedy` · OBJECTLESS_CLOSURE_OR_STATEMENT_BOUNDARY

Setze ein und bearbeite; zur Ausführung; schließe den Schritt.

Rezept: `O+P+CHD+DY` · Makro: `A:P+CHD;X:-;C:EXEC>CLOSE`

### G515-E0303 · `chap` · OBJECTLESS_ACTION_BEFORE_EXPLICIT_RESET

Entnimm und setze ein; an der bezeichneten Stelle.

Rezept: `CH+A_ADDR+P` · Makro: `A:CH+P;X:-;C:ADDR:A`

### G515-E0314 · `qokeedy` · OBJECTLESS_CLOSURE_OR_STATEMENT_BOUNDARY

Trage ein; auf Grad II; schließe den Schritt.

Rezept: `OK+EE+DY` · Makro: `A:OK;X:-;C:GRADE:II>CLOSE`

### G515-E0315 · `qokal` · OBJECTLESS_ACTION_BEFORE_EXPLICIT_RESET

Trage ein; zur Zielspalte.

Rezept: `OK+AL` · Makro: `A:OK;X:-;C:REL:AL`

### G515-E0316 · `okedy` · OBJECTLESS_CLOSURE_OR_STATEMENT_BOUNDARY

Trage ein; auf Grad I; schließe den Schritt.

Rezept: `OK+E+DY` · Makro: `A:OK;X:-;C:GRADE:I>CLOSE`

### G515-E0317 · `qokshd` · OBJECTLESS_ACTION_BEFORE_EXPLICIT_RESET

Trage ein und halte fest; an der bezeichneten Stelle.

Rezept: `OK+SH+D_ADDR` · Makro: `A:OK+SH;X:-;C:ADDR:D`

### G515-E0319 · `chady` · OBJECTLESS_CLOSURE_OR_STATEMENT_BOUNDARY

Entnimm; an der bezeichneten Stelle; schließe den Schritt.

Rezept: `CH+A_ADDR+DY` · Makro: `A:CH;X:-;C:ADDR:A>CLOSE`

### G515-E0335 · `dar` · PRE_ACTION_SCOPE_PROLOGUE

Von der Ausgangszeile; an der bezeichneten Stelle.

Rezept: `D_ADDR+AR` · Makro: `A:-;X:-;C:ADDR:D>REL:AR`

### G515-E0336 · `qotey` · ARGUMENT_INITIALIZER

Danach: Bezug: den laufenden Eintrag; auf Grad I. → Ordne den laufenden Eintrag [wie zuvor] zu; führe fort.

Rezept: `OT+E+Y` · Makro: `A:-;X:Y;C:THEN>GRADE:I`

### G515-E0380 · `cheta` · OBJECTLESS_ACTION_BEFORE_EXPLICIT_RESET

Entnimm und lege fest; auf Grad I; an der bezeichneten Stelle.

Rezept: `CH+E+T+A_ADDR` · Makro: `A:CH+T;X:-;C:GRADE:I>ADDR:A`

### G515-E0381 · `r` · OBJECTLESS_ACTION_BEFORE_EXPLICIT_RESET

Kennzeichne.

Rezept: `R` · Makro: `A:R;X:-;C:-`

### G515-E0382 · `sheod` · OBJECTLESS_ACTION_BEFORE_EXPLICIT_RESET

Halte fest; auf Grad I und zur Ausführung; an der bezeichneten Stelle.

Rezept: `SH+E+O+D_ADDR` · Makro: `A:SH;X:-;C:GRADE:I>EXEC>ADDR:D`

### G515-E0383 · `shokaiir` · ACTION_INITIALIZER

Halte fest, trage ein und kennzeichne; auf der bezeichneten Stufe. → Im laufenden Satz kennzeichne den laufenden Eintrag.

Rezept: `SH+OK+IIN+R` · Makro: `A:SH+OK+R;X:-;C:STAGE`

### G515-E0406 · `ol` · CONTINUATION_PROLOGUE

Führe fort.

Rezept: `OL` · Makro: `A:-;X:-;C:CONTINUE`

### G515-E0414 · `pchof` · OBJECTLESS_ACTION_BEFORE_EXPLICIT_RESET

Setze ein und entnimm; zur Ausführung; an der bezeichneten Stelle.

Rezept: `P+CH+O+LOCAL_CHAR_F` · Makro: `A:P+CH;X:-;C:EXEC>LOCAL:F`

### G515-E0435 · `okar` · OBJECTLESS_ACTION_BEFORE_EXPLICIT_RESET

Trage ein; von der Ausgangszeile.

Rezept: `OK+AR` · Makro: `A:OK;X:-;C:REL:AR`

### G515-E0436 · `shedy` · OBJECTLESS_CLOSURE_OR_STATEMENT_BOUNDARY

Halte fest; auf Grad I; schließe den Schritt.

Rezept: `SH+E+DY` · Makro: `A:SH;X:-;C:GRADE:I>CLOSE`

### G515-E0446 · `dal` · PRE_ACTION_SCOPE_PROLOGUE

Zur Zielspalte.

Rezept: `AL` · Makro: `A:-;X:-;C:REL:AL`

### G515-E0447 · `shedy` · OBJECTLESS_CLOSURE_OR_STATEMENT_BOUNDARY

Halte fest; auf Grad I; schließe den Schritt.

Rezept: `SH+E+DY` · Makro: `A:SH;X:-;C:GRADE:I>CLOSE`

### G515-E0457 · `shedy` · OBJECTLESS_CLOSURE_OR_STATEMENT_BOUNDARY

Halte fest; auf Grad I; schließe den Schritt.

Rezept: `SH+E+DY` · Makro: `A:SH;X:-;C:GRADE:I>CLOSE`

### G515-E0458 · `shedy` · OBJECTLESS_CLOSURE_OR_STATEMENT_BOUNDARY

Halte fest; auf Grad I; schließe den Schritt.

Rezept: `SH+E+DY` · Makro: `A:SH;X:-;C:GRADE:I>CLOSE`

### G515-E0459 · `dair` · PRE_ACTION_SCOPE_PROLOGUE

Entlang der Lesebahn; an der bezeichneten Stelle.

Rezept: `D_ADDR+AIR` · Makro: `A:-;X:-;C:ADDR:D>REL:AIR`

### G515-E0460 · `sair` · ACTION_INITIALIZER

Wähle; entlang der Lesebahn. → Im laufenden Satz wähle; führe fort.

Rezept: `S+AIR` · Makro: `A:S;X:-;C:REL:AIR`

### G515-E0461 · `ol` · CARRIED_ACTION_OBJECTLESS_CONTROL

Im laufenden Satz wähle; führe fort.

Rezept: `OL` · Makro: `A:^S;X:-;C:CONTINUE`

### G515-E0491 · `daly` · ARGUMENT_INITIALIZER

Bezug: den laufenden Eintrag; zur Zielspalte. → Wähle den laufenden Eintrag [wie zuvor] und kennzeichne den laufenden Eintrag [wie zuvor]; auf der bezeichneten Stufe.

Rezept: `AL+Y` · Makro: `A:-;X:Y;C:REL:AL`

### G515-E0497 · `dal` · PRE_ACTION_SCOPE_PROLOGUE

Zur Zielspalte.

Rezept: `AL` · Makro: `A:-;X:-;C:REL:AL`

### G515-E0498 · `shol` · OBJECTLESS_ACTION_BEFORE_EXPLICIT_RESET

Halte fest; führe fort.

Rezept: `SH+OL` · Makro: `A:SH;X:-;C:CONTINUE`

### G515-E0503 · `oteedy` · CLOSURE_BOUNDARY

Danach: auf Grad II; schließe den Schritt.

Rezept: `OT+EE+DY` · Makro: `A:-;X:-;C:THEN>GRADE:II>CLOSE`

### G515-E0524 · `otchedy` · OBJECTLESS_CLOSURE_OR_STATEMENT_BOUNDARY

Danach: bearbeite; schließe den Schritt.

Rezept: `OT+CHD+DY` · Makro: `A:CHD;X:-;C:THEN>CLOSE`

### G515-E0547 · `lchey` · PRE_ACTION_SCOPE_PROLOGUE

Bezug: den laufenden Eintrag; über die Eintragsverbindung.

Rezept: `L+Y` · Makro: `A:-;X:Y;C:REL:L`

### G515-E0562 · `dor` · PRE_ACTION_SCOPE_PROLOGUE

Bezug: die Eintragseinheit; an der bezeichneten Stelle.

Rezept: `D_ADDR+OR` · Makro: `A:-;X:OR;C:ADDR:D`

### G515-E0563 · `aiin` · ARGUMENT_INITIALIZER

Bezug: den Kennwert. → Halte den Kennwert [wie zuvor] fest; auf Grad II; führe fort.

Rezept: `AIIN` · Makro: `A:-;X:AIIN;C:-`

### G515-E0566 · `lchedy` · OBJECTLESS_CLOSURE_OR_STATEMENT_BOUNDARY

Bearbeite; über die Eintragsverbindung; schließe den Schritt.

Rezept: `L+CHD+DY` · Makro: `A:CHD;X:-;C:REL:L>CLOSE`

### G515-E0576 · `kody` · OBJECTLESS_CLOSURE_OR_STATEMENT_BOUNDARY

Ordne zu; zur Ausführung; schließe den Schritt.

Rezept: `K+O+DY` · Makro: `A:K;X:-;C:EXEC>CLOSE`

### G515-E0577 · `qotchedy` · OBJECTLESS_CLOSURE_OR_STATEMENT_BOUNDARY

Danach: bearbeite; schließe den Schritt.

Rezept: `OT+CHD+DY` · Makro: `A:CHD;X:-;C:THEN>CLOSE`

### G515-E0578 · `cphedy` · OBJECTLESS_CLOSURE_OR_STATEMENT_BOUNDARY

Entnimm und setze ein; auf Grad I; schließe den Schritt.

Rezept: `CH+P+E+DY` · Makro: `A:CH+P;X:-;C:GRADE:I>CLOSE`

### G515-E0579 · `daiin` · NOMINAL_CONTROL_PROLOGUE

Bezug: den Kennwert.

Rezept: `AIIN` · Makro: `A:-;X:AIIN;C:-`

## Grenze

Ein Initialisierungslink ist nur dann gesetzt, wenn die spätere Karte die Quell-ID ausdrücklich als ihren geerbten Zustand nennt. Alle anderen Rollen bleiben kontextuelle Arbeitsrollen, keine neuen Wortbedeutungen.
