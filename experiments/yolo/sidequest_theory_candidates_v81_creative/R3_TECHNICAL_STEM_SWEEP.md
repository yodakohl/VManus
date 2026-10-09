# R3 — schneller technischer Wortstamm-Sweep

## Ergebnis

Für den kreativen Zehnseiten-Sidequest trägt derzeit am besten **kein reines
Sprachmodell und kein reiner Nomenklator**, sondern eine gemischte
Werkstattnotation:

```text
Eintritts-/Schreibvariante
+ kurze Operations- oder Bezugskarte
+ Argumentklasse
+ optionaler Schrittabschluss
+ auswendig gelernte Ganzkarte, wenn die Kombination nicht ausreicht
```

Das ist absichtlich eine Arbeitstheorie mit hohem Durchsatz. Sie soll lesbare
Vorschläge erzeugen, nicht etwas beweisen. Alle 173 festen Prosakarten und alle
381 festen Prosaereignisse haben jetzt einen kurzen Default. Keine Karte muss
mehr einen ganzen Satz wie „Pflanzenmaterial zeitgebunden beschaffen“ bedeuten.

Die gewählte Fassung benutzt:

- 13 wiederkehrende Stammachsen;
- 5 Argumentklassen;
- 2 Abschlusszeichen;
- 18 kurze praktische Bedeutungsachsen für die deutsche Ausschreibung;
- 78 auswendig gelernte Ganzkarten für die Fälle, in denen eine
  Stammzerlegung noch keinen brauchbaren Wert liefert.

95/173 Karten mit 246/381 Ereignissen erhalten wenigstens einen gemeinsam
verwendeten Stamm oder ein gemeinsam verwendetes formales Teil. Davon sind 27
Karten mit 86 Ereignissen stärker kompositionell; 68 Karten mit 160 Ereignissen
sind Mischfälle. 78 Karten mit 135 Ereignissen bleiben Ganzkarten. Das ist
weniger elegant als eine voll reguläre Sprache, aber für eine kleine Werkstatt
um 1420 viel leichter lernbar als 381 unabhängige Sätze.

## Schnell getestete Konkurrenzmodelle

Die vollständige Übersicht steht in `R3_STEM_MODELS.tsv`.

| Modell | Was daran funktioniert | Warum nicht allein gewählt |
|---|---|---|
| opaker 173er-Nomenklator | jede Karte kann einen festen Wert haben | erklärt keine Kartenfamilien |
| lateinische Flexionskürzung | sichtbare Stücke lassen sich leicht zerlegen | gleiche Endungen müssten zu viele unvereinbare Dinge bedeuten |
| Rezeptimperative | ergibt sofort knappe Lesungen wie nehmen, zugeben, wärmen, seihen | erklärt die sichtbaren Familien nur schwach |
| Werkstattbuchung | Posten + Operation + Argument + Status funktioniert in Herbal und besonders Bio | allein zu abstrakt für Stoffe und konkrete Geräte |
| reines Wasserwerk | liest viele Bio-Folgen sehr flüssig | zwingt Herbal unnötig in Rohre und Ventile |
| reiner Exemplarindex | erklärt beliebige lokale Inhalte | wäre ohne Meisterbuch intern nicht lesbar |
| gemischte Codebuch-Rezeptnotation | verbindet Stammökonomie, kurze Imperative und erlaubte Ganzkarten | gewählt; bleibt bewusst unregelmäßig |

## Gewählte Stammtafel

### Operations- und Bezugskerne

| Stamm | knapper Werkstattwert | typische lokale Ausschreibung |
|---|---|---|
| `OK` | Posten setzen | Anteil zugeben, Zielstation belegen, Lauf aktivieren |
| `OT` | markierten Gegenbezug wählen | zweiter Posten, vorige Dauer, unterer Ablauf |
| `L` | Anschluss oder Ablauf | weiter zum nächsten Empfänger, abziehen, abführen |
| `OR` | Ansatz oder bereitetes Ergebnis | frischer Ansatz, vorige Mischung, gebrauchsfertiger Auszug |
| `E` | Zustandsgrenze | bis bereit, bis gleichmäßig, bis klar |
| `EY` | sichtbarer Sollzustand | Zustand prüfen; lokal oft „klar genug“ |
| `D` | vorhandenen Bestand einsetzen | vorigen Bestand am bezeichneten Platz weiterführen |
| `K` | Transfer | eingießen, weiterleiten, einen Anteil bewegen |
| `O` | Voransatz/Weiterführung | vorigen Kontext wieder aufnehmen |
| `AL` | Ort oder Ziel | Stelle, Station, Becken, Öffnung |
| `AR` | Quelle oder „von dort“ | daraus, aus demselben Ansatz, vom Rücklauf |
| `AIIN` | Maß | Menge, Anteil oder lokale Dauerangabe |
| `CHOR` | zeitliche Auswahl | im passenden Stadium sammeln/nehmen |
| `CHEY` | Anteil auswählen | bezeichneten Materialanteil nehmen |

