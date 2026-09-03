# GDT767-Methode — atomare Ganzwörter gegen historische Stoff- und Formklassen

## Frage

Welche der 28 bereits beobachteten vollständigen Wörter lassen sich durch
unabhängig wiederkehrende Nachbarfelder als Rohdroge, getrocknete Droge,
Zubereitung oder konkrete Substanzklasse eingrenzen?

Die Arbeitsannahme ist ein spätmittelalterlich plausibles Mischregister:

```text
gelernter Ganzname
+ optionaler Pflanzenteil oder Arzneiform
+ Zustand/Qualität und Grad

oder

Rezeptformel + Zutat/Zubereitung + Menge + Vorgang/Ergebnis
```

Historische Wörter liefern Kandidaten für diese Plätze. Sie werden nicht über
EVA-Schreibung, sichtbare Initialen oder lateinische Lautähnlichkeit an ein
Ziel gebunden.

## Eingaben und feste Grenze

Der Builder verwendet:

- die von GDT766 registrierten 25 vollständigen `ofch`-Formen;
- `chor`, `schor` und `lchor` aus dem GDT766-Ganzwortdeck; `pchor` bleibt als
  Öffnungsform außerhalb der Zielkohorte;
- die fünf GDT766-Linien mit 46 lokalen Token-Defaults;
- GDT766s vier schwache `ofch`-/Reproduktionskontakte;
- das von GDT764 bereitgestellte, bereits guarded semantische Cacheumfeld;
- GDT754s Inventar von 172 quellkomponierten Ganzformen;
- `src/HISTORICAL_CANDIDATE_DECK.tsv` mit 18 Kandidaten;
- `src/HISTORICAL_SOURCE_REGISTRY.tsv` mit sechs historischen Quellen.

Nur reader-exakte Vorkommen im vorhandenen Cache sind zulässig. ZL3b, IT2a
und RF1b sind alternative Lesungen desselben Manuskripts. Es werden keine
neuen Seiten, Bilder oder Transkriptionen geöffnet. Selektoren mit `f84` oder
`f84r` bleiben verboten.

## Zielkohorte

Ein `ofch`-Ziel ist jedes reader-exakte, durch Leerraum begrenzte vollständige
Wort, dessen EVA-Oberfläche die Zeichenfolge `ofch` enthält. Die
Zeichenfolge ist nur ein formaler Selektor und erhält keinen semantischen
Wert.

Zusätzlich werden ausschließlich die exakten Ganzwörter `chor`, `schor` und
`lchor` aufgenommen. Längere ähnliche Formen werden nicht als diese Wörter
gezählt.

Die deterministische Kohorte umfasst:

- 25 `ofch`-Ganzformen mit 43 Vorkommen;
- `chor` mit 176 Vorkommen;
- `schor` mit drei Vorkommen;
- `lchor` mit zwei Vorkommen;
- insgesamt 28 Ganzformen und 224 Vorkommen.

## Target-excluding Geber

Ein Ziel darf nie über seine eigene frühere deutsche Lesung oder über die
Lesung eines anderen Zielworts gestützt werden. Vor der Merkmalsextraktion
werden deshalb alle folgenden vollständigen Oberflächen als Geber gesperrt:

1. die 28 Zielwörter;
2. `pchor`;
3. die 172 GDT754-`PRODUCTIVE_COMPOUND`-Formen.

Nach Mengenvereinigung sind 200 verschiedene Oberflächen gesperrt. Ein
verbleibender Geber muss zugleich reader-exakt und im GDT764-Umfeld
quarantäne-sauber sein. Eine alte Quellglosse oder bloß ähnliche Schreibform
erzeugt kein Merkmal.

Für jedes Zielvorkommen werden drei Fenster getrennt gespeichert:

- `D1`: direkte linke oder rechte Nachbarschaft;
- `R3`: Abstand eins bis drei auf derselben Linie;
- `LINE`: alle übrigen zugelassenen Geber derselben geschriebenen Linie.

Intern behält jeder Geber Oberfläche, Ordinal, Abstand, Merkmalsmenge und
semantische Quelle. Die veröffentlichte Occurrence-Datei serialisiert
Oberfläche, Ordinal, Abstand und Merkmale; der Validator bindet jeden davon
erneut an seine semantische Quelle und bestätigt, dass alle Zieloberflächen
blockiert und alle verwendeten Geber reader-exakt sowie sauber sind.

