# GDT683 — der Grundansatz wird korrekt gerendert

Status: `PASS_374_BILATERAL_OL_BASE__64_MAJORITY_WITH_RIVAL__25_OVERRIDES__V57_ZERO_OL_DEBT`

## Ergebnis

Die sechs sichtbaren `ol`-Schulden waren ein Integrationsfehler: GDT664 hatte
`ol = Grundansatz` bereits im Praxis- und Stammkanal publiziert, während das
fortgeschriebene Tokenglossar den älteren Strukturtext
„Eigenschafts-/Zustands-/Materialträger“ behielt. V57 zieht die praktische
Karte an fünf Stellen ein. Auf f115r.1 wird sie bewusst nicht eingesetzt,
weil IT2a und RF1b dort `cheop ol` zu einem Pulverstoff-Compound binden.

Der Vollcensus deckt alle 463 exakten ZL3b-`ol` auf 417 Zeilen und 108 bereits
zugelassenen Seiten ab:

| Leserklasse | Stellen | GDT683-Renderer |
|---|---:|---|
| IT2a und RF1b exakt `ol` | 374 | bilateral portabel `Grundansatz` |
| nur IT2a exakt `ol` | 35 | Mehrheitsdefault plus RF1b-Rivale |
| nur RF1b exakt `ol` | 29 | Mehrheitsdefault plus IT2a-Rivale |
| kein Alternativleser exakt `ol` | 25 | lokale Boundary-/Form-/Rivalenentscheidung |

Damit erhalten 438 Stellen den Arbeitsdefault, aber nur 374 dürfen
leserübergreifend „portabel“ heißen. Bei allen 64 Mehrheitsstellen steht die
abweichende Leserform samt verfügbarer publizierter Bedeutung direkt im
Occurrence-Artefakt.

## Korrigierte Grenzkarte

Der erste Aligner konnte „Join plus Glyphwechsel“ nicht darstellen. Der neue
zeichenbasierte DP-Aligner lässt begrenzte fuzzy joins und nur verbessernde
2→2-Resegmentierungen zu. Dadurch wird f80r.23 korrekt von IT2a-only zu
bilateral verschoben. Neun weitere Stellen werden korrekt als grenzaktiv
erkannt. Endstand:

- 63/463 Positionen sind bei mindestens einem Alternativleser grenzaktiv;
- 23/25 weder-exakten Fälle sind Grenzfälle;
- nur f113v.30 (`al/al`) und f20v.11 (`cphol/cphol`) sind reine
  Einzelformkonflikte.

Die 25 lokalen Karten unterscheiden nun explizit:

- publizierte exakte Ganzwörter wie `lol`, `olchedy`, `olkeey`, `olaiin`,
  `oldal`, `olshedy`, `olain` und `olkeeody`;
- Kompositionsinferenz wie `olcheor`, `cholol`, `olchoiin` und `olkar`;
- gemeinsam erhaltene Kerne mit offenem Abschluss, etwa IT2a `olkedy` gegen
  RF1b `olke`;
- ungelöste sichtbare Komponenten, darunter das `e` in `olekar`, das Schluss-o
  in `olchedyo` und auf f112r.32 der Abschlussunterschied zwischen IT2a
  `alshedy` und RF1b `alshe | y`;
- den lokalen Aktionsrivalen `ol+y → oly = abseihen`.

Jede dieser Karten benennt Evidenztyp, Komposition, offenen Bestandteil,
Leserscope und den exakten ZL3b-Quellspan. Der 417-Zeilen-Renderer kollabiert
diesen Span genau einmal. Er schreibt daher nicht mehr gleichzeitig
„Pulverstoff-Compound“ und einen zweiten unabhängigen Stoff an dieselbe Grenze.

## Die sechs V57-Korrekturen

| Locus | Entscheidung | konkrete Lesung |
|---|---|---|
| f112r.36#2 | bilateral freies `ol` | Grundansatz |
| f115r.1#6 | gebundenes `cheopol` | bis zur Mittelstufe getrockneter Pulverstoff |
| f80r.17#8 | Mehrheitsdefault; RF1b liest `l` | Grundansatz; `Pfund/Gewichtseinheit` bleibt Rivale |
| f80v.35#9 | bilateral freies `ol` | Grundansatz im nominalen Ergebnisregister |
| f86v5.2#9 | bilateral freies `ol` | Grundansatz vor dem leserunsicheren Abkühlbefehl |
| f86v6.4#4 | bilateral freies `ol` + `aiin` | drei Teile Grundansatz |

