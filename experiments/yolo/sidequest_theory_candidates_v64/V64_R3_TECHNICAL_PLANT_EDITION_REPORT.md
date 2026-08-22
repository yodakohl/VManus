# V64 R3 — Technische Pflanzenrohstoff-/Registeredition

## Ergebnis

Die Alternativedition ist vollständig: **5 Records, 19 Aussagen, 20 Felder und 100 Ereignisse**. Sie liest die Herbal-Seiten als bebildertes Rohstoff- und Chargenregister für Pflanzenmaterial: Teile sammeln, waschen, mazerieren, seihen, abteilen, einen Ansatz beziehungsweise eine vorige Charge aufnehmen, einen lokalen Materialtest ausführen und Produkte oder Referenzfraktionen lagern.

Das ist eine kreative lokale Edition, keine Entzifferung. Die V60-Werte bleiben exakt fixiert; die V61-Grenzen, V62-Register und V63-Status werden unverändert übernommen. Von 100 Ereignissen besitzen nur 29 eine lizenzierte V63-Schablone, 71 bleiben `EXEMPLAR_ONLY`. Alle Herbal-Felder bleiben **0 `UNIQUE`, 15 `AMBIGUOUS`, 5 `UNPARSED`**; die 19 Aussagen bleiben 14 `AMBIGUOUS`, 5 `UNPARSED`.

## Schichtenvertrag

```text
opake joint_tuple_id
  -> vorhandener formaler Prompt (nur Slotoperation, kein Bedeutungswort)
  -> fixer V60-Exact-Wert, falls vorhanden
  -> unveränderter V62-Zustandsumschlag
  -> unveränderter V63-Status
  -> sichtbarer V53-Besitzer als stilles Recordargument
  -> V64-Pflanzenoperation als lokale Hypothese, niemals Kartenglosse
```

Die Herbal-Anker sind: `MASS?` 9, `ANSATZ?` 5, `ANWENDEN?` 3, `BEREIT?` 3 sowie `VORIGES?`, `KLAR?`, `ZIEL?`, `ANTEIL?` je 1. Dazu treten formale Slotprompts, ohne semantische Vererbung. Wasser, Pflanzenteil, Mazeration, Sieben, Gefäß, Musterstreifen, Farbauszug, Mucilage und Lagerart sind ausdrücklich lokale Argumente.

## Fünf vollständige Records

| Record | bestes festes Bildargument | technische Prozess-/Produktlesung | lokale Feldstatus | Urteil |
|---|---|---|---|---|
| H1 | skabiosen-/Teufelsabbiss-nahe Wiesenpflanze | Wurzelstock waschen, schneiden und mazerieren; Prüfportion nach Maß am Musterstreifen einsetzen, Rest lagern; zweiten Auszug verknüpfen und freigeben | 2 A | iatromedizinisch |
| H2 | obere Teile derselben skabiosenartigen Pflanze | Pressauszug eröffnen; frühe und späte Erntecharge über `LINK_ACTIVE`, `VORIGES?` und `MASS?` als Vergleichsserie führen, gleich seihen und lagern | 3 A | technisch, nur intern |
| H3 | kleine Schattenpflanze, Veilchen als Leitbild | Blüten/Kraut trennen, Wasserextrakt zweimal seihen und am `KLAR?`-Gate schließen; Referenzblüte, dosierte Filtratserie und separater Blattauszug | 3 A / 1 U | iatromedizinisch |
| H4 | breitblättriges Kraut; Allium/Wegerich offen | zwei gemessene Blattflotten und Presskuchen in drei Commits erzeugen, danach per Relationsslot/Ansatz als Paarposten vergleichen und lagern | 3 A / 1 U | technisch, nur intern |
| H5 | feuchtlandliebende drüsige/borstige Pflanze; Sonnentau-Rivale | kleine Klebflüssigkeitscharge auf zwei Prüfflächen einsetzen; Teile getrennt trocknen, Blatt lagern, Frischrest als Klebmasse und Blüte als Referenzlos buchen | 4 A / 3 U | Gleichstand |

`A = AMBIGUOUS`, `U = UNPARSED`. Die vollständigen deutschen Artikel stehen in `V64_R3_5_RECORD_PLANT_EDITION.tsv`; sämtliche 20 Feldtexte und 100 geschichteten Ereignislesungen stehen in den entsprechenden Volltabellen.

## Ausführbare Prozessgraphen

