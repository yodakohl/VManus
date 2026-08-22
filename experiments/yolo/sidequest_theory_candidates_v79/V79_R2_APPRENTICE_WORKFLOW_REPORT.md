# V79 R2 — historische Lehrlingsprobe und Widerspruchsreparatur

## Ergebnis

Der formale Kopier- und Rückleseablauf ist mit einem Masterexemplar lehrbar;
eine konkrete Bedeutungsfortsetzung ohne Masterexemplar ist es nicht. Alle 19
aussageninternen physischen Zeilenübergänge wurden vor jeder Bedeutungsdeutung
geprüft. Nur **E180→E181** erfüllt gleichzeitig dieselbe exakte Karte,
denselben sichtbaren Owner, keinen `Close` und keinen Owner-Reset.

Für dieses eine sichtbare Paar gilt daher eine **lokale
anticipation/carry/dittography-Hypothese**: Beide Schriftbilder bleiben erhalten,
aber die erste Kopie wird nicht als zweiter Quelltoken gelesen. Das ist **kein
belegter Standard-Catchword** und keine allgemeine Kustodenregel. Absichtliche
Vorausnahme und versehentliche Dittographie bleiben bei einem einzigen Beispiel
beobachtungsmäßig unentscheidbar.

Die interne Rückleseentscheidung lautet:

- `dcda…`: `FORMAL_LINK`; `ET?` nur, falls ein Master/Schlüssel genau diese
  Zuordnung vorgibt.
- `b5fcea…`: `FORMAL_RELATION_OR_ENTRY_MARK_WITH_ENTRY_BIAS`; `PER?` nur,
  falls ein Master/Schlüssel genau diese Zuordnung vorgibt.

Es wird keine neue portable Wortbedeutung eingeführt.

## Kompakter Lehr- und Kopierworkflow

1. Der Meister weist Seite, lokalen sichtbaren Owner und Quellstelle im
   Exemplar zu. Der Lehrling beginnt ohne mitgeschleppte Substanz-, Ziel- oder
   Richtungswerte.
2. Pro Position wird die exakte sichtbare Karte kopiert. Ihre Form liefert
   allein keine konkrete Handlung oder Sache; diese kommt aus dem
   Masterexemplar.
3. `Close` beendet die formale Aussage. Ein physisches Zeilenende tut dies
   nicht automatisch.
4. Ein sichtbarer Owner-Bruch löscht lokale Argumente auch dann, wenn die
   rekonstruierte Aussage grammatisch weiterläuft.
5. An jedem aussageninternen Zeilenübergang werden vorsemantisch vier Fragen
   geprüft: gleiche exakte Karte, gleicher Owner, kein `Close`, kein Reset.
6. Nur wenn alle vier Antworten positiv sind, dürfen zwei sichtbare Kopien als
   ein Quelltoken rückgelesen werden. Die Randkopie bleibt im Faksimilebestand
   und wird nicht gelöscht.
7. Der Lehrling darf eine solche Doppelung aus einem Masterexemplar übernehmen,
   aber nicht selbst an neuen Stellen erzeugen. Bei jeder abweichenden Karte
   werden beide Token gelesen.
8. Zur Kontrolle wird rückwärts geprüft: Karte, Owner, Reset, `Close` und
   lokale Slotmitgliedschaft müssen exakt wiedergewonnen werden. Inhaltliche
   Wörter dürfen ohne Master nicht ergänzt werden.

Das Verfahren ist kurz genug für Werkstattunterricht: fünf sichtbare Zustände
(Karte, Owner, Zeilenkante, `Close`, Reset) plus eine konservative
Ausnahmeregel. Seine Reichweite bleibt lokal; aus einem Treffer folgt keine
historische Werkstattkonvention.

## Vollständiger Übergangsaudit

Die 116 ausgewählten Aussagen enthalten 18 zeilenübergreifende Aussagen und 19
physische Übergänge. Das Ergebnis ist:

- 1 Übergang mit Read-once-Treffer: E180→E181;
- 14 weitere Übergänge beim selben Owner, aber mit verschiedenen exakten
  Karten;
