# GDT1033: fester Galen-Rahmen NOT / Lebensmittel / SOLID_FOOD

## Entscheidung vor neuem Census

Nach Primärlektüre von RAW510, sämtlichen59 Parent-Einträgen,163/164/373/928,
608 und den gespeicherten Typ-/Scopegrenzen ist eine echte neue lokale
Konsequenz offen: Passt die geratene Typisierung zu **allen** Vorkommen des
zusätzlich festgelegten Rahmens? Die alten Ganzlesungen liefern die zwei
Motivationen, beweisen aber weder automatische Konstituentengrenzen noch die
Verallgemeinerung. Ein Gegenbeispiel verwirft genau diese neue Schreibregel;
kompatible Fälle behalten sie bedingt; offene Typen/fehlende Fälle stoppen den
Test. Keine Variante entscheidet die historische Bedeutung.

Kleinster ausreichender Versuch: ein vollständiger Census aller exakten lshedy
im bereits exponierten GDT928-Absatzpaket, ohne Optimierung. Gesamtbudget
10:47:16–11:07:16UTC, einschließlich Vorprüfung, Implementierung, Validierung und
Publikation. Kein längerer Solver, keine neuen Typen/Glossen/Quellen, keine
Schwellen-, Rahmen- oder Textreparatur. RAW510 und59Werte werden gehasht gebunden.
Die wissenschaftliche Regel ist vollständig in RAW510 und src/SPEC.json festgelegt.

## Feste Regel und Nenner

N={sshey,sol,oltydy,or}; S=lshedy. Für jedes exakte S werden auf derselben
physischen Zeile maximal seine zwei unmittelbaren Vorgänger betrachtet:

1. Zweiter Vorgänger inN: LONG=N X S, auch wenn X wiederum ein N ist.
2. Sonst unmittelbarer Vorgänger inN: SHORT=N S.
3. Sonst OUTSIDE_CONTRACT; kein anderer Abstand oder Zeilenübergang.

LONG verlangt einen einzelnen bereits typisierten Lebensmittelterm bei X:
shedy,qokain,okedy,char,cheey,qokopy,dal,aiin sind FOOD_TYPE_POSSIBLE. Die letzten
drei behalten ihre unbestätigten Bezugs-/Nominalisierungsbedingungen. olor
bleibt OPEN_TYPE, weil eine Pflanze nicht automatisch essbar ist. Alle50übrigen
alten Formen sind FIXED_TYPE_CONFLICT unter der expliziten Null-Koerzions-Regel.
Unbekannte Formen bleiben UNKNOWN_WORD. SHORT benötigt einen noch zu bindenden
Kontextreferenten und ist kein positiver Bedeutungsbeleg.

Alle drei Transkriptionen getrennt, keine Unabhängigkeit der Lesarten. Jede
Absatzmetadatenzeile wird bewahrt. Vor Wortzugriff: f84-Präfix undf116v ablehnen,
Seiten-/Blattidentität prüfen, ganze Entwicklungsblätter76/80 ausschließen.
Danach wird jedes vorhandene S gezählt. Eine lokale Form ist nur primär, wenn
die ganze betreffende Zeile anchor_eligible exaktTrue hat; anderenfalls
SOURCE_UNCERTAIN, unabhängig davon, wie schön die Nachbarwörter passen.
Unsichere andere Zeilen desselben ganzen Absatzes bleiben vorhanden und werden
nicht ausgelassen, geglättet oder als Wortbedeutung interpretiert. Das ist ein
lokaler wörtlicher Rahmen ohne Absatzrang oder vollständigen Antezedentenzensus;
die unveränderte Ganzabsatzregel von1031 wird damit nicht neu ausgeführt.

Der ganze umgebende Absatz bleibt unter seiner ID/Hash im unveränderten Paket
nachlesbar. EVENT-Tabelle zeigt jeden S-Fall, nicht nur LONG oder günstige X.
Unsichere Schreibungen von S werden nicht als exaktes S normalisiert. Fokalwort-
Auswahl und beide Entwicklungsabsätze sind bekannt; kein historisch blinder
Holdout. RAW507/1031 und das Gesamtprojekt hatten das Paket bereits exponiert.

## Vorab festgelegte Entscheidung

JeLesart: kein Absatzvertrag→NO_OWNED_PARAGRAPH_DATA; mindestens ein primärer
Konflikt→REFUTED_FIXED_LOCAL_WRITER; sonst mindestens ein FOOD_TYPE_POSSIBLE→
CONDITIONAL_COMPATIBILITY_ONLY; sonst mindestens ein primärer LONG→
NO_TYPED_DISCRIMINATION; sonstNO_CAPACITY. Offene/unbekannte und unsichere Fälle
werden in jeder Zeile mitberichtet. Globale Zusammenfassung lautet
READING_SPECIFIC_COUNTEREXAMPLE, wenn mindestens eine Lesart widerspricht;
sonst CONDITIONAL_COMPATIBILITY_ONLY bei mindestens einer kompatiblen Lesart;
sonst NO_TYPED_DISCRIMINATION bei offenenLONGs; sonstNO_CAPACITY. Das Wort
READING_SPECIFIC behauptet keine Wiederholung im anderen Reader.

Ein gleichzeitiger kompatibler Fall hebt einen Widerspruch nicht auf.
Verschachtelte Negation, zufällige Nachbarschaft über Satzgrenzen, opake
Slotgrammatik oder andere Konstituenten sind vorab Alternativen; sie werden
nicht als nachträgliche Ausnahme des geprüften Schreibers eingebaut.
Keine der Entscheidungen bestätigt NOT, SOLID_FOOD oder einen Pflanzennamen.
Die Gleichheit struktureller Rollen mit anderen Bedeutungen bleibt offen.

## Artefakte und unabhängige Prüfung

SCOPE.json: alle Metadatenzeilen, Absatz/Seite/Blatt/Gruppen/Zeilenflags und
DEVELOPMENT beziehungsweiseIN_SCOPE. EVENTS.json: sämtliche nicht ausgeschlossenen
exakten S, einschließlich OUTSIDE_CONTRACT und SOURCE_UNCERTAIN; genaue Form,
Position, Quell-IDs, feste LONG/SHORT-Auswahl und unveränderter Parent-Eintrag
bei bekanntem X. RESULT.json enthält alle Lesartnenner und Entscheidungen.
Der unabhängig geschriebene Validator rekonstruiert diese Dateien direkt aus
den Eingaben, ohne Hauptcodeimport/-lektüre. Beide Programme und der Vertrag
werden vor Zielausführung gebunden. Vorprüfung nutzt nur künstliche Fälle:
alle59X×4N, unbekannterX, unsichere Zeile, überlappendeN, Zeilengrenze,
Entwicklungs- und Sperrselektoren mit nichtlesbarer Gift-Nutzlast.

Dies ist ein formaler lokaler Grammatik-/Typfalsifier einer geratenen Lesung,
kein neu erworbenes gerichtetes Inschrift-zu-Inschrift-Bedeutungspaket. Der
GDT388-Scoregate wird weder beansprucht noch durch diese Auswertung ersetzt;
die dokumentierte Endpunktunterscheidung gilt. Keine Signifikanzbehauptung,
kein Vergleich unter einer vorgetäuschten Gesamt-Suchnull. Kein Reservebild,
f84/f84r oderf116v, keine neue externe Quelle oder Kontaktaufnahme.
