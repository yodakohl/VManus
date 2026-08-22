# V67 R1 — Lehrbuch der Ganzkartenkürzung

## Ergebnis und Grenze

Die zehn Seiten lassen sich als **registerabhängiges Werkstattsystem** lehren, ohne eine Lautung, ein Alphabet oder eine Sprachidentität zu behaupten. Die stärkste Unterrichtsform ist ein Mischmodell:

1. eine formularartige Reihenfolge ordnet den Quellstoff;
2. kurze imperative Werkstattprosa realisiert besonders die Biological-Handlungen;
3. ein reines Exemplar-/Codebuch trägt seltene Prosa und sämtliche Astro-Gruppen.

„Brevigraph“ bedeutet hier nur: Eine **exakte sichtbare Ganzkarte** ist die Adresse eines bereits gelehrten Eintrags. Sie ist weder Anfangsbuchstabe noch lautliche Abkürzung. Ihre sichtbaren Teile, ihr PAGE_HOST und ihre Oberfläche übertragen keine Bedeutung.

Die Ebenen bleiben im Unterricht und in der Ausgabe getrennt:

| Ebene | Inhalt | Darf wohin übertragen werden? |
|---|---|---|
| EXACT_CARD_OR_LOCAL_GROUP_ID | unveränderte Prosa-joint_tuple_id oder Astro-Seitenadresse | nur identisch kopieren |
| FORMAL_VALUE | ausgewählter Slot/Frame/Close-Zustand | strukturell, nicht als Wortübersetzung |
| ATOMIC_OR_WHOLE_CARD_MNEMONIC | elf fragezeichenmarkierte Lehrgriffe oder UNKNOWN | nur über dieselbe exakte Prosa-Karte |
| LOCAL_SELECTED_SOURCE_FRAGMENT | konkrete V64/V65/V66-Expansion | nur im Record- bzw. Seitencodebuch |
| COMPLETE_RECORD_TEXT | vollständige ausgewählte Artikel-, Prozess- oder Diagrammlesung | niemals zurück ins Wörterbuch |

Der Renderer ist eine sechste, nachgelagerte Produktionsstufe. Er setzt die schon gewählte Karte in sichtbare Form; er erzeugt keine Quelle.

## Quellenreihenfolge

**Herbal:** Bildbesitzer → Material/Teil → Bedingung/Zeit → Zubereitung/Handlung → Parameter → Ziel/Anwendung → Aufbewahrung/Fortsetzung.

**Biological:** Bildbesitzer/Station → aktiver Posten → Parameter/Link/Ziel → Zustandsprüfung → Handlung/Übergabe → Terminal/Close.

**Astro:** Seitennamespace → Diagrammbesitzer/Zentrum → lokale Adresse → lokaler Wert oder lokale Regel → gerichtetes Rendering.

Das ist eine didaktische Quellenordnung, keine Behauptung über lateinische oder deutsche Wortstellung. Die formularartige Ordnung ist für Herbal am sparsamsten; der kurze Imperativ ist für Bio am flüssigsten; das reine Codebuch hält Astro und den seltenen Prosarest am saubersten. Der direkte Punktevergleich steht in `V67_R1_SOURCE_ORDER_MODEL_COMPARISON.tsv`. Die ausgewählte Mischform erzielt 29/30 didaktische Passpunkte, aber dieser Wert ist keine historische Evidenz.

## Werkstatt und Ablage

Fünf Funktionen genügen: Lehrmeister/Redaktor, Bild- und Rissmeister, Register-/Codebuchhüter, Hauptschreiber/Renderer und Korrektor/Rückleser. Das sind Produktionsrollen, keine Behauptung von fünf Händen. In einer Dreierwerkstatt vereinigt Person 2 Bild und Register, Person 3 Schreiben und Korrektur. Die vollständige Kompetenzgrenze jeder Rolle steht in `V67_R1_FIVE_SCRIBE_ROLES.tsv`.

Der Schrank besitzt vier getrennte Lagen:

1. **Common Ledger:** die 173 Prosa-Ganzkarten mit exakter Identität und unverändertem formalen V60-Stand;
2. **kleines Lehrdeck:** nur die elf V60-Mnemonics MASS?, ANWENDEN?, BEREIT?, ANSATZ?, ZIEL?, KLAR?, VORIGES?, ANTEIL?, TEMPERIEREN?, SPÜLEN?, ABLASSEN?;
3. **Record-Exemplare:** konkrete lokale Nomen, Handlungen, OWNER/ACTIVE/TARGET/PREVIOUS-IDs und vollständige Artikel/Prozesse;
4. **Astro-Seitenbücher:** drei voneinander getrennte lokale Inventare für f67r2, f68r1 und f69v.

