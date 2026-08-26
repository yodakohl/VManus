# GDT480 — Mikroeintrags-Templateatlas

Jeder der 135 GDT479-Mikroeinträge besitzt nun zwei explizite Baupläne: ein enges bedeutungsgleiches Template und eine gröbere Rollenform. Auch Einzelstücke behalten einen Default; Wiederholung erhöht nur die Vertrautheit.

| Ebene | Templates | wiederkehrend | abgedeckte Einträge | seitenübergreifend | registerübergreifend |
|---|---:|---:|---:|---:|---:|
| Enges Bedeutungstemplate | 120 | 13 | 28 | 5 | 3 |
| Rollenform | 105 | 21 | 51 | 13 | 8 |

Acht enge Wiederholungsfamilien verbinden 18 Einträge mit verschiedenen sichtbaren Oberflächen; fünf weitere sind echte Oberflächenwiederholungen. Dreizehn Rollenformen verbinden 33 Einträge über mehr als ein enges Bedeutungstemplate hinweg.

## Wiederkehrende enge Templates

### G480-T005 — 4 Einträge, CROSS_REGISTER

- Komponenten: `CATALOGUE[DANACH · {N1} @START_FRESH_SIBLING:FORWARD_OPEN]`
- Leseschablone: Namenseintrag »{N1}« — Folgevermerk. Reihenfolge konkret: OT — danach Namenseintrag »{N1}«.
- Rezepte: `CATALOGUE[OT @START_FRESH_SIBLING:FORWARD_OPEN]`
- Seiten/Register: f71v|f77r|f88v / CELESTIAL|BIOLOGICAL|PHARMA
- Einträge: G475-R005|G475-R087|G475-R100|G475-R105

### G480-T003 — 2 Einträge, CROSS_PAGE

- Komponenten: `CATALOGUE[{N1} · ZIELORT · POSTEN @NONE]`
- Leseschablone: Namenseintrag »{N1}« — Zielzuordnung, Postenangabe.
- Rezepte: `CATALOGUE[AL+Y @NONE]`
- Seiten/Register: f71v|f72r / CELESTIAL
- Einträge: G475-R003|G475-R059

### G480-T012 — 2 Einträge, CROSS_PAGE

- Komponenten: `CATALOGUE[AUSFÜHRUNG · HIER · {N1} @NONE]`
- Leseschablone: Namenseintrag »{N1}« — Ausführungsvermerk, Hier-Vermerk.
- Rezepte: `CATALOGUE[O+LOCAL_CHAR_F @NONE]`
- Seiten/Register: f71v|f72r / CELESTIAL
- Einträge: G475-R012|G475-R032

### G480-T023 — 2 Einträge, SAME_PAGE_RECURRENT

- Komponenten: `COORDINATE[DANACH · AUSGANG · ZIELORT · POSTEN @START_FRESH_SIBLING:FORWARD_OPEN]`
- Leseschablone: Adressspur: danach → Ausgang → Zielort → Posten. Reihenfolge konkret: OT — danach Ausgang.
- Rezepte: `COORDINATE[OT+AR+AL+Y @START_FRESH_SIBLING:FORWARD_OPEN]`
- Seiten/Register: f72r / CELESTIAL
- Einträge: G475-R023|G475-R037

### G480-T030 — 2 Einträge, SAME_PAGE_RECURRENT

- Komponenten: `INSTRUCTION[SETZEN · GRAD II · POSTEN @NONE / AUSGANG · POSTEN @NONE]`
- Leseschablone: 1. Setze den Posten, auf Grad II. 2. Im selben Gang setze den Posten vom Ausgang.
- Rezepte: `INSTRUCTION[OK+EE+Y @NONE / AR+Y @NONE]`
- Seiten/Register: f72r / CELESTIAL
- Einträge: G475-R030|G475-R042

### G480-T036 — 2 Einträge, SAME_PAGE_RECURRENT

- Komponenten: `INSTRUCTION[SETZEN · ZIELORT · AUSGANG @NONE]`
- Leseschablone: Setze den Eintrag zum Zielort und vom Ausgang.
- Rezepte: `INSTRUCTION[OK+AL+AR @NONE]`
- Seiten/Register: f72r / CELESTIAL
- Einträge: G475-R038|G475-R077

