# GDT1154 — Ganzabsatzvergleich liefert keinen belastbaren internen Paralleltext

**Entscheidung: NO_ORDER_LEAD.** Der tatsächlich ausgeführte Vergleich von 6611 vollständigen Absatzpaaren findet keinen Treffer, der das vorab festgelegte Kriterium gegen Umordnungen ganzer Zeilen erfüllt. Das ist kein Nachweis gegen Abschrift, gemeinsame Vorlagen oder Bedeutung. Es ist ein fehlgeschlagener Versuch, auf dieser konkreten Grundlage einen internen Paralleltext für die Bedeutungsarbeit zu gewinnen. Keine Übersetzung gewonnen.

## Warum dieser Test

Die Entstehungshypothese war, dass bearbeitete Fassungen gemeinsamer Einträge trotz fehlender langer wortgleicher Passagen eine gemeinsame Reihenfolge über mehrere Zeilen bewahren könnten. GDT928 verlangt zwei getrennte exakte Mehrwortanker und bleibt ohne Kandidaten; GDT925 verlangt identische ganze Zeilenmultimengen; GDT914 prüft lokale Vierer-Editmuster. Keines dieser Kriterien wurde gelockert oder sein Entscheid ersetzt. Hier wird die längste gemeinsame Teilfolge ganzer Wörter über Absatzinnenzeilen verglichen, mit Lücken, ohne Zeichenänderungen oder Bedeutungszuweisungen.

Die Gegenprobe erhält jede einzelne Zeile einschließlich Wortfolge und Wortbestand vollständig. Nur die Innenzeilen jedes Absatzes werden unabhängig umgeordnet; Randzeilen bleiben erhalten, aber unbewertet. Jeder der199 Durchläufe durchsucht wiederum ALLE zulässigen Paare beider auswertbarer Lesungen. Somit wird der ausgewählte Besttreffer mit Besttreffern derselben gesamten Suche verglichen, nicht mit einem beliebigen Einzelpaar.

## Vollständige Abdeckung

| Lesung | Vollständige Quellabsätze | Zulässige Absätze | Geprüfte blattübergreifende Paare |
|---|---:|---:|---:|
| ZL3b |659|2|1|
| IT2a |690|141|6610|
| RF1b |0 bestimmbar|0|0|

Mindestens6 Zeilen, ausschließlich nach GDT928 sichere Ganzzeilen und mindestens20 Innengruppen; Längenverhältnis höchstens2. Alle Ausschlussgründe und Absatz-IDs stehen in artifacts/eligibility.json. Gründe überlappen: IT454/ZL422 Absätze sind zu kurz, IT167/ZL628 enthalten mindestens eine unzulässige Ganzzeile, IT301/ZL260 haben zu wenig Innengruppen. RF fehlen native Absatzmarkierungen; seine Null ist fehlende Prüfbarkeit. Die geringe ZL-Abdeckung ist eine wesentliche Grenze, keine dritte bestätigende Stimme.

## Der beste tatsächliche Treffer

IT2a **f82v.5–10 / f83v.1–8**, bewertete Innenzeilen f82v.6–9 und f83v.2–7:

- 41 beziehungsweise61 Wörter;17 multiset-gemeinsame Vorkommen.
- Längste geordnete Teilfolge12 Wörter; normierter Wert24/102 =0,235294.
- Gewählter deterministischer Vergleich: `dol shedy shedy dar dair qotedy qokal chedy qokol chedy chedy qokal`.
- Verteilt über4 beziehungsweise6 Innenzeilen; die räumliche Verteilungsbedingung wäre erfüllt.
- **117 von199 vollständigen Gegenproben erreichen mindestens denselben Maximalwert.** Der registrierte plus-one Rang ist118/200 =**0,59**, oberhalb des vorab gesetzten0,05-Kriteriums.
- Daher kein nominiertes Paar. Keine Ersatzwahl des zweitbesten Treffers.

[CANDIDATE_TABLE.md](CANDIDATE_TABLE.md) zeigt die zehn besten IT-Paare und das einzige ZL-Paar. [WHOLE_CONTEXTS.md](WHOLE_CONTEXTS.md) enthält ihre vollständigen Absätze, die deterministischen Zuordnungen mit Originalgruppen-IDs und die Absatzverfügbarkeit in alternativen Lesungen. artifacts/ALL_PAIRS.tsv enthält alle6611 Paarwerte; NULL_MAXIMA.json sämtliche199 Suchmaxima samt Gewinnern. Die Tabellen sind deskriptiv, keine Herkunftskanten oder Bedeutungsbeweise.

