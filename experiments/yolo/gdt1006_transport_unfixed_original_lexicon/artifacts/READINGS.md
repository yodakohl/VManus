# Vollständige bedingte Lesungen aus GDT1006

Dies sind Modellzeugen, keine bestätigten Übersetzungen. Jede hier gezeigte Lesung deckt alle 63 ZL3b-Gruppen ab. Die unklare sol/chedy-Grenze bleibt bestehen. Fracht A/B/C sind anonyme Identitäten; Tier- und Pflanzennamen werden nicht vorausgesetzt. Die Satzmuster und ihre Bedeutungen sind Annahmen. Anweisungen und Erzählung sind dadurch nicht unterschieden.

Alle 33 gefundenen kohärenten vollständigen Wörterbücher werden ohne Auswahl gezeigt. Die Projektion enthält 102 Kombinationen aus elf Wortrollen und fünf Bezugseinstellungen. Sie erschöpft nur bei BIJECTIVE die Rollenprojektion, nicht alle vollständigen Wörterbücher innerhalb einer Projektion.

[102 Kandidaten](PROJECTED_CANDIDATES.tsv) · [Alle 1.232 geprüften Karten](CANDIDATES.tsv) · [Alle 47 Wortdomänen je Familie](WORD_DOMAINS.tsv) · [Satzmuster gegen Inhalt](SYNTAX_VS_WORLD.tsv)

## FUNCTIONAL

21 kohärente vollständige Karten; 66 positive Rollen-/Bezugsvarianten. Projektionsraum vollständig: False. Stopp: CANDIDATE_CAP.

### FUNCTIONAL Karte 340

Kohärente Bezugseinstellungen: [0, 2, 8, 10]. Alle übrigen der 32 Varianten widersprechen mindestens einer registrierten Folge; ihre vollständigen Ergebnisse stehen in FAMILY_FUNCTIONAL.json.

| Form | Bedingte Terminalrolle |
|---|---|
| chckhdy | WOULD_BE |
| checthy | ALL |
| ched | WITHOUT_AGENT |
| chedain | NEXT |
| chedy | W |
| cheeety | RETURN_EXCLUDING |
| chety | UNHARMED |
| dal | BESIDES |
| lchedy | W |
| ldy | ALONE |
| lkedy | PAIRED_WITH |
| ockhey | FORBIDDEN |
| olsaly | ATTENDED_BY |
| opshedy | HOME |
| otaiin | THERE |
| otchedy | OTHER_CARGO |
| otedy | RETURN |
| otor | COLOC |
| otshdy | GOAL |
| pdalshdy | INIT |
| qetal | AT_MOST_ONE |
| qokal | TRAVEL_TOGETHER |
| qokchedy | UNATTENDED |
| qokedol | FAR_BANK |
| qokedy | G |
| qokeedy | CONVEY_OUT |
| qokeey | TAKE_OUT |
| qoky | FERRY |
| qotedaiin | LEAVE |
| qotedy | OUTWARD |
| qoteedy | B |
| saiin | C |
| sain | WHEN |
| sar | UNSAFE |
| schedair | LIKEWISE |
| shdy | WITHOUT_HARM |
| shecthedy | JOINING_RESULT |
| shecthy | REST_CARGO |
| shedaiin | PAIRS |
| shedy | M |
| shey | EXAMPLE |
| shocphedy | CARGOS |
| soiiin | THUS |
| sol | THEN |
| soldy | HARM |
| solkeedy | WITH_TRIP |
| tchedy | FINALLY |

| Gruppen (einsbasiert) | Vollständiger Wortlaut | Bedingte Lesung |
|---|---|---|
| 1–5 | pdalshdy shocphedy otor shedy opshedy | Die drei Frachtstücke befinden sich mit der Begleitperson am Ausgangsufer. |
| 6–9 | otshdy qokedol shdy soldy | Ziel ist das gegenüberliegende Ufer ohne Schaden. |
| 10–15 | sar shedaiin ockhey sain ched shedy | Gefährliche Paare dürfen nicht ohne Begleitperson zusammenbleiben. |
| 16–20 | qetal dal shedy shey lchedy | Höchstens ein Frachtstück neben der Begleitperson; Beispiel: Fracht A. |
| 21–24 | solkeedy qoteedy qokeey qokedy | Mit dem Boot Fracht B hinüberbringen. |
| 25–25 | sol | Dann. |
| 26–27 | cheeety qokedy | Ohne Fracht B zurückfahren (Gegenvariante: mit dieser Fracht). |
| 28–29 | qoky saiin | Fracht C zum jeweils anderen Ufer übersetzen. |
| 30–32 | solkeedy qokedy otedy | Mit Fracht B zurückfahren. |
| 33–33 | sol | Dann. |
| 34–39 | chedy lkedy qokchedy qokedy chckhdy sar | Fracht A wäre mit Fracht B unbeaufsichtigt ein gefährliches Paar. |
| 40–41 | schedair otchedy | Entsprechend für das andere/erste Frachtstück; erstes/zweites Paarargument ersetzen. |
| 42–44 | qokeedy chedain chedy | Als Nächstes Fracht A hinüberbringen. |
| 45–46 | qotedaiin otaiin | Das zuletzt beförderte Frachtstück dort lassen (Zielufer/gegenwärtiges Ufer). |
| 47–48 | otedy ldy | Allein zurückfahren. |
| 49–53 | tchedy qotedy qokal shedy qokedy | Abschließend fahren Begleitperson und Fracht B gemeinsam hinüber. |
| 54–57 | shecthedy shecthy otor chedy | Die zuletzt beförderte Fracht befindet sich nun bei den übrigen, darunter Fracht A. |
| 58–63 | soiiin checthy chety otaiin olsaly shedy | Somit sind alle unversehrt dort, begleitet von der Begleitperson. |

| Variante | Einstellungen | Gefährliche Paare | Die sieben tatsächlichen Ladungen | Aufgelöste Bezüge |
|---|---|---|---|---|
| V00 | exclude=EXCLUDING, first=FIRST, other=OTHER, there=GOAL, copy=FIRST | Fracht C + Fracht B; Fracht B + Fracht A | Fracht B → leer → Fracht C → Fracht B → Fracht A → leer → Fracht B | S12: OTHER_CARGO → Fracht C |
| V02 | exclude=EXCLUDING, first=FIRST, other=OTHER, there=CURRENT, copy=FIRST | Fracht C + Fracht B; Fracht B + Fracht A | Fracht B → leer → Fracht C → Fracht B → Fracht A → leer → Fracht B | S12: OTHER_CARGO → Fracht C |
| V08 | exclude=EXCLUDING, first=RECENT, other=OTHER, there=GOAL, copy=FIRST | Fracht C + Fracht B; Fracht B + Fracht A | Fracht B → leer → Fracht C → Fracht B → Fracht A → leer → Fracht B | S12: OTHER_CARGO → Fracht C |
| V10 | exclude=EXCLUDING, first=RECENT, other=OTHER, there=CURRENT, copy=FIRST | Fracht C + Fracht B; Fracht B + Fracht A | Fracht B → leer → Fracht C → Fracht B → Fracht A → leer → Fracht B | S12: OTHER_CARGO → Fracht C |

Alle aufgeführten Pfade erreichen das Ziel ohne physischen Widerspruch, falsche Zustandsbehauptung oder unbeaufsichtigtes Gefahrpaar. Das bedeutet Konsistenz unter den angenommenen Regeln; es bedeutet keine unabhängige Bedeutungsbestätigung.

### FUNCTIONAL Karte 346

Kohärente Bezugseinstellungen: [0, 2, 4, 6]. Alle übrigen der 32 Varianten widersprechen mindestens einer registrierten Folge; ihre vollständigen Ergebnisse stehen in FAMILY_FUNCTIONAL.json.

| Form | Bedingte Terminalrolle |
|---|---|
| chckhdy | WOULD_BE |
| checthy | ALL |
| ched | WITHOUT_AGENT |
| chedain | NEXT |
| chedy | C |
| cheeety | RETURN_EXCLUDING |
| chety | UNHARMED |
| dal | BESIDES |
| lchedy | W |
| ldy | ALONE |
| lkedy | PAIRED_WITH |
| ockhey | FORBIDDEN |
| olsaly | ATTENDED_BY |
| opshedy | HOME |
| otaiin | THERE |
| otchedy | OTHER_CARGO |
| otedy | RETURN |
| otor | COLOC |
| otshdy | GOAL |
| pdalshdy | INIT |
| qetal | AT_MOST_ONE |
| qokal | TRAVEL_TOGETHER |
| qokchedy | UNATTENDED |
| qokedol | FAR_BANK |
| qokedy | G |
| qokeedy | CONVEY_OUT |
| qokeey | TAKE_OUT |
| qoky | FERRY |
| qotedaiin | LEAVE |
| qotedy | OUTWARD |
| qoteedy | B |
| saiin | FIRST_CARGO |
| sain | WHEN |
| sar | UNSAFE |
| schedair | LIKEWISE |
| shdy | WITHOUT_HARM |
| shecthedy | JOINING_RESULT |
| shecthy | REST_CARGO |
| shedaiin | PAIRS |
| shedy | M |
| shey | EXAMPLE |
| shocphedy | CARGOS |
| soiiin | THUS |
| sol | THEN |
| soldy | HARM |
| solkeedy | WITH_TRIP |
| tchedy | FINALLY |

| Gruppen (einsbasiert) | Vollständiger Wortlaut | Bedingte Lesung |
|---|---|---|
| 1–5 | pdalshdy shocphedy otor shedy opshedy | Die drei Frachtstücke befinden sich mit der Begleitperson am Ausgangsufer. |
| 6–9 | otshdy qokedol shdy soldy | Ziel ist das gegenüberliegende Ufer ohne Schaden. |
| 10–15 | sar shedaiin ockhey sain ched shedy | Gefährliche Paare dürfen nicht ohne Begleitperson zusammenbleiben. |
| 16–20 | qetal dal shedy shey lchedy | Höchstens ein Frachtstück neben der Begleitperson; Beispiel: Fracht A. |
| 21–24 | solkeedy qoteedy qokeey qokedy | Mit dem Boot Fracht B hinüberbringen. |
| 25–25 | sol | Dann. |
| 26–27 | cheeety qokedy | Ohne Fracht B zurückfahren (Gegenvariante: mit dieser Fracht). |
| 28–29 | qoky saiin | zuerst/zuletzt erwähnte Fracht zum jeweils anderen Ufer übersetzen. |
| 30–32 | solkeedy qokedy otedy | Mit Fracht B zurückfahren. |
| 33–33 | sol | Dann. |
| 34–39 | chedy lkedy qokchedy qokedy chckhdy sar | Fracht C wäre mit Fracht B unbeaufsichtigt ein gefährliches Paar. |
| 40–41 | schedair otchedy | Entsprechend für das andere/erste Frachtstück; erstes/zweites Paarargument ersetzen. |
| 42–44 | qokeedy chedain chedy | Als Nächstes Fracht C hinüberbringen. |
| 45–46 | qotedaiin otaiin | Das zuletzt beförderte Frachtstück dort lassen (Zielufer/gegenwärtiges Ufer). |
| 47–48 | otedy ldy | Allein zurückfahren. |
| 49–53 | tchedy qotedy qokal shedy qokedy | Abschließend fahren Begleitperson und Fracht B gemeinsam hinüber. |
| 54–57 | shecthedy shecthy otor chedy | Die zuletzt beförderte Fracht befindet sich nun bei den übrigen, darunter Fracht C. |
| 58–63 | soiiin checthy chety otaiin olsaly shedy | Somit sind alle unversehrt dort, begleitet von der Begleitperson. |

| Variante | Einstellungen | Gefährliche Paare | Die sieben tatsächlichen Ladungen | Aufgelöste Bezüge |
|---|---|---|---|---|
| V00 | exclude=EXCLUDING, first=FIRST, other=OTHER, there=GOAL, copy=FIRST | Fracht C + Fracht B; Fracht B + Fracht A | Fracht B → leer → Fracht A → Fracht B → Fracht C → leer → Fracht B | S08: FIRST_CARGO → Fracht A; S12: OTHER_CARGO → Fracht A |
| V02 | exclude=EXCLUDING, first=FIRST, other=OTHER, there=CURRENT, copy=FIRST | Fracht C + Fracht B; Fracht B + Fracht A | Fracht B → leer → Fracht A → Fracht B → Fracht C → leer → Fracht B | S08: FIRST_CARGO → Fracht A; S12: OTHER_CARGO → Fracht A |
| V04 | exclude=EXCLUDING, first=FIRST, other=FIRST, there=GOAL, copy=FIRST | Fracht C + Fracht B; Fracht B + Fracht A | Fracht B → leer → Fracht A → Fracht B → Fracht C → leer → Fracht B | S08: FIRST_CARGO → Fracht A; S12: OTHER_CARGO → Fracht A |
| V06 | exclude=EXCLUDING, first=FIRST, other=FIRST, there=CURRENT, copy=FIRST | Fracht C + Fracht B; Fracht B + Fracht A | Fracht B → leer → Fracht A → Fracht B → Fracht C → leer → Fracht B | S08: FIRST_CARGO → Fracht A; S12: OTHER_CARGO → Fracht A |

Alle aufgeführten Pfade erreichen das Ziel ohne physischen Widerspruch, falsche Zustandsbehauptung oder unbeaufsichtigtes Gefahrpaar. Das bedeutet Konsistenz unter den angenommenen Regeln; es bedeutet keine unabhängige Bedeutungsbestätigung.

### FUNCTIONAL Karte 347

Kohärente Bezugseinstellungen: [0, 2, 4, 6, 8, 10, 12, 14]. Alle übrigen der 32 Varianten widersprechen mindestens einer registrierten Folge; ihre vollständigen Ergebnisse stehen in FAMILY_FUNCTIONAL.json.

| Form | Bedingte Terminalrolle |
|---|---|
| chckhdy | WOULD_BE |
| checthy | ALL |
| ched | WITHOUT_AGENT |
| chedain | NEXT |
| chedy | C |
| cheeety | RETURN_EXCLUDING |
| chety | UNHARMED |
| dal | BESIDES |
| lchedy | W |
| ldy | ALONE |
| lkedy | PAIRED_WITH |
| ockhey | FORBIDDEN |
| olsaly | ATTENDED_BY |
| opshedy | HOME |
| otaiin | THERE |
| otchedy | OTHER_CARGO |
| otedy | RETURN |
| otor | COLOC |
| otshdy | GOAL |
| pdalshdy | INIT |
| qetal | AT_MOST_ONE |
| qokal | TRAVEL_TOGETHER |
| qokchedy | UNATTENDED |
| qokedol | FAR_BANK |
| qokedy | G |
| qokeedy | CONVEY_OUT |
| qokeey | TAKE_OUT |
| qoky | FERRY |
| qotedaiin | LEAVE |
| qotedy | OUTWARD |
| qoteedy | B |
| saiin | W |
| sain | WHEN |
| sar | UNSAFE |
| schedair | LIKEWISE |
| shdy | WITHOUT_HARM |
| shecthedy | JOINING_RESULT |
| shecthy | REST_CARGO |
| shedaiin | PAIRS |
| shedy | M |
| shey | EXAMPLE |
| shocphedy | CARGOS |
| soiiin | THUS |
| sol | THEN |
| soldy | HARM |
| solkeedy | WITH_TRIP |
| tchedy | FINALLY |

| Gruppen (einsbasiert) | Vollständiger Wortlaut | Bedingte Lesung |
|---|---|---|
| 1–5 | pdalshdy shocphedy otor shedy opshedy | Die drei Frachtstücke befinden sich mit der Begleitperson am Ausgangsufer. |
| 6–9 | otshdy qokedol shdy soldy | Ziel ist das gegenüberliegende Ufer ohne Schaden. |
| 10–15 | sar shedaiin ockhey sain ched shedy | Gefährliche Paare dürfen nicht ohne Begleitperson zusammenbleiben. |
| 16–20 | qetal dal shedy shey lchedy | Höchstens ein Frachtstück neben der Begleitperson; Beispiel: Fracht A. |
| 21–24 | solkeedy qoteedy qokeey qokedy | Mit dem Boot Fracht B hinüberbringen. |
| 25–25 | sol | Dann. |
| 26–27 | cheeety qokedy | Ohne Fracht B zurückfahren (Gegenvariante: mit dieser Fracht). |
| 28–29 | qoky saiin | Fracht A zum jeweils anderen Ufer übersetzen. |
| 30–32 | solkeedy qokedy otedy | Mit Fracht B zurückfahren. |
| 33–33 | sol | Dann. |
| 34–39 | chedy lkedy qokchedy qokedy chckhdy sar | Fracht C wäre mit Fracht B unbeaufsichtigt ein gefährliches Paar. |
| 40–41 | schedair otchedy | Entsprechend für das andere/erste Frachtstück; erstes/zweites Paarargument ersetzen. |
| 42–44 | qokeedy chedain chedy | Als Nächstes Fracht C hinüberbringen. |
| 45–46 | qotedaiin otaiin | Das zuletzt beförderte Frachtstück dort lassen (Zielufer/gegenwärtiges Ufer). |
| 47–48 | otedy ldy | Allein zurückfahren. |
| 49–53 | tchedy qotedy qokal shedy qokedy | Abschließend fahren Begleitperson und Fracht B gemeinsam hinüber. |
| 54–57 | shecthedy shecthy otor chedy | Die zuletzt beförderte Fracht befindet sich nun bei den übrigen, darunter Fracht C. |
| 58–63 | soiiin checthy chety otaiin olsaly shedy | Somit sind alle unversehrt dort, begleitet von der Begleitperson. |

| Variante | Einstellungen | Gefährliche Paare | Die sieben tatsächlichen Ladungen | Aufgelöste Bezüge |
|---|---|---|---|---|
| V00 | exclude=EXCLUDING, first=FIRST, other=OTHER, there=GOAL, copy=FIRST | Fracht C + Fracht B; Fracht B + Fracht A | Fracht B → leer → Fracht A → Fracht B → Fracht C → leer → Fracht B | S12: OTHER_CARGO → Fracht A |
| V02 | exclude=EXCLUDING, first=FIRST, other=OTHER, there=CURRENT, copy=FIRST | Fracht C + Fracht B; Fracht B + Fracht A | Fracht B → leer → Fracht A → Fracht B → Fracht C → leer → Fracht B | S12: OTHER_CARGO → Fracht A |
| V04 | exclude=EXCLUDING, first=FIRST, other=FIRST, there=GOAL, copy=FIRST | Fracht C + Fracht B; Fracht B + Fracht A | Fracht B → leer → Fracht A → Fracht B → Fracht C → leer → Fracht B | S12: OTHER_CARGO → Fracht A |
| V06 | exclude=EXCLUDING, first=FIRST, other=FIRST, there=CURRENT, copy=FIRST | Fracht C + Fracht B; Fracht B + Fracht A | Fracht B → leer → Fracht A → Fracht B → Fracht C → leer → Fracht B | S12: OTHER_CARGO → Fracht A |
| V08 | exclude=EXCLUDING, first=RECENT, other=OTHER, there=GOAL, copy=FIRST | Fracht C + Fracht B; Fracht B + Fracht A | Fracht B → leer → Fracht A → Fracht B → Fracht C → leer → Fracht B | S12: OTHER_CARGO → Fracht A |
| V10 | exclude=EXCLUDING, first=RECENT, other=OTHER, there=CURRENT, copy=FIRST | Fracht C + Fracht B; Fracht B + Fracht A | Fracht B → leer → Fracht A → Fracht B → Fracht C → leer → Fracht B | S12: OTHER_CARGO → Fracht A |
| V12 | exclude=EXCLUDING, first=RECENT, other=FIRST, there=GOAL, copy=FIRST | Fracht C + Fracht B; Fracht B + Fracht A | Fracht B → leer → Fracht A → Fracht B → Fracht C → leer → Fracht B | S12: OTHER_CARGO → Fracht A |
| V14 | exclude=EXCLUDING, first=RECENT, other=FIRST, there=CURRENT, copy=FIRST | Fracht C + Fracht B; Fracht B + Fracht A | Fracht B → leer → Fracht A → Fracht B → Fracht C → leer → Fracht B | S12: OTHER_CARGO → Fracht A |

Alle aufgeführten Pfade erreichen das Ziel ohne physischen Widerspruch, falsche Zustandsbehauptung oder unbeaufsichtigtes Gefahrpaar. Das bedeutet Konsistenz unter den angenommenen Regeln; es bedeutet keine unabhängige Bedeutungsbestätigung.

### FUNCTIONAL Karte 348

Kohärente Bezugseinstellungen: [0, 2]. Alle übrigen der 32 Varianten widersprechen mindestens einer registrierten Folge; ihre vollständigen Ergebnisse stehen in FAMILY_FUNCTIONAL.json.

| Form | Bedingte Terminalrolle |
|---|---|
| chckhdy | WOULD_BE |
| checthy | ALL |
| ched | WITHOUT_AGENT |
| chedain | NEXT |
| chedy | FIRST_CARGO |
| cheeety | RETURN_EXCLUDING |
| chety | UNHARMED |
| dal | BESIDES |
| lchedy | W |
| ldy | ALONE |
| lkedy | PAIRED_WITH |
| ockhey | FORBIDDEN |
| olsaly | ATTENDED_BY |
| opshedy | HOME |
| otaiin | THERE |
| otchedy | OTHER_CARGO |
| otedy | RETURN |
| otor | COLOC |
| otshdy | GOAL |
| pdalshdy | INIT |
| qetal | AT_MOST_ONE |
| qokal | TRAVEL_TOGETHER |
| qokchedy | UNATTENDED |
| qokedol | FAR_BANK |
| qokedy | G |
| qokeedy | CONVEY_OUT |
| qokeey | TAKE_OUT |
| qoky | FERRY |
| qotedaiin | LEAVE |
| qotedy | OUTWARD |
| qoteedy | B |
| saiin | C |
| sain | WHEN |
| sar | UNSAFE |
| schedair | LIKEWISE |
| shdy | WITHOUT_HARM |
| shecthedy | JOINING_RESULT |
| shecthy | REST_CARGO |
| shedaiin | PAIRS |
| shedy | M |
| shey | EXAMPLE |
| shocphedy | CARGOS |
| soiiin | THUS |
| sol | THEN |
| soldy | HARM |
| solkeedy | WITH_TRIP |
| tchedy | FINALLY |

| Gruppen (einsbasiert) | Vollständiger Wortlaut | Bedingte Lesung |
|---|---|---|
| 1–5 | pdalshdy shocphedy otor shedy opshedy | Die drei Frachtstücke befinden sich mit der Begleitperson am Ausgangsufer. |
| 6–9 | otshdy qokedol shdy soldy | Ziel ist das gegenüberliegende Ufer ohne Schaden. |
| 10–15 | sar shedaiin ockhey sain ched shedy | Gefährliche Paare dürfen nicht ohne Begleitperson zusammenbleiben. |
| 16–20 | qetal dal shedy shey lchedy | Höchstens ein Frachtstück neben der Begleitperson; Beispiel: Fracht A. |
| 21–24 | solkeedy qoteedy qokeey qokedy | Mit dem Boot Fracht B hinüberbringen. |
| 25–25 | sol | Dann. |
| 26–27 | cheeety qokedy | Ohne Fracht B zurückfahren (Gegenvariante: mit dieser Fracht). |
| 28–29 | qoky saiin | Fracht C zum jeweils anderen Ufer übersetzen. |
| 30–32 | solkeedy qokedy otedy | Mit Fracht B zurückfahren. |
| 33–33 | sol | Dann. |
| 34–39 | chedy lkedy qokchedy qokedy chckhdy sar | zuerst/zuletzt erwähnte Fracht wäre mit Fracht B unbeaufsichtigt ein gefährliches Paar. |
| 40–41 | schedair otchedy | Entsprechend für das andere/erste Frachtstück; erstes/zweites Paarargument ersetzen. |
| 42–44 | qokeedy chedain chedy | Als Nächstes zuerst/zuletzt erwähnte Fracht hinüberbringen. |
| 45–46 | qotedaiin otaiin | Das zuletzt beförderte Frachtstück dort lassen (Zielufer/gegenwärtiges Ufer). |
| 47–48 | otedy ldy | Allein zurückfahren. |
| 49–53 | tchedy qotedy qokal shedy qokedy | Abschließend fahren Begleitperson und Fracht B gemeinsam hinüber. |
| 54–57 | shecthedy shecthy otor chedy | Die zuletzt beförderte Fracht befindet sich nun bei den übrigen, darunter zuerst/zuletzt erwähnte Fracht. |
| 58–63 | soiiin checthy chety otaiin olsaly shedy | Somit sind alle unversehrt dort, begleitet von der Begleitperson. |

