# GDT636 — aus 19 offenen Resten wird ein kleines Apotheker-Feldsystem

## Ergebnis

Die 19 in GDT635 noch offenen Vierkopf-Reste brauchen keine 19 unabhängigen
Wortbedeutungen. Sie lassen sich fast vollständig aus einem kleinen Satz von
Stoff-, Zustands-, Zubereitungs-, Träger- und Stufenfeldern zusammensetzen.

Das vollständige Raster umfasst:

- 19 Restkörper;
- 76 tatsächlich belegte `p/s/r/l + Rest`-Formen;
- 527 Token auf der unveränderten 179-Seiten-Auswahl;
- 398 dreileser-exakte Oberflächen;
- 527 einzeln veröffentlichte Zeilenkontexte;
- 14 konkrete Übersetzungsspannen mit 42 Zieltoken;
- ein V13-Wörterbuch mit 251 Zeilen.

Damit bleibt in dieser Vierkopf-Fläche kein Rest und keine der 76 Formen ohne
Default.

## Die vollständige 19er-Tabelle

| Rest | Zerlegung | kurzer Default | konkrete Vierkopflesung |
|---|---|---|---|
| `ar` | `a+R` | Fraktionsklasse I | Pulver-/Samen-/Wurzel-/Holzfraktion I |
| `chey` | `ch+e+y` | Trockenform I | jeweiliger Kopfstoff, trocken gebunden, Form I |
| `al` | `a+L` | Rohstoffform I | Pulver-, Saat-, Wurzel- oder Holzrohstoff I |
| `y` | `y` | unmarkierte Grundform | Kopfstoff in Grundform |
| `air` | `a+i+R` | Fraktionsklasse II | Pulver-/Samen-/Wurzel-/Holzfraktion II |
| `chdy` | `ch+d+y` | getrocknete Kurz-/Kompaktform | jeweiliger Kopfstoff, durchgetrocknet |
| `oiin` | `o+iin` | Zubereitungsform III | Pulver-/Samen-/Wurzel-/Holzzubereitung III |
| `shey` | `sh+e+y` | Feucht-/Einweichform I | angefeuchteter oder eingeweichter Kopfstoff I |
| `am` | `a+m` | Maßform I; nur zeilenfinal zusätzlich Abschluss | ein Maß des Kopfstoffs; in Endstellung zusätzlich Eintrag abgeschlossen |
| `cheey` | `ch+ee+y` | Trockenform II | jeweiliger Kopfstoff, trocken gebunden, Form II |
| `chy` | `ch+y` | Trocken-Grundform | trockener Kopfstoff in Grundform |
| `olchedy` | `ol+chedy` | getrockneter Zubereitungsstoff | getrockneter Pulver-/Saat-/Wurzel-/Holzansatz |
| `chol` | `ch+ol` | trockener Stoff/Trockengut | trockenes Gut des jeweiligen Kopfstoffs |
| `odaiin` | `o+d+a+III` | Zubereitungsdosis III | Kopfstoffzubereitung, Dosis III |
| `oraiin` | `o+r+a+III` | Portion III | Pulver-/Samen-/Wurzel-/Holzportion III |
| `ody` | `o+d+y` | fertig aufbereitete Grundform | Kopfstoff, fertig aufbereitet |
| `cheo` | `ch+e+o` | Trockenansatz | trockene Zubereitung des Kopfstoffs |
| `oaiin` | `o+a+III` | Zubereitungscharge III | Kopfstoffzubereitung, Charge III |
| `oral` | `or+al` | Rohstoff-/Zutatenportion | Portion des jeweiligen Rohstoffs |

Die vollständigen 76 Einzelglossen mit Vorkommens- und Leserzahlen stehen in
`artifacts/RESIDUAL_76_FORM_GRID.tsv`.

## Der stärkste Gewinn: drei echte Leitern

### A-R ist eine Fraktionsleiter

```text
ar      Fraktion I
air     Fraktion II
aiir    Fraktion III
aiiir   vorhergesagte Fraktion IV
```

| Stufe | nackt | unter `p/s/r/l` |
|---|---:|---:|
| `ar` | 321 | 90 |
| `air` | 56 | 31 |
| `aiir` | 20 | 4 |
| `aiiir` | 0 | 0 |

13 Zeilen enthalten mindestens zwei nackte Stufen. Unter den vier Köpfen gibt
es für `ar` zwei exakte zweiseitige Austauschrahmen:

```text
f86v6.17  par  or ...    Pulverfraktion I ...
f33v.9    sar  or ...    Samenfraktion I ...

f81v.1    par  shey ...  Pulverfraktion I, Feuchtform I ...
f103r.17  sar  shey ...  Samenfraktion I, Feuchtform I ...
```