```text
H1 OWNER -> F001 COLLECT/WASH/CUT/MACERATE/APPLY/MASS/STORE
         -> F002 RESUME/LINK/READY                         [kein Commit]

H2 OWNER -> F003 PRESS/MASS -> F004 EARLY/LINK/PREVIOUS/MASS
         -> F005 LATE/PARALLEL/STRAIN/COMPARE/STORE       [kein Commit]

H3 OWNER -> F006 SORT/MACERATE/STRAIN/CLEAR [COMMIT]
         -> F007 RESERVE -> F008 DOSE/MASS -> F009 EXTRACT/READY/STORE

H4 OWNER -> F010 STANDARD/MASS/MACERATE [COMMIT]
         -> F011 MASS/PRESS/STRAIN [COMMIT]
         -> F012 PARALLEL/WASH/STRAIN [COMMIT]
         -> F013 MASS/TARGET_SLOT/LINK/COMPARE/STORE

H5 OWNER -> F014 PART/MASS -> F015 SOAK/APPLY/TARGET
         -> F016 APPLY/DRY [COMMIT] -> F017 PART/DRY
         -> F018 RESUME/STORE -> F019 FRESH_BINDER/STORE
         -> F020 SELECT_PART/MASS
```

Der Graphexecutor folgt der Feldreihenfolge, wendet an jeder Aussage zuerst den ausgewählten V62-Übergang an, führt nur lizenzierte V63-Schablonen aus, expandiert übrige Positionen lokal und committet ausschließlich an beobachteten Terminalfeldern. Die vollständig adressierten Knoten-/Kantenpfade stehen in `V64_R3_5_RECORD_PROCESS_GRAPHS.tsv`.

## Vergleich mit der iatromedizinischen Edition

Die 19 gleich abgegrenzten Aussagen werden einzeln in `V64_R3_19_STATEMENT_COMPARISON.tsv` gegenübergestellt. Eng auf Ablauf und Register bezogen gewinnt die technische Lesung 8 Aussagen, die iatromedizinische 5; 6 bleiben gleichwertig. Besonders stark ist der technische Rivale bei:

- H2: drei offene, miteinander verknüpfte Ernte-/Vergleichschargen;
- H4: zwei Parameterposten, drei sichtbare Commits und abschließende Fraktionsbuchung;
- H5-S001/002: `MASS? -> ANWENDEN? -> ZIEL?` sowie ein zweiter `ANWENDEN?`-Auftrag mit Commit.

Die stärksten Gegenfälle sind H1, H3 und H5-S005. Dort muss die Technik unbebilderte Musterstreifen, Farbanalyse oder Binderzwecke erfinden, während der sichtbare Herbal-Kontext und die V53-Mechanismusvergleiche gewöhnliche materia medica näherlegen. H5 behält außerdem die auffällige Reihenfolge `ACTION_APPLY -> TARGET_ASSIGN`; der Registerschreiber kann eine nachgetragene Zieladresse annehmen, aber diese Reparatur ist nicht kostenlos.

## Annahmekosten und Gesamturteil

Die symmetrische Kostenliste berechnet pro Aussage stille Teil-/Erntewahl, Prozessschritt, Medium, Ziel/Gefäß und Lagerbedingung mit je 1; eine Produktfunktion sowie Krankheit/Körperbezug mit je 2. Sichtbarer Besitzer, fixe Exact-Werte, formale Prompts und V62-Register kosten 0. Das ist ein Beschreibungsmaß, keine Wahrscheinlichkeit.

Gesamtsumme: **technisches Pflanzenregister 113**, **iatromedizinisch 107**. Die technische Fassung ist an acht einzelnen Transaktionen knapper und gewinnt die interne Registerkohärenz von H2 und H4. Als vollständige Herbal-Edition bleibt jedoch die **iatromedizinische Lesung insgesamt kohärenter**, weil sie den Bild-/Seitentyp und vorhandene historische Mechanismen nutzt, während die Technik fünf neue Endproduktklassen bezahlen muss. H5 bleibt unentschieden.

Urteil: **KEEP als stärkster ausführbarer nichtmedizinischer Herbal-Rivale; nicht zum Kartenwörterbuch oder zur bevorzugten Gesamtedition erheben.**

## Artefakte und Reproduktion

- `V64_R3_100_EVENT_PLANT_LEDGER.tsv`
- `V64_R3_20_FIELD_PLANT_EDITION.tsv`
- `V64_R3_19_STATEMENT_COMPARISON.tsv`
- `V64_R3_5_RECORD_PLANT_EDITION.tsv`
- `V64_R3_5_RECORD_PROCESS_GRAPHS.tsv`
- `V64_R3_10_RECORD_MODEL_ASSUMPTION_COSTS.tsv`
- `V64_R3_BUILD_TECHNICAL_PLANT_EDITION.py`
- `V64_R3_VALIDATE_TECHNICAL_PLANT_EDITION.py`

```bash
python3 V64_R3_BUILD_TECHNICAL_PLANT_EDITION.py
python3 V64_R3_VALIDATE_TECHNICAL_PLANT_EDITION.py
```
