# GDT819 — f77r: sichtbare Formen vor hypothetischer Satzgrammatik

2026-09-05. Aktuelle Route, Index/Arbeitsbasis GDT818 und GDT819
PREREGISTRATION gelesen. Die widersprüchlichen Lesungen und C0-Satzversuche
waren bekannt; dies ist kein blinder paläographischer Test. Keine neue Seite,
keine Bildbearbeitung, keine geänderte Transkription oder Wortbedeutung.

## Ergebnis in drei getrennten Aussagen

1. **f77r.12:** Der erste strittige -daiin-Cluster besitzt einen sichtbaren
   Zusatz über dem linken Bankzeichen. Das begünstigt lokal **IT shedaiin**
   gegenüber unmarkiertem ZL chedaiin. Es folgt ein sichtbar abgesetzter
   chedy-artiger Cluster, ohne eindeutiges Satzgrenzzeichen. Der deutsche
   Konflikt `ist wird/enthält` ist dadurch an dieser Stelle weniger quellensicher,
   nicht grammatisch gelöst und nicht aus einer Lesung gelöscht.
2. **f77r.34:** Zwei aufeinanderfolgende, jeweils vollständig geschriebene,
   stark ähnliche qokaiin-artige Gruppen sind sichtbar. Die Wiederholung ist
   nicht bloß ein doppelter Tabellen-/Renderereintrag. Eine neue Bedeutung,
   zwei Luftsorten oder zwei Satzrollen folgen daraus nicht.
3. **f77r.35:** Die acht großen ZL/IT-Gruppen sind im Bild gut nachvollziehbar.
   Vor dem Schlusswort liegt ein kompakter Cluster mit d-artigem Schleifenstrich;
   eine zusätzliche sichere Wortgrenze entsprechend RF-clean `che aiin` sehe
   ich nicht. Der nachträglich gelesene Rohquellen-Audit bestätigt hier ebenfalls
   acht RF-Quellgruppen; die neunte ASCII-Einheit entsteht im Cleaner. Die
   k/t-Zuweisung im vorherigen Galgenwort bleibt hier **offen**. Acht Gruppen
   sind trotzdem kein Nachweis von acht deutschen oder sprachlichen Wörtern.

## Authentifizierte Quelle und Vorgehen

