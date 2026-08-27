# GDT554 — horizontales Arbeitsbuch der 78 Aussagen

Die Makros sind eine kompakte Rückseite der unveränderten deutschen Arbeitslesung: `A` nennt sichtbare Aktionen, `^A` eine gleichsatzlich geerbte Aktion, `X` Argumente und `C` die geordnete Kontrollspur. Sie sind keine behauptete historische Syntax.

## Steckplatzbewegungen

| Bewegung | Events | Aussagen | Seiten | Beispiel |
|---|---:|---:|---:|---|
| `SET_A1__SET_X1` | 128 | 47 | 4 | Halte den Pflanzenposten; auf Grad II. |
| `SET_A1__KEEP_X1` | 94 | 40 | 4 | Halte die Arbeitseinheit [wie zuvor]; führe fort. |
| `KEEP_A1__SET_X1` | 77 | 27 | 4 | Danach: im laufenden Satz halte den Pflanzenposten; auf Grad I. |
| `KEEP_A1__KEEP_X1` | 61 | 27 | 4 | Im laufenden Satz halte den Pflanzenposten [wie zuvor]; zur Ausführung und auf der bezeichneten Stufe; an der bezeichneten Stelle. |
| `SET_A2__SET_X1` | 54 | 33 | 4 | Gib den Pflanzenposten zu und nimm den Pflanzenposten; zur Zielstelle; zur Ausführung; an der bezeichneten Stelle. |
| `SET_A1__EMPTY_X` | 32 | 26 | 4 | Halte; auf Grad I; führe fort. |
| `SET_A2__KEEP_X1` | 27 | 19 | 3 | Nimm den Pflanzenposten [wie zuvor] und setze den Pflanzenposten [wie zuvor] ein; an der bezeichneten Stelle; schließe den Schritt. |
| `SET_A3__SET_X1` | 18 | 15 | 4 | Halte den Pflanzenposten, stelle den Pflanzenposten ein und nimm den Pflanzenposten. |
| `SET_A1__SET_X2` | 11 | 7 | 4 | Stelle den Pflanzenposten [außen] und den Pflanzenposten [innen] ein; zur Ausführung. |
| `SET_A2__EMPTY_X` | 10 | 10 | 3 | Stelle ein und halte; führe fort. |
| `EMPTY_A__EMPTY_X` | 9 | 9 | 2 | Danach: auf Grad I; schließe den Schritt. |
| `EMPTY_A__SET_X1` | 7 | 6 | 2 | Bezug: den Arbeitswert. |
| `SET_A3__KEEP_X1` | 7 | 7 | 2 | Nimm den Arbeitswert [wie zuvor], setze den Arbeitswert [wie zuvor] ein und gib den Arbeitswert [wie zuvor] zu; auf Grad I [außen], auf Grad I [innen] und zur Ausführung; an der bezeichneten Stelle. |
| `KEEP_A1__EMPTY_X` | 4 | 4 | 3 | Im laufenden Satz halte; führe fort. |
| `SET_A2__SET_X2` | 3 | 3 | 3 | Stelle den Pflanzenposten [außen] und den Pflanzenposten [innen] ein und nimm den Pflanzenposten [außen] und den Pflanzenposten [innen]; auf Grad II; an der bezeichneten Stelle. |
| `SET_A3__EMPTY_X` | 2 | 2 | 2 | Nimm, setze ein und wähle; auf Grad I und zur Ausführung. |
| `KEEP_A1__SET_X2` | 1 | 1 | 1 | Im laufenden Satz entnimm den laufenden Eintrag und den Kennwert; an der bezeichneten Stelle. |
| `SET_A3__SET_X2` | 1 | 1 | 1 | Halte den Pflanzenposten [außen] und den Pflanzenposten [innen], stelle den Pflanzenposten [außen] und den Pflanzenposten [innen] ein und nimm den Pflanzenposten [außen] und den Pflanzenposten [innen]. |

## Wiederkehrende vollständige Aussagenschablonen

- **1 Karten · 6 Aussagen · 2 Seiten:** `SET_A1__EMPTY_X|A>G1>CLOSE`
- **2 Karten · 2 Aussagen · 1 Seiten:** `SET_A1__EMPTY_X|A>REL || SET_A1__EMPTY_X|A>G1>CLOSE`
- **1 Karten · 2 Aussagen · 1 Seiten:** `EMPTY_A__EMPTY_X|THEN>G1>CLOSE`
- **1 Karten · 2 Aussagen · 2 Seiten:** `SET_A1__EMPTY_X|A>G2>CLOSE`
- **1 Karten · 2 Aussagen · 1 Seiten:** `SET_A1__EMPTY_X|THEN>A>CLOSE`

## Stärkste seitenübergreifende Mehrkartenrahmen

- **ABSTRACT_ROLE · 2 Karten · 5 Aussagen / 3 Seiten:** `KEEP_A1__SET_X1|X || KEEP_A1__SET_X1|X`
- **ABSTRACT_ROLE · 2 Karten · 3 Aussagen / 3 Seiten:** `KEEP_A1__KEEP_X1|CONT || KEEP_A1__SET_X1|X`
- **ABSTRACT_ROLE · 2 Karten · 3 Aussagen / 3 Seiten:** `SET_A1__SET_X1|A>X || KEEP_A1__SET_X1|X`
- **ABSTRACT_ROLE · 2 Karten · 3 Aussagen / 2 Seiten:** `KEEP_A1__SET_X1|X || KEEP_A1__KEEP_X1|REL`
- **ABSTRACT_ROLE · 2 Karten · 3 Aussagen / 2 Seiten:** `SET_A1__SET_X1|A>X || SET_A1__SET_X1|A>X`
- **EXACT_PORTABLE · 2 Karten · 2 Aussagen / 2 Seiten:** `A:^S;X:AIIN;C:- || A:^S;X:^AIIN;C:REL:AL`
- **ABSTRACT_ROLE · 2 Karten · 3 Aussagen / 3 Seiten:** `KEEP_A1__SET_X1|X || SET_A1__SET_X1|A>X`
- **ABSTRACT_ROLE · 2 Karten · 3 Aussagen / 2 Seiten:** `KEEP_A1__SET_X1|THEN>X || KEEP_A1__SET_X1|X`
- **ABSTRACT_ROLE · 2 Karten · 3 Aussagen / 2 Seiten:** `SET_A1__KEEP_X1|A>CONT || SET_A1__KEEP_X1|A>CONT`
- **EXACT_PORTABLE · 2 Karten · 2 Aussagen / 1 Seiten:** `A:S;X:-;C:- || A:^S;X:AIIN;C:-`
- **EXACT_PORTABLE · 2 Karten · 2 Aussagen / 1 Seiten:** `A:S;X:^Y;C:- || A:^S;X:AIIN;C:-`
- **EXACT_PORTABLE · 2 Karten · 2 Aussagen / 1 Seiten:** `A:SH;X:^OR;C:CONTINUE || A:SH;X:^OR;C:CONTINUE`

## Die 16 absichtlich verbfreien Fragmente

- `G515-E0048` / `daiin` / ARGUMENT_OR_VALUE_FRAGMENT: Bezug: den Arbeitswert.
- `G515-E0190` / `qotedy` / CLOSURE_FRAGMENT: Danach: auf Grad I; schließe den Schritt.
- `G515-E0221` / `dar` / RELATION_OR_ADDRESS_FRAGMENT: Vom Ausgangsmaterial; an der bezeichneten Stelle.
- `G515-E0240` / `otedy` / CLOSURE_FRAGMENT: Danach: auf Grad I; schließe den Schritt.
- `G515-E0335` / `dar` / RELATION_OR_ADDRESS_FRAGMENT: Von der Ausgangszeile; an der bezeichneten Stelle.
- `G515-E0336` / `qotey` / ARGUMENT_OR_VALUE_FRAGMENT: Danach: Bezug: den laufenden Eintrag; auf Grad I.
- `G515-E0406` / `ol` / CONTINUATION_FRAGMENT: Führe fort.
- `G515-E0446` / `dal` / RELATION_OR_ADDRESS_FRAGMENT: Zur Zielspalte.
- `G515-E0459` / `dair` / RELATION_OR_ADDRESS_FRAGMENT: Entlang der Lesebahn; an der bezeichneten Stelle.
- `G515-E0491` / `daly` / ARGUMENT_OR_VALUE_FRAGMENT: Bezug: den laufenden Eintrag; zur Zielspalte.
- `G515-E0497` / `dal` / RELATION_OR_ADDRESS_FRAGMENT: Zur Zielspalte.
- `G515-E0503` / `oteedy` / CLOSURE_FRAGMENT: Danach: auf Grad II; schließe den Schritt.
- `G515-E0547` / `lchey` / ARGUMENT_OR_VALUE_FRAGMENT: Bezug: den laufenden Eintrag; über die Eintragsverbindung.
- `G515-E0562` / `dor` / ARGUMENT_OR_VALUE_FRAGMENT: Bezug: die Eintragseinheit; an der bezeichneten Stelle.
- `G515-E0563` / `aiin` / ARGUMENT_OR_VALUE_FRAGMENT: Bezug: den Kennwert.
- `G515-E0579` / `daiin` / ARGUMENT_OR_VALUE_FRAGMENT: Bezug: den Kennwert.

## Vollständige 78-Aussagen-Ausgabe

### G515-S001 · f4r · HERBAL

Makro: `A:K+CH;X:Y;C:EXEC>ADDR:D>REL:AL || A:CH+P;X:^Y;C:ADDR:A>CLOSE`

Gib den Pflanzenposten zu und nimm den Pflanzenposten; zur Zielstelle; zur Ausführung; an der bezeichneten Stelle. Nimm den Pflanzenposten [wie zuvor] und setze den Pflanzenposten [wie zuvor] ein; an der bezeichneten Stelle; schließe den Schritt.

### G515-S002 · f4r · HERBAL

Makro: `A:SH;X:-;C:GRADE:I>CONTINUE || A:^SH;X:-;C:CONTINUE || A:SH;X:Y;C:GRADE:II || A:^SH;X:Y;C:THEN>GRADE:I || A:^SH;X:^Y;C:ADDR:D>EXEC>STAGE || A:CH;X:OR;C:- || A:T;X:Y+Y;C:EXEC || A:CH;X:OR;C:ADDR:D || A:SH;X:^OR;C:CONTINUE || A:SH;X:^OR;C:CONTINUE || A:CH+T;X:^OR;C:CONTINUE || A:SH+T+CH;X:Y;C:- || A:CH;X:AIIN;C:- || A:S;X:^AIIN;C:- || A:CH;X:OR+AIIN;C:- || A:^CH;X:^AIIN;C:CLASS>LOCAL:M || A:CH;X:^AIIN;C:THEN>CONTINUE || A:^CH;X:^AIIN;C:CONTINUE || A:^CH;X:Y;C:- || A:CH;X:AIIN;C:- || A:^CH;X:AIIN;C:THEN || A:^CH;X:AIIN;C:- || A:SH;X:AIN;C:- || A:CH;X:^AIN;C:THEN>CONTINUE || A:^CH;X:Y;C:- || A:T;X:Y+Y;C:- || A:^T;X:AIIN;C:- || A:OK;X:AIIN;C:- || A:CH+T;X:Y;C:-`

