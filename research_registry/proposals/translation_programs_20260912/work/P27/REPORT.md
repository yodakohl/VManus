# P27 — Teil, Herkunft, Inhalt und Umwandlung getrennt gelesen

2026-09-12. **Zwei explizite Zweierketten führen ein angenommenes Umwandlungsergebnis als nächsten Ausgang weiter. Keine der beiden konkreten Begriffswelten erklärt jedoch alle Konsequenzen; eine gemeinsame Lesung von HERB4 und f83r ist nicht erreicht.**

Alle vier HERB4-Absätze und alle sieben f83r-Records wurden ausgeführt: 486 Gruppen je Fassung, zehn Nomenformen und vier feste Relationswörter, 77 hypothetisch belegte Positionen, 409 offen. Die vier vollständigen Reader sind [M FRESH](READING_M_FRESH.md), [M REUSE](READING_M_REUSE.md), [B FRESH](READING_B_FRESH.md), [B REUSE](READING_B_REUSE.md). [CHAPTER.md](CHAPTER.md) enthält alle elf Abschnitte, konkrete Verfahrens- und rein pflanzliche Gegenlesung samt Sachproblemen.

## Gemeinsamer Vertrag

M benennt Pflanzengut, Kraut, Blüten, Früchte, Pflanzenrückstand, Feinanteil, Auszug, Flüssigkeit, Pressrückstand und Gefäß. B verwendet an denselben zehn Formen Pflanze, oberirdisches Kraut, Blüten, Früchte, Rinde, Blütenstaub, Pflanzensaft, Saft, Mark und Fruchtkapsel. [MODEL.json](MODEL.json) bindet jeden Wert an seine ganze Schreibform; kein Morphem wird übersetzt.

In beiden Welten: ol=ist Teil von; sho=enthält; chedy=wird zu; qokeedy=stammt aus. Linkes Thema ist der zuletzt unbeansprucht genannte Gegenstand. Rechtes Ziel ist das erste der zehn Nomen vor dem nächsten Relationswort/Recordende. Nur wird-zu macht sein Ergebnis zum neuen Thema. Unbekannte Zwischenwörter werden ausgewiesen, nicht als gelesene Syntax übersprungen. Die Regeln sind in [DECISION.md](DECISION.md) vor Ausführung festgelegt.

FRESH gibt jeder Nomenposition eine eigene Identität. REUSE setzt innerhalb eines Records gleiche ganze Formen gleich. Weder Formwiederholung noch flüssige deutsche Darstellung beweist diese Identität.

## Tatsächlich geprüfte Folgen

Je Fassung 30 Relationspositionen, davon 13 beidseitig gebunden. Sechs linke Rollen fehlen, 16 rechte; fünf Stellen haben beide Lücken, daher 17 unvollständige Relationen. Von den 13 gebundenen Relationen besitzen zehn ungelesene Zwischenwörter. Keine dieser Zahlen ist Übersetzungsgenauigkeit.

[RELATIONS.tsv](RELATIONS.tsv) enthält jede Relation in jeder Welt/Identität, alle Teilnehmerbelege, intervenierenden Formen, Typfragen und Selbstbezüge. [RECORD_COVERAGE.tsv](RECORD_COVERAGE.tsv) zeigt alle elf Records. Die Vier-Welten-Zeilen sind abhängige Alternativen, keine Wiederholungsbestätigung.

**Die zwei vollständigen Zweierketten:**

| Stellen | M | B | ungelöste Konsequenz |
|---|---|---|---|
| f83r.4:2 → .4:9 über shedy .4:7 | Gefäß → Flüssigkeit → Flüssigkeit | Fruchtkapsel → Saft → Saft | Gefäß-Stoff-Wechsel beziehungsweise unerklärte Organfolge; zweiter Unterschied unbenannt |
| f83r.22:5 → .23:9 über shedy .23:4 | Pressrückstand → Flüssigkeit → Flüssigkeit | Mark → Saft → Saft | keine gelesene Umwandlungsart oder Unterscheidung der zwei Flüssigkeits-/Saftzustände |

[PRODUCT_USES.tsv](PRODUCT_USES.tsv) zeigt fünf Produktverwendungen: zwei haben beide Relationen vollständig, drei weitere folgen in P4 einer Umwandlung mit unbekanntem Ausgangsstoff. Nur drei der fünf Nachfolger besitzen selbst ein rechtes Ziel. Diese Ebenen sind getrennt; die drei P4-Verwendungen sind keine vollständigen Produktionsketten. Die Präzisierung gegenüber der ersten technischen Zählübersicht ist in [REVISIONS.md](REVISIONS.md) dokumentiert.

## Typ und Identität verhindern scheinbare Lösungen

M verlangt drei ungeklärte Gefäß/Stoff-Beziehungen auf f83r: .2:10 Gefäß→Pressrückstand, .4:2 Gefäß→Flüssigkeit, .6:7 Gefäß stammt aus Pressrückstand. Die letzte könnte eine besondere Gefäßherstellung meinen, aber diese Geschichte steht nicht im gelesenen Text. Keine dieser Stellen wird durch 'Gefäßinhalt' ersetzt.