| Variante | Einstellungen | Gefährliche Paare | Die sieben tatsächlichen Ladungen | Aufgelöste Bezüge |
|---|---|---|---|---|
| V00 | exclude=EXCLUDING, first=FIRST, other=OTHER, there=GOAL, copy=FIRST | Fracht C + Fracht B; Fracht B + Fracht A | Fracht B → leer → Fracht C → Fracht B → Fracht A → leer → Fracht B | S11: FIRST_CARGO → Fracht A; S12: OTHER_CARGO → Fracht C; S13: FIRST_CARGO → Fracht A; S17: FIRST_CARGO → Fracht A |
| V02 | exclude=EXCLUDING, first=FIRST, other=OTHER, there=CURRENT, copy=FIRST | Fracht C + Fracht B; Fracht B + Fracht A | Fracht B → leer → Fracht C → Fracht B → Fracht A → leer → Fracht B | S11: FIRST_CARGO → Fracht A; S12: OTHER_CARGO → Fracht C; S13: FIRST_CARGO → Fracht A; S17: FIRST_CARGO → Fracht A |

Alle aufgeführten Pfade erreichen das Ziel ohne physischen Widerspruch, falsche Zustandsbehauptung oder unbeaufsichtigtes Gefahrpaar. Das bedeutet Konsistenz unter den angenommenen Regeln; es bedeutet keine unabhängige Bedeutungsbestätigung.

### FUNCTIONAL Karte 386

Kohärente Bezugseinstellungen: [4, 6, 12, 14]. Alle übrigen der 32 Varianten widersprechen mindestens einer registrierten Folge; ihre vollständigen Ergebnisse stehen in FAMILY_FUNCTIONAL.json.

| Form | Bedingte Terminalrolle |
|---|---|
| chckhdy | WOULD_BE |
| checthy | ALL |
| ched | WITHOUT_AGENT |
| chedain | NEXT |
| chedy | C |
| cheeety | RETURN_EXCLUDING |
| chety | UNHARMED |
| dal | BESIDES |
| lchedy | W |
| ldy | ALONE |
| lkedy | PAIRED_WITH |
| ockhey | FORBIDDEN |
| olsaly | ATTENDED_BY |
| opshedy | HOME |
| otaiin | THERE |
| otchedy | OTHER_CARGO |
| otedy | RETURN |
| otor | COLOC |
| otshdy | GOAL |
| pdalshdy | INIT |
| qetal | AT_MOST_ONE |
| qokal | TRAVEL_TOGETHER |
| qokchedy | UNATTENDED |
| qokedol | FAR_BANK |
| qokedy | G |
| qokeedy | CONVEY_OUT |
| qokeey | TAKE_OUT |
| qoky | FERRY |
| qotedaiin | LEAVE |
| qotedy | OUTWARD |
| qoteedy | B |
| saiin | OTHER_CARGO |
| sain | WHEN |
| sar | UNSAFE |
| schedair | LIKEWISE |
| shdy | WITHOUT_HARM |
| shecthedy | JOINING_RESULT |
| shecthy | REST_CARGO |
| shedaiin | PAIRS |
| shedy | M |
| shey | EXAMPLE |
| shocphedy | CARGOS |
| soiiin | THUS |
| sol | THEN |
| soldy | HARM |
| solkeedy | WITH_TRIP |
| tchedy | FINALLY |

| Gruppen (einsbasiert) | Vollständiger Wortlaut | Bedingte Lesung |
|---|---|---|
| 1–5 | pdalshdy shocphedy otor shedy opshedy | Die drei Frachtstücke befinden sich mit der Begleitperson am Ausgangsufer. |
| 6–9 | otshdy qokedol shdy soldy | Ziel ist das gegenüberliegende Ufer ohne Schaden. |
| 10–15 | sar shedaiin ockhey sain ched shedy | Gefährliche Paare dürfen nicht ohne Begleitperson zusammenbleiben. |
| 16–20 | qetal dal shedy shey lchedy | Höchstens ein Frachtstück neben der Begleitperson; Beispiel: Fracht A. |
| 21–24 | solkeedy qoteedy qokeey qokedy | Mit dem Boot Fracht B hinüberbringen. |
| 25–25 | sol | Dann. |
| 26–27 | cheeety qokedy | Ohne Fracht B zurückfahren (Gegenvariante: mit dieser Fracht). |
| 28–29 | qoky saiin | andere/erste Fracht zum jeweils anderen Ufer übersetzen. |
| 30–32 | solkeedy qokedy otedy | Mit Fracht B zurückfahren. |
| 33–33 | sol | Dann. |
| 34–39 | chedy lkedy qokchedy qokedy chckhdy sar | Fracht C wäre mit Fracht B unbeaufsichtigt ein gefährliches Paar. |
| 40–41 | schedair otchedy | Entsprechend für das andere/erste Frachtstück; erstes/zweites Paarargument ersetzen. |
| 42–44 | qokeedy chedain chedy | Als Nächstes Fracht C hinüberbringen. |
| 45–46 | qotedaiin otaiin | Das zuletzt beförderte Frachtstück dort lassen (Zielufer/gegenwärtiges Ufer). |
| 47–48 | otedy ldy | Allein zurückfahren. |
| 49–53 | tchedy qotedy qokal shedy qokedy | Abschließend fahren Begleitperson und Fracht B gemeinsam hinüber. |
| 54–57 | shecthedy shecthy otor chedy | Die zuletzt beförderte Fracht befindet sich nun bei den übrigen, darunter Fracht C. |
| 58–63 | soiiin checthy chety otaiin olsaly shedy | Somit sind alle unversehrt dort, begleitet von der Begleitperson. |

| Variante | Einstellungen | Gefährliche Paare | Die sieben tatsächlichen Ladungen | Aufgelöste Bezüge |
|---|---|---|---|---|
| V04 | exclude=EXCLUDING, first=FIRST, other=FIRST, there=GOAL, copy=FIRST | Fracht C + Fracht B; Fracht B + Fracht A | Fracht B → leer → Fracht A → Fracht B → Fracht C → leer → Fracht B | S08: OTHER_CARGO → Fracht A; S12: OTHER_CARGO → Fracht A |
| V06 | exclude=EXCLUDING, first=FIRST, other=FIRST, there=CURRENT, copy=FIRST | Fracht C + Fracht B; Fracht B + Fracht A | Fracht B → leer → Fracht A → Fracht B → Fracht C → leer → Fracht B | S08: OTHER_CARGO → Fracht A; S12: OTHER_CARGO → Fracht A |
| V12 | exclude=EXCLUDING, first=RECENT, other=FIRST, there=GOAL, copy=FIRST | Fracht C + Fracht B; Fracht B + Fracht A | Fracht B → leer → Fracht A → Fracht B → Fracht C → leer → Fracht B | S08: OTHER_CARGO → Fracht A; S12: OTHER_CARGO → Fracht A |
| V14 | exclude=EXCLUDING, first=RECENT, other=FIRST, there=CURRENT, copy=FIRST | Fracht C + Fracht B; Fracht B + Fracht A | Fracht B → leer → Fracht A → Fracht B → Fracht C → leer → Fracht B | S08: OTHER_CARGO → Fracht A; S12: OTHER_CARGO → Fracht A |

Alle aufgeführten Pfade erreichen das Ziel ohne physischen Widerspruch, falsche Zustandsbehauptung oder unbeaufsichtigtes Gefahrpaar. Das bedeutet Konsistenz unter den angenommenen Regeln; es bedeutet keine unabhängige Bedeutungsbestätigung.

### FUNCTIONAL Karte 537

Kohärente Bezugseinstellungen: [4, 6, 12, 14]. Alle übrigen der 32 Varianten widersprechen mindestens einer registrierten Folge; ihre vollständigen Ergebnisse stehen in FAMILY_FUNCTIONAL.json.

| Form | Bedingte Terminalrolle |
|---|---|
| chckhdy | WOULD_BE |
| checthy | ALL |
| ched | WITHOUT_AGENT |
| chedain | NEXT |
| chedy | W |
| cheeety | RETURN_EXCLUDING |
| chety | UNHARMED |
| dal | BESIDES |
| lchedy | C |
| ldy | ALONE |
| lkedy | PAIRED_WITH |
| ockhey | FORBIDDEN |
| olsaly | ATTENDED_BY |
| opshedy | HOME |
| otaiin | THERE |
| otchedy | OTHER_CARGO |
| otedy | RETURN |
| otor | COLOC |
| otshdy | GOAL |
| pdalshdy | INIT |
| qetal | AT_MOST_ONE |
| qokal | TRAVEL_TOGETHER |
| qokchedy | UNATTENDED |
| qokedol | FAR_BANK |
| qokedy | G |
| qokeedy | CONVEY_OUT |
| qokeey | TAKE_OUT |
| qoky | FERRY |
| qotedaiin | LEAVE |
| qotedy | OUTWARD |
| qoteedy | B |
| saiin | OTHER_CARGO |
| sain | WHEN |
| sar | UNSAFE |
| schedair | LIKEWISE |
| shdy | WITHOUT_HARM |
| shecthedy | JOINING_RESULT |
| shecthy | REST_CARGO |
| shedaiin | PAIRS |
| shedy | M |
| shey | EXAMPLE |
| shocphedy | CARGOS |
| soiiin | THUS |
| sol | THEN |
| soldy | HARM |
| solkeedy | WITH_TRIP |
| tchedy | FINALLY |

| Gruppen (einsbasiert) | Vollständiger Wortlaut | Bedingte Lesung |
|---|---|---|
| 1–5 | pdalshdy shocphedy otor shedy opshedy | Die drei Frachtstücke befinden sich mit der Begleitperson am Ausgangsufer. |
| 6–9 | otshdy qokedol shdy soldy | Ziel ist das gegenüberliegende Ufer ohne Schaden. |
| 10–15 | sar shedaiin ockhey sain ched shedy | Gefährliche Paare dürfen nicht ohne Begleitperson zusammenbleiben. |
| 16–20 | qetal dal shedy shey lchedy | Höchstens ein Frachtstück neben der Begleitperson; Beispiel: Fracht C. |
| 21–24 | solkeedy qoteedy qokeey qokedy | Mit dem Boot Fracht B hinüberbringen. |
| 25–25 | sol | Dann. |
| 26–27 | cheeety qokedy | Ohne Fracht B zurückfahren (Gegenvariante: mit dieser Fracht). |
| 28–29 | qoky saiin | andere/erste Fracht zum jeweils anderen Ufer übersetzen. |
| 30–32 | solkeedy qokedy otedy | Mit Fracht B zurückfahren. |
| 33–33 | sol | Dann. |
| 34–39 | chedy lkedy qokchedy qokedy chckhdy sar | Fracht A wäre mit Fracht B unbeaufsichtigt ein gefährliches Paar. |
| 40–41 | schedair otchedy | Entsprechend für das andere/erste Frachtstück; erstes/zweites Paarargument ersetzen. |
| 42–44 | qokeedy chedain chedy | Als Nächstes Fracht A hinüberbringen. |
| 45–46 | qotedaiin otaiin | Das zuletzt beförderte Frachtstück dort lassen (Zielufer/gegenwärtiges Ufer). |
| 47–48 | otedy ldy | Allein zurückfahren. |
| 49–53 | tchedy qotedy qokal shedy qokedy | Abschließend fahren Begleitperson und Fracht B gemeinsam hinüber. |
| 54–57 | shecthedy shecthy otor chedy | Die zuletzt beförderte Fracht befindet sich nun bei den übrigen, darunter Fracht A. |
| 58–63 | soiiin checthy chety otaiin olsaly shedy | Somit sind alle unversehrt dort, begleitet von der Begleitperson. |

| Variante | Einstellungen | Gefährliche Paare | Die sieben tatsächlichen Ladungen | Aufgelöste Bezüge |
|---|---|---|---|---|
| V04 | exclude=EXCLUDING, first=FIRST, other=FIRST, there=GOAL, copy=FIRST | Fracht C + Fracht B; Fracht B + Fracht A | Fracht B → leer → Fracht C → Fracht B → Fracht A → leer → Fracht B | S08: OTHER_CARGO → Fracht C; S12: OTHER_CARGO → Fracht C |
| V06 | exclude=EXCLUDING, first=FIRST, other=FIRST, there=CURRENT, copy=FIRST | Fracht C + Fracht B; Fracht B + Fracht A | Fracht B → leer → Fracht C → Fracht B → Fracht A → leer → Fracht B | S08: OTHER_CARGO → Fracht C; S12: OTHER_CARGO → Fracht C |
| V12 | exclude=EXCLUDING, first=RECENT, other=FIRST, there=GOAL, copy=FIRST | Fracht C + Fracht B; Fracht B + Fracht A | Fracht B → leer → Fracht C → Fracht B → Fracht A → leer → Fracht B | S08: OTHER_CARGO → Fracht C; S12: OTHER_CARGO → Fracht C |
| V14 | exclude=EXCLUDING, first=RECENT, other=FIRST, there=CURRENT, copy=FIRST | Fracht C + Fracht B; Fracht B + Fracht A | Fracht B → leer → Fracht C → Fracht B → Fracht A → leer → Fracht B | S08: OTHER_CARGO → Fracht C; S12: OTHER_CARGO → Fracht C |

Alle aufgeführten Pfade erreichen das Ziel ohne physischen Widerspruch, falsche Zustandsbehauptung oder unbeaufsichtigtes Gefahrpaar. Das bedeutet Konsistenz unter den angenommenen Regeln; es bedeutet keine unabhängige Bedeutungsbestätigung.

### FUNCTIONAL Karte 550

Kohärente Bezugseinstellungen: [0, 2, 8, 10]. Alle übrigen der 32 Varianten widersprechen mindestens einer registrierten Folge; ihre vollständigen Ergebnisse stehen in FAMILY_FUNCTIONAL.json.

| Form | Bedingte Terminalrolle |
|---|---|
| chckhdy | WOULD_BE |
| checthy | ALL |
| ched | WITHOUT_AGENT |
| chedain | NEXT |
| chedy | C |
| cheeety | RETURN_EXCLUDING |
| chety | UNHARMED |
| dal | BESIDES |
| lchedy | C |
| ldy | ALONE |
| lkedy | PAIRED_WITH |
| ockhey | FORBIDDEN |
| olsaly | ATTENDED_BY |
| opshedy | HOME |
| otaiin | THERE |
| otchedy | OTHER_CARGO |
| otedy | RETURN |
| otor | COLOC |
| otshdy | GOAL |
| pdalshdy | INIT |
| qetal | AT_MOST_ONE |
| qokal | TRAVEL_TOGETHER |
| qokchedy | UNATTENDED |
| qokedol | FAR_BANK |
| qokedy | G |
| qokeedy | CONVEY_OUT |
| qokeey | TAKE_OUT |
| qoky | FERRY |
| qotedaiin | LEAVE |
| qotedy | OUTWARD |
| qoteedy | B |
| saiin | W |
| sain | WHEN |
| sar | UNSAFE |
| schedair | LIKEWISE |
| shdy | WITHOUT_HARM |
| shecthedy | JOINING_RESULT |
| shecthy | REST_CARGO |
| shedaiin | PAIRS |
| shedy | M |
| shey | EXAMPLE |
| shocphedy | CARGOS |
| soiiin | THUS |
| sol | THEN |
| soldy | HARM |
| solkeedy | WITH_TRIP |
| tchedy | FINALLY |

| Gruppen (einsbasiert) | Vollständiger Wortlaut | Bedingte Lesung |
|---|---|---|
| 1–5 | pdalshdy shocphedy otor shedy opshedy | Die drei Frachtstücke befinden sich mit der Begleitperson am Ausgangsufer. |
| 6–9 | otshdy qokedol shdy soldy | Ziel ist das gegenüberliegende Ufer ohne Schaden. |
| 10–15 | sar shedaiin ockhey sain ched shedy | Gefährliche Paare dürfen nicht ohne Begleitperson zusammenbleiben. |
| 16–20 | qetal dal shedy shey lchedy | Höchstens ein Frachtstück neben der Begleitperson; Beispiel: Fracht C. |
| 21–24 | solkeedy qoteedy qokeey qokedy | Mit dem Boot Fracht B hinüberbringen. |
| 25–25 | sol | Dann. |
| 26–27 | cheeety qokedy | Ohne Fracht B zurückfahren (Gegenvariante: mit dieser Fracht). |
| 28–29 | qoky saiin | Fracht A zum jeweils anderen Ufer übersetzen. |
| 30–32 | solkeedy qokedy otedy | Mit Fracht B zurückfahren. |
| 33–33 | sol | Dann. |
| 34–39 | chedy lkedy qokchedy qokedy chckhdy sar | Fracht C wäre mit Fracht B unbeaufsichtigt ein gefährliches Paar. |
| 40–41 | schedair otchedy | Entsprechend für das andere/erste Frachtstück; erstes/zweites Paarargument ersetzen. |
| 42–44 | qokeedy chedain chedy | Als Nächstes Fracht C hinüberbringen. |
| 45–46 | qotedaiin otaiin | Das zuletzt beförderte Frachtstück dort lassen (Zielufer/gegenwärtiges Ufer). |
| 47–48 | otedy ldy | Allein zurückfahren. |
| 49–53 | tchedy qotedy qokal shedy qokedy | Abschließend fahren Begleitperson und Fracht B gemeinsam hinüber. |
| 54–57 | shecthedy shecthy otor chedy | Die zuletzt beförderte Fracht befindet sich nun bei den übrigen, darunter Fracht C. |
| 58–63 | soiiin checthy chety otaiin olsaly shedy | Somit sind alle unversehrt dort, begleitet von der Begleitperson. |

| Variante | Einstellungen | Gefährliche Paare | Die sieben tatsächlichen Ladungen | Aufgelöste Bezüge |
|---|---|---|---|---|
| V00 | exclude=EXCLUDING, first=FIRST, other=OTHER, there=GOAL, copy=FIRST | Fracht C + Fracht B; Fracht B + Fracht A | Fracht B → leer → Fracht A → Fracht B → Fracht C → leer → Fracht B | S12: OTHER_CARGO → Fracht A |
| V02 | exclude=EXCLUDING, first=FIRST, other=OTHER, there=CURRENT, copy=FIRST | Fracht C + Fracht B; Fracht B + Fracht A | Fracht B → leer → Fracht A → Fracht B → Fracht C → leer → Fracht B | S12: OTHER_CARGO → Fracht A |
| V08 | exclude=EXCLUDING, first=RECENT, other=OTHER, there=GOAL, copy=FIRST | Fracht C + Fracht B; Fracht B + Fracht A | Fracht B → leer → Fracht A → Fracht B → Fracht C → leer → Fracht B | S12: OTHER_CARGO → Fracht A |
| V10 | exclude=EXCLUDING, first=RECENT, other=OTHER, there=CURRENT, copy=FIRST | Fracht C + Fracht B; Fracht B + Fracht A | Fracht B → leer → Fracht A → Fracht B → Fracht C → leer → Fracht B | S12: OTHER_CARGO → Fracht A |

Alle aufgeführten Pfade erreichen das Ziel ohne physischen Widerspruch, falsche Zustandsbehauptung oder unbeaufsichtigtes Gefahrpaar. Das bedeutet Konsistenz unter den angenommenen Regeln; es bedeutet keine unabhängige Bedeutungsbestätigung.

### FUNCTIONAL Karte 559

Kohärente Bezugseinstellungen: [0, 2]. Alle übrigen der 32 Varianten widersprechen mindestens einer registrierten Folge; ihre vollständigen Ergebnisse stehen in FAMILY_FUNCTIONAL.json.

| Form | Bedingte Terminalrolle |
|---|---|
| chckhdy | WOULD_BE |
| checthy | ALL |
| ched | WITHOUT_AGENT |
| chedain | NEXT |
| chedy | FIRST_CARGO |
| cheeety | RETURN_EXCLUDING |
| chety | UNHARMED |
| dal | BESIDES |
| lchedy | C |
| ldy | ALONE |
| lkedy | PAIRED_WITH |
| ockhey | FORBIDDEN |
| olsaly | ATTENDED_BY |
| opshedy | HOME |
| otaiin | THERE |
| otchedy | OTHER_CARGO |
| otedy | RETURN |
| otor | COLOC |
| otshdy | GOAL |
| pdalshdy | INIT |
| qetal | AT_MOST_ONE |
| qokal | TRAVEL_TOGETHER |
| qokchedy | UNATTENDED |
| qokedol | FAR_BANK |
| qokedy | G |
| qokeedy | CONVEY_OUT |
| qokeey | TAKE_OUT |
| qoky | FERRY |
| qotedaiin | LEAVE |
| qotedy | OUTWARD |
| qoteedy | B |
| saiin | W |
| sain | WHEN |
| sar | UNSAFE |
| schedair | LIKEWISE |
| shdy | WITHOUT_HARM |
| shecthedy | JOINING_RESULT |
| shecthy | REST_CARGO |
| shedaiin | PAIRS |
| shedy | M |
| shey | EXAMPLE |
| shocphedy | CARGOS |
| soiiin | THUS |
| sol | THEN |
| soldy | HARM |
| solkeedy | WITH_TRIP |
| tchedy | FINALLY |

| Gruppen (einsbasiert) | Vollständiger Wortlaut | Bedingte Lesung |
|---|---|---|
| 1–5 | pdalshdy shocphedy otor shedy opshedy | Die drei Frachtstücke befinden sich mit der Begleitperson am Ausgangsufer. |
| 6–9 | otshdy qokedol shdy soldy | Ziel ist das gegenüberliegende Ufer ohne Schaden. |
| 10–15 | sar shedaiin ockhey sain ched shedy | Gefährliche Paare dürfen nicht ohne Begleitperson zusammenbleiben. |
| 16–20 | qetal dal shedy shey lchedy | Höchstens ein Frachtstück neben der Begleitperson; Beispiel: Fracht C. |
| 21–24 | solkeedy qoteedy qokeey qokedy | Mit dem Boot Fracht B hinüberbringen. |
| 25–25 | sol | Dann. |
| 26–27 | cheeety qokedy | Ohne Fracht B zurückfahren (Gegenvariante: mit dieser Fracht). |
| 28–29 | qoky saiin | Fracht A zum jeweils anderen Ufer übersetzen. |
| 30–32 | solkeedy qokedy otedy | Mit Fracht B zurückfahren. |
| 33–33 | sol | Dann. |
| 34–39 | chedy lkedy qokchedy qokedy chckhdy sar | zuerst/zuletzt erwähnte Fracht wäre mit Fracht B unbeaufsichtigt ein gefährliches Paar. |
| 40–41 | schedair otchedy | Entsprechend für das andere/erste Frachtstück; erstes/zweites Paarargument ersetzen. |
| 42–44 | qokeedy chedain chedy | Als Nächstes zuerst/zuletzt erwähnte Fracht hinüberbringen. |
| 45–46 | qotedaiin otaiin | Das zuletzt beförderte Frachtstück dort lassen (Zielufer/gegenwärtiges Ufer). |
| 47–48 | otedy ldy | Allein zurückfahren. |
| 49–53 | tchedy qotedy qokal shedy qokedy | Abschließend fahren Begleitperson und Fracht B gemeinsam hinüber. |
| 54–57 | shecthedy shecthy otor chedy | Die zuletzt beförderte Fracht befindet sich nun bei den übrigen, darunter zuerst/zuletzt erwähnte Fracht. |
| 58–63 | soiiin checthy chety otaiin olsaly shedy | Somit sind alle unversehrt dort, begleitet von der Begleitperson. |

| Variante | Einstellungen | Gefährliche Paare | Die sieben tatsächlichen Ladungen | Aufgelöste Bezüge |
|---|---|---|---|---|
| V00 | exclude=EXCLUDING, first=FIRST, other=OTHER, there=GOAL, copy=FIRST | Fracht C + Fracht B; Fracht B + Fracht A | Fracht B → leer → Fracht A → Fracht B → Fracht C → leer → Fracht B | S11: FIRST_CARGO → Fracht C; S12: OTHER_CARGO → Fracht A; S13: FIRST_CARGO → Fracht C; S17: FIRST_CARGO → Fracht C |
| V02 | exclude=EXCLUDING, first=FIRST, other=OTHER, there=CURRENT, copy=FIRST | Fracht C + Fracht B; Fracht B + Fracht A | Fracht B → leer → Fracht A → Fracht B → Fracht C → leer → Fracht B | S11: FIRST_CARGO → Fracht C; S12: OTHER_CARGO → Fracht A; S13: FIRST_CARGO → Fracht C; S17: FIRST_CARGO → Fracht C |

Alle aufgeführten Pfade erreichen das Ziel ohne physischen Widerspruch, falsche Zustandsbehauptung oder unbeaufsichtigtes Gefahrpaar. Das bedeutet Konsistenz unter den angenommenen Regeln; es bedeutet keine unabhängige Bedeutungsbestätigung.

### FUNCTIONAL Karte 565

Kohärente Bezugseinstellungen: [0, 2, 4, 6]. Alle übrigen der 32 Varianten widersprechen mindestens einer registrierten Folge; ihre vollständigen Ergebnisse stehen in FAMILY_FUNCTIONAL.json.