GDT811 `src/VISUAL_SOURCES.tsv` wurde guarded nur für physical_page=f77r
projiziert. Das persönlich zuerst betrachtete ganze offizielle Bild ist:
[Yale 1006212, Gesamtseite](https://collections.library.yale.edu/iiif/2/1006212/full/2000,/0/default.jpg),
2000 × 2687 Pixel, SHA-256
`6bcedcaccc8107da32d6d1ca950b96708b529538d7902a2108398a3c0b9327df`.
Es trifft den vorhandenen GDT811-Hash exakt und wurde aus dem Cache wiederverwendet.

[Offizielles info.json](https://collections.library.yale.edu/iiif/2/1006212/info.json)
nennt die native Bezugsfläche 2793 × 3752. Anschließend wurden ausschließlich
unveränderte IIIF-Pixelregionen desselben Bildes in nativer Regionsgröße
angefordert und persönlich angesehen. Keine Hochskalierung, Schärfung,
Kontraständerung, Retusche, Generierung oder neue OCR. Alle sieben tatsächlich
verwendeten Renditionen mit URL, Region, Ausgabemaßen und Hash stehen in
`F77R_IMAGES.tsv`; keine privaten Cachepfade sind Teil der Veröffentlichung.

Die gesamte f77r-Textfolge aller drei Lesungen sowie die Quellenflags wurden
zur Ortsregistrierung durch die folgenden begrenzten Projektionen gelesen:

```sh
./vmanus-exp query-tsv transcription/voynich_zl3b_lines.tsv --selector page --allow f77r --columns page,locus,kind,paragraph_start,paragraph_end,eva_clean --forbid-prefix f84 --forbid-prefix f84r
./vmanus-exp query-tsv transcription/voynich_cross_transcription_lines.tsv --selector page --allow f77r --columns page,locus,zl3b_clean,it2a_clean,rf1b_clean --forbid-prefix f84 --forbid-prefix f84r
```

Jeweils 50 selektierte Loci, nicht 50 Prosa-Zeilen: .1–8 sind getrennte obere
Labels; P.9–24 ist der erste Prosaabsatz, P.25–37 der zweite, P.38–48 der
dritte; .49/.50 sind weitere getrennte Labels. Somit ist .12 die vierte
physische Zeile des ersten Prosaabsatzes, .34/.35 die zehnte/elfte des zweiten.
Die Zählung diente erst nach dem Abgleich der ganzen Nachbarfolgen als Kontrolle.

Auf der ganzen Seite liegt P.9–24 unter dem großen oberen Bildbogen. P.25–37
füllt den Raum rechts der mittleren Figur-/Auslassdarstellung und läuft unten
weiter nach links. Seine wechselnde linke Begrenzung ist kein neuer Absatz
bei jeder Einrückung. Die untersuchten Wörter haben keine Bildzeiger; weder
die mittlere Darstellung noch der obere Bogen wird zum Einzelwortbesitzer.

## f77r.12: oberes Zeichen, nicht glatter deutscher Satz

Ortsabgleich in F77R_UPPER_CONTEXT:

```text
.11 qoteedy qokaiin shedy chol shedy shcthey qokeedy oteedy cham
.12 ZL solteedy qoteedy qodeedy chedaiin chedy shedaiin shealol ched
.12 IT solteedy qoteedy qodeedy shedaiin chedy shedaiin sheol ol ched
.12 RF soltee y qotee y qodeedy che aiin che y shedaiin sheolol che
.13 ZL qokeedy qol sheedy shol tedy chedy lsheedy qokedy qolal chedy
```

Die ganzen Anfangsfolgen .11 und .13 sowie .12 `solteedy qoteedy qodeedy`
registrieren die Zielzeile; die abweichenden Endtrennungen werden nicht zur
Ortswahl passend gemacht. F77R_L12_DETAIL zeigt den mittleren/rechten Teil
mit beiden -daiin-Gruppen und dem dazwischenstehenden chedy-artigen Cluster.

Am **ersten** strittigen Bankanfang steht über dem waagerechten Bankteil ein
hochgezogener gebogener, stellenweise geschlossen wirkender Strich. Der später
in allen drei Lesungen als shedaiin wiedergegebene Cluster derselben Zeile hat
einen ähnlichen markierten Beginn. Der dazwischenliegende chedy-artige Anfang
hat diesen Zusatz nicht in gleicher Weise. Dies ist der konkrete Bildgrund
für die vorläufige Präferenz shedaiin am ersten Ort; kein Wunsch, `ist wird`
zu vermeiden. Root hat diese beiden Ausschnitte separat angesehen und denselben
Zusatz bemerkt. Das sind zwei Beobachter desselben RGB-Bildes, keine zwei Quellen.

Zwischen der ersten -daiin-Gruppe und dem folgenden chedy liegt sichtbare freie
Fläche. Ich erkenne dort keinen eigenständigen eindeutigen Punkt/Strich als
Satzzeichen, keinen Zeilenwechsel und keinen Absatzbeginn. Der Abstand wird
nicht numerisch als Ausreißer behauptet. Die zwei Gruppen bleiben zwei Gruppen;
das Bild fügt weder eine syntaktische Trennung ein noch beweist es, dass eine
unmarkierte Klauselgrenze ausgeschlossen wäre.

**Folge:** Eine exakte GDT818-Kopula `chedaiin=ist?` kann an diesem Ort nur
unter der umstrittenen ZL-Ganzwortlesung eingesetzt werden. Die visuelle
IT-Präferenz lässt diesen speziellen Gegenkontakt schwächer werden. Sie
bestätigt die Kopula andernorts nicht und macht aus shedaiin kein Synonym.

## f77r.34: die doppelte Gruppe bleibt geschrieben

F77R_MIDDLE_CONTEXT registriert die Zielstelle durch diese unverkürzte Folge:

```text
.33 ZL daiin chedy qol keedy qoteeedy sar oiiiin cheety dy
.34 ZL qokaiin shedy chedy qolchedy qokaiin qokaiin checkhy raiin
.34 IT qokaiin shedy chedy qol chedy qokaiin qokaiin checkhy raiin
.34 RF qokaiin shedy chedy qolche y qokaiin qokaiin checkhy aiin
.35 ZL solkeey okaiin chedy qokain sheedy qokaiin chedaiin chealy
.36 ZL dshedy pchedy qotain chedy dolchl qokeedy qokol olchey
```

Im rechten Teil von .34 sind zwei aufeinanderfolgende komplette q-/o-/Galgen-
und Minimgruppen zu sehen, jeweils mit eigenem Anfang und Auslauf. Ihre starke
Ähnlichkeit erklärt den dreifach gleichen qokaiin-Doppelansatz. Es ist nicht
ein einzelner langer Auslauf, der vom Tabellenrenderer zweimal ausgegeben wird.
Die beiden Gruppen sind durch unbeschriebenen Zwischenraum getrennt; ich sehe
keine Streichung, die eine von ihnen als offensichtlich aufgehoben ausweist.
Aus einem RGB-Bild wird daraus keine Behauptung über Schreibchronologie gemacht.

Kein eigenes eindeutiges Satzzeichen trennt die beiden wiederholten Gruppen.
Die Wiederholung liegt innerhalb derselben physischen Zeile, nicht über einer
Absatzkante. Auch vor .35 erfolgt nur der nächste physische Zeilenbeginn im
selben Quellenabsatz. Die vorhandene Formverdoppelung bleibt daher eine reale
Aufgabe für jede feste Luft- oder andere Wortvermutung; sie darf weder gelöscht
noch durch ungeschriebene Unterscheidungsmerkmale aufgelöst werden.

## f77r.35: ganze Folge und unsichere Stellen getrennt

```text
ZL/IT solkeey okaiin chedy qokain sheedy qokaiin chedaiin chealy
RF    solkeey okaiin chedy qokain sheedy qotaiin che aiin chealy
```

Das Bild lässt die Folge vom linken solkeey-artigen Anfang bis zum chealy-
artigen Schluss verfolgen, nicht nur einen isolierten hübschen Vierwortsatz.
Die folgende .36 beginnt sichtbar anders (`dshedy pchedy qotain …`); .35 ist
kein nachträglich aus zwei verschiedenen Zeilen zusammengesetzter Versuch.

**Galgenwort nach sheedy:** Das Ziel ist als ganze Gruppe geschrieben. Im
höheren Galgenbereich sieht man einen kleinen oberen Ring/Schlaufenbereich;
die anschließende a-/Minimfolge ist vorhanden. Die unmittelbar darüberstehenden
Doppelgruppen .34 sowie die qotedy-Vergleichsgruppen .31 wurden im nativen
F77R_L31_COMPARATOR mit betrachtet. Die kleine Formdifferenz genügt mir hier
nicht für eine sichere k/t-Zuweisung. Deshalb bleiben ZL/IT qokaiin und RF
qotaiin als benannte Alternativen stehen; keine Lesung gewinnt aufgrund von
`Luft` oder der gewünschten Bedingung.

**Vorletzte große Gruppe:** F77R_L35_TAIL_DETAIL zeigt nach dem Bank-/che-
artigen Anfang vor dem aiin-artigen Auslauf einen aufragenden, geschlossen
wirkenden Schleifenstrich. Er ist mit einem d-artigen Zeichen vereinbar.
Innerhalb dieser Folge erkenne ich keinen auffallend großen leeren Zwischenraum,
der eine harte Trennung `che | aiin` sichtbar erzwingen würde. Die kompakte
chedaiin-Gruppierung ist visuell plausibel. Die hier zitierte RF-clean-Leerstelle
ist selbst kein Beweis für eine vom Schreiber gesetzte Wortlücke. Der nach
dieser persönlichen Bildbeobachtung gelesene Rohquellen-Audit kontrolliert die
Normalisierung gesondert, siehe folgender Nachtrag.

**Gruppen- gegen Satzgrenze:** Die acht großen ZL/IT-Gruppen sind als praktische
Bildgliederung nachvollziehbar, aber freie Fläche besitzt keinen entzifferten
grammatischen Wert. Insbesondere gibt es zwischen qokain und sheedy, wo der
deutsche wenn-Satz beginnen soll, kein eindeutiges zusätzliches Satzgrenzzeichen
oder einen Absatzwechsel. Ein gewöhnlicher Wortabstand beweist weder den
Nebensatz noch dessen Abwesenheit. Ebenso wird aus dem letzten sichtbaren
Wort und dem Zeilenende kein gesicherter Satzabschluss.

### POST_SOURCE_AUDIT: die RF-Leerstelle ist kein zweites Quellwort

`src/SOURCE_AUDIT.md` wurde anschließend vollständig gelesen. Der dort
quellengebundene separatorbewahrende Atlas gibt für RF .35 die Schlussgruppen
`sheedy.qotaiin.che@152;aiin.chealy` an. Insgesamt sind es acht Quellgruppen,
nicht neun. `che@152;aiin` wird durch den Legacy-Cleaner an der Semikolongrenze
in die ASCII-Fragmente `che aiin` zerlegt; das sind nicht zwei von RF getrennt
angesetzte Quellwörter. Nicht die Entfernung eines Fragezeichens, sondern die
Behandlung der numerischen Entität mit Semikolon erzeugt die zusätzliche Grenze.

Dasselbe Problem betrifft auf RF .12 die Gruppen `che@152;aiin` und
`che@152;y`: Die vier ASCII-Fragmente sind dort zwei Quellgruppen. Die
Nummernentität `@152;` bleibt ausdrücklich uninterpretiert und wird nicht
automatisch durch EVA d ersetzt. Der echte RF-Ganzwortunterschied qotaiin
auf .35 bleibt ebenfalls. Die source-aware Korrektur entfernt somit das
Argument „RF schreibt ein zusätzliches Wort“, nicht jede Glyphendifferenz
und schon gar nicht die Pflicht, die Wortbedeutungen unabhängig zu begründen.

## Begrenzter Beitrag zur laufenden Inhaltsarbeit

Die Bildprüfung entfernt kein bequemes Problem per Bedeutungswechsel:
die Doppelgruppe .34 bleibt; .12 besitzt tatsächlich einen für die konkurrierende
Lesung wichtigen Zusatz; .35 hat einen kompakten vorletzten Cluster, aber noch
eine offene k/t-Frage. Die festen vier Nomen-/Prädikatswelten sowie wenn/mit,
Luft/ist/kalt bleiben C0. Keine Änderung an ihnen oder an einer TSV-Lesung.

Die nächste Arbeit kann die bedingten Textaussagen präziser formulieren:
`ist wird/enthält` auf .12 ist abhängig von einem jetzt visuell schwächeren
Ganzwortansatz; `Luft Luft` auf .34 bleibt eine tatsächliche Wiederholung unter
der Luft-Hypothese; die .35-Schlussgliederung besitzt auch in RF vier
Quellgruppen, aber eine echte qotaiin- und offene Entitätslesung. Kein Wort und keine
Klausel ist dadurch entziffert. Keine neuen semantischen Bildkanten behauptet.