B hat diese spezifischen Gefäßkonflikte nicht, weil es qokaiin anders benennt. Das ist kein Sieg: Fruchtkapsel→Mark/Saft und Fruchtkapsel aus Mark bleiben unerklärt. HERB4 liefert außerdem 'Pflanzensaft enthält Kraut' und 'Blütenstaub enthält Blüten', deren natürliche Richtung problematisch ist. 'Stammt aus' wäre gerade nicht dasselbe wie das fest gewählte 'enthält'. Die einzelne brauchbare Gegenlesung 'Kraut enthält Pflanzensaft' auf f29v rettet diese anderen Stellen nicht.

REUSE erzeugt vier Selbstbezüge: zwei wird-zu (.4:9, .23:9) und zwei stammt-aus (.14:2, .27:3). [CYCLES.tsv](CYCLES.tsv) trennt Herkunfts-, Umwandlungs- und Teil/Ganzes-Graphen. Kein strikter Teil/Ganzes-Zyklus tritt auf. Umwandlung desselben Individuums kann eine Zustandsänderung meinen, identifiziert aber kein neues Produkt; Selbstherkunft bleibt ohne Zusatzgeschichte problematisch. FRESH hat keine Zyklen, was durch neue Erwähnungs-IDs stark begünstigt wird und kein Identitätsbeleg ist. Der pro Record nach Ganzformen zusammengezogene Klassenquotient entspricht hier REUSE; seine Schleifen beweisen keine individuellen Zyklen in FRESH. Mehrere Records werden nicht zu einem globalen Individuum verschmolzen.

## Fehlende Brücke und Bildgrenze

[WORD_INVENTORY.tsv](WORD_INVENTORY.tsv) zeigt: keines der zehn gewählten Nomen überspannt HERB4 und f83r. ol kommt in beiden Paketen vor, besitzt in f83r aber keine vollständige Teil-von-Bindung. Der Entwurf enthält somit keine vollständige gemeinsame lexikalische Relationsbrücke zwischen den Paketen. Das kleine gewählte Lexikon begrenzt die Aussage; andere Begriffe sind nicht widerlegt.

Alle 15 f88r-Beschriftungen /16 Gruppen wurden zusätzlich exakt angewendet: null Anschlüsse ([LABEL_TRANSFER.tsv](LABEL_TRANSFER.tsv)). Fehlende Bestätigungskapazität, keine Label-Widerlegung.

Root hat das schon zugelassene vollständige f83r-Bild selbst erneut betrachtet: Figuren in Trägerformen, Anhänge und ein unterer Verbindungsbogen; keine ausgewiesene Herstellungsfolge oder identifizierte Substanz. [VISION.md](VISION.md) trennt diese Beobachtung von Verarbeitungs- und Pflanzenallegorie. Kein Wort ist einem Bildteil zugewiesen, keine neue bildgebundene Relation.

## Entscheidung, Reproduktion und Umfang

**Keine der beiden Welten als gemeinsame Lesung auswählen.** Die Zwei-Schritt-Ergebnisfortführung ist konkret ausgearbeitet, aber ihre Begriffe, Relationen und individuellen Zustände bleiben unbestätigt. Insbesondere ist chedy=wird-zu nicht aus der Kette erschlossen. Kein stiller Wechsel zu 'liefert', 'fließt' oder 'Gefäßinhalt'. Frühere P05/P11/P12/P15-Glossen bleiben unverändert und wurden nicht als Wissen verwendet.

Primärvorgänger GDT767/768/790/809/811 sowie GDT827 geprüft; vorherige gesamte Text- und Bildexposition offen gelegt. Nur publizierte P11-, P12- und P25-Projektionen sowie bestehende f83r-Bildbytes. Keine Reserveseite oder neue Seitenauswahl, keine Kontakte; f84/f84r geschlossen. Keine Signifikanzbehauptung; unabhängige Bedeutungsbestätigung null. Kein scorefähiges Bild-Text-Paket. ZL-framierte Lesung, keine neue Dreilesartenprüfung.

Reproduktion: `python3 research_registry/proposals/translation_programs_20260912/work/P27/build.py`, dann `python3 research_registry/proposals/translation_programs_20260912/work/P27/validate.py`. Rückleseprüfung: Quellhashes, vier vollständige Sequenzen, alle120Relationszeilen, Produktbezüge mit beiden Vollständigkeitsflags und separat implementierter Graphabschluss. Das bestätigt Ausführung, keine Bedeutung.

Nächster Kandidat zur Auswahlprüfung: P04, Ersatzstoffe für dieselbe Aufgabe versus gemeinsam verwendete Zutaten. Keine automatische Reparatur der gewählten Gefäß-/Umwandlungswerte.