| Form | Bedingte Terminalrolle |
|---|---|
| chckhdy | WOULD_BE |
| checthy | ALL |
| ched | WITHOUT_AGENT |
| chedain | NEXT |
| chedy | W |
| cheeety | RETURN_EXCLUDING |
| chety | UNHARMED |
| dal | BESIDES |
| lchedy | C |
| ldy | ALONE |
| lkedy | PAIRED_WITH |
| ockhey | FORBIDDEN |
| olsaly | ATTENDED_BY |
| opshedy | HOME |
| otaiin | THERE |
| otchedy | OTHER_CARGO |
| otedy | RETURN |
| otor | COLOC |
| otshdy | GOAL |
| pdalshdy | INIT |
| qetal | AT_MOST_ONE |
| qokal | TRAVEL_TOGETHER |
| qokchedy | UNATTENDED |
| qokedol | FAR_BANK |
| qokedy | G |
| qokeedy | CONVEY_OUT |
| qokeey | TAKE_OUT |
| qoky | FERRY |
| qotedaiin | LEAVE |
| qotedy | OUTWARD |
| qoteedy | B |
| saiin | FIRST_CARGO |
| sain | WHEN |
| sar | UNSAFE |
| schedair | LIKEWISE |
| shdy | WITHOUT_HARM |
| shecthedy | JOINING_RESULT |
| shecthy | REST_CARGO |
| shedaiin | PAIRS |
| shedy | M |
| shey | EXAMPLE |
| shocphedy | CARGOS |
| soiiin | THUS |
| sol | THEN |
| soldy | HARM |
| solkeedy | WITH_TRIP |
| tchedy | FINALLY |

| Gruppen (einsbasiert) | Vollständiger Wortlaut | Bedingte Lesung |
|---|---|---|
| 1–5 | pdalshdy shocphedy otor shedy opshedy | Die drei Frachtstücke befinden sich mit der Begleitperson am Ausgangsufer. |
| 6–9 | otshdy qokedol shdy soldy | Ziel ist das gegenüberliegende Ufer ohne Schaden. |
| 10–15 | sar shedaiin ockhey sain ched shedy | Gefährliche Paare dürfen nicht ohne Begleitperson zusammenbleiben. |
| 16–20 | qetal dal shedy shey lchedy | Höchstens ein Frachtstück neben der Begleitperson; Beispiel: Fracht C. |
| 21–24 | solkeedy qoteedy qokeey qokedy | Mit dem Boot Fracht B hinüberbringen. |
| 25–25 | sol | Dann. |
| 26–27 | cheeety qokedy | Ohne Fracht B zurückfahren (Gegenvariante: mit dieser Fracht). |
| 28–29 | qoky saiin | zuerst/zuletzt erwähnte Fracht zum jeweils anderen Ufer übersetzen. |
| 30–32 | solkeedy qokedy otedy | Mit Fracht B zurückfahren. |
| 33–33 | sol | Dann. |
| 34–39 | chedy lkedy qokchedy qokedy chckhdy sar | Fracht A wäre mit Fracht B unbeaufsichtigt ein gefährliches Paar. |
| 40–41 | schedair otchedy | Entsprechend für das andere/erste Frachtstück; erstes/zweites Paarargument ersetzen. |
| 42–44 | qokeedy chedain chedy | Als Nächstes Fracht A hinüberbringen. |
| 45–46 | qotedaiin otaiin | Das zuletzt beförderte Frachtstück dort lassen (Zielufer/gegenwärtiges Ufer). |
| 47–48 | otedy ldy | Allein zurückfahren. |
| 49–53 | tchedy qotedy qokal shedy qokedy | Abschließend fahren Begleitperson und Fracht B gemeinsam hinüber. |
| 54–57 | shecthedy shecthy otor chedy | Die zuletzt beförderte Fracht befindet sich nun bei den übrigen, darunter Fracht A. |
| 58–63 | soiiin checthy chety otaiin olsaly shedy | Somit sind alle unversehrt dort, begleitet von der Begleitperson. |

| Variante | Einstellungen | Gefährliche Paare | Die sieben tatsächlichen Ladungen | Aufgelöste Bezüge |
|---|---|---|---|---|
| V00 | exclude=EXCLUDING, first=FIRST, other=OTHER, there=GOAL, copy=FIRST | Fracht C + Fracht B; Fracht B + Fracht A | Fracht B → leer → Fracht C → Fracht B → Fracht A → leer → Fracht B | S08: FIRST_CARGO → Fracht C; S12: OTHER_CARGO → Fracht C |
| V02 | exclude=EXCLUDING, first=FIRST, other=OTHER, there=CURRENT, copy=FIRST | Fracht C + Fracht B; Fracht B + Fracht A | Fracht B → leer → Fracht C → Fracht B → Fracht A → leer → Fracht B | S08: FIRST_CARGO → Fracht C; S12: OTHER_CARGO → Fracht C |
| V04 | exclude=EXCLUDING, first=FIRST, other=FIRST, there=GOAL, copy=FIRST | Fracht C + Fracht B; Fracht B + Fracht A | Fracht B → leer → Fracht C → Fracht B → Fracht A → leer → Fracht B | S08: FIRST_CARGO → Fracht C; S12: OTHER_CARGO → Fracht C |
| V06 | exclude=EXCLUDING, first=FIRST, other=FIRST, there=CURRENT, copy=FIRST | Fracht C + Fracht B; Fracht B + Fracht A | Fracht B → leer → Fracht C → Fracht B → Fracht A → leer → Fracht B | S08: FIRST_CARGO → Fracht C; S12: OTHER_CARGO → Fracht C |

Alle aufgeführten Pfade erreichen das Ziel ohne physischen Widerspruch, falsche Zustandsbehauptung oder unbeaufsichtigtes Gefahrpaar. Das bedeutet Konsistenz unter den angenommenen Regeln; es bedeutet keine unabhängige Bedeutungsbestätigung.

### FUNCTIONAL Karte 566

Kohärente Bezugseinstellungen: [0, 2, 4, 6, 8, 10, 12, 14]. Alle übrigen der 32 Varianten widersprechen mindestens einer registrierten Folge; ihre vollständigen Ergebnisse stehen in FAMILY_FUNCTIONAL.json.

| Form | Bedingte Terminalrolle |
|---|---|
| chckhdy | WOULD_BE |
| checthy | ALL |
| ched | WITHOUT_AGENT |
| chedain | NEXT |
| chedy | W |
| cheeety | RETURN_EXCLUDING |
| chety | UNHARMED |
| dal | BESIDES |
| lchedy | C |
| ldy | ALONE |
| lkedy | PAIRED_WITH |
| ockhey | FORBIDDEN |
| olsaly | ATTENDED_BY |
| opshedy | HOME |
| otaiin | THERE |
| otchedy | OTHER_CARGO |
| otedy | RETURN |
| otor | COLOC |
| otshdy | GOAL |
| pdalshdy | INIT |
| qetal | AT_MOST_ONE |
| qokal | TRAVEL_TOGETHER |
| qokchedy | UNATTENDED |
| qokedol | FAR_BANK |
| qokedy | G |
| qokeedy | CONVEY_OUT |
| qokeey | TAKE_OUT |
| qoky | FERRY |
| qotedaiin | LEAVE |
| qotedy | OUTWARD |
| qoteedy | B |
| saiin | C |
| sain | WHEN |
| sar | UNSAFE |
| schedair | LIKEWISE |
| shdy | WITHOUT_HARM |
| shecthedy | JOINING_RESULT |
| shecthy | REST_CARGO |
| shedaiin | PAIRS |
| shedy | M |
| shey | EXAMPLE |
| shocphedy | CARGOS |
| soiiin | THUS |
| sol | THEN |
| soldy | HARM |
| solkeedy | WITH_TRIP |
| tchedy | FINALLY |

| Gruppen (einsbasiert) | Vollständiger Wortlaut | Bedingte Lesung |
|---|---|---|
| 1–5 | pdalshdy shocphedy otor shedy opshedy | Die drei Frachtstücke befinden sich mit der Begleitperson am Ausgangsufer. |
| 6–9 | otshdy qokedol shdy soldy | Ziel ist das gegenüberliegende Ufer ohne Schaden. |
| 10–15 | sar shedaiin ockhey sain ched shedy | Gefährliche Paare dürfen nicht ohne Begleitperson zusammenbleiben. |
| 16–20 | qetal dal shedy shey lchedy | Höchstens ein Frachtstück neben der Begleitperson; Beispiel: Fracht C. |
| 21–24 | solkeedy qoteedy qokeey qokedy | Mit dem Boot Fracht B hinüberbringen. |
| 25–25 | sol | Dann. |
| 26–27 | cheeety qokedy | Ohne Fracht B zurückfahren (Gegenvariante: mit dieser Fracht). |
| 28–29 | qoky saiin | Fracht C zum jeweils anderen Ufer übersetzen. |
| 30–32 | solkeedy qokedy otedy | Mit Fracht B zurückfahren. |
| 33–33 | sol | Dann. |
| 34–39 | chedy lkedy qokchedy qokedy chckhdy sar | Fracht A wäre mit Fracht B unbeaufsichtigt ein gefährliches Paar. |
| 40–41 | schedair otchedy | Entsprechend für das andere/erste Frachtstück; erstes/zweites Paarargument ersetzen. |
| 42–44 | qokeedy chedain chedy | Als Nächstes Fracht A hinüberbringen. |
| 45–46 | qotedaiin otaiin | Das zuletzt beförderte Frachtstück dort lassen (Zielufer/gegenwärtiges Ufer). |
| 47–48 | otedy ldy | Allein zurückfahren. |
| 49–53 | tchedy qotedy qokal shedy qokedy | Abschließend fahren Begleitperson und Fracht B gemeinsam hinüber. |
| 54–57 | shecthedy shecthy otor chedy | Die zuletzt beförderte Fracht befindet sich nun bei den übrigen, darunter Fracht A. |
| 58–63 | soiiin checthy chety otaiin olsaly shedy | Somit sind alle unversehrt dort, begleitet von der Begleitperson. |

| Variante | Einstellungen | Gefährliche Paare | Die sieben tatsächlichen Ladungen | Aufgelöste Bezüge |
|---|---|---|---|---|
| V00 | exclude=EXCLUDING, first=FIRST, other=OTHER, there=GOAL, copy=FIRST | Fracht C + Fracht B; Fracht B + Fracht A | Fracht B → leer → Fracht C → Fracht B → Fracht A → leer → Fracht B | S12: OTHER_CARGO → Fracht C |
| V02 | exclude=EXCLUDING, first=FIRST, other=OTHER, there=CURRENT, copy=FIRST | Fracht C + Fracht B; Fracht B + Fracht A | Fracht B → leer → Fracht C → Fracht B → Fracht A → leer → Fracht B | S12: OTHER_CARGO → Fracht C |
| V04 | exclude=EXCLUDING, first=FIRST, other=FIRST, there=GOAL, copy=FIRST | Fracht C + Fracht B; Fracht B + Fracht A | Fracht B → leer → Fracht C → Fracht B → Fracht A → leer → Fracht B | S12: OTHER_CARGO → Fracht C |
| V06 | exclude=EXCLUDING, first=FIRST, other=FIRST, there=CURRENT, copy=FIRST | Fracht C + Fracht B; Fracht B + Fracht A | Fracht B → leer → Fracht C → Fracht B → Fracht A → leer → Fracht B | S12: OTHER_CARGO → Fracht C |
| V08 | exclude=EXCLUDING, first=RECENT, other=OTHER, there=GOAL, copy=FIRST | Fracht C + Fracht B; Fracht B + Fracht A | Fracht B → leer → Fracht C → Fracht B → Fracht A → leer → Fracht B | S12: OTHER_CARGO → Fracht C |
| V10 | exclude=EXCLUDING, first=RECENT, other=OTHER, there=CURRENT, copy=FIRST | Fracht C + Fracht B; Fracht B + Fracht A | Fracht B → leer → Fracht C → Fracht B → Fracht A → leer → Fracht B | S12: OTHER_CARGO → Fracht C |
| V12 | exclude=EXCLUDING, first=RECENT, other=FIRST, there=GOAL, copy=FIRST | Fracht C + Fracht B; Fracht B + Fracht A | Fracht B → leer → Fracht C → Fracht B → Fracht A → leer → Fracht B | S12: OTHER_CARGO → Fracht C |
| V14 | exclude=EXCLUDING, first=RECENT, other=FIRST, there=CURRENT, copy=FIRST | Fracht C + Fracht B; Fracht B + Fracht A | Fracht B → leer → Fracht C → Fracht B → Fracht A → leer → Fracht B | S12: OTHER_CARGO → Fracht C |

Alle aufgeführten Pfade erreichen das Ziel ohne physischen Widerspruch, falsche Zustandsbehauptung oder unbeaufsichtigtes Gefahrpaar. Das bedeutet Konsistenz unter den angenommenen Regeln; es bedeutet keine unabhängige Bedeutungsbestätigung.

### FUNCTIONAL Karte 593

Kohärente Bezugseinstellungen: [0, 2, 8, 10]. Alle übrigen der 32 Varianten widersprechen mindestens einer registrierten Folge; ihre vollständigen Ergebnisse stehen in FAMILY_FUNCTIONAL.json.

| Form | Bedingte Terminalrolle |
|---|---|
| chckhdy | WOULD_BE |
| checthy | ALL |
| ched | WITHOUT_AGENT |
| chedain | NEXT |
| chedy | C |
| cheeety | RETURN_EXCLUDING |
| chety | UNHARMED |
| dal | BESIDES |
| lchedy | G |
| ldy | ALONE |
| lkedy | PAIRED_WITH |
| ockhey | FORBIDDEN |
| olsaly | ATTENDED_BY |
| opshedy | HOME |
| otaiin | THERE |
| otchedy | OTHER_CARGO |
| otedy | RETURN |
| otor | COLOC |
| otshdy | GOAL |
| pdalshdy | INIT |
| qetal | AT_MOST_ONE |
| qokal | TRAVEL_TOGETHER |
| qokchedy | UNATTENDED |
| qokedol | FAR_BANK |
| qokedy | G |
| qokeedy | CONVEY_OUT |
| qokeey | TAKE_OUT |
| qoky | FERRY |
| qotedaiin | LEAVE |
| qotedy | OUTWARD |
| qoteedy | B |
| saiin | W |
| sain | WHEN |
| sar | UNSAFE |
| schedair | LIKEWISE |
| shdy | WITHOUT_HARM |
| shecthedy | JOINING_RESULT |
| shecthy | REST_CARGO |
| shedaiin | PAIRS |
| shedy | M |
| shey | EXAMPLE |
| shocphedy | CARGOS |
| soiiin | THUS |
| sol | THEN |
| soldy | HARM |
| solkeedy | WITH_TRIP |
| tchedy | FINALLY |

| Gruppen (einsbasiert) | Vollständiger Wortlaut | Bedingte Lesung |
|---|---|---|
| 1–5 | pdalshdy shocphedy otor shedy opshedy | Die drei Frachtstücke befinden sich mit der Begleitperson am Ausgangsufer. |
| 6–9 | otshdy qokedol shdy soldy | Ziel ist das gegenüberliegende Ufer ohne Schaden. |
| 10–15 | sar shedaiin ockhey sain ched shedy | Gefährliche Paare dürfen nicht ohne Begleitperson zusammenbleiben. |
| 16–20 | qetal dal shedy shey lchedy | Höchstens ein Frachtstück neben der Begleitperson; Beispiel: Fracht B. |
| 21–24 | solkeedy qoteedy qokeey qokedy | Mit dem Boot Fracht B hinüberbringen. |
| 25–25 | sol | Dann. |
| 26–27 | cheeety qokedy | Ohne Fracht B zurückfahren (Gegenvariante: mit dieser Fracht). |
| 28–29 | qoky saiin | Fracht A zum jeweils anderen Ufer übersetzen. |
| 30–32 | solkeedy qokedy otedy | Mit Fracht B zurückfahren. |
| 33–33 | sol | Dann. |
| 34–39 | chedy lkedy qokchedy qokedy chckhdy sar | Fracht C wäre mit Fracht B unbeaufsichtigt ein gefährliches Paar. |
| 40–41 | schedair otchedy | Entsprechend für das andere/erste Frachtstück; erstes/zweites Paarargument ersetzen. |
| 42–44 | qokeedy chedain chedy | Als Nächstes Fracht C hinüberbringen. |
| 45–46 | qotedaiin otaiin | Das zuletzt beförderte Frachtstück dort lassen (Zielufer/gegenwärtiges Ufer). |
| 47–48 | otedy ldy | Allein zurückfahren. |
| 49–53 | tchedy qotedy qokal shedy qokedy | Abschließend fahren Begleitperson und Fracht B gemeinsam hinüber. |
| 54–57 | shecthedy shecthy otor chedy | Die zuletzt beförderte Fracht befindet sich nun bei den übrigen, darunter Fracht C. |
| 58–63 | soiiin checthy chety otaiin olsaly shedy | Somit sind alle unversehrt dort, begleitet von der Begleitperson. |

| Variante | Einstellungen | Gefährliche Paare | Die sieben tatsächlichen Ladungen | Aufgelöste Bezüge |
|---|---|---|---|---|
| V00 | exclude=EXCLUDING, first=FIRST, other=OTHER, there=GOAL, copy=FIRST | Fracht C + Fracht B; Fracht B + Fracht A | Fracht B → leer → Fracht A → Fracht B → Fracht C → leer → Fracht B | S12: OTHER_CARGO → Fracht A |
| V02 | exclude=EXCLUDING, first=FIRST, other=OTHER, there=CURRENT, copy=FIRST | Fracht C + Fracht B; Fracht B + Fracht A | Fracht B → leer → Fracht A → Fracht B → Fracht C → leer → Fracht B | S12: OTHER_CARGO → Fracht A |
| V08 | exclude=EXCLUDING, first=RECENT, other=OTHER, there=GOAL, copy=FIRST | Fracht C + Fracht B; Fracht B + Fracht A | Fracht B → leer → Fracht A → Fracht B → Fracht C → leer → Fracht B | S12: OTHER_CARGO → Fracht A |
| V10 | exclude=EXCLUDING, first=RECENT, other=OTHER, there=CURRENT, copy=FIRST | Fracht C + Fracht B; Fracht B + Fracht A | Fracht B → leer → Fracht A → Fracht B → Fracht C → leer → Fracht B | S12: OTHER_CARGO → Fracht A |

Alle aufgeführten Pfade erreichen das Ziel ohne physischen Widerspruch, falsche Zustandsbehauptung oder unbeaufsichtigtes Gefahrpaar. Das bedeutet Konsistenz unter den angenommenen Regeln; es bedeutet keine unabhängige Bedeutungsbestätigung.

### FUNCTIONAL Karte 614

Kohärente Bezugseinstellungen: [0, 2, 8, 10]. Alle übrigen der 32 Varianten widersprechen mindestens einer registrierten Folge; ihre vollständigen Ergebnisse stehen in FAMILY_FUNCTIONAL.json.

| Form | Bedingte Terminalrolle |
|---|---|
| chckhdy | WOULD_BE |
| checthy | ALL |
| ched | WITHOUT_AGENT |
| chedain | NEXT |
| chedy | W |
| cheeety | RETURN_EXCLUDING |
| chety | UNHARMED |
| dal | BESIDES |
| lchedy | G |
| ldy | ALONE |
| lkedy | PAIRED_WITH |
| ockhey | FORBIDDEN |
| olsaly | ATTENDED_BY |
| opshedy | HOME |
| otaiin | THERE |
| otchedy | OTHER_CARGO |
| otedy | RETURN |
| otor | COLOC |
| otshdy | GOAL |
| pdalshdy | INIT |
| qetal | AT_MOST_ONE |
| qokal | TRAVEL_TOGETHER |
| qokchedy | UNATTENDED |
| qokedol | FAR_BANK |
| qokedy | G |
| qokeedy | CONVEY_OUT |
| qokeey | TAKE_OUT |
| qoky | FERRY |
| qotedaiin | LEAVE |
| qotedy | OUTWARD |
| qoteedy | B |
| saiin | C |
| sain | WHEN |
| sar | UNSAFE |
| schedair | LIKEWISE |
| shdy | WITHOUT_HARM |
| shecthedy | JOINING_RESULT |
| shecthy | REST_CARGO |
| shedaiin | PAIRS |
| shedy | M |
| shey | EXAMPLE |
| shocphedy | CARGOS |
| soiiin | THUS |
| sol | THEN |
| soldy | HARM |
| solkeedy | WITH_TRIP |
| tchedy | FINALLY |

| Gruppen (einsbasiert) | Vollständiger Wortlaut | Bedingte Lesung |
|---|---|---|
| 1–5 | pdalshdy shocphedy otor shedy opshedy | Die drei Frachtstücke befinden sich mit der Begleitperson am Ausgangsufer. |
| 6–9 | otshdy qokedol shdy soldy | Ziel ist das gegenüberliegende Ufer ohne Schaden. |
| 10–15 | sar shedaiin ockhey sain ched shedy | Gefährliche Paare dürfen nicht ohne Begleitperson zusammenbleiben. |
| 16–20 | qetal dal shedy shey lchedy | Höchstens ein Frachtstück neben der Begleitperson; Beispiel: Fracht B. |
| 21–24 | solkeedy qoteedy qokeey qokedy | Mit dem Boot Fracht B hinüberbringen. |
| 25–25 | sol | Dann. |
| 26–27 | cheeety qokedy | Ohne Fracht B zurückfahren (Gegenvariante: mit dieser Fracht). |
| 28–29 | qoky saiin | Fracht C zum jeweils anderen Ufer übersetzen. |
| 30–32 | solkeedy qokedy otedy | Mit Fracht B zurückfahren. |
| 33–33 | sol | Dann. |
| 34–39 | chedy lkedy qokchedy qokedy chckhdy sar | Fracht A wäre mit Fracht B unbeaufsichtigt ein gefährliches Paar. |
| 40–41 | schedair otchedy | Entsprechend für das andere/erste Frachtstück; erstes/zweites Paarargument ersetzen. |
| 42–44 | qokeedy chedain chedy | Als Nächstes Fracht A hinüberbringen. |
| 45–46 | qotedaiin otaiin | Das zuletzt beförderte Frachtstück dort lassen (Zielufer/gegenwärtiges Ufer). |
| 47–48 | otedy ldy | Allein zurückfahren. |
| 49–53 | tchedy qotedy qokal shedy qokedy | Abschließend fahren Begleitperson und Fracht B gemeinsam hinüber. |
| 54–57 | shecthedy shecthy otor chedy | Die zuletzt beförderte Fracht befindet sich nun bei den übrigen, darunter Fracht A. |
| 58–63 | soiiin checthy chety otaiin olsaly shedy | Somit sind alle unversehrt dort, begleitet von der Begleitperson. |

| Variante | Einstellungen | Gefährliche Paare | Die sieben tatsächlichen Ladungen | Aufgelöste Bezüge |
|---|---|---|---|---|
| V00 | exclude=EXCLUDING, first=FIRST, other=OTHER, there=GOAL, copy=FIRST | Fracht C + Fracht B; Fracht B + Fracht A | Fracht B → leer → Fracht C → Fracht B → Fracht A → leer → Fracht B | S12: OTHER_CARGO → Fracht C |
| V02 | exclude=EXCLUDING, first=FIRST, other=OTHER, there=CURRENT, copy=FIRST | Fracht C + Fracht B; Fracht B + Fracht A | Fracht B → leer → Fracht C → Fracht B → Fracht A → leer → Fracht B | S12: OTHER_CARGO → Fracht C |
| V08 | exclude=EXCLUDING, first=RECENT, other=OTHER, there=GOAL, copy=FIRST | Fracht C + Fracht B; Fracht B + Fracht A | Fracht B → leer → Fracht C → Fracht B → Fracht A → leer → Fracht B | S12: OTHER_CARGO → Fracht C |
| V10 | exclude=EXCLUDING, first=RECENT, other=OTHER, there=CURRENT, copy=FIRST | Fracht C + Fracht B; Fracht B + Fracht A | Fracht B → leer → Fracht C → Fracht B → Fracht A → leer → Fracht B | S12: OTHER_CARGO → Fracht C |

Alle aufgeführten Pfade erreichen das Ziel ohne physischen Widerspruch, falsche Zustandsbehauptung oder unbeaufsichtigtes Gefahrpaar. Das bedeutet Konsistenz unter den angenommenen Regeln; es bedeutet keine unabhängige Bedeutungsbestätigung.

### FUNCTIONAL Karte 912

Kohärente Bezugseinstellungen: [0, 2, 8, 10]. Alle übrigen der 32 Varianten widersprechen mindestens einer registrierten Folge; ihre vollständigen Ergebnisse stehen in FAMILY_FUNCTIONAL.json.

