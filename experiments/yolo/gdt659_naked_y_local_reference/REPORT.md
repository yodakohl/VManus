# GDT659 — nacktes `y` ist eine bewegliche Eintragsgrenze

## Ergebnis

V36 gibt allen 270 bislang offenen, durch Leerraum getrennten `y`-Positionen
eine konkrete Kontextfunktion. Das Ergebnis ist **kein** Wortwert `y = dieser`.
Dasselbe sichtbare Zeichen eröffnet am Zeilenanfang einen Eintrag, bindet medial
einen neuen oder zugehörigen Posten an, schließt am Zeilenende eine Angabe und
fungiert auf Beschriftungszeilen als graphisches Gliederungszeichen.

Damit werden 270 Positionen in 257 Zeilen auf 125 Seiten lesbar. Acht Zeilen
werden unter den V36-Arbeitskarten oberflächenvollständig. Keine der acht ist
strikt, vor allem wegen instabiler Lesergrenzen. Die wichtigste ist f80v.21:

> Kalte Drogenfraktion I; heiß, Grad II; Ansatzrohstoff Klasse I, heiß am
> Gradanfang; **hierzu: trocken gebundene Wurzeldroge, Form I**; Rohstoff Klasse
> I, heiß am Gradanfang; Zutat, Menge III; Ansatzrohstoff Klasse I, heiß am
> Gradanfang; ein Maß kalten Ansatzes.

Die stärkere lokale Fassung `zu derselben Droge:` bleibt für diese Stelle ein
guter Rivale. `Hierzu:` ist als Default besser, weil es keinen bestimmten
Stoffantezedenten erfindet.

## Warum `y` kein gewöhnliches Ganzwort ist

Der sichere Zensus verteilt die 270 Vorkommen auf alle Zeilenpositionen:

| Position | Anzahl |
|---|---:|
| Zeilenanfang | 60 |
| medial | 167 |
| Zeilenende | 34 |
| einziges Zeichen der Zeile | 9 |

259 Vorkommen gehören zum Fließtext, elf zu Beschriftungen. Alle neun
Einzelzeichen sind Beschriftungszeilen: fünf auf f49v und vier auf f66r. Sie
als gesprochenes „dieser“ oder „Grundform“ zu übersetzen würde Inhalt erfinden;
V36 liest sie als sichtbare Beschriftungs-/Eintragsmarken.

Noch deutlicher ist die Schreibrichtung. Auf den 245 Zeilen mit genau einem
`y` zieht IT2a ein initiales `y` 28-mal nach rechts und nie nach links; RF1b
tut dies 22-mal und nie nach links. Ein finales `y` wird von IT2a zehnmal und
von RF1b neunmal nach links gezogen, nie nach rechts. Medial kommen beide
Richtungen vor. Das Zeichen sitzt daher an einer beweglichen Grenze:

```text
Zeilenanfang   y | SACHKOPF       -> Eintrag / hierzu: SACHKOPF
medial         ANGABE | y | POSTEN -> ANGABE; hierzu / neuer Posten: POSTEN
Zeilenende     ANGABE | y          -> ANGABE; Abschluss
Label          y                   -> graphische Eintragsmarke
```

Nur 83/270 nackte `y` bleiben in allen drei Transkriptionen als getrenntes
Einzelzeichen zählungsstabil. Die übrigen werden in wenigstens einer Lesung
verbunden, anders segmentiert oder nicht als dasselbe nackte Zeichen geführt.
Eine globale Wortkarte würde genau diese sichtbare Grenzfunktion verdecken.

## Die Kontextkarten

Die strukturelle Karte wird zuerst bestimmt; erst danach erzeugt der Renderer
eine lesbare deutsche Fassung. Beschriftungstoken haben Vorrang. Im Fließtext
gelten Zeilenanfang und Zeilenende direkt; medial entscheidet, ob im sicheren
ZL3b-Wortbestand eine fusionierte Schwester `y+RECHTS`, `LINKS+y`, beide oder
keine von beiden sichtbar ist.

