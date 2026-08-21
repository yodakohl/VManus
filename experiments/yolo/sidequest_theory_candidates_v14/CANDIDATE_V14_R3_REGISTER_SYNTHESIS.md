# V14 R3 — Technischer Register- und Notationsschreiber

Datum: 2026-08-21

Status: unabhängiger explorativer Sidequest-Kandidat; keine Übersetzung und
kein GDT-Ergebnis. Perspektive R3: technischer Register-, Rechen- und
Notationsschreiber um 1420. Die V14-Berichte der anderen Rollen wurden nicht
gelesen. `f84` und `f84r` blieben versiegelt.

## Entscheidung

**Gewinner: iatromedizinischer WHAT/HOW/WHEN-Verbund in einer generischen
Karten- und Registermaschine.**

Das generische indexierte Formular ist sehr wahrscheinlich die
**Produktionstechnik**, aber nicht die vollständigste Zweckbeschreibung. Die
sparsamste konkrete Gesamtlesung der zehn Seiten ist:

```text
WHAT  Herbal:  Welcher bildadressierte Simple/Träger, welche Eigenschaften?
HOW   Bio:     Welche Zubereitung, Einstellung, Anwendung oder Prozesslage?
WHEN  Astro:   Welche Zeit-, Himmels- oder prognostische Konfiguration gilt?
```

`WHEN` bedeutet dabei nicht, dass jeder Bio-Record auf einen bestimmten Stern
verweist. Die drei Astro-Seiten bilden eine getrennte Nachschlageabteilung mit
eigenen lokalen Namensräumen. Ein Benutzer kann sie bei Bedarf konsultieren,
wie man eine Kalendertafel neben einem Rezeptbuch konsultiert. Diese lockere
Kopplung erklärt zugleich, warum kein formaler prose-to-diagram pointer
nachgewiesen ist.

Arbeitskonfidenzen:

| Aussage | Konfidenz |
|---|---:|
| gemeinsame Karten-/Registermaschine | .84 |
| Herbal = offene Simple-/Materia-medica-Dossiers | .72 |
| Bio = gebundene praktische HOW-Konfigurationen | .66 |
| Astro = konsultierbare WHEN/CONDITION-Instrumente | .61 |
| alle drei als iatromedizinischer WHAT/HOW/WHEN-Verbund | .57 |
| ein Eintrag-zu-Eintrag-Konkordanzschlüssel zwischen den Registern | .19 |

Der stärkste Rivale ist ein **generisches illustriertes
Werkstatt-Formular-/Exemplarbuch** mit Konfidenz `.51`: Pflanzen, Figuren und
Kreise geben nur verschiedene Übungs- oder Sachklassen vor; die Kartenmaschine
füllt sie ohne einheitlichen medizinischen Zweck. Dieser Rivale erklärt die
interne Notation beinahe gleich gut, aber weniger gut, warum gerade
bildadressierte Simple, menschliche Bad-/Gefäßszenen und astronomische
Auswahlinstrumente in einem aufwendig erhaltenen Buch zusammenstehen.

## Die ausführbare Architektur

Die Maschine trennt fünf Ebenen, die ein Schreiber praktisch auseinanderhalten
kann:

```text
QUELLINHALT
  Simple-Artikel | Anwendungs-/Prozessanweisung | Kalender-/Prognosewissen
        ↓
BILD- UND REGISTERELLIPSE
  Bild, Seitenart und Routine liefern ausgelassene Argumente
        ↓
LOGISCHE BUCHUNG
  ADDRESS + ITEM + RELATION + REFERENCE + VALUE + optional COMMIT
        ↓
EXAKTE KARTENWAHL
  gemeinsame Lehrkarten + Registerdeck + seltene Exemplar-/Seitenkarte
        ↓
RENDERER
  Hand/Register wählt Wrapper, Verbindung, Abstand, Zeilenanpassung und Schluss
```

