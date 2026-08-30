# GDT651 — vier CKH-Schalen statt erfundener Misch- und Bindungsprosa

## Ergebnis

Das CKH-Feld ist jetzt als ein einziges 4×6-Raster in V28 abgebildet. Acht
bereits vorhandene Karten wurden korrigiert, sieben beobachtete Schwesterformen
neu aufgenommen. Die neuen Formen lesen 124 zuvor offene Tokenpositionen und
schließen vier weitere Mehrwortzeilen, drei davon strikt.

Die wichtigste inhaltliche Korrektur ist bewusst deutlich: **„Arzneimischung“
und physisch „gebunden“ waren zu konkret, ohne dass eine Mischhandlung oder
Bindung sichtbar war.** V28 verwendet stattdessen den ersetzbaren Sachkopf
„Arzneikompositum“ und behandelt das äußere `E` nur familienintern als
attributive Fügung (`E_ATTR`).

## Das Raster

| Schale | Arbeitslesung am Beispiel Y | Parse |
|---|---|---|
| CHCKHY | Arzneikompositum: trocken, Gradanfang | CH+CKH+Y |
| CHECKHY | trockenes Arzneikompositum am Gradanfang | CH+E_ATTR+CKH+Y |
| SHCKHY | Arzneikompositum: feucht, Gradanfang | SH+CKH+Y |
| SHECKHY | feuchtes Arzneikompositum am Gradanfang | SH+E_ATTR+CKH+Y |

Das äußere E erzeugt also im jetzigen Modell keinen zweiten Gegenstand und
keinen physischen Zustand. Es kippt die lemmahafte Qualitätsangabe in eine
attributive Form. `CKH` und `E_ATTR` bleiben reine familiengebundene
Analysetags; im Wörterbuch steht keine freie Karte für eines von beiden.

Die Endungen werden innerhalb der Familie weiterhin so gerendert:

| Endzelle | lokaler Wert |
|---|---|
| Y | Gradanfang |
| EY | Gradmitte |
| EEY | Gradende |
| DY | Gradanfang, abgeschlossen |
| EDY | Gradmitte, abgeschlossen |
| EEDY | Gradende, abgeschlossen |

17 der 24 Rasterzellen sind beobachtet; 15 besitzen mindestens einen
dreileser-exakten Anker. CHECKHEDY und SHECKHDY sind zwar beobachtet, aber ohne
exakten Zielbeleg und bleiben draußen. Sieben weitere Zellen fehlen ganz und
erhalten keine Bedeutung.

## Sieben neue Ganzkarten

| Oberfläche | V28-Arbeitswert | Belege | Seiten | exakt | Stufe |
|---|---|---:|---:|---:|---|
| CHECKHY | trockenes Arzneikompositum am Gradanfang | 46 | 31 | 43 | stark |
| CHECKHEY | trockenes Arzneikompositum in der Gradmitte | 10 | 9 | 9 | stark |
| CHECKHDY | trockenes Arzneikompositum am Gradanfang, abgeschlossen | 1 | 1 | 1 | niedrig belegt |
| SHCKHY | Arzneikompositum: feucht, Gradanfang | 51 | 25 | 44 | stark |
| SHCKHEY | Arzneikompositum: feucht, Gradmitte | 10 | 9 | 8 | stark |
| SHCKHDY | Arzneikompositum: feucht, Gradanfang, abgeschlossen | 1 | 1 | 1 | niedrig belegt |
| SHCKHEDY | Arzneikompositum: feucht, Gradmitte, abgeschlossen | 5 | 4 | 3 | niedrig belegt |

Insgesamt sind 109 von 124 neuen Zieltoken in allen drei Lesern exakt; ein
weiteres ist durch Zusammenziehen der Lesergrenze stabil. 14 Stellen behalten
eine sichtbare Leserwarnung. Es wurde keine Kollision mit einer bereits
konkret gelesenen Nachbarstelle festgestellt.

## Warum „Arzneikompositum“?

