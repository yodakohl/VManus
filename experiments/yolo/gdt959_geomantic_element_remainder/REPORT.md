# GDT959 — eine bedingte Wortfamilie, vier klare und drei unsichere Gesamtlesungen

Die neue Hypothese grenzt die32 vollständigen f66r-Rechnungen ein: Vier bleiben mit
bekannten Quellenzuordnungen über die drei Transkriptionsfassungen hinweg möglich.
Drei weitere benötigen eine Ergänzung der unklaren Quellenform *Amitia*. Das sind
**vier bzw. sieben lokale Lesungshypothesen, kein identifiziertes Wort**. Der Rest
`ary` könnte je nach Kandidat Feuer, Erde oder Luft zuordnen; mit freier Ergänzung
der unbekannten Quellenstelle entstehen weitere bedingte Varianten.

Diese Spur wurde nach GDT957 bemerkt und ausgewählt. Die zwei günstigen Feuerfälle
und mehrere Gegenbeispiele waren vor der Registrierung manuell bekannt. Der
[öffentliche Folgeversuch](PREREGISTRATION.md), Commit da1a29564, registriert vor der
automatisierten Gesamtauswertung alle376 ursprünglichen Kandidaten, alle drei
historischen Tabellen und beide Leserichtungen. Er ist ausdrücklich post-exposure.
Die Ergebnisse von GDT957, seine Schlüssel und seine Nicht-Eindeutigkeit bleiben
unverändert. Dies ist zusätzliche bedingte Einschränkung, keine rückwirkende Bestätigung.

## Tatsächlich geprüfte Konsequenz

Bei allen15 Rohwörtern je Edition wurde genau der erste EVA-Buchstabe entfernt.
Alle danach identischen vollständigen Reste mit mindestens zwei verschiedenen
Anfängen wurden gebunden. Es existiert dabei in jeder Edition nur die Familie
`ary`: ZL3b `rary/dary/fary`, IT2a und RF1b nur `rary/fary`. IT2a liest die vierte
Position `dara`, RF1b dort `@152;ary` unbekannt. Daher stammt die zusätzliche
Dreierbedingung ausschließlich aus ZL3b; die Editionen liefern keine drei
unabhängigen semantischen Belege. Sämtliche unbekannten Formen bleiben erhalten.

Für jeden unveränderten Schlüssel wurden alle15 Figurennamen vorhergesagt und mit
jeder der drei Elementtabellen verbunden. Die Hypothese verlangt eine gemeinsame
Elementklasse innerhalb jeder tatsächlich lesbaren Familie. Unterschiedliche
bekannte Elemente sind Widersprüche; unbekannte Quellenwerte werden getrennt
behandelt. Die vollständigen [1128 Kandidatenfälle](artifacts/ALL_CANDIDATES.json)
und [1128 Familienkonsequenzen](artifacts/ALL_FAMILY_CONSEQUENCES.tsv) enthalten auch
jeden ausgeschlossenen Kandidaten samt vorhergesagten Namen, Elementen und Konflikten.
Es wurde keine günstige Einzelstelle nachträglich ausgewählt.

## Quellenrivalen und verbleibende Kandidaten