Der ältere globale Wert `air = Wurzelteil` wird dadurch ersetzt. Ein
Wurzelbild kann lokal zeigen, wovon eine Fraktion genommen wird; es kann aber
nicht erklären, warum derselbe Rest in `pair/sair/rair/lair` erscheint.

### O-N ist eine Zubereitungsleiter

```text
on / oin / oiin / oiiin = Zubereitungsform I / II / III / IV
```

Die nackten Häufigkeiten sind `1/7/26/11`, die vierköpfigen `0/5/25/5`.
Darum ist `oiin` in dieser Notation **III**, nicht II und nicht ein isoliertes
Fantasiewort.

### A-M ist eine Maß-/Abschlussleiter

```text
am / aim / aiim = Maßform I / II / III
```

Nackt tritt die Reihe `67/5/1`-mal auf; 58 ihrer 73 Vorkommen stehen am
Zeilenende. Bei den vierköpfigen `pam/sam/ram/lam` stehen 21 von 24 am Ende,
darunter `ram` 11 von 11. Der konkrete Default lautet deshalb „Maß I“ und in
Endstellung zugleich „Eintrag abgeschlossen“. „Mischen/unterarbeiten“ bleibt
als praktischer Rivale erhalten, wird aber nicht ohne sichtbaren Beleg zum
Verb befördert.

## Warum `ar`, `or`, `al` und `ol` nicht dasselbe heißen dürfen

Der wichtigste Kollisionscheck zählt vollständige physische Zeilen, in denen
beide Oberflächen vorkommen:

| Paar | gemeinsame Zeilen | notwendige Trennung |
|---|---:|---|
| `ar / or` | 48 | Fraktion I / Portion |
| `al / ol` | 20 | Rohstoffform I / allgemeines Material |
| `chey / cheey` | 15 | Trockenform I / II |
| `chy / chdy` | 7 | trockene Grundform / durchgetrocknetes Ergebnis |
| `chdy / chedy` | 24 | kurze-kompakte / erweiterte Trockenresultatform |
| `shey / shedy` | 39 | feuchte Form I / eingeweichtes Ergebnis |

Damit verschwinden die bisherigen schlimmsten Doppelglossen. Ein Text kann
nun etwa eine **Samenfraktion II** (`sair`) zusammen mit einer **Portion III**
(`oraiin`) und **Saatmaterial** (`sol`) führen, ohne dreimal dasselbe zu sagen.

## `ody` heißt nicht kühlen

`ody` wurde zeitweise als „kühlen“ geführt. Das widerspricht dem eigenen
Kompositionssystem: Kälte wird durch `t`, Hitze durch `k` markiert; in `o+d+y`
steht keines von beiden. Die elf Vierkopfbelege, zehn davon dreileser-exakt,
passen besser zu:

```text
o   Zubereitung
d+y resultativ/fertig
ody fertig aufbereitet
```

So ergibt `f106v.38 rody raiin` konkret **„aufbereitete Wurzel, Charge III“**.

## Die Syntax bleibt zweigeteilt

Die 527 Vorkommen verteilen sich nicht wie vier austauschbare Wörter:

| Kopfklasse | Token | am Zeilenanfang | Mitte oder Ende |
|---|---:|---:|---:|
| `p/s` Eintrag/Stoff | 285 | 128 | 157 |
| `r/l` Zutat/Pflanzenteil | 242 | 16 | 226 |

Die bessere Arbeitsgrammatik bleibt daher:

```text
p/s = Eintrags-, Stoff- oder Chargenkopf
r/l = überwiegend interner Zutaten- oder Pflanzenteilkopf
```

Der gleiche Rest erzeugt unter allen vier Köpfen eine semantische Familie,
aber keine künstlich flache Einheits-Satzstellung.

## Vierzehn konkrete Lesungen

1. `f86v6.17 par or aiin`
   **Pulverfraktion I; weitere Portion III.** Dreileser-exakt.

2. `f33v.9 sar or aiin`
   **Samenfraktion I; weitere Portion III.** Dreileser-exakt.

3. `f81v.1 par shey`
   **Pulverfraktion I, angefeuchtet/eingeweicht bis Form I.** Dreileser-exakt.

4. `f81r.24 par ody`
   **Pulverfraktion I, fertig aufbereitet.** ZL3b/IT2a verbinden hier die
   Grenze unterschiedlich; diese Gabel bleibt sichtbar.

5. `f4r.12 soiin chaiin chaiin`
   **Samenzubereitung III; zweimal trocken, Grad III.** Ganze Zeile
   dreileser-exakt.

6. `f49r.12 podaiin cheo kcho daiin chcthy`
   **Pulverzubereitung, Dosis III: Trockenansatz; heiß-trockener Ansatz,
   Dosis III, mit trockenem Blatt-/Krautgut.** Ganze Zeile dreileser-exakt.

