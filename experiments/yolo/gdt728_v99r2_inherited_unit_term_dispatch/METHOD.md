# GDT728 method

## Frage

Können alle geerbten globalen `Dosis`-/`Dosen`-Formulierungen des vollständigen
V99-Wörterbuchs als exakte Ganzwortfamilien in `Portion`, `Teil`, `Maß`,
`Wert` oder `HOLD` dispatcht werden, ohne aus `d`, `dain` oder `daiin` ein
freies Mengenwort zu machen?

## Festes Inventar

Der Ausgangsbestand ist GDT727s vollständiges Wörterbuch mit 1.586 Readings.
Im globalen V48-Layer tragen genau 60 Readings in beiden semantischen
Ausgabefeldern Dosiswortlaut; sie summieren sich auf 293 beobachtete
Vorkommen. Die alte Formklasse zerfällt in:

- 24 gezählte Plurale,
- 18 singuläre Arbeitsobjekte,
- 11 römisch indizierte Achsen,
- sechs Komposita und
- eine redundante Form `eine Portion als Dosis`.

Alle 60 Reading-IDs, Oberflächen sowie Alt- und Neutexte stehen vor dem Lauf
explizit in `src/V99R2_60_UNIT_TERM_SPECS.tsv`. Der Generator entdeckt keine
Änderungsziele durch Suchen-und-Ersetzen. Der Suchbestand dient nur als
Vollständigkeitsprüfung gegen die vorregistrierte Liste. Dadurch bleiben
`dosg` als Oberflächenidentität und legitime Erwähnungen in Evidenzfeldern
unberührt.

## Dispatch

1. Echte `Dosis` oder `Gabe` würde eine Verabreichung, einen Patienten oder
   eine Posologie verlangen. Keine der 60 Arbeitslesungen besitzt das.
2. Ein sichtbarer Stoff-, Produkt- oder Arbeitskopf mit zählbarer Menge erhält
   den neutralen Default `Portion`. Das betrifft 55 Ganzformen. Bei den elf
   römischen Altformen wird II/III nur dann kardinal als zwei/drei Portionen
   realisiert, wenn das exakte Ganzwort bereits einen Stoff- oder
   Zubereitungskopf trägt.
3. `dolas` erhält `Teil`, weil sein geerbter exakter Ganzformpfad den
   Teil-/Verhältnislink `A_PART_OR_LINK` trägt. Gleichheit und Zahl der Teile
   bleiben ausdrücklich offen.
4. `doly` erhält `Maß`, weil es im geerbten Messfamilienregister als exakte
   Abguss-Ganzform steht. Weder `dol` noch eine historische Einheit werden
   daraus exportiert.
5. `odan`, `odain` und `odaiin` bleiben `Wertstufe I–III`: GDT627 klassifiziert
   `oda/od` als offenen Wertkopf, der weder Grad noch Menge global auswählt.
6. `HOLD` wäre der Fallback ohne ausgabefähigen Default. Keine Form braucht ihn
   in dieser explorativen Runde; jede Zeile behält jedoch den stärksten Rivalen
   und ihren offenen Slot.

Der Dispatch verändert nur die beiden semantischen Texte und fünf
Lineage-/Auditfelder der 60 Zielzeilen. Scores, Confidence-Level, positive und
negative Evidenz, Scope, Exportrechte, Struktur-Tags, Identitäten und
Komponentenkarten bleiben unverändert.

## Historische Konventionsvergleiche

Die Quellen dienen ausschließlich als Vergleich für Rezeptmengen, nicht als
Voynich-Wortgleichungen:

- Theodoricus trennt eine in drei Teile geteilte Zutat von ihrer späteren
  Verwendung in einer Tränke ([Mulomedicina I.16.19](https://d-nb.info/1279095032/34)).
- Ein mittelbairisches Rezept der ersten Hälfte des 15. Jahrhunderts nennt
  konkrete `lott`-Gewichte ([GNM Hs 1481a](https://kdih.badw.de/datenbank/handschrift/39/2/5)).
- Das neapolitanische *Liber de coquina* von 1308–1314 nennt Zutaten in
  Unzen ([Rezept 14](https://corpus.atliteg.org/opera/liber-de-coquina-a/93)).
- Der Katalog zu BL Add MS 41486 überliefert ein Rezept mit `tres partes`
  ([British Library](https://searcharchives.bl.uk/catalog/032-002085127)).
- Ein Überblick zur mittelalterlichen Pharmakologie trennt Zutatenanteile,
  Herstellung, Verabreichung und Dosierung
  ([NCBI Bookshelf](https://www.ncbi.nlm.nih.gov/books/NBK606146/)).

Alle fünf Vergleichszeilen haben `voynich_relation_credit=0` und
`historical_confirmation=H0_NONE`.

## Validierung und Reichweite

Der unabhängige Validator importiert den Generator nicht. Er rekonstruiert den
60er-Zielbestand, prüft 293 Vorkommen und 61 entfernte Dosis-Tokens pro
semantischem Feld, kontrolliert die erlaubten Änderungsfelder und verlangt
Byteparität für alle 324 aktiven sowie 1.202 nicht betroffenen globalen
Readings. Fünf aktive Reader-Artefakte werden nur gehasht und nicht neu
geschrieben.

V99R2 ist eine explorative deutsche Arbeitsedition. Es bestätigt keine
Klartextsprache, Lautung, historische Maßeinheit, Zutat, Krankheit oder
Behandlung und gibt keinem Teilstring einen freien Wert. Es öffnet keine neue
Seite, kein Bild und keine Transkription; `f84` und `f84r` bleiben verboten.
