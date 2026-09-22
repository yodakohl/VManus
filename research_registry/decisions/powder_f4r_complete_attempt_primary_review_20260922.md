# f4r: unabhängige Kritik des vollständigen eingefrorenen Autorenversuchs

2026-09-22. Gelesen wurden die ganze [MD-Vorlage](../proposals/raw370_f4r_complete_extension_attempt_20260922.md)
und das [JSON](../proposals/raw370_f4r_complete_extension_attempt_20260922.json),
einschließlich aller 62 Positionen, 13 neuen Werte, 11 Klauselabsichten,
Kostenlisten, vier Rivalen und vier erhaltenen erfolglosen Varianten.
Keine neue Glosse, Konstruktion oder Materialwirkung wird durch diese Kritik
ergänzt. Kein weiterer Absatz, Corpuslauf, Simulator, Bild oder Quelle.

**Ergebnis:** Kein vollständiger legaler Abschluss aus den tatsächlich
deklarierten Regeln wurde gefunden. Die beste Fassung bleibt MISSING_BINDING
für Grammatik und Materialfluss. Sie ist nicht als Ganzes durch einen
unvermeidlichen Typwiderspruch widerlegt. Die neun aufgelisteten Kostenpunkte
sind zudem keine nachgewiesenen neun unabhängigen Nichtdefault-Bindungen.
Einige Pflichten können sich vorhandene allgemeine Regeln teilen. Das
rechtfertigt keine automatische Fertigmeldung: Die angebotenen D1/M2-Schemata
liefern noch keine vollständige Ableitung der beabsichtigten Fortsetzung.

## Bindings und Vollständigkeit

- JSON SHA256 stimmt: `677776574fd892b7034d999f59e521054172eeef907f5020c1de704767cb0ba8`.
- MD SHA256 stimmt: `e2f9ff723159796ef0cb66eb37eaa71fbe702252981047bc114e652f7db479bd`.
- Parent-V2, SELECTED und MD entsprechen ihren JSON-Hashbindings.
- Beide ganzen Originalabsätze sind strukturell identisch mit SELECTED.
  Alle 31+31 Rohformen und IDs bleiben in derselben Reihenfolge erhalten.
  Jede Positionszuordnung stimmt exakt mit ihrem alten oder neu angebotenen
  Eintrag; ZL 17 alte Positionen, IT 18. Alle 13 neuen exakten Formen bleiben
  eigenständige Ganzformannahmen; `chaiin` hat überall denselben PARTLY-Wert.
- Alle 65 alten Einträge, 15 alten Aliasannahmen, 18 Produktionen und V2-
  `global_effects` sind unverändert. Die neue Entitätsform `@163;s` wurde
  nicht normalisiert, sondern ausdrücklich neu mit EVENLY belegt.

Die 13 neuen Werte wurden vollständig geprüft: MOIST_PLANT_MEAL, FINALLY,
WATER, UNTIL, CLEAN, WORK_INTO_PASTE, DECANT, PARTLY, EVENLY, RETRIEVE,
ENTIRELY, FINE_PART und POWDER. Es gibt dabei keine versteckte alte
Wortwertänderung. Neue Aliaswerte sind trotzdem neue fitted Annahmen.
WORK_INTO_PASTE und DECANT sind ausdrücklich zusätzliche Effektvokabeln;
sie dürfen nicht als schon getestete Folgen der alten KNEAD-/KEEP-Regeln gelten.

## Vollständige Klausel- und Flussprüfung

