# V65 R1 — Biological-Zweitausgabe des Werkstattlehrmeisters

Status: vollständige kreative Quellenedition, **keine Entzifferung**. Geltung
nur für `f81v`, `f82r`, `f83r`.

## Entscheidung

Die sechs Records lassen sich am sparsamsten als bebilderte Arbeitszettel für
therapeutische Bäder, Waschungen und Irrigationen lesen, wenn daneben ein
vollständig ausführbarer Apparate-Rivale stehen bleibt. Die Karten liefern
nicht die Sachnomen. Das feste V60-Deck bleibt unverändert; V65 füllt
`OWNER`, `ACTIVE`, `TARGET` und `PREVIOUS` nur mit markierten, recordlokalen
Exemplaren.

```text
sichtbar und lizenziert:
  exact joint tuple / formaler Prompt / Feldschluss
  → V61-Aussage über physische Zeilen
  → V62-Registertransition
  → V63 UNIQUE | AMBIGUOUS | UNPARSED

nur Exemplar:
  → medizinische konkrete Füllung
  → apparative konkrete Rivalfüllung
```

Damit bleibt keine sichtbare Einheit in der Vollausgabe ohne lokale
Defaultlesung. Bei 191/281 unparsed Ereignissen ist diese Lesung ausdrücklich
`EXEMPLAR_ONLY_COMPLETE`, nicht nachträglich erfundene Kartenbedeutung.

## Vollständigkeit

| Record | Seite | Felder | Events | V61-Aussagen | V63 Aussage U/A/X | Prozess |
|---|---|---:|---:|---:|---:|---|
| B1 | f81v | 24 | 66 | 21 | 4/8/9 | Grundansatz → Temperieren → Nachspülen → Klären/Übergabe |
| B2 | f82r | 26 | 62 | 22 | 1/6/15 | Station vorbereiten → erste Anwendung → Ablassen → zweiter Gang → Varianten |
| B3 | f83r | 38 | 86 | 34 | 6/12/16 | Absetzen → warmer Gang → Schalten → Stationswechsel → Nachgang → Schluss |
| B4 | f83r | 20 | 47 | 16 | 1/7/8 | warmer Nachgang → Filtern → Reinigen/Ablassen → Neuansatz |
| B5 | f83r | 5 | 11 | 3 | 0/1/2 | Abziehen → Erwärmen → Halten/Übergeben |
| B6 | f83r | 2 | 9 | 1 | 0/1/0 | kalter offener Filtergang |
| **Summe** | **3 Seiten** | **115** | **281** | **97** | **12/35/50** | **103 ausführbare Graphkanten** |

Auf Ereignisebene erkennt V63 56 exakte, 29 nur formale und 5 konvergente
Positionen; 191 bleiben exemplarisch. Auf Feldebene sind 14 `UNIQUE`, 41
`AMBIGUOUS`, 60 `UNPARSED`. Die 61 biologischen Vorkommen der elf V60-Karten
sind bytegleich übernommen. Das Wörterbuchdelta hat null Zeilen.

## Die sechs Zweitfassungen

### B1 — gemeinsames Grundbad

Prozessgraph: `START → REINIGEN → GRUNDANSATZ → TEMPERIEREN → NACHSPÜLEN →
KLÄREN/ÜBERGEBEN → END`.

Medizinischer Default: Einen Kräuterzusatz im gemeinsamen Grundbad dosieren,
mit dem recordlokal vorigen Posten verbinden, mischen, temperieren, die
Badestelle spülen, absetzen, klären und die fertige Portion an die erste
Behandlungsstelle geben. Apparativ: dieselben 21 Klauseln als Beschickungs-,
Spül-, Absetz- und Übergabegang einer Mischbeckenanlage. Der Lehrling setzt
`B1:O01` einmal, führt S001–S021 in fünf Phasen aus und lässt F044 offen.

Revision gegen V54: Der pauschale „Grundkreislauf“ wird in 21 Aussagen und
fünf Registerphasen zerlegt; kein geschlossener Rücklauf wird behauptet.
Stärkster Widerspruch: 43/66 Ereignisse sind unparsed, und Öl, Becken,
Badestelle und Rücklauf kommen nur aus dem Exemplar.

### B2 — einzelne Bad-/Anwendungsstation

