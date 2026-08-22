# V53 — Auswahl der vollständigen Herbal-Ausgabe

Status: kreative Arbeitsübersetzung der vier erlaubten Herbal-Seiten, keine
Entzifferung. Die vier Rollen arbeiteten unabhängig; R4 wurde vor Sichtung der
anderen Berichte eingefroren.

## Auswahl

Die fünf Records werden als **bebilderte Materia-medica-Artikel mit
werkstattartiger Karten-/Feldnotation** gelesen. Das Bild liefert den stillen
Gegenstand. Die Schrift notiert eine Folge aus Teil, Zubereitungsstand, Maß,
Bezug, Gebrauch und Feldabschluss. Sie ist keine Wort-für-Wort-Prosa.

Die beste konkrete Fassung ist:

1. `f10r_R1`: eine skabiosen-/Teufelsabbiss-nahe Wurzelzubereitung, am ehesten
   ein medizinisches Wurzelwasser. Reinigen, zerkleinern, mit Wasser bereiten,
   eine abgemessene Portion verwenden, Rest verwahren; eine warme Anwendung
   bleibt möglich.
2. `f10r_R2`: eine zweite Zubereitung derselben Bildpflanze aus oberem
   Pflanzenmaterial, Saft beziehungsweise Sud, Öl und äußerlichem Gebrauch.
3. `f11r_R1`: eine kleine Schattenpflanze; Veilchen ist die historisch
   produktivste Lesung, eine Dolden-/Wurzelpflanze der stärkste Bildrivale.
   Der Artikel wird als geklärter Wein-/Wasserauszug plus warme Auflage gelesen.
4. `f55v_R1`: ein breitblättriges Heilkraut, Allium/Bärlauch und Wegerich als
   gleich ernsthafte Rivalen. Zwei Bereitungen: Auszug/Waschung und warme
   Auflage.
5. `f56r_R1`: eine feuchtlandliebende, drüsige oder borstige Pflanze;
   Sonnentau ist der stärkste enge Bildvergleich. Kleine Mengen des Krauts
   werden ausgezogen, getrennt getrocknet und als Brust-/Hustenmittel
   verwendet. Dies ist die riskanteste der fünf Lesungen.

Die vollständigen Texte stehen in `V53_SELECTED_FIVE_ARTICLES.tsv`.

## Was gegenüber V52 wirklich verbessert wurde

- Die 20 Felder und 100 Ereignisse bleiben vollständig erhalten.
- Pflanzenname, Wasser, Wein, Öl, Honig, Körperstelle und Krankheit werden
  nicht mehr heimlich einzelnen Karten zugewiesen.
- `CLOSE` bleibt nur Feldschluss; eine Zeile beendet keinen Satz.
- f11r und f55v erhalten echte botanische Rivalen statt Scheinsicherheit.
- Der engste historische Treffer wird bevorzugt: Frankfurt UB Ms. germ. qu.
  17 (erstes Viertel 15. Jh.) enthält Abiss-/Teufelsabbiss-Wasser gegen innere
  Beschwerden. Das beweist keine Identität, macht f10r_R1 aber zur besten
  konkreten Quellenrekonstruktion.
- Veilchenwein/-öl und Allium-/Wegerich-Verfahren bleiben historische
  Mechanismusanalogien; der Sonnentau-Brusttrank bleibt ausdrücklich eine
  Hochrisikowette.

## Kartenanker versus Artikelinhalt

Nur 32 der 100 Herbal-Ereignisse tragen überhaupt einen ausgewählten V50/V51-
Anker; 68 sind opak. Deshalb gilt:

```text
sichtbare Karte -> schwacher formaler/atomarer Anker
Bild + Artikeltyp + Nachbarkarten -> konkrete Quellenphrase
ganzer Record -> flüssige deutsche Arbeitsübersetzung
```

Die flüssigen Texte sind damit vollständige, handhabbare Defaultlesungen, aber
nicht die Summe eines entzifferten Wörterbuchs.

## Vier-Rollen-Bilanz

- R1 bevorzugt fünf medizinische Herbal-Artikel und konkrete
  Pflanzenbesitzer.
- R2 liefert die stärksten historischen Vergleichsrezepte und markiert die
  wachsende Unsicherheit von f10r_R1 bis f56r.
- R3 erklärt die gleiche Struktur sparsamer als Material-, Chargen-, Teile-
  und Anwendungregister.
- R4 entfernt ungestützte Krankheitsnamen und hält die Bildbesitzer breit.

Die Auswahl verbindet R2s historische Quellenmechanismen mit R3s
Registerarchitektur und R4s konservativer Besitzerwahl. R1s präzisere
Pflanzennamen bleiben als Rivalen erhalten.

## Protokollabweichung

R2 öffnete bei einer anfänglichen PDF-Zuordnung versehentlich ausschließlich
Bild-Thumbnails von `f54v`, `f55r`, `f56v` und `f57r`. Es wurden keine Text-
oder Tabellendaten daraus gelesen. Die Eindrücke wurden verworfen und gingen
nicht in die Auswahl ein. `f84` und `f84r` blieben vollständig versiegelt.

## Restwiderspruch

Alle fünf Artikel lassen sich mit gewöhnlicher mittelalterlicher
Materia-medica füllen, obwohl zwei Drittel der Karten opak sind. Historische
Plausibilität ist daher gerade kein Nachweis. V53 liefert eine bessere
Werkstatt-Arbeitstheorie, aber noch kein lesbares Kartenlexikon.