| Klausel / Positionen | Befund und genaue Grenze |
|---|---|
| C1, .1:1 | Neues feuchtes Mahlgut enthält laut Eintrag Wasser sowie groben und feinen Feststoff. Das ist ein initialer benannter Bestand, keine nachträgliche zweite Hilfsstoffzufuhr. Mengen, Körnung und Feuchte sind unbestätigte Bedingungen. |
| C2, .1:2–3 | FINALLY/D1 verschiebt eine DRY-Operation. Das ist als neue Konstruktion offengelegt; derselbe alte DRY-Effekt bleibt erhalten. Scope bis Absatzende und späterer Patient sind noch eigens zu binden. Keine kostenlose Manner-Deutung und keine schon vorhandene alte Reihenfolgeregel. |
| C3, .1:4–9 | M2 liefert die neue Reihenfolge WITH_MEDIUM PartitionOperation SupplyKind. Neues WATER passt zur Wasserbeschränkung. G2/UNTIL kann anschließend bereits POWDER/CLEAN an den ausgewählten SIEVE-Ausgang binden. Die Trägerwasserverteilung und die geforderte reine Grobrestform folgen daraus nicht vollständig. |
| C4, .2:1–4 | WORK_INTO_PASTE setzt genügend vorhandene Feuchte voraus und bewahrt Solid/Wasser ohne Ölzufuhr. ZLs zweimaliges KEEP kann denselben freien T betreffen; es kopiert keine Masse. ITs zusätzliches FINE ist nicht als Manner frei verwendbar und braucht die angebotene, noch unlizenzierte Ergebnis-/Feststoffbindung. |
| C5, .2:5–7 | DECANT benennt ausdrücklich die mögliche Freisetzung von J. Es ist daher kein ungeschrieben erzeugter alter Wasserbestand. Positives mobiles Wasser muss jedoch nach dem ersten SIEVE im Pastenast vorhanden sein. PARTLY bleibt bei DECANT und GRIND dieselbe Teilmengenartangabe. |
| C6, .2:8–9 und .3:1 | RETRIEVE ENTIRELY COARSE_GRIST ist eine nachvollziehbare Kombination der alten Wiederaufnahme mit neuem Manner-Wert; die Zeilengrenze verhindert sie nicht. Benötigt wird genau ein freier, rein grober passender Rest. Weder neue R-Masse noch eine beliebige Typumbenennung sind zulässig. |
| C7, .3:2–4 | FINE soll den bearbeiteten echten Teil von R als Ergebnis bestimmen. Damit wird der unmittelbare N1-Konflikt vermieden, aber nur als ausdrücklich andere Ergebnisbindung. GRIND selbst darf nur erhalten/verkleinern; PARTLY allein legt noch nicht den all-feinen Endpunkt des bearbeiteten Teils fest. |
| C8, .3:5–7 | SEPARATE Q FINE_PART soll die neue feine Ausgabe messen. Weder D1 noch M2 enthält diese Mess-/Ausgabekonstruktion. N1 hat den Kopf vor seinem Mengenlauf; P1/P2 liefern nicht automatisch diese konkrete Folge. Dies bleibt eine echte unvollständige Ableitung des angebotenen Baums. |
| C9, .4:1–4 | Fronted COARSE_PART und POWDER Q sollen Eingabe und Ausgabe von GRIND sein. Die alte A1-Nachstellung ist als vorhandener Eingabebezug beschrieben; sie begründet die neue Ausgaberolle nicht von selbst. Ein allgemeiner Ergebnisrahmen könnte mehrere solche Stellen behandeln, wurde aber nicht als zusätzliche vollständige Regel angeboten. |
| C10, .4:5–6 | RINSE PLANT_MATERIAL soll U als Patienten und J als entfernte Zufuhr haben. cthy ist kein Wassername. Die benannte frühere Wasserherkunft macht J grundsätzlich möglich, aber weder seine tatsächliche Verfügbarkeit noch diese ganze Argumentbindung ist schon abgeschlossen. Eine allgemeine Klassenhierarchie wurde nicht erschöpfend geprüft; daraus folgt keine universelle RINSE-Syntax-Unmöglichkeit. |
| C11, aufgeschobenes .1:3 | Der letzte DRY-Schritt wäre erst nach festgelegter D1-Scope-/Patientenbindung ausführbar. Er ist kein Beleg für ein bis dahin trocken gebliebenes Material. Der DRY_STATE-Vorbehalt wird korrekt nicht als Rettung ausgenutzt. |

**Präzisierung zum ersten Grobrest:** Der neue kodalchy-Eintrag setzt bereits
positiven Grob- und Feinanteil. Wenn das unveränderte SIEVE nur teilt und der
ausgewählte Ausgang all-feines POWDER ist, muss positiver grober Feststoff
im übrigen Material verbleiben. „Kein positiver Grobanteil folgt“ wäre deshalb
zu stark. Nicht gesichert ist die stärkere Bedingung eines **rein groben**,
als COARSE_GRIST passenden gesamten Restes: Ein Teil der feinen Körnung
könnte ebenfalls zurückbleiben. Auch die Verteilung des enthaltenen Wassers
auf beide Ausgänge ist im alten Effekt nicht gebunden. Sie darf hier nicht
einfach als positive Wasserzuteilung an P ergänzt werden.

DECANT liefert bei erfüllter Vorbedingung eine wirkliche spätere J-Quelle.
Die Vorbedingung wird aber nicht dadurch wahr, dass eine plausible spätere
Verwendung für J vorhanden ist. Ebenso benötigt PARTLY eine Teilmengenwirkung,
ohne den unbearbeiteten Rest oder den bearbeiteten Teil als zusätzliche
kopierte Masse zu zählen. Die Vorlage behauptet richtigerweise keine bereits
erfolgreich durchlaufene Materialsimulation.

## Was die Kostenliste tatsächlich beweist

Die zwei ausgeschriebenen neuen Schemata sind D1 (Aufschub einer Operation)
und M2 (Medium–Partition–Mittel-Reihenfolge). Sie erschöpfen das bewilligte
Kontingent, lösen jedoch nicht selbst die Ergebnis- und Messkonstruktionen
in C7–C9. Mit **genau diesen** angebotenen Schemata ist der beabsichtigte Baum
daher noch nicht vollständig lizenziert. Daraus folgt keine Mindestzahl
neuer Schemata über alle denkbaren Grammatiken. Insbesondere könnte ein
einziger tatsächlich formulierter allgemeiner Ergebnisrahmen mehrere
Ergebnis-/Eigenschaftsstellen zugleich behandeln. Eine solche Regel wurde
in dieser Kritik nicht nachgetragen oder als kostenlos angenommen.

