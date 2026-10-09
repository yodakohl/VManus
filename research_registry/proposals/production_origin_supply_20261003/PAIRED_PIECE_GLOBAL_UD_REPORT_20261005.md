# Feste Zweistückgruppen: global eindeutig lesbarer Stückcode ausgeschlossen

## Frage und Entscheidung

Die noch unvollständige Rohidee paart aufeinanderfolgende Quellstücke über
ursprüngliche Wortgrenzen hinweg. Für ihre bequeme Realisierung durch einen
festen, nichtlöschenden, auf **allen endlichen Stückfolgen** eindeutig lesbaren
Code liegt bereits ein Widerspruch vor. Dafür keine Zeichentafel bauen.
Dies ist ein enger Konstruktionsausschluss, kein neues Manuskriptmuster und
kein Ausschluss jeder Paarung oder kontextabhängigen Schrift.

Die genaue Voraussetzung steht in der
[Vertragsnotiz](PAIRED_PIECE_GLOBAL_UD_CONTRACT_NOTE_20261005.json).
Quellwortende-/Fortsetzungsinformation gehört zum Stücktoken; eine reguläre
Gruppe enthält genau zwei Tokens, eine letzte Gruppe gegebenenfalls eines.
Schreiben verkettet feste Codes ohne Nullstücke, Kontextwechsel oder Ligaturen
über Codegrenzen. Globales Stück-UD ist stärker als eindeutiger Inhalt eines
vollständigen Textes. Diese zusätzliche Annahme war noch kein festgelegter
Bestandteil eines vollständigen ursprünglichen Schreibers; nur dieser
Realisierungsweg wird hier verworfen.

## Vorher festgelegte Belege

Das vorhandene manuelle Wortpaket enthält `ol` auf f23r.5 G008, in allen drei
Lesern mit bestimmtem Leerraum links und rechts, gefolgt von weiteren Gruppen.
Die ausgewählte vollständige Gruppe `olol` steht auf f14r.3 G005 am Zeilenende.
Der selector-first Abruf bestätigt das vorhandene Profil; ganze Zeile:
`ydaiin olchy kchor daiin olol`, nach Lesern getrennt.
Eine endgültige Gruppenposition von `olol` schwächt das Argument nicht:
Die letzte Gruppe darf höchstens zwei Stücke enthalten.

Vorhandene exakte Ganzformzählungen, keine eingebetteten Teilstrings:

| Form | ZL3b | IT2a | RF1b |
|---|---:|---:|---:|
| ol |455|456|469|
| olol |14|14|14|

`ol` verteilt sich über107/106/103 zugelassene Selektoren;
`olol` über jeweils13. Positions- und Wiederholungsprofile bleiben im
[gespeicherten Profil](PAIRED_PIECE_GLOBAL_UD_PROFILES_20261005.json).
Es wird weder eine Bedeutung noch eine Teilbedeutung vorgeschlagen.
Die drei Leser sind Alternativen desselben Manuskripts. Die beiden Zeilen
wurden hier nicht am Originalbild neu geprüft; das Argument bindet die
exakten Transkriptionsgruppen unter der ausdrücklich angenommenen gemeinsamen
Trägerregel. Aus `olol = ol + ol` folgt keine native Morphemgrenze.

## Kurzer Beweis und Grenzen

Wenn W zwei Stücke p und q schreibt, schreibt WW unter derselben homomorphen
Regel die vier Stücke p,q,p,q. Globale eindeutige Decodierung verbietet eine
zweite Lesung von WW aus nur einem oder zwei Tokens. Genau diesen Fall liefern
das nichtfinale W=`ol` und die vollständige Gruppe WW=`olol`.
Das gleiche Argument gilt für jede feste positive Stückzahl k, wenn reguläre
W-Gruppen k Stücke und andere Gruppen höchstens k Stücke enthalten.

Die Verkettungslogik stammt bereits aus
[GDT1207 METHOD](../../../experiments/yolo/gdt1207_letter_alias_parity_frequency/METHOD.md).
1207s ALT-Parität und dessen Quellenfehlschlag bleiben unverändert;
hier entsteht der Widerspruch durch die starre Stückzahl.
[GDT1201](../../../experiments/yolo/gdt1201_transparent_chunk_confluence/REPORT.md)
zeigt ausdrücklich, dass mehrere Chunk-Parsen denselben expandierten Inhalt
haben können. Dies wird nicht widerlegt. Ebenso bleiben Lesbarkeit nur auf
legalen Texten, Gruppen-/Kontextcodes oder variable Stückzahlen außerhalb
des vorliegenden Vertrags. Dafür liegt noch kein ausgewählter Ersatzschreiber
vor. GDT1196s Einzelstücke und1179s ganze Wortpaare behalten ihre ursprünglichen
Fehlschläge; kein Frequenztest wird hier neu ausgeführt.

## Prüfung und Konsequenz

[Belegvalidator](PAIRED_PIECE_GLOBAL_UD_VALIDATE_20261005.py) und
[Ergebnis](PAIRED_PIECE_GLOBAL_UD_RESULT_20261005.json): PASS für die drei
getrennten Bindungen, Quellhashes, exakten Strings und äußeren Grenzen.
Das ist keine unabhängige Bild-/Beweisbestätigung. Mathematische Vertragskritik
kam vom Produzenten ohne Datenprüfung; Root band die vorab gewählten Belege.
Keine Tabelle, kein neuer GDT-Versuch, keine Quellenänderung, keine neue
Wortbedeutung. Die allgemeine unvollständige Paaridee erhält keinen positiven
Überlebensstatus. Nächste Auswahl muss einen wirklich anderen vollständigen
Schreibvertrag und dessen Kosten benennen, statt diese Annahme still zu lockern.
Lokaler Arbeitscheckpoint gemäß bestehender Ausnahme; keine Veröffentlichung.
