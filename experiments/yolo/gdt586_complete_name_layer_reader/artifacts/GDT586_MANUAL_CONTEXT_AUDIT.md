# GDT586 — manueller Kontextaudit

## Architekturkorrektur

Die 109 Werte lassen sich nicht wörtlich in 793 Lauftextaussagen einsetzen. 107 Namensspannen gehören zu 89 lokalen Karten und besitzen keine exakte Satzkante; zwei `LOCAL_X`-Werte gehören zu G515-S046 und G515-S050. Der Gesamtleser führt deshalb 793 Aussagen und 744 lokale Karten getrennt.

## Wiederhergestellter Rivalenkanal

Bei 60 Sternslots stand im GDT585-Assignment als alter Alias `NONE`. GDT586 holt den tatsächlichen alten Primärwert occurrence-genau aus dem GDT582-15.889-Slot-Ledger zurück. Dadurch bleiben Werte wie `Sternringstelle 35` und `Sternringstelle 39` wieder sichtbar.

## Die 19 Gruppen nach vollständigem exaktem Kontext

| Gruppe | Kontexteffekt | Disposition | beste aktuelle Lesung |
|---|---|---|---|
| GDT585-C001 | ORDER_CORRECTION | SOURCE_ORDER_REPAIRED__VISUAL_PAIR_RETAINED | In Quellreihenfolge steht zuerst die rechte Blütenform mit Folgevermerk und danach die linke Blütenform. In der getrennten Bildspur bleibt die natürliche Links-rechts-Lesung linke plus rechte Blütenform derselben Pflanze die beste Arbeitshypothese. |
| GDT585-C002 | SUPPORTS | KEEP_ONE_FIGURE_TWO_VALUES | Die eine Anweisung hält O und ODADY gemeinsam. Am besten liest sich das als ein Figuren- oder Ringeintrag mit Primärwert und mitgeführtem Zweitwert, nicht als zwei zufällig nebeneinanderstehende Einzelwörter. |
| GDT585-C003 | SUPPORTS | KEEP_ORDERED_VALUE_PAIR_TO_TARGET | YT und DY bilden unter derselben Halteanweisung ein geordnetes Wertepaar, das gemeinsam zur Zielposition gehört. Welche realen Kalenderwerte dahinterstehen, bleibt offen. |
| GDT585-C004 | SUPPORTS | KEEP_TWO_FIELD_RING_ENTRY | L und DY werden gemeinsam entlang der Ringbahn gesetzt. Die brauchbarste Lesung ist ein zweifeldriger Ring- oder Figureneintrag, nicht ein zerlegtes natürlichsprachliches Wort. |
| GDT585-C005 | NEUTRAL | KEEP_CATALOGUE_PAIR_WITH_ORIGIN | EE und Y bleiben zwei katalogisierte Werte derselben Stelle; OT und AR kennzeichnen Folge und Ausgangszuordnung. Der Kontext erzwingt weder ein Compound noch zwei unabhängige Objekte. |
| GDT585-C006 | SUPPORTS | KEEP_CARRIED_PAIR_FROM_SOURCE | OS und EEEO werden gemeinsam von einer Ausgangsposition gehalten. Das passt weiterhin am besten zu Primärwert plus mitgeführtem Wert innerhalb eines Ringeintrags. |
| GDT585-C007 | STRONGLY_SUPPORTS | KEEP_CONTINUED_RECORD_PAIR | Der volle Record führt erst A, dann einen Positionswert und AY und endet mit der Anweisung, F und EOR weiter zur Zielposition zu halten. F/EOR ist daher am ehesten das zweifeldrige Schlussglied eines fortgesetzten Ringrecords. |
| GDT585-C008 | NEUTRAL | KEEP_CATALOGUE_PAIR_WITH_ORIGIN | YF und Y bleiben ein geordnetes Katalogpaar mit Ausgangszuordnung. Eine inhaltliche Kalender- oder Sternidentität lässt sich aus dem Singleton nicht ergänzen. |
| GDT585-C009 | STRONGLY_SUPPORTS | KEEP_SAME_VALUE_TWO_ROLES | Der identische Kurzwert O erscheint zweimal in technisch getrennten Rollen derselben Aufnahme- und Einstellanweisung. Das ist der klarste Gruppenfall für einen wiederholten Wert statt zweier verschieden benannter Sterne. |
| GDT585-C010 | STRONGLY_SUPPORTS | KEEP_LEFT_TERMINAL_CHAIN | Endfigur D und linker Speiseanschluss CHD bilden den ersten Katalogkopf; unmittelbar danach folgt KCHS als linker Anschlusskopf. Der volle Record stärkt damit eine linke Endstellen- und Anschlussfolge. |
| GDT585-C011 | SUPPORTS | KEEP_RIGHT_TERMINAL_PACKAGE | D plus EDY liest sich weiterhin am besten als Endfigur mit rechtem Entnahme- oder Endanschluss. Der Folgevermerk gehört zur Karte, nicht zu einem neuen Lauftextsatz. |
| GDT585-C012 | SUPPORTS | KEEP_ROOT_AND_BASE_PAIR | D und AM bilden ein geordnetes Drogenpaar zwischen Ausgangs- und Zielzuordnung. Wurzeldroge in oder mit einer Salben- oder Fettgrundlage ist die konkreteste aktuelle Lesung, aber noch kein bestätigtes Mischrezept. |
| GDT585-C013 | STRONGLY_SUPPORTS | KEEP_REPEATED_PLANT_REFERENCE | Y erscheint zweimal in derselben Namensklasse und derselben Karte. Das spricht eher für denselben Kraut- oder Pflanzenreferenten in zwei technischen Rollen als für zwei verschiedene Stoffe. |
| GDT585-C014 | TENTATIVE | KEEP_ROOT_TO_PLANT_REFERENCE_AS_LEAD | D plus DA kann als Wurzelteil einer benannten langblättrigen Mutterpflanze gelesen werden. Die doppelte Ausgangszuordnung erlaubt aber weiterhin zwei katalogisierte Einträge; die possessive Lesung bleibt eine Hypothese. |
| GDT585-C015 | SUPPORTS | KEEP_LEAF_ROOT_PACKAGE | S und D ergeben am plausibelsten ein Blatt- plus Wurzelpaket. Dass beide Teile sicher von derselben Pflanze stammen, geht über den sichtbaren Singleton hinaus und bleibt ersetzbar. |
| GDT585-C016 | SUPPORTS | KEEP_INFLORESCENCE_HERB_REFERENCE | SY plus Y liest sich gut als Blüten- oder Fruchtstand einer Krautform. Die technische Hülle behandelt beide weiterhin als katalogisierte Namen, nicht als automatisch segmentiertes Wort. |
| GDT585-C017 | GRAMMAR_DOMINATES | KEEP_THREE_OBJECT_INSTRUCTION | Die Grammatik ist hier entscheidend: S, OIIN und E stehen als drei benannte Objekte unter einer Halte- und Fortsetzungsanweisung zum Zielgefäß. Eine gemeinsame Pflanzenfragment-Deutung darf danebenstehen, ersetzt aber nicht diese Dreiobjekt-Anweisung. |
| GDT585-C018 | TENTATIVE | KEEP_LEAF_TO_PLANT_REFERENCE_AS_LEAD | YT plus EM passt als Blattteil mit benannter grauwurzliger Mutterpflanze. Ebenso möglich bleiben zwei katalogisierte Drogen; der Singleton macht die Organ-von-Art-Beziehung nicht zwingend. |
| GDT585-C019 | WEAKENS | VISUAL_PAIR_ONLY__TEXTUAL_COMPOUND_REJECTED | DCHOS und YOR bleiben als Bildhypothese rote Fingerwurzel neben Trockenvorrat brauchbar. Textlich sind es jedoch zwei verschiedene Singleton-Records und Owner; dazwischen steht OKAIN als eigener Record. GDT586 verbindet sie deshalb niemals zu einem Satz oder Rezept. |

## Zwei konkrete Reparaturen

- C001: Quellreihenfolge ist rechte Blütenform mit OT-Vermerk, dann linke Blütenform. Die umgekehrte Links-rechts-Folge bleibt ausschließlich Bildspur.
- C019: DCHOS und YOR liegen in getrennten Records und Ownern; dazwischen steht OKAIN als eigener Record. Die Verbindung bleibt `VISUAL_PAIR_ONLY`.

C007 und C010 sind die einzigen Gruppen, deren exakter Recordkontext über die bisherige Gruppe hinausgeht. Alle anderen Fälle enden am Singleton- oder Zweikartenrecord; zusätzlicher Lauftextkontext wurde nicht erfunden.