Halte; auf Grad I; führe fort. Im laufenden Satz halte; führe fort. Halte den Pflanzenposten; auf Grad II. Danach: im laufenden Satz halte den Pflanzenposten; auf Grad I. Im laufenden Satz halte den Pflanzenposten [wie zuvor]; zur Ausführung und auf der bezeichneten Stufe; an der bezeichneten Stelle. Nimm die Arbeitseinheit. Stelle den Pflanzenposten [außen] und den Pflanzenposten [innen] ein; zur Ausführung. Nimm die Arbeitseinheit; an der bezeichneten Stelle. Halte die Arbeitseinheit [wie zuvor]; führe fort. Halte die Arbeitseinheit [wie zuvor]; führe fort. Nimm die Arbeitseinheit [wie zuvor] und stelle die Arbeitseinheit [wie zuvor] ein; führe fort. Halte den Pflanzenposten, stelle den Pflanzenposten ein und nimm den Pflanzenposten. Nimm den Arbeitswert. Wähle den Arbeitswert [wie zuvor]. Nimm die Arbeitseinheit und den Arbeitswert. Im laufenden Satz nimm den Arbeitswert [wie zuvor]; in der bezeichneten Klasse und an der bezeichneten Stelle. Danach: nimm den Arbeitswert [wie zuvor]; führe fort. Im laufenden Satz nimm den Arbeitswert [wie zuvor]; führe fort. Im laufenden Satz nimm den Pflanzenposten. Nimm den Arbeitswert. Danach: im laufenden Satz nimm den Arbeitswert. Im laufenden Satz nimm den Arbeitswert. Halte den Materialanteil. Danach: nimm den Materialanteil [wie zuvor]; führe fort. Im laufenden Satz nimm den Pflanzenposten. Stelle den Pflanzenposten [außen] und den Pflanzenposten [innen] ein. Im laufenden Satz stelle den Arbeitswert ein. Setze den Arbeitswert im Arbeitsgang an. Nimm den Pflanzenposten und stelle den Pflanzenposten ein.

### G515-S003 · f4r · HERBAL

Makro: `A:P;X:Y+AIIN;C:ADDR:D || A:^P;X:Y;C:THEN || A:^P;X:Y;C:- || A:T;X:Y;C:CLOSE`

Setze den Pflanzenposten und den Arbeitswert ein; an der bezeichneten Stelle. Danach: im laufenden Satz setze den Pflanzenposten ein. Im laufenden Satz setze den Pflanzenposten ein. Stelle den Pflanzenposten ein; schließe den Schritt.

### G515-S004 · f4r · HERBAL

Makro: `A:CH;X:OR;C:- || A:SH+T+CH;X:Y+Y;C:- || A:T+CH;X:Y+Y;C:ADDR:D>GRADE:II || A:^CH;X:AIIN;C:THEN || A:CH+T;X:^AIIN;C:CONTINUE || A:^T;X:AIIN;C:- || A:CH+T;X:^AIIN;C:EXEC>LOCAL:M || A:SH;X:OR;C:- || A:SH;X:^OR;C:CONTINUE || A:SH;X:^OR;C:CONTINUE || A:CH+T;X:Y;C:- || A:CH+P;X:^Y;C:CONTINUE>CLOSE`

Nimm die Arbeitseinheit. Halte den Pflanzenposten [außen] und den Pflanzenposten [innen], stelle den Pflanzenposten [außen] und den Pflanzenposten [innen] ein und nimm den Pflanzenposten [außen] und den Pflanzenposten [innen]. Stelle den Pflanzenposten [außen] und den Pflanzenposten [innen] ein und nimm den Pflanzenposten [außen] und den Pflanzenposten [innen]; auf Grad II; an der bezeichneten Stelle. Danach: im laufenden Satz nimm den Arbeitswert. Nimm den Arbeitswert [wie zuvor] und stelle den Arbeitswert [wie zuvor] ein; führe fort. Im laufenden Satz stelle den Arbeitswert ein. Nimm den Arbeitswert [wie zuvor] und stelle den Arbeitswert [wie zuvor] ein; zur Ausführung; an der bezeichneten Stelle. Halte die Arbeitseinheit. Halte die Arbeitseinheit [wie zuvor]; führe fort. Halte die Arbeitseinheit [wie zuvor]; führe fort. Nimm den Pflanzenposten und stelle den Pflanzenposten ein. Nimm den Pflanzenposten [wie zuvor] und setze den Pflanzenposten [wie zuvor] ein; führe fort; schließe den Schritt.

### G515-S005 · f4r · HERBAL

Makro: `A:-;X:AIIN;C:- || A:CH+K+CH;X:Y;C:EXEC || A:T;X:Y;C:- || A:K;X:OR;C:- || A:^K;X:AIIN;C:- || A:^K;X:^AIIN;C:EXEC>STAGE:II>REL:L || A:SH;X:OR;C:- || A:SH+SH;X:Y;C:CONTINUE || A:CH+P;X:AIIN;C:- || A:CH;X:^AIIN;C:THEN>EXEC>STAGE || A:SH;X:OR;C:GRADE:I || A:^SH;X:Y;C:THEN || A:S;X:^Y;C:EXEC>STAGE || A:CH;X:AIIN;C:- || A:CH;X:AIIN;C:- || A:^CH;X:AIIN;C:- || A:CH+T;X:Y;C:GRADE:I`

Bezug: den Arbeitswert. Nimm den Pflanzenposten, gib den Pflanzenposten zu und nimm den Pflanzenposten; zur Ausführung. Stelle den Pflanzenposten ein. Gib die Arbeitseinheit zu. Im laufenden Satz gib den Arbeitswert zu. Im laufenden Satz gib den Arbeitswert [wie zuvor] zu; über die Verbindung im Pflanzenartikel; zur Ausführung und auf der zweiten Stufe. Halte die Arbeitseinheit. Halte den Pflanzenposten und halte den Pflanzenposten; führe fort. Nimm den Arbeitswert und setze den Arbeitswert ein. Danach: nimm den Arbeitswert [wie zuvor]; zur Ausführung und auf der bezeichneten Stufe. Halte die Arbeitseinheit; auf Grad I. Danach: im laufenden Satz halte den Pflanzenposten. Wähle den Pflanzenposten [wie zuvor]; zur Ausführung und auf der bezeichneten Stufe. Nimm den Arbeitswert. Nimm den Arbeitswert. Im laufenden Satz nimm den Arbeitswert. Nimm den Pflanzenposten und stelle den Pflanzenposten ein; auf Grad I.

### G515-S006 · f20v · HERBAL

Makro: `A:S;X:-;C:LOCAL:F>STAGE || A:^S;X:-;C:REL:AR || A:OK;X:Y;C:EXEC || A:^OK;X:Y;C:- || A:P+CH;X:Y;C:EXEC>LOCAL:F>EXEC>GRADE:I || A:P;X:Y;C:EXEC || A:P;X:Y;C:BEGIN>EXEC || A:^P;X:Y;C:CONTINUE || A:P;X:Y;C:EXEC>CLOSE`

Wähle; auf der bezeichneten Stufe; an der bezeichneten Stelle. Im laufenden Satz wähle; vom Ausgangsmaterial. Setze den Pflanzenposten im Arbeitsgang an; zur Ausführung. Im laufenden Satz setze den Pflanzenposten im Arbeitsgang an. Setze den Pflanzenposten ein und nimm den Pflanzenposten; zur Ausführung [außen], zur Ausführung [innen] und auf Grad I; an der bezeichneten Stelle. Setze den Pflanzenposten ein; zur Ausführung. Setze den Pflanzenposten ein; mit Beginnmarker und zur Ausführung. Im laufenden Satz setze den Pflanzenposten ein; führe fort. Setze den Pflanzenposten ein; zur Ausführung; schließe den Schritt.

### G515-S007 · f20v · HERBAL

Makro: `A:CH+P;X:Y;C:- || A:S+S;X:^Y;C:EXEC || A:K;X:Y;C:EXEC>STAGE || A:CH;X:^Y;C:GRADE:I>EXEC>REL:L || A:^CH;X:^Y;C:CONTINUE || A:CH;X:^Y;C:EXEC>STAGE || A:CH+T;X:Y;C:- || A:^T;X:^Y;C:THEN>CONTINUE || A:^T;X:^Y;C:CONTINUE || A:CH;X:AIIN;C:EXEC>ADDR:D || A:^CH;X:Y;C:THEN || A:OK;X:Y;C:- || A:SH;X:^Y;C:EXEC || A:K;X:^Y;C:CONTINUE || A:SH;X:^Y;C:CONTINUE || A:CH+CH+T;X:Y;C:- || A:^T;X:Y;C:THEN || A:^T;X:Y;C:- || A:T+SH;X:Y;C:CONTINUE || A:^SH;X:Y;C:THEN || A:SH;X:^Y;C:EXEC || A:^SH;X:OR;C:- || A:^SH;X:AIIN;C:- || A:SH;X:^AIIN;C:CONTINUE || A:^SH;X:AIIN;C:-`

Nimm den Pflanzenposten und setze den Pflanzenposten ein. Wähle den Pflanzenposten [wie zuvor] und wähle den Pflanzenposten [wie zuvor]; zur Ausführung. Gib den Pflanzenposten zu; zur Ausführung und auf der bezeichneten Stufe. Nimm den Pflanzenposten [wie zuvor]; über die Verbindung im Pflanzenartikel; auf Grad I und zur Ausführung. Im laufenden Satz nimm den Pflanzenposten [wie zuvor]; führe fort. Nimm den Pflanzenposten [wie zuvor]; zur Ausführung und auf der bezeichneten Stufe. Nimm den Pflanzenposten und stelle den Pflanzenposten ein. Danach: im laufenden Satz stelle den Pflanzenposten [wie zuvor] ein; führe fort. Im laufenden Satz stelle den Pflanzenposten [wie zuvor] ein; führe fort. Nimm den Arbeitswert; zur Ausführung; an der bezeichneten Stelle. Danach: im laufenden Satz nimm den Pflanzenposten. Setze den Pflanzenposten im Arbeitsgang an. Halte den Pflanzenposten [wie zuvor]; zur Ausführung. Gib den Pflanzenposten [wie zuvor] zu; führe fort. Halte den Pflanzenposten [wie zuvor]; führe fort. Nimm den Pflanzenposten, nimm den Pflanzenposten und stelle den Pflanzenposten ein. Danach: im laufenden Satz stelle den Pflanzenposten ein. Im laufenden Satz stelle den Pflanzenposten ein. Stelle den Pflanzenposten ein und halte den Pflanzenposten; führe fort. Danach: im laufenden Satz halte den Pflanzenposten. Halte den Pflanzenposten [wie zuvor]; zur Ausführung. Im laufenden Satz halte die Arbeitseinheit. Im laufenden Satz halte den Arbeitswert. Halte den Arbeitswert [wie zuvor]; führe fort. Im laufenden Satz halte den Arbeitswert.

### G515-S008 · f20v · HERBAL

Makro: `A:T+SH;X:-;C:CONTINUE || A:^SH;X:-;C:LOCAL:F>CONTINUE>CONTINUE || A:^SH;X:OR;C:THEN || A:SH;X:^OR;C:CONTINUE || A:SH;X:OR;C:- || A:SH+CH;X:Y;C:LOCAL:F>EXEC>ADDR:D || A:CH;X:Y;C:THEN || A:CH+CH+P;X:Y;C:- || A:^P;X:Y;C:- || A:^P;X:^Y;C:ADDR:D>EXEC>STAGE || A:CH+K;X:Y;C:CLASS || A:^K;X:AIN;C:- || A:CH;X:Y;C:GRADE:I>EXEC || A:SH+S;X:^Y;C:EXEC || A:CH+S;X:^Y;C:GRADE:I>EXEC || A:^S;X:^Y;C:REL:AR || A:^S;X:AIIN;C:- || A:SH+CH+T;X:Y;C:EXEC || A:SH;X:^Y;C:EXEC || A:CH+T;X:Y;C:- || A:^T;X:AIIN;C:- || A:SH;X:Y;C:GRADE:I>EXEC || A:T;X:Y;C:GRADE:I || A:S;X:^Y;C:- || A:S;X:AIIN;C:EXEC || A:SH;X:AIN;C:- || A:CH;X:OR+Y;C:REL:AL || A:SH;X:^Y;C:EXEC || A:^SH;X:^Y;C:REL:AR || A:^SH;X:Y;C:- || A:^SH;X:AIIN;C:- || A:^SH;X:^AIIN;C:ADDR:D || A:S;X:^AIIN;C:- || A:K;X:Y+Y;C:- || A:K;X:Y;C:GRADE:I>EXEC>ADDR:D || A:^K;X:^Y;C:CLASS || A:CH+T;X:Y;C:- || A:^T;X:^Y;C:CONTINUE || A:SH;X:^Y;C:ADDR:D || A:^SH;X:Y;C:THEN || A:^SH;X:^Y;C:ADDR:D || A:SH+OK;X:AIIN;C:- || A:CH+CH+T;X:Y;C:EXEC || A:^T;X:^Y;C:CONTINUE || A:^T;X:AIIN;C:- || A:^T;X:Y;C:- || A:CH;X:OR;C:- || A:T;X:Y;C:GRADE:I || A:OK;X:^Y;C:EXEC>STAGE || A:^OK;X:Y;C:- || A:^OK;X:^Y;C:CONTINUE || A:CH;X:OR+Y;C:-`

