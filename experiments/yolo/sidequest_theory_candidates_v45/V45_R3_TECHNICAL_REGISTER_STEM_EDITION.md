# V45 R3 — stammtransparente technische Registeredition

## Auftrag und Perspektive

Ich rekonstruiere die zehn freigegebenen Seiten als Registerschreiber um 1420:
ein Lehrling lernt wenige wiederkehrende Arbeitsachsen, eine Tabelle zulässiger
Kompletierungen und einen kleinen Rest lokaler Ganzkarten. Das Ergebnis ist
bewusst eine kreative Werkstatttheorie, keine Entzifferung.

Die Eingaben sind ausschließlich die bereits f84-freien V40-, V43- und
V44-Artefakte. Die drei Astro-Seiten besitzen keine GDT327-Prosaereignisse;
ihre 395 lokalen V43-Labels werden deshalb unverändert separat geführt.
`f84` und `f84r` wurden nicht geöffnet.

## Ergebnis

Eine vollkommen lexikalische Zerlegung funktioniert weiterhin nicht. Eine
technische Zweischicht-Lesung funktioniert aber erheblich besser als 173
unverbundene deutsche Kartensätze:

```text
gemeinsamer Stamm oder abstrakte Arbeitsachse
  + Host-Erweiterung
  + lizenzierte exakte Zelle/Koordinate
  + lokales Argument aus Bild, Record und vorherigem Schritt
  + optional DY/COMMIT
  = konkrete Kartenlesung
```

Von 173 Prosakarten sind in dieser Fassung:

- **73** aus einem inhaltlichen Stamm oder einer produktiven formalen Achse
  plus Kompletierung lesbar;
- **91** nur schwach über eine gemeinsame templatische Achse organisiert; ihr
  konkreter Wert muss weiterhin lokal gelernt werden;
- **9** bildlokale Pflanzen-/Habitatwerte bleiben ausdrücklich memorierte
  Ganzkarten-Ausnahmen.

Damit wird nichts schöngerechnet: 164 Karten teilen irgendeine Werkstattachse,
aber nur 73 erhalten ihren wesentlichen Arbeitswert wirklich daraus.

## Das gemeinsame Kernlexikon

| Kern | Minimaler gemeinsamer Wert | Typ | Urteil |
|---|---|---|---|
| `AIIN` | bestimmter Parameter, besonders vorgeschriebenes Maß | Parameterachse | stark für die Maßkarte; Nachbarwerte nur formale Verwandtschaft |
| `OR` | bereiteter verwendbarer Arbeitsbestand | Inhaltsstamm | stärkster flüssigkeitsnaher Kern |
| `CHOR` | Beschaffung/Sammelzeit des Bildowners | Inhaltsstamm | klein, aber kohärent |
| `CHEY` | ausgewählter Materialanteil | Inhaltsstamm | Bildargument bleibt lokal |
| `CHY` | warme Zubereitung oder Anwendung | schwacher Inhaltsstamm | zwei Karten; vorläufig |
| `OK` | begrenzten Arbeitsposten aktivieren | produktive Operationsachse | 23 Karten / 79 Ereignisse |
| `OT` | markierten Bezug, Parameter oder Weg wählen | Relationsachse | 5 Karten / 9 Ereignisse |
| `L` | Fortsetzungs-, Empfänger- oder Transferweg | Transferachse | 23 Karten / 52 Ereignisse; konkreter Inhalt kommt aus der Zelle |
| `EY` | geforderten beobachtbaren Endzustand erreichen | Zustandsachse | nicht das freie sichtbare Suffix `-ey` |
| `Y` | aktuellen Recordträger oder Zustand führen | Zustands-/Deixisachse | nicht allgemein „Gegenstand“ |
| `CH` | Arbeitszustand verändern, trennen oder umleiten | Transformationsachse | konkrete Operation aus Kompletierung |
| `DY/COMMIT` | lokalen Arbeitsschritt vollziehen und Zelle schließen | Schlusskomponente | keine vollständige Aktion für sich |

Weitere Anlautachsen `A/C/D/E/F/H/K/O/P/R/S/T` reduzieren den Lehrstoff, sind
aber keine belastbaren Inhaltswörter. Sie sagen dem Schreiber, in welcher
Tabelle er den lokalen Kartenwert sucht: Adresse, Konstruktion, Rückverweis,
Zustand, Filterweg, lokales Objekt, Mittel/Gefäß, Folgeposten, Übergabe,
Fortgang, Relation oder Gleichzustand.

