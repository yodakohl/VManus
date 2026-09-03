# GDT769 — Rollen-, Identitäts- und konkreter Arbeitsreader

Dies ist die derzeit beste **ersetzbare Arbeitslesung**, keine bestätigte
Entzifferung. Strukturrolle, deutsches Arbeitswort und historischer
Vergleich bleiben getrennt. Kein EVA-Teilstring erhält einen lateinischen
Buchstaben-, Laut- oder Morphemwert.

## Fünf Zielwörter

| EVA-Ganzwort | gewählte Rolle | Arbeitsdefault | Confidence | Auswahlbasis | stärkster Rivale |
|---|---|---|---|---|---|
| `ol` | R05_SEQUENCE_FIELD_LINKER | und/mit; nach einer Menge von/aus | C1_LOCAL_FRAME__C0_ROLE_TIEBREAK | SPECIFICITY_DISPATCH_PRIORITY_AMONG_EQUAL_GATE_SCORES | Zubereitungsbasis |
| `ckhy` | OPEN | mischen | C0_RIVAL_ONLY | NO_ROLE_GATE_PASSED | Mischung oder Kompositum |
| `pcheey` | R04_BOUND_RECORD_FIELD | gebundenes Zubereitungs-/Form-II-Feld | C1_REPLICATED_REPLACEABLE | UNIQUE_TOP_ROLE_GATE | Paste, Salben- oder Mischform II |
| `ols` | R04_BOUND_RECORD_FIELD | Maß-/Produktposten | C0_RIVAL_ONLY | SPECIFICITY_DISPATCH_PRIORITY_AMONG_EQUAL_GATE_SCORES | Abschlussprodukt |
| `otar` | R05_SEQUENCE_FIELD_LINKER | weiter/dann | C1_LOCAL_FRAME__C0_ROLE_TIEBREAK | SPECIFICITY_DISPATCH_PRIORITY_AMONG_EQUAL_GATE_SCORES | bis |

`ol` und `otar` werden vorläufig als mitlaufende Feldzeichen
gelesen. `ckhy` erhält in passenden Endlagen „mischen“, obwohl die
globale Rolle gegen das Nomen „Mischung“ offen bleibt. `pcheey` ist
kein belegtes Trockenwort; `ols` ist weder automatisch flüssig noch
ein Filtrat.

## Vollständige Zeilen

### 1. `f105r.24` — BOUNDED_QUALITY_VALUE_RECORD

EVA: `pcheor ain ckheey okeeey paiin ar aiiin chpaiikey sheo pcheey dal daiin dam`

Arbeitslesung: **Trockenposten; Wert II; Kompositum in Endlage; starke Erhitzungs-Endstufe; Recordposten III; Anteil mit Wert IV; Zubereitungsposten II; Feuchtzubereitung; gebundenes Zubereitungs-/Form-II-Feld; Rohstoffposten I mit Wert III; Maß I.**

Befund: pcheey steht nach der Feuchtzubereitung und vor dem vollständig begrenzten dal-daiin-Wertfeld; das stützt ein gebundenes Zubereitungs-/Formfeld, während Paste, Salben- oder Mischform als konkrete Identität offenbleibt.

Tokenfolge: `pcheor`=Trockenposten [C1_ROLE__C0_IDENTITY] · `ain`=Wert II [C2_VALUE_ROLE__C0_AXIS] · `ckheey`=Kompositum in Endlage [C1_PREPARATION_ROLE__C0_IDENTITY] · `okeeey`=starke Erhitzungs-Endstufe [C1_STATE_CELL] · `paiin`=Recordposten III [C1_RECORD_ROLE__C0_IDENTITY] · `ar`=Anteil [C2_AMOUNT_ROLE__C0_UNIT] · `aiiin`=Wert IV [C2_BOUND_VALUE__C0_AXIS] · `chpaiikey`=Zubereitungsposten II [C0_LOCAL_RECORD_DEFAULT] · `sheo`=Feuchtzubereitung [C2_STATE_PREPARATION__C0_MEDIUM] · `pcheey`=gebundenes Zubereitungs-/Form-II-Feld [C2_RECORD_FORM_ROLE__C0_FORM_IDENTITY] · `dal`=Rohstoffposten I [C2_BOUND_HEAD__C0_AXIS] · `daiin`=Wert III [C2_BOUND_VALUE__C0_AXIS] · `dam`=Maß I [C1_AMOUNT_FIELD__C0_UNIT]

### 2. `f10v.1` — PARALLEL_BOUNDED_VALUE_RECORD

