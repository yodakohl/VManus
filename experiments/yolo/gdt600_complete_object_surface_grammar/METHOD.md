# GDT600 — Methode

## Aufgabe

Die GDT599-Fassung besitzt bereits für jede Aktion ein Objekt, spricht aber
viele Kombinationen noch als Rohmontage: `Entnimm oder lass`, `Beschicke oder
bereite`, flach gereihte Orts- und Gradangaben, unvollständige Rahmenfragmente
und Q-Sätze mit einem zweiten Übernahmeimperativ. GDT600 baut daraus eine
einheitliche deutsche Oberfläche. Die darunterliegenden Objekt- und
Zustandsfelder bleiben gleich; Verb-, Referenz- und Relationslesungen sind
dagegen bewusst neue, separat ausgewiesene Arbeitshypothesen.

## Fester Bestand

- genau `f75r`, `f77r`, `f81r`, `f81v`, `f82r` und `f83r`;
- 2.272 Hosts, 1.443 Aktionen und 313 Aussagen in unveränderter Reihenfolge;
- jedes GDT599-Objekt, jede Objektklasse, jeder Root, jeder Quellenpointer,
  jeder Referenzmodus und jede Absatzgrenze;
- alle 24 Q-Übergänge, 46 AIIN-Mengenbindungen, drei Override-Fortwirkungen,
  40 lokale Karten, 40 ererbte manuelle Reviews und die 125er Reviewqueue;
- keine neue Seite, Transkription, Segmentierung, Wurzel oder Bilddeutung.

## Renderer

Die 20 Regeln arbeiten nach der bereits abgeschlossenen Objektauswahl:

1. Die sieben lokalen CH+Leitung→FLOW-Entscheidungen W03–W09 werden als eine
   gemeinsame Provenienzregel geführt. Die Objekte bleiben FLOW.
2. CH wählt nach Objekt und sichtbarem Pfad zwischen `entnehmen`,
   `herausnehmen` und `ablassen`; ein Stationskanal zählt wie Kontakt/Leitung.
3. OK wird durchgehend zu `vorbereiten`.
4. T+CONDITION unterscheidet Herkunftszustand und Zielzweck.
5. Quelle und Ziel erhalten rootabhängige Valenz: Herkunft, Empfänger,
   Abflussrichtung, Zweck oder statischer Ort.
6. K mit Quelle, aber ohne sichtbaren Empfänger, wird als Heranführen oder
   Heranbringen gesprochen; 14 nicht-körperliche K-Ziele erhalten den Dativ.
7. Grad-, Modus-, Bad-, Arbeitsort-, Quellen-, Pfad- und Zielangaben werden in
   einer getypten Reihenfolge gesetzt. Nur explizit non-T-governierte Grade
   wechseln von `auf Grad` zu `bei Grad`; T-, gemischte und ungebundene
   Rahmen werden neutral als Gradangabe gesprochen; T-gebundene Rahmen nennen
   ausdrücklich eine Einstellung auf Grad.
8. Alle 153 FRAME-Hosts werden vollständige Imperative. Zehn mit sichtbarem
   Teilnehmer bleiben `Verwende …`, 143 reine Modifikatorrahmen werden
   `Führe den vorangehenden Arbeitsschritt … aus`.
9. Q spricht zuerst die Eingangsaktion und erklärt danach das Resultat zum
   neuen Ansatz. Sieben Folgebezüge — darunter zwei über CARRY/HANDOFF-Aliase
   — heißen `diesen neuen Stationsansatz`.
10. Achtzehn nächste identische Aktionen desselben Arbeitsgangs erhalten
    `erneut`; OL- und Rahmenhosts unterbrechen den Bezug nicht, OT tut es.
11. Probe und Körperteil erhalten passende Determinierer und Genusformen.

## Provenienzkorrekturen

Die alte T06-Bezeichnung `RIGHT_SAME_EVENT_COMPLETED_OR_ROOT_DEFAULT` wird
kausal geteilt. Sechzehn Fälle beziehen sich tatsächlich auf einen bereits
fertigen rechten Host. Fünf Fälle lesen dagegen nur den rechten Root vor und
beziehen ihr Objekt aus `DEFAULT:P:PORTION` beziehungsweise
`DEFAULT:CH:STATION`; der spätere Endzustand darf diese Vorschau nicht
nachträglich als Vererbung erscheinen lassen.

## Kontrolle

Der Validator rekonstruiert die Edition aus den publizierten GDT599-Artefakten
und prüft 326 Bedingungen. Unter anderem werden alle alten TSV-Spalten
zeilenweise, nicht nur über Summen, verglichen. Ein normalisiertes Atommultiset
schützt je Host die nichtverbalen Atome Grade, Modi, Füllung, Bad, Arbeitsort,
Quelle, Ziel, Pfad, Rahmenbezug und sämtliche sichtbar mitgeführten
Teilnehmer. Verbwahl, Referenzrealisierung und Relationsart werden nicht
weg-normalisiert, sondern in eigenen neuen Feldern und Regelzählungen
offengelegt. Q-Resultate werden separat gegen ihre 24 Übergangskarten geprüft.
Sämtliche Ergebnisdateien werden bytegleich neu gebaut.

## Aussagegrenze

Das Ergebnis ist eine bessere und vollständig ausführbare Arbeitssprache für
die aktuelle Theorie. Es bestätigt kein historisches deutsches Klartextwort,
keine Voynich-Lautung und keine reale Rezeptur. Gerade die 972 breiten
STATION-Hosts, 54 Rootdefaults und 125 Reviewfälle bleiben Material für die
nächste Bedeutungsrunde.