| Form | Bedingte Terminalrolle |
|---|---|
| chckhdy | WOULD_BE |
| checthy | ALL |
| ched | WITHOUT_AGENT |
| chedain | NEXT |
| chedy | W |
| cheeety | RETURN_EXCLUDING |
| chety | UNHARMED |
| dal | BESIDES |
| lchedy | W |
| ldy | ALONE |
| lkedy | PAIRED_WITH |
| ockhey | FORBIDDEN |
| olsaly | ATTENDED_BY |
| opshedy | HOME |
| otaiin | THERE |
| otchedy | OTHER_CARGO |
| otedy | RETURN |
| otor | COLOC |
| otshdy | GOAL |
| pdalshdy | INIT |
| qetal | AT_MOST_ONE |
| qokal | TRAVEL_TOGETHER |
| qokchedy | UNATTENDED |
| qokedol | FAR_BANK |
| qokedy | C |
| qokeedy | CONVEY_OUT |
| qokeey | TAKE_OUT |
| qoky | FERRY |
| qotedaiin | LEAVE |
| qotedy | OUTWARD |
| qoteedy | B |
| saiin | G |
| sain | WHEN |
| sar | UNSAFE |
| schedair | LIKEWISE |
| shdy | WITHOUT_HARM |
| shecthedy | JOINING_RESULT |
| shecthy | REST_CARGO |
| shedaiin | PAIRS |
| shedy | M |
| shey | EXAMPLE |
| shocphedy | CARGOS |
| soiiin | THUS |
| sol | THEN |
| soldy | HARM |
| solkeedy | WITH_TRIP |
| tchedy | FINALLY |

| Gruppen (einsbasiert) | Vollständiger Wortlaut | Bedingte Lesung |
|---|---|---|
| 1–5 | pdalshdy shocphedy otor shedy opshedy | Die drei Frachtstücke befinden sich mit der Begleitperson am Ausgangsufer. |
| 6–9 | otshdy qokedol shdy soldy | Ziel ist das gegenüberliegende Ufer ohne Schaden. |
| 10–15 | sar shedaiin ockhey sain ched shedy | Gefährliche Paare dürfen nicht ohne Begleitperson zusammenbleiben. |
| 16–20 | qetal dal shedy shey lchedy | Höchstens ein Frachtstück neben der Begleitperson; Beispiel: Fracht A. |
| 21–24 | solkeedy qoteedy qokeey qokedy | Mit dem Boot Fracht C hinüberbringen. |
| 25–25 | sol | Dann. |
| 26–27 | cheeety qokedy | Ohne Fracht C zurückfahren (Gegenvariante: mit dieser Fracht). |
| 28–29 | qoky saiin | Fracht B zum jeweils anderen Ufer übersetzen. |
| 30–32 | solkeedy qokedy otedy | Mit Fracht C zurückfahren. |
| 33–33 | sol | Dann. |
| 34–39 | chedy lkedy qokchedy qokedy chckhdy sar | Fracht A wäre mit Fracht C unbeaufsichtigt ein gefährliches Paar. |
| 40–41 | schedair otchedy | Entsprechend für das andere/erste Frachtstück; erstes/zweites Paarargument ersetzen. |
| 42–44 | qokeedy chedain chedy | Als Nächstes Fracht A hinüberbringen. |
| 45–46 | qotedaiin otaiin | Das zuletzt beförderte Frachtstück dort lassen (Zielufer/gegenwärtiges Ufer). |
| 47–48 | otedy ldy | Allein zurückfahren. |
| 49–53 | tchedy qotedy qokal shedy qokedy | Abschließend fahren Begleitperson und Fracht C gemeinsam hinüber. |
| 54–57 | shecthedy shecthy otor chedy | Die zuletzt beförderte Fracht befindet sich nun bei den übrigen, darunter Fracht A. |
| 58–63 | soiiin checthy chety otaiin olsaly shedy | Somit sind alle unversehrt dort, begleitet von der Begleitperson. |

| Variante | Einstellungen | Gefährliche Paare | Die sieben tatsächlichen Ladungen | Aufgelöste Bezüge |
|---|---|---|---|---|
| V00 | exclude=EXCLUDING, first=FIRST, other=OTHER, there=GOAL, copy=FIRST | Fracht C + Fracht B; Fracht C + Fracht A | Fracht C → leer → Fracht B → Fracht C → Fracht A → leer → Fracht C | S12: OTHER_CARGO → Fracht B |
| V02 | exclude=EXCLUDING, first=FIRST, other=OTHER, there=CURRENT, copy=FIRST | Fracht C + Fracht B; Fracht C + Fracht A | Fracht C → leer → Fracht B → Fracht C → Fracht A → leer → Fracht C | S12: OTHER_CARGO → Fracht B |
| V08 | exclude=EXCLUDING, first=RECENT, other=OTHER, there=GOAL, copy=FIRST | Fracht C + Fracht B; Fracht C + Fracht A | Fracht C → leer → Fracht B → Fracht C → Fracht A → leer → Fracht C | S12: OTHER_CARGO → Fracht B |
| V10 | exclude=EXCLUDING, first=RECENT, other=OTHER, there=CURRENT, copy=FIRST | Fracht C + Fracht B; Fracht C + Fracht A | Fracht C → leer → Fracht B → Fracht C → Fracht A → leer → Fracht C | S12: OTHER_CARGO → Fracht B |

Alle aufgeführten Pfade erreichen das Ziel ohne physischen Widerspruch, falsche Zustandsbehauptung oder unbeaufsichtigtes Gefahrpaar. Das bedeutet Konsistenz unter den angenommenen Regeln; es bedeutet keine unabhängige Bedeutungsbestätigung.

### FUNCTIONAL Karte 913

Kohärente Bezugseinstellungen: [0, 2, 8, 10]. Alle übrigen der 32 Varianten widersprechen mindestens einer registrierten Folge; ihre vollständigen Ergebnisse stehen in FAMILY_FUNCTIONAL.json.

| Form | Bedingte Terminalrolle |
|---|---|
| chckhdy | WOULD_BE |
| checthy | ALL |
| ched | WITHOUT_AGENT |
| chedain | NEXT |
| chedy | W |
| cheeety | RETURN_EXCLUDING |
| chety | UNHARMED |
| dal | BESIDES |
| lchedy | C |
| ldy | ALONE |
| lkedy | PAIRED_WITH |
| ockhey | FORBIDDEN |
| olsaly | ATTENDED_BY |
| opshedy | HOME |
| otaiin | THERE |
| otchedy | OTHER_CARGO |
| otedy | RETURN |
| otor | COLOC |
| otshdy | GOAL |
| pdalshdy | INIT |
| qetal | AT_MOST_ONE |
| qokal | TRAVEL_TOGETHER |
| qokchedy | UNATTENDED |
| qokedol | FAR_BANK |
| qokedy | C |
| qokeedy | CONVEY_OUT |
| qokeey | TAKE_OUT |
| qoky | FERRY |
| qotedaiin | LEAVE |
| qotedy | OUTWARD |
| qoteedy | B |
| saiin | G |
| sain | WHEN |
| sar | UNSAFE |
| schedair | LIKEWISE |
| shdy | WITHOUT_HARM |
| shecthedy | JOINING_RESULT |
| shecthy | REST_CARGO |
| shedaiin | PAIRS |
| shedy | M |
| shey | EXAMPLE |
| shocphedy | CARGOS |
| soiiin | THUS |
| sol | THEN |
| soldy | HARM |
| solkeedy | WITH_TRIP |
| tchedy | FINALLY |

| Gruppen (einsbasiert) | Vollständiger Wortlaut | Bedingte Lesung |
|---|---|---|
| 1–5 | pdalshdy shocphedy otor shedy opshedy | Die drei Frachtstücke befinden sich mit der Begleitperson am Ausgangsufer. |
| 6–9 | otshdy qokedol shdy soldy | Ziel ist das gegenüberliegende Ufer ohne Schaden. |
| 10–15 | sar shedaiin ockhey sain ched shedy | Gefährliche Paare dürfen nicht ohne Begleitperson zusammenbleiben. |
| 16–20 | qetal dal shedy shey lchedy | Höchstens ein Frachtstück neben der Begleitperson; Beispiel: Fracht C. |
| 21–24 | solkeedy qoteedy qokeey qokedy | Mit dem Boot Fracht C hinüberbringen. |
| 25–25 | sol | Dann. |
| 26–27 | cheeety qokedy | Ohne Fracht C zurückfahren (Gegenvariante: mit dieser Fracht). |
| 28–29 | qoky saiin | Fracht B zum jeweils anderen Ufer übersetzen. |
| 30–32 | solkeedy qokedy otedy | Mit Fracht C zurückfahren. |
| 33–33 | sol | Dann. |
| 34–39 | chedy lkedy qokchedy qokedy chckhdy sar | Fracht A wäre mit Fracht C unbeaufsichtigt ein gefährliches Paar. |
| 40–41 | schedair otchedy | Entsprechend für das andere/erste Frachtstück; erstes/zweites Paarargument ersetzen. |
| 42–44 | qokeedy chedain chedy | Als Nächstes Fracht A hinüberbringen. |
| 45–46 | qotedaiin otaiin | Das zuletzt beförderte Frachtstück dort lassen (Zielufer/gegenwärtiges Ufer). |
| 47–48 | otedy ldy | Allein zurückfahren. |
| 49–53 | tchedy qotedy qokal shedy qokedy | Abschließend fahren Begleitperson und Fracht C gemeinsam hinüber. |
| 54–57 | shecthedy shecthy otor chedy | Die zuletzt beförderte Fracht befindet sich nun bei den übrigen, darunter Fracht A. |
| 58–63 | soiiin checthy chety otaiin olsaly shedy | Somit sind alle unversehrt dort, begleitet von der Begleitperson. |

| Variante | Einstellungen | Gefährliche Paare | Die sieben tatsächlichen Ladungen | Aufgelöste Bezüge |
|---|---|---|---|---|
| V00 | exclude=EXCLUDING, first=FIRST, other=OTHER, there=GOAL, copy=FIRST | Fracht C + Fracht B; Fracht C + Fracht A | Fracht C → leer → Fracht B → Fracht C → Fracht A → leer → Fracht C | S12: OTHER_CARGO → Fracht B |
| V02 | exclude=EXCLUDING, first=FIRST, other=OTHER, there=CURRENT, copy=FIRST | Fracht C + Fracht B; Fracht C + Fracht A | Fracht C → leer → Fracht B → Fracht C → Fracht A → leer → Fracht C | S12: OTHER_CARGO → Fracht B |
| V08 | exclude=EXCLUDING, first=RECENT, other=OTHER, there=GOAL, copy=FIRST | Fracht C + Fracht B; Fracht C + Fracht A | Fracht C → leer → Fracht B → Fracht C → Fracht A → leer → Fracht C | S12: OTHER_CARGO → Fracht B |
| V10 | exclude=EXCLUDING, first=RECENT, other=OTHER, there=CURRENT, copy=FIRST | Fracht C + Fracht B; Fracht C + Fracht A | Fracht C → leer → Fracht B → Fracht C → Fracht A → leer → Fracht C | S12: OTHER_CARGO → Fracht B |

Alle aufgeführten Pfade erreichen das Ziel ohne physischen Widerspruch, falsche Zustandsbehauptung oder unbeaufsichtigtes Gefahrpaar. Das bedeutet Konsistenz unter den angenommenen Regeln; es bedeutet keine unabhängige Bedeutungsbestätigung.

### FUNCTIONAL Karte 914

Kohärente Bezugseinstellungen: [0, 2, 4, 6, 8, 10, 12, 14]. Alle übrigen der 32 Varianten widersprechen mindestens einer registrierten Folge; ihre vollständigen Ergebnisse stehen in FAMILY_FUNCTIONAL.json.

| Form | Bedingte Terminalrolle |
|---|---|
| chckhdy | WOULD_BE |
| checthy | ALL |
| ched | WITHOUT_AGENT |
| chedain | NEXT |
| chedy | W |
| cheeety | RETURN_EXCLUDING |
| chety | UNHARMED |
| dal | BESIDES |
| lchedy | G |
| ldy | ALONE |
| lkedy | PAIRED_WITH |
| ockhey | FORBIDDEN |
| olsaly | ATTENDED_BY |
| opshedy | HOME |
| otaiin | THERE |
| otchedy | OTHER_CARGO |
| otedy | RETURN |
| otor | COLOC |
| otshdy | GOAL |
| pdalshdy | INIT |
| qetal | AT_MOST_ONE |
| qokal | TRAVEL_TOGETHER |
| qokchedy | UNATTENDED |
| qokedol | FAR_BANK |
| qokedy | C |
| qokeedy | CONVEY_OUT |
| qokeey | TAKE_OUT |
| qoky | FERRY |
| qotedaiin | LEAVE |
| qotedy | OUTWARD |
| qoteedy | B |
| saiin | G |
| sain | WHEN |
| sar | UNSAFE |
| schedair | LIKEWISE |
| shdy | WITHOUT_HARM |
| shecthedy | JOINING_RESULT |
| shecthy | REST_CARGO |
| shedaiin | PAIRS |
| shedy | M |
| shey | EXAMPLE |
| shocphedy | CARGOS |
| soiiin | THUS |
| sol | THEN |
| soldy | HARM |
| solkeedy | WITH_TRIP |
| tchedy | FINALLY |

| Gruppen (einsbasiert) | Vollständiger Wortlaut | Bedingte Lesung |
|---|---|---|
| 1–5 | pdalshdy shocphedy otor shedy opshedy | Die drei Frachtstücke befinden sich mit der Begleitperson am Ausgangsufer. |
| 6–9 | otshdy qokedol shdy soldy | Ziel ist das gegenüberliegende Ufer ohne Schaden. |
| 10–15 | sar shedaiin ockhey sain ched shedy | Gefährliche Paare dürfen nicht ohne Begleitperson zusammenbleiben. |
| 16–20 | qetal dal shedy shey lchedy | Höchstens ein Frachtstück neben der Begleitperson; Beispiel: Fracht B. |
| 21–24 | solkeedy qoteedy qokeey qokedy | Mit dem Boot Fracht C hinüberbringen. |
| 25–25 | sol | Dann. |
| 26–27 | cheeety qokedy | Ohne Fracht C zurückfahren (Gegenvariante: mit dieser Fracht). |
| 28–29 | qoky saiin | Fracht B zum jeweils anderen Ufer übersetzen. |
| 30–32 | solkeedy qokedy otedy | Mit Fracht C zurückfahren. |
| 33–33 | sol | Dann. |
| 34–39 | chedy lkedy qokchedy qokedy chckhdy sar | Fracht A wäre mit Fracht C unbeaufsichtigt ein gefährliches Paar. |
| 40–41 | schedair otchedy | Entsprechend für das andere/erste Frachtstück; erstes/zweites Paarargument ersetzen. |
| 42–44 | qokeedy chedain chedy | Als Nächstes Fracht A hinüberbringen. |
| 45–46 | qotedaiin otaiin | Das zuletzt beförderte Frachtstück dort lassen (Zielufer/gegenwärtiges Ufer). |
| 47–48 | otedy ldy | Allein zurückfahren. |
| 49–53 | tchedy qotedy qokal shedy qokedy | Abschließend fahren Begleitperson und Fracht C gemeinsam hinüber. |
| 54–57 | shecthedy shecthy otor chedy | Die zuletzt beförderte Fracht befindet sich nun bei den übrigen, darunter Fracht A. |
| 58–63 | soiiin checthy chety otaiin olsaly shedy | Somit sind alle unversehrt dort, begleitet von der Begleitperson. |

| Variante | Einstellungen | Gefährliche Paare | Die sieben tatsächlichen Ladungen | Aufgelöste Bezüge |
|---|---|---|---|---|
| V00 | exclude=EXCLUDING, first=FIRST, other=OTHER, there=GOAL, copy=FIRST | Fracht C + Fracht B; Fracht C + Fracht A | Fracht C → leer → Fracht B → Fracht C → Fracht A → leer → Fracht C | S12: OTHER_CARGO → Fracht B |
| V02 | exclude=EXCLUDING, first=FIRST, other=OTHER, there=CURRENT, copy=FIRST | Fracht C + Fracht B; Fracht C + Fracht A | Fracht C → leer → Fracht B → Fracht C → Fracht A → leer → Fracht C | S12: OTHER_CARGO → Fracht B |
| V04 | exclude=EXCLUDING, first=FIRST, other=FIRST, there=GOAL, copy=FIRST | Fracht C + Fracht B; Fracht C + Fracht A | Fracht C → leer → Fracht B → Fracht C → Fracht A → leer → Fracht C | S12: OTHER_CARGO → Fracht B |
| V06 | exclude=EXCLUDING, first=FIRST, other=FIRST, there=CURRENT, copy=FIRST | Fracht C + Fracht B; Fracht C + Fracht A | Fracht C → leer → Fracht B → Fracht C → Fracht A → leer → Fracht C | S12: OTHER_CARGO → Fracht B |
| V08 | exclude=EXCLUDING, first=RECENT, other=OTHER, there=GOAL, copy=FIRST | Fracht C + Fracht B; Fracht C + Fracht A | Fracht C → leer → Fracht B → Fracht C → Fracht A → leer → Fracht C | S12: OTHER_CARGO → Fracht B |
| V10 | exclude=EXCLUDING, first=RECENT, other=OTHER, there=CURRENT, copy=FIRST | Fracht C + Fracht B; Fracht C + Fracht A | Fracht C → leer → Fracht B → Fracht C → Fracht A → leer → Fracht C | S12: OTHER_CARGO → Fracht B |
| V12 | exclude=EXCLUDING, first=RECENT, other=FIRST, there=GOAL, copy=FIRST | Fracht C + Fracht B; Fracht C + Fracht A | Fracht C → leer → Fracht B → Fracht C → Fracht A → leer → Fracht C | S12: OTHER_CARGO → Fracht B |
| V14 | exclude=EXCLUDING, first=RECENT, other=FIRST, there=CURRENT, copy=FIRST | Fracht C + Fracht B; Fracht C + Fracht A | Fracht C → leer → Fracht B → Fracht C → Fracht A → leer → Fracht C | S12: OTHER_CARGO → Fracht B |

Alle aufgeführten Pfade erreichen das Ziel ohne physischen Widerspruch, falsche Zustandsbehauptung oder unbeaufsichtigtes Gefahrpaar. Das bedeutet Konsistenz unter den angenommenen Regeln; es bedeutet keine unabhängige Bedeutungsbestätigung.

### FUNCTIONAL Karte 917

Kohärente Bezugseinstellungen: [0, 2, 4, 6]. Alle übrigen der 32 Varianten widersprechen mindestens einer registrierten Folge; ihre vollständigen Ergebnisse stehen in FAMILY_FUNCTIONAL.json.

| Form | Bedingte Terminalrolle |
|---|---|
| chckhdy | WOULD_BE |
| checthy | ALL |
| ched | WITHOUT_AGENT |
| chedain | NEXT |
| chedy | W |
| cheeety | RETURN_EXCLUDING |
| chety | UNHARMED |
| dal | BESIDES |
| lchedy | G |
| ldy | ALONE |
| lkedy | PAIRED_WITH |
| ockhey | FORBIDDEN |
| olsaly | ATTENDED_BY |
| opshedy | HOME |
| otaiin | THERE |
| otchedy | OTHER_CARGO |
| otedy | RETURN |
| otor | COLOC |
| otshdy | GOAL |
| pdalshdy | INIT |
| qetal | AT_MOST_ONE |
| qokal | TRAVEL_TOGETHER |
| qokchedy | UNATTENDED |
| qokedol | FAR_BANK |
| qokedy | C |
| qokeedy | CONVEY_OUT |
| qokeey | TAKE_OUT |
| qoky | FERRY |
| qotedaiin | LEAVE |
| qotedy | OUTWARD |
| qoteedy | B |
| saiin | FIRST_CARGO |
| sain | WHEN |
| sar | UNSAFE |
| schedair | LIKEWISE |
| shdy | WITHOUT_HARM |
| shecthedy | JOINING_RESULT |
| shecthy | REST_CARGO |
| shedaiin | PAIRS |
| shedy | M |
| shey | EXAMPLE |
| shocphedy | CARGOS |
| soiiin | THUS |
| sol | THEN |
| soldy | HARM |
| solkeedy | WITH_TRIP |
| tchedy | FINALLY |

| Gruppen (einsbasiert) | Vollständiger Wortlaut | Bedingte Lesung |
|---|---|---|
| 1–5 | pdalshdy shocphedy otor shedy opshedy | Die drei Frachtstücke befinden sich mit der Begleitperson am Ausgangsufer. |
| 6–9 | otshdy qokedol shdy soldy | Ziel ist das gegenüberliegende Ufer ohne Schaden. |
| 10–15 | sar shedaiin ockhey sain ched shedy | Gefährliche Paare dürfen nicht ohne Begleitperson zusammenbleiben. |
| 16–20 | qetal dal shedy shey lchedy | Höchstens ein Frachtstück neben der Begleitperson; Beispiel: Fracht B. |
| 21–24 | solkeedy qoteedy qokeey qokedy | Mit dem Boot Fracht C hinüberbringen. |
| 25–25 | sol | Dann. |
| 26–27 | cheeety qokedy | Ohne Fracht C zurückfahren (Gegenvariante: mit dieser Fracht). |
| 28–29 | qoky saiin | zuerst/zuletzt erwähnte Fracht zum jeweils anderen Ufer übersetzen. |
| 30–32 | solkeedy qokedy otedy | Mit Fracht C zurückfahren. |
| 33–33 | sol | Dann. |
| 34–39 | chedy lkedy qokchedy qokedy chckhdy sar | Fracht A wäre mit Fracht C unbeaufsichtigt ein gefährliches Paar. |
| 40–41 | schedair otchedy | Entsprechend für das andere/erste Frachtstück; erstes/zweites Paarargument ersetzen. |
| 42–44 | qokeedy chedain chedy | Als Nächstes Fracht A hinüberbringen. |
| 45–46 | qotedaiin otaiin | Das zuletzt beförderte Frachtstück dort lassen (Zielufer/gegenwärtiges Ufer). |
| 47–48 | otedy ldy | Allein zurückfahren. |
| 49–53 | tchedy qotedy qokal shedy qokedy | Abschließend fahren Begleitperson und Fracht C gemeinsam hinüber. |
| 54–57 | shecthedy shecthy otor chedy | Die zuletzt beförderte Fracht befindet sich nun bei den übrigen, darunter Fracht A. |
| 58–63 | soiiin checthy chety otaiin olsaly shedy | Somit sind alle unversehrt dort, begleitet von der Begleitperson. |

| Variante | Einstellungen | Gefährliche Paare | Die sieben tatsächlichen Ladungen | Aufgelöste Bezüge |
|---|---|---|---|---|
| V00 | exclude=EXCLUDING, first=FIRST, other=OTHER, there=GOAL, copy=FIRST | Fracht C + Fracht B; Fracht C + Fracht A | Fracht C → leer → Fracht B → Fracht C → Fracht A → leer → Fracht C | S08: FIRST_CARGO → Fracht B; S12: OTHER_CARGO → Fracht B |
| V02 | exclude=EXCLUDING, first=FIRST, other=OTHER, there=CURRENT, copy=FIRST | Fracht C + Fracht B; Fracht C + Fracht A | Fracht C → leer → Fracht B → Fracht C → Fracht A → leer → Fracht C | S08: FIRST_CARGO → Fracht B; S12: OTHER_CARGO → Fracht B |
| V04 | exclude=EXCLUDING, first=FIRST, other=FIRST, there=GOAL, copy=FIRST | Fracht C + Fracht B; Fracht C + Fracht A | Fracht C → leer → Fracht B → Fracht C → Fracht A → leer → Fracht C | S08: FIRST_CARGO → Fracht B; S12: OTHER_CARGO → Fracht B |
| V06 | exclude=EXCLUDING, first=FIRST, other=FIRST, there=CURRENT, copy=FIRST | Fracht C + Fracht B; Fracht C + Fracht A | Fracht C → leer → Fracht B → Fracht C → Fracht A → leer → Fracht C | S08: FIRST_CARGO → Fracht B; S12: OTHER_CARGO → Fracht B |

Alle aufgeführten Pfade erreichen das Ziel ohne physischen Widerspruch, falsche Zustandsbehauptung oder unbeaufsichtigtes Gefahrpaar. Das bedeutet Konsistenz unter den angenommenen Regeln; es bedeutet keine unabhängige Bedeutungsbestätigung.

### FUNCTIONAL Karte 965

Kohärente Bezugseinstellungen: [4, 6, 12, 14]. Alle übrigen der 32 Varianten widersprechen mindestens einer registrierten Folge; ihre vollständigen Ergebnisse stehen in FAMILY_FUNCTIONAL.json.