## Zwölf Nachbarmerkmale

Zugelassene Geber können zwölf bereits registrierte Feldmerkmale tragen:

```text
DRY, MOIST, HOT, COLD, STAGE, VALUE_AMOUNT,
CTHY_LEAF, CHOR_REPRO, PREP, PROCESS_CLOSE, H1, H2
```

`CTHY_LEAF` entsteht nur aus dem vollständigen Wort `cthy`.
`CHOR_REPRO` würde nur aus exaktem `chor` entstehen; weil `chor` selbst zur
Zielkohorte gehört, ist es im strikten Geberlauf gesperrt. Damit kann kein
`ofch`-Wort seine Blütenlesung durch das zugleich untersuchte `chor`
bestätigen.

Spezifische Anforderungen wie `ROOT_IDENTITY`, `WOOD_BARK_IDENTITY`,
`RESIN_GUM_IDENTITY`, `SALT_IDENTITY` oder `LIQUID` werden nicht aus einem
generischen Material-, Feucht- oder Zubereitungsfeld erfunden. Fehlt ein
unabhängig lizenzierter Geber, bleibt der Kandidat bei null.

Die 224 Vorkommenszeilen werden pro Ganzform und Merkmal zu
`D1/R3/LINE`-Vorkommenszählern aggregiert. Es wird Anwesenheit pro
Zielvorkommen gezählt, nicht die Zahl beliebig vieler Geber derselben Klasse.

## Historisches Kandidatendeck

Die 18 Kandidaten sind in zwei Ebenen getrennt.

### Stoffebene

- `S00`: benannte Arzneidroge, Identität offen;
- `S01`: Blütendroge;
- `S02`: Samendroge;
- `S03`: Wurzeldroge;
- `S04`: Blattdroge;
- `S05`: Holz- oder Rindendroge;
- `S06`: Harz oder Gummi;
- `S07`: Arzneisalz.

### Formebene

- `F00`: Arzneiform offen;
- `F01`: Rohdroge;
- `F02`: getrocknete Droge;
- `F03`: Pulver;
- `F04`: Zubereitung;
- `F05`: Mazerat oder feuchter Auszug;
- `F06`: Arzneiöl;
- `F07`: Arzneiwasser;
- `F08`: Kräuterwein;
- `F09`: Arzneiessig.

Jede Karte enthält erforderliche R3-Merkmale, mindestens eines aus einer
R3-Alternativmenge, verbotene Linienmerkmale, zulässige GDT766-Kanäle,
Wiederholungsbedarf, historische Formen, Quellen und Attestationsart. Keine
Karte besitzt Komponenten- oder Schreibähnlichkeitskredit.

## Evidenzstufen und Rangfolge

Ein Kandidat trifft an einem Vorkommen nur, wenn alle erforderlichen
R3-Merkmale vorhanden sind, gegebenenfalls mindestens ein Alternativmerkmal
vorhanden ist und kein verbotenes Linienmerkmal vorkommt. Kandidaten ohne
positive Gate-Anforderung (`S00`, `F00`) sind Fallbacks und erzeugen selbst
keinen Treffer.

Die Evidenzstufe lautet:

| Bedingung | Stufe |
|---|---:|
| wiederholte R3-Treffer und passender GDT766-Kanal | 4 |
| wiederholte R3-Treffer ohne Kanalpassung | 3 |
| ein R3-Treffer und Kanalpassung | 2 |
| ein R3-Treffer ohne Kanalpassung | 1 |
| kein Treffer oder semantische Redundanz | 0 |

Innerhalb von Stoff- und Formebene wird zuerst nach Evidenzstufe, dann nach
folgendem deskriptiven Score sortiert:

```text
20 * Evidenzstufe
+ 10 * (R3-Treffer / Vorkommen)
+ min(9, R3-Treffer)
```

Der getrennte Explorationsscore addiert zwei Punkte für passende Kanalrolle
und höchstens einen sichtbaren, nicht evidenzwirksamen Alt-Blüten-Tiebreak.
Der Score ist keine Wahrscheinlichkeit und bestätigt kein Wort.

Für `chor=S04 Blattdroge` gilt eine vorab eingebaute
Redundanzkontrolle: Wiederholte `cthy`-Parallelität spricht für zwei
verschiedene Pflanzenteile, nicht für zwei Blattwörter. Ein solcher Kandidat
wird auf Evidenzstufe null gesetzt.

## Separierbarkeit