Der Encoder speichert also nicht notwendig jedes Quellwort. Er speichert eine
ausreichende Werkstattbuchung. Der Decoder rekonstruiert zuerst die Buchung und
ergänzt erst danach aus Bild und Register plausible Quellwörter. Das erklärt,
warum exakte Kartenidentität mehr trägt als naive EVA-Wörter: sichtbare
`AIIN/DAIIN/SAIIN/CHAIIN/TAIIN`, freie `Y/DY/CHY/SHY/SY/CHEY` und
`CHOL/OL/QOL/SOL/TOL/CHEOL` können verschiedene Renderer derselben ganzen
Karte sein. Wrapper sind Einpassungs- und Übergangsentscheidungen; sie sind
keine stabilen übersetzten Präfixe.

### Zustandsregister des Schreibers

Ein Schreiber braucht nur fünf kleine Gedächtnisplätze:

```text
R = aktueller Seitentyp: HERBAL_OPEN | BIO_COMMITTED | ASTRO_ARRAY
H = durch Bild, Record oder letzten Commit aktiver Hauptbezug
S = aktueller Slot/Eintrag
E = offene Relation über Feld- oder Zeilengrenze
V = zuletzt gesetzter Standard/Referenzwert
```

Schreibalgorithmus:

1. Wähle `R` aus dem vorgezeichneten Seitentyp.
2. Setze `H` durch das Bild oder den laufenden Record; schreibe dieses Argument
   gewöhnlich nicht aus.
3. Kodiert die Quelle einen neuen Eintrag, setze qokaiin oder eine andere
   zugelassene Kopfkarte und aktiviere `S`.
4. Schreibe Inhalt als exakte gemeinsame oder registerlokale Karten. Bei L/O
   hänge den nächsten Block unter den aktiven Bezug; fehlt ein Endpunkt, nimm
   ihn aus `H`, `S` oder `E`.
5. Bei `FORMULA_F3` setze zwei markierte Einträge unter dieselbe aktive
   Referenz `V`, ohne zu behaupten, dass `V` eine Menge ist.
6. In Bio setze die exakte kategoriale Wertkarte und befestige den
   DY/B3-Schluss: die Zelle ist committed. In Herbal darf das Feld offen
   weiterlaufen. In Astro übernimmt der gezeichnete Locus die Adresse; die
   beigeschriebene Karte ist sein lokaler Name oder Wert.
7. Übergib die logische Kartenfolge an den Hand-/Registerrenderer. Dieser
   wählt unter lizenzierten Realisierungen Wrapper, JOIN/SPACE, `s` am
   Zeilenanfang und `q` nach einem DY-Schluss und passt den Text an den noch
   freien Bildraum an.

Rücklesealgorithmus:

```text
sichtbare Gruppe
  → Wrapper/Schluss vom exakten Kartenträger trennen
  → aktive Bild-/Recordadresse H rekonstruieren
  → qokaiin, L/O, F3 und COMMIT als Buchungshandlungen ausführen
  → exakte lokale Werte unverändert bewahren
  → erst zuletzt registergerechte Quellklasse paraphrasieren
```

Unbekannte Karten dürfen in diesem Verfahren unbekannt bleiben. Das ist keine
Verlegenheit, sondern dieselbe Operation wie das korrekte Kopieren eines
Arzneinamens oder Tabellenwerts, dessen Expansion ein Lehrling nicht kennt.

## Registerprogramme

### Herbal A: offener Artikelmodus

Die Pflanze wird zuerst gezeichnet; die Schrift fließt anschließend durch den
verfügbaren Raum. Deshalb sind Stamm-Unterbrechung, Zeilenende und physisches
Feld keine zuverlässigen Satz- oder Bedeutungsschlüsse. Das Bild setzt `H =
CURRENT_SIMPLE`; der Text kann Name/Synonym, Kennzeichen, Qualität, Standort,
Teil, Vorbereitung oder Gebrauch liefern. Der große lokale lexikalische
Schwanz ist gerade zu erwarten: Pflanzennamen und spezifische Eigenschaften
werden aus dem Exemplar kopiert, während nur wenige Relations- und
Registerkarten portabel sind. Die geringe Schließungsrate lässt fortlaufende
abgekürzte Fachprosa zu.