| Form | Bedingte Terminalrolle |
|---|---|
| chckhdy | WOULD_BE |
| checthy | ALL |
| ched | WITHOUT_AGENT |
| chedain | NEXT |
| chedy | W |
| cheeety | RETURN_EXCLUDING |
| chety | UNHARMED |
| dal | BESIDES |
| lchedy | G |
| ldy | ALONE |
| lkedy | PAIRED_WITH |
| ockhey | FORBIDDEN |
| olsaly | ATTENDED_BY |
| opshedy | HOME |
| otaiin | THERE |
| otchedy | OTHER_CARGO |
| otedy | RETURN |
| otor | COLOC |
| otshdy | GOAL |
| pdalshdy | INIT |
| qetal | AT_MOST_ONE |
| qokal | TRAVEL_TOGETHER |
| qokchedy | UNATTENDED |
| qokedol | FAR_BANK |
| qokedy | C |
| qokeedy | CONVEY_OUT |
| qokeey | TAKE_OUT |
| qoky | FERRY |
| qotedaiin | LEAVE |
| qotedy | OUTWARD |
| qoteedy | B |
| saiin | OTHER_CARGO |
| sain | WHEN |
| sar | UNSAFE |
| schedair | LIKEWISE |
| shdy | WITHOUT_HARM |
| shecthedy | JOINING_RESULT |
| shecthy | REST_CARGO |
| shedaiin | PAIRS |
| shedy | M |
| shey | EXAMPLE |
| shocphedy | CARGOS |
| soiiin | THUS |
| sol | THEN |
| soldy | HARM |
| solkeedy | WITH_TRIP |
| tchedy | FINALLY |

| Gruppen (einsbasiert) | Vollständiger Wortlaut | Bedingte Lesung |
|---|---|---|
| 1–5 | pdalshdy shocphedy otor shedy opshedy | Die drei Frachtstücke befinden sich mit der Begleitperson am Ausgangsufer. |
| 6–9 | otshdy qokedol shdy soldy | Ziel ist das gegenüberliegende Ufer ohne Schaden. |
| 10–15 | sar shedaiin ockhey sain ched shedy | Gefährliche Paare dürfen nicht ohne Begleitperson zusammenbleiben. |
| 16–20 | qetal dal shedy shey lchedy | Höchstens ein Frachtstück neben der Begleitperson; Beispiel: Fracht B. |
| 21–24 | solkeedy qoteedy qokeey qokedy | Mit dem Boot Fracht C hinüberbringen. |
| 25–25 | sol | Dann. |
| 26–27 | cheeety qokedy | Ohne Fracht C zurückfahren (Gegenvariante: mit dieser Fracht). |
| 28–29 | qoky saiin | andere/erste Fracht zum jeweils anderen Ufer übersetzen. |
| 30–32 | solkeedy qokedy otedy | Mit Fracht C zurückfahren. |
| 33–33 | sol | Dann. |
| 34–39 | chedy lkedy qokchedy qokedy chckhdy sar | Fracht A wäre mit Fracht C unbeaufsichtigt ein gefährliches Paar. |
| 40–41 | schedair otchedy | Entsprechend für das andere/erste Frachtstück; erstes/zweites Paarargument ersetzen. |
| 42–44 | qokeedy chedain chedy | Als Nächstes Fracht A hinüberbringen. |
| 45–46 | qotedaiin otaiin | Das zuletzt beförderte Frachtstück dort lassen (Zielufer/gegenwärtiges Ufer). |
| 47–48 | otedy ldy | Allein zurückfahren. |
| 49–53 | tchedy qotedy qokal shedy qokedy | Abschließend fahren Begleitperson und Fracht C gemeinsam hinüber. |
| 54–57 | shecthedy shecthy otor chedy | Die zuletzt beförderte Fracht befindet sich nun bei den übrigen, darunter Fracht A. |
| 58–63 | soiiin checthy chety otaiin olsaly shedy | Somit sind alle unversehrt dort, begleitet von der Begleitperson. |

| Variante | Einstellungen | Gefährliche Paare | Die sieben tatsächlichen Ladungen | Aufgelöste Bezüge |
|---|---|---|---|---|
| V04 | exclude=EXCLUDING, first=FIRST, other=FIRST, there=GOAL, copy=FIRST | Fracht C + Fracht B; Fracht C + Fracht A | Fracht C → leer → Fracht B → Fracht C → Fracht A → leer → Fracht C | S08: OTHER_CARGO → Fracht B; S12: OTHER_CARGO → Fracht B |
| V06 | exclude=EXCLUDING, first=FIRST, other=FIRST, there=CURRENT, copy=FIRST | Fracht C + Fracht B; Fracht C + Fracht A | Fracht C → leer → Fracht B → Fracht C → Fracht A → leer → Fracht C | S08: OTHER_CARGO → Fracht B; S12: OTHER_CARGO → Fracht B |
| V12 | exclude=EXCLUDING, first=RECENT, other=FIRST, there=GOAL, copy=FIRST | Fracht C + Fracht B; Fracht C + Fracht A | Fracht C → leer → Fracht B → Fracht C → Fracht A → leer → Fracht C | S08: OTHER_CARGO → Fracht B; S12: OTHER_CARGO → Fracht B |
| V14 | exclude=EXCLUDING, first=RECENT, other=FIRST, there=CURRENT, copy=FIRST | Fracht C + Fracht B; Fracht C + Fracht A | Fracht C → leer → Fracht B → Fracht C → Fracht A → leer → Fracht C | S08: OTHER_CARGO → Fracht B; S12: OTHER_CARGO → Fracht B |

Alle aufgeführten Pfade erreichen das Ziel ohne physischen Widerspruch, falsche Zustandsbehauptung oder unbeaufsichtigtes Gefahrpaar. Das bedeutet Konsistenz unter den angenommenen Regeln; es bedeutet keine unabhängige Bedeutungsbestätigung.

### FUNCTIONAL Karte 1110

Kohärente Bezugseinstellungen: [4, 6, 12, 14]. Alle übrigen der 32 Varianten widersprechen mindestens einer registrierten Folge; ihre vollständigen Ergebnisse stehen in FAMILY_FUNCTIONAL.json.

| Form | Bedingte Terminalrolle |
|---|---|
| chckhdy | WOULD_BE |
| checthy | ALL |
| ched | WITHOUT_AGENT |
| chedain | NEXT |
| chedy | G |
| cheeety | RETURN_EXCLUDING |
| chety | UNHARMED |
| dal | BESIDES |
| lchedy | W |
| ldy | ALONE |
| lkedy | PAIRED_WITH |
| ockhey | FORBIDDEN |
| olsaly | ATTENDED_BY |
| opshedy | HOME |
| otaiin | THERE |
| otchedy | OTHER_CARGO |
| otedy | RETURN |
| otor | COLOC |
| otshdy | GOAL |
| pdalshdy | INIT |
| qetal | AT_MOST_ONE |
| qokal | TRAVEL_TOGETHER |
| qokchedy | UNATTENDED |
| qokedol | FAR_BANK |
| qokedy | C |
| qokeedy | CONVEY_OUT |
| qokeey | TAKE_OUT |
| qoky | FERRY |
| qotedaiin | LEAVE |
| qotedy | OUTWARD |
| qoteedy | B |
| saiin | OTHER_CARGO |
| sain | WHEN |
| sar | UNSAFE |
| schedair | LIKEWISE |
| shdy | WITHOUT_HARM |
| shecthedy | JOINING_RESULT |
| shecthy | REST_CARGO |
| shedaiin | PAIRS |
| shedy | M |
| shey | EXAMPLE |
| shocphedy | CARGOS |
| soiiin | THUS |
| sol | THEN |
| soldy | HARM |
| solkeedy | WITH_TRIP |
| tchedy | FINALLY |

| Gruppen (einsbasiert) | Vollständiger Wortlaut | Bedingte Lesung |
|---|---|---|
| 1–5 | pdalshdy shocphedy otor shedy opshedy | Die drei Frachtstücke befinden sich mit der Begleitperson am Ausgangsufer. |
| 6–9 | otshdy qokedol shdy soldy | Ziel ist das gegenüberliegende Ufer ohne Schaden. |
| 10–15 | sar shedaiin ockhey sain ched shedy | Gefährliche Paare dürfen nicht ohne Begleitperson zusammenbleiben. |
| 16–20 | qetal dal shedy shey lchedy | Höchstens ein Frachtstück neben der Begleitperson; Beispiel: Fracht A. |
| 21–24 | solkeedy qoteedy qokeey qokedy | Mit dem Boot Fracht C hinüberbringen. |
| 25–25 | sol | Dann. |
| 26–27 | cheeety qokedy | Ohne Fracht C zurückfahren (Gegenvariante: mit dieser Fracht). |
| 28–29 | qoky saiin | andere/erste Fracht zum jeweils anderen Ufer übersetzen. |
| 30–32 | solkeedy qokedy otedy | Mit Fracht C zurückfahren. |
| 33–33 | sol | Dann. |
| 34–39 | chedy lkedy qokchedy qokedy chckhdy sar | Fracht B wäre mit Fracht C unbeaufsichtigt ein gefährliches Paar. |
| 40–41 | schedair otchedy | Entsprechend für das andere/erste Frachtstück; erstes/zweites Paarargument ersetzen. |
| 42–44 | qokeedy chedain chedy | Als Nächstes Fracht B hinüberbringen. |
| 45–46 | qotedaiin otaiin | Das zuletzt beförderte Frachtstück dort lassen (Zielufer/gegenwärtiges Ufer). |
| 47–48 | otedy ldy | Allein zurückfahren. |
| 49–53 | tchedy qotedy qokal shedy qokedy | Abschließend fahren Begleitperson und Fracht C gemeinsam hinüber. |
| 54–57 | shecthedy shecthy otor chedy | Die zuletzt beförderte Fracht befindet sich nun bei den übrigen, darunter Fracht B. |
| 58–63 | soiiin checthy chety otaiin olsaly shedy | Somit sind alle unversehrt dort, begleitet von der Begleitperson. |

| Variante | Einstellungen | Gefährliche Paare | Die sieben tatsächlichen Ladungen | Aufgelöste Bezüge |
|---|---|---|---|---|
| V04 | exclude=EXCLUDING, first=FIRST, other=FIRST, there=GOAL, copy=FIRST | Fracht C + Fracht B; Fracht C + Fracht A | Fracht C → leer → Fracht A → Fracht C → Fracht B → leer → Fracht C | S08: OTHER_CARGO → Fracht A; S12: OTHER_CARGO → Fracht A |
| V06 | exclude=EXCLUDING, first=FIRST, other=FIRST, there=CURRENT, copy=FIRST | Fracht C + Fracht B; Fracht C + Fracht A | Fracht C → leer → Fracht A → Fracht C → Fracht B → leer → Fracht C | S08: OTHER_CARGO → Fracht A; S12: OTHER_CARGO → Fracht A |
| V12 | exclude=EXCLUDING, first=RECENT, other=FIRST, there=GOAL, copy=FIRST | Fracht C + Fracht B; Fracht C + Fracht A | Fracht C → leer → Fracht A → Fracht C → Fracht B → leer → Fracht C | S08: OTHER_CARGO → Fracht A; S12: OTHER_CARGO → Fracht A |
| V14 | exclude=EXCLUDING, first=RECENT, other=FIRST, there=CURRENT, copy=FIRST | Fracht C + Fracht B; Fracht C + Fracht A | Fracht C → leer → Fracht A → Fracht C → Fracht B → leer → Fracht C | S08: OTHER_CARGO → Fracht A; S12: OTHER_CARGO → Fracht A |

Alle aufgeführten Pfade erreichen das Ziel ohne physischen Widerspruch, falsche Zustandsbehauptung oder unbeaufsichtigtes Gefahrpaar. Das bedeutet Konsistenz unter den angenommenen Regeln; es bedeutet keine unabhängige Bedeutungsbestätigung.

### FUNCTIONAL Karte 1127

Kohärente Bezugseinstellungen: [0, 2]. Alle übrigen der 32 Varianten widersprechen mindestens einer registrierten Folge; ihre vollständigen Ergebnisse stehen in FAMILY_FUNCTIONAL.json.

| Form | Bedingte Terminalrolle |
|---|---|
| chckhdy | WOULD_BE |
| checthy | ALL |
| ched | WITHOUT_AGENT |
| chedain | NEXT |
| chedy | FIRST_CARGO |
| cheeety | RETURN_EXCLUDING |
| chety | UNHARMED |
| dal | BESIDES |
| lchedy | G |
| ldy | ALONE |
| lkedy | PAIRED_WITH |
| ockhey | FORBIDDEN |
| olsaly | ATTENDED_BY |
| opshedy | HOME |
| otaiin | THERE |
| otchedy | OTHER_CARGO |
| otedy | RETURN |
| otor | COLOC |
| otshdy | GOAL |
| pdalshdy | INIT |
| qetal | AT_MOST_ONE |
| qokal | TRAVEL_TOGETHER |
| qokchedy | UNATTENDED |
| qokedol | FAR_BANK |
| qokedy | C |
| qokeedy | CONVEY_OUT |
| qokeey | TAKE_OUT |
| qoky | FERRY |
| qotedaiin | LEAVE |
| qotedy | OUTWARD |
| qoteedy | B |
| saiin | W |
| sain | WHEN |
| sar | UNSAFE |
| schedair | LIKEWISE |
| shdy | WITHOUT_HARM |
| shecthedy | JOINING_RESULT |
| shecthy | REST_CARGO |
| shedaiin | PAIRS |
| shedy | M |
| shey | EXAMPLE |
| shocphedy | CARGOS |
| soiiin | THUS |
| sol | THEN |
| soldy | HARM |
| solkeedy | WITH_TRIP |
| tchedy | FINALLY |

| Gruppen (einsbasiert) | Vollständiger Wortlaut | Bedingte Lesung |
|---|---|---|
| 1–5 | pdalshdy shocphedy otor shedy opshedy | Die drei Frachtstücke befinden sich mit der Begleitperson am Ausgangsufer. |
| 6–9 | otshdy qokedol shdy soldy | Ziel ist das gegenüberliegende Ufer ohne Schaden. |
| 10–15 | sar shedaiin ockhey sain ched shedy | Gefährliche Paare dürfen nicht ohne Begleitperson zusammenbleiben. |
| 16–20 | qetal dal shedy shey lchedy | Höchstens ein Frachtstück neben der Begleitperson; Beispiel: Fracht B. |
| 21–24 | solkeedy qoteedy qokeey qokedy | Mit dem Boot Fracht C hinüberbringen. |
| 25–25 | sol | Dann. |
| 26–27 | cheeety qokedy | Ohne Fracht C zurückfahren (Gegenvariante: mit dieser Fracht). |
| 28–29 | qoky saiin | Fracht A zum jeweils anderen Ufer übersetzen. |
| 30–32 | solkeedy qokedy otedy | Mit Fracht C zurückfahren. |
| 33–33 | sol | Dann. |
| 34–39 | chedy lkedy qokchedy qokedy chckhdy sar | zuerst/zuletzt erwähnte Fracht wäre mit Fracht C unbeaufsichtigt ein gefährliches Paar. |
| 40–41 | schedair otchedy | Entsprechend für das andere/erste Frachtstück; erstes/zweites Paarargument ersetzen. |
| 42–44 | qokeedy chedain chedy | Als Nächstes zuerst/zuletzt erwähnte Fracht hinüberbringen. |
| 45–46 | qotedaiin otaiin | Das zuletzt beförderte Frachtstück dort lassen (Zielufer/gegenwärtiges Ufer). |
| 47–48 | otedy ldy | Allein zurückfahren. |
| 49–53 | tchedy qotedy qokal shedy qokedy | Abschließend fahren Begleitperson und Fracht C gemeinsam hinüber. |
| 54–57 | shecthedy shecthy otor chedy | Die zuletzt beförderte Fracht befindet sich nun bei den übrigen, darunter zuerst/zuletzt erwähnte Fracht. |
| 58–63 | soiiin checthy chety otaiin olsaly shedy | Somit sind alle unversehrt dort, begleitet von der Begleitperson. |

| Variante | Einstellungen | Gefährliche Paare | Die sieben tatsächlichen Ladungen | Aufgelöste Bezüge |
|---|---|---|---|---|
| V00 | exclude=EXCLUDING, first=FIRST, other=OTHER, there=GOAL, copy=FIRST | Fracht C + Fracht B; Fracht C + Fracht A | Fracht C → leer → Fracht A → Fracht C → Fracht B → leer → Fracht C | S11: FIRST_CARGO → Fracht B; S12: OTHER_CARGO → Fracht A; S13: FIRST_CARGO → Fracht B; S17: FIRST_CARGO → Fracht B |
| V02 | exclude=EXCLUDING, first=FIRST, other=OTHER, there=CURRENT, copy=FIRST | Fracht C + Fracht B; Fracht C + Fracht A | Fracht C → leer → Fracht A → Fracht C → Fracht B → leer → Fracht C | S11: FIRST_CARGO → Fracht B; S12: OTHER_CARGO → Fracht A; S13: FIRST_CARGO → Fracht B; S17: FIRST_CARGO → Fracht B |

Alle aufgeführten Pfade erreichen das Ziel ohne physischen Widerspruch, falsche Zustandsbehauptung oder unbeaufsichtigtes Gefahrpaar. Das bedeutet Konsistenz unter den angenommenen Regeln; es bedeutet keine unabhängige Bedeutungsbestätigung.

### FUNCTIONAL Karte 1131

Kohärente Bezugseinstellungen: [0, 2, 8, 10]. Alle übrigen der 32 Varianten widersprechen mindestens einer registrierten Folge; ihre vollständigen Ergebnisse stehen in FAMILY_FUNCTIONAL.json.

| Form | Bedingte Terminalrolle |
|---|---|
| chckhdy | WOULD_BE |
| checthy | ALL |
| ched | WITHOUT_AGENT |
| chedain | NEXT |
| chedy | G |
| cheeety | RETURN_EXCLUDING |
| chety | UNHARMED |
| dal | BESIDES |
| lchedy | G |
| ldy | ALONE |
| lkedy | PAIRED_WITH |
| ockhey | FORBIDDEN |
| olsaly | ATTENDED_BY |
| opshedy | HOME |
| otaiin | THERE |
| otchedy | OTHER_CARGO |
| otedy | RETURN |
| otor | COLOC |
| otshdy | GOAL |
| pdalshdy | INIT |
| qetal | AT_MOST_ONE |
| qokal | TRAVEL_TOGETHER |
| qokchedy | UNATTENDED |
| qokedol | FAR_BANK |
| qokedy | C |
| qokeedy | CONVEY_OUT |
| qokeey | TAKE_OUT |
| qoky | FERRY |
| qotedaiin | LEAVE |
| qotedy | OUTWARD |
| qoteedy | B |
| saiin | W |
| sain | WHEN |
| sar | UNSAFE |
| schedair | LIKEWISE |
| shdy | WITHOUT_HARM |
| shecthedy | JOINING_RESULT |
| shecthy | REST_CARGO |
| shedaiin | PAIRS |
| shedy | M |
| shey | EXAMPLE |
| shocphedy | CARGOS |
| soiiin | THUS |
| sol | THEN |
| soldy | HARM |
| solkeedy | WITH_TRIP |
| tchedy | FINALLY |

| Gruppen (einsbasiert) | Vollständiger Wortlaut | Bedingte Lesung |
|---|---|---|
| 1–5 | pdalshdy shocphedy otor shedy opshedy | Die drei Frachtstücke befinden sich mit der Begleitperson am Ausgangsufer. |
| 6–9 | otshdy qokedol shdy soldy | Ziel ist das gegenüberliegende Ufer ohne Schaden. |
| 10–15 | sar shedaiin ockhey sain ched shedy | Gefährliche Paare dürfen nicht ohne Begleitperson zusammenbleiben. |
| 16–20 | qetal dal shedy shey lchedy | Höchstens ein Frachtstück neben der Begleitperson; Beispiel: Fracht B. |
| 21–24 | solkeedy qoteedy qokeey qokedy | Mit dem Boot Fracht C hinüberbringen. |
| 25–25 | sol | Dann. |
| 26–27 | cheeety qokedy | Ohne Fracht C zurückfahren (Gegenvariante: mit dieser Fracht). |
| 28–29 | qoky saiin | Fracht A zum jeweils anderen Ufer übersetzen. |
| 30–32 | solkeedy qokedy otedy | Mit Fracht C zurückfahren. |
| 33–33 | sol | Dann. |
| 34–39 | chedy lkedy qokchedy qokedy chckhdy sar | Fracht B wäre mit Fracht C unbeaufsichtigt ein gefährliches Paar. |
| 40–41 | schedair otchedy | Entsprechend für das andere/erste Frachtstück; erstes/zweites Paarargument ersetzen. |
| 42–44 | qokeedy chedain chedy | Als Nächstes Fracht B hinüberbringen. |
| 45–46 | qotedaiin otaiin | Das zuletzt beförderte Frachtstück dort lassen (Zielufer/gegenwärtiges Ufer). |
| 47–48 | otedy ldy | Allein zurückfahren. |
| 49–53 | tchedy qotedy qokal shedy qokedy | Abschließend fahren Begleitperson und Fracht C gemeinsam hinüber. |
| 54–57 | shecthedy shecthy otor chedy | Die zuletzt beförderte Fracht befindet sich nun bei den übrigen, darunter Fracht B. |
| 58–63 | soiiin checthy chety otaiin olsaly shedy | Somit sind alle unversehrt dort, begleitet von der Begleitperson. |

| Variante | Einstellungen | Gefährliche Paare | Die sieben tatsächlichen Ladungen | Aufgelöste Bezüge |
|---|---|---|---|---|
| V00 | exclude=EXCLUDING, first=FIRST, other=OTHER, there=GOAL, copy=FIRST | Fracht C + Fracht B; Fracht C + Fracht A | Fracht C → leer → Fracht A → Fracht C → Fracht B → leer → Fracht C | S12: OTHER_CARGO → Fracht A |
| V02 | exclude=EXCLUDING, first=FIRST, other=OTHER, there=CURRENT, copy=FIRST | Fracht C + Fracht B; Fracht C + Fracht A | Fracht C → leer → Fracht A → Fracht C → Fracht B → leer → Fracht C | S12: OTHER_CARGO → Fracht A |
| V08 | exclude=EXCLUDING, first=RECENT, other=OTHER, there=GOAL, copy=FIRST | Fracht C + Fracht B; Fracht C + Fracht A | Fracht C → leer → Fracht A → Fracht C → Fracht B → leer → Fracht C | S12: OTHER_CARGO → Fracht A |
| V10 | exclude=EXCLUDING, first=RECENT, other=OTHER, there=CURRENT, copy=FIRST | Fracht C + Fracht B; Fracht C + Fracht A | Fracht C → leer → Fracht A → Fracht C → Fracht B → leer → Fracht C | S12: OTHER_CARGO → Fracht A |

Alle aufgeführten Pfade erreichen das Ziel ohne physischen Widerspruch, falsche Zustandsbehauptung oder unbeaufsichtigtes Gefahrpaar. Das bedeutet Konsistenz unter den angenommenen Regeln; es bedeutet keine unabhängige Bedeutungsbestätigung.

### FUNCTIONAL Karte 1135

Kohärente Bezugseinstellungen: [0, 2, 8, 10]. Alle übrigen der 32 Varianten widersprechen mindestens einer registrierten Folge; ihre vollständigen Ergebnisse stehen in FAMILY_FUNCTIONAL.json.

| Form | Bedingte Terminalrolle |
|---|---|
| chckhdy | WOULD_BE |
| checthy | ALL |
| ched | WITHOUT_AGENT |
| chedain | NEXT |
| chedy | G |
| cheeety | RETURN_EXCLUDING |
| chety | UNHARMED |
| dal | BESIDES |
| lchedy | C |
| ldy | ALONE |
| lkedy | PAIRED_WITH |
| ockhey | FORBIDDEN |
| olsaly | ATTENDED_BY |
| opshedy | HOME |
| otaiin | THERE |
| otchedy | OTHER_CARGO |
| otedy | RETURN |
| otor | COLOC |
| otshdy | GOAL |
| pdalshdy | INIT |
| qetal | AT_MOST_ONE |
| qokal | TRAVEL_TOGETHER |
| qokchedy | UNATTENDED |
| qokedol | FAR_BANK |
| qokedy | C |
| qokeedy | CONVEY_OUT |
| qokeey | TAKE_OUT |
| qoky | FERRY |
| qotedaiin | LEAVE |
| qotedy | OUTWARD |
| qoteedy | B |
| saiin | W |
| sain | WHEN |
| sar | UNSAFE |
| schedair | LIKEWISE |
| shdy | WITHOUT_HARM |
| shecthedy | JOINING_RESULT |
| shecthy | REST_CARGO |
| shedaiin | PAIRS |
| shedy | M |
| shey | EXAMPLE |
| shocphedy | CARGOS |
| soiiin | THUS |
| sol | THEN |
| soldy | HARM |
| solkeedy | WITH_TRIP |
| tchedy | FINALLY |