### G480-T037 — 2 Einträge, SAME_PAGE_RECURRENT

- Komponenten: `INSTRUCTION[SETZEN · ZIELORT @NONE]`
- Leseschablone: Setze den Eintrag zum Zielort.
- Rezepte: `INSTRUCTION[OK+AL @NONE]`
- Seiten/Register: f72r / CELESTIAL
- Einträge: G475-R039|G475-R041

### G480-T038 — 2 Einträge, SAME_PAGE_RECURRENT

- Komponenten: `INSTRUCTION[SETZEN · ZIELORT · POSTEN @NONE]`
- Leseschablone: Setze den Posten zum Zielort.
- Rezepte: `INSTRUCTION[OK+AL+Y @NONE]`
- Seiten/Register: f72r / CELESTIAL
- Einträge: G475-R040|G475-R048

### G480-T048 — 2 Einträge, SAME_PAGE_RECURRENT

- Komponenten: `CATALOGUE[{N1} · ZIELORT · ZIELORT @NONE]`
- Leseschablone: Namenseintrag »{N1}« — Zielzuordnung, Zielzuordnung.
- Rezepte: `CATALOGUE[AL+AL @NONE]`
- Seiten/Register: f72r / CELESTIAL
- Einträge: G475-R053|G475-R079

### G480-T050 — 2 Einträge, CROSS_REGISTER

- Komponenten: `COORDINATE[DANACH · ZIELORT · POSTEN @START_FRESH_SIBLING:FORWARD_OPEN]`
- Leseschablone: Adressspur: danach → Zielort → Posten. Reihenfolge konkret: OT — danach Zielort.
- Rezepte: `COORDINATE[OT+AL+Y @START_FRESH_SIBLING:FORWARD_OPEN]`
- Seiten/Register: f72r|f89r / CELESTIAL|PHARMA
- Einträge: G475-R055|G475-R133

### G480-T061 — 2 Einträge, SAME_PAGE_RECURRENT

- Komponenten: `CATALOGUE[{N1} · WERT @NONE]`
- Leseschablone: Namenseintrag »{N1}« — Wertangabe.
- Rezepte: `CATALOGUE[AIIN @NONE]`
- Seiten/Register: f72r / CELESTIAL
- Einträge: G475-R067|G475-R072

### G480-T071 — 2 Einträge, CROSS_REGISTER

- Komponenten: `CATALOGUE[{N1} · AUSGANG · {N2} @NONE]`
- Leseschablone: Namenseintrag »{N1}« / Namenseintrag »{N2}« — Ausgangszuordnung.
- Rezepte: `CATALOGUE[AR @NONE]`
- Seiten/Register: f72r|f89r / CELESTIAL|PHARMA
- Einträge: G475-R080|G475-R134

### G480-T116 — 2 Einträge, SAME_PAGE_RECURRENT

- Komponenten: `CATALOGUE[{N1} · ANTEIL @NONE]`
- Leseschablone: Namenseintrag »{N1}« — Anteilsangabe.
- Rezepte: `CATALOGUE[AIN @NONE]`
- Seiten/Register: f89r / PHARMA
- Einträge: G475-R128|G475-R131

## Alle Rollenformen

