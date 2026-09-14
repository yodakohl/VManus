# IDEA237 — vorhandenes Wissen zur Wortzusammensetzung ist der Ausgangspunkt

2026-09-14. Gezielte Primärprüfung auf Nutzereinwand. **Wir beginnen nicht ohne
Strukturwissen. Die Empfehlung eines freien Differentialmodells über rohe
Schriftgruppen war zu wenig an den vorhandenen Befunden ausgerichtet.**
Diese Notiz präzisiert die Auswahlentscheidung nach ASSESSMENT.md; die
Sprachkorrektur bleibt verbindlich. Kein neuer empirischer Versuch.

## Bereits vorhandene Ergebnisse

| Befund | Konkrete bereits geprüfte Konsequenz | Was damit nicht feststeht |
|---|---|---|
| Leerstellen markieren eine reale Hierarchie. | Im [Typologiebericht](../../../archive_pre_reset_2026-08-06/semantic_assumptions/results/typology_neutral_structure_report.md) lassen sich vergleichbare sichtbare Grenzen von inneren Verbindungen unterscheiden. | Eine Gruppe ist damit kein bestätigtes Wort einer europäischen Sprache; unsichere Abstände werden dadurch nicht sicher. |
| Wiederverwendbare Teile bilden neue Formen. | Im selben alten Test ließen sich rund 91 Prozent der zuvor nicht beobachteten Prüfgruppen aus bekannten formalen Kern-/Formbestandteilen rekonstruieren: ZL 91,7, IT 90,9, RF 91,7 Prozent. | Dies ist Rekonstruierbarkeit unter der damaligen Zerlegung, keine Vorhersage einer bestimmten neuen Wortbedeutung. Die drei Transkriptionen sind Lesungen desselben Manuskripts. |
| Es existiert ein übertragbares Inventar gelernter Einheiten. | [GDT605](../../../experiments/yolo/gdt605_multisymbol_unit_alphabet/REPORT.md): 98 gelernte Einheiten, davon 97 im Prüfteil, keine dort zusätzlich benötigte Einheit; außerdem ein Zusammenhang mit der annotierten Sicherheit von Abständen. | Die 98 Einheiten sind Ergebnis der festen Kollaps-/Merge-Regeln, kein entziffertes Alphabet und keine nachgewiesenen Morpheme. Die dort getesteten Ein-Buchstaben-Angriffe scheiterten; keine allgemeine Sprachwiderlegung. |
| Zusammensetzung besitzt eine Richtung. | [GDT608](../../../experiments/yolo/gdt608_compositional_stem_orientation/REPORT.md): Linke und rechte Bestandteile sagen Teile des äußeren Kontexts und der Grenzposition ihrer Kombination voraus. Das direkte Modell schlägt die Vertauschung auf allen 23 Prüfblättern. | Kein frei kombinierbarer vollständiger Code. Die exakte Kombination bleibt auf allen 23 Prüfblättern und bei 51 von 64 Kombinationstypen besser als die reine Komponentenregel. |
| Konkrete Bestandteile haben unterschiedliche Positionsprofile. | In GDT608 stehen rechte y/dy/aN-Komponenten nahe den definierten Chunk-Enden, rechtes k überwiegend nicht; linkes q nahe dem Chunk-Anfang. o ist heterogen; ol/or sowie ok/ot benötigen zusätzliche paarspezifische Information. | Chunk-Anfang ist keine Übersetzung von q als „Anfang“, Chunk-Ende keine Übersetzung von y als „Ende“. BPE-Kinder und Chunks sind modellgebundene Einheiten. |
| Äußere Form und Schreibkontext hängen zusammen. | [GDT282](../../../GDT282_OUTER_WRAPPER_CLASS_TRANSFER_REPORT.md) überträgt Information der äußeren Formklasse über Abschnitte und Hände. [GDT286](../../../GDT286_HOST_TO_WRAPPER_TRANSFER_REPORT.md) zeigt zusätzlich Positionsabhängigkeit. [GDT318](../../../GDT318_GLOBAL_WRAPPER_ENTRY_STATE_REPORT.md) findet gemeinsame s–Zeilenbeginn- und q–vorheriges-DY-Zusammenhänge. | Statistische Tendenzen sind keine deterministischen Weglassregeln. Formhüllen dürfen weder automatisch als bedeutungslos gestrichen noch als neue Laut-/Bedeutungszeichen ausgegeben werden. |
| Nicht alle erkannten Teile kombinieren frei. | [GDT326](../../../GDT326_HOST_COORDINATE_COMPOSITION_REPORT.md) scheitert bei vorher ungesehenen Kern-/Koordinatenkombinationen gegenüber seinem Registervergleich. | Der dort formal gespeicherte Gesamttupel ist kein nachgewiesenes Lexem. Das Ergebnis widerlegt nicht die engeren positiven Kompositionsbefunde. |
| Formwechsel können über Wortgruppen zusammenhängen. | [GDT915](../../../experiments/yolo/gdt915_terminal_lr_phrase_transfer/REPORT.md) überträgt eine r/l-Mitvariation bekannter Zweierfamilien. [GDT916](../../../experiments/yolo/gdt916_unseen_lr_stem_pair_transfer/REPORT.md) bestätigt sie nicht für neue Stammkombinationen. | Kein allgemeiner Kasus, keine universelle Kongruenzregel und keine neue Bedeutungszuordnung. Die feste Testfolge bleibt abgeschlossen. |