| Gruppen (einsbasiert) | Vollständiger Wortlaut | Bedingte Lesung |
|---|---|---|
| 1–5 | pdalshdy shocphedy otor shedy opshedy | Die drei Frachtstücke befinden sich mit der Begleitperson am Ausgangsufer. |
| 6–9 | otshdy qokedol shdy soldy | Ziel ist das gegenüberliegende Ufer ohne Schaden. |
| 10–15 | sar shedaiin ockhey sain ched shedy | Gefährliche Paare dürfen nicht ohne Begleitperson zusammenbleiben. |
| 16–20 | qetal dal shedy shey lchedy | Höchstens ein Frachtstück neben der Begleitperson; Beispiel: Fracht C. |
| 21–24 | solkeedy qoteedy qokeey qokedy | Mit dem Boot Fracht C hinüberbringen. |
| 25–25 | sol | Dann. |
| 26–27 | cheeety qokedy | Ohne Fracht C zurückfahren (Gegenvariante: mit dieser Fracht). |
| 28–29 | qoky saiin | Fracht A zum jeweils anderen Ufer übersetzen. |
| 30–32 | solkeedy qokedy otedy | Mit Fracht C zurückfahren. |
| 33–33 | sol | Dann. |
| 34–39 | chedy lkedy qokchedy qokedy chckhdy sar | Fracht B wäre mit Fracht C unbeaufsichtigt ein gefährliches Paar. |
| 40–41 | schedair otchedy | Entsprechend für das andere/erste Frachtstück; erstes/zweites Paarargument ersetzen. |
| 42–44 | qokeedy chedain chedy | Als Nächstes Fracht B hinüberbringen. |
| 45–46 | qotedaiin otaiin | Das zuletzt beförderte Frachtstück dort lassen (Zielufer/gegenwärtiges Ufer). |
| 47–48 | otedy ldy | Allein zurückfahren. |
| 49–53 | tchedy qotedy qokal shedy qokedy | Abschließend fahren Begleitperson und Fracht C gemeinsam hinüber. |
| 54–57 | shecthedy shecthy otor chedy | Die zuletzt beförderte Fracht befindet sich nun bei den übrigen, darunter Fracht B. |
| 58–63 | soiiin checthy chety otaiin olsaly shedy | Somit sind alle unversehrt dort, begleitet von der Begleitperson. |

| Variante | Einstellungen | Gefährliche Paare | Die sieben tatsächlichen Ladungen | Aufgelöste Bezüge |
|---|---|---|---|---|
| V00 | exclude=EXCLUDING, first=FIRST, other=OTHER, there=GOAL, copy=FIRST | Fracht C + Fracht B; Fracht C + Fracht A | Fracht C → leer → Fracht A → Fracht C → Fracht B → leer → Fracht C | S12: OTHER_CARGO → Fracht A |
| V02 | exclude=EXCLUDING, first=FIRST, other=OTHER, there=CURRENT, copy=FIRST | Fracht C + Fracht B; Fracht C + Fracht A | Fracht C → leer → Fracht A → Fracht C → Fracht B → leer → Fracht C | S12: OTHER_CARGO → Fracht A |
| V08 | exclude=EXCLUDING, first=RECENT, other=OTHER, there=GOAL, copy=FIRST | Fracht C + Fracht B; Fracht C + Fracht A | Fracht C → leer → Fracht A → Fracht C → Fracht B → leer → Fracht C | S12: OTHER_CARGO → Fracht A |
| V10 | exclude=EXCLUDING, first=RECENT, other=OTHER, there=CURRENT, copy=FIRST | Fracht C + Fracht B; Fracht C + Fracht A | Fracht C → leer → Fracht A → Fracht C → Fracht B → leer → Fracht C | S12: OTHER_CARGO → Fracht A |

Alle aufgeführten Pfade erreichen das Ziel ohne physischen Widerspruch, falsche Zustandsbehauptung oder unbeaufsichtigtes Gefahrpaar. Das bedeutet Konsistenz unter den angenommenen Regeln; es bedeutet keine unabhängige Bedeutungsbestätigung.

## BIJECTIVE

12 kohärente vollständige Karten; 36 positive Rollen-/Bezugsvarianten. Projektionsraum vollständig: True. Stopp: RESIDUAL_SYNTAX_EXHAUSTED.

### BIJECTIVE Karte 27

Kohärente Bezugseinstellungen: [0, 2]. Alle übrigen der 32 Varianten widersprechen mindestens einer registrierten Folge; ihre vollständigen Ergebnisse stehen in FAMILY_BIJECTIVE.json.

| Form | Bedingte Terminalrolle |
|---|---|
| chckhdy | WOULD_BE |
| checthy | ALL |
| ched | WITHOUT_AGENT |
| chedain | NEXT |
| chedy | FIRST_CARGO |
| cheeety | RETURN_EXCLUDING |
| chety | UNHARMED |
| dal | BESIDES |
| lchedy | W |
| ldy | ALONE |
| lkedy | PAIRED_WITH |
| ockhey | FORBIDDEN |
| olsaly | ATTENDED_BY |
| opshedy | HOME |
| otaiin | THERE |
| otchedy | OTHER_CARGO |
| otedy | RETURN |
| otor | COLOC |
| otshdy | GOAL |
| pdalshdy | INIT |
| qetal | AT_MOST_ONE |
| qokal | TRAVEL_TOGETHER |
| qokchedy | UNATTENDED |
| qokedol | FAR_BANK |
| qokedy | G |
| qokeedy | CONVEY_OUT |
| qokeey | TAKE_OUT |
| qoky | FERRY |
| qotedaiin | LEAVE |
| qotedy | OUTWARD |
| qoteedy | B |
| saiin | C |
| sain | WHEN |
| sar | UNSAFE |
| schedair | LIKEWISE |
| shdy | WITHOUT_HARM |
| shecthedy | JOINING_RESULT |
| shecthy | REST_CARGO |
| shedaiin | PAIRS |
| shedy | M |
| shey | EXAMPLE |
| shocphedy | CARGOS |
| soiiin | THUS |
| sol | THEN |
| soldy | HARM |
| solkeedy | WITH_TRIP |
| tchedy | FINALLY |

| Gruppen (einsbasiert) | Vollständiger Wortlaut | Bedingte Lesung |
|---|---|---|
| 1–5 | pdalshdy shocphedy otor shedy opshedy | Die drei Frachtstücke befinden sich mit der Begleitperson am Ausgangsufer. |
| 6–9 | otshdy qokedol shdy soldy | Ziel ist das gegenüberliegende Ufer ohne Schaden. |
| 10–15 | sar shedaiin ockhey sain ched shedy | Gefährliche Paare dürfen nicht ohne Begleitperson zusammenbleiben. |
| 16–20 | qetal dal shedy shey lchedy | Höchstens ein Frachtstück neben der Begleitperson; Beispiel: Fracht A. |
| 21–24 | solkeedy qoteedy qokeey qokedy | Mit dem Boot Fracht B hinüberbringen. |
| 25–25 | sol | Dann. |
| 26–27 | cheeety qokedy | Ohne Fracht B zurückfahren (Gegenvariante: mit dieser Fracht). |
| 28–29 | qoky saiin | Fracht C zum jeweils anderen Ufer übersetzen. |
| 30–32 | solkeedy qokedy otedy | Mit Fracht B zurückfahren. |
| 33–33 | sol | Dann. |
| 34–39 | chedy lkedy qokchedy qokedy chckhdy sar | zuerst/zuletzt erwähnte Fracht wäre mit Fracht B unbeaufsichtigt ein gefährliches Paar. |
| 40–41 | schedair otchedy | Entsprechend für das andere/erste Frachtstück; erstes/zweites Paarargument ersetzen. |
| 42–44 | qokeedy chedain chedy | Als Nächstes zuerst/zuletzt erwähnte Fracht hinüberbringen. |
| 45–46 | qotedaiin otaiin | Das zuletzt beförderte Frachtstück dort lassen (Zielufer/gegenwärtiges Ufer). |
| 47–48 | otedy ldy | Allein zurückfahren. |
| 49–53 | tchedy qotedy qokal shedy qokedy | Abschließend fahren Begleitperson und Fracht B gemeinsam hinüber. |
| 54–57 | shecthedy shecthy otor chedy | Die zuletzt beförderte Fracht befindet sich nun bei den übrigen, darunter zuerst/zuletzt erwähnte Fracht. |
| 58–63 | soiiin checthy chety otaiin olsaly shedy | Somit sind alle unversehrt dort, begleitet von der Begleitperson. |

| Variante | Einstellungen | Gefährliche Paare | Die sieben tatsächlichen Ladungen | Aufgelöste Bezüge |
|---|---|---|---|---|
| V00 | exclude=EXCLUDING, first=FIRST, other=OTHER, there=GOAL, copy=FIRST | Fracht C + Fracht B; Fracht B + Fracht A | Fracht B → leer → Fracht C → Fracht B → Fracht A → leer → Fracht B | S11: FIRST_CARGO → Fracht A; S12: OTHER_CARGO → Fracht C; S13: FIRST_CARGO → Fracht A; S17: FIRST_CARGO → Fracht A |
| V02 | exclude=EXCLUDING, first=FIRST, other=OTHER, there=CURRENT, copy=FIRST | Fracht C + Fracht B; Fracht B + Fracht A | Fracht B → leer → Fracht C → Fracht B → Fracht A → leer → Fracht B | S11: FIRST_CARGO → Fracht A; S12: OTHER_CARGO → Fracht C; S13: FIRST_CARGO → Fracht A; S17: FIRST_CARGO → Fracht A |

Alle aufgeführten Pfade erreichen das Ziel ohne physischen Widerspruch, falsche Zustandsbehauptung oder unbeaufsichtigtes Gefahrpaar. Das bedeutet Konsistenz unter den angenommenen Regeln; es bedeutet keine unabhängige Bedeutungsbestätigung.

### BIJECTIVE Karte 28

Kohärente Bezugseinstellungen: [0, 2]. Alle übrigen der 32 Varianten widersprechen mindestens einer registrierten Folge; ihre vollständigen Ergebnisse stehen in FAMILY_BIJECTIVE.json.

| Form | Bedingte Terminalrolle |
|---|---|
| chckhdy | WOULD_BE |
| checthy | ALL |
| ched | WITHOUT_AGENT |
| chedain | NEXT |
| chedy | FIRST_CARGO |
| cheeety | RETURN_EXCLUDING |
| chety | UNHARMED |
| dal | BESIDES |
| lchedy | C |
| ldy | ALONE |
| lkedy | PAIRED_WITH |
| ockhey | FORBIDDEN |
| olsaly | ATTENDED_BY |
| opshedy | HOME |
| otaiin | THERE |
| otchedy | OTHER_CARGO |
| otedy | RETURN |
| otor | COLOC |
| otshdy | GOAL |
| pdalshdy | INIT |
| qetal | AT_MOST_ONE |
| qokal | TRAVEL_TOGETHER |
| qokchedy | UNATTENDED |
| qokedol | FAR_BANK |
| qokedy | G |
| qokeedy | CONVEY_OUT |
| qokeey | TAKE_OUT |
| qoky | FERRY |
| qotedaiin | LEAVE |
| qotedy | OUTWARD |
| qoteedy | B |
| saiin | W |
| sain | WHEN |
| sar | UNSAFE |
| schedair | LIKEWISE |
| shdy | WITHOUT_HARM |
| shecthedy | JOINING_RESULT |
| shecthy | REST_CARGO |
| shedaiin | PAIRS |
| shedy | M |
| shey | EXAMPLE |
| shocphedy | CARGOS |
| soiiin | THUS |
| sol | THEN |
| soldy | HARM |
| solkeedy | WITH_TRIP |
| tchedy | FINALLY |

| Gruppen (einsbasiert) | Vollständiger Wortlaut | Bedingte Lesung |
|---|---|---|
| 1–5 | pdalshdy shocphedy otor shedy opshedy | Die drei Frachtstücke befinden sich mit der Begleitperson am Ausgangsufer. |
| 6–9 | otshdy qokedol shdy soldy | Ziel ist das gegenüberliegende Ufer ohne Schaden. |
| 10–15 | sar shedaiin ockhey sain ched shedy | Gefährliche Paare dürfen nicht ohne Begleitperson zusammenbleiben. |
| 16–20 | qetal dal shedy shey lchedy | Höchstens ein Frachtstück neben der Begleitperson; Beispiel: Fracht C. |
| 21–24 | solkeedy qoteedy qokeey qokedy | Mit dem Boot Fracht B hinüberbringen. |
| 25–25 | sol | Dann. |
| 26–27 | cheeety qokedy | Ohne Fracht B zurückfahren (Gegenvariante: mit dieser Fracht). |
| 28–29 | qoky saiin | Fracht A zum jeweils anderen Ufer übersetzen. |
| 30–32 | solkeedy qokedy otedy | Mit Fracht B zurückfahren. |
| 33–33 | sol | Dann. |
| 34–39 | chedy lkedy qokchedy qokedy chckhdy sar | zuerst/zuletzt erwähnte Fracht wäre mit Fracht B unbeaufsichtigt ein gefährliches Paar. |
| 40–41 | schedair otchedy | Entsprechend für das andere/erste Frachtstück; erstes/zweites Paarargument ersetzen. |
| 42–44 | qokeedy chedain chedy | Als Nächstes zuerst/zuletzt erwähnte Fracht hinüberbringen. |
| 45–46 | qotedaiin otaiin | Das zuletzt beförderte Frachtstück dort lassen (Zielufer/gegenwärtiges Ufer). |
| 47–48 | otedy ldy | Allein zurückfahren. |
| 49–53 | tchedy qotedy qokal shedy qokedy | Abschließend fahren Begleitperson und Fracht B gemeinsam hinüber. |
| 54–57 | shecthedy shecthy otor chedy | Die zuletzt beförderte Fracht befindet sich nun bei den übrigen, darunter zuerst/zuletzt erwähnte Fracht. |
| 58–63 | soiiin checthy chety otaiin olsaly shedy | Somit sind alle unversehrt dort, begleitet von der Begleitperson. |

| Variante | Einstellungen | Gefährliche Paare | Die sieben tatsächlichen Ladungen | Aufgelöste Bezüge |
|---|---|---|---|---|
| V00 | exclude=EXCLUDING, first=FIRST, other=OTHER, there=GOAL, copy=FIRST | Fracht C + Fracht B; Fracht B + Fracht A | Fracht B → leer → Fracht A → Fracht B → Fracht C → leer → Fracht B | S11: FIRST_CARGO → Fracht C; S12: OTHER_CARGO → Fracht A; S13: FIRST_CARGO → Fracht C; S17: FIRST_CARGO → Fracht C |
| V02 | exclude=EXCLUDING, first=FIRST, other=OTHER, there=CURRENT, copy=FIRST | Fracht C + Fracht B; Fracht B + Fracht A | Fracht B → leer → Fracht A → Fracht B → Fracht C → leer → Fracht B | S11: FIRST_CARGO → Fracht C; S12: OTHER_CARGO → Fracht A; S13: FIRST_CARGO → Fracht C; S17: FIRST_CARGO → Fracht C |

Alle aufgeführten Pfade erreichen das Ziel ohne physischen Widerspruch, falsche Zustandsbehauptung oder unbeaufsichtigtes Gefahrpaar. Das bedeutet Konsistenz unter den angenommenen Regeln; es bedeutet keine unabhängige Bedeutungsbestätigung.

### BIJECTIVE Karte 29

Kohärente Bezugseinstellungen: [0, 2, 4, 6]. Alle übrigen der 32 Varianten widersprechen mindestens einer registrierten Folge; ihre vollständigen Ergebnisse stehen in FAMILY_BIJECTIVE.json.

| Form | Bedingte Terminalrolle |
|---|---|
| chckhdy | WOULD_BE |
| checthy | ALL |
| ched | WITHOUT_AGENT |
| chedain | NEXT |
| chedy | W |
| cheeety | RETURN_EXCLUDING |
| chety | UNHARMED |
| dal | BESIDES |
| lchedy | C |
| ldy | ALONE |
| lkedy | PAIRED_WITH |
| ockhey | FORBIDDEN |
| olsaly | ATTENDED_BY |
| opshedy | HOME |
| otaiin | THERE |
| otchedy | OTHER_CARGO |
| otedy | RETURN |
| otor | COLOC |
| otshdy | GOAL |
| pdalshdy | INIT |
| qetal | AT_MOST_ONE |
| qokal | TRAVEL_TOGETHER |
| qokchedy | UNATTENDED |
| qokedol | FAR_BANK |
| qokedy | G |
| qokeedy | CONVEY_OUT |
| qokeey | TAKE_OUT |
| qoky | FERRY |
| qotedaiin | LEAVE |
| qotedy | OUTWARD |
| qoteedy | B |
| saiin | FIRST_CARGO |
| sain | WHEN |
| sar | UNSAFE |
| schedair | LIKEWISE |
| shdy | WITHOUT_HARM |
| shecthedy | JOINING_RESULT |
| shecthy | REST_CARGO |
| shedaiin | PAIRS |
| shedy | M |
| shey | EXAMPLE |
| shocphedy | CARGOS |
| soiiin | THUS |
| sol | THEN |
| soldy | HARM |
| solkeedy | WITH_TRIP |
| tchedy | FINALLY |

| Gruppen (einsbasiert) | Vollständiger Wortlaut | Bedingte Lesung |
|---|---|---|
| 1–5 | pdalshdy shocphedy otor shedy opshedy | Die drei Frachtstücke befinden sich mit der Begleitperson am Ausgangsufer. |
| 6–9 | otshdy qokedol shdy soldy | Ziel ist das gegenüberliegende Ufer ohne Schaden. |
| 10–15 | sar shedaiin ockhey sain ched shedy | Gefährliche Paare dürfen nicht ohne Begleitperson zusammenbleiben. |
| 16–20 | qetal dal shedy shey lchedy | Höchstens ein Frachtstück neben der Begleitperson; Beispiel: Fracht C. |
| 21–24 | solkeedy qoteedy qokeey qokedy | Mit dem Boot Fracht B hinüberbringen. |
| 25–25 | sol | Dann. |
| 26–27 | cheeety qokedy | Ohne Fracht B zurückfahren (Gegenvariante: mit dieser Fracht). |
| 28–29 | qoky saiin | zuerst/zuletzt erwähnte Fracht zum jeweils anderen Ufer übersetzen. |
| 30–32 | solkeedy qokedy otedy | Mit Fracht B zurückfahren. |
| 33–33 | sol | Dann. |
| 34–39 | chedy lkedy qokchedy qokedy chckhdy sar | Fracht A wäre mit Fracht B unbeaufsichtigt ein gefährliches Paar. |
| 40–41 | schedair otchedy | Entsprechend für das andere/erste Frachtstück; erstes/zweites Paarargument ersetzen. |
| 42–44 | qokeedy chedain chedy | Als Nächstes Fracht A hinüberbringen. |
| 45–46 | qotedaiin otaiin | Das zuletzt beförderte Frachtstück dort lassen (Zielufer/gegenwärtiges Ufer). |
| 47–48 | otedy ldy | Allein zurückfahren. |
| 49–53 | tchedy qotedy qokal shedy qokedy | Abschließend fahren Begleitperson und Fracht B gemeinsam hinüber. |
| 54–57 | shecthedy shecthy otor chedy | Die zuletzt beförderte Fracht befindet sich nun bei den übrigen, darunter Fracht A. |
| 58–63 | soiiin checthy chety otaiin olsaly shedy | Somit sind alle unversehrt dort, begleitet von der Begleitperson. |

| Variante | Einstellungen | Gefährliche Paare | Die sieben tatsächlichen Ladungen | Aufgelöste Bezüge |
|---|---|---|---|---|
| V00 | exclude=EXCLUDING, first=FIRST, other=OTHER, there=GOAL, copy=FIRST | Fracht C + Fracht B; Fracht B + Fracht A | Fracht B → leer → Fracht C → Fracht B → Fracht A → leer → Fracht B | S08: FIRST_CARGO → Fracht C; S12: OTHER_CARGO → Fracht C |
| V02 | exclude=EXCLUDING, first=FIRST, other=OTHER, there=CURRENT, copy=FIRST | Fracht C + Fracht B; Fracht B + Fracht A | Fracht B → leer → Fracht C → Fracht B → Fracht A → leer → Fracht B | S08: FIRST_CARGO → Fracht C; S12: OTHER_CARGO → Fracht C |
| V04 | exclude=EXCLUDING, first=FIRST, other=FIRST, there=GOAL, copy=FIRST | Fracht C + Fracht B; Fracht B + Fracht A | Fracht B → leer → Fracht C → Fracht B → Fracht A → leer → Fracht B | S08: FIRST_CARGO → Fracht C; S12: OTHER_CARGO → Fracht C |
| V06 | exclude=EXCLUDING, first=FIRST, other=FIRST, there=CURRENT, copy=FIRST | Fracht C + Fracht B; Fracht B + Fracht A | Fracht B → leer → Fracht C → Fracht B → Fracht A → leer → Fracht B | S08: FIRST_CARGO → Fracht C; S12: OTHER_CARGO → Fracht C |

Alle aufgeführten Pfade erreichen das Ziel ohne physischen Widerspruch, falsche Zustandsbehauptung oder unbeaufsichtigtes Gefahrpaar. Das bedeutet Konsistenz unter den angenommenen Regeln; es bedeutet keine unabhängige Bedeutungsbestätigung.

### BIJECTIVE Karte 30

Kohärente Bezugseinstellungen: [0, 2, 4, 6]. Alle übrigen der 32 Varianten widersprechen mindestens einer registrierten Folge; ihre vollständigen Ergebnisse stehen in FAMILY_BIJECTIVE.json.

| Form | Bedingte Terminalrolle |
|---|---|
| chckhdy | WOULD_BE |
| checthy | ALL |
| ched | WITHOUT_AGENT |
| chedain | NEXT |
| chedy | C |
| cheeety | RETURN_EXCLUDING |
| chety | UNHARMED |
| dal | BESIDES |
| lchedy | W |
| ldy | ALONE |
| lkedy | PAIRED_WITH |
| ockhey | FORBIDDEN |
| olsaly | ATTENDED_BY |
| opshedy | HOME |
| otaiin | THERE |
| otchedy | OTHER_CARGO |
| otedy | RETURN |
| otor | COLOC |
| otshdy | GOAL |
| pdalshdy | INIT |
| qetal | AT_MOST_ONE |
| qokal | TRAVEL_TOGETHER |
| qokchedy | UNATTENDED |
| qokedol | FAR_BANK |
| qokedy | G |
| qokeedy | CONVEY_OUT |
| qokeey | TAKE_OUT |
| qoky | FERRY |
| qotedaiin | LEAVE |
| qotedy | OUTWARD |
| qoteedy | B |
| saiin | FIRST_CARGO |
| sain | WHEN |
| sar | UNSAFE |
| schedair | LIKEWISE |
| shdy | WITHOUT_HARM |
| shecthedy | JOINING_RESULT |
| shecthy | REST_CARGO |
| shedaiin | PAIRS |
| shedy | M |
| shey | EXAMPLE |
| shocphedy | CARGOS |
| soiiin | THUS |
| sol | THEN |
| soldy | HARM |
| solkeedy | WITH_TRIP |
| tchedy | FINALLY |

| Gruppen (einsbasiert) | Vollständiger Wortlaut | Bedingte Lesung |
|---|---|---|
| 1–5 | pdalshdy shocphedy otor shedy opshedy | Die drei Frachtstücke befinden sich mit der Begleitperson am Ausgangsufer. |
| 6–9 | otshdy qokedol shdy soldy | Ziel ist das gegenüberliegende Ufer ohne Schaden. |
| 10–15 | sar shedaiin ockhey sain ched shedy | Gefährliche Paare dürfen nicht ohne Begleitperson zusammenbleiben. |
| 16–20 | qetal dal shedy shey lchedy | Höchstens ein Frachtstück neben der Begleitperson; Beispiel: Fracht A. |
| 21–24 | solkeedy qoteedy qokeey qokedy | Mit dem Boot Fracht B hinüberbringen. |
| 25–25 | sol | Dann. |
| 26–27 | cheeety qokedy | Ohne Fracht B zurückfahren (Gegenvariante: mit dieser Fracht). |
| 28–29 | qoky saiin | zuerst/zuletzt erwähnte Fracht zum jeweils anderen Ufer übersetzen. |
| 30–32 | solkeedy qokedy otedy | Mit Fracht B zurückfahren. |
| 33–33 | sol | Dann. |
| 34–39 | chedy lkedy qokchedy qokedy chckhdy sar | Fracht C wäre mit Fracht B unbeaufsichtigt ein gefährliches Paar. |
| 40–41 | schedair otchedy | Entsprechend für das andere/erste Frachtstück; erstes/zweites Paarargument ersetzen. |
| 42–44 | qokeedy chedain chedy | Als Nächstes Fracht C hinüberbringen. |
| 45–46 | qotedaiin otaiin | Das zuletzt beförderte Frachtstück dort lassen (Zielufer/gegenwärtiges Ufer). |
| 47–48 | otedy ldy | Allein zurückfahren. |
| 49–53 | tchedy qotedy qokal shedy qokedy | Abschließend fahren Begleitperson und Fracht B gemeinsam hinüber. |
| 54–57 | shecthedy shecthy otor chedy | Die zuletzt beförderte Fracht befindet sich nun bei den übrigen, darunter Fracht C. |
| 58–63 | soiiin checthy chety otaiin olsaly shedy | Somit sind alle unversehrt dort, begleitet von der Begleitperson. |

