# GDT958 — feste Formvarianten bringen keinen zusätzlichen Namensbezug

Die vollständige Prüfung ergibt **keinen neuen beobachteten Bezug**. Alle1296 Titel-/Textzellen bleiben gegenüber der wörtlichen GDT952-Grundfassung unverändert. Dieser Folgeversuch liefert deshalb keinen neuen Bedeutungsbefund und keinen Windnamen. Die eng begrenzte Erweiterung ist abgeschlossen.

Die Vorhersagen lagen im öffentlichen Commit87778f0c6 vor dem Textvergleich:155 bereits dokumentierte l/m-Wortpaare und22 bereits dokumentierte r/l-Zweiwortpaare durften ausschließlich als vollständige Einheiten verwendet werden. Kein neuer Stamm, kein Teilwort und keine Endungsregel wurde aus einem Ergebnis gewonnen. Identität, einzelne Bibliotheken und ihre vollständige kombinierte Erreichbarkeit waren festgelegt.

## Alle Fälle

In jeder Tabellenzeile wurden alle drei Modelle LM_ONLY, LR_PHRASE_ONLY und COMBINED separat ausgeführt; ihre Ergebnisse sind innerhalb derselben Edition identisch.

| Edition | Modelle | vollständig gestützte Zuordnungen | unbekanntenabhängige obere Grenze | Entscheidung |
|---|---|---:|---:|---|
|ZL3b|alle3|0|22.560|unaufgelöst|
|IT2a|alle3|0|0|widersprochen|
|RF1b|alle3|0|8.328.000|unaufgelöst|

[Die neun einzelnen Fälle](artifacts/CANDIDATE_TABLE.tsv), [alle1296 Namens-/Sektor-Kandidaten](artifacts/ALL_NAME_CANDIDATES.tsv) und [sämtliche1296 geprüften Zellen mit Fundstellen](artifacts/ALL_CELLS.json) sind vollständig erhalten. Die oberen Grenzen sind großzügige Möglichkeiten bei fehlenden Lesungen; sie stellen keine ausgefüllten Lesungen dar.

## Die konkrete neue Vorhersage

Von108 Titel-/Modellfällen erhalten nur sechs eine zusätzliche Form: der erste Titel in jeder Edition, jeweils unter LM_ONLY und COMBINED.

| Edition | ganzer ursprünglicher Titel f67r2.1 | zusätzlich zulässiger ganzer Titel |
|---|---|---|
|ZL3b|`ykshy s aram`|`ykshy s aral`|
|IT2a|`ykchyr aram`|`ykchyr aral`|
|RF1b|`ykshy s aram`|`ykshy s aral`|

Die22 bekannten r/l-Phrasen erzeugen für keinen Windtitel eine zusätzliche Form. Die anderen elf Titel jeder Edition bleiben vollständig erhalten. Insgesamt sind114 Varianten vorab dokumentiert: [vollständige Vorhersagetabelle](artifacts/FROZEN_TITLE_VARIANTS.tsv). Keine der sechs zusätzlichen Titel-/Modellvarianten liefert einen neuen Bezug in den zugeordneten Texten. Die Gesamtgraphen einschließlich unbekannter Kanten ändern sich nicht.

## Warum das die Entscheidung bestimmt

Die unveränderte historische Quelle verlangt acht gekoppelte Namensbezüge zwischen zwölf Einträgen. Jede der12! Zuordnungen muss alle acht erfüllen. Die GDT952-Widerspruchsurkunde für IT bleibt anwendbar, weil die vollständigen unteren und oberen Graphen identisch bleiben; [UNCHANGED_GRAPH_CERTIFICATE.json](artifacts/UNCHANGED_GRAPH_CERTIFICATE.json) weist diese Identität für alle18 Graphen nach. Affricus und Chorus bleiben schon durch den Quellgraphen ununterscheidbar. In ZL/RF kommen die unveränderten Rohgruppenunsicherheiten hinzu.

Die beiden Bibliotheken belegen geschriebene Formvarianten. Dass sie in diesem Kontext denselben Wind bezeichnen könnten, war die neue Hypothese. GDT800s Widerlegung obligatorischer Allographie, GDT915s gemischte Endungen und GDT916s fehlende Bestätigung neuer Phrasen bleiben bestehen. Das Ergebnis rechtfertigt weder weitere Endungsersetzungen noch die Auswahl kleinerer Titelstücke. Die breitere Möglichkeit eines anders aufgebauten Windtextes bleibt ungeprüft.

## Daten und Validierung

Alle51 bereits exponierten Loci und ihre vollständige Eigentumszuordnung stammen unverändert aus GDT952. Unbekannte Rohgruppen, Gruppenzahlen und unsichere Grenzen wurden nicht repariert. Die drei Transkriptionen sind Varianten eines einzigen physischen Blattes f67; unabhängige Bestätigungskapazität:0. Keine neue Seite oder Reserve wurde geöffnet.

Die unabhängige Prüfung rekonstruiert Bibliotheken, vollständige Variantenmengen, Rohgruppen, sämtliche Zellen und exakte Zuordnungszahlen/Marginalzahlen. Ihr Ergebnis steht in [VALIDATION.json](artifacts/VALIDATION.json). Neue beobachtete Kanten:0; daher kein neues GDT388-Relationspaket und keine Aussage über bestandene Kantengates. Keine Signifikanzbehauptung und kein bestätigtes Wort. Die Originaldateien und auch der ursprüngliche GDT952-Enumfehler bleiben unverändert archiviert.