| Strukturrolle | Anzahl | praktische Wiedergabe | Bedeutung der Wiedergabe |
|---|---:|---|---|
| `Y_LABEL_SIGLUM` | 11 | allein `[Beschriftungszeichen]`, intern Semikolon, terminal Punkt | sichtbares, sonst nicht gesprochenes Beschriftungszeichen |
| `Y_BOS_ENTRY` | 60 | `Eintrag:` | eröffnet die folgende Angabe |
| `Y_MEDIAL_RIGHT_REFERENCE` | 31 | `hierzu:` | bindet den rechten Posten an den laufenden Eintrag |
| `Y_MEDIAL_RIGHT_REFERENCE_MATERIA` | 13 | `hierzu: [Stoffkopf]` | enger Stoff-/Präparat-Untertyp; enthält f80v.21 |
| `Y_MEDIAL_LEFT_CLOSE` | 35 | Semikolon | schließt die linke Angabe |
| `Y_MEDIAL_BIDIRECTIONAL_HINGE` | 49 | `; hierzu:` | schließt links und eröffnet rechts |
| `Y_MEDIAL_UNRESOLVED_HINGE` | 38 | `hierzu:` | Default, wenn keine fusionierte Schwester entscheidet |
| `Y_EOS_CLOSE` | 33 | Punkt | schließt die vorausgehende Angabe |

Diese Karten erfüllen die gewünschte Defaultpflicht: Keine nackte `y`-Sequenz
bleibt bedeutungslos. Zugleich wird aus dem Zeichen weder ein Universalpronomen
noch ein frei kombinierbarer Lautwert.

## f80v.21: der konkrete Wurzelbezug

Die drei Lesungen zeigen die relevante Grenze direkt:

```text
ZL3b  tar kain okal y rchey qokal olor aiin okal otam
IT2a  tor kain okal yrchey qokal olor aiin okal otam
RF1b  t r kain okal y rchey qokal oloraiin okal otam
```

`rchey` ist in V35 bereits die Wurzel-/Wurzeldrogenform „trocken gebunden,
Form I“. IT2a verbindet genau `y+rchey`, während ZL3b und RF1b die Grenze
zeigen. Das entspricht GDT650s Familie `YCHOL/YCHEOL/YCHOR/YCHEOR`: 41
fusionierte Oberflächen plus zehn sichtbare `y | CH...`-Grenzen ergeben 51
lokale Realisierungen, davon 45 am Zeilenanfang. f80v.21 erweitert denselben
Eintragsbauplan vom CH-Stoffkopf auf einen R-Wurzelkopf.

Die praktische Vollfassung bleibt bewusst eine technische Liste und kein
künstlicher Satz:

> Kalte Drogenfraktion I; heiß, Grad II; Ansatzrohstoff Klasse I, heiß am
> Gradanfang; hierzu: trocken gebundene Wurzeldroge, Form I; Rohstoff Klasse I,
> heiß am Gradanfang; Zutat, Menge III; Ansatzrohstoff Klasse I, heiß am
> Gradanfang; ein Maß kalten Ansatzes.

## Die acht neu oberflächenvollständigen Zeilen

Sieben frühere Ein-Loch-Zeilen schließen durch eine `y`-Karte:

- f39v.13: terminaler Eintragsabschluss;
- f76r.13: neuer Unterposten vor heißem Rohstoff Klasse I;
- f77v.1: Gliederung zweier Labelteile;
- f78v.7: neuer Zustandsabschnitt vor dem feuchten Zustand;
- f80v.21: hierzu die trocken gebundene Wurzeldroge;
- f85r1.16: Form-/Abschnittsgrenze vor „trocken am Gradende“;
- f99r.2: Labelschluss nach der heißen Drogenfraktion.

f112r.9 enthielt zwei offene `y` und war daher zuvor keine Ein-Loch-Zeile. V36
liest das mediale Zeichen als Scharnier und das terminale als Abschluss; auch
diese Zeile ist nun oberflächenvollständig. Ihr `ol` behält jedoch den aktiven
Rivalen „Gut/Ansatz“ gegen den abstrakteren Zustands-/Materialträger und ist
daher keine durchgehend gleich konkrete Klartextzeile.

## V36-Abdeckung

Bekannte Tokenpositionen steigen von 16.743 auf 17.013, unbekannte fallen von
15.596 auf 15.326. Vollständige Mehrtokenzeilen steigen von 138 auf 146; die
strenge Untermenge bleibt bei 80, weil die neuen `y`-Grenzen gerade zwischen
den Lesern schwanken. Das Ein-Loch-Deck wächst netto von 239 auf 249: Sieben
alte `y`-Löcher schließen, während 17 vorher verdeckte nächste Restformen
sichtbar werden. Die strenge Ein-Loch-Menge steigt von 57 auf 58.