`f55v` ist der Übergangsmodus: noch bildadressiertes Herbal, aber bereits
Currier-B-nahe Produktion und mehrere geschlossene Felder. Er ist keine eigene
Sprache, sondern die Brücke vom offenen Dossier zur gebundenen Buchung.

### Biological B: committed HOW-Zellen

Figuren, Becken, Gefäße, Leitungen und Stationen setzen `H` und oft auch den
geometrischen Operand. Der Text zerlegt die Quelle in kurze Zellen:

```text
BIO_CELL := ADDRESS/ITEM?
            + QUALIFIER/RELATION/REFERENCE*
            + EXACT_VALUE_CARD
            + COMMIT(DY oder B3)
```

Die 90 Terminalereignisse sind nicht bloße Punkte. Bei den führenden vier
Familien tragen 12/10/8/8 Ereignisse denselben Schlussmechanismus, aber vier
verschiedene exakte Payload-Identitäten. Sechzehn Ein-Karten-Felder sind daher
vollständige geerbte Slotwerte: „für die aus Bild/Formular bekannte Frage gilt
Wert X; bestätigt“. Dass die Wertfamilien zwischen Feldordnungen und
Feldlängen wandern, spricht gegen vier feste Spalten und für
slot-konditionierte kategoriale Antworten.

### Astro: Bildadresse als Bus

Die Kreisblätter besitzen keine GDT327-Prosekarten. Ihre Einträge dürfen daher
nicht mit Herbal-/Bio-Karten gleichgesetzt werden. Hier ist die Zeichnung
selbst der Adressbus:

```text
ASTRO_ENTRY := GEOMETRIC_LOCUS + LOCAL_LABEL_OR_VALUE
```

Die gemeinsame Maschine besteht nur darin, dass exakte sichtbare Identität
unter einer vom Layout gelieferten Adresse bewahrt wird. Der Inhalt und die
Reihenfolgeregel sind seitenlokal.

## Die tragenden Karten und Formeln

### qokaiin

```text
qokaiin := ACTIVATE/NEXT ITEM OR SLOT
```

Sieben von neun Belegen stehen am Feldanfang; alle neun rechten Nachbarn sind
verschieden. Das passt zu einer Adresse, die variable Inhalte eröffnet. Der
mediale Beleg ist ein Untereintrag; der feldfinale und am nächsten Zeilenanfang
wiederholte f82r-Beleg ist am besten als anticipatory carry plus Wiederaufnahme
zu lesen. Quellnah darf qokaiin „Item“, „als Nächstes“, „nimm/setze den nächsten
Eintrag“ heißen. `WATER` oder ein bestimmtes Medium erklärt diese
Positionsökologie schlechter.

Formale Konfidenz ADDRESS/ACTIVATE `.78`; Quellklasse ITEM/NEXT `.64`;
konkretes TAKE/APPLY `.43`.

### L/O

```text
L/O := CONTINUE_UNDER_ACTIVE_RELATION
     ≈ mit/dazu/ebenso unter demselben Bezug
```

`A–L/O–B` bucht B unter A bzw. H. `A–L/O–B–L/O–C` setzt denselben
Beziehungsrahmen fort. Feldinitiales oder alleinstehendes L/O erbt den linken
Bezug; feldfinales L/O speichert eine offene Kante; `L/O–COMMIT` schließt die
Zelle unter dem geerbten Bezug. Eine Regel erklärt damit 14 mediale, drei
initiale, einen alleinstehenden und einen finalen Beleg. Im Herbal kann die
Quelloberfläche „mit/und dazu“ lauten, im Bio „unter derselben Einstellung“.