EVA: `paiin daiin sheo pcheey qoty daiin cthor otydy sain`

Arbeitslesung: **Recordposten III mit Wert III; Feuchtzubereitung; gebundenes Zubereitungs-/Form-II-Feld; Kältestufe I mit Wert III; Pflanzendrogenportion; fertiger Kaltansatz; zwei Drachmen.**

Befund: Die parallele qoty-daiin-Begrenzung nach pcheey zeigt erneut Feldgrammatik; pcheey bleibt ein gebundenes Zubereitungs-/Form-II-Feld und ausdrücklich keine belegte Trockenform.

Tokenfolge: `paiin`=Recordposten III [C1_RECORD_ROLE__C0_IDENTITY] · `daiin`=Wert III [C1_VALUE_ROLE__C0_AXIS] · `sheo`=Feuchtzubereitung [C2_STATE_PREPARATION__C0_MEDIUM] · `pcheey`=gebundenes Zubereitungs-/Form-II-Feld [C2_RECORD_FORM_ROLE__C0_FORM_IDENTITY] · `qoty`=Kältestufe I [C2_QUALITY_ROLE__C0_BINDING] · `daiin`=Wert III [C2_BOUND_VALUE__C0_AXIS] · `cthor`=Pflanzendrogenportion [C2_CONTENT_AMOUNT_ROLE__C0_IDENTITY] · `otydy`=fertiger Kaltansatz [C1_STATE_PREPARATION] · `sain`=zwei Drachmen [C1_RECURRENT_FUSED_VALUE__C0_UNIT]

### 3. `f8r.9` — PART_OR_FORM_INVENTORY

EVA: `tchoep sho pcheey pchey ofchey dsheey sholdaiin shor`

Arbeitslesung: **Krautdrogenposten; Feuchtansatz; gebundenes Zubereitungs-/Form-II-Feld; Trockenform-I-Feld; Blütenzubereitung; vollständig angefeuchtete Drogenportion; Drogenposten III; Fruchtstand.**

Befund: Die dritte pcheey-Stelle bestätigt post-moist plus H1-Formcluster ohne Mengenfeld; sie stützt ein Zubereitungs-/Formfeld, nicht Trockenheit, während sholdaiin reader-nonexact bleibt.

Tokenfolge: `tchoep`=Krautdrogenposten [C0_LOCAL_CONTENT_DEFAULT] · `sho`=Feuchtansatz [C2_STATE_PREPARATION__C0_MEDIUM] · `pcheey`=gebundenes Zubereitungs-/Form-II-Feld [C2_RECORD_FORM_ROLE__C0_FORM_IDENTITY] · `pchey`=Trockenform-I-Feld [C1_RECORD_FORM_ROLE__C0_SUBSTANCE] · `ofchey`=Blütenzubereitung [C1_PREPARATION_ROLE__C0_FLOWER] · `dsheey`=vollständig angefeuchtete Drogenportion [C2_STATE_AMOUNT_ROLE__C0_IDENTITY] · `sholdaiin`=Drogenposten III [C0_NONEXACT_LOCAL_DEFAULT] · `shor`=Fruchtstand [C2_PART_ROLE__C0_FRUIT]

### 4. `f32r.2` — MOIST_PREPARATION_RECORD

EVA: `okor okchor sheor ckhy dal dshodar qotchol`

Arbeitslesung: **Erhitzte Drogenportion; heiß-trockene Drogenportion; feuchter Drogenteil; Mischung/Kompositum; Rohstoffposten I; abgemessene Einweichfraktion I; kalt-trockene Droge.**

Befund: ckhy steht medial unmittelbar nach dem unabhängigen Feuchtteil sheor; hier gilt Mischung/Kompositum, während mischen/verrühren nur als linienfinaler Vorgangsrivale und jedes spezifische Medium offenbleibt.

Tokenfolge: `okor`=erhitzte Drogenportion [C2_QUALITY_AMOUNT_ROLE__C0_IDENTITY] · `okchor`=heiß-trockene Drogenportion [C2_QUALITY_AMOUNT_ROLE__C0_IDENTITY] · `sheor`=feuchter Drogenteil [C2_STATE_CONTENT_ROLE__C0_IDENTITY] · `ckhy`=Mischung/Kompositum [C1_MEDIAL_NOMINAL__C0_IDENTITY] · `dal`=Rohstoffposten I [C1_MATERIAL_MEASURE_ROLE__C0_AXIS] · `dshodar`=abgemessene Einweichfraktion I [C0_NOMINALIZED_WHOLE_DEFAULT] · `qotchol`=kalt-trockene Droge [C2_STATE_ROLE__C0_SUBSTANCE]

