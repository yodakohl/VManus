# Übersetzungsplan: eine kleine Bedeutung rekonstruieren und übertragen

Stand: 2026-09-08. Status: **vorbereiteter Forschungsplan, kein ausgewählter
Bedeutungstest, keine neue Übersetzung**. Die bestehenden Nullbefunde bleiben
gültig. Dieser Plan ersetzt keinen Versuchsbericht und eröffnet keine geschlossene
Familie automatisch wieder.

## Entscheidung

Unser nächstes Ziel ist eine kurze, überprüfbare Bedeutungszuweisung, deren
Bausteine an einer anderen Text-Bild-Kombination dieselbe Arbeit leisten. Wir
sollten ein kleines zusammenhängendes System aus Schrift und Zeichnung gemeinsam
erschließen. Wir müssen dazu nicht vorher ein einzelnes Wort sicher übersetzt
haben. Wir müssen aber verhindern, dass eine frei erfundene Zuordnung jedes
Beispiel nachträglich erklärt.

Der erste Erfolg wäre etwa eine belastbare relationale Aussage über ein
dargestelltes Objekt oder einen Zustand. Ein thematisches Etikett wie
„Astronomie“, eine formale Endungsregel oder ein flüssiger deutscher Absatz
erreicht dieses Ziel nicht. Auch eine erfolgreiche Bedeutungszuweisung würde
Laute, Ursprungssprache und Verschlüsselungsverfahren noch offenlassen.

## Was die Vorgänger bereits ausschließen

| Primärbefund | Konsequenz für diesen Plan |
|---|---|
| [GDT360](../../experiments/yolo/gdt360_existing_annotation_joint_grounding/REPORT.md): gemeinsame Bildmerkmale lieferten keine unabhängige Bedeutungszuweisung. | Keine weitere breite Suche nach Wort-Bild-Korrelationen mit denselben Annotationen. |
| [GDT346](../../experiments/yolo/gdt346_compositional_operator_manifold/REPORT.md): unbekannte Kombinationen formaler Zustände/Operatoren waren schon Gegenstand eines erfolglosen Transfermodells. | „Komposition“ und das Zurückhalten einer Kombination sind allein keine neue Idee. Neu erforderlich ist eine unabhängig erkennbare Bildbedeutung als Ziel. |
| [GDT608](../../experiments/yolo/gdt608_compositional_stem_orientation/REPORT.md): formale Komponentenprofile übertragen teilweise; genaue Paaridentität bleibt nötig. | Keine automatische Zerlegung in übersetzbare Morpheme. Vollständige Formen und feste Mehrgruppen-Konstruktionen bleiben zulässige Einheiten. |
| [GDT794](../../experiments/yolo/gdt794_complete_label_multiform_slot_transfer/REPORT.md): wiederholte Ringinschriften ergeben keinen allgemeinen Winkel-/Platzschlüssel. | Keine neuen Rotationen, Abstandsmerkmale oder Zahlenglossen zur Rettung dieses Tests. |
| [GDT799](../../experiments/yolo/gdt799_f70_f71_f72_homolog_clothing_transition/REPORT.md): Bekleidung trägt teilweise Seiten-/Ringstil; die feste Positionsrelation ist nicht übertragbar. | Eine Bildklasse muss innerhalb geeigneter Vergleichsgruppen variieren. Bekleidung oder Seitenidentität allein reicht nicht. |
| [GDT809](../../experiments/yolo/gdt809_record_conditioned_whole_head_semantic_tournament/REPORT.md): vollständige konkurrierende Lesungen blieben ohne unterscheidende Bedeutungsbeobachtungen. | Keine neue Übersetzung gewinnt durch Sprachfluss, Abdeckung oder zusätzliche frei gesetzte Bedeutungen. |

Die geschlossene Familie `MINIMAL_PAIRS_ALLOGRAPHY_AND_SYNONYMS` verlangt neue
wiederkehrende Ersetzungen auf mehreren unabhängigen Seitenpaaren mit unberührter
Bestätigung. Die vorgeschlagene Erkundung erfüllt diese Bedingung derzeit nicht.
Sie darf keine alten Synonym-/Allographietests unter anderem Namen wiederholen.
Lexikalische Treffer aus `route-check`, `ideas search` und `ideas duplicates`
dienten der Navigation, nicht als Neuheitsnachweis.

## Hauptidee: eine tatsächlich gezeichnete neue Kombination vorhersagen

