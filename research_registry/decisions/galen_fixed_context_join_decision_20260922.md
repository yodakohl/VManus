# Fester kleiner Kontext als mögliche Verbindung zweier ganzer Galen-Lesungen

Vor neuer Kontextzählung,2026-09-22 14:04UTC. Budget bis14:34UTC einschließlich
Vorbereitung, Implementierung, unabhängiger Prüfung und Veröffentlichung.
Keine weitere Kontextverfeinerung nach dem Ergebnis.

Die vollständige Primärprüfung der67/59Lexika hat13gleiche Formen mit
verschiedenen festen Denotationen nachgewiesen. GDT1034/1035 schließen eine
kontextfreie Neubelegung der vier ganzen Inventare unter ihrem Vertrag aus.
GDT311/318 belegen dagegen **formale Schreibwahl** nach Position/vorausgehender
Form; ausdrücklich keine Bedeutungsumschaltung. Neu zu prüfen ist deshalb
die zusätzliche, unbestätigte Annahme, dass ein kleiner vorher sichtbarer
Kontext eine feste Bedeutungstabelle wählen könnte. Die alten Ergebnisse
und alle alten Wortwerte bleiben unverändert.

Kleinste ausreichende Frage: Sind die vorhandenen A-/B-Werte jedes geteilten
Worts unter demselben festen Kontext überhaupt trennbar? Kein neuer Decoder,
kein Text-/Quellentausch, keine freie Bedeutungsneubelegung und keine neue
Morphologie. Nur die vier vorhandenen vollständigen ZL-Absätze (183Gruppen)
aus GDT1034 werden benutzt, einschließlich aller Unsicherheiten.

Kontext ist exakt `(LINE_START, PREV_LITERAL_DY)`. LINE_START bedeutet erste
Rohgruppe der physischen Zeile; PREV_LITERAL_DY bedeutet unmittelbar vorherige
Rohgruppe derselben Zeile endet buchstäblich mitASCII`dy`. Am Zeilenanfang
ist PREV_LITERAL_DY falsch. Kein vorheriges Absatz-, Kapitel-, Folio- oder
Themenetikett darf den Schalter steuern. Das ist ein ausdrücklich neuer
wörtlicher Endungstest, **nicht** die Behauptung, GDT318s parserabgeleitetes
`dy_closure` sei hier identisch repliziert. Keine Entitätsnormalisierung.

Eine globale Funktion `(raw_word, context)->fixed_denotation` existiert für
diese ganzen Belegungen nur, wenn kein Schlüssel sowohl einen A- als auch
einen davon verschieden festgelegten B-Wert fordert. Die13Konfliktpaare
werden aus der vorhandenen semantisch geprüften Gesamttabelle übernommen;
unterschiedliche englische Etiketten allein gelten nicht als neuer Beweis.
Alle183Positionen, alle113Formen, alle13Schnittformen und sämtliche
Kontextkollisionen müssen ausgegeben werden.

Zwei feste Ansichten: RAW_EXACT allePositionen; LITERAL_LINES nur vollständig
anchor_eligible=TrueZeilen als konservative Teilbeobachtung, jedoch alle
Positionen weiterhin im Artefakt. Ein fehlender Teilkonflikt bestätigt keinen
ganzen Code. Ein bestehender Konflikt widerlegt nur diesen Schalter mit den
unveränderten vollständigen Lesungen. Ein kollisionsfreies Ganzinventar würde
eine konkret gemeinsame kontextuelle Belegung ermöglichen, aber noch keine
Galen-Identität oder Wortbedeutung bestätigen. Untersucht wird kein Raum aller
neuen semantischen Zuordnungen und keine allgemeine kontextabhängige Schrift.

Die gegensätzlichen Resultate ändern eine echte Entscheidung: bei Kollision
diesen durch vorhandene Struktur motivierten konkreten Verbindungsvorschlag
schließen; bei voller Kollisionsfreiheit eine gemeinsam ausführbare feste
Werttabelle bewahren und erst danach eine ganze Bedeutungsprüfung erwägen.
Keine automatische zusätzliche Steuergröße, versteckte Familienauswahl oder
größere Polysemie. Vollständig exponierte Daten, keine Signifikanz/Reserve.
