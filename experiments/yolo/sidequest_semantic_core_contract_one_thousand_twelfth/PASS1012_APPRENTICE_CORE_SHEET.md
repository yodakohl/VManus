# Pass 1012 — vorläufiges Kernblatt der Werkstatt

Dieses Blatt ist die Leseregel für die bestehenden 22 Seiten. Es enthält
keine neuen Seiten und keine neuen deutschen Geschichten. Eine bekannte Form
wird zuerst aus diesen kurzen Werten zusammengesetzt. Erst danach darf das
sichtbare Bild den Besitzer konkretisieren.

## Zwölf Inhalts- und Handlungskerne

| Zeichen | Ein Kernwert | Erlaubte Konkretisierung |
|---|---|---|
| `OK` | SETZEN | ansetzen, platzieren, aktiv setzen |
| `CH` | NEHMEN | Teil, Portion oder Eintrag entnehmen |
| `SH` | HALTEN | halten, stehen lassen, Zustand bewahren |
| `K` | GEBEN | zugeben, zuweisen, an eine Stelle geben |
| `AIIN` | MASS | Menge, Wert oder Einstellung |
| `S` | WÄHLEN | Material, Station oder Platz wählen |
| `CHD` | UMSETZEN | zwischen Zuständen oder Stellen versetzen |
| `OR` | ANSATZ | laufende Zubereitung oder Arbeitskonfiguration |
| `T` | EINSTELLEN | Menge, Stufe, Stellung oder Wert setzen |
| `AIN` | PORTION | Teilmenge, Füllung oder einzelne Zelle |
| `R` | MARKIEREN | Zustand, Stelle oder Eintrag kennzeichnen |
| `P` | EINSETZEN | Material oder Eintrag in einen Rahmen setzen |

## Sechs Referenz-, Folge- und Beziehungskerne

| Zeichen | Ein Kernwert | Wichtigste Grenze |
|---|---|---|
| `Y` | AKTIVER POSTEN | kein Schluss und kein Stoffname |
| `OL` | FORTSETZEN | nicht automatisch warm oder „vom Vorigen“ |
| `OT` | DANACH | kein eigenes Aktionsverb |
| `AL` | ZIELORT | das Bild liefert Gefäß, Körperstelle oder Platz |
| `AR` | AUSGANG | kein Wasser-, Wurzel- oder Quellstoffwort |
| `L` | VERBINDUNG | Anschluss bedeutet noch keine Richtung |

## Acht Steuerzeichen, keine Inhaltswörter

| Zeichen | Werkstattfunktion |
|---|---|
| `E` | GRAD I |
| `EE` | GRAD II |
| `EEE` | GRAD III |
| `DY` | lizenzierter SCHLUSS |
| `O` | lokale AUSFÜHRUNG |
| `CARRIER_Q` | BEGINNMARKER |
| `IIN` | STUFE |
| `DA` | ZWEITE STUFE |

Die Grade bedeuten nicht von selbst kurz, lang, kalt, warm oder vollständig.
Die laufende Handlung bestimmt, wie ihr Grad praktisch aussieht.

## Elf konkrete Fachkandidaten

Diese Bedeutungen sind nützlich, aber noch nicht Teil des harten Kerns. Auf
den vorhandenen Seiten müssen sie jeweils denselben Vorgang behalten:

`CTH=BEREIT`, `SHED=ABSETZEN`, `CKH=DURCHLASS`, `CHEO=AUSZUG`,
`AIR=LAUF`, `CHK=BEARBEITEN`, `SOLK=AUFFANGEN`, `LSH=SPÜLEN`,
`CPH=UMLEITEN`, `CFH=TRENNEN`, `LD=BEFESTIGEN`.

Bei einem Konflikt wird nicht ihre Bedeutung verbreitert. Entweder ist die
betreffende Form eine gelernte Ganzkarte, oder der Kandidat fällt aus dem
Wörterbuch.

## Neunzehn lokale Zeichen

Teil-, Innen-, Außen-, Rand-, Mitte-, Paar-, Rahmen- und Sondermarken sowie
lokale Stoffklassen bleiben Adressen des Bildes oder Masterexemplars. Sie sind
keine allgemein übersetzbaren Wörter. Ihre vollständige Liste und die jeweils
verbotene Umdeutung stehen in `PASS1012_56_SIGN_SEMANTIC_CONTRACT.tsv`.

## Leseregel

1. Die sichtbare Form in bekannte Komponenten zerlegen.
2. Ausschließlich die obigen Kernwerte in derselben Reihenfolge einsetzen.
3. Grade, Beginn und Schluss als Steuerung behandeln, nicht als Sachwörter.
4. Das Bild darf Pflanze, Teil, Gefäß, Badestation oder Himmelsplatz liefern.
5. Das Bild darf keinen unsichtbaren Filter, Stoff, Pfeil oder Apparat liefern.
6. Ergibt die Summe keinen sinnvollen Gang, wird die Gesamtform als gelernte
   Karte ausgesondert. Die Wurzelwerte werden nicht passend umgeschrieben.

Beispiel:

`OK + EE + Y` wird **SETZEN + GRAD II + AKTIVER POSTEN**. Im Pflanzenartikel
kann dies „den Pflanzenteil im zweiten Grad ansetzen“ heißen, im Badblatt „den
Stationsposten im zweiten Grad halten/setzen“. Es darf nicht ohne weitere
Stütze zu *warmem Wasser*, *Öl* oder *vollständig kochen* werden.