## Konkrete Übersetzungskorrekturen

Die neue Edition macht die gemeinsamen Werte in den Lesungen sichtbar:

```text
AIIN             Arbeite nach dem vorgeschriebenen Maß.

OR               Der bereitete verwendbare Arbeitsbestand.
OR + AIN         Verwende den bereiteten Arbeitsbestand frisch.

CHOR + BLÜTE     Beschaffe den Bildowner vor der Blüte.
CHOR + FRÜHJAHR  Beschaffe den Bildowner im Frühjahr.

CHEY + WURZEL    Wähle als Materialanteil die faserige untere Wurzel.
CHEY + MARKIERT  Wähle den bezeichneten Materialanteil.

EY               Arbeite bis zum geforderten sichtbaren Endzustand
                 (im lokalen Nassprozess: klarer Ablauf).
```

Das produktive `OK` wird überall als Aktivierung gelesen, während die
Kompletierung die Operation auswählt:

```text
OK + AIN   Aktiviere den Arbeitsposten: gib einen abgemessenen Anteil zu.
OK + AL    Aktiviere den Arbeitsposten: vereinige beide Anteile.
OK + AR    Aktiviere den Arbeitsposten an der bezeichneten Stelle.
OK + AIR   Aktiviere als Nächstes den oberen Lauf.
OK + AIIN  Aktiviere den nächsten abgemessenen Arbeitsposten.
```

`OT` leitet entsprechend keine einheitliche Sache, sondern einen markierten
Bezug ein:

```text
OT + AIIN  Nutze den markierten Bezug: dieselbe Dauer wie zuvor.
OT + AL    Nutze den markierten Bezug: zum unteren Ablauf.
OT + AR    Nutze den markierten Bezug: danach den unteren Ablauf.
```

`Y` bleibt abstrakter. Die Basiskarte führt den aktuellen Arbeitsposten; eine
andere exakte Zelle führt ihn bis zur gleichmäßigen Mischung. Die Habitatkarte
`choy` widersetzt sich dieser Lesung und bleibt eine der neun memorierten
Ausnahmen. Ebenso ist `L` kein Wort für Flüssigkeit: Öl, Kochen, Abziehen,
Empfänger und Fortsetzung werden erst durch die jeweilige Zelle bestimmt.

## Lehrbarkeit für mehrere Schreiber

Der Lehrplan dieser Fassung wäre handwerklich einfach:

1. zwölf zentrale Prompts (`AIIN`, `OR`, `CHOR`, `CHEY`, `CHY`, `OK`, `OT`,
   `L`, `EY`, `Y`, `CH`, `DY`);
2. elf schwache Registerachsen als Karteikasten-Adressen;
3. die häufigsten exakten Kompletierungen von `OK`, `L`, `O` und `E`;
4. neun bildlokale Ganzkarten;
5. Positionsrenderer getrennt vom Kartenwert.

Das ist kein sauberes modernes Präfix-Stamm-Suffix-System. Es ähnelt eher
einem historisch lernbaren technischen Formular mit wenigen produktiven
Prompts, vielen festen Abbreviaturkarten und aus dem Bild ausgelassenen
Argumenten.

## Vollständige Artefakte

- `V45_R3_STEM_AXIS_LEXICON.tsv` — 23 gemeinsame Stämme/Achsen;
- `V45_R3_COMPLETE_173_CARD_LEXICON.tsv` — jede Prosakarte mit Kern,
  Kompletierung/Koordinate, lokalem Argument und vollständiger deutscher
  Lesung;
- `V45_R3_COMPLETE_381_EVENT_TRANSLATION.tsv` — jede der 381 festen
  Prosastellen in Manuskriptreihenfolge;
- `V45_R3_ASTRO_395_LABELS_UNCHANGED.tsv` — die drei Astro-Seiten unverändert
  aus V43;
- `V45_R3_VALIDATION.json` — Vollständigkeits- und Versiegelungskontrolle.

## Grenze

Diese Edition zeigt, dass eine konsistentere **Werkstattlektüre** mit
gemeinsamen Prompts möglich ist. Sie zeigt nicht, dass die vorgeschlagenen
Kerne gesprochene Wörter, Morpheme oder historische Bedeutungen waren. Der
entscheidende Vorbehalt bleibt: Die 91 templatischen Karten werden durch das
System geordnet, aber nicht aus ihm übersetzt. Ihr konkreter Wert bleibt eine
gelernte lokale Konvention.