Stelle ein und halte; führe fort. Im laufenden Satz halte; an der bezeichneten Stelle; führe 2-mal fort. Danach: im laufenden Satz halte die Arbeitseinheit. Halte die Arbeitseinheit [wie zuvor]; führe fort. Halte die Arbeitseinheit. Halte den Pflanzenposten und nimm den Pflanzenposten; zur Ausführung; an der bezeichneten Stelle und an der bezeichneten Stelle. Danach: nimm den Pflanzenposten. Nimm den Pflanzenposten, nimm den Pflanzenposten und setze den Pflanzenposten ein. Im laufenden Satz setze den Pflanzenposten ein. Im laufenden Satz setze den Pflanzenposten [wie zuvor] ein; zur Ausführung und auf der bezeichneten Stufe; an der bezeichneten Stelle. Nimm den Pflanzenposten und gib den Pflanzenposten zu; in der bezeichneten Klasse. Im laufenden Satz gib den Materialanteil zu. Nimm den Pflanzenposten; auf Grad I und zur Ausführung. Halte den Pflanzenposten [wie zuvor] und wähle den Pflanzenposten [wie zuvor]; zur Ausführung. Nimm den Pflanzenposten [wie zuvor] und wähle den Pflanzenposten [wie zuvor]; auf Grad I und zur Ausführung. Im laufenden Satz wähle den Pflanzenposten [wie zuvor]; vom Ausgangsmaterial. Im laufenden Satz wähle den Arbeitswert. Halte den Pflanzenposten, nimm den Pflanzenposten und stelle den Pflanzenposten ein; zur Ausführung. Halte den Pflanzenposten [wie zuvor]; zur Ausführung. Nimm den Pflanzenposten und stelle den Pflanzenposten ein. Im laufenden Satz stelle den Arbeitswert ein. Halte den Pflanzenposten; auf Grad I und zur Ausführung. Stelle den Pflanzenposten ein; auf Grad I. Wähle den Pflanzenposten [wie zuvor]. Wähle den Arbeitswert; zur Ausführung. Halte den Materialanteil. Nimm die Arbeitseinheit und den Pflanzenposten; zur Zielstelle. Halte den Pflanzenposten [wie zuvor]; zur Ausführung. Im laufenden Satz halte den Pflanzenposten [wie zuvor]; vom Ausgangsmaterial. Im laufenden Satz halte den Pflanzenposten. Im laufenden Satz halte den Arbeitswert. Im laufenden Satz halte den Arbeitswert [wie zuvor]; an der bezeichneten Stelle. Wähle den Arbeitswert [wie zuvor]. Gib den Pflanzenposten [außen] und den Pflanzenposten [innen] zu. Gib den Pflanzenposten zu; auf Grad I und zur Ausführung; an der bezeichneten Stelle. Im laufenden Satz gib den Pflanzenposten [wie zuvor] zu; in der bezeichneten Klasse. Nimm den Pflanzenposten und stelle den Pflanzenposten ein. Im laufenden Satz stelle den Pflanzenposten [wie zuvor] ein; führe fort. Halte den Pflanzenposten [wie zuvor]; an der bezeichneten Stelle. Danach: im laufenden Satz halte den Pflanzenposten. Im laufenden Satz halte den Pflanzenposten [wie zuvor]; an der bezeichneten Stelle. Halte den Arbeitswert und setze den Arbeitswert im Arbeitsgang an. Nimm den Pflanzenposten, nimm den Pflanzenposten und stelle den Pflanzenposten ein; zur Ausführung. Im laufenden Satz stelle den Pflanzenposten [wie zuvor] ein; führe fort. Im laufenden Satz stelle den Arbeitswert ein. Im laufenden Satz stelle den Pflanzenposten ein. Nimm die Arbeitseinheit. Stelle den Pflanzenposten ein; auf Grad I. Setze den Pflanzenposten [wie zuvor] im Arbeitsgang an; zur Ausführung und auf der bezeichneten Stufe. Im laufenden Satz setze den Pflanzenposten im Arbeitsgang an. Im laufenden Satz setze den Pflanzenposten [wie zuvor] im Arbeitsgang an; führe fort. Nimm die Arbeitseinheit und den Pflanzenposten.

### G515-S009 · f31r · HERBAL

Makro: `A:K;X:Y;C:GRADE:II>ADDR:D>GRADE:I || A:CHD;X:Y;C:BEGIN>EXEC>LOCAL:F || A:SH;X:^Y;C:GRADE:II || A:S;X:^Y;C:- || A:^S;X:AIIN;C:- || A:OK;X:^AIIN;C:GRADE:II || A:CH+P+K;X:^AIIN;C:GRADE:I>ADDR:A>GRADE:I>EXEC || A:CH;X:Y;C:ADDR:D>GRADE:II || A:^CH;X:AIIN;C:- || A:OK;X:^AIIN;C:GRADE:II>CLOSE`

Gib den Pflanzenposten zu; auf Grad II und auf Grad I; an der bezeichneten Stelle. Bearbeite den Pflanzenposten; mit Beginnmarker und zur Ausführung; an der bezeichneten Stelle. Halte den Pflanzenposten [wie zuvor]; auf Grad II. Wähle den Pflanzenposten [wie zuvor]. Im laufenden Satz wähle den Arbeitswert. Setze den Arbeitswert [wie zuvor] im Arbeitsgang an; auf Grad II. Nimm den Arbeitswert [wie zuvor], setze den Arbeitswert [wie zuvor] ein und gib den Arbeitswert [wie zuvor] zu; auf Grad I [außen], auf Grad I [innen] und zur Ausführung; an der bezeichneten Stelle. Nimm den Pflanzenposten; auf Grad II; an der bezeichneten Stelle. Im laufenden Satz nimm den Arbeitswert. Setze den Arbeitswert [wie zuvor] im Arbeitsgang an; auf Grad II; schließe den Schritt.

### G515-S010 · f31r · HERBAL

Makro: `A:OK+S;X:-;C:GRADE:II || A:S;X:-;C:- || A:^S;X:AIIN;C:- || A:SH+K;X:Y;C:GRADE:I>GRADE:II || A:^K;X:^Y;C:GRADE:I>LOCAL:F || A:OK;X:Y;C:GRADE:II || A:^OK;X:Y;C:- || A:^OK;X:AIIN;C:- || A:OK;X:Y;C:GRADE:II || A:S;X:^Y;C:REL:AIR || A:CH+K;X:Y;C:GRADE:I || A:S;X:^Y;C:- || A:^S;X:AIIN;C:- || A:^S;X:^AIIN;C:STAGE:II || A:^S;X:^AIIN;C:THEN>REL:AR || A:^S;X:Y;C:- || A:^S;X:^Y;C:ADDR:D>REL:AR || A:^S;X:^Y;C:REL:L>EXEC || A:R;X:^Y;C:- || A:^R;X:^Y;C:REL:AR || A:SH;X:Y;C:GRADE:II || A:K;X:^Y;C:GRADE:II>CONTINUE || A:CHD;X:Y;C:- || A:OK;X:Y;C:GRADE:I || A:^OK;X:AIIN;C:- || A:SH;X:Y;C:GRADE:II>EXEC>ADDR:D || A:OK;X:OR;C:GRADE:I`

Setze im Arbeitsgang an und wähle; auf Grad II. Wähle. Im laufenden Satz wähle den Arbeitswert. Halte den Pflanzenposten und gib den Pflanzenposten zu; auf Grad I und auf Grad II. Im laufenden Satz gib den Pflanzenposten [wie zuvor] zu; auf Grad I; an der bezeichneten Stelle. Setze den Pflanzenposten im Arbeitsgang an; auf Grad II. Im laufenden Satz setze den Pflanzenposten im Arbeitsgang an. Im laufenden Satz setze den Arbeitswert im Arbeitsgang an. Setze den Pflanzenposten im Arbeitsgang an; auf Grad II. Wähle den Pflanzenposten [wie zuvor]; entlang der Verarbeitungsbahn. Nimm den Pflanzenposten und gib den Pflanzenposten zu; auf Grad I. Wähle den Pflanzenposten [wie zuvor]. Im laufenden Satz wähle den Arbeitswert. Im laufenden Satz wähle den Arbeitswert [wie zuvor]; auf der zweiten Stufe. Danach: im laufenden Satz wähle den Arbeitswert [wie zuvor]; vom Ausgangsmaterial. Im laufenden Satz wähle den Pflanzenposten. Im laufenden Satz wähle den Pflanzenposten [wie zuvor]; vom Ausgangsmaterial; an der bezeichneten Stelle. Im laufenden Satz wähle den Pflanzenposten [wie zuvor]; über die Verbindung im Pflanzenartikel; zur Ausführung. Markiere den Pflanzenposten [wie zuvor]. Im laufenden Satz markiere den Pflanzenposten [wie zuvor]; vom Ausgangsmaterial. Halte den Pflanzenposten; auf Grad II. Gib den Pflanzenposten [wie zuvor] zu; auf Grad II; führe fort. Bearbeite den Pflanzenposten. Setze den Pflanzenposten im Arbeitsgang an; auf Grad I. Im laufenden Satz setze den Arbeitswert im Arbeitsgang an. Halte den Pflanzenposten; auf Grad II und zur Ausführung; an der bezeichneten Stelle. Setze die Arbeitseinheit im Arbeitsgang an; auf Grad I.

### G515-S011 · f31r · HERBAL

Makro: `A:T+SH+OK;X:Y;C:GRADE:I>EXEC>ADDR:D || A:OK;X:^Y;C:GRADE:I>CLOSE`

Stelle den Pflanzenposten ein, halte den Pflanzenposten und setze den Pflanzenposten im Arbeitsgang an; auf Grad I und zur Ausführung; an der bezeichneten Stelle. Setze den Pflanzenposten [wie zuvor] im Arbeitsgang an; auf Grad I; schließe den Schritt.

### G515-S012 · f31r · HERBAL

Makro: `A:-;X:-;C:THEN>GRADE:I>CLOSE`

Danach: auf Grad I; schließe den Schritt.

### G515-S013 · f31r · HERBAL

Makro: `A:CH+P+S;X:-;C:GRADE:I>EXEC || A:CHD;X:-;C:ADDR:A || A:S;X:-;C:- || A:^S;X:AIIN;C:- || A:^S;X:^AIIN;C:REL:AL || A:K;X:Y;C:GRADE:II>ADDR:D>REL:AR || A:S;X:AIIN;C:- || A:CH+CH+K;X:Y;C:GRADE:I>GRADE:I || A:SH;X:^Y;C:GRADE:I>CONTINUE || A:OK;X:^Y;C:GRADE:I>CLOSE`