| Variante | Einstellungen | Gefährliche Paare | Die sieben tatsächlichen Ladungen | Aufgelöste Bezüge |
|---|---|---|---|---|
| V00 | exclude=EXCLUDING, first=FIRST, other=OTHER, there=GOAL, copy=FIRST | Fracht C + Fracht B; Fracht B + Fracht A | Fracht B → leer → Fracht A → Fracht B → Fracht C → leer → Fracht B | S08: FIRST_CARGO → Fracht A; S12: OTHER_CARGO → Fracht A |
| V02 | exclude=EXCLUDING, first=FIRST, other=OTHER, there=CURRENT, copy=FIRST | Fracht C + Fracht B; Fracht B + Fracht A | Fracht B → leer → Fracht A → Fracht B → Fracht C → leer → Fracht B | S08: FIRST_CARGO → Fracht A; S12: OTHER_CARGO → Fracht A |
| V04 | exclude=EXCLUDING, first=FIRST, other=FIRST, there=GOAL, copy=FIRST | Fracht C + Fracht B; Fracht B + Fracht A | Fracht B → leer → Fracht A → Fracht B → Fracht C → leer → Fracht B | S08: FIRST_CARGO → Fracht A; S12: OTHER_CARGO → Fracht A |
| V06 | exclude=EXCLUDING, first=FIRST, other=FIRST, there=CURRENT, copy=FIRST | Fracht C + Fracht B; Fracht B + Fracht A | Fracht B → leer → Fracht A → Fracht B → Fracht C → leer → Fracht B | S08: FIRST_CARGO → Fracht A; S12: OTHER_CARGO → Fracht A |

Alle aufgeführten Pfade erreichen das Ziel ohne physischen Widerspruch, falsche Zustandsbehauptung oder unbeaufsichtigtes Gefahrpaar. Das bedeutet Konsistenz unter den angenommenen Regeln; es bedeutet keine unabhängige Bedeutungsbestätigung.

### BIJECTIVE Karte 40

Kohärente Bezugseinstellungen: [0, 2, 4, 6]. Alle übrigen der 32 Varianten widersprechen mindestens einer registrierten Folge; ihre vollständigen Ergebnisse stehen in FAMILY_BIJECTIVE.json.

| Form | Bedingte Terminalrolle |
|---|---|
| chckhdy | WOULD_BE |
| checthy | ALL |
| ched | WITHOUT_AGENT |
| chedain | NEXT |
| chedy | W |
| cheeety | RETURN_EXCLUDING |
| chety | UNHARMED |
| dal | BESIDES |
| lchedy | G |
| ldy | ALONE |
| lkedy | PAIRED_WITH |
| ockhey | FORBIDDEN |
| olsaly | ATTENDED_BY |
| opshedy | HOME |
| otaiin | THERE |
| otchedy | OTHER_CARGO |
| otedy | RETURN |
| otor | COLOC |
| otshdy | GOAL |
| pdalshdy | INIT |
| qetal | AT_MOST_ONE |
| qokal | TRAVEL_TOGETHER |
| qokchedy | UNATTENDED |
| qokedol | FAR_BANK |
| qokedy | C |
| qokeedy | CONVEY_OUT |
| qokeey | TAKE_OUT |
| qoky | FERRY |
| qotedaiin | LEAVE |
| qotedy | OUTWARD |
| qoteedy | B |
| saiin | FIRST_CARGO |
| sain | WHEN |
| sar | UNSAFE |
| schedair | LIKEWISE |
| shdy | WITHOUT_HARM |
| shecthedy | JOINING_RESULT |
| shecthy | REST_CARGO |
| shedaiin | PAIRS |
| shedy | M |
| shey | EXAMPLE |
| shocphedy | CARGOS |
| soiiin | THUS |
| sol | THEN |
| soldy | HARM |
| solkeedy | WITH_TRIP |
| tchedy | FINALLY |

| Gruppen (einsbasiert) | Vollständiger Wortlaut | Bedingte Lesung |
|---|---|---|
| 1–5 | pdalshdy shocphedy otor shedy opshedy | Die drei Frachtstücke befinden sich mit der Begleitperson am Ausgangsufer. |
| 6–9 | otshdy qokedol shdy soldy | Ziel ist das gegenüberliegende Ufer ohne Schaden. |
| 10–15 | sar shedaiin ockhey sain ched shedy | Gefährliche Paare dürfen nicht ohne Begleitperson zusammenbleiben. |
| 16–20 | qetal dal shedy shey lchedy | Höchstens ein Frachtstück neben der Begleitperson; Beispiel: Fracht B. |
| 21–24 | solkeedy qoteedy qokeey qokedy | Mit dem Boot Fracht C hinüberbringen. |
| 25–25 | sol | Dann. |
| 26–27 | cheeety qokedy | Ohne Fracht C zurückfahren (Gegenvariante: mit dieser Fracht). |
| 28–29 | qoky saiin | zuerst/zuletzt erwähnte Fracht zum jeweils anderen Ufer übersetzen. |
| 30–32 | solkeedy qokedy otedy | Mit Fracht C zurückfahren. |
| 33–33 | sol | Dann. |
| 34–39 | chedy lkedy qokchedy qokedy chckhdy sar | Fracht A wäre mit Fracht C unbeaufsichtigt ein gefährliches Paar. |
| 40–41 | schedair otchedy | Entsprechend für das andere/erste Frachtstück; erstes/zweites Paarargument ersetzen. |
| 42–44 | qokeedy chedain chedy | Als Nächstes Fracht A hinüberbringen. |
| 45–46 | qotedaiin otaiin | Das zuletzt beförderte Frachtstück dort lassen (Zielufer/gegenwärtiges Ufer). |
| 47–48 | otedy ldy | Allein zurückfahren. |
| 49–53 | tchedy qotedy qokal shedy qokedy | Abschließend fahren Begleitperson und Fracht C gemeinsam hinüber. |
| 54–57 | shecthedy shecthy otor chedy | Die zuletzt beförderte Fracht befindet sich nun bei den übrigen, darunter Fracht A. |
| 58–63 | soiiin checthy chety otaiin olsaly shedy | Somit sind alle unversehrt dort, begleitet von der Begleitperson. |

| Variante | Einstellungen | Gefährliche Paare | Die sieben tatsächlichen Ladungen | Aufgelöste Bezüge |
|---|---|---|---|---|
| V00 | exclude=EXCLUDING, first=FIRST, other=OTHER, there=GOAL, copy=FIRST | Fracht C + Fracht B; Fracht C + Fracht A | Fracht C → leer → Fracht B → Fracht C → Fracht A → leer → Fracht C | S08: FIRST_CARGO → Fracht B; S12: OTHER_CARGO → Fracht B |
| V02 | exclude=EXCLUDING, first=FIRST, other=OTHER, there=CURRENT, copy=FIRST | Fracht C + Fracht B; Fracht C + Fracht A | Fracht C → leer → Fracht B → Fracht C → Fracht A → leer → Fracht C | S08: FIRST_CARGO → Fracht B; S12: OTHER_CARGO → Fracht B |
| V04 | exclude=EXCLUDING, first=FIRST, other=FIRST, there=GOAL, copy=FIRST | Fracht C + Fracht B; Fracht C + Fracht A | Fracht C → leer → Fracht B → Fracht C → Fracht A → leer → Fracht C | S08: FIRST_CARGO → Fracht B; S12: OTHER_CARGO → Fracht B |
| V06 | exclude=EXCLUDING, first=FIRST, other=FIRST, there=CURRENT, copy=FIRST | Fracht C + Fracht B; Fracht C + Fracht A | Fracht C → leer → Fracht B → Fracht C → Fracht A → leer → Fracht C | S08: FIRST_CARGO → Fracht B; S12: OTHER_CARGO → Fracht B |

Alle aufgeführten Pfade erreichen das Ziel ohne physischen Widerspruch, falsche Zustandsbehauptung oder unbeaufsichtigtes Gefahrpaar. Das bedeutet Konsistenz unter den angenommenen Regeln; es bedeutet keine unabhängige Bedeutungsbestätigung.

### BIJECTIVE Karte 41

Kohärente Bezugseinstellungen: [0, 2]. Alle übrigen der 32 Varianten widersprechen mindestens einer registrierten Folge; ihre vollständigen Ergebnisse stehen in FAMILY_BIJECTIVE.json.

| Form | Bedingte Terminalrolle |
|---|---|
| chckhdy | WOULD_BE |
| checthy | ALL |
| ched | WITHOUT_AGENT |
| chedain | NEXT |
| chedy | FIRST_CARGO |
| cheeety | RETURN_EXCLUDING |
| chety | UNHARMED |
| dal | BESIDES |
| lchedy | W |
| ldy | ALONE |
| lkedy | PAIRED_WITH |
| ockhey | FORBIDDEN |
| olsaly | ATTENDED_BY |
| opshedy | HOME |
| otaiin | THERE |
| otchedy | OTHER_CARGO |
| otedy | RETURN |
| otor | COLOC |
| otshdy | GOAL |
| pdalshdy | INIT |
| qetal | AT_MOST_ONE |
| qokal | TRAVEL_TOGETHER |
| qokchedy | UNATTENDED |
| qokedol | FAR_BANK |
| qokedy | C |
| qokeedy | CONVEY_OUT |
| qokeey | TAKE_OUT |
| qoky | FERRY |
| qotedaiin | LEAVE |
| qotedy | OUTWARD |
| qoteedy | B |
| saiin | G |
| sain | WHEN |
| sar | UNSAFE |
| schedair | LIKEWISE |
| shdy | WITHOUT_HARM |
| shecthedy | JOINING_RESULT |
| shecthy | REST_CARGO |
| shedaiin | PAIRS |
| shedy | M |
| shey | EXAMPLE |
| shocphedy | CARGOS |
| soiiin | THUS |
| sol | THEN |
| soldy | HARM |
| solkeedy | WITH_TRIP |
| tchedy | FINALLY |

| Gruppen (einsbasiert) | Vollständiger Wortlaut | Bedingte Lesung |
|---|---|---|
| 1–5 | pdalshdy shocphedy otor shedy opshedy | Die drei Frachtstücke befinden sich mit der Begleitperson am Ausgangsufer. |
| 6–9 | otshdy qokedol shdy soldy | Ziel ist das gegenüberliegende Ufer ohne Schaden. |
| 10–15 | sar shedaiin ockhey sain ched shedy | Gefährliche Paare dürfen nicht ohne Begleitperson zusammenbleiben. |
| 16–20 | qetal dal shedy shey lchedy | Höchstens ein Frachtstück neben der Begleitperson; Beispiel: Fracht A. |
| 21–24 | solkeedy qoteedy qokeey qokedy | Mit dem Boot Fracht C hinüberbringen. |
| 25–25 | sol | Dann. |
| 26–27 | cheeety qokedy | Ohne Fracht C zurückfahren (Gegenvariante: mit dieser Fracht). |
| 28–29 | qoky saiin | Fracht B zum jeweils anderen Ufer übersetzen. |
| 30–32 | solkeedy qokedy otedy | Mit Fracht C zurückfahren. |
| 33–33 | sol | Dann. |
| 34–39 | chedy lkedy qokchedy qokedy chckhdy sar | zuerst/zuletzt erwähnte Fracht wäre mit Fracht C unbeaufsichtigt ein gefährliches Paar. |
| 40–41 | schedair otchedy | Entsprechend für das andere/erste Frachtstück; erstes/zweites Paarargument ersetzen. |
| 42–44 | qokeedy chedain chedy | Als Nächstes zuerst/zuletzt erwähnte Fracht hinüberbringen. |
| 45–46 | qotedaiin otaiin | Das zuletzt beförderte Frachtstück dort lassen (Zielufer/gegenwärtiges Ufer). |
| 47–48 | otedy ldy | Allein zurückfahren. |
| 49–53 | tchedy qotedy qokal shedy qokedy | Abschließend fahren Begleitperson und Fracht C gemeinsam hinüber. |
| 54–57 | shecthedy shecthy otor chedy | Die zuletzt beförderte Fracht befindet sich nun bei den übrigen, darunter zuerst/zuletzt erwähnte Fracht. |
| 58–63 | soiiin checthy chety otaiin olsaly shedy | Somit sind alle unversehrt dort, begleitet von der Begleitperson. |

| Variante | Einstellungen | Gefährliche Paare | Die sieben tatsächlichen Ladungen | Aufgelöste Bezüge |
|---|---|---|---|---|
| V00 | exclude=EXCLUDING, first=FIRST, other=OTHER, there=GOAL, copy=FIRST | Fracht C + Fracht B; Fracht C + Fracht A | Fracht C → leer → Fracht B → Fracht C → Fracht A → leer → Fracht C | S11: FIRST_CARGO → Fracht A; S12: OTHER_CARGO → Fracht B; S13: FIRST_CARGO → Fracht A; S17: FIRST_CARGO → Fracht A |
| V02 | exclude=EXCLUDING, first=FIRST, other=OTHER, there=CURRENT, copy=FIRST | Fracht C + Fracht B; Fracht C + Fracht A | Fracht C → leer → Fracht B → Fracht C → Fracht A → leer → Fracht C | S11: FIRST_CARGO → Fracht A; S12: OTHER_CARGO → Fracht B; S13: FIRST_CARGO → Fracht A; S17: FIRST_CARGO → Fracht A |

Alle aufgeführten Pfade erreichen das Ziel ohne physischen Widerspruch, falsche Zustandsbehauptung oder unbeaufsichtigtes Gefahrpaar. Das bedeutet Konsistenz unter den angenommenen Regeln; es bedeutet keine unabhängige Bedeutungsbestätigung.

### BIJECTIVE Karte 42

Kohärente Bezugseinstellungen: [0, 2, 4, 6]. Alle übrigen der 32 Varianten widersprechen mindestens einer registrierten Folge; ihre vollständigen Ergebnisse stehen in FAMILY_BIJECTIVE.json.

| Form | Bedingte Terminalrolle |
|---|---|
| chckhdy | WOULD_BE |
| checthy | ALL |
| ched | WITHOUT_AGENT |
| chedain | NEXT |
| chedy | G |
| cheeety | RETURN_EXCLUDING |
| chety | UNHARMED |
| dal | BESIDES |
| lchedy | W |
| ldy | ALONE |
| lkedy | PAIRED_WITH |
| ockhey | FORBIDDEN |
| olsaly | ATTENDED_BY |
| opshedy | HOME |
| otaiin | THERE |
| otchedy | OTHER_CARGO |
| otedy | RETURN |
| otor | COLOC |
| otshdy | GOAL |
| pdalshdy | INIT |
| qetal | AT_MOST_ONE |
| qokal | TRAVEL_TOGETHER |
| qokchedy | UNATTENDED |
| qokedol | FAR_BANK |
| qokedy | C |
| qokeedy | CONVEY_OUT |
| qokeey | TAKE_OUT |
| qoky | FERRY |
| qotedaiin | LEAVE |
| qotedy | OUTWARD |
| qoteedy | B |
| saiin | FIRST_CARGO |
| sain | WHEN |
| sar | UNSAFE |
| schedair | LIKEWISE |
| shdy | WITHOUT_HARM |
| shecthedy | JOINING_RESULT |
| shecthy | REST_CARGO |
| shedaiin | PAIRS |
| shedy | M |
| shey | EXAMPLE |
| shocphedy | CARGOS |
| soiiin | THUS |
| sol | THEN |
| soldy | HARM |
| solkeedy | WITH_TRIP |
| tchedy | FINALLY |

| Gruppen (einsbasiert) | Vollständiger Wortlaut | Bedingte Lesung |
|---|---|---|
| 1–5 | pdalshdy shocphedy otor shedy opshedy | Die drei Frachtstücke befinden sich mit der Begleitperson am Ausgangsufer. |
| 6–9 | otshdy qokedol shdy soldy | Ziel ist das gegenüberliegende Ufer ohne Schaden. |
| 10–15 | sar shedaiin ockhey sain ched shedy | Gefährliche Paare dürfen nicht ohne Begleitperson zusammenbleiben. |
| 16–20 | qetal dal shedy shey lchedy | Höchstens ein Frachtstück neben der Begleitperson; Beispiel: Fracht A. |
| 21–24 | solkeedy qoteedy qokeey qokedy | Mit dem Boot Fracht C hinüberbringen. |
| 25–25 | sol | Dann. |
| 26–27 | cheeety qokedy | Ohne Fracht C zurückfahren (Gegenvariante: mit dieser Fracht). |
| 28–29 | qoky saiin | zuerst/zuletzt erwähnte Fracht zum jeweils anderen Ufer übersetzen. |
| 30–32 | solkeedy qokedy otedy | Mit Fracht C zurückfahren. |
| 33–33 | sol | Dann. |
| 34–39 | chedy lkedy qokchedy qokedy chckhdy sar | Fracht B wäre mit Fracht C unbeaufsichtigt ein gefährliches Paar. |
| 40–41 | schedair otchedy | Entsprechend für das andere/erste Frachtstück; erstes/zweites Paarargument ersetzen. |
| 42–44 | qokeedy chedain chedy | Als Nächstes Fracht B hinüberbringen. |
| 45–46 | qotedaiin otaiin | Das zuletzt beförderte Frachtstück dort lassen (Zielufer/gegenwärtiges Ufer). |
| 47–48 | otedy ldy | Allein zurückfahren. |
| 49–53 | tchedy qotedy qokal shedy qokedy | Abschließend fahren Begleitperson und Fracht C gemeinsam hinüber. |
| 54–57 | shecthedy shecthy otor chedy | Die zuletzt beförderte Fracht befindet sich nun bei den übrigen, darunter Fracht B. |
| 58–63 | soiiin checthy chety otaiin olsaly shedy | Somit sind alle unversehrt dort, begleitet von der Begleitperson. |

| Variante | Einstellungen | Gefährliche Paare | Die sieben tatsächlichen Ladungen | Aufgelöste Bezüge |
|---|---|---|---|---|
| V00 | exclude=EXCLUDING, first=FIRST, other=OTHER, there=GOAL, copy=FIRST | Fracht C + Fracht B; Fracht C + Fracht A | Fracht C → leer → Fracht A → Fracht C → Fracht B → leer → Fracht C | S08: FIRST_CARGO → Fracht A; S12: OTHER_CARGO → Fracht A |
| V02 | exclude=EXCLUDING, first=FIRST, other=OTHER, there=CURRENT, copy=FIRST | Fracht C + Fracht B; Fracht C + Fracht A | Fracht C → leer → Fracht A → Fracht C → Fracht B → leer → Fracht C | S08: FIRST_CARGO → Fracht A; S12: OTHER_CARGO → Fracht A |
| V04 | exclude=EXCLUDING, first=FIRST, other=FIRST, there=GOAL, copy=FIRST | Fracht C + Fracht B; Fracht C + Fracht A | Fracht C → leer → Fracht A → Fracht C → Fracht B → leer → Fracht C | S08: FIRST_CARGO → Fracht A; S12: OTHER_CARGO → Fracht A |
| V06 | exclude=EXCLUDING, first=FIRST, other=FIRST, there=CURRENT, copy=FIRST | Fracht C + Fracht B; Fracht C + Fracht A | Fracht C → leer → Fracht A → Fracht C → Fracht B → leer → Fracht C | S08: FIRST_CARGO → Fracht A; S12: OTHER_CARGO → Fracht A |

Alle aufgeführten Pfade erreichen das Ziel ohne physischen Widerspruch, falsche Zustandsbehauptung oder unbeaufsichtigtes Gefahrpaar. Das bedeutet Konsistenz unter den angenommenen Regeln; es bedeutet keine unabhängige Bedeutungsbestätigung.

### BIJECTIVE Karte 43

Kohärente Bezugseinstellungen: [0, 2]. Alle übrigen der 32 Varianten widersprechen mindestens einer registrierten Folge; ihre vollständigen Ergebnisse stehen in FAMILY_BIJECTIVE.json.

| Form | Bedingte Terminalrolle |
|---|---|
| chckhdy | WOULD_BE |
| checthy | ALL |
| ched | WITHOUT_AGENT |
| chedain | NEXT |
| chedy | FIRST_CARGO |
| cheeety | RETURN_EXCLUDING |
| chety | UNHARMED |
| dal | BESIDES |
| lchedy | G |
| ldy | ALONE |
| lkedy | PAIRED_WITH |
| ockhey | FORBIDDEN |
| olsaly | ATTENDED_BY |
| opshedy | HOME |
| otaiin | THERE |
| otchedy | OTHER_CARGO |
| otedy | RETURN |
| otor | COLOC |
| otshdy | GOAL |
| pdalshdy | INIT |
| qetal | AT_MOST_ONE |
| qokal | TRAVEL_TOGETHER |
| qokchedy | UNATTENDED |
| qokedol | FAR_BANK |
| qokedy | C |
| qokeedy | CONVEY_OUT |
| qokeey | TAKE_OUT |
| qoky | FERRY |
| qotedaiin | LEAVE |
| qotedy | OUTWARD |
| qoteedy | B |
| saiin | W |
| sain | WHEN |
| sar | UNSAFE |
| schedair | LIKEWISE |
| shdy | WITHOUT_HARM |
| shecthedy | JOINING_RESULT |
| shecthy | REST_CARGO |
| shedaiin | PAIRS |
| shedy | M |
| shey | EXAMPLE |
| shocphedy | CARGOS |
| soiiin | THUS |
| sol | THEN |
| soldy | HARM |
| solkeedy | WITH_TRIP |
| tchedy | FINALLY |

| Gruppen (einsbasiert) | Vollständiger Wortlaut | Bedingte Lesung |
|---|---|---|
| 1–5 | pdalshdy shocphedy otor shedy opshedy | Die drei Frachtstücke befinden sich mit der Begleitperson am Ausgangsufer. |
| 6–9 | otshdy qokedol shdy soldy | Ziel ist das gegenüberliegende Ufer ohne Schaden. |
| 10–15 | sar shedaiin ockhey sain ched shedy | Gefährliche Paare dürfen nicht ohne Begleitperson zusammenbleiben. |
| 16–20 | qetal dal shedy shey lchedy | Höchstens ein Frachtstück neben der Begleitperson; Beispiel: Fracht B. |
| 21–24 | solkeedy qoteedy qokeey qokedy | Mit dem Boot Fracht C hinüberbringen. |
| 25–25 | sol | Dann. |
| 26–27 | cheeety qokedy | Ohne Fracht C zurückfahren (Gegenvariante: mit dieser Fracht). |
| 28–29 | qoky saiin | Fracht A zum jeweils anderen Ufer übersetzen. |
| 30–32 | solkeedy qokedy otedy | Mit Fracht C zurückfahren. |
| 33–33 | sol | Dann. |
| 34–39 | chedy lkedy qokchedy qokedy chckhdy sar | zuerst/zuletzt erwähnte Fracht wäre mit Fracht C unbeaufsichtigt ein gefährliches Paar. |
| 40–41 | schedair otchedy | Entsprechend für das andere/erste Frachtstück; erstes/zweites Paarargument ersetzen. |
| 42–44 | qokeedy chedain chedy | Als Nächstes zuerst/zuletzt erwähnte Fracht hinüberbringen. |
| 45–46 | qotedaiin otaiin | Das zuletzt beförderte Frachtstück dort lassen (Zielufer/gegenwärtiges Ufer). |
| 47–48 | otedy ldy | Allein zurückfahren. |
| 49–53 | tchedy qotedy qokal shedy qokedy | Abschließend fahren Begleitperson und Fracht C gemeinsam hinüber. |
| 54–57 | shecthedy shecthy otor chedy | Die zuletzt beförderte Fracht befindet sich nun bei den übrigen, darunter zuerst/zuletzt erwähnte Fracht. |
| 58–63 | soiiin checthy chety otaiin olsaly shedy | Somit sind alle unversehrt dort, begleitet von der Begleitperson. |

| Variante | Einstellungen | Gefährliche Paare | Die sieben tatsächlichen Ladungen | Aufgelöste Bezüge |
|---|---|---|---|---|
| V00 | exclude=EXCLUDING, first=FIRST, other=OTHER, there=GOAL, copy=FIRST | Fracht C + Fracht B; Fracht C + Fracht A | Fracht C → leer → Fracht A → Fracht C → Fracht B → leer → Fracht C | S11: FIRST_CARGO → Fracht B; S12: OTHER_CARGO → Fracht A; S13: FIRST_CARGO → Fracht B; S17: FIRST_CARGO → Fracht B |
| V02 | exclude=EXCLUDING, first=FIRST, other=OTHER, there=CURRENT, copy=FIRST | Fracht C + Fracht B; Fracht C + Fracht A | Fracht C → leer → Fracht A → Fracht C → Fracht B → leer → Fracht C | S11: FIRST_CARGO → Fracht B; S12: OTHER_CARGO → Fracht A; S13: FIRST_CARGO → Fracht B; S17: FIRST_CARGO → Fracht B |