`AL`, `AR` und `AIIN` stehen sowohl als lesbare Kurzwerte als auch in den
bereits vorhandenen formalen Argumentpositionen. Das ist eine Werkstattlesung,
keine Behauptung, diese Zeichen seien deutsche oder lateinische Morpheme.

### Kompletierungen

```text
RIGHT-AIIN  = Standardmaß
RIGHT-AIN   = Anteil oder Passage
RIGHT-AL    = Ort oder Ziel
RIGHT-AR    = Quelle / von dort
RIGHT-AIR   = Lauf oder Weg
DY          = diesen Schritt fertig
B3          = diesen Posten fertig
```

Die sichtbaren Anfänge `q-`, `s-`, `d-`, `t-`, `ch-` und `sh-` werden nicht
mit fünf neuen Sachbedeutungen überladen. Wo dieselbe exakte Karte mehrere
solche Oberflächen hat, sind sie zunächst Schreib-/Eintrittsvarianten. Damit
können mehrere Schreiber dieselbe Tafel lernen, ohne jede Handvariation zu
einem neuen Wort zu machen.

## Was `shey / cheey` jetzt bedeutet

Die kurze Defaultlesung ist nur:

```text
EY = SICHTZUSTAND PRÜFEN
```

Im lokalen Nassprozess kann das zu „warten, bis es klar genug ist“ werden. Im
anderen Feld kann es nur „den verlangten Zustand prüfen“ heißen. Der einzelne
Ausdruck bedeutet **nicht** „bis die Flüssigkeit klar abläuft“. Flüssigkeit,
Klarheit und Ablauf sind drei lokale Ergänzungen, nicht Inhalt eines einzigen
Wortes. `shey` kann also ohne Schaden eine Eintrittsvariante plus Zustandskarte
oder eine unteilbare Zustandskarte sein; diese Runde muss das nicht entscheiden.

## Historischer Schnell-Sweep

Die Quellen liefern Analogien für die **Bauweise**, nicht die Voynich-Werte.

