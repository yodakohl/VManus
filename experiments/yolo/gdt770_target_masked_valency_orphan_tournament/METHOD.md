# GDT770-Methode — targetmaskiertes Valenz- und Waisenturnier

## Frage

GDT770 prüft eine kleine praktische Frage: Wenn in einer bereits vollständig
gelesenen Zeile die bisherige Rolle und der deutsche Default von `ol`, `ckhy`,
`ols` oder `otar` entfernt werden, welcher **vorab feste Ganzwortkandidat**
schließt die verbleibenden Strukturkanten mit den wenigsten Zusatzannahmen?

Das ist kein Übersetzungswettbewerb. Gewertet werden nur Bindungen an
target-unabhängig eingefrorene Rollen der direkten Nachbarn. Eine wohlklingende
Zeile, historische Plausibilität oder der bisherige GDT769-Default bringt
keinen Punkt.

## Fester Zeilenbestand und Maskierung

Die einzige Kohorte ist `src/COHORT_15_LINE_SPECS.tsv`: fünfzehn bereits
zugelassene vollständige Reader-Zeilen. Sie wird nicht durch weitere Treffer
oder passendere Seiten ergänzt.

- Nur die vier vollständigen Oberflächen `ol`, `ckhy`, `ols` und `otar` sind
  Targets. Alle exakten Token-Gleichheiten werden zeilenweit gleichzeitig
  maskiert. Der feste Bestand enthält 17 reader-exakte, gewertete Masken:
  `ol=5`, `ckhy=4`, `ols=3`, `otar=5`. `pcheey` gehört nicht zum Turnier.
- An jeder Targetstelle werden der alte Default, die alte Rolle, alte Evidenz
  und alte Konfidenz entfernt. Die Targetachsen und Targetrollen sind `NONE`.
- Jeder Nicht-Target-Default bleibt lediglich als Reader-Anzeige erhalten.
  Für die Wertung werden ausschließlich seine eingefrorenen Strukturrollen
  und seine Reader-Exaktheit benutzt. `line_class`, der deutsche Default und
  formale `structural_axes` dürfen keinen Zweig, keine Bindung und keine Strafe
  wählen.
- `left_neighbor_roles`, `right_neighbor_roles`, `left_neighbor_exact` und
  `right_neighbor_exact` definieren die beiden unmittelbaren, targetwärts
  gerichteten Nachbarkanten. Nur eine reader-exakte direkte Nachbarkante ist
  bindbar. Es wird nicht über einen näheren Nachbarn zu einem günstigeren
  ferneren Wort gesprungen.
- ZL3b, IT2a und RF1b sind alternative Lesungen desselben Manuskripts, keine
  drei unabhängigen Belege.

Drei bereits lizenzierte targetfreie Mehrtokenkonstruktionen werden vor der
Nachbarsuche als je ein Nicht-Target-Knoten behandelt. So werden 131 Token zu
128 **Scoreknoten**. Der vierte Span, `G770-SPAN-X4P7` in G770-L004, ist nur
für die Reader-Ausgabe target-owned: `ols` an Ordinal 11 bleibt beim Scoring
ein eigener maskierter Targetknoten und `aiin` an Ordinal 12 eine getrennte,
bindbare rechte `VALUE`-Kante. Erst die Reader-Ausgabe konsumiert beide als
eine render-once Einheit und besitzt deshalb 127 praktische Reader-Einheiten.
Kein targettragender Span wird vor der Nachbarsuche kollabiert. Der feste
Bestand enthält keine nicht-exakte Targetdublette. Sollte die Reproduktion
dennoch eine finden, wird sie gleichzeitig maskiert, bleibt ungewertet und
darf weder Nachbar noch Bedeutungsgeber sein.

Die zulässigen Strukturrollen sind `AMOUNT`, `VALUE`, `PATIENT`, `SOURCE`,
`RESULT`, `PROCESS`, `ENDPOINT`, `FIELD`, `CLOSE`,
`PREDICATE_ONLY_CLOSE`, `MATERIAL`, `PREPARATION` und `PRODUCT`. Formale Achsen
wie `DRY`, `HOT` oder `LEVEL_III` bleiben getrennte Beschreibungen; sie sind
weder Rollen noch deutsche oder englische Wörter.