## Was wir daraus entscheiden — und was nicht

Der scheinbar beste gemeinsame Ablauf ist unter diesem Vergleichsmaß nicht von den Gegenproben abgehoben. Damit fehlt ein Grund, gerade dieses Paar als zwei Fassungen desselben Eintrags zu übersetzen. Diese Route wird unter unverändertem Maß nicht weiter ausgebaut. Insbesondere keine nachträgliche Kürzung der Absätze, Verschmelzung ähnlicher Wörter, Normalisierung von Endungen oder Wahl eines vorteilhaften Lesers.

Das Entstehungsmodell bleibt offen. Die Prüfung erfasst nur erhaltene Reihenfolge exakt gleicher Ganzformen in vollständig sicheren längeren Absätzen. Stark bearbeitete Vorlagen, systematische Schreibtransformationen, kürzere Einträge und unsichere Transkriptionen können ihr entgehen. Umgekehrt hätte ein positiver Rang auch aus gemeinsamer Absatzgliederung statt gemeinsamer Herkunft entstehen können. Der Test kann daher gemeinsame Vorlage und lokale Textumbildung nicht generell entscheiden; er prüft die Eignung konkreter Kandidaten für diese Unterscheidung. Ein nächster Herkunftsansatz benötigt eine gesondert begründete, wiederkehrende Bearbeitungsspur oder materielle Herstellungsbeobachtung; das vorliegende Ergebnis liefert sie nicht. Kein automatischer neuer Decoder oder weiterer Umordnungsversuch.

## Registrierung, Exposition und Prüfung

PREREGISTRATION.md und METHOD.md wurden zusammen mit der GDT928-Quelle und Herkunftsdateien lokal vor der neuen Bewertung hashgebunden. Keine öffentliche Vorabregistrierung: der Push folgt erst nach Abschluss. Ein Agent sah nach Registrierung, aber vor seiner Hashprüfung einen Ausschnitt des bereits bekannten JSON-Schemas; das ist im Ergebnis offengelegt. Alle Eingabepins wurden vor dem tatsächlichen Lauf verifiziert. Keine Regel nach Ergebnissen verändert.

Ein unabhängiger Prüfer rekonstruierte die Zulässigkeit und alle Paarwerte mit Hunt–Szymanski statt dem Bitset-Algorithmus des Runners, wiederholte sämtliche199 Gegenproben und prüfte ausgewählte vollständige Zuordnungen zusätzlich durch dynamische Programmierung. Der Prüfbericht steht in artifacts/VALIDATION.md. Beide Berechnungen erhielten unabhängig den Rang0,59.

Nur der bereits exponierte GDT928-Cache aus den179 zuvor freigegebenen Selektoren wurde verwendet. Keine neue Datenfreigabe, kein Bildzugriff, keine gemischte TSV und keine Kontakte. f84/f84r bleiben geschlossen; f116v unzugelassen; Reserven ungeöffnet. ZL/IT/RF repräsentieren ein Manuskript. Keine unabhängige Bestätigung oder bestätigte Wortbedeutung. Der Umordnungsrang beschreibt ausschließlich die registrierte künstliche Referenz; Austauschbarkeit realer Innenzeilen ist nicht nachgewiesen. Keine manuskriptweite Signifikanz oder Herkunftswahrscheinlichkeit. Textausgewählte Paarungen sind nicht GDT388-score-ready.

Abschlussprüfung:15/15 Prüfgruppen PASS, einschließlich aller6611 Paarwerte,199 Suchmaxima samt Gleichständen,1349 Absatzentscheidungen und11 vollständiger Vergleichspakete. Die ursprünglichen Nahtmarkierungen werden aus dem gebundenen928-Cache übernommen; kein erneuter Bild- oder915-Rohdatencheck. Arbeitszeit bis Veröffentlichungsprüfung etwa12Minuten einschließlich Vorbereitung, Umsetzung und unabhängiger Rechnung;45Minuten-Budget nicht ausgeschöpft.