Alle aufgeführten Pfade erreichen das Ziel ohne physischen Widerspruch, falsche Zustandsbehauptung oder unbeaufsichtigtes Gefahrpaar. Das bedeutet Konsistenz unter den angenommenen Regeln; es bedeutet keine unabhängige Bedeutungsbestätigung.

### BIJECTIVE Karte 70

Kohärente Bezugseinstellungen: [0, 2, 4, 6]. Alle übrigen der 32 Varianten widersprechen mindestens einer registrierten Folge; ihre vollständigen Ergebnisse stehen in FAMILY_BIJECTIVE.json.

| Form | Bedingte Terminalrolle |
|---|---|
| chckhdy | WOULD_BE |
| checthy | ALL |
| ched | WITHOUT_AGENT |
| chedain | NEXT |
| chedy | G |
| cheeety | RETURN_EXCLUDING |
| chety | UNHARMED |
| dal | BESIDES |
| lchedy | C |
| ldy | ALONE |
| lkedy | PAIRED_WITH |
| ockhey | FORBIDDEN |
| olsaly | ATTENDED_BY |
| opshedy | HOME |
| otaiin | THERE |
| otchedy | OTHER_CARGO |
| otedy | RETURN |
| otor | COLOC |
| otshdy | GOAL |
| pdalshdy | INIT |
| qetal | AT_MOST_ONE |
| qokal | TRAVEL_TOGETHER |
| qokchedy | UNATTENDED |
| qokedol | FAR_BANK |
| qokedy | W |
| qokeedy | CONVEY_OUT |
| qokeey | TAKE_OUT |
| qoky | FERRY |
| qotedaiin | LEAVE |
| qotedy | OUTWARD |
| qoteedy | B |
| saiin | FIRST_CARGO |
| sain | WHEN |
| sar | UNSAFE |
| schedair | LIKEWISE |
| shdy | WITHOUT_HARM |
| shecthedy | JOINING_RESULT |
| shecthy | REST_CARGO |
| shedaiin | PAIRS |
| shedy | M |
| shey | EXAMPLE |
| shocphedy | CARGOS |
| soiiin | THUS |
| sol | THEN |
| soldy | HARM |
| solkeedy | WITH_TRIP |
| tchedy | FINALLY |

| Gruppen (einsbasiert) | Vollständiger Wortlaut | Bedingte Lesung |
|---|---|---|
| 1–5 | pdalshdy shocphedy otor shedy opshedy | Die drei Frachtstücke befinden sich mit der Begleitperson am Ausgangsufer. |
| 6–9 | otshdy qokedol shdy soldy | Ziel ist das gegenüberliegende Ufer ohne Schaden. |
| 10–15 | sar shedaiin ockhey sain ched shedy | Gefährliche Paare dürfen nicht ohne Begleitperson zusammenbleiben. |
| 16–20 | qetal dal shedy shey lchedy | Höchstens ein Frachtstück neben der Begleitperson; Beispiel: Fracht C. |
| 21–24 | solkeedy qoteedy qokeey qokedy | Mit dem Boot Fracht A hinüberbringen. |
| 25–25 | sol | Dann. |
| 26–27 | cheeety qokedy | Ohne Fracht A zurückfahren (Gegenvariante: mit dieser Fracht). |
| 28–29 | qoky saiin | zuerst/zuletzt erwähnte Fracht zum jeweils anderen Ufer übersetzen. |
| 30–32 | solkeedy qokedy otedy | Mit Fracht A zurückfahren. |
| 33–33 | sol | Dann. |
| 34–39 | chedy lkedy qokchedy qokedy chckhdy sar | Fracht B wäre mit Fracht A unbeaufsichtigt ein gefährliches Paar. |
| 40–41 | schedair otchedy | Entsprechend für das andere/erste Frachtstück; erstes/zweites Paarargument ersetzen. |
| 42–44 | qokeedy chedain chedy | Als Nächstes Fracht B hinüberbringen. |
| 45–46 | qotedaiin otaiin | Das zuletzt beförderte Frachtstück dort lassen (Zielufer/gegenwärtiges Ufer). |
| 47–48 | otedy ldy | Allein zurückfahren. |
| 49–53 | tchedy qotedy qokal shedy qokedy | Abschließend fahren Begleitperson und Fracht A gemeinsam hinüber. |
| 54–57 | shecthedy shecthy otor chedy | Die zuletzt beförderte Fracht befindet sich nun bei den übrigen, darunter Fracht B. |
| 58–63 | soiiin checthy chety otaiin olsaly shedy | Somit sind alle unversehrt dort, begleitet von der Begleitperson. |

| Variante | Einstellungen | Gefährliche Paare | Die sieben tatsächlichen Ladungen | Aufgelöste Bezüge |
|---|---|---|---|---|
| V00 | exclude=EXCLUDING, first=FIRST, other=OTHER, there=GOAL, copy=FIRST | Fracht C + Fracht A; Fracht B + Fracht A | Fracht A → leer → Fracht C → Fracht A → Fracht B → leer → Fracht A | S08: FIRST_CARGO → Fracht C; S12: OTHER_CARGO → Fracht C |
| V02 | exclude=EXCLUDING, first=FIRST, other=OTHER, there=CURRENT, copy=FIRST | Fracht C + Fracht A; Fracht B + Fracht A | Fracht A → leer → Fracht C → Fracht A → Fracht B → leer → Fracht A | S08: FIRST_CARGO → Fracht C; S12: OTHER_CARGO → Fracht C |
| V04 | exclude=EXCLUDING, first=FIRST, other=FIRST, there=GOAL, copy=FIRST | Fracht C + Fracht A; Fracht B + Fracht A | Fracht A → leer → Fracht C → Fracht A → Fracht B → leer → Fracht A | S08: FIRST_CARGO → Fracht C; S12: OTHER_CARGO → Fracht C |
| V06 | exclude=EXCLUDING, first=FIRST, other=FIRST, there=CURRENT, copy=FIRST | Fracht C + Fracht A; Fracht B + Fracht A | Fracht A → leer → Fracht C → Fracht A → Fracht B → leer → Fracht A | S08: FIRST_CARGO → Fracht C; S12: OTHER_CARGO → Fracht C |

Alle aufgeführten Pfade erreichen das Ziel ohne physischen Widerspruch, falsche Zustandsbehauptung oder unbeaufsichtigtes Gefahrpaar. Das bedeutet Konsistenz unter den angenommenen Regeln; es bedeutet keine unabhängige Bedeutungsbestätigung.

### BIJECTIVE Karte 71

Kohärente Bezugseinstellungen: [0, 2]. Alle übrigen der 32 Varianten widersprechen mindestens einer registrierten Folge; ihre vollständigen Ergebnisse stehen in FAMILY_BIJECTIVE.json.

| Form | Bedingte Terminalrolle |
|---|---|
| chckhdy | WOULD_BE |
| checthy | ALL |
| ched | WITHOUT_AGENT |
| chedain | NEXT |
| chedy | FIRST_CARGO |
| cheeety | RETURN_EXCLUDING |
| chety | UNHARMED |
| dal | BESIDES |
| lchedy | C |
| ldy | ALONE |
| lkedy | PAIRED_WITH |
| ockhey | FORBIDDEN |
| olsaly | ATTENDED_BY |
| opshedy | HOME |
| otaiin | THERE |
| otchedy | OTHER_CARGO |
| otedy | RETURN |
| otor | COLOC |
| otshdy | GOAL |
| pdalshdy | INIT |
| qetal | AT_MOST_ONE |
| qokal | TRAVEL_TOGETHER |
| qokchedy | UNATTENDED |
| qokedol | FAR_BANK |
| qokedy | W |
| qokeedy | CONVEY_OUT |
| qokeey | TAKE_OUT |
| qoky | FERRY |
| qotedaiin | LEAVE |
| qotedy | OUTWARD |
| qoteedy | B |
| saiin | G |
| sain | WHEN |
| sar | UNSAFE |
| schedair | LIKEWISE |
| shdy | WITHOUT_HARM |
| shecthedy | JOINING_RESULT |
| shecthy | REST_CARGO |
| shedaiin | PAIRS |
| shedy | M |
| shey | EXAMPLE |
| shocphedy | CARGOS |
| soiiin | THUS |
| sol | THEN |
| soldy | HARM |
| solkeedy | WITH_TRIP |
| tchedy | FINALLY |

| Gruppen (einsbasiert) | Vollständiger Wortlaut | Bedingte Lesung |
|---|---|---|
| 1–5 | pdalshdy shocphedy otor shedy opshedy | Die drei Frachtstücke befinden sich mit der Begleitperson am Ausgangsufer. |
| 6–9 | otshdy qokedol shdy soldy | Ziel ist das gegenüberliegende Ufer ohne Schaden. |
| 10–15 | sar shedaiin ockhey sain ched shedy | Gefährliche Paare dürfen nicht ohne Begleitperson zusammenbleiben. |
| 16–20 | qetal dal shedy shey lchedy | Höchstens ein Frachtstück neben der Begleitperson; Beispiel: Fracht C. |
| 21–24 | solkeedy qoteedy qokeey qokedy | Mit dem Boot Fracht A hinüberbringen. |
| 25–25 | sol | Dann. |
| 26–27 | cheeety qokedy | Ohne Fracht A zurückfahren (Gegenvariante: mit dieser Fracht). |
| 28–29 | qoky saiin | Fracht B zum jeweils anderen Ufer übersetzen. |
| 30–32 | solkeedy qokedy otedy | Mit Fracht A zurückfahren. |
| 33–33 | sol | Dann. |
| 34–39 | chedy lkedy qokchedy qokedy chckhdy sar | zuerst/zuletzt erwähnte Fracht wäre mit Fracht A unbeaufsichtigt ein gefährliches Paar. |
| 40–41 | schedair otchedy | Entsprechend für das andere/erste Frachtstück; erstes/zweites Paarargument ersetzen. |
| 42–44 | qokeedy chedain chedy | Als Nächstes zuerst/zuletzt erwähnte Fracht hinüberbringen. |
| 45–46 | qotedaiin otaiin | Das zuletzt beförderte Frachtstück dort lassen (Zielufer/gegenwärtiges Ufer). |
| 47–48 | otedy ldy | Allein zurückfahren. |
| 49–53 | tchedy qotedy qokal shedy qokedy | Abschließend fahren Begleitperson und Fracht A gemeinsam hinüber. |
| 54–57 | shecthedy shecthy otor chedy | Die zuletzt beförderte Fracht befindet sich nun bei den übrigen, darunter zuerst/zuletzt erwähnte Fracht. |
| 58–63 | soiiin checthy chety otaiin olsaly shedy | Somit sind alle unversehrt dort, begleitet von der Begleitperson. |

| Variante | Einstellungen | Gefährliche Paare | Die sieben tatsächlichen Ladungen | Aufgelöste Bezüge |
|---|---|---|---|---|
| V00 | exclude=EXCLUDING, first=FIRST, other=OTHER, there=GOAL, copy=FIRST | Fracht C + Fracht A; Fracht B + Fracht A | Fracht A → leer → Fracht B → Fracht A → Fracht C → leer → Fracht A | S11: FIRST_CARGO → Fracht C; S12: OTHER_CARGO → Fracht B; S13: FIRST_CARGO → Fracht C; S17: FIRST_CARGO → Fracht C |
| V02 | exclude=EXCLUDING, first=FIRST, other=OTHER, there=CURRENT, copy=FIRST | Fracht C + Fracht A; Fracht B + Fracht A | Fracht A → leer → Fracht B → Fracht A → Fracht C → leer → Fracht A | S11: FIRST_CARGO → Fracht C; S12: OTHER_CARGO → Fracht B; S13: FIRST_CARGO → Fracht C; S17: FIRST_CARGO → Fracht C |

Alle aufgeführten Pfade erreichen das Ziel ohne physischen Widerspruch, falsche Zustandsbehauptung oder unbeaufsichtigtes Gefahrpaar. Das bedeutet Konsistenz unter den angenommenen Regeln; es bedeutet keine unabhängige Bedeutungsbestätigung.

### BIJECTIVE Karte 72

Kohärente Bezugseinstellungen: [0, 2]. Alle übrigen der 32 Varianten widersprechen mindestens einer registrierten Folge; ihre vollständigen Ergebnisse stehen in FAMILY_BIJECTIVE.json.

| Form | Bedingte Terminalrolle |
|---|---|
| chckhdy | WOULD_BE |
| checthy | ALL |
| ched | WITHOUT_AGENT |
| chedain | NEXT |
| chedy | FIRST_CARGO |
| cheeety | RETURN_EXCLUDING |
| chety | UNHARMED |
| dal | BESIDES |
| lchedy | G |
| ldy | ALONE |
| lkedy | PAIRED_WITH |
| ockhey | FORBIDDEN |
| olsaly | ATTENDED_BY |
| opshedy | HOME |
| otaiin | THERE |
| otchedy | OTHER_CARGO |
| otedy | RETURN |
| otor | COLOC |
| otshdy | GOAL |
| pdalshdy | INIT |
| qetal | AT_MOST_ONE |
| qokal | TRAVEL_TOGETHER |
| qokchedy | UNATTENDED |
| qokedol | FAR_BANK |
| qokedy | W |
| qokeedy | CONVEY_OUT |
| qokeey | TAKE_OUT |
| qoky | FERRY |
| qotedaiin | LEAVE |
| qotedy | OUTWARD |
| qoteedy | B |
| saiin | C |
| sain | WHEN |
| sar | UNSAFE |
| schedair | LIKEWISE |
| shdy | WITHOUT_HARM |
| shecthedy | JOINING_RESULT |
| shecthy | REST_CARGO |
| shedaiin | PAIRS |
| shedy | M |
| shey | EXAMPLE |
| shocphedy | CARGOS |
| soiiin | THUS |
| sol | THEN |
| soldy | HARM |
| solkeedy | WITH_TRIP |
| tchedy | FINALLY |

| Gruppen (einsbasiert) | Vollständiger Wortlaut | Bedingte Lesung |
|---|---|---|
| 1–5 | pdalshdy shocphedy otor shedy opshedy | Die drei Frachtstücke befinden sich mit der Begleitperson am Ausgangsufer. |
| 6–9 | otshdy qokedol shdy soldy | Ziel ist das gegenüberliegende Ufer ohne Schaden. |
| 10–15 | sar shedaiin ockhey sain ched shedy | Gefährliche Paare dürfen nicht ohne Begleitperson zusammenbleiben. |
| 16–20 | qetal dal shedy shey lchedy | Höchstens ein Frachtstück neben der Begleitperson; Beispiel: Fracht B. |
| 21–24 | solkeedy qoteedy qokeey qokedy | Mit dem Boot Fracht A hinüberbringen. |
| 25–25 | sol | Dann. |
| 26–27 | cheeety qokedy | Ohne Fracht A zurückfahren (Gegenvariante: mit dieser Fracht). |
| 28–29 | qoky saiin | Fracht C zum jeweils anderen Ufer übersetzen. |
| 30–32 | solkeedy qokedy otedy | Mit Fracht A zurückfahren. |
| 33–33 | sol | Dann. |
| 34–39 | chedy lkedy qokchedy qokedy chckhdy sar | zuerst/zuletzt erwähnte Fracht wäre mit Fracht A unbeaufsichtigt ein gefährliches Paar. |
| 40–41 | schedair otchedy | Entsprechend für das andere/erste Frachtstück; erstes/zweites Paarargument ersetzen. |
| 42–44 | qokeedy chedain chedy | Als Nächstes zuerst/zuletzt erwähnte Fracht hinüberbringen. |
| 45–46 | qotedaiin otaiin | Das zuletzt beförderte Frachtstück dort lassen (Zielufer/gegenwärtiges Ufer). |
| 47–48 | otedy ldy | Allein zurückfahren. |
| 49–53 | tchedy qotedy qokal shedy qokedy | Abschließend fahren Begleitperson und Fracht A gemeinsam hinüber. |
| 54–57 | shecthedy shecthy otor chedy | Die zuletzt beförderte Fracht befindet sich nun bei den übrigen, darunter zuerst/zuletzt erwähnte Fracht. |
| 58–63 | soiiin checthy chety otaiin olsaly shedy | Somit sind alle unversehrt dort, begleitet von der Begleitperson. |

| Variante | Einstellungen | Gefährliche Paare | Die sieben tatsächlichen Ladungen | Aufgelöste Bezüge |
|---|---|---|---|---|
| V00 | exclude=EXCLUDING, first=FIRST, other=OTHER, there=GOAL, copy=FIRST | Fracht C + Fracht A; Fracht B + Fracht A | Fracht A → leer → Fracht C → Fracht A → Fracht B → leer → Fracht A | S11: FIRST_CARGO → Fracht B; S12: OTHER_CARGO → Fracht C; S13: FIRST_CARGO → Fracht B; S17: FIRST_CARGO → Fracht B |
| V02 | exclude=EXCLUDING, first=FIRST, other=OTHER, there=CURRENT, copy=FIRST | Fracht C + Fracht A; Fracht B + Fracht A | Fracht A → leer → Fracht C → Fracht A → Fracht B → leer → Fracht A | S11: FIRST_CARGO → Fracht B; S12: OTHER_CARGO → Fracht C; S13: FIRST_CARGO → Fracht B; S17: FIRST_CARGO → Fracht B |

Alle aufgeführten Pfade erreichen das Ziel ohne physischen Widerspruch, falsche Zustandsbehauptung oder unbeaufsichtigtes Gefahrpaar. Das bedeutet Konsistenz unter den angenommenen Regeln; es bedeutet keine unabhängige Bedeutungsbestätigung.

### BIJECTIVE Karte 73

Kohärente Bezugseinstellungen: [0, 2, 4, 6]. Alle übrigen der 32 Varianten widersprechen mindestens einer registrierten Folge; ihre vollständigen Ergebnisse stehen in FAMILY_BIJECTIVE.json.

| Form | Bedingte Terminalrolle |
|---|---|
| chckhdy | WOULD_BE |
| checthy | ALL |
| ched | WITHOUT_AGENT |
| chedain | NEXT |
| chedy | C |
| cheeety | RETURN_EXCLUDING |
| chety | UNHARMED |
| dal | BESIDES |
| lchedy | G |
| ldy | ALONE |
| lkedy | PAIRED_WITH |
| ockhey | FORBIDDEN |
| olsaly | ATTENDED_BY |
| opshedy | HOME |
| otaiin | THERE |
| otchedy | OTHER_CARGO |
| otedy | RETURN |
| otor | COLOC |
| otshdy | GOAL |
| pdalshdy | INIT |
| qetal | AT_MOST_ONE |
| qokal | TRAVEL_TOGETHER |
| qokchedy | UNATTENDED |
| qokedol | FAR_BANK |
| qokedy | W |
| qokeedy | CONVEY_OUT |
| qokeey | TAKE_OUT |
| qoky | FERRY |
| qotedaiin | LEAVE |
| qotedy | OUTWARD |
| qoteedy | B |
| saiin | FIRST_CARGO |
| sain | WHEN |
| sar | UNSAFE |
| schedair | LIKEWISE |
| shdy | WITHOUT_HARM |
| shecthedy | JOINING_RESULT |
| shecthy | REST_CARGO |
| shedaiin | PAIRS |
| shedy | M |
| shey | EXAMPLE |
| shocphedy | CARGOS |
| soiiin | THUS |
| sol | THEN |
| soldy | HARM |
| solkeedy | WITH_TRIP |
| tchedy | FINALLY |

| Gruppen (einsbasiert) | Vollständiger Wortlaut | Bedingte Lesung |
|---|---|---|
| 1–5 | pdalshdy shocphedy otor shedy opshedy | Die drei Frachtstücke befinden sich mit der Begleitperson am Ausgangsufer. |
| 6–9 | otshdy qokedol shdy soldy | Ziel ist das gegenüberliegende Ufer ohne Schaden. |
| 10–15 | sar shedaiin ockhey sain ched shedy | Gefährliche Paare dürfen nicht ohne Begleitperson zusammenbleiben. |
| 16–20 | qetal dal shedy shey lchedy | Höchstens ein Frachtstück neben der Begleitperson; Beispiel: Fracht B. |
| 21–24 | solkeedy qoteedy qokeey qokedy | Mit dem Boot Fracht A hinüberbringen. |
| 25–25 | sol | Dann. |
| 26–27 | cheeety qokedy | Ohne Fracht A zurückfahren (Gegenvariante: mit dieser Fracht). |
| 28–29 | qoky saiin | zuerst/zuletzt erwähnte Fracht zum jeweils anderen Ufer übersetzen. |
| 30–32 | solkeedy qokedy otedy | Mit Fracht A zurückfahren. |
| 33–33 | sol | Dann. |
| 34–39 | chedy lkedy qokchedy qokedy chckhdy sar | Fracht C wäre mit Fracht A unbeaufsichtigt ein gefährliches Paar. |
| 40–41 | schedair otchedy | Entsprechend für das andere/erste Frachtstück; erstes/zweites Paarargument ersetzen. |
| 42–44 | qokeedy chedain chedy | Als Nächstes Fracht C hinüberbringen. |
| 45–46 | qotedaiin otaiin | Das zuletzt beförderte Frachtstück dort lassen (Zielufer/gegenwärtiges Ufer). |
| 47–48 | otedy ldy | Allein zurückfahren. |
| 49–53 | tchedy qotedy qokal shedy qokedy | Abschließend fahren Begleitperson und Fracht A gemeinsam hinüber. |
| 54–57 | shecthedy shecthy otor chedy | Die zuletzt beförderte Fracht befindet sich nun bei den übrigen, darunter Fracht C. |
| 58–63 | soiiin checthy chety otaiin olsaly shedy | Somit sind alle unversehrt dort, begleitet von der Begleitperson. |

| Variante | Einstellungen | Gefährliche Paare | Die sieben tatsächlichen Ladungen | Aufgelöste Bezüge |
|---|---|---|---|---|
| V00 | exclude=EXCLUDING, first=FIRST, other=OTHER, there=GOAL, copy=FIRST | Fracht C + Fracht A; Fracht B + Fracht A | Fracht A → leer → Fracht B → Fracht A → Fracht C → leer → Fracht A | S08: FIRST_CARGO → Fracht B; S12: OTHER_CARGO → Fracht B |
| V02 | exclude=EXCLUDING, first=FIRST, other=OTHER, there=CURRENT, copy=FIRST | Fracht C + Fracht A; Fracht B + Fracht A | Fracht A → leer → Fracht B → Fracht A → Fracht C → leer → Fracht A | S08: FIRST_CARGO → Fracht B; S12: OTHER_CARGO → Fracht B |
| V04 | exclude=EXCLUDING, first=FIRST, other=FIRST, there=GOAL, copy=FIRST | Fracht C + Fracht A; Fracht B + Fracht A | Fracht A → leer → Fracht B → Fracht A → Fracht C → leer → Fracht A | S08: FIRST_CARGO → Fracht B; S12: OTHER_CARGO → Fracht B |
| V06 | exclude=EXCLUDING, first=FIRST, other=FIRST, there=CURRENT, copy=FIRST | Fracht C + Fracht A; Fracht B + Fracht A | Fracht A → leer → Fracht B → Fracht A → Fracht C → leer → Fracht A | S08: FIRST_CARGO → Fracht B; S12: OTHER_CARGO → Fracht B |

Alle aufgeführten Pfade erreichen das Ziel ohne physischen Widerspruch, falsche Zustandsbehauptung oder unbeaufsichtigtes Gefahrpaar. Das bedeutet Konsistenz unter den angenommenen Regeln; es bedeutet keine unabhängige Bedeutungsbestätigung.

## Was die erhaltenen Konsequenzen nicht unterscheiden

Die sechs globalen Umbenennungen der drei anonymen Frachtstücke ändern keine Transportlogik. SYMMETRY.json gruppiert ausschließlich die elf projizierten Rollen und die Bezugsvariante unter diesen Umbenennungen: sechs Klassen bei BIJECTIVE und 18 bisher beobachtete bei FUNCTIONAL. Das beweist keine Gleichheit der nichtprojizierten Wörterbücher.

OBSERVATION_GROUPS.json gruppiert exakt identische gespeicherte Gefahrpaare, Zustandsfolgen und Ortsbezüge. Diese Gruppen gelten nur für die geprüften Zeugen. Unterschiedliche Referenzregeln oder Wortrollen bleiben in CANDIDATE_CONSEQUENCES.json sichtbar, selbst wenn sie auf diesem Verlauf dieselben Zustände ergeben. Singleton-Wörterbücher innerhalb einer positiven Projektion wurden nicht vollständig aufgezählt.

Zielufer und gegenwärtiges Ufer fallen an den beobachteten Ortsbezügen zusammen. Bei Karten ohne FIRST_CARGO hat dessen FIRST/RECENT-Einstellung keinen Effekt. Ein wiederholter Eigenname und ein korrekt aufgelöster Rückverweis können dieselbe Fahrtfolge beschreiben. Die Wortformen selbst identifizieren weder Boot, Person noch Pflanze unabhängig von der angenommenen Geschichte.