Wir suchen zwei wiederverwendbare Textunterschiede, die zwei voneinander
unterscheidbare sichtbare Eigenschaften oder Beziehungen ausdrücken könnten.
Dann muss eine feste gemeinsame Leseregel ihre Kombination vorhersagen.

Ein rein erfundenes Anschauungsbeispiel: Eine Textänderung könnte „innen statt
außen“, eine andere einen Wechsel des bezeichneten Gegenstands ausdrücken.
Aus getrennten Beispielen müsste die Lesung dann vorhersagen, welcher Gegenstand
in einer anderen echten Zeichnung innen liegt. Diese Wörter sind **keine
Voynich-Vorschläge**. Entscheidend ist die überprüfbare Kombination, nicht die
Wahl dieser Beispielbegriffe.

Alle Beispiele müssen im Manuskript tatsächlich vorkommen. Wir dürfen die
fehlende Kombination nicht selbst zeichnen und als Bestätigung zählen. Eine
Vierfelderstruktur wäre ein guter Entdeckungsanfang, aber vier passende Beispiele
wären noch kein Übersetzungsbeweis. Einzeln gelernte Etiketten, Schreibvarianten,
Seitenstil und räumliche Anordnung bleiben Gegenmodelle. Wenn diese dieselbe
Vorhersage liefern, hat der Test die Bedeutung nicht identifiziert.

Konkreter Einstieg sind die bereits dokumentierten Wiederholungen aus GDT794:
`okeod` an drei Stellen der f69-Anordnung sowie `okal` und `okaly` jeweils zweimal
in derselben f72-Anordnung. Sie liefern wiederkehrende vollständige Formen,
**noch keine zwei Operationen oder belegte Vierfelderstruktur**. Die erste
Prüfung fragt ausschließlich, ob dort eine neue, vom alten Positionsendpunkt
verschiedene Bildrelation und eine zweite unabhängige Textvariation überhaupt
vorliegen. Wir setzen weder `y` als Operator noch die alten Besitzerkarten als
richtige Bildzuordnung voraus. Bereits korrigierte Bildidentitäten, besonders
f72r/f72v, müssen aus den aktuellen Quellen übernommen werden.

Der vorab begrenzte neue Suchgegenstand ist eine wiederkehrende Konfiguration
des dargestellten Gegenstands bzw. seiner ausdrücklich gezeichneten Beziehung
zu einem anderen Gegenstand. Winkel, Listenposition, Nachbarabstand, Sektorzahl
und der bekannte Bekleidungsendpunkt sind ausgeschlossen. Gibt es nur solche
alten Endpunkte, endet die Prüfung bereits dort. Die konkreten neuen Merkmale
wären Entdeckungen und müssten vor einem späteren Bedeutungstest separat
festgelegt werden; ihre Auswahl darf nicht als vorhergesagte Bestätigung gelten.

Fehlt diese Konstellation, wird dieser konkrete Einstieg beendet. Es folgt kein
neuer Winkeltest, kein automatischer Ersatz durch l/m und keine corpusweite
Suche nach einer nachträglich passenden Vierfeldertafel.

## Zweite, unabhängige Möglichkeit: die Zeichnung liefert ein Naturgesetz

Auf der bereits freigegebenen f67r2-Komposition beschreibt
[GDT871](../../experiments/yolo/gdt871_remaining_shared_diagram_orientation/REPORT.md)
kleine Gesichter mit farbigen sichelartigen Teilen. Root hat das bereits unter
GDT871 freigegebene Original Yale1006194 innerhalb seines bestehenden
Panelumfangs für diese Planung erneut selbst visuell angesehen. Dies ist keine
neue unabhängige Beobachtung oder Blindbestätigung. Das bestätigt hier keine
gemessene Phasenfolge, Himmelskörperidentität oder Gerätefunktion.

Die kreative Möglichkeit ist enger: Vielleicht hängen Position, Ausmaß und
Seite einer dargestellten Teilfläche nach einer einfachen geometrischen Regel
zusammen. Eine solche Regel könnte Bedeutungen gemeinsam mit wiederkehrenden
Inschriften eingrenzen, ohne übersetzte Namen vorauszusetzen. Sie müsste eine
zusätzliche Eigenschaft vorhersagen, die nicht zum Anpassen der Regel benutzt
wurde. Ein frei gedrehter Farbklassifikator leistet das nicht.

