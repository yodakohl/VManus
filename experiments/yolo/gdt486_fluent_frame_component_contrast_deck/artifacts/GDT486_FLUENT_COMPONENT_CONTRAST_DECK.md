# GDT486 — Kontraststapel der flüssigen Komponentenrahmen

GDT486 hält Register, aktives Modell, lesbare Satzklasse, Eventgrenzen und alle umgebenden Komponenten fest. Zwei Records bilden nur dann ein Paar, wenn genau eine funktionale Komponente wechselt; gelernte Namensslots werden nie als Bedeutungswechsel gezählt.

- Streng auf derselben Seite: **33 Paare / 32 Records**.
- Mit gleicher-Register-Erweiterung: **48 Paare / 47 Records**.
- Modellgebundene Kontrastregeln: **29**; exakt gleiche Wortänderung: **28**; kontextuell erklärt: **1**; Wörterbuchdruck: **0**.
- Sichtbare Bedeutungswerte im Deck: **13**; davon sekundäre Handlungen: **3**.

## Seitenkapazität

| Seite | Register | Records | seiteninterne Paare | Registerpaar-Berührungen | kontrastgedeckte Records |
|---|---|---:|---:|---:|---:|
| f17r | HERBAL | 1 | 0 | 0 | 0 |
| f71v | CELESTIAL | 15 | 0 | 8 | 5 |
| f72r | CELESTIAL | 68 | 31 | 39 | 30 |
| f77r | BIOLOGICAL | 9 | 0 | 0 | 0 |
| f88v | PHARMA | 13 | 0 | 7 | 5 |
| f89r | PHARMA | 29 | 2 | 9 | 7 |

Vier Seiten tragen Kontrastpaare; f17r und f77r haben in diesen 135 Records keinen zweiten Record mit identischem Rahmen und genau einem funktionalen Wechsel. Das ist fehlende Kapazität, kein Gegenbeispiel.

## 29 modellgebundene Kontrastregeln