Nimm, setze ein und wähle; auf Grad I und zur Ausführung. Bearbeite; an der bezeichneten Stelle. Wähle. Im laufenden Satz wähle den Arbeitswert. Im laufenden Satz wähle den Arbeitswert [wie zuvor]; zur Zielstelle. Gib den Pflanzenposten zu; vom Ausgangsmaterial; auf Grad II; an der bezeichneten Stelle. Wähle den Arbeitswert. Nimm den Pflanzenposten, nimm den Pflanzenposten und gib den Pflanzenposten zu; auf Grad I [außen] und auf Grad I [innen]. Halte den Pflanzenposten [wie zuvor]; auf Grad I; führe fort. Setze den Pflanzenposten [wie zuvor] im Arbeitsgang an; auf Grad I; schließe den Schritt.

### G515-S014 · f31r · HERBAL

Makro: `A:K;X:Y+Y;C:GRADE:II>ADDR:D || A:CHD;X:Y;C:- || A:^CHD;X:^Y;C:REL:L>CLOSE`

Gib den Pflanzenposten [außen] und den Pflanzenposten [innen] zu; auf Grad II; an der bezeichneten Stelle. Bearbeite den Pflanzenposten. Im laufenden Satz bearbeite den Pflanzenposten [wie zuvor]; über die Verbindung im Pflanzenartikel; schließe den Schritt.

### G515-S015 · f31r · HERBAL

Makro: `A:SH;X:-;C:GRADE:I>CLOSE`

Halte; auf Grad I; schließe den Schritt.

### G515-S016 · f31r · HERBAL

Makro: `A:OK;X:-;C:GRADE:I>CLOSE`

Setze im Arbeitsgang an; auf Grad I; schließe den Schritt.

### G515-S017 · f31r · HERBAL

Makro: `A:CH;X:-;C:GRADE:I>EXEC>REL:L || A:CH;X:-;C:GRADE:I>EXEC>ADDR:D || A:OK;X:Y;C:GRADE:I>EXEC>ADDR:D || A:CH;X:^Y;C:GRADE:I>EXEC>REL:L || A:CH+T;X:Y;C:- || A:R;X:^Y;C:STAGE:II>STAGE || A:SH;X:^Y;C:GRADE:II>EXEC || A:SH+CH+T;X:Y;C:GRADE:I || A:OK;X:^Y;C:GRADE:I>CONTINUE`

Nimm; über die Verbindung im Pflanzenartikel; auf Grad I und zur Ausführung. Nimm; auf Grad I und zur Ausführung; an der bezeichneten Stelle. Setze den Pflanzenposten im Arbeitsgang an; auf Grad I und zur Ausführung; an der bezeichneten Stelle. Nimm den Pflanzenposten [wie zuvor]; über die Verbindung im Pflanzenartikel; auf Grad I und zur Ausführung. Nimm den Pflanzenposten und stelle den Pflanzenposten ein. Markiere den Pflanzenposten [wie zuvor]; auf der zweiten Stufe und auf der bezeichneten Stufe. Halte den Pflanzenposten [wie zuvor]; auf Grad II und zur Ausführung. Halte den Pflanzenposten, nimm den Pflanzenposten und stelle den Pflanzenposten ein; auf Grad I. Setze den Pflanzenposten [wie zuvor] im Arbeitsgang an; auf Grad I; führe fort.

### G515-S018 · f31r · HERBAL

Makro: `A:T;X:-;C:CONTINUE || A:SH+S;X:-;C:EXEC || A:OK;X:-;C:GRADE:I>CLOSE`

Stelle ein; führe fort. Halte und wähle; zur Ausführung. Setze im Arbeitsgang an; auf Grad I; schließe den Schritt.

### G515-S019 · f31r · HERBAL

Makro: `A:OK;X:-;C:GRADE:I>CLOSE`

Setze im Arbeitsgang an; auf Grad I; schließe den Schritt.

### G515-S020 · f31r · HERBAL

Makro: `A:OK;X:-;C:GRADE:I>CLOSE`

Setze im Arbeitsgang an; auf Grad I; schließe den Schritt.

### G515-S021 · f31r · HERBAL

Makro: `A:OK;X:-;C:GRADE:II>CLOSE`

Setze im Arbeitsgang an; auf Grad II; schließe den Schritt.

### G515-S022 · f31r · HERBAL

Makro: `A:-;X:-;C:ADDR:D>REL:AR || A:SH+SH;X:Y;C:GRADE:I>ADDR:D>GRADE:I || A:K;X:^Y;C:CONTINUE>GRADE:I>CONTINUE || A:OK;X:Y;C:- || A:^OK;X:^Y;C:REL:AL || A:^OK;X:Y;C:- || A:^OK;X:Y;C:ADDR:D>GRADE:II || A:K;X:Y;C:- || A:K;X:Y;C:GRADE:II || A:OK;X:^Y;C:ADDR:A>LOCAL:I>STAGE || A:K;X:Y+Y;C:GRADE:II || A:^K;X:AIIN;C:BEGIN>EXEC || A:CH+S;X:Y;C:GRADE:I || A:OK;X:^Y;C:GRADE:I>CLOSE`

Vom Ausgangsmaterial; an der bezeichneten Stelle. Halte den Pflanzenposten und halte den Pflanzenposten; auf Grad I [außen] und auf Grad I [innen]; an der bezeichneten Stelle. Gib den Pflanzenposten [wie zuvor] zu; auf Grad I; führe 2-mal fort. Setze den Pflanzenposten im Arbeitsgang an. Im laufenden Satz setze den Pflanzenposten [wie zuvor] im Arbeitsgang an; zur Zielstelle. Im laufenden Satz setze den Pflanzenposten im Arbeitsgang an. Im laufenden Satz setze den Pflanzenposten im Arbeitsgang an; auf Grad II; an der bezeichneten Stelle. Gib den Pflanzenposten zu. Gib den Pflanzenposten zu; auf Grad II. Setze den Pflanzenposten [wie zuvor] im Arbeitsgang an; auf der bezeichneten Stufe; an der bezeichneten Stelle und mit der lokalen Variante i. Gib den Pflanzenposten [außen] und den Pflanzenposten [innen] zu; auf Grad II. Im laufenden Satz gib den Arbeitswert zu; mit Beginnmarker und zur Ausführung. Nimm den Pflanzenposten und wähle den Pflanzenposten; auf Grad I. Setze den Pflanzenposten [wie zuvor] im Arbeitsgang an; auf Grad I; schließe den Schritt.

### G515-S023 · f31r · HERBAL

Makro: `A:SH;X:Y;C:GRADE:II || A:CHD;X:AIIN;C:- || A:^CHD;X:^AIIN;C:ADDR:D>REL:AR || A:SH;X:OR;C:CONTINUE>GRADE:I || A:K;X:^OR;C:BEGIN>EXEC>GRADE:I>GRADE:I>CLOSE`

Halte den Pflanzenposten; auf Grad II. Bearbeite den Arbeitswert. Im laufenden Satz bearbeite den Arbeitswert [wie zuvor]; vom Ausgangsmaterial; an der bezeichneten Stelle. Halte die Arbeitseinheit; auf Grad I; führe fort. Gib die Arbeitseinheit [wie zuvor] zu; mit Beginnmarker, zur Ausführung, auf Grad I [außen] und auf Grad I [innen]; schließe den Schritt.

### G515-S024 · f31r · HERBAL

Makro: `A:-;X:-;C:THEN>GRADE:I>CLOSE`

Danach: auf Grad I; schließe den Schritt.

### G515-S025 · f31r · HERBAL

Makro: `A:K;X:Y;C:GRADE:I>CLOSE`

Gib den Pflanzenposten zu; auf Grad I; schließe den Schritt.

### G515-S026 · f31r · HERBAL

Makro: `A:S;X:-;C:REL:AL || A:S+S;X:-;C:ADDR:A>STAGE || A:^S;X:OR;C:- || A:CHD;X:Y;C:- || A:^CHD;X:AIIN;C:- || A:OK;X:^AIIN;C:GRADE:II>CLOSE`

Wähle; zur Zielstelle. Wähle und wähle; auf der bezeichneten Stufe; an der bezeichneten Stelle. Im laufenden Satz wähle die Arbeitseinheit. Bearbeite den Pflanzenposten. Im laufenden Satz bearbeite den Arbeitswert. Setze den Arbeitswert [wie zuvor] im Arbeitsgang an; auf Grad II; schließe den Schritt.

### G515-S027 · f31r · HERBAL

Makro: `A:SH;X:Y;C:GRADE:I>ADDR:D>REL:AIR || A:SH;X:^Y;C:GRADE:I>CONTINUE || A:CH+K;X:Y;C:GRADE:I || A:OK;X:^Y;C:GRADE:I>ADDR:D>ADDR:AM || A:^OK;X:OR;C:THEN>GRADE:I || A:CH+T;X:AIIN+Y;C:-`

Halte den Pflanzenposten; entlang der Verarbeitungsbahn; auf Grad I; an der bezeichneten Stelle. Halte den Pflanzenposten [wie zuvor]; auf Grad I; führe fort. Nimm den Pflanzenposten und gib den Pflanzenposten zu; auf Grad I. Setze den Pflanzenposten [wie zuvor] im Arbeitsgang an; auf Grad I; an der bezeichneten Stelle und an der bezeichneten Stelle. Danach: im laufenden Satz setze die Arbeitseinheit im Arbeitsgang an; auf Grad I. Nimm den Arbeitswert und den Pflanzenposten und stelle den Arbeitswert und den Pflanzenposten ein.

### G515-S028 · f66r · SOURCE_SECTION_T

Makro: `A:P;X:AIIN;C:- || A:^P;X:^AIIN;C:THEN>GRADE:II>CLOSE`

Setze den Kennwert ein. Danach: im laufenden Satz setze den Kennwert [wie zuvor] ein; auf Grad II; schließe den Schritt.

### G515-S029 · f66r · SOURCE_SECTION_T

Makro: `A:P+CHD;X:-;C:EXEC>CLOSE`

Setze ein und bearbeite; zur Ausführung; schließe den Schritt.

### G515-S030 · f66r · SOURCE_SECTION_T

Makro: `A:CH+P;X:-;C:ADDR:A || A:CH+CH;X:Y;C:GRADE:I>LOCAL:F || A:SH;X:^Y;C:ADDR:D>CLOSE`

Entnimm und setze ein; an der bezeichneten Stelle. Entnimm den laufenden Eintrag und entnimm den laufenden Eintrag; auf Grad I; an der bezeichneten Stelle. Halte den laufenden Eintrag [wie zuvor] fest; an der bezeichneten Stelle; schließe den Schritt.

### G515-S031 · f66r · SOURCE_SECTION_T

Makro: `A:P+CH+S;X:Y;C:GRADE:I || A:P+CHD;X:^Y;C:CONTINUE || A:OK+S;X:^Y;C:REL:AL || A:S;X:^Y;C:REL:AIR || A:SH+K;X:Y;C:GRADE:I>GRADE:I || A:OK;X:^Y;C:GRADE:II>ADDR:D>REL:AR || A:OK;X:^Y;C:REL:AL || A:OK;X:^Y;C:GRADE:I>CLOSE`

Setze den laufenden Eintrag ein, entnimm den laufenden Eintrag und wähle den laufenden Eintrag; auf Grad I. Setze den laufenden Eintrag [wie zuvor] ein und bearbeite den laufenden Eintrag [wie zuvor]; führe fort. Trage den laufenden Eintrag [wie zuvor] ein und wähle den laufenden Eintrag [wie zuvor]; zur Zielspalte. Wähle den laufenden Eintrag [wie zuvor]; entlang der Lesebahn. Halte den laufenden Eintrag fest und ordne den laufenden Eintrag zu; auf Grad I [außen] und auf Grad I [innen]. Trage den laufenden Eintrag [wie zuvor] ein; von der Ausgangszeile; auf Grad II; an der bezeichneten Stelle. Trage den laufenden Eintrag [wie zuvor] ein; zur Zielspalte. Trage den laufenden Eintrag [wie zuvor] ein; auf Grad I; schließe den Schritt.