Für jeden historischen Kandidaten wird über alle 28 Zielwörter ein vollständiger
Vektor aus `D1/R3/LINE`-Treffern erzeugt. Kandidaten mit identischem Vektor
bleiben ausdrücklich in derselben Rivalengruppe; der publizierte Kurz-Hash
dient nur der reproduzierbaren Vektoridentität.

Diese Prüfung fragt nicht, welches historische Wort ähnlich aussieht. Sie
fragt, ob die beobachteten unabhängigen Felder die Kandidaten überhaupt
auseinanderhalten können.

## `chor`/`cthy`-Parallelität und Schattenkontakte

Im `LINE`-Fenster wird jedes exakte `cthy` bei einem exakten `chor` separat
ausgegeben. Richtung, Abstand, Reihenfolge und direkte Nachbarschaft bleiben
sichtbar. Erwartet werden 15 `chor`-Positionen auf 14 Loci, fünf davon direkt
benachbart und mit beiden geschriebenen Reihenfolgen.

Die vier GDT766-Kontakte zwischen einem `ofch`-Wort und `schor`, `chory` oder
`shor` werden in einer getrennten Schattentabelle übernommen. Sie erhalten
null exakten-`chor`-Ankerkredit, null Identitätskredit und null
Komponentenexport. Ihr Zweck ist explorativ: Sie halten Blüte beziehungsweise
Samen/Frucht als C0-Rivalen sichtbar.

## Wörterbuchentscheidung

Pro Ganzwort wird auf jeder Ebene der beste Kandidat mit Evidenzstufe
mindestens zwei und ohne Redundanzstrafe gewählt. Fehlt ein solcher Kandidat,
fällt die Stoffebene auf `S00` und die Formebene auf `F00` zurück.

`chor` ist ein Sonderfall: Es trifft mehrere unvereinbare Formkarten stark.
Darum wird keine einzelne Roh-, Trocken- oder Zubereitungsform exportiert; die
portable Lesung bleibt „anderer oder reproduktiver Pflanzenteilposten; nicht
Blattgut“.

Das Wörterbuch trennt anschließend:

1. ausgewählte target-freie Stoff- und Formklasse;
2. portable Ganzwortbeschreibung;
3. konkreten, ausdrücklich ersetzbaren Readerdefault;
4. Rivalen, Evidenz und Gegenbeleg.

Alle konkreten Stoffidentitäten bleiben `C0_REPLACEABLE_DEFAULT`. Frühere
Blütenwerte bleiben sichtbar, bis bessere Evidenz sie ersetzt. Nur
`ofcheol` und `qofcheol` werden von „Blütenauszug“ auf die ehrlichere
„Blütenzubereitung“ zurückgenommen; Auszug und konkrete Flüssigkeiten bleiben
Rivalen.

## Fünf-Linien-Reader

Die 46 registrierten Tokenpositionen der Linien f22r.4, f22v.1, f41v.2,
f93r.2 und f107r.38 werden genau einmal ausgegeben. Für die sieben Positionen,
deren Ganzwort im 28er-Deck liegt, wird der GDT767-Default verwendet; alle
anderen behalten den registrierten lokalen GDT766-Default.

Die deutsche Linie verbindet Tokenwerte ausschließlich mit Semikolons. Das
erhält die schriftliche Reihenfolge, behauptet aber weder Anfügung noch
Satzsyntax. Eingefügte deutsche Flexion oder Glättung liefert keine Evidenz.

## Reproduktion und Claim-Grenze

```bash
python3 experiments/yolo/gdt767_ofch_historical_identity_cofield_tournament/src/run.py
python3 experiments/yolo/gdt767_ofch_historical_identity_cofield_tournament/src/validate.py
```

GDT767 darf 28 konkrete, ersetzbare Ganzwortdefaults und fünf vollständige
Arbeitslinien ausgeben. Es darf Form-/Zustandsklassen auswählen, die
`cthy`/`chor`-Parallelität als Hinweis auf verschiedene Pflanzenteilposten
verwenden und Blüte als C0-Default stehen lassen.

Es darf kein Lexem, keine Substanz, Pflanze, Flüssigkeit, Einheit, Sprache,
Phonetik oder Klartextklausel bestätigen; keine Bedeutung auf einen
Teilstring übertragen; keine ungesehene Form erzeugen; und keine neue Seite,
kein Bild, kein Transkript, `f84` oder `f84r` öffnen.
