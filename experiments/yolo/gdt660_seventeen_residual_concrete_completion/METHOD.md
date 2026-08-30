# GDT660 — Methode

## Frage

Können genau die siebzehn von GDT659 freigelegten Restoberflächen eine
konkrete V37-Arbeitslesung erhalten, die sämtliche ihrer sicheren Vorkommen
abdeckt, ohne `s`, `y`, `dy`, `-ar`, `-ain` oder andere kurze Stücke als freie
Universalwerte in unbekannte Wörter auslaufen zu lassen?

## Eingaben

- GDT659s vollständige V36-Arbeitsedition, Glossar, Wörterbuch und
  179-Seiten-Allowlist;
- die bereits veröffentlichten Familienraster GDT626, GDT635, GDT640,
  GDT645, GDT647, GDT650, GDT652 und GDT657;
- ZL3b-Token sowie ZL3b/IT2a/RF1b-Zeilen ausschließlich über
  `./vmanus-exp query-tsv` mit ausdrücklicher Seitenauswahl und Sperren für
  f1r, f84 und f84r.

## Methode

1. Die Zielmenge wird vor jeder Bedeutungszuweisung auf genau
   `cholkar,qodain,lcho,kchor,okchan,opchar,ydy,schokey,s,dy,solkchy,yckhey,`
   `lshcthy,ysheey,cheeytal,ochedar,cheoty` festgelegt.
2. Sämtliche Zielvorkommen werden samt Position, Nachbarn, Tokenart und drei
   Leserfassungen neu gezählt. Die konservative Spalte `split_normalized`
   akzeptiert nur vollständige, aufeinanderfolgende Lesertoken, deren
   Konkatenation exakt die ZL3b-Zieloberfläche ergibt. Sie erfasst also
   Leser-*Splits* wie `chol | kar`, nicht umgekehrte Fusionen eines nackten
   `s` oder `dy` mit seinem Nachbarn. Die ZL3b-Oberfläche bleibt unverändert.
3. Fünfzehn längere Oberflächen erhalten ausschließlich exakte Ganzformkarten.
   Eine Karte darf sichtbare, bereits belegte Bauteile erklären, exportiert
   diese Erklärung aber nicht in fremde Superformen oder unbelegte Zellen.
4. `s` und `dy` werden occurrence-scoped gelesen. Acht alleinstehende
   L-Token-`s` sind Beschriftungszeichen; die 264 P-Token-`s` erhalten den
   konkreten Samen-/Saatgutdefault. `dy` schließt je nach Position das
   vorausgehende Wertfeld oder den Eintrag und wird praktisch als
   Abschlussvermerk, Semikolon oder Punkt gerendert.
5. `ydy`, `ysheey` und `yckhey` bewahren ihre vollständige Oberfläche, erhalten
   aber eine positionsabhängige Feldwechsel-, Eintrags- oder Bezugsfassung.
6. Die V36-Edition wird tokenweise nach V37 projiziert. Jede Nichtzielposition
   muss in Oberfläche, Glosse, Quelle und Scope unverändert bleiben.
7. Der unabhängige Validator fragt die geschützte Quelle vor dem Lesen der
   Ergebnisdateien erneut ab, rekonstruiert Zählungen und Kontextkarten ohne
   Import des Builders und baut anschließend alle Builderartefakte in einem
   temporären Verzeichnis byte-identisch nach.

## Entscheidungsregel und Aussagegrenze

Jede der siebzehn Zieloberflächen muss an jeder ZL3b-Position eine konkrete
inhaltliche oder sichtbare strukturelle Standardlesung besitzen. Generische
Füller wie „Arbeitsgut“, „Vorgang“, „Schritt ausführen“ oder „weiterleiten“ sind
unzulässig. Ein nicht gesprochenes Zeichen darf als Interpunktion erscheinen,
wenn seine Kontextkarte die sichtbare Funktion benennt.

Die Karten sind eine ersetzbare technische Arbeitstheorie, kein bestätigter
Klartext. Sie behaupten weder Lautwerte noch Sprache, Phonetik, freie
Morpheme, eine bestimmte Pflanze, Krankheit oder Zutat. ZL3b, IT2a und RF1b
sind alternative Lesungen desselben Manuskripts. Es werden keine neue Seite,
kein Bild und keine der gesperrten Seiten f1r/f84/f84r geöffnet.