- **G480-S054** · 5 Einträge · CROSS_REGISTER · `CATALOGUE[NAME · ARG @NONE]` · strenge Templates 3
- **G480-S005** · 4 Einträge · CROSS_REGISTER · `CATALOGUE[ORDER · NAME @START_FRESH_SIBLING:FORWARD_OPEN]` · strenge Templates 1
- **G480-S008** · 3 Einträge · CROSS_PAGE · `INSTRUCTION[ACTION · REL · ARG @NONE]` · strenge Templates 2
- **G480-S014** · 3 Einträge · CROSS_REGISTER · `COORDINATE[ORDER · REL · ARG @START_FRESH_SIBLING:FORWARD_OPEN]` · strenge Templates 2
- **G480-S020** · 3 Einträge · SAME_PAGE_RECURRENT · `INSTRUCTION[ACTION · REL · MOD @NONE]` · strenge Templates 3
- **G480-S044** · 3 Einträge · SAME_PAGE_RECURRENT · `CATALOGUE[NAME · REL · REL @NONE]` · strenge Templates 2
- **G480-S002** · 2 Einträge · CROSS_PAGE · `CATALOGUE[REL @NONE / REL · NAME @NONE]` · strenge Templates 2
- **G480-S003** · 2 Einträge · CROSS_PAGE · `CATALOGUE[NAME · REL · ARG @NONE]` · strenge Templates 1
- **G480-S012** · 2 Einträge · CROSS_PAGE · `CATALOGUE[MOD · MOD · NAME @NONE]` · strenge Templates 1
- **G480-S021** · 2 Einträge · SAME_PAGE_RECURRENT · `INSTRUCTION[NAME · REL · ACTION · NAME @NONE]` · strenge Templates 2
- **G480-S022** · 2 Einträge · SAME_PAGE_RECURRENT · `COORDINATE[ORDER · REL · REL · ARG @START_FRESH_SIBLING:FORWARD_OPEN]` · strenge Templates 1
- **G480-S027** · 2 Einträge · CROSS_REGISTER · `CATALOGUE[ORDER · NAME · ARG @START_FRESH_SIBLING:FORWARD_OPEN]` · strenge Templates 2
- **G480-S029** · 2 Einträge · SAME_PAGE_RECURRENT · `INSTRUCTION[ACTION · MOD · ARG @NONE / REL · ARG @NONE]` · strenge Templates 1
- **G480-S032** · 2 Einträge · CROSS_REGISTER · `INSTRUCTION[ACTION · REL · NAME @NONE]` · strenge Templates 2
- **G480-S034** · 2 Einträge · SAME_PAGE_RECURRENT · `INSTRUCTION[ACTION · REL · REL @NONE]` · strenge Templates 1
- **G480-S035** · 2 Einträge · SAME_PAGE_RECURRENT · `INSTRUCTION[ACTION · REL @NONE]` · strenge Templates 1
- **G480-S040** · 2 Einträge · SAME_PAGE_RECURRENT · `COORDINATE[ORDER · REL @START_FRESH_SIBLING:FORWARD_OPEN]` · strenge Templates 2
- **G480-S045** · 2 Einträge · CROSS_REGISTER · `INSTRUCTION[ACTION · MOD @NONE]` · strenge Templates 2
- **G480-S046** · 2 Einträge · CROSS_REGISTER · `CATALOGUE[NAME · REL @NONE]` · strenge Templates 2
- **G480-S063** · 2 Einträge · CROSS_REGISTER · `CATALOGUE[NAME · REL · NAME @NONE]` · strenge Templates 1
- **G480-S079** · 2 Einträge · CROSS_PAGE · `INSTRUCTION[ACTION · ARG @NONE]` · strenge Templates 2
- **G480-S001** · 1 Einträge · SINGLETON · `CATALOGUE[ORDER · NAME @START_FRESH_SIBLING:FORWARD_OPEN / NAME @NONE]` · strenge Templates 1
- **G480-S004** · 1 Einträge · SINGLETON · `INSTRUCTION[ACTION · ORDER · REL @KEEP_ACTIVE_UNIT:BRIDGE_LEFT_TO_RIGHT]` · strenge Templates 1
- **G480-S006** · 1 Einträge · SINGLETON · `INSTRUCTION[REL · ACTION · ACTION · ARG @NONE]` · strenge Templates 1
- **G480-S007** · 1 Einträge · SINGLETON · `COORDINATE[ORDER · ARG @START_FRESH_SIBLING:FORWARD_OPEN]` · strenge Templates 1
- **G480-S009** · 1 Einträge · SINGLETON · `COORDINATE[ORDER · REL @START_FRESH_SIBLING:FORWARD_OPEN / REL @NONE / REL · ARG @NONE]` · strenge Templates 1
- **G480-S010** · 1 Einträge · SINGLETON · `COORDINATE[NAME · REL · REL @NONE / MOD @NONE / ARG @NONE]` · strenge Templates 1
- **G480-S011** · 1 Einträge · SINGLETON · `CATALOGUE[NAME · REL · ARG @NONE / REL @NONE]` · strenge Templates 1
- **G480-S013** · 1 Einträge · SINGLETON · `CATALOGUE[ORDER · REL · NAME @START_FRESH_SIBLING:FORWARD_OPEN]` · strenge Templates 1
- **G480-S015** · 1 Einträge · SINGLETON · `INSTRUCTION[ORDER · REL @START_FRESH_SIBLING:FORWARD_OPEN / ACTION · REL @NONE]` · strenge Templates 1
- **G480-S016** · 1 Einträge · SINGLETON · `INSTRUCTION[ACTION · ORDER · ACTION · NAME @KEEP_ACTIVE_UNIT:BRIDGE_LEFT_TO_RIGHT]` · strenge Templates 1
- **G480-S017** · 1 Einträge · SINGLETON · `INSTRUCTION[NAME · ACTION · NAME @NONE]` · strenge Templates 1
- **G480-S018** · 1 Einträge · SINGLETON · `CATALOGUE[NAME · ARG · ARG @NONE]` · strenge Templates 1
- **G480-S019** · 1 Einträge · SINGLETON · `COORDINATE[MOD · ARG @NONE / REL @NONE / REL · ARG @NONE]` · strenge Templates 1
- **G480-S023** · 1 Einträge · SINGLETON · `COORDINATE[ORDER · ARG @START_FRESH_SIBLING:FORWARD_OPEN / ORDER · ARG @START_FRESH_SIBLING:FORWARD_OPEN]` · strenge Templates 1
- **G480-S024** · 1 Einträge · SINGLETON · `INSTRUCTION[ORDER · REL · NAME @START_FRESH_SIBLING:FORWARD_OPEN / ARG · ACTION @NONE / ARG · MOD @NONE]` · strenge Templates 1
- **G480-S025** · 1 Einträge · SINGLETON · `INSTRUCTION[MOD · ORDER @KEEP_ACTIVE_UNIT:BACKWARD_HOLD / ACTION · REL · MOD @NONE]` · strenge Templates 1
- **G480-S026** · 1 Einträge · SINGLETON · `COORDINATE[MOD · MOD · REL · REL · REL @NONE]` · strenge Templates 1
- **G480-S028** · 1 Einträge · SINGLETON · `CATALOGUE[ORDER · NAME · REL @START_FRESH_SIBLING:FORWARD_OPEN]` · strenge Templates 1
- **G480-S030** · 1 Einträge · SINGLETON · `COORDINATE[ORDER · ARG · ARG @START_FRESH_SIBLING:FORWARD_OPEN]` · strenge Templates 1
- **G480-S031** · 1 Einträge · SINGLETON · `INSTRUCTION[ACTION · NAME · REL · NAME @NONE]` · strenge Templates 1
- **G480-S033** · 1 Einträge · SINGLETON · `INSTRUCTION[ACTION · NAME · REL · REL @NONE]` · strenge Templates 1
- **G480-S036** · 1 Einträge · SINGLETON · `CATALOGUE[ORDER · NAME · REL · NAME @START_FRESH_SIBLING:FORWARD_OPEN]` · strenge Templates 1
- **G480-S037** · 1 Einträge · SINGLETON · `COORDINATE[ORDER · REL @START_FRESH_SIBLING:FORWARD_OPEN / ARG @NONE]` · strenge Templates 1
- **G480-S038** · 1 Einträge · SINGLETON · `INSTRUCTION[ACTION · REL · NAME · MOD @NONE]` · strenge Templates 1
- **G480-S039** · 1 Einträge · SINGLETON · `INSTRUCTION[ACTION · NAME · REL @NONE]` · strenge Templates 1
- **G480-S041** · 1 Einträge · SINGLETON · `CATALOGUE[ARG · REL · NAME @NONE]` · strenge Templates 1
- **G480-S042** · 1 Einträge · SINGLETON · `INSTRUCTION[ACTION · NAME @NONE]` · strenge Templates 1
- **G480-S043** · 1 Einträge · SINGLETON · `COORDINATE[ORDER · ORDER · MOD @START_FRESH_SIBLING|KEEP_ACTIVE_UNIT:FORWARD_OPEN|BRIDGE_LEFT_TO_RIGHT]` · strenge Templates 1
- **G480-S047** · 1 Einträge · SINGLETON · `COORDINATE[ORDER · MOD @START_FRESH_SIBLING:FORWARD_OPEN]` · strenge Templates 1
- **G480-S048** · 1 Einträge · SINGLETON · `INSTRUCTION[ACTION · REL · NAME · MOD @NONE] || INSTRUCTION[ORDER · NAME · REL · ARG @KEEP_ACTIVE_UNIT:FORWARD_OPEN] || COORDINATE[ORDER · REL · ARG @KEEP_ACTIVE_UNIT:FORWARD_OPEN]` · strenge Templates 1
- **G480-S049** · 1 Einträge · SINGLETON · `CATALOGUE[ARG · NAME · MOD @NONE]` · strenge Templates 1
- **G480-S050** · 1 Einträge · SINGLETON · `COORDINATE[ORDER · MOD @START_FRESH_SIBLING:FORWARD_OPEN / ARG @NONE]` · strenge Templates 1
- **G480-S051** · 1 Einträge · SINGLETON · `INSTRUCTION[NAME · MOD · MOD @NONE / REL @NONE / ACTION · MOD · ACTION @NONE]` · strenge Templates 1
- **G480-S052** · 1 Einträge · SINGLETON · `CATALOGUE[NAME · ARG @NONE / REL · REL · ARG @NONE]` · strenge Templates 1
- **G480-S053** · 1 Einträge · SINGLETON · `COORDINATE[ORDER · MOD · ARG @START_FRESH_SIBLING:FORWARD_OPEN / ARG @NONE]` · strenge Templates 1
- **G480-S055** · 1 Einträge · SINGLETON · `INSTRUCTION[MOD · MOD · ACTION · ORDER · NAME @KEEP_ACTIVE_UNIT:BRIDGE_LEFT_TO_RIGHT]` · strenge Templates 1
- **G480-S056** · 1 Einträge · SINGLETON · `INSTRUCTION[NAME · MOD · ARG @NONE / ACTION · ARG @NONE] || INSTRUCTION[NAME · ORDER · REL · ORDER @KEEP_ACTIVE_UNIT|KEEP_ACTIVE_UNIT:BRIDGE_LEFT_TO_RIGHT|BACKWARD_HOLD]` · strenge Templates 1
- **G480-S057** · 1 Einträge · SINGLETON · `CATALOGUE[ARG · REL · NAME · MOD @NONE]` · strenge Templates 1
- **G480-S058** · 1 Einträge · SINGLETON · `COORDINATE[ARG · ARG @NONE]` · strenge Templates 1
- **G480-S059** · 1 Einträge · SINGLETON · `INSTRUCTION[MOD · ACTION · MOD · ARG @NONE / NAME · ARG · MOD @NONE]` · strenge Templates 1
- **G480-S060** · 1 Einträge · SINGLETON · `CATALOGUE[MOD · MOD @NONE / MOD @NONE / NAME · REL · ARG @NONE]` · strenge Templates 1
- **G480-S061** · 1 Einträge · SINGLETON · `CATALOGUE[NAME · REL · ARG @NONE / REL · REL @NONE]` · strenge Templates 1
- **G480-S062** · 1 Einträge · SINGLETON · `CATALOGUE[ARG · REL · NAME @NONE] || CATALOGUE[ORDER · ARG @KEEP_ACTIVE_UNIT:FORWARD_OPEN / ORDER · NAME @KEEP_ACTIVE_UNIT:FORWARD_OPEN] || INSTRUCTION[ORDER · NAME · ACTION · NAME · REL @KEEP_ACTIVE_UNIT:FORWARD_OPEN]` · strenge Templates 1
- **G480-S064** · 1 Einträge · SINGLETON · `CATALOGUE[ARG · NAME · REL @NONE]` · strenge Templates 1
- **G480-S065** · 1 Einträge · SINGLETON · `CATALOGUE[NAME · REL @NONE / ACTION · REL @NONE]` · strenge Templates 1
- **G480-S066** · 1 Einträge · SINGLETON · `INSTRUCTION[NAME · ACTION · ACTION · NAME @NONE]` · strenge Templates 1
- **G480-S067** · 1 Einträge · SINGLETON · `COORDINATE[REL · REL @NONE] || COORDINATE[ORDER · NAME · REL @KEEP_ACTIVE_UNIT:FORWARD_OPEN]` · strenge Templates 1
- **G480-S068** · 1 Einträge · SINGLETON · `CATALOGUE[NAME · REL · NAME · REL @NONE] || CATALOGUE[ORDER · NAME @KEEP_ACTIVE_UNIT:FORWARD_OPEN]` · strenge Templates 1
- **G480-S069** · 1 Einträge · SINGLETON · `COORDINATE[ORDER · MOD · MOD @START_FRESH_SIBLING:FORWARD_OPEN]` · strenge Templates 1
- **G480-S070** · 1 Einträge · SINGLETON · `COORDINATE[ORDER · ORDER @START_FRESH_SIBLING|KEEP_ACTIVE_UNIT:FORWARD_OPEN|BACKWARD_HOLD]` · strenge Templates 1
- **G480-S071** · 1 Einträge · SINGLETON · `CATALOGUE[NAME · ORDER · NAME @START_FRESH_SIBLING:BRIDGE_LEFT_TO_RIGHT]` · strenge Templates 1
- **G480-S072** · 1 Einträge · SINGLETON · `INSTRUCTION[ORDER · ACTION · MOD @START_FRESH_SIBLING:FORWARD_OPEN]` · strenge Templates 1
- **G480-S073** · 1 Einträge · SINGLETON · `COORDINATE[ORDER · ORDER · ARG @START_FRESH_SIBLING|KEEP_ACTIVE_UNIT:FORWARD_OPEN|BRIDGE_LEFT_TO_RIGHT / MOD @NONE]` · strenge Templates 1
- **G480-S074** · 1 Einträge · SINGLETON · `INSTRUCTION[NAME · ACTION · ACTION · ARG @NONE]` · strenge Templates 1
- **G480-S075** · 1 Einträge · SINGLETON · `CATALOGUE[ORDER · REL @START_FRESH_SIBLING:FORWARD_OPEN / REL · NAME @NONE]` · strenge Templates 1
- **G480-S076** · 1 Einträge · SINGLETON · `INSTRUCTION[ORDER · ACTION · ORDER @START_FRESH_SIBLING|KEEP_ACTIVE_UNIT:FORWARD_OPEN|BACKWARD_HOLD]` · strenge Templates 1
- **G480-S077** · 1 Einträge · SINGLETON · `CATALOGUE[ORDER · NAME · MOD @START_FRESH_SIBLING:FORWARD_OPEN]` · strenge Templates 1
- **G480-S078** · 1 Einträge · SINGLETON · `CATALOGUE[MOD · NAME @NONE]` · strenge Templates 1
- **G480-S080** · 1 Einträge · SINGLETON · `CATALOGUE[NAME · REL · NAME · REL @NONE]` · strenge Templates 1
- **G480-S081** · 1 Einträge · SINGLETON · `CATALOGUE[ORDER · NAME · MOD · REL · NAME @START_FRESH_SIBLING:FORWARD_OPEN]` · strenge Templates 1
- **G480-S082** · 1 Einträge · SINGLETON · `CATALOGUE[NAME · REL · REL · NAME @NONE]` · strenge Templates 1
- **G480-S083** · 1 Einträge · SINGLETON · `INSTRUCTION[ACTION · ACTION · ARG @NONE] || INSTRUCTION[NAME · ORDER @KEEP_ACTIVE_UNIT:BACKWARD_HOLD] || INSTRUCTION[ORDER · NAME · MOD @KEEP_ACTIVE_UNIT:FORWARD_OPEN]` · strenge Templates 1
- **G480-S084** · 1 Einträge · SINGLETON · `CATALOGUE[ORDER · ORDER · NAME @START_FRESH_SIBLING|KEEP_ACTIVE_UNIT:FORWARD_OPEN|BRIDGE_LEFT_TO_RIGHT]` · strenge Templates 1
- **G480-S085** · 1 Einträge · SINGLETON · `CATALOGUE[REL · REL · NAME · ARG @NONE]` · strenge Templates 1
- **G480-S086** · 1 Einträge · SINGLETON · `INSTRUCTION[ARG · ACTION · ARG · MOD @NONE] || INSTRUCTION[ORDER @KEEP_ACTIVE_UNIT:FORWARD_OPEN / ACTION · MOD · ACTION @NONE]` · strenge Templates 1
- **G480-S087** · 1 Einträge · SINGLETON · `INSTRUCTION[ACTION · ARG @NONE / ARG @NONE]` · strenge Templates 1
- **G480-S088** · 1 Einträge · SINGLETON · `INSTRUCTION[NAME · ACTION · MOD · ARG @NONE]` · strenge Templates 1
- **G480-S089** · 1 Einträge · SINGLETON · `CATALOGUE[NAME · REL · NAME · MOD @NONE]` · strenge Templates 1
- **G480-S090** · 1 Einträge · SINGLETON · `CATALOGUE[NAME · MOD · REL · REL · NAME @NONE]` · strenge Templates 1
- **G480-S091** · 1 Einträge · SINGLETON · `COORDINATE[ARG · MOD · ARG @NONE]` · strenge Templates 1
- **G480-S092** · 1 Einträge · SINGLETON · `CATALOGUE[NAME · ARG · ARG @NONE] || CATALOGUE[NAME · ORDER · ARG @KEEP_ACTIVE_UNIT:BRIDGE_LEFT_TO_RIGHT]` · strenge Templates 1
- **G480-S093** · 1 Einträge · SINGLETON · `CATALOGUE[NAME · MOD @NONE]` · strenge Templates 1
- **G480-S094** · 1 Einträge · SINGLETON · `INSTRUCTION[NAME · REL · NAME · ACTION · NAME · ORDER @KEEP_ACTIVE_UNIT:BACKWARD_HOLD]` · strenge Templates 1
- **G480-S095** · 1 Einträge · SINGLETON · `INSTRUCTION[MOD · ACTION · ACTION · MOD · ARG @NONE]` · strenge Templates 1
- **G480-S096** · 1 Einträge · SINGLETON · `CATALOGUE[ORDER · ORDER · NAME @START_FRESH_SIBLING|KEEP_ACTIVE_UNIT:FORWARD_OPEN|BRIDGE_LEFT_TO_RIGHT / ARG @NONE]` · strenge Templates 1
- **G480-S097** · 1 Einträge · SINGLETON · `INSTRUCTION[ACTION · ORDER @KEEP_ACTIVE_UNIT:BACKWARD_HOLD / ACTION · ORDER @KEEP_ACTIVE_UNIT:BACKWARD_HOLD / ARG @NONE]` · strenge Templates 1
- **G480-S098** · 1 Einträge · SINGLETON · `CATALOGUE[NAME · MOD · MOD @NONE]` · strenge Templates 1
- **G480-S099** · 1 Einträge · SINGLETON · `INSTRUCTION[ACTION · ARG · ARG · ARG @NONE]` · strenge Templates 1
- **G480-S100** · 1 Einträge · SINGLETON · `INSTRUCTION[ACTION · MOD · MOD · ACTION @NONE]` · strenge Templates 1
- **G480-S101** · 1 Einträge · SINGLETON · `INSTRUCTION[ARG · ACTION @NONE]` · strenge Templates 1
- **G480-S102** · 1 Einträge · SINGLETON · `INSTRUCTION[ACTION · MOD · MOD · ARG @NONE]` · strenge Templates 1
- **G480-S103** · 1 Einträge · SINGLETON · `INSTRUCTION[ACTION · ACTION · NAME @NONE]` · strenge Templates 1
- **G480-S104** · 1 Einträge · SINGLETON · `CATALOGUE[MOD · MOD · NAME · REL @NONE]` · strenge Templates 1
- **G480-S105** · 1 Einträge · SINGLETON · `COORDINATE[ORDER · ORDER · REL · ORDER @START_FRESH_SIBLING|KEEP_ACTIVE_UNIT|KEEP_ACTIVE_UNIT:FORWARD_OPEN|BRIDGE_LEFT_TO_RIGHT|BACKWARD_HOLD]` · strenge Templates 1

Die Rollenformen ersetzen keine Wurzelbedeutung. Sie zeigen nur, dass etwa ACTION·ARG und ORDER·REL dieselbe grobe Satzstelle teilen können. Für eine konkrete Lesung bleibt immer das enge Template mit seinem vollständigen Komponenten- und Reihenfolgetrace maßgeblich.