Formale Konfidenz `.76`; WITH/ALSO/LIKEWISE `.61`; spezifische medizinische
Relation `.34`.

### `FORMULA_F3 = Y–AIIN–Y`

F3 ist eine gelehrte, rendererunabhängige Ganzkartenformel. Ihre beste
Arbeitsausführung lautet:

```text
F3 := BIND(Y_left, ACTIVE_REFERENCE V)
      BIND(Y_right, ACTIVE_REFERENCE V)
```

Auf f10r steht sie als `Y–Y–AIIN–Y` am Ende eines offenen Herbal-Feldes; auf
f83r als `Y–AIIN–Y–LCHE[COMMIT]` am Kopf einer Bio-Zelle. Das genügt für
„zwei Markierungen unter derselben aktiven Referenz“, nicht für „gleiche
Menge“ oder *ana*. Ein Schreiber kopiert F3 als einen Formelsatz und rendert
die drei Karten passend zur Zelle.

Konfidenz gelernte Formel `.86`; shared active reference `.48`; gewöhnliche
formelhafte Fachprosa `.42`; dyadischer Indexrahmen `.36`; gleiche Menge `.18`.

## Kontinuierliche Rücklesungen

Die folgenden Texte sind Quellklassen, keine plaintext translations. `P`
bezeichnet bild-/registergegeben, `F` formale Buchung und `S` spekulative
Inhaltsexpansion.

### Vollständiger Herbal-Absatz: f10r, Record 2

Oberflächen-Audit:

```text
f10r.6  ycheor cthy chor cthaiin qoctholy dy chy taiin shy
f10r.8  qotchor chor otol chol cholor chol daiin dar
f10r.9  oykchor shor chor chy kaiiin dy chodaiin
```

Kontinuierliche Rücklesung:

> `[P]` Zum abgebildeten Simple läuft der zweite Artikelabschnitt weiter.
> `[S]` Verzeichne sein unterscheidendes Merkmal oder seine Qualität und den
> dazugehörigen Teil/Umstand. `[F]` Setze zwei markierte Angaben unter den
> aktuell geltenden Standard (F3). `[F]` Führe auf der nächsten physischen
> Zeile mehrere Einträge mit L/O unter demselben Bezug fort; der dort genannte
> Standard bleibt aktiv. `[S]` Ergänze zuletzt eine weitere spezifische
> Eigenschaft, Herkunfts-, Zubereitungs- oder Gebrauchsangabe. Der Absatz bleibt
> bis zum dritten Zeilenstück offen; keines der drei Zeilenenden ist ein
> lokaler COMMIT.

Der konkrete Inhaltskandidat lautet: **Eigenschaft plus Zubereitung/Gebrauch
des abgebildeten Simples**. Ein bestimmter Pflanzenteil oder Stoff ist nicht
eingesetzt.

### Vollständiger Biological-Record: f82r.27

```text
pchedy{DY} | rsheal daldy{DY} | qokeedy{DY} | rshedy{DY} |
qoteedy{DY} | qokeedy{DY} | lochedy{DY}

Zelllängen:       1 | 2 | 1 | 1 | 1 | 1 | 1
anonyme Werte:    A | B+b | C | D | E | C | F
```

Kontinuierliche Rücklesung:

> `[P]` Für die dargestellte Station/Anwendung gilt der geerbte HOW-Record.
> `[F]` Setze und bestätige Wert A. Trage im zweiten Slot die Qualifikation B
> mit Wert b ein und bestätige sie. Setze danach die vollständigen geerbten
> Slotwerte C, D, E, nochmals exakt C und schließlich F; bestätige jede Zelle.
> `[S]` Die Werte können etwa Zubereitungszustand, Medium, Prozessstufe,
> Applikationsart, Stärke oder Dauer sein. Die Wiederholung von C in Zelle 3
> und 6 bedeutet denselben formalen Wert, nicht notwendig dieselbe sichtbare
> Handlung.