Die drei verschiedenen Zuordnungen stehen nebeneinander in Turners1655-Fassung von
[*Of Geomancy*](https://www.princeton.edu/~ezb/geomancy/agrippa.html): A nach Zeichen,
B nach Planeten/Figurennatur, C als gebräuchliche Alternative. Dass der Autor B
bevorzugt, bestimmt weder das Alter der Zuordnung noch die Voynich-Lesung. Die
frühe Quellenbindung bleibt partiell. In A wird *Amitia* nicht stillschweigend in
Amissio umgeschrieben: Figur10 hat unten keinen bekannten Elementwert; oben wird
jede der vier konsistenten Ergänzungen separat zugelassen.

|Richtung|Kandidat|Tabelle|Quellenstatus|Figuren an den physischen Positionen1/4/8|
|---|---:|---|---|---|
|TOP_DOWN|18557|B|alle Familienwerte bekannt|Rubeus / Puer / Fortuna major|
|TOP_DOWN|18621|B|alle Familienwerte bekannt|Rubeus / Puer / Fortuna major|
|BOTTOM_UP|18557|C|alle Familienwerte bekannt|Carcer / Tristitia / Fortuna major|
|BOTTOM_UP|18663|A|nur mit unbekannter Quellenzuordnung|Amissio / Albus / Tristitia|
|BOTTOM_UP|27441|A|nur mit unbekannter Quellenzuordnung|Amissio / Carcer / Caput draconis|
|BOTTOM_UP|31011|C|alle Familienwerte bekannt|Acquisitio / Conjunctio / Puer|
|BOTTOM_UP|48658|A|nur mit unbekannter Quellenzuordnung|Carcer / Caput draconis / Amissio|

Die vier klaren Varianten ergeben `ary=Feuer` in den beiden B-Lesungen,
`ary=Erde` bei C/18557 unten→oben und `ary=Luft` bei C/31011 unten→oben.
Die sieben oberen Möglichkeiten bilden sieben verschiedene vollständige
Figurenlisten. Keine der15 Positionen hat über alle sieben nur einen Figurennamen;
es verbleiben je Position vier bis sieben Namen. Auch die vier klaren Fälle
identifizieren keinen einzigen gemeinsamen Figurennamen an einer Position.

Nur unter der zusätzlichen Wahl von Tabelle B und der ZL3b-Dreierfamilie bleiben
die zwei oben→unten-Lesungen18557/18621. Sie stimmen bei neun der15 Zuordnungen
überein, etwa `rary→Rubeus`, `fary→Fortuna major` und `salf→Albus`. Das sind konkrete
**bedingte Figurennamen**, keine Übersetzungen `rot`, `großes Glück` oder `weiß` im
laufenden Manuskript. Sechs Zuordnungen unterscheiden die zwei Kandidaten weiter.

## Vollständige sieben Lesungen in physischer Reihenfolge

|Position|ZL3b / IT2a / RF1b|TOP_DOWN 18557 B|TOP_DOWN 18621 B|BOTTOM_UP 18557 C|BOTTOM_UP 18663 A|BOTTOM_UP 27441 A|BOTTOM_UP 31011 C|BOTTOM_UP 48658 A|
|---|---|---|---|---|---|---|---|---|
|1|rary / rary / rary|Rubeus|Rubeus|Carcer|Amissio|Amissio|Acquisitio|Carcer|
|2|[r:s]als / rals / sals|Laetitia|Laetitia|Via|Via|Acquisitio|Amissio|Via|
|3|qo[r:n] / qor / qor|Caput draconis|Puella|Conjunctio|Acquisitio|Via|Via|Conjunctio|
|4|dary / dara / @152;ary|Puer|Puer|Tristitia|Albus|Carcer|Conjunctio|Caput draconis|
|5|ykeol / ykcol / ykeol|Acquisitio|Caput draconis|Cauda draconis|Puer|Fortuna minor|Fortuna minor|Laetitia|
|6|saly / syly / saly|Puella|Carcer|Amissio|Carcer|Albus|Tristitia|Fortuna major|
|7|salf / salf / salf|Albus|Albus|Fortuna minor|Fortuna minor|Puer|Cauda draconis|Acquisitio|
|8|fary / fary / fary|Fortuna major|Fortuna major|Fortuna major|Tristitia|Caput draconis|Puer|Amissio|
|9|qotesy / qotesy / qotesy|Fortuna minor|Fortuna minor|Albus|Fortuna major|Cauda draconis|Puella|Puer|
|10|ykaly / ykaly / ykal@221;|Amissio|Conjunctio|Puella|Puella|Laetitia|Laetitia|Rubeus|
|11|doly / daoly / doly|Cauda draconis|Cauda draconis|Acquisitio|Conjunctio|Rubeus|Rubeus|Fortuna minor|
|12|saiin / raiin / saiin|Tristitia|Tristitia|Puer|Caput draconis|Tristitia|Fortuna major|Albus|
|13|qokal / qokal / qokal|Conjunctio|Amissio|Caput draconis|Cauda draconis|Fortuna major|Albus|Tristitia|
|14|qolsa / qolsa / qolsa|Via|Via|Laetitia|Laetitia|Puella|Carcer|Cauda draconis|
|15|raral / raral / raral|Carcer|Acquisitio|Rubeus|Rubeus|Conjunctio|Caput draconis|Puella|

## Alle ursprünglichen Populationen, keine Reduktion auf günstige Editionen

Die folgende untere/obere Zahl gilt nur für die tatsächlich bekannten Familien.
Sie bestätigt keine in unbekannten Zeichen verborgene weitere Familie. Zusätzliche
ZL/RF-Kandidaten bleiben in der vollständigen Tabelle erhalten, obwohl ihre beiden
unbekannten Wörter keine vollständige lesbare Benennung erlauben.

|Edition/Richtung|Tabelle|alle Kandidaten|unten kompatibel|oben möglich|widersprochen|
|---|---|---:|---:|---:|---:|
|ZL3b_TOP_DOWN|A|76|2|6|70|
|ZL3b_TOP_DOWN|B|76|3|3|73|
|ZL3b_TOP_DOWN|C|76|1|1|75|
|ZL3b_BOTTOM_UP|A|152|3|12|140|
|ZL3b_BOTTOM_UP|B|152|2|2|150|
|ZL3b_BOTTOM_UP|C|152|6|6|146|
|IT2a_TOP_DOWN|A|16|2|3|13|
|IT2a_TOP_DOWN|B|16|2|2|14|
|IT2a_TOP_DOWN|C|16|1|1|15|
|IT2a_BOTTOM_UP|A|16|1|6|10|
|IT2a_BOTTOM_UP|B|16|2|2|14|
|IT2a_BOTTOM_UP|C|16|4|4|12|
|RF1b_TOP_DOWN|A|60|11|15|45|
|RF1b_TOP_DOWN|B|60|9|9|51|
|RF1b_TOP_DOWN|C|60|8|8|52|
|RF1b_BOTTOM_UP|A|56|5|20|36|
|RF1b_BOTTOM_UP|B|56|12|12|44|
|RF1b_BOTTOM_UP|C|56|14|14|42|

[Identische physische Vorhersagen](artifacts/IDENTICAL_PHYSICAL_READINGS.json) werden
zusammengefasst, ohne Schlüssel-, Editions- oder Tabellenherkunft zu verlieren.
[Alle32 vollständigen IT-Kandidaten gegen alle Editionen](artifacts/COMPLETE_IT2A_CROSS_EDITION.json)
und [alle verbleibenden Namensmengen](artifacts/REMAINING_NAME_MARGINALS.tsv) machen
die Unterschiede und die Unterscheidungsgrenze nachvollziehbar.

## Entscheidung, Kapazität und Prüfung

Die vier klaren Gesamtlesungen und drei quellenseitig unsicheren Rivalen werden
als explizite Hypothesen behalten. Kein Schlüssel und keine Elementklasse werden
als gelöste Lesung übernommen. Gegenüber957 ist eine zusätzliche sprachformabhängige
Bedingung sichtbar geworden; ihre Auswahl nach Kenntnis der Daten lässt keine
Signifikanzbehauptung zu. Es gibt keine geeignete Gegenkontrolle der gesamten Suche.

Die nächste sinnvolle Fortsetzung braucht eine weitere konkrete Konsequenz dieser
bestehenden Gesamtlesungen, etwa aus ihrem Zusammenhang mit dem übrigen f66r-Inhalt.
Sie darf die noch freie Tabelle oder Richtung nicht bloß nach dem gewünschten
Wortergebnis wählen. Eine weitere Sammlung von Klassenfits würde das Problem nicht lösen.

Ein bereits exponiertes physisches Blatt; **null unabhängige Bestätigungsblätter**.
Keine neue Seite, Bildfreigabe oder Reserve geöffnet; f84/f84r bleiben geschlossen.
Keine neue Relationsevidenz, daher kein behaupteter GDT388-PASS. Die unabhängige
Prüfung in [VALIDATION.json](artifacts/VALIDATION.json) betrifft Rechen- und
Datenkorrektheit, keine Bedeutung. Bestätigte Voynichwörter: **0**.