- 4 Übergänge mit sichtbarem Owner-Reset: E202→E203, E263→E264,
  E290→E291 und E355→E356.

Damit produziert die sichtbare Regel im eingefrorenen Panel keinen zweiten
Treffer. Die vollständigen 19 Zeilen stehen in
`V79_R2_19_LINE_TRANSITION_AUDIT.tsv`. Sie ist eine lokale Reparatur des
beobachteten Doppelbilds, keine generative Entzifferungsregel.

## H2 — vollständige Vorwärts- und Rückwärtsspur

H2 umfasst E015–E038, 24 sichtbare Ereignisse in drei Aussagen unter demselben
unbenannten Ganzpflanzen-Owner.

**Vorwärts:** E015–E023 bilden den ersten Exemplarblock; E022 bleibt ein
formaler Nichtwort-Prompt. E024–E031 bilden den zweiten Block. E027 und E029
stehen in einer wiederholten Verknüpfungskette, aber intern ist nur ihre
`FORMAL_LINK`-Funktion wiedergewinnbar. E030 bleibt ein weiterer formaler
Prompt. E032–E038 bilden den dritten Block. Es gibt innerhalb H2 keinen
Owner-Reset und keinen Read-once-Zeilenübergang.

**Rückwärts:** E038→E015 stellt dieselben 24 Karten, drei Aussagen, denselben
Owner und dieselben formalen Prompt-/Linkstellen wieder her. Es stellt nicht
die in V78 bracketierten Pflanzen-, Mediums- oder Handlungswerte her. Die
Lesung `ET?` ist deshalb gegenüber einem stillen/formalen Link intern nicht
identifizierbar. Der historische Befund, dass `et` als Wort in einem realen
Schlüssel von 1414 vorkommen kann, attestiert nur die zeitgenössische
Möglichkeit der Kategorie, nicht die Zuordnung zu `dcda…`.

## B2 — vollständige Vorwärts- und Rückwärtsspur

B2 umfasst E167–E228, 62 sichtbare Ereignisse und fünf lokale Ownerblöcke:

1. E167–E188: oberes Paar mit Zylinder. E180 am Ende von f82r.3 und E181 am
   Anfang von f82r.4 sind dieselbe exakte Karte in derselben Aussage und beim
   selben Owner. Sichtbar werden beide kopiert; in der Quellzählung gilt
   E180=0 und E181=1.
2. E189–E197: neuer mittlerer Apparate-Owner; Argumente werden bei E189
   gelöscht.
3. E198–E202: neue unaufgelöste mittlere Station; Reset bei E198.
4. E203–E211: neues unteres Mehrfigurenbecken; Reset bei E203, obwohl
   E202→E203 innerhalb derselben Aussage liegt.
5. E212–E228: neuer unterer Randstations-Owner; Reset bei E212.

**Vorwärts:** Der Lehrling folgt diesen fünf lokalen Blöcken und übernimmt
bracketierten Inhalt nur aus dem Master. **Rückwärts:** An E212, E203, E198 und
E189 muss er die Argumente jeweils abbrechen; kein Seitenfluss darf durch die
vier Brüche hindurch erfunden werden. E180/E181 ergeben genau einen
Relation-/Entry-Token.

Nach der lokalen Zusammenlegung bleiben acht Quellvorkommen von `b5fcea…`:
sechs stehen am Feld-/Aussageeingang, zwei medial (das zusammengelegte
E180/E181 und E219). Das stützt eine Entry-Tendenz, widerlegt aber einen reinen
Resetmarker. Intern gewinnt daher die breitere formale Relation-/Entry-Klasse;
die Präpositionslesung `PER?` bleibt ohne Master unbelegt.

## f69v links — 28 lokale Slots, keine erfundene Lesereihenfolge

Die linke Scheibe enthält 28 lokale Slots und 33 sichtbare Gruppensegmente.
Fünf Slots enthalten je zwei Segmente; die übrigen 23 je eines. Die komplette
Vorwärtsspur kopiert A3:G108–A3:G140 jeweils in denselben lokalen Slot. Die
Rückwärtsspur setzt Mehrsegment-Labels wieder zusammen und ordnet alle 33
Segmente ihren 28 sichtbaren Besitzern zu.