Bloße Zeilenfinalität erzeugt ausdrücklich kein `PREDICATE_ONLY_CLOSE`. Im
festen Bestand ist keine solche Targetstelle unabhängig markiert. Das wird für
alle 17 Masken gesondert in
`src/TARGET_INDEPENDENT_SLOT_CONSTRAINTS.tsv` festgehalten, statt eine alte
Targetrolle wieder in den Scorer einzuschleusen. P02 bleibt dadurch
ausführbar, feuert in dieser Kohorte aber nullmal.

Es wird keine neue Seite, kein Bild und keine Transkription geöffnet. `f84` und
`f84r` bleiben gesperrt.

## Feste Kandidatendecks

`src/CANDIDATE_POLICY_SPECS.tsv` ist die vollständige Kandidatenquelle. Eine
mehrzeilige Kandidaten-ID bezeichnet **einen** Positionsdispatch mit festen,
priorisierten Zweigen; sie sind keine nachträglich getrennt wählbaren
Kandidaten.

| Target | Feste Kandidaten |
| --- | --- |
| `ol` | `OPAQUE_NULL`; Positionsrelator: nach linker Menge `von/aus`, sonst zweiseitig `und/mit`; invariantes Nomen `Ansatz/Basis`; invariantes messbares `Produkt/Resultat` |
| `ckhy` | `OPAQUE_NULL`; Positionsdispatch: final mit linkem Patienten `mischen`, medial `Mischung`; invariantes `mischen`; invariantes Nomen `Mischung`; invariantes Nomen `Infusion/Dekokt` |
| `ols` | `OPAQUE_NULL`; Positionsdispatch: vor rechtem Wert `Maß/Dosis`, sonst final `Endportion`, sonst `Produktposten`; invariantes Nomen `Zubereitung`; invariantes `Fertigprodukt/Colatura`; invariantes `abseihen` |
| `otar` | `OPAQUE_NULL`; allgemeine Folge `weiter/dann`; Endpunktrelation `bis`; nominales `Übergangs-/Zubereitungsfeld` |

Die Großbuchstaben in `structural_tag` sind Modellrollen. Die Ausdrücke in
`renderer_de` sind ersetzbare Anzeigen. Keine der beiden Spalten behauptet ein
Lexem oder eine Übersetzung.

## Deterministische nächste Kantenbindung

Für jede Kandidaten-ID wird dieselbe Prozedur ohne Anpassung an den deutschen
Text ausgeführt.

1. Alle Targets einer Zeile werden gleichzeitig maskiert. Zielstellen werden
   danach nach `page`, `locus`, `ordinal` und `target_mask_id` sortiert. Jede
   Seite ist die Resampling-Einheit.
2. Links und rechts stellt jeweils nur der unmittelbare reader-exakte
   Nicht-Target-Nachbar Rollen bereit. Eine Rolle wird als Kante
   `(target_mask_id, side, neighbor_ordinal, role)` adressiert. `NONE` und ein
   nicht exakter Nachbar stellen keine Kante bereit.
3. Positionszweige werden in aufsteigender `branch_priority` geprüft; der erste
   erfüllte Zweig gilt. `ELSE` darf erst nach allen früheren Zweigen feuern.
   Feuert kein Zweig, ist die Verzweigung illegal. Ein invariantes Modell
   benutzt an jeder Targetstelle denselben Zweig.
4. Pflichtausdrücke aus `required_edge_expression` werden zuerst gebunden,
   danach optionale Klassen aus `consumes_left_classes` und
   `consumes_right_classes`. `LEFT_ONE`, `RIGHT_ONE` und `ANY_SIDE` bedeuten
   genau eine Kante. Bei `ANY_SIDE` gewinnt die geringere Distanz; bei der hier
   einzig möglichen Distanzgleichheit gilt links vor rechts. Hat derselbe
   Nachbar mehrere zulässige Rollen, entscheidet die alphabetisch kleinste
   vollständige Rollenbezeichnung. Ein anderer Kandidat bekommt keine
   günstigere Auflösung derselben Gleichheit. Auch die optionale Bindung darf
   höchstens eine noch offene Kante pro Seite verbrauchen.
5. Pro Kandidat und Zielstelle darf jede Kanten-ID nur einmal verbraucht
   werden. Zwei logische Anforderungen dürfen nicht dieselbe Kante teilen.
   Ein solcher zweiter Zugriff bleibt sichtbar und erhält die festgelegte
   Doppelverbrauchsstrafe.