### G515-S032 · f66r · SOURCE_SECTION_T

Makro: `A:OK;X:-;C:GRADE:II>CLOSE`

Trage ein; auf Grad II; schließe den Schritt.

### G515-S033 · f66r · SOURCE_SECTION_T

Makro: `A:OK;X:-;C:REL:AL || A:OK;X:-;C:GRADE:I>CLOSE`

Trage ein; zur Zielspalte. Trage ein; auf Grad I; schließe den Schritt.

### G515-S034 · f66r · SOURCE_SECTION_T

Makro: `A:OK+SH;X:-;C:ADDR:D || A:K+SH;X:Y;C:GRADE:I>CLOSE`

Trage ein und halte fest; an der bezeichneten Stelle. Ordne den laufenden Eintrag zu und halte den laufenden Eintrag fest; auf Grad I; schließe den Schritt.

### G515-S035 · f66r · SOURCE_SECTION_T

Makro: `A:CH;X:-;C:ADDR:A>CLOSE`

Entnimm; an der bezeichneten Stelle; schließe den Schritt.

### G515-S036 · f66r · SOURCE_SECTION_T

Makro: `A:CH+T;X:Y;C:ADDR:D || A:OK+S;X:^Y;C:GRADE:II || A:CH;X:^Y;C:GRADE:II>EXEC || A:OK+CH;X:^Y;C:EXEC || A:^CH;X:Y;C:- || A:CH+K;X:Y;C:GRADE:II || A:CHD;X:Y;C:- || A:CH+K;X:Y;C:- || A:SH;X:Y;C:ADDR:D || A:^SH;X:^Y;C:THEN>GRADE:I>CLOSE`

Entnimm den laufenden Eintrag und lege den laufenden Eintrag fest; an der bezeichneten Stelle. Trage den laufenden Eintrag [wie zuvor] ein und wähle den laufenden Eintrag [wie zuvor]; auf Grad II. Entnimm den laufenden Eintrag [wie zuvor]; auf Grad II und zur Ausführung. Trage den laufenden Eintrag [wie zuvor] ein und entnimm den laufenden Eintrag [wie zuvor]; zur Ausführung. Im laufenden Satz entnimm den laufenden Eintrag. Entnimm den laufenden Eintrag und ordne den laufenden Eintrag zu; auf Grad II. Bearbeite den laufenden Eintrag. Entnimm den laufenden Eintrag und ordne den laufenden Eintrag zu. Halte den laufenden Eintrag fest; an der bezeichneten Stelle. Danach: im laufenden Satz halte den laufenden Eintrag [wie zuvor] fest; auf Grad I; schließe den Schritt.

### G515-S037 · f66r · SOURCE_SECTION_T

Makro: `A:CHD;X:Y;C:- || A:CHD;X:Y;C:- || A:^CHD;X:^Y;C:THEN>GRADE:I>REL:AL || A:CH+CH+P;X:OR;C:GRADE:I || A:K;X:Y;C:ADDR:A>CLOSE`

Bearbeite den laufenden Eintrag. Bearbeite den laufenden Eintrag. Danach: im laufenden Satz bearbeite den laufenden Eintrag [wie zuvor]; zur Zielspalte; auf Grad I. Entnimm die Eintragseinheit, entnimm die Eintragseinheit und setze die Eintragseinheit ein; auf Grad I. Ordne den laufenden Eintrag zu; an der bezeichneten Stelle; schließe den Schritt.

### G515-S038 · f66r · SOURCE_SECTION_T

Makro: `A:-;X:-;C:ADDR:D>REL:AR || A:-;X:Y;C:THEN>GRADE:I || A:K;X:^Y;C:CONTINUE || A:^K;X:^Y;C:REL:AR || A:OK;X:Y;C:GRADE:II>EXEC>ADDR:D || A:OK;X:Y;C:GRADE:I>EXEC>ADDR:D || A:OK;X:Y;C:GRADE:I>EXEC>ADDR:D || A:OK;X:^Y;C:REL:AR || A:SH+K;X:Y;C:GRADE:I || A:OK;X:Y;C:GRADE:II>EXEC>ADDR:D || A:OK;X:^Y;C:GRADE:I>CLOSE`

Von der Ausgangszeile; an der bezeichneten Stelle. Danach: Bezug: den laufenden Eintrag; auf Grad I. Ordne den laufenden Eintrag [wie zuvor] zu; führe fort. Im laufenden Satz ordne den laufenden Eintrag [wie zuvor] zu; von der Ausgangszeile. Trage den laufenden Eintrag ein; auf Grad II und zur Ausführung; an der bezeichneten Stelle. Trage den laufenden Eintrag ein; auf Grad I und zur Ausführung; an der bezeichneten Stelle. Trage den laufenden Eintrag ein; auf Grad I und zur Ausführung; an der bezeichneten Stelle. Trage den laufenden Eintrag [wie zuvor] ein; von der Ausgangszeile. Halte den laufenden Eintrag fest und ordne den laufenden Eintrag zu; auf Grad I. Trage den laufenden Eintrag ein; auf Grad II und zur Ausführung; an der bezeichneten Stelle. Trage den laufenden Eintrag [wie zuvor] ein; auf Grad I; schließe den Schritt.

### G515-S039 · f66r · SOURCE_SECTION_T

Makro: `A:K;X:Y;C:EXEC>ADDR:D>REL:AR || A:K;X:Y;C:GRADE:II>EXEC>CLOSE`

Ordne den laufenden Eintrag zu; von der Ausgangszeile; zur Ausführung; an der bezeichneten Stelle. Ordne den laufenden Eintrag zu; auf Grad II und zur Ausführung; schließe den Schritt.

### G515-S040 · f66r · SOURCE_SECTION_T

Makro: `A:CH+K;X:Y;C:EXEC>GRADE:I>GRADE:II || A:OK;X:Y;C:GRADE:I>EXEC>ADDR:D || A:CH+K;X:^Y;C:GRADE:I>EXEC>CLOSE`

Entnimm den laufenden Eintrag und ordne den laufenden Eintrag zu; zur Ausführung, auf Grad I und auf Grad II. Trage den laufenden Eintrag ein; auf Grad I und zur Ausführung; an der bezeichneten Stelle. Entnimm den laufenden Eintrag [wie zuvor] und ordne den laufenden Eintrag [wie zuvor] zu; auf Grad I und zur Ausführung; schließe den Schritt.

### G515-S041 · f66r · SOURCE_SECTION_T

Makro: `A:OK;X:Y;C:GRADE:II || A:K;X:Y+Y;C:ADDR:D || A:CH+CH+T;X:^Y;C:EXEC || A:R;X:AIIN;C:THEN || A:SH;X:^AIIN;C:GRADE:I>CONTINUE || A:OK;X:AIIN;C:- || A:SH;X:AIIN;C:GRADE:I>EXEC>ADDR:D`

Trage den laufenden Eintrag ein; auf Grad II. Ordne den laufenden Eintrag [außen] und den laufenden Eintrag [innen] zu; an der bezeichneten Stelle. Entnimm den laufenden Eintrag [wie zuvor], entnimm den laufenden Eintrag [wie zuvor] und lege den laufenden Eintrag [wie zuvor] fest; zur Ausführung. Danach: kennzeichne den Kennwert. Halte den Kennwert [wie zuvor] fest; auf Grad I; führe fort. Trage den Kennwert ein. Halte den Kennwert fest; auf Grad I und zur Ausführung; an der bezeichneten Stelle.

### G515-S042 · f66r · SOURCE_SECTION_T

Makro: `A:T+CH+P;X:Y;C:EXEC>GRADE:II || A:^P;X:^Y;C:ADDR:D>CONTINUE || A:K+CH;X:Y;C:EXEC>ADDR:D || A:OK;X:Y;C:GRADE:I>EXEC>ADDR:D || A:OK+SH;X:Y;C:- || A:P;X:AIIN;C:BEGIN>EXEC || A:K+S;X:Y;C:ADDR:D>REL:AIR>EXEC>STAGE:II || A:OK;X:Y;C:ADDR:D || A:SH+R;X:^Y;C:ADDR:D>CONTINUE>STAGE:II>STAGE || A:K;X:Y;C:REL:AL || A:SH+K;X:Y;C:- || A:OK;X:Y;C:- || A:SH+K;X:^Y;C:GRADE:I>REL:AIR || A:CH;X:Y;C:THEN || A:^CH;X:^Y;C:ADDR:D>REL:AR || A:OK;X:Y;C:GRADE:II || A:SH;X:Y;C:ADDR:D || A:K;X:Y;C:CONTINUE || A:^K;X:^Y;C:EXEC || A:CH+K;X:Y;C:GRADE:I || A:SH+CH+T;X:Y;C:- || A:SH;X:^Y;C:REL:AL>REL:AL>GRADE:I>CLOSE`

Lege den laufenden Eintrag fest, entnimm den laufenden Eintrag und setze den laufenden Eintrag ein; zur Ausführung und auf Grad II. Im laufenden Satz setze den laufenden Eintrag [wie zuvor] ein; an der bezeichneten Stelle; führe fort. Ordne den laufenden Eintrag zu und entnimm den laufenden Eintrag; zur Ausführung; an der bezeichneten Stelle. Trage den laufenden Eintrag ein; auf Grad I und zur Ausführung; an der bezeichneten Stelle. Trage den laufenden Eintrag ein und halte den laufenden Eintrag fest. Setze den Kennwert ein; mit Beginnmarker und zur Ausführung. Ordne den laufenden Eintrag zu und wähle den laufenden Eintrag; entlang der Lesebahn; zur Ausführung und auf der zweiten Stufe; an der bezeichneten Stelle. Trage den laufenden Eintrag ein; an der bezeichneten Stelle. Halte den laufenden Eintrag [wie zuvor] fest und kennzeichne den laufenden Eintrag [wie zuvor]; auf der zweiten Stufe und auf der bezeichneten Stufe; an der bezeichneten Stelle; führe fort. Ordne den laufenden Eintrag zu; zur Zielspalte. Halte den laufenden Eintrag fest und ordne den laufenden Eintrag zu. Trage den laufenden Eintrag ein. Halte den laufenden Eintrag [wie zuvor] fest und ordne den laufenden Eintrag [wie zuvor] zu; entlang der Lesebahn; auf Grad I. Danach: entnimm den laufenden Eintrag. Im laufenden Satz entnimm den laufenden Eintrag [wie zuvor]; von der Ausgangszeile; an der bezeichneten Stelle. Trage den laufenden Eintrag ein; auf Grad II. Halte den laufenden Eintrag fest; an der bezeichneten Stelle. Ordne den laufenden Eintrag zu; führe fort. Im laufenden Satz ordne den laufenden Eintrag [wie zuvor] zu; zur Ausführung. Entnimm den laufenden Eintrag und ordne den laufenden Eintrag zu; auf Grad I. Halte den laufenden Eintrag fest, entnimm den laufenden Eintrag und lege den laufenden Eintrag fest. Halte den laufenden Eintrag [wie zuvor] fest; zur Zielspalte [außen] und zur Zielspalte [innen]; auf Grad I; schließe den Schritt.

### G515-S043 · f66r · SOURCE_SECTION_T

Makro: `A:CH+T;X:-;C:GRADE:I>ADDR:A || A:R;X:-;C:- || A:SH;X:-;C:GRADE:I>EXEC>ADDR:D || A:SH+OK+R;X:-;C:STAGE || A:^R;X:Y;C:- || A:^R;X:^Y;C:ADDR:D>REL:AR>ADDR:D || A:SH;X:OR;C:- || A:SH;X:^OR;C:GRADE:I>EXEC>REL:AL || A:SH;X:Y;C:CONTINUE>ADDR:D || A:OK+CHD;X:Y;C:- || A:P;X:Y;C:EXEC || A:^P;X:Y;C:THEN || A:CHD+R;X:^Y;C:STAGE || A:SH;X:^Y;C:GRADE:II>ADDR:S || A:K;X:^Y;C:REL:AR>CLOSE`