Die Reihenfolge L01–L28 ist nur eine redaktionelle Vollständigkeitsadresse. Sie
belegt weder Start, Rotation, Richtung, Rang, Namen noch einen 28-stufigen
Zyklus. Ein Lehrling kann mit Master die Beschriftung reproduzieren; ohne
Master gewinnt er nur Slot- und Segmentmitgliedschaft zurück.

## Historische Plausibilität und Begrenzung

Spätmittelalterliche Kopisten arbeiteten durch engen Blickwechsel zwischen
Vorlage und Kopie; dabei sind Wiederaufnahmefehler und Dittographien ein
plausibler Mechanismus. Lehrmaterial zur Handschriftenüberlieferung beschreibt
Dittographie ausdrücklich als Wiederbeginn mit einem schon kopierten Wort.
Reguläre mittelalterliche Catchwords/Kustoden dienen dagegen typischerweise
der Lagen- oder Seitenfolge. Der Katalogeintrag zu British Library Add MS
54243 (Mitte 15. Jh.) vermerkt reguläre Catchwords im Zusammenhang mit der
Lagenstruktur. Das ist strukturell nicht dasselbe wie E180/E181 mitten in einer
aussageninternen physischen Zeilenfolge.

Quellen zur Mechanismenkalibrierung:

- British Library, [Add MS 54243](https://searcharchives.bl.uk/catalog/040-001959734),
  Katalogbeschreibung und Lagen-/Catchword-Angaben.
- Daniel Wakelin, [“This is the copy”](https://www.cambridge.org/core/books/immaterial-texts-in-late-medieval-england/this-is-the-copy/316C1A3018F584D5D3C78990FAA14805),
  in *Immaterial Texts in Late Medieval England*, zum Nahprozess des Kopierens.
- Harvard Chaucer, [Textual Instability in a Manuscript
  Culture](https://chaucer.fas.harvard.edu/textual-instability-manuscript-culture),
  zu Kopierfehlern, Augensprüngen und Korrektur.
- Goucher College, [How do mistakes enter a
  manuscript?](https://faculty.goucher.edu/eng330/how_do_mistakes_enter_manuscript.htm),
  zur Dittographie als Wiederholung beim Wiederansetzen.

Diese Quellen kalibrieren nur einen möglichen Kopiermechanismus. Keine davon
belegt die konkrete Voynich-Doppelung als Catchword, Dittographie oder
absichtliche Vorausnahme.

## Fehlerfälle und harte Grenzen

- Verschiedene exakte Karten werden nie wegen bloßer Zeilennähe
  zusammengezogen.
- Owner-Reset oder `Close` blockiert Read-once auch bei hypothetischer
  Formgleichheit.
- Eine Wiederholung außerhalb genau desselben aussageninternen
  Zeilenübergangs wird nicht dedupliziert.
- Der Lehrling darf die lokale Doppelung nicht auf neue Stellen übertragen.
- Ein Master kann eine vorhandene Doppelung als zwei Schriftbilder/einen
  Quelltoken vorgeben; ohne Master ist ihre Absicht nicht entscheidbar.
- Astro-Vollständigkeitsreihenfolge ist keine historische Instrumentrichtung.
- Ohne Masterexemplar sind konkrete Substanzen, Handlungen, Himmelsnamen und
  Wörter nicht rückgewinnbar.

## Artefakte und Status

- `V79_R2_19_LINE_TRANSITION_AUDIT.tsv` — 19/19 Übergänge;
- `V79_R2_COMPLETE_FORWARD_BACKWARD_TRACES.tsv` — 119 sichtbare Spurzeilen:
  H2 24, B2 62, f69 links 33;
- `V79_R2_REPAIR_DECISIONS.tsv` — sieben eingefrorene Entscheidungen;
- `V79_R2_RESULT.json` und `V79_R2_VALIDATION.json` — maschinenlesbarer
  Abschluss.

**Status: PASS für formales Kopieren/Rücklesen mit Master; FAIL für konkrete
semantische Fortsetzung ohne Master.** Das Ergebnis ist ein historisch
kalibriertes Werkstattmodell, keine Entzifferung oder Übersetzung.