Prozessgraph: `START → STATION VORBEREITEN → ERSTE ANWENDUNG →
KLÄREN/ABLASSEN → ZWEITER GANG → GEBRAUCHSVARIANTEN → END`.

Medizinischer Default: Eine temperierte Badportion durch mehrere Zugänge und
ein Tuch führen, anwenden, klären, ablassen und nachfüllen; Trank, Auflage und
Bad am Schluss als getrennte lokale Varianten buchen. Apparativ: eine
Prüfcharge durch Kammern, Filter, Anschlüsse und Auffangbehälter führen.
`B2-S005` trägt f82r.3→f82r.4 als **dieselbe Klausel**; die wiederholte sichtbare
Karte ist Carry-Evidenz, keine neue Bedeutung. S010→S011 bleibt die einzige
`UNRESOLVED` Graphkante und muss mit beiden Lesepfaden abgeschrieben werden.

Revision gegen V54: Carry und ungelöste Grenze sind nun ausführbar; die vier
Schlussgebräuche sind keine codierten Diagnosen. Stärkster Widerspruch:
Körperziel, Trank, Auflage und Tuch sind ersetzbare Exemplarannahmen, während
viele Bildlabels nur in der Nähe von Figuren oder Formen liegen.

### B3 — langer Irrigations-/Mehrstationszyklus

Prozessgraph: `START → ABSETZEN/ABLASSEN → WARMER ANWENDUNGSGANG →
SPÜLEN/SCHALTEN → STATIONSWECHSEL → LOKALE NACHANWENDUNG → SCHLUSSGANG →
END`.

Medizinischer Default: Eine Bad- oder Irrigationsflüssigkeit absetzen,
temperieren, mischen, am markierten Ziel anwenden, ablassen und die Folge mit
wechselnden Öffnungen, Portionen und Zustandsprüfungen wiederholen. Apparativ:
ein mehrstufiger Becken-, Filter-, Ventil- und Ablaufbetrieb. Der Lehrling
führt alle 34 Aussagen aus, beachtet drei `RESUME_ACTIVE_ITEM`-Kanten und
setzt bei neuen Zellen Zielslots nach dem V62-Log zurück.

Revision gegen V54: Der lange Zyklus hat nun sechs Phasen und explizite
Registerwechsel; „Kreislauf“ ist nicht mehr still vorausgesetzt. Stärkster
Widerspruch: 57/86 Ereignisse sind unparsed, und zwei sichere Auslasslabels
ohne lokale Figur stützen den rein apparativen Rivalen.

### B4 — warmer Nachgang und Filterung

Prozessgraph: `START → WARMER NACHGANG → FILTERN/SPÜLEN →
REINIGEN/ABLASSEN → NEUANSETZEN/NACHFÜLLEN → END`.

Medizinischer Default: Eine warme Teilportion auswählen, temperieren, als
Waschung oder Auflage verwenden, durch Tuch filtern, Gefäß und unteren Lauf
reinigen, ablassen und frisch nachfüllen. Apparativ: warme Reinigungscharge,
Filtertuch, Nebenlauf und Ablauf. In S003 wird die lizenzierte Folge
`ANTEIL? → TEMPERIEREN? → ANWENDEN?` ausgeführt; Anteil, Flüssigkeit,
Körperstelle und Tuch bleiben dennoch Exemplarfüllungen.

Revision gegen V54: Anwendung, Reinigung und Neuansatz liegen jetzt auf
getrennten START-/Parallelphasen. Stärkster Widerspruch: 32/47 Ereignisse sind
unparsed; „Auflegen“ benötigt einen Körper, obwohl der Bildowner ebenso gut
eine Station sein kann.

### B5 — Wärme- und Übergabenachtrag

Prozessgraph: `START → ABZIEHEN → ERWÄRMEN → HALTEN/ÜBERGEBEN → END`.

Medizinischer Default: Die lokale Restportion abziehen, einmal erwärmen, für
die Frist halten, mit einem **recordintern** vorigen Posten bemessen und zur
nächsten Behandlungsstation geben. Apparativ: derselbe Dreischritt als
Restchargenübergabe. S003 vereinigt F131–F133 über drei loci; der Lehrling darf
dafür niemals ein B4-Register übernehmen.

