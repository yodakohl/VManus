# GDT1039 — gemeinsame Verweisregel im ganzen Stunden-/Tagesentwurf

**Ergebnis:** Eine einzige typisierte Abrufregel erzeugt die sieben vorgegebenen
Bezüge der vollständigen normalisierten80-Gruppen-Lesung. Ihre zwei Varianten
wirken zusammen: Erst frühe Veröffentlichung des laufenden Ergebnisses **und**
nichtverbrauchender Abruf machen beide Schlussvergleiche zu Selbstvergleichen.
Das ist eine nachgewiesene bedingte Eigenschaft dieses verfassten Modells, keine
neue Beobachtung über die Manuskriptbedeutung. Die Regel ist nicht ausgewählt.

Alle sechs Regeln, zwölf Konstruktionen,80 Positionen und357 alten Zahlenpaare
wurden ausgeführt; die unabhängige Implementierung bestätigt alle2142 Zeilen und
31 tatsächlich erreichten Abrufe. Die vollständigen Tabellen stehen in
[COMPARISON_TABLE.json](artifacts/COMPARISON_TABLE.json), die sichtbaren Kandidaten,
Erwähnungsreihenfolgen und Verbrauchsmengen in
[EVENT_TRACES.json](artifacts/EVENT_TRACES.json). Die kompakte nachprüfbare Tabelle
steht in [CANDIDATE_PREDICTIONS.tsv](artifacts/CANDIDATE_PREDICTIONS.tsv).

## Vorhersagen und Beobachtungen je Verweisregel

D=Tageseinheit, U=Stundeneinheit, N=gesetzte24, A/B=Rechnungsrecords,
RA/RB=provenienzverschiedene Ergebnisrecords. Diese Namen sind Modellbegriffe.
T/F sind wahre/falsche Gleichheitsansprüche; U bedeutet ungebunden.

| Vollständige Regel | Vorher festgelegte und beobachtete Bezüge | Wenn A≠B: C11,C12 | Alle357 alten Paare | Widerspruch und verbleibende Mehrdeutigkeit |
|---|---|---|---|---|
| DEFERRED_CONSUMING | D,D,U,N,RA,B,A | F,F | 56 T/T;301 F/F | Beide Schlussansprüche verlangen A=B; Regel bleibt angenommen. |
| DEFERRED_NONCONSUMING | D,D,U,N,RA,B,B | F,T | 56 T/T;301 F/T | C12 tautologisch; C11 erhält die gleiche Gesamtpflicht. |
| EAGER_CONSUMING | D,D,U,N,RB,B,A | T,F | 56 T/T;301 T/F | C11 tautologisch; C12 erhält die gleiche Gesamtpflicht. |
| EAGER_NONCONSUMING | D,D,U,N,RB,B,B | T,T | 357 T/T | Beide Ansprüche tautologisch; mehr Bestehen bedeutet hier weniger Inhalt. |
| UNTYPED_RECENT | C04 wählt U für verlangtes DAY | U,U | 357 ungebunden | Typfehler bereits am ersten Abruf; keine nachträgliche Auswahl von D. |
| GLOBAL_CONSUMPTION | C04 D; C07:40 kein unbenutztes DAY | U,U | 357 ungebunden | Wiedererwähnung erzeugt kein neues D; spätere Vergleiche nicht ausgeführt. |

Für A=B sind alle vier vollständigen Regeln numerisch ununterscheidbar. Auch
für A≠B haben die ersten drei denselben gemeinsamen Wahrheitswert, obwohl
unterschiedliche einzelne Aussagen falsch werden. Nur C12 enthält zwei
konkurrierende METHOD-Records; die anderen typisierten Auswahlen haben meistens
einen Kandidaten. Ob die Schrift nichtreflexive Vergleiche fordert oder welche
Veröffentlichungsgrenze gilt, ist damit nicht unabhängig gebunden.

## Alle alten Rechenfamilien, ohne Auswahl günstiger Fälle

Die Tabelle nennt T/T-Zeilen. Bei den ersten drei Regeln sind die verbleibenden
Zeilen jeweils F/F, F/T beziehungsweise T/F. Beide ungebundenen Regeln stoppen
in sämtlichen Zeilen jeder Familie. Die Originalwerte und Kosten sind über
row_index an die unveränderten357 Originalzeilen gebunden und zusätzlich in der
neuen Tabelle für die verwendeten Felder erhalten.

