# GDT817 — Badehauswart: Behälter, Stoff und Textlage

## Ergebnis und Anspruch

Auf f81v und f83r sind begrenzte Figuren-/Gefäßfelder und angesetzte lange
Formen sichtbar. **Wässriger Dampf ist auf keiner Seite eindeutig identifiziert.**
Das ist kein Nachweis seiner Abwesenheit und keine Widerlegung eines Textes
über Dampf. Die positive praktische Lesung lautet: gemeinsamer Badeplatz auf
f81v; mehrere örtliche Anwendungen mit einer verbundenen Zweiergruppe auf
f83r. Auch das bleibt Bildinterpretation, keine Wortübersetzung.

Genau ein separater Inhaltsrivale wird vorgeschlagen:
`B_CONTAINER: solkeey = Becken?`, ein **offener Behälter**, nicht sein Wasser,
kein Rohr, Auslass, Badvorgang oder allgemeiner Arbeitsplatz. Derselbe Sinn
gilt auf beiden Seiten. Er ist bildlich konkreter gestützt als ein Dampfstoff;
die Bindung gerade dieses Wortes an einen Behälter ist jedoch **nicht** stärker
belegt. Beide Wortmodelle bleiben C0. Das ist eine nach Bild- und Textkenntnis
gebildete Gegenhypothese, kein blinder Test, keine Adoption und kein Synonym
innerhalb der unveränderten Dampf-Hypothese.

## Quellen und tatsächlich gelesener Umfang

Aktuelle Route und GDT816 REPORT zuerst gelesen; Provenienz über GDT791,
V70-Bildinventar und GDT790 kontrolliert. Beide ganzen Seiten persönlich
zunächst als kleinere Cachevorschau und dann in den unten gebundenen offiziellen
Renditionen angesehen. Die höhere f81v-Datei trifft den V70-Hash exakt; f83r
trifft die GDT790-Datei exakt. Andere Pixelgrößen sind andere Dateien und werden
nicht mit deren Hashes gleichgesetzt. Keine neue Voynich-Seite zugelassen.