### 5. `f10v.2` — VALUE_AND_CONTENT_RECORD

EVA: `dain daiin ckhy chcthor choiin qot chodaiin cthy daiin`

Arbeitslesung: **Wert II; Wert III; Mischung/Kompositum; Portion getrockneter Krautdroge; Trockenform III; Abkühlstufe; trockene Zubereitung mit Wert III; Blattgut; Wert III.**

Befund: ckhy steht medial zwischen einer Wertfolge und einer vollständigen Inhalts-/Zustandsserie; hier gilt Mischung/Kompositum, nicht das nur für Finalpositionen vorgesehene mischen/verrühren.

Tokenfolge: `dain`=Wert II [C2_VALUE_ROLE__C0_AXIS] · `daiin`=Wert III [C2_VALUE_ROLE__C0_AXIS] · `ckhy`=Mischung/Kompositum [C1_MEDIAL_NOMINAL__C0_IDENTITY] · `chcthor`=Portion getrockneter Krautdroge [C0_EXACT_WHOLE_DEFAULT] · `choiin`=Trockenform III [C2_FORM_ROLE__C0_AXIS] · `qot`=Abkühlstufe [C0_STATE_OR_LINKER_DEFAULT] · `chodaiin`=trockene Zubereitung mit Wert III [C1_FORM_VALUE_ROLE__C0_AXIS] · `cthy`=Blattgut [C2_HERBAL_ROLE__C1_LEAF] · `daiin`=Wert III [C1_VALUE_ROLE__C0_AXIS]

### 6. `f83v.22` — DRY_TERMINAL_PRODUCT_RECORD

EVA: `char qokar cheolkain shckhey qokal cheor ols`

Arbeitslesung: **Trockener Anteil I; erhitzter Anteil I; erhitztes Trockengut Stufe II; feuchtes Kompositum Mittelstufe; heißer Stoffposten I; Trockenform; Endportion.**

Befund: ols steht linienfinal direkt nach einer unabhängigen Trockenform und wird hier als Endportion gelesen; Maß-/Produktposten bleibt Rivale, Flüssigkeit und Filtrat erhalten keinen Kredit.

Tokenfolge: `char`=trockener Anteil I [C1_FRACTION_STATE_ROLE__C0_IDENTITY] · `qokar`=erhitzter Anteil I [C2_HEAT_FRACTION_ROLE__C0_IDENTITY] · `cheolkain`=erhitztes Trockengut Stufe II [C0_NOMINAL_STATE_DEFAULT] · `shckhey`=feuchtes Kompositum, Mittelstufe [C2_STATE_PREPARATION__C0_MEDIUM] · `qokal`=heißer Stoffposten I [C1_STATE_CONTENT_ROLE__C0_IDENTITY] · `cheor`=Trockenform [C2_DRY_CONTENT_ROLE__C0_IDENTITY] · `ols`=Endportion [C1_TERMINAL_PORTION_ROLE__C0_IDENTITY]

### 7. `f104v.19` — PRODUCT_VALUE_RECORD

EVA: `pcheor chol chpcheor cholkshedy qotol sheedy qokchy qotched sho fchor ols aiin chekal`

Arbeitslesung: **Trockenposten; trocken; zweiter trockengebundener Inhaltskopf; Trocken-Endposten; kaltes Material; Feucht-Endstufe; heiß-trockene Anfangsstufe; Kaltzustand; Feuchtansatz; benannter Drogenposten; Maß-/Produktposten mit Wert III; trocken-heißes Rohstofffeld I.**

Befund: Das reader-exakte ols-aiin-Paar stützt ols hier als gebundenen Maß-/Produktposten; Endportion bleibt Rivale, Flüssigkeit, Filtrat und Öl folgen nicht aus dem Wertkontakt.

Tokenfolge: `pcheor`=Trockenposten [C1_ROLE__C0_IDENTITY] · `chol`=trocken [C2_DRY_STATE_ROLE] · `chpcheor`=trockengebundener Inhaltskopf [C0_LOCAL_CONTENT_DEFAULT] · `cholkshedy`=Trocken-Endposten [C0_LOCAL_STATE_DEFAULT] · `qotol`=kaltes Material [C2_COLD_MATERIAL_ROLE__C0_IDENTITY] · `sheedy`=Feucht-Endstufe [C0_NONEXACT_STATE_DEFAULT] · `qokchy`=heiß-trockene Anfangsstufe [C1_STATE_CELL] · `qotched`=Kaltzustand [C0_LOCAL_STATE_DEFAULT] · `sho`=Feuchtansatz [C2_STATE_PREPARATION__C0_MEDIUM] · `fchor`=benannter Drogenposten [C0_LOCAL_CONTENT_DEFAULT] · `ols`=Maß-/Produktposten [C2_BOUND_RECORD_ROLE__C0_IDENTITY] · `aiin`=Wert III [C2_BOUND_VALUE__C0_AXIS] · `chekal`=trocken-heißes Rohstofffeld I [C2_ORDERED_STATE_ROLE__C0_IDENTITY]