Die Praxisprüfung entfernte zusätzlich erfundene Verben. Nominale
Zustandsfolgen werden nicht mehr zu neuen Heiz-, Kühl- oder Abschlussbefehlen.

`f115r.1`

> Die erste Blütenfraktion abmessen; getrockneten Pulverstoff nehmen und davon
> zwei Dosen bis zur Mittelstufe getrocknetes Gut abteilen. Danach: kalter
> Ansatz, auf Mittelstufe abgeschlossen; bis zur Mittelstufe getrockneter
> Pulverstoff; vollständig abgekühlt und abgeschlossen; eine Portion der
> dritten Ansatzfraktion; bis zur Mittelstufe getrockneter und fertiggestellter
> Ansatz; auf Kühlendstufe abgeschlossener Ansatz; kalt-trocken auf Mittelstufe
> abgeschlossen.

Nur die ersten drei Positionen sind Aktionen. `cheop` und `ol` erhalten im
Tokenparallel die nicht doppelte Aufteilung „bis zur Mittelstufe getrocknet“ +
„Pulverstoff“.

`f86v5.2`

> Zweite Fraktion des Drogenholzpostens: abgeschlossene Kaltzubereitung mit
> leicht angefeuchteter erster heißer Drogenfraktion, einer weiteren ersten
> heißen Drogenfraktion und Blüten- oder Fruchtstand. Getrockneten Pulverstoff
> nehmen; Rohdroge I, kalt auf Anfangsstufe, im Grundansatz. Hiervon den Drogenstoff
> abkühlen, wobei die Befehlsform leserunsicher ist. Zweimal je ein Maß kalten
> Ansatzes.

Die Warnung gehört an `ytol`: IT2a liest `ytal`, RF1b `yt|l`. `ol` selbst ist
an dieser Stelle bilateral exakt.

## Wiederholtes `ol ol`

Sieben Zeilen enthalten benachbarte `ol ol`. GDT683 erfindet daraus weder ein
zweites Lexem noch eine Maßeinheit. Der Literalrenderer bleibt
`Grundansatz | Grundansatz`; sechs Kontexte bleiben zwei getrennte nominale
Grundansatz-Einträge. Nur f81r.5 besitzt mit einleitendem `qol` einen
lizenzierten Aktionsscope und liest das Paar als Grundansatz in zwei Zugaben.

## Rechnerische Änderung

| Größe | V56 | V57 |
|---|---:|---:|
| Leserzeilen | 51 | 51 |
| Tokenstellen | 479 | 479 |
| unbekannte Stellen | 0 | 0 |
| Aktionsstellen | 86 | 86 |
| generische OL-Metaglosse | 6 | 0 |
| Praxiszeilen mit `Ansatz/Gut` | 2 | 0 |

Der unabhängige Validator baut neun Resultatdateien bytegleich neu und besteht
die im Validation-Artefakt ausgewiesenen Einzelprüfungen. Die Guard-Abfrage
selektiert genau 417 Loci, verwirft 98
f84-Zeilen vor der Materialisierung und öffnet keine neue Seite.

## Nächster konkrete Schuldposten

GDT683 schließt nur die OL-Familie. Zwei unmittelbar sichtbare Fremdschulden
bleiben absichtlich stehen: auf f111v.18 trägt ein freies `l` noch denselben
alten Materialträgertext; auf f80v.35 ist `tol` weiterhin nur „Kaltes Gut“.
GDT684 muss deshalb den gesamten V57-Reader nach solchen strukturellen oder
generischen Tokenwerten durchsuchen und sie nach Häufigkeit, Aktionsnähe und
praktischem Informationsverlust ordnen.

## Claim ceiling

`Grundansatz` ist eine konkrete, ersetzbare Arbeitskarte mit 374 bilateral
exakten Wortgrenzen, kein bestätigtes deutsches Wort. Die 64 Mehrheitsstellen
sind ausdrücklich nicht vollständig portabel. GDT683 bestätigt weder Sprache
noch Lautwert, Pflanze, Krankheit, Trägerflüssigkeit oder historisches
Codebuch.