Der Ausdruck ist hier keine behauptete Klartextübersetzung. Er ist die bisher
beste konkrete Sachklasse für einen gelernten Familienkopf, der regelmäßig mit
trocken/feucht und Graden kombiniert wird. „Arzneigut“ wäre sicherer, aber so
allgemein, dass es wenig erklärt; „Arzneimischung“ suggeriert dagegen einen
nicht beobachteten Arbeitsvorgang.

Die historische Parallele trägt die Architektur, nicht die Entzifferung:

- [Wellcome MS 542](https://wellcomecollection.org/works/n674z2xd), ein
  Arzneimitteltext des frühen 15. Jahrhunderts, verbindet Materia-medica-Lemmata
  kompakt mit Qualitäten und Graden.
- [Ó Cuinn, 1415](https://celt.ucc.ie/published/G600005/index.html) ordnet
  Drogennamen, heiß/kalt beziehungsweise trocken/feucht und Gradangaben.
- Die überlieferte Fassung von [De dosibus](https://celt.ucc.ie/document/T600021/)
  behandelt ausdrücklich einfache und zusammengesetzte Arzneien.

Damit ist ein gelerntes Arzneikompositum in einem Qualitäts-/Gradraster um
1420 typologisch plausibel. Es beweist weder Latein noch Irisch noch eine
bestimmte historische Vorlage.

## Vier neu vollständige Zeilen

    f30v.4   otchey daiin chor checkhy qotchod daiin
             Kalt-trockener Ansatz im Mittelgrad; Gradwert III;
             Pflanzenteil; trockenes Arzneikompositum am Gradanfang;
             kalt-trockene Zubereitung, fertig gebunden; Gradwert III.

    f80r.43  sor sheckhy qokar checkhy okain sheckhy qokeey ly
             Samenportion; feuchtes Arzneikompositum am Gradanfang;
             heiße Portion; trockenes Arzneikompositum am Gradanfang;
             heißer Ansatz Grad II; feuchtes Arzneikompositum am
             Gradanfang; heiß am Gradende; rohes Drogenholz.

    f83r.27  dain chedy qokeedy shckhedy shckhedy
             Gradwert II; trocken in der Gradmitte, abgeschlossen;
             heiß am Gradende, abgeschlossen; zweimal Arzneikompositum:
             feucht, Gradmitte, abgeschlossen.

    f76v.33  saiin otaiin shckhedy
             Samencharge III; kalter Ansatz Grad III;
             Arzneikompositum: feucht, Gradmitte, abgeschlossen.

Die ersten drei Zeilen sind dreileser-strikt; f76v.33 ist vollständig, trägt
aber eine Leserabweichung. Es bleiben Sachlisten, keine ausformulierten
Rezepte. Dennoch benennen sie eine Arzneiklasse, Qualität und Grad statt des
früheren generischen oder unbelegt physischen Ersatztexts.

## V27 nach V28

| Kennzahl | V27 | V28 | Änderung |
|---|---:|---:|---:|
| Wörterbuchzeilen | 435 | 450 | +8 Revisionen, +7 neue Karten |
| exakte Glossaroberflächen | 372 | 379 | +7 |
| bekannte Tokenpositionen | 14.617 | 14.741 | +124 |
| unbekannte Tokenpositionen | 17.722 | 17.598 | −124 |
| vollständige Mehrwortzeilen | 103 | 107 | +4 |
| davon strikt | 59 | 62 | +3 |
| Ein-Loch-Zeilen | 153 | 159 | +6 netto |
| davon strikt | 41 | 40 | −1 netto |

Die Bedeutungsrevision und die sieben Ergänzungen verändern 308 Zeilen. Die
höhere Zahl der Ein-Loch-Zeilen ist kein Rückschritt: Neun vorher stärker
unvollständige Zeilen werden erst durch die neuen Karten bis auf genau ein
unbekanntes Wort freigelegt.

## Aussagegrenze

V28 ist eine konkrete **explorative** Arbeitsübersetzung, keine Lösung des
Voynich-Manuskripts. „Arzneikompositum“ und `E_ATTR` sind ersetzbare
Familienwerte. Es werden weder ein freies CKH/E, eine Sprache, Lautwerte,
Zutaten noch Bedeutungen für fehlende Rasterzellen behauptet.