6. Eine Kante wird nie über die physische Zeile, einen anderen Targetmaskenplatz
   oder den unmittelbaren Nachbarn hinaus gesucht. Es gibt keine semantische
   Komponentenzerlegung und keinen Rückgriff auf das unmaskierte Target.

Der DSL-Parser akzeptiert in `NEAREST_*_IN`, `LEFT_ONE`, `RIGHT_ONE` und
`ANY_SIDE` nur nichtleere Mengen der oben genannten Rollen. `ALWAYS` und
`ELSE` dürfen nur als vollständige Bedingung auftreten; Zweigprioritäten sind
pro Kandidat eindeutig und lückenlos, ein `ELSE`-Zweig ist eindeutig und
letztgereiht. Tippfehler werden damit nicht still als bloß fehlende Evidenz
behandelt.

Eine Seite zählt für einen Zweig nur dann als qualifiziert, wenn der Zweig dort
mindestens einmal legal feuert und alle in der Kandidatenzeile verlangten
Kanten besitzt. Mehrere Treffer derselben Seite ergeben weiterhin genau eine
Zweigseite.

## Strukturwaisen

Unter `OPAQUE_NULL` bleiben die targetwärts exponierten Kanten offen. Pro Seite
wird höchstens eine konkrete Nullwaise mit der vorab festen Priorität
`AMOUNT > VALUE > PATIENT > RESULT` angelegt; ein `ENDPOINT`- oder `CLOSE`-
Nachbar zählt in diesem Waisenbuch als `RESULT`. Sind auf beiden Seiten exakte
typisierte Nachbarn vorhanden, kommt unabhängig davon eine einzige
zweiseitige `FIELD_EDGE` hinzu. Sie bezeichnet die durch die Maske
unterbrochene Feldverbindung und verlangt für ihre Auflösung zwei verschiedene
Seitenbindungen. Eine Kandidatenanforderung, die erst durch den Kandidaten
selbst entsteht, ist keine entfernte Nullwaise.

P04 berechnet für jede solche reader-exakte, nach dem Binden weiter offene
Nullwaise vier Punkte. Ein als Resultat ausgegebener Targetposten ohne
gebundene Quelle erhält ebenfalls vier Punkte. So sind die Strafsumme und die
gesonderte Gewinnerhürde für zwei entfernte Waisen auf zwei Seiten auf
demselben expliziten Kantenbestand definiert.

## Feste Strafsumme

`src/PENALTY_SPECS.tsv` ist ausführbar gemeint. Positive Zahlen sind schlecht
und werden addiert:

- illegale Verzweigung oder ungeeigneter Endpunkt: `+6`;
- Vorgang ohne Patient, Maß ohne Wert oder einseitiger Verbinder: `+5`;
- offene Menge, offener Wert, Patient, Resultat oder Feldkante sowie ein
  Targetresultat ohne Quelle: `+4`;
- Doppelverbrauch derselben Kante: `+3`;
- Nomen in einem target-unabhängig markierten reinen Prädikatsabschluss: `+2`;
- ungelöstes Target: `+1`.

Der Runner bindet alle normativen Straf- und Gatefelder einschließlich
Trigger, Anwendungsbereich, Kofeuerregel, Metrik, Vergleichsoperator,
Schwelle, Tie-Regel und Disposition an je einen kanonischen Projekthash. Nur
Namen und Beschreibungsprosa sind nicht normativ; eine stille Abweichung
zwischen TSV und Code bricht die Ausführung ab.

Die in einer Strafzeile mit `|` verbundenen Varianten werden an derselben
Targetstelle höchstens einmal erhoben, außer P04: verschiedene offene
Kanten-IDs werden dort einzeln gezählt. Verschiedene Strafzeilen dürfen
gemeinsam feuern. Ein fehlender rechter Endpunkt erhält P06; derselbe fehlende
Endpunkt wird nicht nochmals als P05-Einseitigkeit berechnet. Eine illegale
Positionsverzweigung bleibt dagegen zusätzlich ungelöst und kann P06 und P01
gemeinsam erhalten.

## Delta gegen das opake Target

Für Zielform `t` und Kandidat `c` sei `P_t(c)` die Summe der obigen Strafen über
die feste Kohorte. Der einzige Primärscore ist

