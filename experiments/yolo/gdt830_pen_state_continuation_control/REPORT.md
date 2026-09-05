# GDT830 — Kontrollversuch stoppt an ungeeigneter Hintergrundmessung

2026-09-05. Registrierter Status: **CONTROL_CAPACITY_STOP**.
Die anschließende Diagnose zeigt eine ungeeignete Strich-/Papiertrennung in
realen Bilddaten. **Die Federzustandshypothese ist damit nicht geprüft.**

## Ergebnis des eingefrorenen Laufs

Die Methode und Implementierungen wurden mit `837a4d38` vor der ersten
Manuskript-Merkmalsextraktion öffentlich veröffentlicht. Vier Original-JPEGs
bereits freigegebener Seiten und 86 vorher ausgewählte Schriftstreifen liefern
1.032 feste Fenster. 249 Fenster bestehen die Qualitätsregel; 783 werden als
`INSUFFICIENT_PAPER` verworfen, weil mehr als 60% ihrer Pixel unter die
registrierte Dunkelheitsdefinition fallen.

| Seite | Ausgewählte Streifen | Kalibrierungszeilen mit gültigen Fenstern | Vollständige gehaltene Vergleiche |
|---|---:|---:|---:|
| f76r | 27 | 13 | 0 |
| f77r | 14 | 7 | 1 |
| f81r | 27 | 5 | 0 |
| f83r | 18 | 5 | 0 |
| Gesamt | **86** | **30** | **1** |

Die erforderlichen 24 vollständigen Vergleichsaufgaben auf allen vier Seiten
werden deutlich verfehlt. Es wird daher keine Trefferrate oder Rangverbesserung
als Testergebnis ausgegeben. Die Paarvergleichstabelle bleibt leer. Die
Kalibrierungskoeffizienten sind als Reproduktionsartefakt erhalten; sie sind
kein verwendbares Modell der historischen Feder.

## Warum dies kein einfacher Mangel an Schriftmaterial ist

Die auffällige Verwerfungsrate führte nach dem registrierten Lauf zu einer
begrenzten Hintergrunddiagnose. Auf dem bereits betrachteten f76r wurde ein
sichtbar unbeschriebener unterer Pergamentbereich gewählt: native Pixel
`[698,3317,1955,3392]`. Diese Wahl war **nach dem Ergebnis**, ist nicht
präregistriert und wird nicht als unabhängiger Bestätigungstest ausgegeben.

Die unveränderte Messung klassifiziert dort **64,6757%** der Pixel als
Vordergrund und findet 4.233 vermeintliche vertikale Strichzentren. Der Bereich
wird folgerichtig ebenfalls wegen zu wenig Papier verworfen. Die mediane
Grauintensität der Aufnahme beträgt dort 173,67; der Filter schätzt das Papier
auf 210,33. Der helle Extremwertfilter hebt somit auch die Papier-/Bildvariation
so stark an, dass gewöhnliche Hintergrundpixel als dunkle Strukturen gelten.

Ein zweiter Betrachter bestätigt die Lage auf schriftfrei wirkendem Pergament
und reproduziert Maske und Strichzählung mit eigener Rechnung. Die Stelle
ist nicht mikroskopisch als tintenfrei zertifiziert; die genaue Mischung aus
Pergamentstruktur, Beleuchtung, Bildkörnung und schwachen Spuren bleibt offen.
Details: `src/BACKGROUND_REVIEW.md`.

Diese Zahlen sind eine Diagnose des Bildverfahrens, kein Nachweis von Tinte,
Schreibspuren oder deren Alter. Ein Verfahren, das in diesem Bereich so viel
Hintergrund als Strichmaterial auswählt, kann seine anschließenden
Kontrastmerkmale nicht verlässlich als Federzustand ausgeben. Auch die 249
formal gültigen Fenster sind dadurch nicht automatisch physisch validiert.

Die Diagnose ist reproduzierbar in `src/audit_background.py` und
`artifacts/BACKGROUND_AUDIT.json`; sie verändert weder die Präregistrierung
noch die ursprünglichen Merkmale, Filter, Schwellen oder Ergebnisartefakte.

## Was die Kontrollen tatsächlich geprüft haben

Sechs synthetische Messkontrollen bestehen, darunter die vollständige
zugelassene Strichbreite 2–10 Pixel auf gleichförmigem Hintergrund. Sie fanden
vor der Registrierung einen Fehler des ersten Hintergrundfilter-Entwurfs:
9 Pixel löschten breitere synthetische Striche nicht vollständig. Der finale
15-Pixel-Filter korrigiert dieses Problem, bildet aber die native
Hintergrundvariation nicht ausreichend ab. Die synthetischen Prüfungen waren
für diesen realen Störfaktor zu einfach.

Der unabhängig geschriebene Validator rekonstruiert alle 1.032 Deskriptoreinträge,
die Kalibrierung, die Vergleichsauswahl und den Kapazitätsstopp. Er prüft die
Hashes, Abmessungen und Dateigrößen aller vier JPEGs sowie die 86 Rechtecke.
Sieben eigene synthetische Rechenkontrollen bestehen. Er misst die Pixel nicht
noch einmal unabhängig und behauptet ausdrücklich keine physische Validierung
von Tinte oder Schreibfolge. Sein PASS bestätigt die Berechnung aus der
Merkmalstabelle, nicht die Eignung des Messverfahrens.

Ein vollständiger Pixel-/Artefakt-Replay des unveränderten Runners besteht. Sämtliche numerischen Ergebnisse und die ursprüngliche
Präregistrierung bleiben erhalten.

## Konsequenz

**Diese konkrete Messkontrolle endet.** Sie hat keine belastbare
Fortsetzungsinformation geliefert. Die registrierten Parameter werden nicht
nachträglich passend gemacht und es wird keine Trefferrate aus dem einzigen
zulässigen Vergleich als Erfolg präsentiert.

Kein strittiger Schriftblock auf f32v/f55v/f82r wurde bewertet. Es gibt keine
zeitliche Richtung, Produktionsfolge, beabsichtigte Lesefolge, Änderung der
Transkription, Sprache oder Übersetzung. Auch ein generelles Fehlen brauchbarer
Federinformationen folgt nicht: Der Versuch scheitert bereits an seiner
Beobachtungsschicht. GDT829 und DIC001 werden dadurch nicht umgedeutet.

Keine neue Seite wurde freigegeben; f84/f84r bleiben geschlossen. Kein
öffentlicher Lösungsansatz, externes Sprachmodell, OCR oder KI-Bildverbesserung
wurde verwendet.
