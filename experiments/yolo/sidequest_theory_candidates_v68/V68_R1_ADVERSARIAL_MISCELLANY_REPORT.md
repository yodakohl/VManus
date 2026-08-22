# V68 R1 — vollständige nichtmedizinische Gegenedition

## Urteil

Der stärkste einheitliche Rivale ist ein **illustriertes Pflanzenmaterial-, Badhaus- und Arbeitskalender-Miszellaneum**:

```text
Herbal: Pflanzenzusätze, Farben, Reiniger, Binder und Vorräte
Bio:    Beckenbeschickung, Filter, Leitungen, Rücklauf, Wartung und Dienst
Astro:  Arbeitswahl, Monatsadressen und seitenlokale Qualitätsregeln
```

Unter der vor der Auswertung eingefrorenen Sechskriterien-Rubrik gewinnt der Rivale numerisch **371:370 von je 420 Punkten**. Das ist ein substantielles Unentschieden: Eine einzige um einen Punkt andere historische oder ikonographische Bewertung kehrt das Ergebnis um. Der Rivale besiegt damit nicht die formale Architektur, sondern zeigt, dass sie inhaltlich domain-neutral bleibt.

Status: vollständige kreative Gegenedition, keine Übersetzung. Bestätigte Lexeme, Lautwerte und Klartextklauseln bleiben null.

## Unveränderte Schichten

`V68_R1_776_GROUP_NONMEDICAL_LEDGER.tsv` übernimmt für 776/776 Gruppen unverändert:

- exakte Prosa-joint_tuple_id beziehungsweise lokale Astro-Adresse;
- formalen Slot, V60-Mnemonic oder UNKNOWN;
- V62-Registerzustand und -übergang;
- V61/V63-Kontext, Feldstatus und Renderer;
- Seitennamespace und sichtbare Oberfläche.

Neu ist ausschließlich die Spalte `nonmedical_rival_local_expansion`. Sie ist als record- oder seitenlokaler Exemplartext markiert und darf nicht ins Kartenwörterbuch zurückfließen. Die 395 Astrogruppen erhalten weder Prosaform noch portables Mnemonic. f68r1 und f69v bleiben unverbunden.

## Vierzehn vollständige Units

Die vollständigen deutschen Texte, ausführbaren Workflows, Lehrzwecke sowie expliziten Bild- und Geschichtsargumente stehen in `V68_R1_14_UNIT_ADVERSARIAL_EDITION.tsv`.

| Unit | nichtmedizinischer Default | Rivale | Iatromedizin | lokales Urteil |
|---|---|---:|---:|---|
| H1 | Wurzelkraut als Scheuer- und Badhauslauge | 26 | 28 | Iatromedizin |
| H2 | zwei Blütenfraktionen für Farbe und Ölpaste | 26 | 28 | Iatromedizin |
| H3 | Duftblüten für Spülwasser und Pflegeöl | 25 | 28 | Iatromedizin |
| H4 | Breitblatt-Reiniger und gebundene Werkstattpaste | 26 | 28 | Iatromedizin |
| H5 | Klebkraut für Fleckprobe, Etikettenleim und Vorrat | 23 | 26 | Iatromedizin |
| B1 | morgendliche Badhausbeschickung und Grundkreislauf | 28 | 27 | Rivale |
| B2 | gewöhnliches Sitz- und Waschbad | 28 | 28 | gleich |
| B3 | langer Reinigungs-, Rücklauf- und Wiederbeschickungszyklus | 28 | 27 | Rivale |
| B4 | Filtertuch-, Beckenrand- und Leitungswartung | 28 | 26 | Rivale |
| B5 | zeitlich gehaltener Wärme- und Übergabeposten | 28 | 23 | Rivale |
| B6 | kalter Filter- und Zielübergabenachtrag | 28 | 23 | Rivale |
| A1 | 7×12 Werkstatt- und Qualitätswahlscheibe plus acht Gates | 25 | 26 | Iatromedizin |
| A2 | Zentrum plus 28 Adressen eines Monatsdienstplans | 26 | 26 | gleich |
| A3 | unabhängige Folge aus 28 Werkstattregeln | 26 | 26 | gleich |

Damit gewinnt Iatromedizin sechs Units, der Rivale fünf; drei bleiben gleich. Die Punktesumme kippt wegen der großen technischen Vorteile in B5 und B6 um einen Punkt zum Rivalen.

## Ausführbarer Gesamtworkflow

1. Der Pflanzenstoffschreiber legt fünf getrennte Artikel an: gewinnen, teilen, prüfen, filtern, binden und lagern. Keine Pflanzenart und kein Produkt ist Kartenwert.
2. Der Badhausmeister eröffnet jeden der sechs Bio-Records mit neuem OWNER und zurückgesetzten ACTIVE/TARGET/PREVIOUS-Registern.
3. Er beschickt Becken, temperiert, filtriert, leitet, hält, lässt ab, spült und übergibt ausschließlich dort, wo ausgewählter Slot oder lokales Exemplar dies fordert.
4. Der Materialschrank kann Pflanzenzusätze für den Badebetrieb liefern, doch diese Verbindung ist nur der Zweckrahmen des Miszellaneums; keine sichtbare Karte verknüpft H mit B.
5. A1 wählt aus sieben Werkstatttagen, zwölf Arbeitsklassen und acht Qualitätsbedingungen eine erlaubte, verkleinerte oder verschobene Arbeit.
6. A2 verwaltet einen separaten Monatsdienstplan mit 28 räumlichen Adressen.
7. A3 liefert 28 unabhängige Regeln für Ernte, Trocknung, Färben, Filtern, Heizen, Badedienst, Reinigung und Vorrat.
8. A2 und A3 werden niemals paarweise gelesen; Start und Drehrichtung bleiben exemplarabhängig.