| Geerbte Familie | Zeilen | Jede der ersten drei Regeln T/T | EAGER_NONCONSUMING T/T | Erhaltene ursprüngliche Einschränkung |
|---|---:|---:|---:|---|
| PRIMARY | 7 | 7 | 7 | Alle60 Wortwerte und12 Konstruktionen geraten. |
| AT_LAST | 7 | 0 | 7 | Geänderter Endpunktwert; seine Abweichung bleibt erhalten. |
| AFTER_FIRST_UNSKIPPED | 7 | 0 | 7 | Zusätzlicher Auswahlschritt bleibt Zusatzannahme. |
| ONE_REFERENT_FOR_DOUBLE | 7 | 0 | 7 | Geänderte Zusammenfassung der beiden Einheitsoperanden. |
| SAME_METHOD_REFERENCE | 7 | 7 | 7 | Altes C12=B/B hier ausdrücklich durch jeweilige neue Regel ersetzt. |
| NIGHT_REVERSE | 161 | 21 | 161 |23 Tageslichtdauern; nur3,10,17 erfüllen A=B. Nachtfolge geändert. |
| NIGHT_RESET | 161 | 21 | 161 |23 Tageslichtdauern; nur7,14,21 erfüllen A=B. Reset bleibt Zusatzregel. |

357 T/T der schwachen Regel bedeuten **nicht**357 vollständige historisch
verträgliche Lesungen: C03/C08, C09, Wortänderungen und andere Quellenpflichten
bleiben bestehen. Der Resolver sieht keine Rechenwahrheit bei seiner Auswahl.
Ein falsches C11 verhindert deshalb nicht die strukturelle Veröffentlichung
und Auswertung von C12. RA und RB bleiben auch bei gleichem Zahlenwert getrennt.

## Datenabgrenzung, Annahmen und Entscheidung

Alle Daten waren bereits exponiert. Unabhängige Bestätigungskapazität: **0**,
bei jeder Regel. Es gibt keine neue Blattprüfung und keine Signifikanzkontrolle
der gesamten Suche. Die60 geratenen Werte, darunter45 Singleton-Typen, und zwölf
maßgeschneiderten Konstruktionen bleiben. Sieben dynamische Abrufe sind nicht
sieben sämtliche Bindungen: globaler Kreis und Anfangsphase, lokale Stunden,
Einheit/Instanz, Typdomäne und feste Grenzen sind weiterhin gesetzt.

Die80 Positionen stammen aus der normalisierten Arbeitskopie. Diplomatisch sind
Position37 `qok[ee:ch]dy` und54 `ra{cty}`; GDT1015s Quellenkorrektur bleibt
unverändert. Keine neue IT/RF-Lesung, keine Reserve, keine neuen Bilder oder
Kontakte. f84/f84r bleiben geschlossen. Bestätigte Wörter: **0**.

**Entscheidung:** Den gemeinsamen bedingten Referenzvertrag und die kombinierte
Gegenfolge behalten; keine der vier vollständigen Regeln allein dadurch auswählen.
Keine weitere Simulation derselben Gleichungen. Nötig ist jetzt eine zusätzliche
vollständige Textfolge mit unveränderten Werten oder eine unabhängig gebundene
Vergleichs-/Abschlussfunktion. GDT1015 und frühere feste Entscheidungen bleiben.

## Registrierung und Reproduktion

Vollständige manuelle Vorhersagen und Ereignisinventar wurden vor beiden
Implementierungen eingefroren. Öffentliche Registrierung:85747038aa4226c92552b412b7ccf5d189432972,
vor Primärlauf und357-Fälle-Replay um16:53UTC. Bereits vor der öffentlichen
Fixierung hatte der unabhängige Validator die zielabgeleitete Ereignisspur mit
fünf synthetischen Zahlenpaaren geprüft; dies ist in PREREGISTRATION vollständig
offengelegt und war kein blinder Test. Technische Korrekturen erfolgten vor dem
öffentlichen Lock. Nach dem Lock wurden Vertrag und Code nicht verändert.

Vorbereitung ab etwa16:26UTC; Budget bis17:01UTC einschließlich Veröffentlichung.
Beide Manifestbefehle reproduzieren Lauf und unabhängige Validierung. Der lokale
Validierungs-PASS ersetzt weder Bedeutungsbelege noch offene historische globale
Repositoryfehler. Die vierstündige Forschung läuft nach diesem Einzelversuch weiter.