Das ist eine echte vollständige Rücklesung ohne erfundene sieben
Slotüberschriften: Die Überschriften kommen aus Bild und Stencil, die exakten
Antworten bleiben erhalten.

### f67r2 als Ganzdiagramm

> `[P/F]` Aktiviere die zentrale Regel oder den zentralen Bezug. Wähle einen
> Eintrag aus dem Siebener-Inventar; ordne ihn in den passenden Abschnitt des
> Zwölfer-Inventars ein; lies dort die lokale Begleitangabe. Die sieben, zwölf
> und die Mitte sind getrennte Adressklassen und keine fortlaufende Prosa.
> `[S]` Als WHEN-Lesung können sieben Himmelskörper/Gouverneure gegen zwölf
> Monate, Zeichen oder Zustandsklassen abgefragt werden.

Die konkrete Sieben-gegen-Zwölf-Deutung ist plausibel (`.52`), aber die Seite
liefert keinen externen Namen und keine bewiesene Zuordnungsrichtung.

### f68r1 als Ganzdiagramm

> `[P/F]` Setze das zentrale Objekt als gemeinsamen Bezug. Lies die 28
> nichtzentralen beschrifteten Sterne als räumlich adressierte Katalogeinträge;
> jeder Stern besitzt einen lokalen Namen/Wert. Benutze Nähe, Sektor oder
> gezeichnete Gruppe, nicht eine erfundene zyklische Reihenfolge. `[S]` Dies
> kann ein Stern-, Phasen-, Tages- oder Prognosekatalog sein, dessen Mitte den
> Bezugszustand vorgibt.

`1+28` ist stark; ein autorischer Start und eine feste Umlaufrichtung sind
nicht sichtbar. Diese Seite ist daher ein räumlicher Katalog, nicht dieselbe
Liste wie f69v.

### f69v als Ganzdiagramm

> `[P/F]` Durchlaufe 28 radiale Loci in der im Exemplar festgelegten Folge und
> lies an jedem Locus seinen lokalen Eintrag. Die abwechselnd langen und kurzen
> Radien markieren zwei Präsentationsklassen A/B. `[S]` Als WHEN-Instrument
> kann dies ein 28-teiliges Mond-/Prognoseschema mit alternierenden
> Unterklassen sein.

Die Rücklesung bleibt unter Rotation und Spiegelung invariant, denn auf der
Seite ist kein sicherer Start und keine Richtung autorisiert. `28 +
Alternation` identifiziert allein weder Mondstationen noch eine Kultur; eine
unabhängige mittelalterliche 28er-Gegenparallele zeigt, dass Alternation nur
eine allgemeine Ordnungsressource sein kann.

## Konkrete Inhaltswetten

| Rang | Wette | Konfidenz | Abgleich mit allen zehn Seiten |
|---:|---|---:|---|
| 1 | Bio-Wertkarten kodieren **Zustand/Prozessstufe oder Anwendungsmodus** | .58 | erklärt kurze committed Zellen und mobile 12/10/8/8-Werte; bleibt mit Gefäß-, Bad- und Figurenbildern vereinbar |
| 2 | Herbal-Artikel enthalten **Eigenschaft plus Zubereitung/Gebrauch eines Simples** | .55 | erklärt offene lokale Prosa und Bildadresse; zwingt keine Bildnähe zu Blatt/Root-Semantik |
| 3 | Astro liefert **Zeit-/Prognosekategorien für praktische Entscheidungen** | .53 | erklärt 7/12 und beide 28er-Instrumente, ohne gemeinsame Liste oder Direktpointer zu erfinden |
| 4 | eine Bio-Slotklasse ist **Medium/Bad** | .43 | ikonographisch attraktiv und mit L/O-Relationen vereinbar; kann die wiederkehrenden Werte noch nicht an sichtbare Flüssigkeit binden |
| 5 | eine Bio-Slotklasse ist **Dauer/Stärke/Grad** | .39 | passt zu kategorialen Werten und aktiver Referenz, aber AIIN ist zu mobil für eine exklusive Mengenkarte |
| 6 | qokaiin wird im Bio-Kontext manchmal als **Nimm/setze den nächsten Schritt** expandiert | .43 | funktional gut, doch ADDRESS/ITEM muss auch den Catchword- und medialen Fall tragen |

