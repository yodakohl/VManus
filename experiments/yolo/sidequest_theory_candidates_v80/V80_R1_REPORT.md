# V80 R1 — Bericht der kanonischen dritten Ausgabe

Status: `PASS__FORMALLY_TEACHABLE__CONCRETE_CONTENT_MASTER_DEPENDENT`.

## Ergebnis

Diese unabhängige R1-Ausgabe bindet die zentral ausgewählten V69/V73–V79-Artefakte
ohne neue Karte, Form, Bedeutung oder Quelle. Sie enthält exakt 173 Karten, 381
Prosaereignisse, 135 Felder, 116 Aussagen, 395 Astrogruppen und 776 vereinte
Gruppen auf den zehn freigegebenen Seiten. f84 und f84r wurden weder gelesen noch
referenziert.

Autonom liest der Lehrling `dcda95c81a5460feb191` nur als `FORMAL_LINK_OR_SLOT` und
`b5fcea1eaed06b2f2291` nur als `FORMAL_RELATION_OR_ENTRY`. `ET?=UND/AUCH?` und
`PER?=DURCH/GEMÄSS?` sind optionale, befragte Meisterglossen aus einer in V77
eingefrorenen Fi1-Kategorie von 1414; sie sind weder durch die Voynichform bewiesen
noch für das Rücklesen nötig. Zwei weitere exakte IDs bleiben formale Nichtwörter.
Alle übrigen 169 Karten haben `EXEMPLAR_VALUE_UNKNOWN`.

## Einfachste Lehrlingsregel um 1420

1. Kopiere Bild/Diagramm und seine freien Räume aus der Vorlage; setze danach Text.
2. Kopiere jede exakte Karte und Grenze, ohne innere Formteile zu deuten.
3. Halte Record, Aussage und sichtbaren Besitzer getrennt; eine Aussage darf die
   physische Linie überschreiten.
4. An einem sichtbaren Besitzerwechsel lösche Stoff, Ziel und Richtung. In B2 sind
   dies exakt E189, E198, E203 und E212.
5. Nur wenn dieselbe exakte Karte am Zeilenende und -anfang, in derselben Aussage,
   beim selben Besitzer und ohne Close steht, bewahre beide sichtbaren Kopien, lies
   aber einmal. Unter 19 Gelegenheiten erfüllt nur E180/E181 diese Regel.
6. Sprich autonom nur die zwei formalen Rollen und zwei Nichtwortkanäle. Für jeden
   konkreten Wert konsultiere den occurrence-gebundenen Eintrag des Masterexemplars.
7. Im Astroblock bleibe im lokalen Rad/Paneel/Slot-Namespace. Erfinde weder Start,
   Richtung, Rotation, f68↔f69-Schlüssel noch einen Prosa-Kartenimport.
8. Bei Unsicherheit kopiere exakt und schreibe `EXEMPLAR_VALUE_UNKNOWN`; ein
   Lehrling darf die Lücke nicht durch Analogie füllen.

## Buchinhalt: genau ein Lead und ein Rivale

Lead: `A_PRACTITIONER_THERAPEUTIC_IATROMATHEMATICAL_COMPENDIUM` — illustriertes therapeutisch-iatromathematisches Praxis- und
Nachschlagekompendium. Rivale: `B_NATURAL_ARTIFICIAL_CELESTIAL_IMAGE_ATLAS_MODELBOOK` — Natur–Kunst–Himmel-Bildatlas oder
Musterbuch. Der eingefrorene V76-Vorsprung beträgt nur 236:235. Deshalb ist der
Lead die konkrete Arbeitsordnung der Edition, nicht eine historische Identifikation.

## Exakt memorierte Vermutungen

- `dcda95c81a5460feb191` → primär `FORMAL_LINK_OR_SLOT`; optional `ET?=UND/AUCH?` nur vom Meister.
- `b5fcea1eaed06b2f2291` → primär `FORMAL_RELATION_OR_ENTRY`; optional `PER?=DURCH/GEMÄSS?` nur vom Meister.
- E180/E181 → zwei sichtbar/ein Quelltoken; lokale Antizipation oder Dittographie.
- Herbal → fünf unbenannte Ganzpflanzenbesitzer mit occurrence-gebundenen Artikeln.
- Bio → lokale Bad-/Anwendungs-/Apparatestationen; kein globaler Fluss.
- Astro → drei lokale Nachschlageinstrumente; Namen, Start und Richtung unbekannt.
- Jedes konkrete Substantiv, Medium, Leiden, Stationsziel und Himmelslabel bleibt
  `[EXEMPLAR:…]`; nichts davon wird aus einer Karte memoriert.

## Widerspruch und Grenze

Der Lead hat keinen sichtbaren Astro→Medizin-Pointer; der Rivale hat keine sichtbare
Natur–Kunst–Himmel-Rubrik. Die Bilder begründen lokale Besitzer, nicht die konkreten
Quellensätze. V79s read-once-Regel besitzt nur ein positives Beispiel. Daher kann
ein Lehrling die 776 Formen rücklesen, aber keinen der konkreten Inhalte ohne
Masterexemplar wiederherstellen.

## Reproduzierbarkeit

`V80_R1_build_canonical_third_edition.py` pinnt alle zentralen Eingaben per SHA-256
und erzeugt sämtliche Tabellen und die lesbare Zehn-Seiten-Ausgabe.
`V80_R1_validate_canonical_third_edition.py` prüft Vollständigkeit, die autonome
Wörterbuchspur, E180/E181, die vier B2-Resets, Astro-Namespaces, Versiegelung und
alle Zählungen. Kein Commit oder Push gehört zu dieser unabhängigen Kandidatenrunde.