Diese Möglichkeit erhält einen kurzen parallelen Sichtbarkeitstest, keine
Priorität als fertige Mondhypothese. Sind keine mindestens drei unterscheidbaren
begrenzten Flächenzustände oder keine wiederverwendbaren Textzuordnungen
erkennbar, endet dieser Einstieg. Keine Pigmentrekonstruktion, Unterlagenrettung
oder neue allgemeine Geräteedition anschließen. Eine erkennbare geometrische
Regel wäre zunächst ein struktureller Befund. Erst eine anschließend festgelegte
Vorhersage mit wiederkehrender, unabhängig zugeordneter Inschrift könnte eine
Bedeutung prüfen. Ein mögliches Phasenbild und ein benutzbares Instrument bleiben
unterschiedliche Behauptungen.

## Erste Runde: 30 Minuten bis zu einer Forschungsentscheidung

Die Zeit beginnt erst mit Ausführung dieser Runde, nicht mit der heutigen
Planvorbereitung. Das ist eine Obergrenze einschließlich Veröffentlichung.
Diese Runde ist ausdrücklich eine Erkundungs-/Machbarkeitsprüfung. Der aktuelle
Quellenstand enthält für beide Einstiege noch keine konkret zurückgehaltene
Beobachtung mit festgelegten unterschiedlichen Bedeutungsprognosen. Daher kann
die Runde ein solches Experiment vorbereiten, aber keine Lesung bestätigen.

1. **0–5 Minuten:** In einem kurzen Protokoll genaue Quellen, sämtliche
   ausgewählten Vorkommen, sichtbare Zielmerkmale und Ausschlussregeln festlegen.
   Bereits gesehenes Material als Erkundungsmaterial kennzeichnen. Kein neuer
   Seitenzugang ist für diese ersten Beispiele vorgesehen.
2. **5–18 Minuten:** Root prüft die konkrete kombinatorische Möglichkeit nativ
   an den Bildern. Ein unabhängiger Agent prüft die begrenzte geometrische
   Möglichkeit. Vorhandene Transkriptionen und Quellenleser wiederverwenden;
   keine neue OCR oder allgemeine Bildpipeline.
3. **18–23 Minuten:** Ein Kritiker sucht die einfachste andere Erklärung.
   Ergebnis: ein konkretes prüfbares Beispiel, ein genau benannter fehlender
   Vergleich oder das Ende des jeweiligen Einstiegs. Eine bloße wiederholte
   Form zählt nicht als positives Bedeutungsresultat.
4. **23–30 Minuten:** Ein gemeinsamer knapper Befund mit Quellen und Entscheidung
   wird geprüft, registriert und veröffentlicht. Keine zwei Verwaltungsprojekte
   für die parallelen Teilfragen.

Ein vorbereiteter Rohideenüberschuss besteht bereits. Der Ideenagent kann während
der Ausführung in einem begrenzten Auftrag weitere unabhängige Vorschläge über
`vmanus-work ideas add` behalten; seine Menge verzögert diesen Test nicht.

## Nur bei ausreichendem Beispiel: höchstens 60 weitere Minuten

Vor Implementierung die vollständige kleine Lesung und ihre Rivalen festlegen:
welche Formen welche Bedeutung tragen, welche Alternativen offenbleiben, welches
reale zusätzliche Detail oder welche Kombination vorhergesagt wird und welche
Beobachtung die Lesung widerlegt. Bildzuordnung und Lesbarkeit müssen unabhängig
von der gewünschten Bedeutung begründet sein. Keine Ausnahme pro Vorkommen.

Das Budget umfasst 10 Minuten Festlegung, höchstens 25 Minuten Auswertung mit
vorhandenen Werkzeugen, 15 Minuten unabhängige Prüfung und 10 Minuten Befund und
Veröffentlichung. Kein allgemeiner Decoder ist dafür erforderlich.

Erkundungsbefunde auf bekannten Bildern bleiben retrospektiv. Ausschluss aus
einer Anpassung macht eine schon zur Auswahl betrachtete Stelle nicht blind.
Bestätigung verlangt eine vorher festgelegte Vorhersage an getrennten realen
Vorkommen oder einer noch nicht für die Hypothese ausgewerteten Beobachtung;
die tatsächliche Exposition wird dokumentiert. Ein neuer Agent allein stellt
keine Blindheit her. Ein einzelner Treffer begründet zunächst eine vorläufige
Zuordnung, keine portable Übersetzung.

