# V57 R4 — Kanzleischreiber: Lehrbarkeit ohne Scheinklarheit

Status: unabhängiger kreativer Sidequest-Pass. Keine Entzifferung.

## Entscheidung

`LEARNABLE_AS_EXEMPLAR_DRIVEN_REGISTER_NOT_AS_GENERATIVE_LANGUAGE`

Mehrere Schreiber um 1420 könnten dieses System lernen, wenn sie nicht 173
Wörter samt Bedeutungen lernen müssten. Sie lernen eine kurze Schreibordnung
und arbeiten daneben mit Musterblättern:

1. Bild und Register bestimmen den stillen Gegenstand.
2. Ein Feld enthält null oder mehr offene Karten und höchstens eine
   Schlusskarte.
3. Vier gemeinsame Prompts setzen einen Standardslot, setzen einen lokalen
   Bezug, verknüpfen den laufenden Arbeitsstand oder rufen einen
   Vorgabeparameter auf.
4. Elf häufige Brückenkarten werden als Ganzbilder wiedererkannt; ihre
   deutschen Mnemonics sind Gedächtnishilfen, keine Übersetzung.
5. Seltene Karten werden aus einem registerlokalen Exemplar kopiert, nicht aus
   Lauten oder Stämmen konstruiert.
6. Die drei Kreisblätter besitzen eine eigene Lehre: Lage beziehungsweise
   Slot wählen, lokales Label kopieren, keine Prosa-Karte hineinlesen.

Damit ist das System als Werkstattpraxis einfach, aber als frei formulierbare
Sprache unvollständig. Ohne Exemplar kann ein Lehrling nur 45/381
Prosaereignisse beziehungsweise 35/135 Felder mit der harten Promptgrammatik
adressieren.

## Lehrplan für einen Lehrling

| Stufe | Lernstoff | Prüfung | typische Dauer |
|---|---|---|---|
| 1 | Seite, Absatz, physische Zeile, Feld und hierarchischer Abstand | ein Blatt fehlerfrei in Felder zerlegen | 2–3 Tage |
| 2 | offene Karte gegen feldfinale Schlusskarte | zehn Musterfelder korrekt kopieren | 2 Tage |
| 3 | vier harte V56-Prompts | vorhandenen Slot setzen und wiedererkennen | 3–5 Tage |
| 4 | elf gemeinsame Ganzkarten | Herbal/Bio-Muster ohne Registertausch kopieren | 1 Woche |
| 5 | lokales Herbal- oder Bio-Exemplardeck | einen vorhandenen Record variieren | mehrere Wochen |
| 6 | Kreisblätter separat | Lage und Label ohne erfundene Laufrichtung übertragen | mehrere Wochen |

Das ist kein moderner Unterrichtsplan. Die Zeitangaben sind nur eine
Werkstattprobe: Regeln werden rasch gelernt, der Kartenvorrat durch wiederholtes
Kopieren.

## Drei Rückleseproben

Die vollständige Tabelle steht in `V57_R4_ROUNDTRIP_AUDIT.tsv`.

### Herbal f10r_R1

```text
Quelle: Bildwurzel vorbereiten, nach Vorgabe verwenden, Rest weiterführen.
Notierbarer Kern: BILDOWNER | TEIL? | SET(STANDARD) | USE? | MASS? |
                 LINK(ACTIVE_STATE) | READY?
Rücklesung: markierten Bildstoff in einem Standardposten verwenden und den
             laufenden Ansatz verbinden.
```

Erhalten bleiben Auswahl, Vorgabe, Gebrauch und Fortsetzung. Verloren gehen
Wurzel, Wasser, Reinigen, Zerkleinern, Verwahren und Wärme. Diese Inhalte
stammen aus Bild, Exemplar und lokaler Artikelkonvention.

### Biological f82r_R1

```text
Quelle: Portion an Station ansetzen, bewegen, klären, ablassen, nachfüllen,
        verwenden.
Notierbarer Kern: MASS? | SET(LOCAL_RELATION) | LINK(ACTIVE_STATE) | USE? |
                 [lokale Bio-Karten] | CLOSE
Rücklesung: Vorgabeposten am lokalen Bezug mit dem Arbeitsstand verbinden,
             verwenden und die Zelle schließen.
```

Die Werkstatt kann die Formularlogik reproduzieren. Bad, Wasser, Tuch,
Temperatur und Körperstelle sind aus diesem Kern nicht wiederzugewinnen.

### Astro f68r1

```text
Quelle: gezeichnete Station im Zentrum-plus-28-Katalog markieren.
Notierbarer Kern: SPATIAL_LOCUS | LOCAL_EXEMPLAR_LABEL
Rücklesung: genau diese gezeichnete Station mit ihrem lokalen Label.
```

Die formale Adresse rundreist verlustarm; Mond, Mondhaus und jede Wirkung tun
es nicht. Das ist die sauberste lehrbare Teilmaschine der zehn Seiten.

## Fehler eines echten Lehrlings

1. **Zeile als Satz lesen:** Er setzt am Zeilenende einen inhaltlichen Schluss.
   Korrektur: nur der Feldschluss beendet die lokale Zelle.
2. **Renderer als neue Karte kopieren:** Er behandelt eine Eintrittsform als
   anderen Wert. Korrektur: zuerst lizenzierte Ganzkarte, dann Platzform.
3. **RIGHT-Klasse übersetzen:** Er macht aus `ARG_AIIN` automatisch MASS.
   Korrektur: RIGHT bleibt Slotklasse; nur die exakte Karte trägt das Mnemonic.
4. **Bildargument ausschreiben:** Er erfindet ein Kartenwort für Pflanze,
   Becken oder Körper. Korrektur: Besitzer bleibt im Bild oder Exemplar.
5. **Bio-Schlusskarte im Herbal verwenden:** Er generalisiert eine lokale
   Kadenz. Korrektur: Registerdeck getrennt halten.
6. **f68 mit f69 gleichnummerieren:** Er erzwingt einen 28↔28-Index.
   Korrektur: Seiten als getrennte Lookup-Instrumente lehren.

## Kanzleigegenprobe

Eine wirkliche generative Fachsprache müsste einem ausgebildeten Schreiber
erlauben, einen neuen Artikel ohne konkrete Vorlage zu verfassen. Der jetzige
Sidequest-Decoder kann das nicht. Er kann einen bestehenden Record korrekt
abschreiben, Slots austauschen und lokale Varianten buchen. Das passt besser
zu Formular, Nomenklator, Musterbuch oder stark abgekürztem Register als zu
einem selbsttragenden Geheimtextalphabet.

Die hohe Lernbarkeit stammt deshalb nicht aus entzifferten Wörtern, sondern
aus einer Zweiteilung:

```text
kleine produktive Kontrollgrammatik
+ großes kopiertes Ganzkarten-/Exemplarinventar
+ stilles Wissen aus Bild und Register
```

## Grenze

Der Pass zeigt nur, dass unsere beste Theorie von mehreren Schreibern
ausführbar wäre. Er zeigt nicht, dass die historischen Schreiber genau diese
deutschen Quellenphrasen oder den medizinischen Inhalt verwendeten.

`f84` und `f84r` blieben versiegelt.
