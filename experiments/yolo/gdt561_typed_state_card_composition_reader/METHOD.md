# GDT561 method

## Question

Kann jede der1.656 bereits zugelassenen Karten mit `OT`, `OL` oder `DY` als
vollständige, geordnete Folge kurzer Arbeitswerte gelesen werden, ohne ein Atom
wegzulassen, die Atome umzuschichten oder für eines der402 exakten Rezepte
einen neuen Ganzkartenwert zu lernen? Lassen sich die getrennten Grad-,
Argument- und Relationshüllen aus GDT558–GDT560 positionsgenau einhängen?

## Inputs

- `GDT413` —46-Eintrag-Komponentenwörterbuch;
- `GDT416` —4.576 kontextuelle Imperativzeilen der alten26 Seiten;
- `GDT539` —546 kontextuelle Ereigniszeilen der aktuellen vier Seiten;
- `GDT557` —1.870 Zustandsmarkerstellen in1.656 eindeutigen Karten;
- `GDT558` —333 Gradzuteilungen;
- `GDT559` —390 Argumentzuteilungen;
- `GDT560` —216 Relationszuteilungen.

## Method

1. Mehrfachzeilen des GDT557-Atlas werden nur über `event_id` verdichtet; für
   jede Karte müssen Rezept, Oberfläche, Position, Grenze und Kontext identisch
   bleiben.
2. Die tatsächlich vorkommenden36 Atome werden in sieben sichtbare Rollen
   aufgeteilt: Handlung, Grad, Argument, Relation, Zustandssteuerung,
   Formsteuerung und Lokal-/Klassenzeichen. `OT/OL/DY` werden dabei als
   Zustandssteuerung geführt; `DY` erhält GDT557s Arbeitslesung
   `ABSCHLIESSEN`. Alle übrigen Werte werden unverändert aus GDT413 übernommen.
3. Jede Atomstelle wird in geschriebener Reihenfolge dreifach ausgegeben:
   `ATOM{ROLLE=WERT}`, als reine Wertfolge und als kurzes deutsches Fragment.
   Strukturzeichen bleiben ausdrücklich Strukturzeichen.
4. Jedes der402 exakten Rezepte erhält einen einzigen vollständigen
   Rezeptdefault. Dieser ist eine Zusammensetzung seiner Atome, kein gelernter
   Ganzkarteneintrag.
5. Die1.656 Karten werden positionsgenau mit GDT416 oder GDT539 verbunden.
   Deren flüssige Kontextzeile bleibt ein eigener Kanal und darf die atomare
   Spur nicht ersetzen.
6. Alle939 spezialisierten Zuteilungen aus GDT558–GDT560 werden über Ereignis,
   Atom und Atomposition verbunden. Der gemeinsame Bestand umfasst787 Karten.
7. Rezepte mit derselben ungeordneten Atommenge werden gruppiert. Wo mehrere
   Reihenfolgen vorkommen, werden alle Varianten als Ordnungszeugen publiziert;
   kein Atom wird für einen vermeintlich schöneren Satz sortiert.
8. Der Validator rekonstruiert Wörterbuch, Karten, Rezepte, Rollen, Trägerlinks
   und Ordnungsfamilien direkt aus den sieben Quellen und prüft einen
   bytegleichen Neubau.

## Decision rule and claim ceiling

Der Leser gilt als vollständig, wenn alle1.656 Karten, alle4.684 Atomstellen
und alle402 Rezepte einen nichtleeren Default besitzen, alle939 Trägerlinks an
derselben Atomposition anschließen und jede beobachtete Reihenfolge erhalten
bleibt.

Das Ergebnis ist eine kreative Arbeitskomposition der bereits gesetzten Werte.
Es bestätigt weder Klartext noch historische Sprache, Syntax, Codebuch,
Lautwert oder Gegenstand. Es ändert keine Seite, Oberfläche, Segmentierung,
Rezeptfolge, Wurzelbedeutung oder Aussagegrenze und lizenziert keine neue Form.
