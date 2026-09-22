# Ganztext-Graphabgleich: begrenzte Vorgängerprüfung

2026-09-22, eigenständige Quellen-/Methodenprüfung, keine Ausführung.
Route zuerst gelesen; Live-Themen `composition` und `controls`, begrenzte
Ideensuchen, `ideas show`, `lookup` und drei gezielte `route-check`-Suchen
gingen der Entscheidung voraus. Keine neue Quelle, kein Bild, kein Corpuslauf,
kein Decoder, keine Reserve und kein Kontakt. Bestätigte Wörter: **0**.

**Entscheidung: jetzt keinen weiteren Graphmatcher auswählen.** Gemeinsame
Wiederholungs-, Häufigkeits- und Ordnungsbedingungen über vollständige Records
wurden bereits geprüft. Ein anderer Optimierer — etwa optimaler Transport —
wäre für sich kein neuer quellenbegründeter Falsifier. Die geprüften alten
Verträge schließen jedoch weder Ganztext-Inhaltsmatching allgemein noch Galen,
Musik, Pflanzenbeschreibungen oder natürliche Sprache aus.

## Die tatsächlich einschlägigen Primärvorgänger

| Primärquelle | Bereits geleisteter Schritt | Ergebnis und genaue Grenze |
|---|---|---|
| [GDT341 Methode](../../experiments/yolo/gdt341_ordered_recipe_event_graph/METHOD.md), [Bericht](../../experiments/yolo/gdt341_ordered_recipe_event_graph/COMPARATOR_REPORT.md) | Vollständige historische Rezeptrecords; anonymisierte Wiederholung, Feldreihenfolge, Fortsetzung, Verzweigung und Abschluss. Charaktere, Lexeme und semantische Rollen bleiben verborgen. | Auf 688 Records/657 Parallelpaaren gewinnt der gewählte geordnete Wiederholungsgraph nicht gegen den ungeordneten Graphen: Top-1 284 gegen 295, MRR .4682 gegen .4960. Ursprünglicher Gate nicht bestanden; keine Voynich-Übertragung. Kein Test einer globalen Quellwort→Zielwort-Zuordnung. |
| [GDT342 Methode](../../experiments/yolo/gdt342_anonymous_entity_flow_graph/METHOD.md), [Bericht](../../experiments/yolo/gdt342_anonymous_entity_flow_graph/COMPARATOR_REPORT.md) | Behält gegenüber341 die vollständige recordlokale Gleichheits-/Inzidenztopologie und Entity-Pfade, statt bloß Feldsummen zu vergleichen. Kein Zugriff auf globale Entitätsnamen im Graphscore. | Top-1 343 und MRR .5401 verbessern reine Ordnung und ungeordnete Inzidenz. Das registrierte Modell muss aber auch rohe diplomatische Wortidentität schlagen; diese erreicht 538/.8075. Gate gescheitert, Zielphase nicht ausgeführt. Das positive lokale Struktur-Signal bleibt erhalten; der Fehlschlag beweist nicht die Nutzlosigkeit aller Graphen. |
| [GDT887 Methode](../../experiments/yolo/gdt887_tacuinum_joint_entry_reconstruction/METHOD.md), [Bericht](../../experiments/yolo/gdt887_tacuinum_joint_entry_reconstruction/REPORT.md) | Drei ganze Tacuinum-Records, gemeinsame gewöhnliche Atomwerte, gemeinsame Entitätskörper, feste Feldfolge und vollständige Zielabsätze. Sämtliche Zielgruppen müssen Quellslots decken. | Beide registrierten Serialisierungen scheitern schon an wiederholten gewöhnlichen Atomen. Die gemeinsame Entitätsstufe wird nicht erreicht. Das betrifft den konkreten Lexem→Ganzgruppen-Compiler mit seinen Auslassungs-/Rubriken-/Präfixregeln, nicht jedes Darstellungsmodell desselben Inhalts. |
| [GDT888 Methode](../../experiments/yolo/gdt888_alphita_joint_name_incidence/METHOD.md), [Bericht](../../experiments/yolo/gdt888_alphita_joint_name_incidence/REPORT.md) | Ein externer asymmetrischer Sechs-Namen-Graph erzwingt eine gemeinsame Namenszuordnung, genaue Häufigkeiten einschließlich Nullen und unbekannte Recordzuordnungen. Andere Wörter bleiben ausdrücklich unmodelliert. | 18 verschiedene IT2a-Lexika, keine gemeinsame eindeutige Namenszuordnung. Der Quellgraph ist starr, seine Manuskripteinbettung deshalb noch nicht eindeutig. Keine Ganzprosa-Übersetzung. |
| [GDT913 Bericht](../../experiments/yolo/gdt913_alphita_senecio_all_candidates/REPORT.md) | Prüft die unveränderten18 Kandidaten an vorab festgelegten vollständigen Senecio-Körperkonsequenzen, statt einen günstigen Fit auszusuchen. | Alle18 widersprechen schon den positiven B/D-Anforderungen. Der ursprüngliche GDT888-Befund bleibt Nicht-Eindeutigkeit;913 ist der gesonderte Folgeentscheid. Keine allgemeine Alphita-Widerlegung. |
| [GDT901 Methode](../../experiments/yolo/gdt901_solmization_joint_relational_lexicon/METHOD.md), [Bericht](../../experiments/yolo/gdt901_solmization_joint_relational_lexicon/REPORT.md) | Der engste Vorgänger zur Absicht „viele gemeinsame Relationen schränken eine Quelle ein“:22 vollständige musikalische Records,42 Mitgliedschaften,52 gerichtete Mutationen,416 Positionen; Lexikon und ganze Absatzzuordnungen werden gemeinsam gesucht. Exakte Häufigkeiten, Köpfe, zehn globale Rollenpartitionen und gemeinsame Stamm-/Affixfaktorisierung; die vollständige Reihenfolge würde durch notwendige Zweierprojektionen geprüft. | Alle zehn Modelle sind bereits unter gemeinsamen Zähl-/Kopfbedingungen UNSAT; eine unabhängige Relaxation ohne Morphologie und Reihenfolge bestätigt das. Individuelle Wortdomänen waren zunächst alle nichtleer: **erst die gemeinsame Konsistenz schließt aus.** Vollständig ist die operative Projektion, nicht die gesamte historische Prosa. Sie enthält global unmodellierten Zielhintergrund und verlangt erste Gruppen als Köpfe. Diese Vertragsgrenzen bleiben bindend. |