Diese Wetten dürfen weiterleben, bis ein fester Seitenbefund sie unmöglich
macht oder eine einfachere Expansion mehr Fälle erklärt.

## Bild-vor-Text und mehrere Hände

Die Bild-vor-Text-Reihenfolge ist kein Nebendetail, sondern Teil des Encoders.
Der Zeichner stellt die Adressfläche bereit. Der Schreiber berechnet daraus
nicht Bedeutung, sondern verfügbaren Schreibraum und ausgelassene Argumente:

- Herbal-Zeilen werden um Pflanzenkörper reflowed; der Pflanzenkörper setzt
  den Dossierkopf, aber eine nahe Karte ist nicht automatisch LEAF oder ROOT.
- Bio-Zeilen und Zellen füllen die freien Flächen über oder zwischen
  Gefäß-/Figurenstationen; geometrische Nähe darf nur einen Recordrahmen, nicht
  einen einzelnen Wortreferenten liefern.
- Astro-Labels werden an fertige Loci gesetzt; dort ist Lage tatsächlich die
  Adresse, aber der lokale Labelinhalt bleibt unbekannt.

Auf den sieben Prosaseiten schreiben Hand 1 (`f10r`, `f11r`, `f56r`) und Hand
2 (`f55v`, `f81v`, `f82r`, `f83r`). Manuskriptweit überspannen 6.906 von 8.448
GDT327-Ereignissen Hände, während eine kleine gemeinsame Deckmitte neben einem
großen registerlokalen Schwanz steht. Das passt zu einem Lehrsystem:

```text
MEISTERBLATT       häufige exakte Karten und Formeln (qokaiin, L/O, F3)
REGISTERBLATT      Herbal-open, Bio-commit oder Astro-array
WERTKARTENDECK     registerlokale exakte Kategorien
SEITENEXEMPLAR     seltene Namen, Werte und Sonderformen
HANDRENDERER       zugelassene Wrapper-, Join- und Zeilenstartgewohnheiten
```

Ein zweiter Schreiber muss die Kartenidentität und den Stencil lernen, nicht
die sichtbare Form jedes Vorgängers imitieren. Erwartbare Fehler sind:
falscher Wrapper bei richtiger Karte, vergessener COMMIT, doppeltes qokaiin am
Zeilenübergang, stehengebliebene L/O-Kante und aus einem falschen
Registerexemplar kopierter Wert. Ein Fehler, der eine exakte Wertkarte durch
eine ähnlich aussehende andere Karte ersetzt, ist semantisch schwerer als ein
Rendererwechsel.

## Historische technische Vergleichsfälle

Die Vergleiche belegen keine Voynich-Lesung; sie zeigen, dass die vorgeschlagene
Werkstattökologie um 1420 gewöhnliche Bestandteile kombiniert.