7. `f14r.13 sodaiin chy kchy kchy`
   **Samenzubereitung, Dosis III; trocken in Grundform, zweimal heiß-trocken
   markiert.** Dreileser-exakt.

8. `f106v.38 rody raiin`
   **Aufbereitete Wurzel, Charge III.** Dreileser-exakt.

9. `f106r.13 pcheo ror aiin`
   **Trockener Pulveransatz mit Wurzelportion III.** Eine Lesergrenze variiert.

10. `f114v.33 kaiin sheey oaiin sheol`
    **Heiß, Grad III; feucht in Form II; Zubereitungscharge III aus feuchtem
    Material.** Das vierte Zieltoken selbst ist instabil: ZL3b/IT2a lesen
    `sheol`, RF1b liest `eol`.

11. `f77v.37 cheey roiin daiin shey`
    **Wurzelzubereitung III, Dosis III: von Trockenform II in Feuchtform I.**
    RF1b trennt `r|oiin`, IT2a liest an derselben Stelle `raiin`.

12. `f83r.40 solchedy olchedy chedaiin`
    **Getrockneter Samenstoff; getrockneter Zubereitungsstoff; Trockenansatz,
    Dosis III.** RF1b zerlegt die Oberflächen stärker.

13. `f114r.21 lcheey lchedo lcheo`
    **Drogenholz in Trockenform II; getrocknete Holzform; trockene
    Holzzubereitung.** Dreileser-exakt.

14. `f77r.7 soral`
    **Samen-Rohstoffportion.** Vollständiger Einwort-Eintrag, dreileser-exakt.

Neun der vierzehn Spannen sind vollständig dreileser-exakt. Sämtliche
abweichenden Grenzen und Glyphlesungen stehen im Artefakt; keine wird zur
scheinbaren Übereinstimmung geglättet.

## Historische Passform

[Wellcome MS.542](https://wellcomecollection.org/works/n674z2xd), frühes 15.
Jahrhundert, enthält ein Materia-medica-Glossar, das gelernte Drogennamen mit
`lignum` oder `radix`, den abgekürzten Qualitäten heiß/trocken und den Graden
II/III verbindet. Das ist genau die gesuchte Architektur aus Ganzwort,
Fachkürzel und Stufe.

[Pal. lat. 1234](https://digi.ub.uni-heidelberg.de/diglit/bav_pal_lat_1234),
Deutschland um 1400, vereint Gradtabellen einfacher Arzneien, einfache und
zusammengesetzte Arzneien, Dosierung, Arzneiwässer, Öle, Materia medica und
einen eigenen Text über Samen in einer Handschrift.

[Wellcome MS.307](https://wellcomecollection.org/works/rexwctzt), spätes 14.
Jahrhundert, mischt gelernte Zutatenwörter mit dem Mengenkürzel `ana`, knappen
Zahl-/Gewichtsangaben und Samenbezeichnungen. Ein technischer Zahlenslot muss
also historisch kein ausgeschriebenes natürlichsprachliches Wort sein.

[Salzburg UB M I 89](https://manuscripta.at/?ID=8162), Bayern/Österreich an der
Wende vom 14. zum 15. Jahrhundert, ist eine lateinisch-deutsche medizinische
Sammelhandschrift; ihr Rezeptteil belegt `pulvis` und `semen` im selben
technischen System ([f148v](https://manuscripta.at/diglit/AT7400-MI89/0298),
[f266r](https://manuscripta.at/diglit/AT7400-MI89/0533)).

Diese Parallelen beweisen keine lateinischen Voynich-Initialen. Sie zeigen
aber, dass die gesuchte Mischform — gelernter Drogenkopf, kurzer
Qualitäts-/Trägercode und kompakte Stufe — um 1400 tatsächlich existierte.

## Wörterbuch V13 und nächste Konsequenz

V13 enthält 251 Zeilen. Die ersten 156 V12-Zeilen bleiben reihenfolge- und
inhaltgleich. Danach folgen 19 explizit begrenzte Restwerte und alle 76
belegten Ganzformen. Der Validator besteht 2.526 Prüfungen und reproduziert 13
Builder-Ausgaben byteidentisch.

Der nächste Hebel ist jetzt klar: zuerst die schon sichtbaren Fortsetzungen
`aiir`, `oiiin`, `aim` und `aiim` unter den vier Köpfen lesen und ihre noch
leeren Zellen als konkrete Vorhersagen festhalten. Danach wird V13 über alle
bereits geöffneten Zeilen gelegt, um die Zeilen mit genau einem unbekannten
Slot zu finden. So wächst die nächste Runde direkt zu vollständigen Passagen,
nicht wieder zu generischer Prozessprosa und nicht zurück zu `f1r`.