| Modell / Satzrahmen | Wechsel | Paare | davon gleiche Seite | Wortsignaturen | Status |
|---|---|---:|---:|---:|---|
| `CATALOGUE` / `CATALOGUE_ENTRY` | `ANTEIL ↔ EINHEIT` | 2 | 0 | 1 | `EXACT_RECURRENT_WORDING_RULE` |
| `CATALOGUE` / `CATALOGUE_ENTRY` | `ANTEIL ↔ HIER` | 3 | 2 | 1 | `EXACT_RECURRENT_WORDING_RULE` |
| `CATALOGUE` / `CATALOGUE_ENTRY` | `ANTEIL ↔ ZIELORT` | 2 | 1 | 1 | `EXACT_RECURRENT_WORDING_RULE` |
| `CATALOGUE` / `CATALOGUE_ENTRY` | `AUSGANG ↔ WERT` | 2 | 2 | 1 | `EXACT_RECURRENT_WORDING_RULE` |
| `CATALOGUE` / `CATALOGUE_ENTRY` | `BAHN ↔ ZIELORT` | 2 | 2 | 1 | `EXACT_RECURRENT_WORDING_RULE` |
| `CATALOGUE` / `CATALOGUE_ENTRY` | `DANACH ↔ EINHEIT` | 1 | 1 | 1 | `SINGLE_WITNESS_WORDING_RULE` |
| `CATALOGUE` / `CATALOGUE_ENTRY` | `EINHEIT ↔ HIER` | 1 | 0 | 1 | `SINGLE_WITNESS_WORDING_RULE` |
| `CATALOGUE` / `CATALOGUE_ENTRY` | `HIER ↔ ZIELORT` | 1 | 1 | 1 | `SINGLE_WITNESS_WORDING_RULE` |
| `CATALOGUE` / `CATALOGUE_ENTRY` | `POSTEN ↔ ZIELORT` | 5 | 3 | 2 | `CONTEXTUAL_GERMAN_REALIZATION` |
| `CATALOGUE` / `CATALOGUE_SEQUENCE` | `AUSGANG ↔ ZIELORT` | 1 | 0 | 1 | `SINGLE_WITNESS_WORDING_RULE` |
| `COORDINATE` / `COORDINATE_AFTER` | `ANTEIL ↔ ZIELORT` | 1 | 1 | 1 | `SINGLE_WITNESS_WORDING_RULE` |
| `COORDINATE` / `COORDINATE_AFTER` | `AUSGANG ↔ HIER` | 1 | 1 | 1 | `SINGLE_WITNESS_WORDING_RULE` |
| `COORDINATE` / `COORDINATE_AFTER` | `AUSGANG ↔ ZIELORT` | 1 | 1 | 1 | `SINGLE_WITNESS_WORDING_RULE` |
| `COORDINATE` / `COORDINATE_AFTER` | `HIER ↔ ZIELORT` | 1 | 1 | 1 | `SINGLE_WITNESS_WORDING_RULE` |
| `COORDINATE` / `COORDINATE_AFTER` | `POSTEN ↔ WERT` | 1 | 0 | 1 | `SINGLE_WITNESS_WORDING_RULE` |
| `INSTRUCTION` / `INSTRUCTION_HALTEN` | `AUSGANG ↔ ZIELORT` | 1 | 1 | 1 | `SINGLE_WITNESS_WORDING_RULE` |
| `INSTRUCTION` / `INSTRUCTION_NEHMEN` | `EINSTELLEN ↔ HIER` | 1 | 0 | 1 | `SINGLE_WITNESS_WORDING_RULE` |
| `INSTRUCTION` / `INSTRUCTION_SETZEN` | `ANTEIL ↔ WERT` | 1 | 0 | 1 | `SINGLE_WITNESS_WORDING_RULE` |
| `INSTRUCTION` / `INSTRUCTION_SETZEN` | `AUSGANG ↔ HIER` | 2 | 2 | 1 | `EXACT_RECURRENT_WORDING_RULE` |
| `INSTRUCTION` / `INSTRUCTION_SETZEN` | `AUSGANG ↔ POSTEN` | 4 | 4 | 1 | `EXACT_RECURRENT_WORDING_RULE` |
| `INSTRUCTION` / `INSTRUCTION_SETZEN` | `AUSGANG ↔ SCHLUSS` | 2 | 2 | 1 | `EXACT_RECURRENT_WORDING_RULE` |
| `INSTRUCTION` / `INSTRUCTION_SETZEN` | `AUSGANG ↔ ZIELORT` | 1 | 1 | 1 | `SINGLE_WITNESS_WORDING_RULE` |
| `INSTRUCTION` / `INSTRUCTION_SETZEN` | `FORTSETZEN ↔ ZIELORT` | 2 | 0 | 1 | `EXACT_RECURRENT_WORDING_RULE` |
| `INSTRUCTION` / `INSTRUCTION_SETZEN` | `HALTEN ↔ ZIELORT` | 1 | 0 | 1 | `SINGLE_WITNESS_WORDING_RULE` |
| `INSTRUCTION` / `INSTRUCTION_SETZEN` | `HIER ↔ POSTEN` | 2 | 2 | 1 | `EXACT_RECURRENT_WORDING_RULE` |
| `INSTRUCTION` / `INSTRUCTION_SETZEN` | `HIER ↔ SCHLUSS` | 1 | 1 | 1 | `SINGLE_WITNESS_WORDING_RULE` |
| `INSTRUCTION` / `INSTRUCTION_SETZEN` | `HIER ↔ WERT` | 1 | 0 | 1 | `SINGLE_WITNESS_WORDING_RULE` |
| `INSTRUCTION` / `INSTRUCTION_SETZEN` | `HIER ↔ ZIELORT` | 2 | 2 | 1 | `EXACT_RECURRENT_WORDING_RULE` |
| `INSTRUCTION` / `INSTRUCTION_SETZEN` | `POSTEN ↔ SCHLUSS` | 2 | 2 | 1 | `EXACT_RECURRENT_WORDING_RULE` |

Zwölf wiederkehrende Gruppen und alle sechzehn Einzelzeugen haben eine einzige Wortänderungssignatur. Nur die folgende wiederkehrende Gruppe braucht zwei Oberflächenformulierungen:

### POSTEN ↔ ZIELORT in CATALOGUE_ENTRY

Wenn beide letzten Komponenten ZIELORT sind, verdichtet die deutsche Fassung sie zu „zweifacher Zielzuordnung“. Ersetzt POSTEN eine der beiden Stellen, wird dieselbe Folge als „Zielzuordnung und Postenangabe“ ausgeschrieben. Die abweichende Wortspanne kommt daher von Zählung und Koordination, nicht von einer wechselnden Komponentenbedeutung.