```text
delta_t(c) = P_t(OPAQUE_NULL) - P_t(c)
margin_t(c, r) = delta_t(c) - delta_t(r)
               = P_t(r) - P_t(c)
```

Ein positives Delta ist eine Verbesserung gegenüber der Maske. Strafen aus
unverändertem Nicht-Target-Hintergrund werden nicht gewertet; sie würden bei
jedem Kandidaten identisch ausfallen. `renderer_de`, Satzfluss,
Wortreihenfolge-Plausibilität und historische Geläufigkeit sind ausdrücklich
keine Scorekanäle.

## Gewinner und Abdeckung

Die Reihenfolge und maschinenlesbaren Schwellen stehen in
`src/WINNER_GATE_SPECS.tsv`. Ein Nicht-Null-Kandidat ist nur ein vorläufiger
Policy-Gewinner, wenn er:

1. NULL um mindestens vier Strafpunkte schlägt;
2. **jeden** anderen festen Kandidaten derselben Zielform um mindestens vier
   schlägt;
3. mindestens zwei unter NULL vorhandene Strukturwaisen auf mindestens zwei
   verschiedenen Seiten entfernt;
4. nach dem Weglassen jeder einzelnen Seite weiterhin strikt vor NULL und
   jedem Rivalen liegt; ein Fold-Gleichstand ist ein Fehlschlag;
5. als Positionsdispatch zusätzlich das beste invariante Modell um mindestens
   vier schlägt und jeden erklärten Zweig auf mindestens zwei Seiten belegt.

Die Zweigabdeckung wird auf der vollen Kohorte geprüft und in den
Leave-one-page-out-Folds nicht neu angepasst. Die feste Policy wird in jedem
Fold unverändert neu gewertet. Ein Kandidat mit einer unterdeckten
Pflichtverzweigung erhält `INSUFFICIENT_BRANCH_COVERAGE`; er wird nicht zum
Verlierer umgedeutet und ein Runner-up wird nicht automatisch eingesetzt. Ein
anderer Kandidat kann nur gewinnen, wenn er unabhängig alle Gates besteht und
auch den unterdeckten Rivalen im Scorevergleich um vier schlägt. Exakte
Gleichstände gehen immer an `OPAQUE_NULL`.

G08 wird nach bestandenen Gates 1–7 ausgewertet. Ein gebundener Vollminimum-
Gleichstand wird zusätzlich trotz seines bereits gescheiterten G03 sichtbar
durch G08 abgewiesen; so bleibt die ausdrücklich registrierte Tie-Regel im
Audit ausführbar, ohne einen früher ausgeschiedenen eindeutigen Leader
nachträglich als Gewinner erscheinen zu lassen.

## Behauptungsgrenze

Ein möglicher Gewinner wäre nur die in dieser kleinen Kohorte nützlichste
strukturelle Ganzwort-Policy. GDT770 bestätigt kein deutsches, englisches,
lateinisches oder anderes Lexem, keine Wortart, keine Komponente, kein
Morphem, keinen Laut, kein Zeichen, keinen Klartext und keine historische
Substanz oder Operation. Alle Komponenten- und EVA/Latin-Kredite bleiben null.

## Reader nach der Wertung

Der vollständige Reader ist ein ausdrücklich nachgelagerter Arbeitsauszug und
kein zusätzlicher Scorekanal. Pro Zielstelle bleiben alle legalen Kandidaten
mit derselben niedrigsten lokalen Strafe sichtbar; Tabellenreihenfolge bricht
keinen Gleichstand. Der deutsche Lesetext konkretisiert Schrägstrichanzeigen
editorial (`Fertigprodukt/Colatura` etwa als `fertige Zubereitung`), ohne einen
neuen Kandidaten oder Punkt zu erzeugen. Zwei gebundene Seiten tragen Stufe A,
eine Seite B, keine Seite C. C-Fälle und lokale Gleichstände stehen in eckigen
Frageklammern.

`READER_UNIT_CONSUMPTION.tsv` ordnet jede der 127 Ausgabeeinheiten ihren
Quellordinalen zu. Diese Mengen müssen disjunkt sein und zusammen exakt alle
131 Token enthalten; ein target-owned Zweierspan erscheint als eine
Reader-Einheit, bleibt aber im Scoring in zwei Knoten getrennt.