Diese Ergebnisse betreffen unterschiedliche Zerlegungen und Umfänge. Sie
dürfen nicht ohne Prüfung zu einem einzigen vermeintlich bewiesenen Parser
zusammengesetzt werden. Gemeinsam begründen sie aber ein stark eingeschränktes
Bild: **mehrstufiger Aufbau, gerichtete Teilkombination, zusätzliche Information
der Gesamtform und Abhängigkeit von Schreibpositionen.** Dieses Bild ist
deutlich konkreter als „wir brauchen zunächst eine Einheit oder irgendeine
Regel“. Das ist eine Zusammenführung vorhandener Befunde, keine neue Entdeckung.

## Konsequenz für IDEA237

1. **Kein Neustart mit beliebigen Rohzeichen-Edits.** Bereits bekannte
   Komponenten-, Gesamtform- und Kontextabhängigkeiten sind explizite
   Anforderungen an einen Kandidaten. Ein abweichendes Schriftmodell kann
   vorgeschlagen werden, muss diese Beobachtungen aber ebenfalls erklären.
   Eine neue natürliche Sprache oder ein neuer Decoder löst diese Aufgabe nicht.
2. **Die bekannte Positionssteuerung ist kein neuer Nachrichtenfund.**
   Ein Delta „q erscheint“ kann mit einem bereits untersuchten Eintrittskontext
   zusammenhängen. Eine Bedeutungsfassung muss erklären, welchen Teil der
   Oberflächenentscheidung die bekannte Struktur trägt und welche zusätzliche
   inhaltliche Entscheidung sie benötigt. Keine statistische Regel wird dabei
   zur ausnahmslosen Lösch-/Präfixregel umgedeutet.
3. **Eine Differentialkomponente bleibt optional.** Unterschiedliche Edits
   zwischen benachbarten Gruppen reichen nicht, ihr Vorrang vor einer Lesung
   im vorhandenen Strukturgerüst zu geben. Die uneingeschränkte Differentialidee
   verliert ihre Vorzugsstellung. Sie ist nicht widerlegt; sie müsste zuerst
   eine konkrete zusätzliche, gemeinsam geltende Inhaltsbeziehung liefern.
4. **Die eigentliche Lücke ist die Zuordnung zu Aussagen.** Ungeklärt ist,
   welche formalen Bestandteile Schriftgestaltung, grammatische Information
   oder Gegenstände/Beziehungen tragen und wie sie sich zu Inhalt verbinden.
   Darauf zielt die gemeinsame vollständige Hypothesenlesung. Keine weiteren
   allgemeinen Kompositionsstatistiken, keine Wiederholung alter Tests und
   keine Reaktivierung der längst überholten Decoderempfehlungen dieser Berichte.

Der unmittelbar nächste Entwurf muss daher anhand der vorhandenen Strukturen
sagen, welche Informationseinheit er annimmt, wie konkrete Gesamtformen und
ihre Kontexte zusammenspielen und welche vollständigen Aussagen daraus folgen.
Die bekannten Bauvorschriften werden als Arbeitsgrundlage genutzt, ohne daraus
bestätigte Bedeutungen zu erfinden. Ein bestätigter Wortanker ist weiterhin
keine Voraussetzung für die Hypothesenentwicklung. Ein zusätzlicher
Informationskanal ist gegenwärtig weder identifiziert noch experimentell gewählt.

## Exposition und Status

Root las die verlinkten Primärberichte gezielt; der kompakte Ideenagent las
GDT608 und GDT318 und leitete unabhängig Anforderungen ab. Keine neuen Rohtext-
oder Bildinhalte, keine neuen Statistiken, Corpus-/Decoderläufe oder Kontakte.
Die alten Zahlen sind ausschließlich beschriftete Bestandsbefunde. Keine neue
Signifikanz, globale Sprachentscheidung oder Bedeutungsbestätigung.
f84/f84r und alle übrigen Reserven bleiben geschlossen. Alte Versuche und
vorherige IDEA237-Fassungen bleiben unverändert; diese Auswahlkorrektur ist
gesondert dokumentiert.