1. Die venezianische Tafel von 1411 mischt Alphabetersetzung, Homophone,
   Nullen und Ganzwortzeichen; rechts stehen unter anderem `Papa`, `et`, `con`
   und `quo`. Das unterstützt ein gemischtes, nicht rein sprachmorphologisches
   System. Quelle: William F. Friedman, *Six Lectures on Cryptology*, Fig. 16,
   [US-Regierungs-PDF](https://www.govinfo.gov/content/pkg/GOVPUB-D-PURL-gpo52787/pdf/GOVPUB-D-PURL-gpo52787.pdf).
2. Die Florentiner Fi1-Tafel von 1414 hat Ganzwortzeichen für `per`, `et` und
   `che`; Pisa 1442 kombiniert `ihs`, `che`, `et`, `per`, `pre`, `pro`, `pra`.
   Das zeigt, dass ganze Funktionswörter und kurze Wortstücke nebeneinander
   stehen konnten. Dokumentiert bei Aloys Meister 1902, S. 49–50 und 58–59,
   [Digitalisat](https://books.google.com/books?id=8-Ux0geGhPIC).
3. Die Este-Tafel von 1435 führt `Q`, `Que`, `Qui`, `Quo` sowie `e duplicatum`
   und `s duplicatum`. Für unsere Werkstatttheorie ist wichtig: Eine Tafel kann
   ganze Silben-/Wortstücke und Metaregeln mischen, ohne dass alles dieselbe
   Granularität hat. [ULB Münster, genaue Editionsseite 35](https://sammlungen.ulb.uni-muenster.de/hd/content/pageview/3076041).
4. Die Sieneser Si1-Tafel von 1433 gibt ganzen Namen/Titeln Zeichen und besitzt
   drei Alternativen für `Serenissimus`; der Lavinde-Komplex von 1379 enthält
   ganze Personen, Orte, Ämter sowie `pax` und `guerra`. Das stützt unsere
   erlaubten Ganzkarten und wechselnden Oberflächen. Meister 1902,
   [ULB-Digitalisat](https://nbn-resolving.org/urn:nbn:de:hbz:6:1-143638), und
   Meister 1906, [Archive.org-PDF](https://archive.org/download/diegeheimschrift00meis/diegeheimschrift00meis.pdf).
5. In spätmittelalterlichen Rezeptzeugen werden gerade die gattungsprägenden
   Ausdrücke besonders regelmäßig gekürzt: `recipe`, `ana`, Drachme, `semis`
   und Unze. Das ist eine gute Analogie für wenige wiederkehrende
   Operator-/Maßkarten bei ansonsten konkreten Zutatenkarten. Quelle:
   [Digital Scholarship in the Humanities 37.3](https://academic.oup.com/dsh/article/37/3/765/6401180).
6. Das italienische *Liber Secreti Naturali* (1425–1450) sammelt über 520
   Rezepte aus Alchemie, Medizin, Metallarbeit, Kosmetik, Landwirtschaft,
   Weinbereitung und Haushalt und besitzt sogar einen alphabetischen
   Sachindex. Ein einziges Werkstattbuch musste also nicht nur ein enges
   Fachgebiet enthalten. [Science History Institute, vollständiges Digitalisat](https://digital.sciencehistory.org/works/wg1tm9j).
7. Harley MS 1736 und Harley MS 2381 zeigen kurze wiederholte Folgen aus
   Nehmen, Mengen, Pulverisieren, Wasser, Salben und Destillation; in Harley
   2381 stehen astrologische Tabellen mitten in einem medizinischen
   Rezeptkomplex. [Harley 1736](https://searcharchives.bl.uk/catalog/040-002047567),
   [Harley 2381](https://searcharchives.bl.uk/catalog/040-002048212).
8. Taccolas autographes *De ingeneis* (ca. 1431–33) verbindet knappen Text mit
   vorausgehenden Zeichnungen und behandelt besonders hydraulische Geräte,
   Höhenmessung und Wasserläufe. Das macht eine bildbesitzergesteuerte
   technische Ausschreibung der Bio-Seiten historisch denkbar, ohne sie zu
   erzwingen. [Museo Galileo, Palatino 766](https://brunelleschi.imss.fi.it/genscheda.asp?appl=LIR&chiave=100556&lingua=ENG&xsl=manoscritto).

## Praktische Leseregel für die nächste Runde

Ein Schreiber liest nicht jedes sichtbare Stück als selbständiges Wort. Er
macht schnell Folgendes:

1. Bild oder lokaler Stationsbesitzer liefert den stillen Gegenstand.
2. Die Karte liefert den kurzen Default aus
   `R3_REVISED_COMMON_DICTIONARY.tsv`.
3. `AIIN/AIN/AL/AR/AIR` füllen Maß, Anteil, Ort, Quelle oder Lauf.
4. `DY/B3` schließt den Schritt oder Posten.
5. Eine nicht sauber zerlegbare Karte wird als gelernte Ganzkarte gelesen.
6. Eine Aussage darf über eine physische Zeile weiterlaufen.

So wird aus einer Karte niemals zwangsläufig ein kompletter deutscher Satz.
Die konkrete Übersetzung entsteht aus **kurzem Kartenwert + Bildbesitzer +
Nachbarschaft**.

## Grenzen dieser R3-Runde

- Astro bleibt in dieser technischen Prosastamm-Runde beim lokalen
  Beschriftungs-/Adressmodell; die 395 Astrogruppen wurden nicht rückwirkend in
  diese 173er Prosalexik gezwungen.
- Pflanzenarten, lateinische Lautwerte und Krankheiten wurden nicht aus der
  Form geraten.
- Die konkreten Fassungen sind kreative Werkstattlesungen. Sie können in der
  nächsten Runde ersetzt werden, sobald eine einfachere Gesamtlesung mehr
  Stellen zugleich erklärt.
- Verwendet wurden nur die festen zehn Seiten. `f84` und `f84r` blieben
  vollständig versiegelt.