Die offizielle Yale-Manifestzuordnung lautet f81v → 1006221 und f83r → 1006224:
[Yale-Manifest](https://collections.library.yale.edu/manifests/2002046).
Bild-URLs, Maße und vollständige SHA-256 stehen in `VISUAL_SOURCES.tsv`.

| Seite | tatsächlich persönlich betrachtete Quellenrendition | Maße |
|---|---|---|
| f81v | [Yale 1006221](https://collections.library.yale.edu/iiif/2/1006221/full/1600,/0/default.jpg) | 1600 × 2091 |
| f83r | [Yale 1006224](https://collections.library.yale.edu/iiif/2/1006224/full/2000,/0/default.jpg) | 2000 × 2721 |

Beide vollständigen Seiten wurden in ZL3b/IT2a/RF1b gelesen, nicht nur Treffer:
83 Loci = f81v 28 + f83r 55. Die drei Lesungen sind Varianten **einer** Quelle.
Beide TSV-Zugriffe waren vor dem Payload auf exakt f81v/f83r begrenzt:

```sh
./vmanus-exp query-tsv transcription/voynich_zl3b_lines.tsv --selector page --allow f81v --allow f83r --columns page,locus,line_number,kind,paragraph_start,paragraph_end,eva_clean --forbid-prefix f84 --forbid-prefix f84r
./vmanus-exp query-tsv transcription/voynich_cross_transcription_lines.tsv --selector page --allow f81v --allow f83r --columns page,locus,zl3b_clean,it2a_clean,rf1b_clean --forbid-prefix f84 --forbid-prefix f84r
```

Die Quellenflags ergeben auf f81v P.1–9, P.10–27 und L.28; auf f83r
P.1–8, .9–17, .18–24, .25–30, .31–44, .47–49, .52–55 sowie L.45/.46/.50/.51.
Das sind editorische Absatz-/Labelgrenzen, keine schon entzifferten Sätze.

## f81v: Beobachtung vor praktischer Deutung

- Unten liegt ein großes, abgerundet umrandetes grünes Feld mit 16 nackten
  Figuren in zwei Reihen zu acht. Die Körper sind helle ausgesparte Formen;
  kleine blaue Striche liegen bei einigen Unterkörpern. Die grüne Farbe reicht
  hinter den Figuren hoch: Sie allein ist keine realistische Wasserstandslinie.
- Eine blasse äußere Umrissform läuft unter dem grünen Feld. Ein langer,
  schmaler, stellenweise grüner Fortsatz trifft links auf dessen Randzone.
  Rechts setzt eine dünne Form mit nach unten laufenden Strichen an.
- Viele Arme sind angewinkelt; einige Hände reichen seitlich oder aufwärts.
  Kein klarer Schöpf-, Gieß- oder Heizvorgang ist dadurch festgelegt. Keine
  Figur muss allein wegen ihrer Haltung eine Bedienerin sein.
- Zwei lange Textblöcke stehen oberhalb; das isolierte Wortpaar L.28 steht
  links neben dem unteren Figurenfeld. Die am Seitenrand sichtbaren Teile
  benachbarter Blätter werden dieser Seite nicht als zusätzliche Besitzer zugerechnet.

Als Badehauswart würde ich zuerst ein gemeinsames Becken mit Benutzern und
seitlichen Anschlüssen vermuten. Sichtbare Ränder motivieren den Behälter,
nackte Figuren im selben Feld die gemeinsame Anwendung. Zufluss, Ablauf,
Füllhöhe, Eintritt/Austritt und Reinigung sind dadurch **nicht** gelesen.
Zwei Reihen sind keine zeitliche Zweistufigkeit. Die dünnen rechten Striche
sind kein eindeutiger vom Wasser aufsteigender Dampf; eine Dampfhaube oder
ein erkennbarer Heizherd fehlt. Das schließt ein natürlich warmes Bad nicht aus.

### Lage des Wortes und ganzer Zielabsatz

`solkeey` beginnt die zehnte physische Zeile des zweiten Absatzes (.19).
Es steht im laufenden Textblock oberhalb des Beckens, nicht im separaten
Wortpaar L.28, nicht am Ende eines sichtbaren Strahls und ohne Textzeiger.
Nähe zur langen linken Form weist dieser Form das Wort nicht als Namen zu.

Der vollständige ZL-Absatz bleibt hier unverändert stehen; keine Zeile wird
zu einer automatisch abgeschlossenen Handlungsanweisung:

```text
10 polshy ashyteed qop okeedy otedy okshedy qoty dairam
11 yshey qokeey okeey oky ykeey qoky oky lky olchy ky dsholyd
12 qol ol chdy shedy qokedy ytedy chetedy lkedey ytedy
13 ykeshey dchsed ytedy ytedy dar ykeday qoty ykedy okal
14 dshedy ykeedy sheeky daiin okedy qokeed qokedy lchpchdy
15 qokal chedy ol sheey salshcthdy qofchedy r chedy ltary
16 lor shedy qoeedy ol chy rshdy lshedy dar chdy pchdy
17 sshkchdy chedy ol shedy qolchedy qokain ckhy dl ral
18 qokchdy chey ol cheky ol shedy qokedy qokedy chckhy qoky
19 solkeey ol shedy qokar shckhy dedy qokar qokal dol chy
20 qocthey chekal chedy qokedy lshety qoldy ltedy qotain
21 lsho qokey lshedy lshedy chedy qolky lchedal qol otar
22 qokal qol oiin cheey dal lchedy chedy salchtedytar
23 shol qetchy ykaiin olkain shedy qoky dchedy rol olcthdy
24 ytey okchedy qokal okeey qol cheedy sal teol dchdy ly
25 oshedy qotedy shol chedy y shchey ol chey qol chedy tchd oky
26 ol checholtar oiin okedy dal shey olkeol olkeedy okeol
27 dsheol oiiin olkeedy tedy cheky shckhedy chal
```

Das ist ausdrücklich nur die ZL-Basis, kein künstlicher Dreilesungs-Konsens.
Am Ziel unterscheiden sich die vollständigen anderen Zeilen:

```text
IT .19 solkeey ol shedy qokar sheckhy dcsedy qokar qokal dol chy
RF .19 solkeey ol she y qokar shckhy dedy qokas qokal dol chy
```

Unter B_CONTAINER wird nur das erste Wort zu `Becken?`; alle übrigen bleiben
genau diese offenen Wörter. Unter DAMPF wird nur dieses Wort zu `Dampf?`.
Die Quellen-/Wasservermutungen liegen im selben Absatz, aber nicht als gelesene
Relation am Ziel: .10 `otedy` ist exakt in ZL/IT, RF hat `ote y`; .17 `qokain`
ist dreifach exakt. .25 `qotedy` ist **nicht** `otedy`. .19 enthält kein `okaiin`;
auch der ganze Absatz .10–27 enthält dieses exakte Wort nicht.

Die Verdoppelungen .13 `ytedy ytedy`, .18 `qokedy qokedy`, .21 `lshedy lshedy`
bleiben in ZL/IT erhalten; RF hat einzelne abweichende Trennungen. .19 hat in
ZL/IT zweimal `qokar`, RF beim zweiten Mal `qokas`. Weder Becken noch Dampf
erklären dadurch schon eine Bedienfolge. Der vorherige Absatz .1–9 enthält
zwar eigene `okaiin`-Vorkommen; sie werden nicht als ungeschriebenes Adjektiv
über .10 hinweg an `solkeey` angehängt. Ebenso bleibt .4 ZL `chcthy` gegenüber
IT/RF `chckhy` verschieden; daraus entsteht kein gemeinsamer Eigenschaftskopf.

## f83r: getrennte örtliche Figuren und ein verbundenes Paar

- Links oben stehen drei Figuren übereinander in verschieden ausgeführten
  offenen Rand-/Schalenformen. Bei der obersten liegt eine Hand an einer
  fächerförmig aufgeweiteten Form; kurze Striche/Punkte umgeben deren Ende.
  Bei einer anderen laufen dünne Striche unter dem kleinen Gefäß nach unten.
- Unten stehen zwei weitere Figuren in offenen Randformen. Ein breiter,
  blau gebänderter Bogen verbindet ihre Zonen sichtbar. Links läuft eine blaue
  Form abwärts und endet in mehreren gekrümmten Fortsätzen mit Punktgruppen.
- Rechts führt eine weitgehend ungefärbte S-Kontur vom Figurenbehälter zu einem
  blau ausgemalten, mehrarmigen Endgebilde. Auch dort liegen gekrümmte Striche
  und Punkte. Das Bild zeigt keine Pfeile und keinen geschlossenen Rücklauf.
- Die drei oberen Figurenstationen sind nicht nachweislich mit dem unteren
  Paar verbunden. Die fünf Figuren sind weder fünf Prozessschritte noch fünf
  anatomische Teile. Der Endknoten wird nicht als Organ oder Stern benannt.

Praktisch sind Einzelanwendungen und eine gekoppelte Anwendung mit offenen
Behältern/Leitungsformen plausibel. Einzelne gestrichelte Enden lassen an
Spritzwasser, Ausfluss oder Strahlen denken. Das ist spezifischer als bloß
„etwas geschieht“, aber noch keine gesicherte Stoff- oder Richtungsbestimmung.
Die ähnlichen Endkonventionen zeigen seitwärts, abwärts und an einer Stelle
aufwärts. Sie identifizieren nicht eigens einen thermisch erzeugten, vom
Flüssigkeitsspiegel steigenden Dampf. Farbige Bänder beweisen weder Wasser
noch Feuer; ein Heizgerät, Siedevorgang oder eindeutiger Dampfweg fehlt.

### Zielposition, vollständiger Absatz und Nachbartexte

Die drei großen oberen Textblöcke begleiten die drei linken Figurenzonen;
die kürzeren unteren Blöcke nutzen die Freiräume um das verbundene Paar.
P.52–55 steht **links unten**, unterhalb des linken offenen Endsystems und
links neben/unter dem mehrarmigen Endgebilde. `solkeey` eröffnet diese vier
Zeilen. Das Wort steht nicht am oberen fächer-/sprühartigen Ende und besitzt
keinen Zeiger auf irgendein Ende. Seine Nähe zum unteren Endgebilde erlaubt
keinen automatischen Besitzer `Auslass`, `Dampf` oder `Becken`.

```text
ZL .52 solkeey qekey raly ol
ZL .53 solchkal cheol qotar ol
ZL .54 daiin ol dain chey ldalor
ZL .55 sol rtain cthal
IT .52 solkeey qekey raly ol
IT .53 solchkal cheol qotar ol
IT .54 daiin ol dain chey ldalor
IT .55 sol rtain cthol
RF .52 solkeey qekey raly ol
RF .53 solchkal cheal qotar ol
RF .54 daiin ol dain chey ldalor
RF .55 sol r tain cth l
```

B_CONTAINER liefert wörtlich `Becken? [qekey] [raly] [ol] …`; DAMPF liefert
`Dampf? [qekey] [raly] [ol] …`. Alle restlichen Wörter und Wiederholungen oben
bleiben erhalten. Der ganze Absatz enthält kein exaktes `otedy`, `qokain`
oder `okaiin`. Die früheren Kandidaten liegen in anderen Absätzen (.8, .16,
.21/.22, .39); sie schaffen keinen geschriebenen Dampf-Wasser-Zusammenhang hier.

Familie A bleibt unverändert: Die physisch nächste vorherige Form für .54
`daiin` ist .53 Schluss-`ol`; für .54 `dain` ist es das innere `ol`. Der
mögliche Kontrast ist daher `[ol] viel? … [ol] wenig?`, bei offenem `ol` und
unbewiesener Syntax, **nicht** „viel Dampf“ oder „großes Becken“. Kein Wert
darf über die dazwischenstehenden Wörter an `solkeey` zurückspringen.

Die Seite besitzt außerdem .20/.21 `solkeedy` und .41 `solkey`, jeweils
dreifach exakt: Das sind nicht zusätzliche Vorkommen von `solkeey`. Das
wiederkehrende selbständige `sol` ist kein entschlüsselter Wortbestandteil.
Die getrennten Labels .45 `chtorol`, .46 `olsaiin`, .51 `darolsy` und das
abweichende .50 ZL `sasoldal` / IT `saroldal` / RF `s roldal` werden nicht
nachträglich in P.52–55 eingebaut. P.47–49 endet eigenständig mit
`sol daiiin chedy`; auch dieser Grad wird nicht als Dampfgrad weitergereicht.

## Konkreter Vergleich und nächste Bedeutungsfrage

Der Beckenrivale benötigt keine ungesehene Dampfphase, sondern einen auf beiden
Seiten sichtbaren Behältertyp. Er benötigt weiterhin die **ungesicherte**
Annahme, dass `solkeey` diesen Typ benennt. Das Bild verteilt weder die
Wortbedeutung noch die Besitzeridentität. Im kurzen f83r-Absatz steht der
mutmaßliche Behältername nicht unmittelbar an einem Figurenbecken; im langen
f81v-Absatz ist er kein eigener Titel. Diese Kosten bleiben ausdrücklich.

Der nächste brauchbare Unterschied ist **Stoff versus Behälter**, nicht
warm/kalt oder eine neue Gradpolitur: Lässt sich eine wirklich geschriebene
Relation mit `qokain` als Wasser konsequent lesen? Unter DAMPF wäre eine
Stoffumwandlung denkbar; unter BECKEN wären Füllung/Inhalt/Anwendung andere
Relationen. Ein angenommenes „wird Wasser“ darf für den Behälter nicht
unbemerkt zu „wird **mit** Wasser **gefüllt**“ werden. Die Zusatzwörter sind
gerade der Unterschied, den das Manuskript erst tragen müsste. Auf diesen
zwei Zielabsätzen ist eine solche Relation noch nicht identifiziert.

Vor dem Rivalenvorschlag ausgeführt: `route-check` mit
`solkeey Becken Bad bath basin Dampf f81v f83r`. Relevante Treffer GDT590,
GDT261 und GDT790 primär geprüft. GDT590 warnt selbst vor Einzelwortbesitz
aus Nähe; GDT261 trägt keine universelle angrenzende Label-/Komponentenbrücke;
GDT790 liefert Panelkontext, keine neuen Einzelwortbedeutungen. Die früheren
V70-Ganzseitenrevisionen nennen bereits gemeinsame Becken bzw. gekoppelte
Stationen. Diese Bildkategorien werden hier kontrolliert, nicht als neue
Entdeckung ausgegeben; deren frei formulierte Bedienprosa wird nicht übernommen.

**Stand:** brauchbarer fester Behälterrivale und präzisere Text-/Bildgrenzen;
kein lexikalischer Sieger, kein Bildbeweis für Dampf, keine neue gesicherte
Text-Bild-Kante und keine Veröffentlichung durch diesen Teilauftrag.