Ergänzend geprüft: [GDT899](../../experiments/yolo/gdt899_astrolabium_joint_condition_program_code/REPORT.md)
blieb in beiden Solverencodings für alle sechs Kopfvarianten **UNKNOWN**;
Timeout ist keine Widerlegung. [GDT1001](../../experiments/yolo/gdt1001_cato_typed_complete_branch_code/REPORT.md)
schließt nur den vollständigen Cato-Baum unter zwei festen Schreibern aus;
das auffällige anfängliche Neunfach-SEQ ist eine Eigenschaft des gelieferten
Schreibers, kein Befund gegen Pflanzenvermehrung als Inhalt.

## Was damit nicht schon erledigt ist

Keiner der oben geprüften Berichte ist genau ein freies optimal-transport-
Matching zweier roher, mehrsprachiger Ganztext-Wortgraphen. Die begrenzte Suche
fand keinen Primärversuch dieses Namens; das ist **keine** Aussage, dass
solche Forschung im Gesamtarchiv fehlt. Die wissenschaftlich relevante Idee
einer gemeinsamen unbekannten Zuordnung über viele Beziehungen ist dagegen
in887/888/901 klar vorhanden. Ein neuer Methodenname begründet ihre Wiederholung
nicht.

[GDT838](../../experiments/yolo/gdt838_recoded_passage_capacity/REPORT.md)
fand unter seinen festen 16-Gruppen-/Wiederholungskriterien keine internen
blätterübergreifenden Bijektionskandidaten.
[GDT928](../../experiments/yolo/gdt928_multi_anchor_complete_paragraphs/REPORT.md)
fand keine ganzen Absatzpaare mit zwei disjunkten exakten Wortfolgen. Beides
sind enge Kapazitätsbefunde, keine Ablehnung paraphrastischer Inhaltsbeziehungen.
GDT928s komplette bereits exponierte Absätze sind eine vorhandene Arbeitsquelle,
kein neu unabhängiger Bestätigungsbestand.

Auch [GDT381](../../experiments/yolo/gdt381_relational_topology_transfer/REPORT.md)
ist zu unterscheiden: Seine lesbare Topologie überträgt teilweise; der starke
Voynich-Score bleibt wegen Überschneidung von Zieldefinition und Prädiktor
nicht promovierbar. Ein aus denselben Wiederholungen definiertes Ziel und
anschließend daran bewertetes Matching würde diesen Fehler wiederholen.

## Warum hier kein einzelner neuer Test nominiert wird

Für die vorhandenen Galen-Quellen könnte man sofort Wortfrequenzen,
Wiederholungen und Nachbarschaften berechnen. Es fehlt aber noch der vorher
begründete Vertrag, **welche dieser Beziehungen eine angenommene historische
Darstellung im Voynich unverändert erhalten muss**. Drei naheliegende Antworten
führen nicht automatisch zu einem neuen geeigneten Test:

- Exakte globale Ganzwortgleichheit und feste Reihenfolge definieren einen
  engen Schreibervertrag derselben Art wie887/901. Ein anderes Quellkapitel
  allein begründet nicht, warum gerade dieser Vertrag die aktuelle
  paraphrastische Galen-Lesung entscheidet.
- Freie Umordnung, Synonyme, Projektionsatome oder unmodellierter Hintergrund
  können zulässige Hypothesen sein. Sie müssen jedoch vor dem Matching
  begrenzt werden. Nachträglich gewählte Freiheit würde gerade wieder jene
  selbst eingesetzten Bedeutungen und Bezugsregeln tragen, die der neue
  Ansatz vermeiden soll.
- Ein weicher gemeinsamer Graphscore löst die fehlende Invarianz nicht:
  Gewichtung, Massenteilung und erlaubte Fehlkanten bestimmen dann, was ein
  guter Match bedeutet. „Bestes Ergebnis unter den vorhandenen Quellen“
  ist ohne einen definierten diskriminierenden Ausgang noch keine
  Einschränkung der Quellenidentität.

Die vorhandenen positiven Befunde werden dadurch nicht gelöscht: Anonyme
Struktur trägt in342 reales Parallelitätssignal, und901 zeigt konkret, dass
gemeinsame Relationen mehr ausschließen als isolierte Wortdomänen. Ein
künftiger quellengebundener Ganztextvertrag kann daran anknüpfen. **Heute wird
kein weiterer Matcher implementiert und kein alter Vertrag abgeschwächt.**

Die Root-Entscheidung, stattdessen das separat vorbereitete Verkürzungsgesetz
an sechs festen geratenen Synonymmengen mit Layoutkontrolle zu prüfen, wurde
zum Abschluss mitgeteilt. Dieses andere Design wurde hier nicht geprüft oder
ausgewählt. Die Notiz ändert weder Registry noch Route noch Ledger und enthält
keinen neuen empirischen Manuskriptbefund.