Ein Eintrag nennt immer Namespace, Record/Diagramm, locus, Feld/Adresse, exakte Karten- oder Gruppenidentität und Quellfragment. UNKNOWN bleibt kopierbar. Eine neue lokale Expansion wird niemals rückwirkend gemeinsamer Kartenwert.

## Neun Lektionen

Das Curriculum in `V67_R1_9_LESSON_CURRICULUM.tsv` führt von Behauptungsgrenzen über Ganzkarten, Quellenordnung, stille Register, Slotgrammatik und Renderer zur Astro-Sonderklasse und zur Abschlussrücklesung. Memoriert werden nur Namespace, elf Lehrgriffe, drei Ordnungsrahmen, vier Registeroperationen, kleine Slotklasse und Close-/Reflow-Regel. Produktiv bleiben die konkrete lokale Füllung, die Wahl eines bereits lizenzierten Eintrags und der Zeilenumbruch. Kein Lehrling muss 776 Bedeutungen als gemeinsames Wörterbuch auswendig lernen; er muss aber die lokalen Exemplare zuverlässig schlagen können.

## Encoder: Quelle zu sichtbarer Karte

1. Bestimme zuerst HERBAL, BIO oder ASTRO und öffne nur dessen Ledger.
2. Trage Bildbesitzer oder Diagrammzentrum als Kontext ein; mache daraus keinen Kartenwert.
3. Schreibe das konkrete Quellmemorandum in der registereigenen Reihenfolge.
4. Gliedere Prosa nach den ausgewählten 116 V61-Aussagen, nicht nach physischen Zeilen. Astro wird nach ausgewählter lokaler Adresse gegliedert.
5. Initialisiere OWNER, ACTIVE, TARGET und PREVIOUS mit anonymen recordlokalen V62-IDs. Am Recordende werden alle vier zurückgesetzt.
6. Weise nur lizenzierte V63-Slots zu. UNIQUE darf produktiv benutzt, AMBIGUOUS nur mit beiden Möglichkeiten vermerkt, EXEMPLAR_ONLY nicht erzwungen werden.
7. Schlage für jeden Slot oder Exemplarrest die **exakte Ganzkarte** nach. Weder sichtbare Komponenten noch ähnliche Oberfläche dürfen eine Karte erzeugen.
8. Setze Mnemonic und lokale Quellenexpansion in getrennte Spalten. Bei UNKNOWN wird die Karte unverändert kopiert und die Quelle bleibt im Record-Exemplar.
9. Übergib Identität, Feldzustand und ausgewählte Closure an den Renderer.
10. Der Korrektor vergleicht Kartenidentität, Oberfläche, Registerzustand und Exemplaradresse; erst danach gilt das Feld als freigegeben.

Für Astro entfallen Prosa-Slots und das gemeinsame Deck vollständig. f67r2 bleibt 7×12 mit weiterem Zwölfer- und Achterinventar, f68r1 bleibt Zentrum plus 28 räumliche Stationen, f69v bleibt unabhängige geordnete 28er-Regelfolge. Gewählte Startpunkte sind editorisch; f68r1 und f69v werden nie verbunden.

## Rückleser: sichtbare Karte zu Quelle

1. Lies Seite, Record/Diagramm, locus und Feld/Adresse vor jeder Oberfläche.
2. Identifiziere die Ganzkarte nur über ihre exakte Ledger-ID; zerlege sie nicht.
3. Lies formalen Slot und Mnemonic separat. Das Mnemonic ist ein Lehrgriff, keine Übersetzung.
4. Aktualisiere die vier V62-Register ausschließlich nach dem ausgewählten Übergang.
5. Schlage lokale Nomen, Patient/Apparat/Pflanze, seltene Handlung und UNKNOWN im Record-Exemplar nach.
6. Reflowe die physischen loci nach V61 zur ausgewählten Aussage. Ein Zeilenende beendet keine Aussage.
7. Behandle angehängtes Close als Feldcommit. Close liefert weder Objekt noch Handlung; freies DY bleibt davon unterschieden.
8. Füge die Aussagen in die vollständige ausgewählte Record- oder Diagrammfolge ein.
9. Wenn der Exemplar- oder Registerschlag fehlt, gib UNRESOLVED aus; rate nicht aus der Oberfläche.

## Renderer, Reflow und Schließung

