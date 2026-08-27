# GDT516 — Methode

## Frage

Lassen sich die 159 auf den vier neuen Seiten erstmals laufend beobachteten
Oberflächen auf endliche alte Rezeptträger und gemeinsame portable Gerüste
zurückführen? Und können die zehn Kontakte mit alten Lokalkarten sowie die
sechs in GDT515 offenen Zerlegungen ohne einen neuen portablen Wert konsolidiert
werden?

## Eingaben

Der Pass öffnet keine Manuskriptseite. Er verwendet ausschließlich:

- GDT515s Audit der 159 wirklich neuen Oberflächen, die vollständigen 597
  ausgewählten Karten und die laufende beziehungsweise vereinigte
  30-Seiten-Ausgabe;
- GDT407s eingefrorene 26-Seiten-Rezepte und Lokalkarten als ältere Träger;
- GDT413s 46-Komponenten-Tafel mit 19 portablen Arbeitswerten;
- GDT421/GDT427 für bereits beobachtete und zuvor nur erlaubte Aktionsfolgen;
- GDT473 für die bereits ausgearbeiteten Namensschalen von `doly` und `okyd`.

## Rezept- und Familienkompression

Ein „alter Rezeptträger“ ist hier eine vollständige, auf den alten 26 Seiten
bereits beobachtete Mehrkomponenten-Rezeptfolge. Für jedes neue Rezept werden
vier Mengen berechnet:

1. exakte alte vollständige Rezeptträger;
2. der längste zusammenhängende Abschnitt, der selbst ein vollständiges altes
   Rezept ist;
3. die maximale disjunkte Abdeckung durch solche alten Mehrkomponentenrezepte;
4. das portable 19-Kern-Gerüst und das nur aus Aktionsköpfen bestehende Gerüst.

Damit wird nicht bloß irgendein alter Teilstring gezählt. Ein Fragment erhält
die stärkere Trägerwertung nur, wenn es früher als vollständige laufende Karte
vorkam. Eine wiederkehrende portable Familie benötigt mindestens zwei neue
Oberflächen und ein nichtleeres portables Gerüst.

## Kontextpolitik

Die zehn alten-Lokal/neuer-Kontext-Kontakte werden vollständig und einzeln
behandelt. Erlaubt sind vier endliche Entscheidungen: exakte Übereinstimmung,
gemeinsame sichtbare Rezeptvereinheitlichung, bereits belegte
Name-plus-Funktionsschale oder ausdrücklich rollenabhängige Label-/Prosalesung.
Eine rollenabhängige Form erhält zwei sichtbare Rezepte, aber keine zweite
portable Wortbedeutung.

`x` wird auf f66r als neutraler lokaler Tag `LOCAL_X` vereinheitlicht, gleich
ob es allein oder in `axor/chxar` steht. `LOCAL_C`, `LOCAL_NAME_CORE_D` und
`LOCAL_NAME_CORE_YD` bleiben ebenfalls lokale Tags ohne portablen Wert.

## Zusätzliche Familienprüfungen

Alle laufenden 30-Seiten-Oberflächen auf sichtbares `…dy` werden erneut
gezählt. Für jedes tatsächlich vorhandene `…dy`/`…y`-Paar wird festgehalten,
ob beide Oberflächen dasselbe oder verschiedene Rezepte tragen. Dadurch wird
ein sichtbares `d` vor `y` nicht automatisch als Schlusszeichen behandelt.

Aus den 159 neuen Rezepten werden außerdem benachbarte Aktionsköpfe einmal
direkt und einmal nach Ausblendung dazwischenliegender Slots gezählt. Alte
26-Seiten-Beobachtungen und die GDT427-Liste erlaubter, bislang fehlender
Folgen werden daneben gestellt.

## Ausgabe und Grenze

Der Builder schreibt einen 159-Zeilen-Familienatlas, die endlichen
Kontextentscheidungen, die `dy/y`- und Aktionsfolgen-Audits sowie reversible
Overlays über alle 597 neuen Karten und alle 5.866 Gruppen. Die Originalspalten
bleiben unverändert; neue Entscheidungen stehen nur in zusätzlichen
GDT516-Spalten.

Der Pass ist eine kreative Arbeitskonsolidierung. Er bestätigt kein Lexem,
keinen Klartext, keine Sprache und keine historische Wortbedeutung.