Entnimm und lege fest; auf Grad I; an der bezeichneten Stelle. Kennzeichne. Halte fest; auf Grad I und zur Ausführung; an der bezeichneten Stelle. Halte fest, trage ein und kennzeichne; auf der bezeichneten Stufe. Im laufenden Satz kennzeichne den laufenden Eintrag. Im laufenden Satz kennzeichne den laufenden Eintrag [wie zuvor]; von der Ausgangszeile; an der bezeichneten Stelle [außen] und an der bezeichneten Stelle [innen]. Halte die Eintragseinheit fest. Halte die Eintragseinheit [wie zuvor] fest; zur Zielspalte; auf Grad I und zur Ausführung. Halte den laufenden Eintrag fest; an der bezeichneten Stelle; führe fort. Trage den laufenden Eintrag ein und bearbeite den laufenden Eintrag. Setze den laufenden Eintrag ein; zur Ausführung. Danach: im laufenden Satz setze den laufenden Eintrag ein. Bearbeite den laufenden Eintrag [wie zuvor] und kennzeichne den laufenden Eintrag [wie zuvor]; auf der bezeichneten Stufe. Halte den laufenden Eintrag [wie zuvor] fest; auf Grad II; an der bezeichneten Stelle. Ordne den laufenden Eintrag [wie zuvor] zu; von der Ausgangszeile; schließe den Schritt.

### G515-S044 · f66r · SOURCE_SECTION_T

Makro: `A:OK+CH;X:Y;C:GRADE:I || A:OK+R;X:^Y;C:STAGE || A:CH+K;X:Y;C:GRADE:I || A:^K;X:Y;C:REL:AL || A:^K;X:AIIN;C:- || A:^K;X:^AIIN;C:REL:AL || A:SH;X:^AIIN;C:GRADE:I>CLOSE`

Trage den laufenden Eintrag ein und entnimm den laufenden Eintrag; auf Grad I. Trage den laufenden Eintrag [wie zuvor] ein und kennzeichne den laufenden Eintrag [wie zuvor]; auf der bezeichneten Stufe. Entnimm den laufenden Eintrag und ordne den laufenden Eintrag zu; auf Grad I. Im laufenden Satz ordne den laufenden Eintrag zu; zur Zielspalte. Im laufenden Satz ordne den Kennwert zu. Im laufenden Satz ordne den Kennwert [wie zuvor] zu; zur Zielspalte. Halte den Kennwert [wie zuvor] fest; auf Grad I; schließe den Schritt.

### G515-S045 · f66r · SOURCE_SECTION_T

Makro: `A:CHD;X:Y;C:- || A:K;X:^Y;C:REL:L>REL:AR || A:^K;X:^Y;C:CONTINUE || A:OK;X:^Y;C:GRADE:I>CLOSE`

Bearbeite den laufenden Eintrag. Ordne den laufenden Eintrag [wie zuvor] zu; über die Eintragsverbindung und von der Ausgangszeile. Im laufenden Satz ordne den laufenden Eintrag [wie zuvor] zu; führe fort. Trage den laufenden Eintrag [wie zuvor] ein; auf Grad I; schließe den Schritt.

### G515-S046 · f66r · SOURCE_SECTION_T

Makro: `A:-;X:-;C:CONTINUE || A:CH+K;X:Y;C:GRADE:II || A:R;X:^Y;C:STAGE:II>STAGE || A:CH+K;X:Y;C:- || A:^K;X:OR;C:ADDR:A>LOCAL:X || A:K;X:^OR;C:ADDR:A>REL:AR || A:^K;X:Y;C:- || A:^K;X:AIIN;C:-`

Führe fort. Entnimm den laufenden Eintrag und ordne den laufenden Eintrag zu; auf Grad II. Kennzeichne den laufenden Eintrag [wie zuvor]; auf der zweiten Stufe und auf der bezeichneten Stufe. Entnimm den laufenden Eintrag und ordne den laufenden Eintrag zu. Im laufenden Satz ordne die Eintragseinheit zu; an der bezeichneten Stelle und mit dem lokalen X-Zeichen-/Namenskern. Ordne die Eintragseinheit [wie zuvor] zu; von der Ausgangszeile; an der bezeichneten Stelle. Im laufenden Satz ordne den laufenden Eintrag zu. Im laufenden Satz ordne den Kennwert zu.

### G515-S047 · f66r · SOURCE_SECTION_T

Makro: `A:P+CH;X:-;C:EXEC>LOCAL:F || A:SH;X:OR+AIIN;C:CONTINUE>LOCAL:F>ADDR:D || A:^SH;X:^AIIN;C:THEN>REL:AR || A:^SH;X:OR;C:THEN>REL:AL || A:CHD+R;X:Y;C:LOCAL:F || A:CHD;X:Y;C:- || A:^CHD;X:^Y;C:ADDR:D>REL:AR || A:^CHD;X:^Y;C:EXEC>ADDR:D>REL:AIR || A:^CHD;X:^Y;C:EXEC>LOCAL:F>REL:AR>ADDR:AM || A:CH+K;X:Y;C:REL:AL>GRADE:III || A:SH;X:^Y;C:GRADE:I>CONTINUE || A:^SH;X:^Y;C:ADDR:D>REL:AIR>EXEC>CLOSE`

Setze ein und entnimm; zur Ausführung; an der bezeichneten Stelle. Halte die Eintragseinheit und den Kennwert fest; an der bezeichneten Stelle und an der bezeichneten Stelle; führe fort. Danach: im laufenden Satz halte den Kennwert [wie zuvor] fest; von der Ausgangszeile. Danach: im laufenden Satz halte die Eintragseinheit fest; zur Zielspalte. Bearbeite den laufenden Eintrag und kennzeichne den laufenden Eintrag; an der bezeichneten Stelle. Bearbeite den laufenden Eintrag. Im laufenden Satz bearbeite den laufenden Eintrag [wie zuvor]; von der Ausgangszeile; an der bezeichneten Stelle. Im laufenden Satz bearbeite den laufenden Eintrag [wie zuvor]; entlang der Lesebahn; zur Ausführung; an der bezeichneten Stelle. Im laufenden Satz bearbeite den laufenden Eintrag [wie zuvor]; von der Ausgangszeile; zur Ausführung; an der bezeichneten Stelle und an der bezeichneten Stelle. Entnimm den laufenden Eintrag und ordne den laufenden Eintrag zu; zur Zielspalte; auf Grad III. Halte den laufenden Eintrag [wie zuvor] fest; auf Grad I; führe fort. Im laufenden Satz halte den laufenden Eintrag [wie zuvor] fest; entlang der Lesebahn; zur Ausführung; an der bezeichneten Stelle; schließe den Schritt.

### G515-S048 · f66r · SOURCE_SECTION_T

Makro: `A:CH+K;X:Y;C:- || A:SH;X:^Y;C:GRADE:I>ADDR:D || A:K+SH;X:Y;C:GRADE:I>EXEC || A:^SH;X:^Y;C:REL:L || A:^SH;X:OR;C:REL:L || A:SH;X:OR;C:GRADE:I || A:^SH;X:^OR;C:REL:AL || A:^SH;X:OR;C:ADDR:D || A:SH;X:^OR;C:GRADE:I>CLOSE`

Entnimm den laufenden Eintrag und ordne den laufenden Eintrag zu. Halte den laufenden Eintrag [wie zuvor] fest; auf Grad I; an der bezeichneten Stelle. Ordne den laufenden Eintrag zu und halte den laufenden Eintrag fest; auf Grad I und zur Ausführung. Im laufenden Satz halte den laufenden Eintrag [wie zuvor] fest; über die Eintragsverbindung. Im laufenden Satz halte die Eintragseinheit fest; über die Eintragsverbindung. Halte die Eintragseinheit fest; auf Grad I. Im laufenden Satz halte die Eintragseinheit [wie zuvor] fest; zur Zielspalte. Im laufenden Satz halte die Eintragseinheit fest; an der bezeichneten Stelle. Halte die Eintragseinheit [wie zuvor] fest; auf Grad I; schließe den Schritt.

### G515-S049 · f66r · SOURCE_SECTION_T

Makro: `A:OK;X:-;C:REL:AR || A:SH;X:-;C:GRADE:I>CLOSE`

Trage ein; von der Ausgangszeile. Halte fest; auf Grad I; schließe den Schritt.

### G515-S050 · f66r · SOURCE_SECTION_T

Makro: `A:K+CH;X:Y;C:GRADE:I>EXEC>ADDR:D || A:CH;X:^Y;C:LOCAL:X>REL:AR || A:^CH;X:Y;C:REL:AL || A:CHD;X:^Y;C:LOCAL:F>REL:AR || A:CH+R;X:^Y;C:GRADE:I>EXEC || A:^R;X:Y;C:REL:AL || A:R;X:Y;C:- || A:SH;X:OR;C:- || A:SH+CH+K;X:^OR;C:GRADE:I>EXEC>CLOSE`

Ordne den laufenden Eintrag zu und entnimm den laufenden Eintrag; auf Grad I und zur Ausführung; an der bezeichneten Stelle. Entnimm den laufenden Eintrag [wie zuvor]; von der Ausgangszeile; mit dem lokalen X-Zeichen-/Namenskern. Im laufenden Satz entnimm den laufenden Eintrag; zur Zielspalte. Bearbeite den laufenden Eintrag [wie zuvor]; von der Ausgangszeile; an der bezeichneten Stelle. Entnimm den laufenden Eintrag [wie zuvor] und kennzeichne den laufenden Eintrag [wie zuvor]; auf Grad I und zur Ausführung. Im laufenden Satz kennzeichne den laufenden Eintrag; zur Zielspalte. Kennzeichne den laufenden Eintrag. Halte die Eintragseinheit fest. Halte die Eintragseinheit [wie zuvor] fest, entnimm die Eintragseinheit [wie zuvor] und ordne die Eintragseinheit [wie zuvor] zu; auf Grad I und zur Ausführung; schließe den Schritt.

### G515-S051 · f66r · SOURCE_SECTION_T

Makro: `A:-;X:-;C:REL:AL || A:SH;X:-;C:GRADE:I>CLOSE`

Zur Zielspalte. Halte fest; auf Grad I; schließe den Schritt.

### G515-S052 · f66r · SOURCE_SECTION_T

Makro: `A:OK;X:OR;C:- || A:^OK;X:^OR;C:REL:AL || A:SH+S;X:^OR;C:GRADE:I`

Trage die Eintragseinheit ein. Im laufenden Satz trage die Eintragseinheit [wie zuvor] ein; zur Zielspalte. Halte die Eintragseinheit [wie zuvor] fest und wähle die Eintragseinheit [wie zuvor]; auf Grad I.

### G515-S053 · f66r · SOURCE_SECTION_T

Makro: `A:P+SH;X:Y;C:GRADE:I>EXEC>ADDR:D || A:CH;X:^Y;C:LOCAL:F>CONTINUE || A:SH;X:^Y;C:EXEC>LOCAL:F>CONTINUE || A:OK;X:Y;C:GRADE:I>EXEC>ADDR:D || A:OK;X:Y;C:REL:AL || A:T;X:Y;C:REL:AR>EXEC>CLOSE`