Betroffene Paare: `G486-P003|G486-P004|G486-P017|G486-P032|G486-P037`. Eine Wörterbuchänderung ist **nicht** nötig.

## Alle 48 gleichen-Register-Paare

| Paar | Bereich | Rahmen | Wechsel | deutsche Änderung |
|---|---|---|---|---|
| `G475-R002 ↔ G475-R022` | SAME_REGISTER_CROSS_PAGE | `CATALOGUE_SEQUENCE` | `AUSGANG ↔ ZIELORT` | `Ausgangszuordnung=>Zielzuordnung` |
| `G475-R018 ↔ G475-R003` | SAME_REGISTER_CROSS_PAGE | `CATALOGUE_ENTRY` | `ANTEIL ↔ ZIELORT` | `Anteils-=>Zielzuordnung` |
| `G475-R003 ↔ G475-R053` | SAME_REGISTER_CROSS_PAGE | `CATALOGUE_ENTRY` | `POSTEN ↔ ZIELORT` | `∅=>zweifacher || und Postenangabe=>∅` |
| `G475-R003 ↔ G475-R079` | SAME_REGISTER_CROSS_PAGE | `CATALOGUE_ENTRY` | `POSTEN ↔ ZIELORT` | `∅=>zweifacher || und Postenangabe=>∅` |
| `G475-R004 ↔ G475-R038` | SAME_REGISTER_CROSS_PAGE | `INSTRUCTION_SETZEN` | `FORTSETZEN ↔ ZIELORT` | `Führe das Setzen des Eintrags=>Setze den Eintrag zur Zielposition , ausgehend || aus fort=>∅` |
| `G475-R004 ↔ G475-R077` | SAME_REGISTER_CROSS_PAGE | `INSTRUCTION_SETZEN` | `FORTSETZEN ↔ ZIELORT` | `Führe das Setzen des Eintrags=>Setze den Eintrag zur Zielposition , ausgehend || aus fort=>∅` |
| `G475-R034 ↔ G475-R008` | SAME_REGISTER_CROSS_PAGE | `INSTRUCTION_SETZEN` | `HIER ↔ WERT` | `Eintrag=>Positionswert || an der bezeichneten Stelle=>∅` |
| `G475-R055 ↔ G475-R014` | SAME_REGISTER_CROSS_PAGE | `COORDINATE_AFTER` | `POSTEN ↔ WERT` | `von der=>über die || Positionsposten=>Positionswert` |
| `G475-R018 ↔ G475-R059` | SAME_PAGE_OWNER | `CATALOGUE_ENTRY` | `ANTEIL ↔ ZIELORT` | `Anteils-=>Zielzuordnung` |
| `G475-R034 ↔ G475-R020` | SAME_PAGE_OWNER | `INSTRUCTION_SETZEN` | `AUSGANG ↔ ZIELORT` | `von der Ausgangsposition aus=>∅ || ∅=>zur Zielposition` |
| `G475-R038 ↔ G475-R020` | SAME_PAGE_OWNER | `INSTRUCTION_SETZEN` | `AUSGANG ↔ HIER` | `∅=>an der bezeichneten Stelle || , ausgehend von der Ausgangsposition=>∅` |
| `G475-R020 ↔ G475-R040` | SAME_PAGE_OWNER | `INSTRUCTION_SETZEN` | `HIER ↔ POSTEN` | `Eintrag an der bezeichneten Stelle=>Positionsposten` |
| `G475-R020 ↔ G475-R048` | SAME_PAGE_OWNER | `INSTRUCTION_SETZEN` | `HIER ↔ POSTEN` | `Eintrag an der bezeichneten Stelle=>Positionsposten` |
| `G475-R020 ↔ G475-R056` | SAME_PAGE_OWNER | `INSTRUCTION_SETZEN` | `HIER ↔ SCHLUSS` | `an der bezeichneten Stelle=>∅ || ∅=>und schließe den Schritt` |
| `G475-R077 ↔ G475-R020` | SAME_PAGE_OWNER | `INSTRUCTION_SETZEN` | `AUSGANG ↔ HIER` | `∅=>an der bezeichneten Stelle || , ausgehend von der Ausgangsposition=>∅` |
| `G475-R062 ↔ G475-R021` | SAME_PAGE_OWNER | `INSTRUCTION_HALTEN` | `AUSGANG ↔ ZIELORT` | `von der Ausgangsposition aus=>zur Zielposition` |
| `G475-R028 ↔ G475-R029` | SAME_PAGE_OWNER | `CATALOGUE_ENTRY` | `POSTEN ↔ ZIELORT` | `Postenangabe=>Zielzuordnung` |
| `G475-R029 ↔ G475-R081` | SAME_PAGE_OWNER | `CATALOGUE_ENTRY` | `DANACH ↔ EINHEIT` | `Folgevermerk=>Einheitsangabe` |
| `G475-R031 ↔ G475-R055` | SAME_PAGE_OWNER | `COORDINATE_AFTER` | `ANTEIL ↔ ZIELORT` | `vom Sektoranteil=>von der Zielposition` |
| `G475-R038 ↔ G475-R040` | SAME_PAGE_OWNER | `INSTRUCTION_SETZEN` | `AUSGANG ↔ POSTEN` | `Eintrag=>Positionsposten || , ausgehend von der Ausgangsposition=>∅` |
| `G475-R038 ↔ G475-R048` | SAME_PAGE_OWNER | `INSTRUCTION_SETZEN` | `AUSGANG ↔ POSTEN` | `Eintrag=>Positionsposten || , ausgehend von der Ausgangsposition=>∅` |
| `G475-R038 ↔ G475-R056` | SAME_PAGE_OWNER | `INSTRUCTION_SETZEN` | `AUSGANG ↔ SCHLUSS` | `, ausgehend von der Ausgangsposition=>und schließe den Schritt` |
| `G475-R054 ↔ G475-R039` | SAME_PAGE_OWNER | `INSTRUCTION_SETZEN` | `HIER ↔ ZIELORT` | `an der bezeichneten Stelle=>zur Zielposition` |
| `G475-R040 ↔ G475-R056` | SAME_PAGE_OWNER | `INSTRUCTION_SETZEN` | `POSTEN ↔ SCHLUSS` | `Positionsposten=>Eintrag || ∅=>und schließe den Schritt` |
| `G475-R077 ↔ G475-R040` | SAME_PAGE_OWNER | `INSTRUCTION_SETZEN` | `AUSGANG ↔ POSTEN` | `Eintrag=>Positionsposten || , ausgehend von der Ausgangsposition=>∅` |
| `G475-R054 ↔ G475-R041` | SAME_PAGE_OWNER | `INSTRUCTION_SETZEN` | `HIER ↔ ZIELORT` | `an der bezeichneten Stelle=>zur Zielposition` |
| `G475-R047 ↔ G475-R052` | SAME_PAGE_OWNER | `COORDINATE_AFTER` | `AUSGANG ↔ ZIELORT` | `Ausgangsposition=>Zielposition` |
| `G475-R047 ↔ G475-R058` | SAME_PAGE_OWNER | `COORDINATE_AFTER` | `AUSGANG ↔ HIER` | `Ausgangsposition=>bezeichneten Stelle` |
| `G475-R048 ↔ G475-R056` | SAME_PAGE_OWNER | `INSTRUCTION_SETZEN` | `POSTEN ↔ SCHLUSS` | `Positionsposten=>Eintrag || ∅=>und schließe den Schritt` |
| `G475-R077 ↔ G475-R048` | SAME_PAGE_OWNER | `INSTRUCTION_SETZEN` | `AUSGANG ↔ POSTEN` | `Eintrag=>Positionsposten || , ausgehend von der Ausgangsposition=>∅` |
| `G475-R058 ↔ G475-R052` | SAME_PAGE_OWNER | `COORDINATE_AFTER` | `HIER ↔ ZIELORT` | `bezeichneten Stelle=>Zielposition` |
| `G475-R059 ↔ G475-R053` | SAME_PAGE_OWNER | `CATALOGUE_ENTRY` | `POSTEN ↔ ZIELORT` | `∅=>zweifacher || und Postenangabe=>∅` |
| `G475-R071 ↔ G475-R053` | SAME_PAGE_OWNER | `CATALOGUE_ENTRY` | `BAHN ↔ ZIELORT` | `Bahnvermerk und=>zweifacher` |
| `G475-R077 ↔ G475-R056` | SAME_PAGE_OWNER | `INSTRUCTION_SETZEN` | `AUSGANG ↔ SCHLUSS` | `, ausgehend von der Ausgangsposition=>und schließe den Schritt` |
| `G475-R057 ↔ G475-R067` | SAME_PAGE_OWNER | `CATALOGUE_ENTRY` | `AUSGANG ↔ WERT` | `Ausgangszuordnung=>Wertangabe` |
| `G475-R057 ↔ G475-R072` | SAME_PAGE_OWNER | `CATALOGUE_ENTRY` | `AUSGANG ↔ WERT` | `Ausgangszuordnung=>Wertangabe` |
| `G475-R059 ↔ G475-R079` | SAME_PAGE_OWNER | `CATALOGUE_ENTRY` | `POSTEN ↔ ZIELORT` | `∅=>zweifacher || und Postenangabe=>∅` |
| `G475-R061 ↔ G475-R081` | SAME_PAGE_OWNER | `CATALOGUE_ENTRY` | `HIER ↔ ZIELORT` | `Hier-Vermerk=>Zielzuordnung` |
| `G475-R071 ↔ G475-R079` | SAME_PAGE_OWNER | `CATALOGUE_ENTRY` | `BAHN ↔ ZIELORT` | `Bahnvermerk und=>zweifacher` |
| `G475-R129 ↔ G475-R094` | SAME_REGISTER_CROSS_PAGE | `INSTRUCTION_SETZEN` | `HALTEN ↔ ZIELORT` | `∅=>am Zielgefäß || und halte ihn=>∅` |
| `G475-R095 ↔ G475-R113` | SAME_REGISTER_CROSS_PAGE | `INSTRUCTION_NEHMEN` | `EINSTELLEN ↔ HIER` | `und stelle beide ein=>an der bezeichneten Stelle` |
| `G475-R096 ↔ G475-R118` | SAME_REGISTER_CROSS_PAGE | `CATALOGUE_ENTRY` | `EINHEIT ↔ HIER` | `Einheitsangabe=>Hier-Vermerk` |
| `G475-R128 ↔ G475-R096` | SAME_REGISTER_CROSS_PAGE | `CATALOGUE_ENTRY` | `ANTEIL ↔ EINHEIT` | `Anteilsangabe=>Einheitsangabe` |
| `G475-R131 ↔ G475-R096` | SAME_REGISTER_CROSS_PAGE | `CATALOGUE_ENTRY` | `ANTEIL ↔ EINHEIT` | `Anteilsangabe=>Einheitsangabe` |
| `G475-R111 ↔ G475-R099` | SAME_REGISTER_CROSS_PAGE | `CATALOGUE_ENTRY` | `ANTEIL ↔ HIER` | `Anteilsangabe=>Hier-Vermerk` |
| `G475-R130 ↔ G475-R102` | SAME_REGISTER_CROSS_PAGE | `INSTRUCTION_SETZEN` | `ANTEIL ↔ WERT` | `Drogenanteil=>Mengenwert` |
| `G475-R128 ↔ G475-R118` | SAME_PAGE_OWNER | `CATALOGUE_ENTRY` | `ANTEIL ↔ HIER` | `Anteilsangabe=>Hier-Vermerk` |
| `G475-R131 ↔ G475-R118` | SAME_PAGE_OWNER | `CATALOGUE_ENTRY` | `ANTEIL ↔ HIER` | `Anteilsangabe=>Hier-Vermerk` |

## Lesart

Der Kontraststapel bestätigt nicht unabhängig, dass die deutschen Grundwerte wahr sind: Er wurde aus derselben Arbeitstheorie gebaut. Er zeigt aber, dass die GDT485-Redaktion diese Werte nicht beliebig verschluckt oder gegeneinander vertauscht. Unter identischem lesbaren Rahmen erzeugt jeder einzelne Komponentenwechsel eine sichtbare, passende Bedeutungsänderung; die einzige Signaturverdopplung ist vollständig durch deutsche Zählung erklärbar.

Der nächste Schritt sollte deshalb die 17 Einzelzeugen mit Nachbarrahmen verbinden und insbesondere die drei erstmals berührten sekundären Handlungen `EINSTELLEN`, `FORTSETZEN` und `HALTEN` zu wiederkehrenden Kontrastregeln ausbauen, ohne ihre Bedeutungen umzudeuten.