Revision gegen V54: Aus fünf Feldern werden drei Aussagen, deren letzte drei
Felder trägt. Stärkster Widerspruch: 7/11 Ereignisse und drei offene Felder
lassen Frist, Wärme und Übergabe weitgehend exemplarisch.

### B6 — kalter offener Filtergang

Prozessgraph: `START → KALTER FILTERGANG → END`.

Medizinischer Default: Eine ungekochte, bemessene Waschportion durch Tuch an
die bezeichnete Stelle führen. Apparativ: eine kalte Vorlaufcharge durch den
Filter zum Zielanschluss führen. F134–F135 sind genau eine V61-Aussage; alle
vier Register werden am B6-Anfang neu gesetzt und vor dem nächsten Record
zurückgesetzt.

Revision gegen V54: Der Zweifeldgang ist jetzt eine einzige fortgesetzte
Klausel ohne B5-Carry. Stärkster Widerspruch: 6/9 Ereignisse und beide offenen
Felder sind unparsed; Person, Kochen, Tuch und Ziel sind reine
Exemplarergänzungen.

## Lehrlingsregel

1. Den Bild-/Recordowner einmal als anonyme `B*:O01`-ID setzen.
2. Nicht nach Zeilen, sondern nach der V61-Aussagefolge lesen; interne Carries
   auf demselben Klauselzettel fortführen.
3. Sichtbare V60-Karten und formale Prompts nur mit ihren festgelegten kurzen
   Werten ausführen. Oberfläche, Komponenten und PAGE_HOST bleiben stumm.
4. `OWNER`, `ACTIVE`, `TARGET`, `PREVIOUS` genau nach dem V62-Transitionlog
   tragen, ersetzen oder wiederaufnehmen; an jeder Recordgrenze zurücksetzen.
5. V63-Status laut ansagen: `UNIQUE` ausführen, `AMBIGUOUS` mit Rivalen buchen,
   `UNPARSED` als opake Identität kopieren.
6. Erst danach entweder die markierte medizinische oder die markierte
   apparative Exemplarspalte einsetzen. Kein Exemplarwort ins Wörterbuch
   zurückschreiben.
7. `CLOSE` nur als Feldcommit ausführen und nie als Satzwort lesen; offene
   Recordenden offen lassen.

## Gesamtwiderspruch und Urteil

Die Ausgabe ist vollständig ausführbar, aber semantisch stark
exemplarabhängig: nur 90/281 Ereignisse haben einen lizenzierten exakten oder
formalen Parserpfad. Frauen, Körperteile, Krankheiten, Wasser, Tuch, Becken,
Leitung und Gefäß sind nirgends Kartenwerte. Die stärkste nichtmedizinische
Gesamtlesung ist deshalb ein illustriertes Badehaus-/Wasserwerk-Musterbuch mit
Chargen-, Filter-, Spül- und Übergabegängen. Die Figuren und lokalen
Anwendungsvarianten halten therapeutische Balneologie als bevorzugten
Exemplarinhalt knapp vor diesem Rivalen; die formale Maschine entscheidet die
Domäne nicht.

## Artefakte und Validierung

- `V65_R1_281_EVENT_INTERLINEAR.tsv`: 281/281 Ereignisse, beide Exemplarspuren.
- `V65_R1_115_FIELD_EDITION.tsv`: 115/115 Felder.
- `V65_R1_97_STATEMENT_EDITION.tsv`: alle 97 Bio-Aussagen aus V61.
- `V65_R1_6_RECORD_EDITION.tsv`: sechs vollständige deutsche Recordtexte und
  Apparaterivalen.
- `V65_R1_PROCESS_GRAPH_EDGES.tsv`: 103 ausführbare Kanten einschließlich
  sechs Recordabschlüssen.
- `V65_R1_V60_DECK_FREEZE.tsv` und `V65_R1_DICTIONARY_DELTA.tsv`: elf Werte
  unverändert, null Änderungen.
- `V65_R1_BUILDER.py`, `V65_R1_VALIDATOR.py`, `V65_R1_VALIDATION.json`:
  reproduzierbarer Build und `PASS` für 3 Seiten / 6 Records / 115 Felder /
  281 Ereignisse / 97 Aussagen.