### 8. `f86v5.13` — AMOUNT_AND_SEQUENCE_RIVAL

EVA: `daiin shar otam ytaiin otal teody cthy or aiin otar aiiin`

Arbeitslesung: **Wert III; angefeuchtete Fraktion I; Maß Kaltansatz I; Kaltposten III; kalter Rohstoffposten I; abgekühlter Endansatz; Blattgut; Portion mit Wert III; dann/anschließend; Wert IV.**

Befund: otar folgt auf die vollständige or-aiin-Mengenformel und steht vor Wert IV; dann/anschließend verbindet die Felder am knappsten, ein nominaler Zubereitungs-/Recordposten bleibt Rivale.

Tokenfolge: `daiin`=Wert III [C1_VALUE_ROLE__C0_AXIS] · `shar`=angefeuchtete Fraktion I [C2_STATE_FRACTION_ROLE__C0_IDENTITY] · `otam`=Maß Kaltansatz I [C1_COLD_MEASURE_ROLE__C0_UNIT] · `ytaiin`=Kaltposten III [C2_COLD_RECORD_ROLE__C0_AXIS] · `otal`=kalter Rohstoffposten I [C1_COLD_CONTENT_ROLE__C0_IDENTITY] · `teody`=abgekühlter Endansatz [C1_CLOSE_STATE_ROLE__C0_OPERATION] · `cthy`=Blattgut [C2_HERBAL_ROLE__C1_LEAF] · `or`=Portion [C2_AMOUNT_HEAD__C0_UNIT] · `aiin`=Wert III [C2_BOUND_VALUE__C0_AXIS] · `otar`=dann/anschließend [C1_SEQUENCE_LEAD__C0_LEXEME] · `aiiin`=Wert IV [C1_VALUE_ROLE__C0_AXIS]

### 9. `f75r.43` — CLOSE_OR_SEQUENCE_RIVAL

EVA: `yshedy chekar oldy qokain chkar otar oldy`

Arbeitslesung: **Mazerations-Endzustand; Zwischenzubereitung; fertiger Auszug; Hitzestufe II; heiß-trockene Fraktion I; dann/anschließend; fertiger Auszug.**

Befund: otar steht zwischen einem nominalen Zustandsblock und dem wiederholten Abschlusswort oldy; dann/anschließend ist die aktuelle Kontextlesung, ein nominaler Posten bleibt offen.

Tokenfolge: `yshedy`=Mazerations-Endzustand [C1_STATE_CLOSE_ROLE__C0_PROCESS] · `chekar`=Zwischenzubereitung [C0_LOCAL_FORCED_DEFAULT] · `oldy`=fertiger Auszug [C2_CLOSE_PRODUCT_ROLE__C0_IDENTITY] · `qokain`=Hitzestufe II [C2_HEAT_VALUE_ROLE__C0_AXIS] · `chkar`=heiß-trockene Fraktion I [C2_STATE_FRACTION_ROLE__C0_IDENTITY] · `otar`=dann/anschließend [C1_SEQUENCE_LEAD__C0_LEXEME] · `oldy`=fertiger Auszug [C2_CLOSE_PRODUCT_ROLE__C0_IDENTITY]

### 10. `f115v.5` — PROCESS_OR_SEQUENCE_RIVAL

EVA: `dair cheky qoteey otar chl oleed`

Arbeitslesung: **Anteil II; getrocknete, leicht erhitzte Zubereitung; Kälte-Endstufe; dann/anschließend; Trocknen; abgeschlossene Endzubereitung.**

Befund: otar steht unmittelbar vor dem unabhängigen vollständigen Prozesswort chl; dann/anschließend ist hier die stärkste lokale Lesung, während das letzte oleed reader-nonexact bleibt.