Das ist der wichtigste Durchsatzeffekt nach f80v.21: V36 liefert nicht nur
eine lokale Übersetzung, sondern legt die nächste kleine, konkrete
Bedeutungsfront frei.

## Manuelle und historische Passform

Die manuelle Auditdatei enthält 38 über Sektionen, Sprachen, Hände,
Zeilenpositionen und Leserzustände verteilte Kontexte. Jeder Eintrag bewahrt
drei konkurrierende Lesungen — Rückverweis, Eintragsgliederung und Abschluss —
sowie einen ausdrücklichen Austauschtrigger. In der 36er Kernstichprobe gewinnt
am Zeilenanfang überwiegend der Eintragskopf, am Zeilenende 8/8 der Abschluss;
medial bleibt die Funktion tatsächlich gemischt. Bei vier der 38 Auditzielen
— f50r.5, f86v3.13, f66r.62 und f116r.20 — widerspricht die manuelle Bestlesung
der mechanischen Schwesterkarte. V36 codiert diese vier Stellen nicht nach der
Stichprobe um; ihre dokumentierten Austauschtrigger bleiben ausdrücklich live.

Zeitnahe Vergleichstexte zeigen dieselbe *Architektur*, nicht dasselbe Zeichen:

- Das [Apothekerinventar John Hexhams von 1415](https://www.cambridge.org/core/services/aop-cambridge-core/content/view/59B01213AEAB60E532993FEF2521927B/S0025727300030167a.pdf/div-class-title-the-inventory-of-john-hexham-a-fifteenth-century-apothecary-div.pdf)
  setzt wiederholt *Item* vor Öl-, Wasser- und Objektköpfe.
- [Harley MS 4087, um 1445](https://searcharchives.bl.uk/catalog/040-002049924)
  verwendet *ad idem* vor einem weiteren Rezept; der Rückbezug kann dabei dem
  Zweck gelten und muss nicht „dieselbe Droge“ bedeuten.
- Der ältere Sammelcodex [Royal MS 12 G IV](https://searcharchives.bl.uk/catalog/040-002106802)
  enthält ausdrücklich 1429–1430 datierte englische Rezeptzusätze und
  kombiniert Rezepttext, Rubriken, Paraphen und graphische Randzeichen.
- Die [Lanfrank-Überlieferung um 1380/1420](https://quod.lib.umich.edu/c/cme/AHA2727/1%3A1.4?rgn=div2%3Bview%3Dfulltext)
  kombiniert Absatzzeichen mit Formeln wie „another electuary“ und „also
  take“.
- [Cappelli Online](https://www.adfontes.uzh.ch/en/ressourcen/abkuerzungen/cappelli-online/page_id/2/85)
  belegt die starke Kürzbarkeit von *item/idem/eiusdem*-Funktionen, aber keine
  Gleichung mit EVA `y`.
- Friedmans [Überblick über frühe Nomenklatoren](https://www.nsa.gov/portals/75/documents/news-features/declassified-documents/friedman-documents/reports-research/FOLDER_535/41772109081119.pdf)
  zeigt, dass um 1379/1411 Einzelzeichen, Nulls und ganze Wortkarten gemeinsam
  vorkommen konnten. Er entscheidet nicht zwischen Wort, Kürzel und Grenzmarke.

## Arbeitsgrenze und nächste Front

V36 ist eine ersetzbare Kontextübersetzung, keine behauptete Entzifferung des
Zeichens. Bereits gebundene finale `-y`-Funktionen bleiben ausschließlich in
ihren jeweils lizenzierten längeren Familien erhalten und werden nicht durch
die nackten Karten überschrieben. Historische
Analogien begründen nur den Notationstyp; sie identifizieren weder Sprache noch
Lautung.

Der nächste sinnvolle Pass beginnt bei den 17 durch V36 neu freigelegten
Ein-Loch-Zeilen. Dort müssen wieder konkrete Stoff-, Mengen-, Zustands- oder
Präparatwerte eingesetzt werden; ein Rückfall auf „Arbeitsgut“ oder „Vorgang“
ist ausgeschlossen.