Vergleichsmodelle erhalten Seiten-/Ringstruktur, räumliche Hinweise, Häufigkeiten
und die im jeweiligen Test relevanten sichtbaren Merkmale. Die Anzahl geprüfter
Kandidaten und ausgewählter Merkmale muss in die Bewertung eingehen. Wenn eine
geordnete Inschrift-zu-Inschrift-Relation beansprucht wird, gelten zusätzlich
die bestehenden ausführbaren GDT388-Gates. Lokale Bildbeobachtungen sind davon
zu unterscheiden; siehe [Geltungsbereich](../../docs/RELATION_GATE_SCOPE_CORRECTION.md).

| Ausgang | Tatsächlich geänderte Forschungsentscheidung |
|---|---|
| Lesung sagt zusätzliche reale Kombination voraus, Rivalen nicht; später unabhängige Wiederholung gelingt | Eine begrenzte Bedeutungsregel zum Transfer auswählen. Restmehrdeutigkeit ausdrücklich behalten. |
| Formen passen, aber verschiedene Bedeutungen machen dieselben Vorhersagen | Keine Wörter übersetzen; genau die Beobachtung bestimmen, an der diese Bedeutungen auseinandergehen. |
| Ausreichender Vergleich widerspricht der festen Lesung | Diese Lesung mit Gegenbeispiel schließen; keine Reparaturkette. |
| Geeigneter Vergleich fehlt | Den konkreten Einstieg wegen fehlender Daten zurückstellen, ohne die allgemeine Hypothese als widerlegt auszugeben. |

## Vom ersten Schlüssel zum übersetzten Abschnitt

Eine erfolgreiche kleine Regel wird eingefroren und auf weitere vollständige
Formen und Konstruktionen angewendet. Zuerst prüfen wir, ob sie außerhalb ihres
Entdeckungsbildes dieselbe Beziehung erklärt. Dann wählen wir einen kurzen
zusammenhängenden Text, in dem sie wiederkehrt, und sagen eine konkrete weitere
Beziehung voraus. Unbekannte Gruppen bleiben unbekannt; grammatische Tags werden
nicht nachträglich als Wörter ausgegeben.

Mit mehreren unabhängig gestützten Bedeutungsregeln werden vollständige
kurze Lesungen gegeneinander prüfbar. Erst dann lohnt ein eng begrenzter
Sprach-/Kodierungsvergleich, der **dieselben** Bedeutungen und Schriftformen
gemeinsam erklärt und zusätzliche unbenutzte Formen vorhersagt. Bedeutungsgewinn
und phonetische Entzifferung können getrennt voranschreiten. Ein Bildschlüssel
allein garantiert keinen übertragbaren Prosa- oder Sprachschlüssel.

Fehlen in den freigegebenen Quellen die nötigen Gegensätze, wird vor jeder
Datenerweiterung der gesuchte Vergleich konkret beschrieben. Die fünf übrigen
visuellen Freigaben sind eine knappe Zugangsmöglichkeit, kein automatisch blindes
Testset. f84 und f84r bleiben versiegelt. Keine allgemeine Metadatensuche, keine
öffentlichen Entzifferungsansätze, keine fremden LLM-API-Schlüssel.

## Einordnung der heutigen Arbeit

Drei Agenten lieferten unabhängig Vorschläge bzw. Kritik. Root hat die relevanten
Primärberichte und die bereits bekannte f67r2-Originalaufnahme geprüft. Ein
Vorschlag zur Referenzerhaltung aus alten Besitzerkarten wurde nicht übernommen:
typisierte interne Beziehungen allein beseitigen die Bedeutungsmehrdeutigkeit
nicht. Ebenso wurde die bekannte Vereinbarkeit von festem Zahlenwert und
wechselndem Wertebereich nicht erneut als konkurrierende Übersetzung verkauft.

Heute entstanden dieser Plan und sein kompakter Routenverweis. Es gab keine neue
Seitenfreigabe, Rohdatenmessung, statistische Auswertung oder Bedeutungsentscheidung.
Bestätigte Lexeme und Sätze bleiben **0**. Der nächste materielle Versuch braucht
die normale Registrierung und anschließend einen kurzen Ledger-Eintrag; reine
Planung erhält keine neue GDT-Nummer und keine erfundene Befundzeile.