Der Renderer darf die ausgewählte Ganzkarte, ihre lizenzierte Hüllenform, JOIN/SPACE, Feldschluss und physischen Zeilenfit ausführen. Er darf weder joint_tuple_id verändern noch eine Source-Rolle hinzufügen. Bei Platzmangel wird an der physischen Linie umgebrochen und derselbe statement_id weitergeführt. Beim neuen Feld bleibt eine offene Aussage aktiv, sofern V61 dies auswählt. Ein Close schließt das Feld, nicht notwendig den Satz. Erst Statement- und Recordkarte entscheiden über den Quellabschluss.

Die 46 ausgewählten Prosa-Zeilengrenzen werden in den 14 Unit-Zeilen mit ihren V61-Klassen referenziert. Damit bleiben insbesondere der Carry f82r.3→f82r.4 und die f83r-Fortsetzungen unabhängig vom sichtbaren Zeilenende.

## Vollständige Rücklesetests

`V67_R1_776_COVERAGE_LEDGER.tsv` enthält jede sichtbare Einheit: 100 Herbal-Events, 281 Bio-Events und 395 Astro-Gruppen. `V67_R1_14_UNIT_ROUNDTRIP.tsv` führt die fünf Herbal-Records, sechs Bio-Records und drei Astrodiagramme samt vollständiger ausgewählter Quelle, Zählung und Sequenzfingerabdruck.

Die Prüfung besitzt bewusst drei verschiedene Aussagen:

- **Mechanische Identität:** 776/776 Einheiten kehren mit unveränderter Karten-/Seitenadresse und gerenderter Oberfläche zurück.
- **Strukturelle Rücklesung:** 119/381 Prosaevents besitzen einen ausgewählten formalen oder mnemonic-basierten Anker; 262/381 bleiben prosaischer Exemplarrest.
- **Konkrete Quellenrücklesung:** 14/14 vollständige Units sind mit Record-/Seitencodebuch und Registern rücklesbar. 395/395 Astro-Gruppen benötigen ihr jeweiliges Seitenbuch. Eine semantische Inversion aus der Oberfläche allein wird 0-mal behauptet.

Die vollständigen Langtraces in `V67_R1_REPRESENTATIVE_LONG_TRACES.tsv` enthalten:

- H5 f56r: 27/27 Events, Quellfragment → Slot → exakte Karte → Renderer → Recordschlag;
- B3 f83r: 86/86 Events mit ausgewähltem Statement-/Registerkontext;
- A3 f69v: 140/140 lokale Gruppen, jede ausschließlich über ihre f69v-Adresse.

Zusammen sind das 253 lückenlose Trace-Zeilen. Der Rückweg prüft Identitäts- und Ablagedisziplin, nicht Entzifferungswahrheit.

## Typische Fehler und Reparatur

Die 14 konkreten Fälle in `V67_R1_APPRENTICE_ERROR_REPAIRS.tsv` decken Kartenzerlegung, Mnemonic=Übersetzung, PAGE_HOST-Transfer, Zeile=Satz, semantisches Close, zum Kartenwert erhobene Register, Wörterbuchleck, geratenes UNKNOWN, Prosaimport nach Astro, f68↔f69-Verknüpfung, normalisierte Rotation, recordübergreifenden Carry, erzwungene Totalanalyse und Identitätsverlust beim Rendern ab. Die allgemeine Meisterregel lautet: **Repariere nur die Ebene, auf der der Fehler entstand; ändere niemals still die darunterliegende Kartenidentität.**

## Stärkster Widerspruch

Das System ist lehrbar, aber codebuchschwer: 657/776 Gruppen sind kein produktiv gelesener gemeinsamer Prosaanker, sondern Prosa-Exemplarrest oder Astro-Seiteneintrag. Ein vollständiger source→cards→source-Rundlauf gelingt deshalb nur, weil das lokale Exemplar mitgeführt wird; er ist kein unabhängiger Beweis, dass die kreative medizinische Quelle historisch richtig ist. Dieselbe formale Produktion kann eine nichtmedizinische Werkstattprosa tragen. Zusätzlich bleiben Astro-Start und -Richtung unbewiesen. Diese Grenzen sind Teil des Unterrichts, nicht zu behebende Lücken durch neue Kartenglossen.

## Lehrregel

> Erst Namespace und Quelle, dann Register und Slot, dann die exakte Ganzkarte, zuletzt Renderer und Close; rückwärts in genau umgekehrter Ordnung — niemals aus Formteilen, Bild oder Zeilenende lesen.