- [Wellcome MS.8515](https://wellcomecollection.org/works/w9nkm98w), um 1425,
  ist ein praktisches Handbuch aus Kalender, Rechenalgorithmen, astronomischen
  Tabellen und astrologischer Medizin; medizinische Rezepte wurden später von
  mehreren Händen ergänzt. Das ist der engste Vergleich für getrennte
  Rechen-/WHEN-Instrumente plus praktische Medizin in einem fortbenutzten Buch.
- [BL Add MS 29301](https://searcharchives.bl.uk/catalog/032-002020783),
  um 1420–30, vereint illustrierte Chirurgie, Instrumente, Zodiac Man,
  Heilpflanzenzeichnungen, *Circa instans* und Rezepte. Es stützt gerade die
  Kombination WHAT/HOW/WHEN, nicht die Voynich-Kartenform.
- [BL Harley MS 2378](https://searcharchives.bl.uk/catalog/040-002032704) ist
  ein im 15. Jahrhundert organisch geführtes medizinisch-kulinarisch-
  alchemistisches Sammelbuch; Rezepte kamen von mehreren Händen hinzu, und der
  Inhalt umfasst Astrologia medicorum sowie sieben Kräuter und sieben Planeten.
- [BL Harley MS 2558](https://searcharchives.bl.uk/catalog/040-002032705) ist
  das ärztliche Commonplace-Buch Thomas Fayrefords mit botanischen Synonymen,
  Herbal, Fällen, Behandlung, Uroskopie und Prognostik. Es zeigt, warum
  Registerwechsel und lokale Wortschätze in einem praktischen Buch sinnvoll
  sind.
- [Wellcome MS.97](https://wellcomecollection.org/works/ad2gt65q), etwas später
  (ab 1484), ist ausdrücklich ein mehrhändig geführtes Daten- und Regelhandbuch
  für astrologische Medizin mit Rezepten, Aderlass, Glückstagen, Kreisen und
  Tabellen. Es ist ein später Funktionsvergleich für den WHAT/HOW/WHEN-Gebrauch,
  kein Datierungs- oder Herkunftsbeleg.

Keiner dieser Zeugen besitzt nach diesem Bericht ein Voynich-gleiches
Kartenbuch, einen Donor, dieselbe Sprache oder dieselben 28 Werte.

## Modellvergleich nach V14-Rubrik

| Modell | Abdeckung /25 | Workflow /20 | Register /15 | Lesungen /15 | historisch /15 | Rivalen/Prognosen /10 | Gesamt |
|---|---:|---:|---:|---:|---:|---:|---:|
| WHAT/HOW/WHEN in Kartenmaschine | 23 | 18 | 14 | 12 | 14 | 9 | **90** |
| generisches indexiertes Formular-/Exemplarbuch | 22 | 19 | 13 | 8 | 11 | 9 | **82** |
| medizinische Herbal+Bio-Sammlung, Astro unverbundener Annex | 21 | 16 | 12 | 11 | 14 | 8 | **82** |
| natürlich-philosophisches Kompendium | 17 | 14 | 12 | 9 | 13 | 7 | **72** |
| abgekürzte gewöhnliche Mischprosa | 15 | 13 | 8 | 10 | 13 | 7 | **66** |

Der Sieger gewinnt nicht, weil WHEN bewiesen wäre, sondern weil er mit einer
losen Konsultationsregel mehr erklärt als der generische Rivale. Der Rivale
bleibt gefährlich: Falls die Bio-Bilder keine wiederholbaren praktischen Slots
tragen und die Astro-Instrumente keinerlei medizinisch nutzbare
Auswahlstruktur zeigen, fällt der Zweckgewinn weg; die Kartenmaschine selbst
bleibt dennoch bestehen.

## Vorhersagen und nächster rangändernder Befund

Nur innerhalb der zehn festen Seiten sagt das Modell voraus:

1. Derselbe exakte Bio-Wert muss bei Wiederholung als dieselbe kategoriale
   Antwort rücklesbar sein, auch wenn Feldordinal und sichtbarer Wrapper
   wechseln. Auf f82r.27 müssen die Zellen 3 und 6 mit `qokeedy` denselben
   formalen Wert C besitzen.
2. qokaiin soll nach einem Commit eher eine neue Buchung eröffnen als eine
   konkrete Flüssigkeit fortsetzen; der f82r.3–4-Doppelfall muss als
   Zeilencarry oder engste Dittographie erklärbar bleiben.
3. Alle FIRST/ONLY/LAST-L/O-Fälle müssen einen lokal noch aktiven Bezug finden;
   besonders f83r.52→54 muss die offene Kante über den physischen Zeilenraum
   tragen können.
4. F3 muss in Herbal und Bio dieselbe Referenzhandlung zulassen, obwohl der
   eine Beleg offen und der andere committed ist. Eine zwingende asymmetrische
   Dreiwortphrase in einem der beiden Kontexte würde den Prosa-Rivalen stärken.
5. Handwechsel sollen die exakte gemeinsame Karte erhalten, aber Wrapper- und
   Join-Häufigkeiten ändern dürfen. Ein handgebundener Ersatz des gesamten
   Kartendecks würde das Lehrsystem schwächen.
6. f68r1 soll ohne nachträglich erfundenen Start als räumlicher `1+28`-Katalog
   funktionieren; f69v soll genau wegen der Alternation eine zweiklassige
   28er-Folge tragen. Eine klare autorische gemeinsame Start-/Richtungsmarke
   auf beiden Seiten würde eine stärkere gemeinsame WHEN-Tafel ermöglichen;
   widersprechende Kardinalität oder ein nicht lokusgebundenes Label würde sie
   schwächen.
7. Die offenen Herbal-Absätze sollen über Bildunterbrechungen hinweg
   fortsetzbar bleiben. Wenn jede Pflanzennähe stattdessen wiederholt eine
   singuläre Wort-zu-Teil-Zuweisung erzwingt, muss der Artikeldecoder durch
   einen Caption-Decoder ersetzt werden.

**Der einzelne Befund, der die Rangfolge am stärksten ändern würde**, ist eine
blind inventarisierte Zuordnung aller wiederholten Bio-Wertkarten zu
wiederholten, zeichnerisch definierten Stationsklassen auf `f81v/f82r/f83r`.
Wenn derselbe exakte Wert trotz wechselnder Position wiederholt dieselbe
visuelle HOW-Klasse trägt, steigt der medizinische Verbund deutlich. Wenn die
Werte visuell frei permutieren und nur die Schreibkadenz erhalten, gewinnt das
generische Formular-/Exemplarbuch. Nähe allein genügt nicht; die Station muss
vor dem Lesen der Karten definiert werden.

## Schluss

Die beste R3-Synthese ist kein verschlüsselter Satztext und keine moderne
Datenbank. Sie ist eine handschriftlich ausführbare technische
Kompilationspraxis:

```text
medizinisch-praktischer WHAT/HOW/WHEN-Inhalt
  ausgeführt durch ein generisches Kartenregister
  mit bildgeerbten Adressen, mobilen Relations- und Referenzformeln,
  exakten kategorialen Werten, lokalen Commits und handabhängigem Renderer
```

Der Zweck ist vorläufig medizinisch-praktisch; die Maschine ist stärker
belegt als der Zweck. Diese Asymmetrie ist produktiv: Die Kartenmaschine darf
stehen bleiben, selbst wenn WHAT/HOW/WHEN später gegen ein generisches
Werkstattbuch verliert.

## Quellen- und Siegelnotiz

Verwendet wurden ausschließlich `f10r`, `f11r`, `f55v`, `f56r`, `f81v`,
`f82r`, `f83r`, `f67r2`, `f68r1` und `f69v`. Die sechs vorhandenen offiziellen
Yale-IIIF-Bilder für Bio/Astro wurden über eine vorselektierte, mit
`./vmanus-exp query-tsv` und `--forbid-prefix f84` gelesene Allow-Liste
aufgerufen. Die sieben Prosaseiten wurden nur aus f84-freien GDT327/GDT276-
Beständen bzw. mit explizit erlaubtem Locus gelesen. Die Kreis-Seiten wurden
nicht an GDT327-Tupel angeschlossen. Keine neue Voynich-Seite, kein Substring,
keine Phonetik und keine Sprachidentifikation wurde verwendet. `f84` und
`f84r` wurden nicht geöffnet, geparst, angezeigt, verbunden oder bewertet.