Setze den laufenden Eintrag ein und halte den laufenden Eintrag fest; auf Grad I und zur Ausführung; an der bezeichneten Stelle. Entnimm den laufenden Eintrag [wie zuvor]; an der bezeichneten Stelle; führe fort. Halte den laufenden Eintrag [wie zuvor] fest; zur Ausführung; an der bezeichneten Stelle; führe fort. Trage den laufenden Eintrag ein; auf Grad I und zur Ausführung; an der bezeichneten Stelle. Trage den laufenden Eintrag ein; zur Zielspalte. Lege den laufenden Eintrag fest; von der Ausgangszeile; zur Ausführung; schließe den Schritt.

### G515-S054 · f66r · SOURCE_SECTION_T

Makro: `A:SH;X:-;C:GRADE:I>CLOSE`

Halte fest; auf Grad I; schließe den Schritt.

### G515-S055 · f66r · SOURCE_SECTION_T

Makro: `A:SH;X:-;C:GRADE:I>CLOSE`

Halte fest; auf Grad I; schließe den Schritt.

### G515-S056 · f66r · SOURCE_SECTION_T

Makro: `A:-;X:-;C:ADDR:D>REL:AIR || A:S;X:-;C:REL:AIR || A:^S;X:-;C:CONTINUE || A:^S;X:AIIN;C:- || A:^S;X:AIIN;C:- || A:^S;X:^AIIN;C:REL:AL || A:^S;X:^AIIN;C:ADDR:D>CONTINUE || A:CH;X:Y;C:GRADE:I>EXEC || A:^CH;X:^Y;C:ADDR:D>REL:AIR || A:^CH;X:Y;C:REL:AL || A:^CH;X:^Y;C:ADDR:D>REL:AIR>REL:AL || A:SH;X:Y;C:ADDR:D>CONTINUE>REL:AR || A:^SH;X:OR;C:ADDR:D || A:T+SH;X:^OR;C:EXEC>GRADE:I>EXEC || A:OK;X:Y;C:REL:AL || A:OK;X:Y;C:- || A:^OK;X:^Y;C:CONTINUE || A:K+CH+K;X:Y;C:GRADE:II || A:OK;X:Y;C:- || A:R;X:Y;C:STAGE:II || A:OK+S;X:^Y;C:GRADE:II || A:^S;X:Y;C:CONTINUE`

Entlang der Lesebahn; an der bezeichneten Stelle. Wähle; entlang der Lesebahn. Im laufenden Satz wähle; führe fort. Im laufenden Satz wähle den Kennwert. Im laufenden Satz wähle den Kennwert. Im laufenden Satz wähle den Kennwert [wie zuvor]; zur Zielspalte. Im laufenden Satz wähle den Kennwert [wie zuvor]; an der bezeichneten Stelle; führe fort. Entnimm den laufenden Eintrag; auf Grad I und zur Ausführung. Im laufenden Satz entnimm den laufenden Eintrag [wie zuvor]; entlang der Lesebahn; an der bezeichneten Stelle. Im laufenden Satz entnimm den laufenden Eintrag; zur Zielspalte. Im laufenden Satz entnimm den laufenden Eintrag [wie zuvor]; entlang der Lesebahn und zur Zielspalte; an der bezeichneten Stelle. Halte den laufenden Eintrag fest; von der Ausgangszeile; an der bezeichneten Stelle; führe fort. Im laufenden Satz halte die Eintragseinheit fest; an der bezeichneten Stelle. Lege die Eintragseinheit [wie zuvor] fest und halte die Eintragseinheit [wie zuvor] fest; zur Ausführung [außen], auf Grad I und zur Ausführung [innen]. Trage den laufenden Eintrag ein; zur Zielspalte. Trage den laufenden Eintrag ein. Im laufenden Satz trage den laufenden Eintrag [wie zuvor] ein; führe fort. Ordne den laufenden Eintrag zu, entnimm den laufenden Eintrag und ordne den laufenden Eintrag zu; auf Grad II. Trage den laufenden Eintrag ein. Kennzeichne den laufenden Eintrag; auf der zweiten Stufe. Trage den laufenden Eintrag [wie zuvor] ein und wähle den laufenden Eintrag [wie zuvor]; auf Grad II. Im laufenden Satz wähle den laufenden Eintrag; führe fort.

### G515-S057 · f66r · SOURCE_SECTION_T

Makro: `A:T;X:Y;C:EXEC>ADDR:D>GRADE:III || A:K;X:Y;C:GRADE:I>EXEC>ADDR:D || A:CHD;X:Y;C:- || A:K;X:Y;C:GRADE:I>EXEC>ADDR:D || A:SH;X:^Y;C:GRADE:I>CLOSE`

Lege den laufenden Eintrag fest; zur Ausführung und auf Grad III; an der bezeichneten Stelle. Ordne den laufenden Eintrag zu; auf Grad I und zur Ausführung; an der bezeichneten Stelle. Bearbeite den laufenden Eintrag. Ordne den laufenden Eintrag zu; auf Grad I und zur Ausführung; an der bezeichneten Stelle. Halte den laufenden Eintrag [wie zuvor] fest; auf Grad I; schließe den Schritt.

### G515-S058 · f66r · SOURCE_SECTION_T

Makro: `A:SH+K;X:Y;C:GRADE:I>GRADE:II>LOCAL:F || A:CHD;X:Y;C:- || A:SH;X:^Y;C:GRADE:I>CONTINUE || A:SH;X:^Y;C:CONTINUE || A:K;X:^Y;C:GRADE:I>CLOSE`

Halte den laufenden Eintrag fest und ordne den laufenden Eintrag zu; auf Grad I und auf Grad II; an der bezeichneten Stelle. Bearbeite den laufenden Eintrag. Halte den laufenden Eintrag [wie zuvor] fest; auf Grad I; führe fort. Halte den laufenden Eintrag [wie zuvor] fest; führe fort. Ordne den laufenden Eintrag [wie zuvor] zu; auf Grad I; schließe den Schritt.

### G515-S059 · f66r · SOURCE_SECTION_T

Makro: `A:-;X:Y;C:REL:AL || A:S+R;X:^Y;C:STAGE || A:CH;X:^Y;C:GRADE:I>EXEC>REL:L || A:K;X:^Y;C:REL:AL || A:SH;X:Y;C:GRADE:I>EXEC>ADDR:D || A:CH+CH+T;X:^Y;C:GRADE:I>CLOSE`

Bezug: den laufenden Eintrag; zur Zielspalte. Wähle den laufenden Eintrag [wie zuvor] und kennzeichne den laufenden Eintrag [wie zuvor]; auf der bezeichneten Stufe. Entnimm den laufenden Eintrag [wie zuvor]; über die Eintragsverbindung; auf Grad I und zur Ausführung. Ordne den laufenden Eintrag [wie zuvor] zu; zur Zielspalte. Halte den laufenden Eintrag fest; auf Grad I und zur Ausführung; an der bezeichneten Stelle. Entnimm den laufenden Eintrag [wie zuvor], entnimm den laufenden Eintrag [wie zuvor] und lege den laufenden Eintrag [wie zuvor] fest; auf Grad I; schließe den Schritt.

### G515-S060 · f66r · SOURCE_SECTION_T

Makro: `A:-;X:-;C:REL:AL || A:SH;X:-;C:CONTINUE || A:OK;X:Y;C:GRADE:I>EXEC>ADDR:D || A:CH;X:Y;C:EXEC>ADDR:D || A:K+CH;X:Y;C:GRADE:I>EXEC>ADDR:D || A:S+SH;X:^Y;C:GRADE:I>CLOSE`

Zur Zielspalte. Halte fest; führe fort. Trage den laufenden Eintrag ein; auf Grad I und zur Ausführung; an der bezeichneten Stelle. Entnimm den laufenden Eintrag; zur Ausführung; an der bezeichneten Stelle. Ordne den laufenden Eintrag zu und entnimm den laufenden Eintrag; auf Grad I und zur Ausführung; an der bezeichneten Stelle. Wähle den laufenden Eintrag [wie zuvor] und halte den laufenden Eintrag [wie zuvor] fest; auf Grad I; schließe den Schritt.

### G515-S061 · f66r · SOURCE_SECTION_T

Makro: `A:-;X:-;C:THEN>GRADE:II>CLOSE`

Danach: auf Grad II; schließe den Schritt.

### G515-S062 · f66r · SOURCE_SECTION_T

Makro: `A:K;X:Y;C:GRADE:II>EXEC>CLOSE`

Ordne den laufenden Eintrag zu; auf Grad II und zur Ausführung; schließe den Schritt.

### G515-S063 · f66r · SOURCE_SECTION_T

Makro: `A:SH+CH+T;X:Y;C:GRADE:I>EXEC || A:^T;X:^Y;C:CONTINUE || A:^T;X:^Y;C:REL:L>ADDR:D || A:SH;X:^Y;C:REL:L>GRADE:I>CLOSE`

Halte den laufenden Eintrag fest, entnimm den laufenden Eintrag und lege den laufenden Eintrag fest; auf Grad I und zur Ausführung. Im laufenden Satz lege den laufenden Eintrag [wie zuvor] fest; führe fort. Im laufenden Satz lege den laufenden Eintrag [wie zuvor] fest; über die Eintragsverbindung; an der bezeichneten Stelle. Halte den laufenden Eintrag [wie zuvor] fest; über die Eintragsverbindung; auf Grad I; schließe den Schritt.

### G515-S064 · f66r · SOURCE_SECTION_T

Makro: `A:OK;X:Y;C:GRADE:II || A:CH+K;X:Y;C:GRADE:I || A:^K;X:Y;C:- || A:SH;X:Y;C:GRADE:II>EXEC>ADDR:D || A:^SH;X:^Y;C:THEN>GRADE:II>EXEC>ADDR:D || A:^SH;X:^Y;C:THEN>CONTINUE || A:OK;X:Y;C:- || A:CH+CH+K;X:^Y;C:GRADE:I>CLOSE`

Trage den laufenden Eintrag ein; auf Grad II. Entnimm den laufenden Eintrag und ordne den laufenden Eintrag zu; auf Grad I. Im laufenden Satz ordne den laufenden Eintrag zu. Halte den laufenden Eintrag fest; auf Grad II und zur Ausführung; an der bezeichneten Stelle. Danach: im laufenden Satz halte den laufenden Eintrag [wie zuvor] fest; auf Grad II und zur Ausführung; an der bezeichneten Stelle. Danach: im laufenden Satz halte den laufenden Eintrag [wie zuvor] fest; führe fort. Trage den laufenden Eintrag ein. Entnimm den laufenden Eintrag [wie zuvor], entnimm den laufenden Eintrag [wie zuvor] und ordne den laufenden Eintrag [wie zuvor] zu; auf Grad I; schließe den Schritt.

### G515-S065 · f66r · SOURCE_SECTION_T

Makro: `A:SH;X:Y;C:GRADE:I || A:CH;X:^Y;C:ADDR:D>GRADE:I>EXEC>REL:L || A:CH+K;X:Y;C:GRADE:I || A:CH;X:^Y;C:GRADE:I>EXEC || A:^CH;X:OR;C:ADDR:D || A:^CH;X:Y+AIIN;C:ADDR:D || A:SH;X:^AIIN;C:GRADE:I>CLOSE`

Halte den laufenden Eintrag fest; auf Grad I. Entnimm den laufenden Eintrag [wie zuvor]; über die Eintragsverbindung; auf Grad I und zur Ausführung; an der bezeichneten Stelle. Entnimm den laufenden Eintrag und ordne den laufenden Eintrag zu; auf Grad I. Entnimm den laufenden Eintrag [wie zuvor]; auf Grad I und zur Ausführung. Im laufenden Satz entnimm die Eintragseinheit; an der bezeichneten Stelle. Im laufenden Satz entnimm den laufenden Eintrag und den Kennwert; an der bezeichneten Stelle. Halte den Kennwert [wie zuvor] fest; auf Grad I; schließe den Schritt.

### G515-S066 · f66r · SOURCE_SECTION_T