Tokenfolge: `dair`=Anteil II [C2_FRACTION_ROLE__C0_SUBSTANCE] · `cheky`=getrocknete, leicht erhitzte Zubereitung [C0_STATE_PREPARATION_DEFAULT] · `qoteey`=Kälte-Endstufe [C2_COLD_END_ROLE] · `otar`=dann/anschließend [C2_LOCAL_SEQUENCE__C0_LEXEME] · `chl`=Trocknen [C2_PROCESS_ROLE__C0_LEXEME] · `oleed`=abgeschlossene Endzubereitung [C0_NONEXACT_PRODUCT_DEFAULT]

### 11. `f58r.13` — PREPARATION_BEFORE_PROCESS

EVA: `ytar sheear cheoldy ykeol cheal cheody chal chaiin ol oly`

Arbeitslesung: **Gekühlte Fraktion I; Zubereitungszusatz; getrockneter Endauszug; Zwischenansatz; Trockenstoff I in Mittelstufe; getrocknete Masse; Trockenstoff I in Anfangsstufe; Trockenstufe III und/mit Abseihen.**

Befund: ol übernimmt hier kontextuell die Feldrelation und/mit vor oly; Ansatz/Zubereitungsbasis bleibt der Haupt-Rivale, und weder sichtbares ol noch oly gibt eine Ölidentität.

Tokenfolge: `ytar`=gekühlte Fraktion I [C2_COLD_FRACTION_ROLE__C0_ACTION] · `sheear`=Zubereitungszusatz [C0_LOCAL_CONTENT_DEFAULT] · `cheoldy`=getrockneter Endauszug [C0_LOCAL_PRODUCT_DEFAULT] · `ykeol`=Zwischenansatz [C0_LOCAL_PREPARATION_DEFAULT] · `cheal`=Trockenstoff I, Mittelstufe [C2_DRY_CONTENT_ROLE__C0_IDENTITY] · `cheody`=getrocknete Masse [C1_DRY_PRODUCT_ROLE__C0_IDENTITY] · `chal`=Trockenstoff I, Anfangsstufe [C1_DRY_CONTENT_ROLE__C0_IDENTITY] · `chaiin`=Trockenstufe III [C1_DRY_VALUE_ROLE__C0_AXIS] · `ol`=und/mit [C1_CONTEXT_RELATION__C0_LEXEME] · `oly`=Abseihen [C2_PROCESS_ROLE__C0_LEXEME]

### 12. `f3r.19` — PART_AND_STATE_INVENTORY

EVA: `otchor ol cheor qoeor dair qoteol qosaiin chor cthy`

Arbeitslesung: **Kalt-trockene Portion und/mit Trockenform; Zubereitungsportion; Anteil II; Kaltzubereitung; Dosis III; Blütenstand; Blattgut.**

Befund: ol verbindet hier die kalt-trockene Portion kontextuell als und/mit mit der Trockenform; Ansatz/Zubereitungsbasis bleibt Haupt-Rivale, eine Flüssigkeits- oder Ölidentität fehlt.

Tokenfolge: `otchor`=kalt-trockene Portion [C1_TARGET_FREE_AXIS_RENDER] · `ol`=und/mit [C1_CONTEXT_RELATION__C0_LEXEME] · `cheor`=Trockenform [C2_CURRENT_EXACT_WHOLE] · `qoeor`=Zubereitungsportion [C0_MANUAL_SLOT_FILL] · `dair`=Anteil II [C2_FRACTION_ROLE__C0_SUBSTANCE] · `qoteol`=Kaltzubereitung [C1_NOMINALIZED_EXACT_WHOLE] · `qosaiin`=Dosis III [C0_MANUAL_SLOT_FILL] · `chor`=Blütenstand [C2_PART_ROLE__C0_FLOWER] · `cthy`=Blattgut [C2_HERBAL_ROLE__C1_LEAF]

## Entscheidungsbild

Gewählte Rollen: 4; gewählte Identitätsdefaults: 3. Offene C0-Defaults bleiben im Wörterbuch
sichtbar und werden nicht zu bestätigten Lexemen hochgestuft.

## Historischer Architekturvergleich

Das Quellenregister enthält 17 Einträge. Sie liefern nur erwartbare Rezeptarchitektur und Kandidatenklassen.
Der gezielte Relatorvergleich ergänzt 17 periodennahe Muster für Mengenrelation, finales Mischen und Schrittfolge.

## Behauptungsgrenze

Bestätigte Lexeme: **0**. Bestätigte Klartextklauseln: **0**. Produktive Komponenten oder EVA→Latein-Zuordnungen: **0**. Die Ausgabe ist konkret genug, um an weiteren zugelassenen Zeilen ersetzt oder verbessert zu werden, aber keine fertige Übersetzung.
