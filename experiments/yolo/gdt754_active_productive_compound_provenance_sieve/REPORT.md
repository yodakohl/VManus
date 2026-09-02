# GDT754 — 172 aktive Kompositionskarten zurück auf ehrliche Ganzformhypothesen

Status: `PARTIAL__172_ACTIVE_PRODUCTIVE_COMPOUNDS__889_SOURCE_PROSE_CELLS_159_PAGES__686_READER_EXACT__168_COMPOSITION_AXES_ONLY__1_LOCAL_ROLE_PATCH_FAMILY_42_CELLS__1_FORM_ANALOGY_ONLY__2_CORRECTED_PAIR_HYPOTHESES__12_GDT737_QUARANTINES__ZERO_SOURCE_LITERAL_PROSE_SPOKEN__172_BACKGROUND_HYPOTHESES_PRESERVED__24_HISTORICAL_BRIDGE_TARGETS__ZERO_COMPONENT_EXPORT__NO_NEW_PAGE`

## Ergebnis

Der in GDT753 sichtbare Fehler war kein Einzelfall. Das aktive Wörterbuch
enthielt 172 exakte Ganzformkarten aus GDT664/GDT666, deren konkrete deutsche
Sätze ausdrücklich als `PRODUCTIVE_COMPOUND` aus Analystenbausteinen gebaut
worden waren. Diese Karten sprechen derzeit an 889 Cachepositionen auf 159
zugelassenen Seiten; 686 Positionen sind reader-exakt.

| Quelle | Formen | aktive Zellen |
|---|---:|---:|
| GDT664 | 65 | 449 |
| GDT666 | 107 | 440 |
| gesamt | 172 | 889 |

Das spätere unabhängige Material ist viel dünner als die konkrete Prosa
vermuten ließ. GDT737 trifft zwölf Formen nur mit einer negativen
Headword-Quarantäne. GDT738 liefert zwei exakte Formtreffer, GDT753 zwei. Die
Artefakte aus GDT745, GDT746, GDT748, GDT749 und GDT750 treffen keine der 172
Formen. Insgesamt besitzen nur `lkaiin`, `lky`, `qokeol` und `okeol` irgendein
positives späteres Rollenindiz.

## Was sich am Renderer ändert

Keiner der 172 alten konkreten Sätze bleibt als gesprochene Übersetzung aktiv.
Sie werden aber nicht gelöscht: alte Prosa, Komposition, Achsen, Trägerannahmen
und Rivalen stehen vollständig im Inventar und im Entscheidungstableau. An
ihre Stelle treten nichtleere, ausdrücklich als Arbeitshypothese markierte
Ganzformdefaults.

| Form | alte konkrete Prosa | neuer gesprochener Arbeitsdefault |
|---|---|---|
| `air` | zweite Drogenfraktion | Index/Stufe II und Teil-/Fraktionsfeld; genaue Ganzform offen |
| `lkaiin` | Holzdroge, heiß auf Stufe III | heiß/warm, Stufe III und Stoffrolle; genaue Ganzform offen |
| `opchedy` | vollständig getrocknetes Pulverpräparat | trocken plus Stoff-, Zubereitungs-, Vorgangs- und Abschlussfeld; genaue Ganzform offen |
| `qokeol`, `okeol` | zwei verschiedene konkrete Heizsätze | gemeinsames Wärme-/Mittelstufenfeld; Funktion und Träger offen |

Das ist eine Korrektur der Behauptungsebene, kein Rückfall auf bedeutungslose
Prosa. `air` behält zum Beispiel die Hypothese Stufe II/Teil, sagt aber nicht
mehr ohne Beleg „Droge“. `opchedy` behält sein trockenes
Zubereitungs-/Prozessprofil, behauptet aber nicht mehr „Pulver“. `lkaiin`
behält global nur die Rollenarbeitshypothese; an 42 genau lokalisierten Zellen
bleiben die stärkeren GDT738-Vorkommenslesarten erhalten.

Die 889-Zeilen-Positionsdatei macht die Änderung direkt renderbar: 847 Zellen
erhalten den GDT754-Ganzformdefault, 42 die schon vorhandene lokale
GDT738-Lesart. In allen 889 Zeilen bleibt die alte Quellhypothese daneben
sichtbar.

## Was die Zahlen bedeuten

Die 172 Entscheidungen teilen sich so auf:

- 168 reine Kompositionsachsen-Hypothesen;
- zwei korrigierte gemeinsame Ganzformhypothesen (`qokeol/okeol`);
- eine Formanalogierolle (`lky`);
- eine globale Hypothese mit lokalen stärkeren Rollenpatches (`lkaiin`).

Damit sind keine 172 Wörter entschlüsselt. Wir besitzen nun aber eine saubere
Trennung zwischen dem, was früher kreativ zusammengesetzt wurde, und dem, was
später tatsächlich eine Form oder ein konkretes Vorkommen stützt. Genau diese
Trennung verhindert, dass der nächste historische Vergleich unsere eigenen
alten Bausteine nur wiederfindet.

## Nächster Weg

Die 24 folgenreichsten Ganzformen sind nach Reichweite und vorhandener Evidenz
in einem historischen Brückendeck fixiert. Als Nächstes werden sie als
vollständige Formen gegen reale spätmittelalterliche Fachregister geprüft:
Maß-/Fraktions-/Gradkürzel, Rezeptverben oder gebundene Anweisungen,
Zustands-/Qualitätsangaben und gelernte Drogen- oder Zubereitungsheadwords.

Der Vergleich startet bei den Rollenprofilen und ganzen Schriftformen. EVA
`p/s/r/l` oder andere Zeichen werden nicht als lateinische Initialen gelesen.
Treffer werden zunächst als Kandidaten gerankt, nicht als fertige Lexeme. Das
Ziel ist dennoch konkret: Kandidaten wie Wasser, Wein, Öl, Salz, Wurzel, Blatt,
reiben, erwärmen, baden, trocknen, einweichen oder Gefäß müssen an eine ganze
Form und ein passendes wiederkehrendes Rollenprofil gebunden werden, nicht an
eine nachträglich ausgewählte Einzelglyphe.

## Reproduktion

```bash
python3 experiments/yolo/gdt754_active_productive_compound_provenance_sieve/src/run.py
python3 experiments/yolo/gdt754_active_productive_compound_provenance_sieve/src/validate.py
```

Kein neues Blatt, Bild oder Transkript wurde geöffnet; f84 und f84r blieben
gesperrt.