Auch `count_as_listed=9` ist als Aufzählung richtig, aber keine gesicherte
Zahl von neun zusätzlichen Nichtdefault-Entscheidungen:

- Der neue PARTLY-Eintrag ist ausdrücklich eine Artangabe mit derselben
  Proper-Subportion-Bedeutung. Alte Adjunktregeln gestatten Artangaben an ihrer
  unmittelbar zugehörigen Operation vor oder nach dem Verb. Die beiden
  postverbalen Bindungen an DECANT und GRIND können daher schon gewöhnliche
  Anwendungen dieses Lexikoneintrags sein. Die Definition neuer Semantik
  ist eine Kostenposition, aber nicht automatisch eine weitere freie
  Scopeentscheidung zusätzlich zur lexikalischen Festlegung.
- POWDER/CLEAN am ausgewählten SIEVE-Ausgang ist bereits die alte G2/UNTIL-
  Folge. Zusätzlich unbestätigt sind der reine Grobrest und der Wasserweg;
  sie sind nicht mit dieser bereits lizenzierten Ausgangsbindung zu vermengen.
- Eine allgemeine Ergebnisregel könnte ITs FINE und den späteren FINE-
  Resultatscope gemeinsam behandeln; ihre tatsächlichen Parameterbindungen
  wären dennoch einzeln offenzulegen. Ob dies weitere Kosten spart, kann
  erst eine ausgeschriebene vollständige Regel zeigen.

Somit sollte der wissenschaftliche Stopp auf **nicht abgeschlossener
Konstruktion und offenem Materialfluss unter dem festen Budget** beruhen.
Die stärkere Aussage „mindestens neun nichtdefault Bindungen erforderlich“
ist nicht bewiesen. Eine bloße Umbenennung oder Zusammenfassung der Kosten
schließt den Versuch allerdings ebenfalls nicht ab. Keine vollständig
ausgeschriebene, schon deklarierte Lösung innerhalb aller Grenzen wurde
bei dieser Prüfung gefunden; es fand keine erschöpfende Grammatiksuche statt.

## Harte Konflikte, offene Flüsse und fehlende neue Unterscheidung

Die erhaltenen **fest gebundenen** Fehlvarianten sind korrekt enger als die
allgemeine Fragestellung:

- A_SERIAL_OIL verletzt mit OIL als WITH_MEDIUM-Argument die eingefrorene
  Wasserbeschränkung. Der gleichpatientige serielle WATER-Ersatz nach DRY
  hat kein verbleibendes enthaltenes Wasser. Andere Scopebindungen sind
  dadurch nicht allgemein ausgeschlossen.
- C_LITERAL_COARSE_FINE verletzt als eine simultane N1-NP tatsächlich die
  disjunkten Grade. Der beste Entwurf behauptet diese NP gerade nicht.
- D_WHOLE_FINE_GRIND lässt unter seinen festgelegten Eingabe-/Ausgabebindungen
  keinen positiven Grobzweig derselben neuen Partition übrig. Ein anderer
  Herkunftsrahmen wäre ein anderer Vertrag, nicht die geräuschlose Rettung.
- B_SPREAD_FINAL_WATER bleibt ohne Quelle des freien J und mit offenem
  Q-Besitzer unvollständig. Nur **wenn** Q WATER selbst messen soll, entsteht
  der feste Dimensionskonflikt; ungebundene Mengen sind zunächst Lücken.

Die beste FINALLY/DECANT-Fassung vermeidet diese konkreten Bindungen, bezahlt
dafür aber neue Annahmen und schließt den Fluss noch nicht. Der gedachte
Schluss R=2Q und N=p+2Q folgt erst bei lizenzierten beiden Q-Ausgängen,
richtiger Herkunft, Erschöpfung und Feststofferhaltung. Er ist zurzeit eine
bedingte Aussicht, keine neu festgestellte Mengengleichung.

CARRY und FRESH bleiben im angebotenen Baum an denselben Lücken stehen;
ohne alte P2-/J1-Eingangslistenkonstruktion liefert FRESH nicht automatisch
R oder J neu. Die beiden getrennten daiin bilden keinen Q-Q-Lauf. Daher
liefert f4r keine neue ADD/REITERATED/TWO-Unterscheidung. Die alte bedingte
REITERATED-Widerlegung und die ADD/TWO-Gleichwertigkeit bleiben unverändert.

Der angemessene Abschluss ist ein erhaltener vollständiger Wortentwurf mit
präzisen unvollständigen Bindungen und einer qualifizierten Kostenkritik,
keine allgemeine Unmöglichkeit von f4r und kein Bedeutungs-PASS. Null
bestätigte Wörter; die unveränderte Auswahlkapazität aus GDT1036 ist kein
Nachweis des neuen Inhalts.