Der Lehrzweck ist stärker als beim medizinischen Inhalt: Ein Lehrling kann die Bio-Units als konkrete Bedien- und Wartungszettel ohne Diagnose lernen. Im Herbal-Register ist derselbe Vorteil schwächer, weil fünf unterschiedliche technische Produktklassen zusätzlich memoriert werden müssen.

## Symmetrische Bewertung

`V68_R1_FROZEN_SYMMETRIC_RUBRIC.tsv` vergibt je Unit und Theorie gleichgewichtet 0–5 Punkte für:

1. formale Treue;
2. sichtbare Ikonographie;
3. ausführbaren Workflow;
4. Annahmeökonomie;
5. historische Gattung;
6. registerübergreifenden Zweck.

Beide Theorien erhalten überall 5/5 für formale Treue, weil sie dieselben Karten und Register benutzen. Jeder konkrete, nicht sichtbare Gegenstand, Stoffwert, Zweck oder externe Astro-Label kostet genau eine Annahmeeinheit. `V68_R1_ASSUMPTION_COSTS.tsv` veröffentlicht alle 121 Einzelkosten: 55 beim Rivalen, 66 bei der iatromedizinischen Fassung. Die niedrigere Rivalenkostenlast wird teilweise durch schwächere Herbal- und Astro-Gattungstreue aufgehoben.

Registersummen:

| Register | Rivale | Iatromedizin | Vorsprung |
|---|---:|---:|---:|
| Herbal | 126 | 138 | Medizin +12 |
| Biological | 168 | 154 | Rivale +14 |
| Astro | 77 | 78 | Medizin +1 |
| Gesamt | **371** | **370** | Rivale +1 |

Diese Punkte messen interne Editionsqualität, nicht die Wahrscheinlichkeit einer Entzifferung.

## Ikonographie und Geschichte

**Herbal:** Die Bilder tragen Pflanzenbesitzer und Teile. Sie zeigen weder Alaun, Asche, Wachs, Tuch, Leder noch Badhausprodukte. Illustrierte Materia medica ist deshalb die spezifischere historische Bild-Text-Gattung. Pflanzenfarben, Laugen, Duftöle und Binder sind zwar spätmittelalterlich plausible Werkstattklassen, ihre Bündelung unter genau diesen fünf Bildern bleibt Zusatzannahme.

**Biological:** Figuren, Becken, Verbindungen und Auslässe passen gleichermaßen zu Badenden und zu einem bedienten Badhaus. B1–B4 können Therapie und gewöhnlichen Dienst tragen. B5/B6 besitzen dagegen so wenig Körperargument, dass Übergabe-, Wärme-, Filter- und Vorratszettel klar billiger sind als Patient und Heilziel. Ein moderner geschlossener hydraulischer Plan wird ausdrücklich nicht behauptet.

**Astro:** 7/12/8 und Zentrum+28 besitzen spezifischere planetarisch-zodiakale beziehungsweise Mondhaus-Parallelen als eine generische Arbeitsrota. Der Arbeitskalender gewinnt nur an semantischer Sparsamkeit. Er darf weder eine unsichtbare Legende noch einen A2↔A3-Schlüssel behaupten.

## Stärkste Widersprüche

Der vollständige wechselseitige Widerspruchsvergleich steht in `V68_R1_CONTRADICTION_LEDGER.tsv`.

- Gegen den Rivalen: Kein Werkzeug oder fertiges Handwerksprodukt erscheint auf den Herbal-Bildern; H2–H5 verlangen erfundene Farbe-, Duft-, Binder- oder Klebequalitäten.
- Gegen den Rivalen: A1s sieben Werkstatttage × zwölf Arbeitsklassen sind weit generischer als die historische Planeten×Tierkreis-Familie.
- Gegen den Rivalen: B3s Wiederverwendung geklärter Badflüssigkeit kann eine moderne hydraulische Überlesung sein.
- Gegen Iatromedizin: Krankheit, Körperziel und Therapie sind in fast allen Bio-Records nicht sichtbar und keine Kartenwerte.
- Gegen Iatromedizin: B5/B6 funktionieren vollständig als technische Nachträge ohne Patient.
- Gegen beide: Die 657 exemplarabhängigen Gruppen bleiben ohne Masterexemplar semantisch unlesbar; ein verlustfreier Ledger-Roundtrip bestätigt nur Ablage, nicht Inhalt.

## Schluss

Der Rivale besteht den Drucktest und gewinnt die eingefrorene Punktzahl hauchdünn. Das faire Urteil bleibt dennoch **inhaltlich unentschieden**:

- Iatromedizin besitzt die stärkere Herbal- und spezifische Astro-Gattung.
- Das nichtmedizinische Miszellaneum besitzt die stärkere apparative Bio-Ausgabe und elf weniger konkrete Annahmen.
- Keine Karte unterscheidet beide Welten.

Lehrregel: **Gleiche Karte und gleicher Slot dürfen verschiedene lokale Werkstattprosa tragen; entschieden wird nur durch offen ausgewiesenes Bild, Geschichte, Ablauf und Annahmekosten.**
