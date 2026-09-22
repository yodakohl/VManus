# GDT1037: eine feste Bedeutungstabelle mit drei Eintrittskontexten

## Frage vor der Ausführung

Können die zwei bestehenden ganzen Galen-Lesefamilien unverändert durch eine
kontextabhängige Tabelle verbunden werden? A enthält II/III mit95Rohgruppen
und67Werten, B IV/V mit88Gruppen und59Werten. Die vollständige frühere
[semantische Schnittprüfung](../../../research_registry/decisions/galen_1029_501_complete_lexicon_intersection_20260922.md)
hat alle13gemeinsamen Formen verglichen: jede verlangt verschiedene A-/B-
Denotationen. Zusammen sind113exakte Formen belegt. A enthält bereits die
in RAW500 offengelegte qoky-Erweiterung; GDT1028 bleibt unverändert.

GDT1034/1035 betreffen einen anderen Vertrag: freie neue kontextfreie
Einzelwertcodes unter konservativen Quellkapazitäten. Hier bleiben gerade
die alten Werte und vollständigen Positionsbindungen erhalten. Kein Wert
wird verschoben, umgedeutet, aufgeteilt oder als Füller gestrichen. Der Test
untersucht keinen Raum aller neuen semantischen Zuordnungen.

## Motivation und zusätzlicher Vertrag

GDT311/318 belegten formale Schreibwahl nach Position/vorangehender Form auf
bereits lizenzierten Varianten. Sie bestätigten keine Bedeutungsumschaltung.
Neu angenommen wird die globale Funktion:

    D(exakte Rohform, LINE_START, PREV_LITERAL_DY) = feste Denotation.

LINE_START ist wahr genau an der ersten Gruppe der physischen Quellzeile.
PREV_LITERAL_DY ist wahr genau dann, wenn die unmittelbar vorherige Rohgruppe
derselben Zeile buchstäblich mit ASCII `dy` endet. Am Zeilenanfang ist es
falsch. Drei mögliche Kontexte: START, AFTER_DY, OTHER. Kein Kapitel-, Folio-,
Abschnitts-, Autoren-, Currier- oder Familientag darf D steuern; diese Angaben
bleiben Herkunftsmetadaten. Kein Überspringen von Gruppen oder Zeilengrenzen.

Die wörtliche Endung wird ausdrücklich neu fixiert. Dies repliziert nicht
GDT318s parserabgeleitetes dy_closure und beweist nicht deren Identität.
Unsichere Rohzeichen bleiben unverändert; keine Normalisierung, Auflösung
von Entitäten oder Reparatur von Gruppen.

## Datenabgrenzung

Nur vier ganze exponierte ZL3b-Absätze aus GDT1034s SPEC: f107v.45–49(49),
f111r.44–47(46), f76v.37–41(55), f80v.19–22(33). Das eigene GDT928-Paket ist
mit SHA256 `667ca3ae0705a6bb3ccfcd09ea7ee04e28747e58d810e8fa9379f28c0f4fc89b`
gebunden. Alle vier alten vollständigen Tokenreceipts und Lexika werden
gebunden und positionsgenau abgeglichen. Metadaten/Selektoren werden vor
Wortzugriff geprüft. Kein gemischtes Roh-TSV, neues Bild, neue Transkription
oder fremder Zielabsatz. f84/f84r versiegelt; f116v nicht zugelassen.

Alle183Positionen werden ausgegeben: Original-ID, Rohform, Vorgänger,
Kontextmerkmale, Quelle/Lesefamilie, alter Wert und anchor_eligible. Alle113
Formen bleiben im Nenner; alle13Schnittformen werden mit sämtlichen drei
Kontexten tabelliert, auch leeren Zellen. Alternative Leser sind hier nicht
zusätzlich zugelassen: Die festen vier Quellentwürfe sind ZL-Projektionen.

## Feste Ansichten und Entscheidung

RAW_EXACT benutzt alle183Positionen, bedingt auf ihrer Rohlesung.
LITERAL_LINES benutzt nur Positionen vollständig anchor_eligible=True
markierter Zeilen. Ihr fehlender Konflikt bestätigt keinen ganzen Code;
ausgeschlossene Positionen bleiben vollständig im RAW-Artefakt.

Für jeden Schlüssel wird die Menge verlangter fester Werte gebildet.
Bei einer semantisch vorab geprüften Schnittform bedeutet mindestens eine
A- und B-Position im selben Kontext: REFUTED_FIXED_CONTEXT_JOIN.
Die Literalansicht bezeichnet denselben Teilkonflikt als
REFUTED_FIXED_CONTEXT_JOIN_ON_LITERAL_LINES; ohne Teilkonflikt gilt
NO_LITERAL_CONFLICT_NOT_FULL_CODE. Jede Konfliktzelle und alle belegenden
Original-IDs werden berichtet.
Unterschiedliche englische Etiketten sind nicht allein der Beweis: Die
bindende frühere semantische Tabelle begründet die13Nichtidentitäten.

Enthält RAW keine Kollision, lautet der Befund COMPATIBLE_FIXED_CONTEXT_TABLE,
mit vollständiger tatsächlich belegter Zuordnung. Das wäre eine Tabelle
für diese festen Entwürfe, keine Identifikation Galens/einer Sprache und
kein übersetztes Wort. Fehlende oder abweichende Quellenbindungen ergeben
INVALID_INPUT. Keine Signifikanz oder Wahrscheinlichkeit aus der früheren
Suche; beide Ansichten sind keine unabhängigen Studien.

## Ausführung und Stopp

PREREG_LOCK bindet Methode, Spezifikation, beide unabhängig geschriebenen
Programme und claimtragende Quellen. Der echte Lauf erfolgt erst nach
öffentlichem Lock auf main und dessen Beleg in PUBLIC_REGISTRATION.
Synthetische Prüfungen dürfen zuvor laufen und lesen keinen Zielinhalt.
Der unabhängige Validator liest/importiert das Hauptprogramm nicht und
rekonstruiert alle Positionen, Zellen und Ergebnisse separat.

Der [Entscheidungsbeleg](../../../research_registry/decisions/galen_fixed_context_join_decision_20260922.md)
begrenzt Vorbereitung bis Veröffentlichung auf14:04–14:34UTC. Nach dem
Ergebnis keine zusätzlichen Merkmale, Wortwerte, Absätze oder automatische
Decoder-Erweiterung. Die vorhandenen13kontextfreien Konflikte und früheren
Quelltexte waren bekannt; die neue gesamte Kontextzählung erfolgt nach dem
Lock. Frühere Entscheidungen bleiben unverändert;0bestätigte Wörter.