Makro: `A:CHD;X:-;C:THEN>CLOSE`

Danach: bearbeite; schließe den Schritt.

### G515-S067 · f66r · SOURCE_SECTION_T

Makro: `A:CH;X:Y;C:THEN>GRADE:I>EXEC>GRADE:I || A:T+CHD;X:^Y;C:CONTINUE>CLOSE`

Danach: entnimm den laufenden Eintrag; auf Grad I [außen], zur Ausführung und auf Grad I [innen]. Lege den laufenden Eintrag [wie zuvor] fest und bearbeite den laufenden Eintrag [wie zuvor]; führe fort; schließe den Schritt.

### G515-S068 · f66r · SOURCE_SECTION_T

Makro: `A:SH;X:Y;C:REL:L>GRADE:I>EXEC>ADDR:D || A:OK;X:Y;C:- || A:^OK;X:AIIN;C:- || A:^OK;X:^AIIN;C:THEN>ADDR:AM || A:T+CH;X:^AIIN;C:GRADE:I>EXEC || A:SH;X:OR;C:GRADE:I || A:^SH;X:Y;C:THEN>GRADE:I>EXEC || A:P+CH+S;X:^Y;C:REL:L>GRADE:II || A:^S;X:^Y;C:CONTINUE || A:^S;X:^Y;C:REL:AR || A:K;X:Y;C:REL:AL>GRADE:I || A:^K;X:Y;C:THEN>GRADE:I || A:T+SH;X:Y;C:REL:L>CONTINUE || A:SH+CH+T;X:Y;C:GRADE:I || A:R;X:^Y;C:- || A:^R;X:^Y;C:CONTINUE || A:^R;X:AIIN;C:- || A:SH;X:^AIIN;C:GRADE:I>CONTINUE || A:CH+T;X:Y;C:BEGIN>EXEC>GRADE:I || A:OK;X:^Y;C:GRADE:I>CLOSE`

Halte den laufenden Eintrag fest; über die Eintragsverbindung; auf Grad I und zur Ausführung; an der bezeichneten Stelle. Trage den laufenden Eintrag ein. Im laufenden Satz trage den Kennwert ein. Danach: im laufenden Satz trage den Kennwert [wie zuvor] ein; an der bezeichneten Stelle. Lege den Kennwert [wie zuvor] fest und entnimm den Kennwert [wie zuvor]; auf Grad I und zur Ausführung. Halte die Eintragseinheit fest; auf Grad I. Danach: im laufenden Satz halte den laufenden Eintrag fest; auf Grad I und zur Ausführung. Setze den laufenden Eintrag [wie zuvor] ein, entnimm den laufenden Eintrag [wie zuvor] und wähle den laufenden Eintrag [wie zuvor]; über die Eintragsverbindung; auf Grad II. Im laufenden Satz wähle den laufenden Eintrag [wie zuvor]; führe fort. Im laufenden Satz wähle den laufenden Eintrag [wie zuvor]; von der Ausgangszeile. Ordne den laufenden Eintrag zu; zur Zielspalte; auf Grad I. Danach: im laufenden Satz ordne den laufenden Eintrag zu; auf Grad I. Lege den laufenden Eintrag fest und halte den laufenden Eintrag fest; über die Eintragsverbindung; führe fort. Halte den laufenden Eintrag fest, entnimm den laufenden Eintrag und lege den laufenden Eintrag fest; auf Grad I. Kennzeichne den laufenden Eintrag [wie zuvor]. Im laufenden Satz kennzeichne den laufenden Eintrag [wie zuvor]; führe fort. Im laufenden Satz kennzeichne den Kennwert. Halte den Kennwert [wie zuvor] fest; auf Grad I; führe fort. Entnimm den laufenden Eintrag und lege den laufenden Eintrag fest; mit Beginnmarker, zur Ausführung und auf Grad I. Trage den laufenden Eintrag [wie zuvor] ein; auf Grad I; schließe den Schritt.

### G515-S069 · f66r · SOURCE_SECTION_T

Makro: `A:-;X:Y;C:REL:L || A:OK;X:Y;C:REL:AL || A:SH+CH+T;X:Y;C:- || A:^T;X:^Y;C:THEN>REL:AL || A:CHD;X:^Y;C:THEN>CLOSE`

Bezug: den laufenden Eintrag; über die Eintragsverbindung. Trage den laufenden Eintrag ein; zur Zielspalte. Halte den laufenden Eintrag fest, entnimm den laufenden Eintrag und lege den laufenden Eintrag fest. Danach: im laufenden Satz lege den laufenden Eintrag [wie zuvor] fest; zur Zielspalte. Danach: bearbeite den laufenden Eintrag [wie zuvor]; schließe den Schritt.

### G515-S070 · f66r · SOURCE_SECTION_T

Makro: `A:OK;X:Y;C:GRADE:I || A:^OK;X:^Y;C:REL:AR || A:K;X:^Y;C:CONTINUE>GRADE:I>CONTINUE || A:OK;X:^Y;C:REL:AL || A:CH+K;X:Y;C:GRADE:I>EXEC || A:K+CHD;X:Y+Y;C:- || A:CH;X:Y;C:EXEC>ADDR:D || A:SH;X:Y;C:GRADE:I>EXEC>ADDR:D || A:OK;X:Y;C:- || A:^OK;X:^Y;C:REL:L>CLOSE`

Trage den laufenden Eintrag ein; auf Grad I. Im laufenden Satz trage den laufenden Eintrag [wie zuvor] ein; von der Ausgangszeile. Ordne den laufenden Eintrag [wie zuvor] zu; auf Grad I; führe 2-mal fort. Trage den laufenden Eintrag [wie zuvor] ein; zur Zielspalte. Entnimm den laufenden Eintrag und ordne den laufenden Eintrag zu; auf Grad I und zur Ausführung. Ordne den laufenden Eintrag [außen] und den laufenden Eintrag [innen] zu und bearbeite den laufenden Eintrag [außen] und den laufenden Eintrag [innen]. Entnimm den laufenden Eintrag; zur Ausführung; an der bezeichneten Stelle. Halte den laufenden Eintrag fest; auf Grad I und zur Ausführung; an der bezeichneten Stelle. Trage den laufenden Eintrag ein. Im laufenden Satz trage den laufenden Eintrag [wie zuvor] ein; über die Eintragsverbindung; schließe den Schritt.

### G515-S071 · f66r · SOURCE_SECTION_T

Makro: `A:-;X:OR;C:ADDR:D || A:-;X:AIIN;C:- || A:SH;X:^AIIN;C:GRADE:II>CONTINUE || A:SH;X:^AIIN;C:REL:L>GRADE:I>CLOSE`

Bezug: die Eintragseinheit; an der bezeichneten Stelle. Bezug: den Kennwert. Halte den Kennwert [wie zuvor] fest; auf Grad II; führe fort. Halte den Kennwert [wie zuvor] fest; über die Eintragsverbindung; auf Grad I; schließe den Schritt.

### G515-S072 · f66r · SOURCE_SECTION_T

Makro: `A:CHD;X:-;C:REL:L>CLOSE`

Bearbeite; über die Eintragsverbindung; schließe den Schritt.

### G515-S073 · f66r · SOURCE_SECTION_T

Makro: `A:CH;X:Y;C:GRADE:II>ADDR:D || A:SH+K;X:^Y;C:GRADE:I>CONTINUE || A:^K;X:^Y;C:REL:AL>CONTINUE || A:^K;X:AIIN;C:REL:L>EXEC>ADDR:D || A:SH;X:^AIIN;C:GRADE:I>CONTINUE || A:^SH;X:Y;C:THEN>GRADE:II || A:^SH;X:AIIN;C:REL:L || A:OK+CHD;X:Y;C:REL:AL || A:P+CHD;X:^Y;C:CLOSE`

Entnimm den laufenden Eintrag; auf Grad II; an der bezeichneten Stelle. Halte den laufenden Eintrag [wie zuvor] fest und ordne den laufenden Eintrag [wie zuvor] zu; auf Grad I; führe fort. Im laufenden Satz ordne den laufenden Eintrag [wie zuvor] zu; zur Zielspalte; führe fort. Im laufenden Satz ordne den Kennwert zu; über die Eintragsverbindung; zur Ausführung; an der bezeichneten Stelle. Halte den Kennwert [wie zuvor] fest; auf Grad I; führe fort. Danach: im laufenden Satz halte den laufenden Eintrag fest; auf Grad II. Im laufenden Satz halte den Kennwert fest; über die Eintragsverbindung. Trage den laufenden Eintrag ein und bearbeite den laufenden Eintrag; zur Zielspalte. Setze den laufenden Eintrag [wie zuvor] ein und bearbeite den laufenden Eintrag [wie zuvor]; schließe den Schritt.

### G515-S074 · f66r · SOURCE_SECTION_T

Makro: `A:K;X:-;C:EXEC>CLOSE`

Ordne zu; zur Ausführung; schließe den Schritt.

### G515-S075 · f66r · SOURCE_SECTION_T

Makro: `A:CHD;X:-;C:THEN>CLOSE`

Danach: bearbeite; schließe den Schritt.

### G515-S076 · f66r · SOURCE_SECTION_T

Makro: `A:CH+P;X:-;C:GRADE:I>CLOSE`

Entnimm und setze ein; auf Grad I; schließe den Schritt.

### G515-S077 · f66r · SOURCE_SECTION_T

Makro: `A:-;X:AIIN;C:- || A:SH;X:Y;C:GRADE:I || A:^SH;X:Y;C:THEN>GRADE:I>CONTINUE || A:R;X:AIIN;C:- || A:SH;X:^AIIN;C:GRADE:II>CLOSE`

Bezug: den Kennwert. Halte den laufenden Eintrag fest; auf Grad I. Danach: im laufenden Satz halte den laufenden Eintrag fest; auf Grad I; führe fort. Kennzeichne den Kennwert. Halte den Kennwert [wie zuvor] fest; auf Grad II; schließe den Schritt.

### G515-S078 · f66r · SOURCE_SECTION_T

Makro: `A:SH+CH+T;X:Y;C:- || A:K;X:^Y;C:REL:L>GRADE:I>CONTINUE || A:OK;X:^Y;C:CONTINUE || A:K;X:^Y;C:ADDR:D>REL:AR || A:^K;X:Y;C:REL:L || A:K;X:Y;C:REL:L>GRADE:II>ADDR:D || A:T;X:Y;C:- || A:SH+K;X:Y;C:GRADE:I>REL:AL || A:SH+CH+K;X:^Y;C:REL:AR`

Halte den laufenden Eintrag fest, entnimm den laufenden Eintrag und lege den laufenden Eintrag fest. Ordne den laufenden Eintrag [wie zuvor] zu; über die Eintragsverbindung; auf Grad I; führe fort. Trage den laufenden Eintrag [wie zuvor] ein; führe fort. Ordne den laufenden Eintrag [wie zuvor] zu; von der Ausgangszeile; an der bezeichneten Stelle. Im laufenden Satz ordne den laufenden Eintrag zu; über die Eintragsverbindung. Ordne den laufenden Eintrag zu; über die Eintragsverbindung; auf Grad II; an der bezeichneten Stelle. Lege den laufenden Eintrag fest. Halte den laufenden Eintrag fest und ordne den laufenden Eintrag zu; zur Zielspalte; auf Grad I. Halte den laufenden Eintrag [wie zuvor] fest, entnimm den laufenden Eintrag [wie zuvor] und ordne den laufenden Eintrag [wie zuvor] zu; von der Ausgangszeile.

## Reichweitengrenze

Jede Folge bleibt innerhalb ihrer ursprünglichen Aussage. Registerwörter dürfen verschieden sein, solange dieselbe portable Wurzelspur erhalten bleibt. Null exakte Kontextwidersprüche gilt nur für die wiederholten Zustände dieser vier Seiten.
