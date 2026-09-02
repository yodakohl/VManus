# GDT746 — welche Ganzwortfamilien halten in der realen Verteilung?

## Ergebnis

Die Formanalogie aus GDT745 ist nicht bloß kosmetisch, aber auch kein fertiges
Wörterbuch. Unter 52 direkten Distanz-1-Beziehungen werden 15 durch Abschnitt,
Zeilenposition, semantische Ganzwortflanken und Abschlussnähe stark verstärkt;
zehn weitere sind kompatibel, 19 gewöhnlich/gemischt und acht wegen einer
Singleton-Seite nur schwach lesbar. Kein Paar erfüllt die harte
Verteilungs-Gegenfallstufe.

Vier Kandidaten besitzen mehrere starke Nachbarn:

| Form | verstärkte Familie | neuer Arbeitswert |
|---|---|---|
| `alom` | `alam`, `alol` | Rohstoff-/Stoffform der Klasse I; ein Maß davon als Nebenlesung |
| `chtar` | `chtal`, `chkar` plus kompatibles `choar` | trockene Fraktion/Teilform; Temperatur und Träger offen |
| `dsheedy` | `dshedy`, `dsheey`, `sheedy` | vollständig angefeuchteter/eingeweichter Stoff; Portion/Stufe offen |
| `ykeeey` | `ykeedy`, `ykeey` | hieraus bis zur heißen Endstufe führen; Abschluss sehr wahrscheinlich |

Acht weitere Kandidaten erhalten mindestens einen tragenden Vergleich:
`chckh`, `cheeey`, `chetar`, `chtl`, `okeeody`, `qochey`, `sheeol` und
`ykeeody`. Besonders brauchbar bleiben damit:

- `cheeey`: trockener End-/Vollzustand; Träger offen;
- `chetar`: erste trockene Fraktion der Mittelstufe;
- `okeeody`: vollständig erhitzter oder ausgekochter Ansatz im Endzustand;
- `qochey`: trocken bis zur Mittelstufe; heißer Zustand gegen Stoffzugabe und
  Mengenfeld offen;
- `sheeol`: behandelter Stoff; feucht/eingeweicht bevorzugt, trockene Endform
  als Rivale;
- `ykeeody`: heißer End-/Abschlusszustand; Ansatzlesung schwächer.

## Der unabhängige 46-Wort-Vergleich

Die 52 ausgewählten direkten Nachbarn belegen nur 6,65 Prozent der möglichen
17×46-Beziehungen. Trotzdem besetzen sie 16 der 85 Top-5-Verteilungsplätze;
bei gleichmäßiger Belegung wären 5,65 zu erwarten. Das ist eine 2,83-fache
Anreicherung als deskriptiver Arbeitswert, keine Wahrscheinlichkeit. Elf der
17 Kandidaten haben mindestens einen direkten Formnachbarn in ihren fünf
nächsten Verteilungen. Bei 14/17 überschneidet sich mindestens eine Achse des
Top-5-Verteilungskonsenses mit der GDT745-Formfamilie.

Diese zweite Sicht schränkt die Wörter sinnvoll ein. Sie stützt unabhängig vor
allem `MATERIAL` für `alom`, `DRY` für `chckh/cheeey/chetar/chtar/qochey`,
`PREPARATION|END_STAGE` für `okeeody`, `END_STAGE` für
`dsheedy/sheeol/ykeeey` und `HOT|END_STAGE` für `ykeeody`. Spezifischere Teile
wie Feuchtigkeit bei `dsheedy` oder Mittelstufe bei `qochey` stammen weiterhin
aus der direkten Formfamilie und dürfen nicht als unabhängig wiedergefunden
ausgegeben werden.

## Was nicht hält

`adchey`, `cheear` und `otalsy` haben jeweils nur ein reader-exaktes Vorkommen.
Sie behalten Formanalogien, aber keinen Verteilungsbonus. `oteeol` verliert den
vorläufigen Bonus, sobald der Abschnitt aus der Wertung entfernt wird.
`oteeos` bleibt ebenfalls offen: Seine beiden Kaltansatz-Nachbarn verteilen
sich nicht ungewöhnlich ähnlich.

Die exakten flankierenden Wörter sind überwiegend nicht identisch: Der Median
beider exakten Flanken-Jaccards ist null. Nur zehn linke und 18 rechte Paare
teilen überhaupt eine konkrete Flankenoberfläche. Das Signal betrifft also
Rollen-/Positionsverteilungen, nicht wiederkehrende identische Phrasen. Die
reader-exakt gegen alle-ZL3b-Sensitivität ist dagegen stabil: der Median der
absoluten Hybridabweichung beträgt 0,012; nur ein Paar überschreitet 0,10.

## Konkrete Konsequenz

Die beste Arbeitstheorie wird enger: Schreibähnliche Ganzwörter bilden bei
einem substanziellen Teil der 17 Kandidaten auch Verteilungsfamilien. Die
verstärkten Kerne sind Zustände wie trocken/Endbereich, Stoff-/Ansatzträger und
einige Teil-/Prozessformen. Das rechtfertigt konkrete Arbeitskarten, aber keine
Behauptung, `o`, `ch`, `-dy` oder ein anderer EVA-Teil bedeute für sich Wasser,
trocken, Ende oder irgendein lateinisches Kürzel.

Der nächste produktive Schritt ist, für jeden Kandidaten die fünf
verteilungsnächsten bekannten Ganzwörter gegen die direkten Formnachbarn zu
verschneiden und nur die gemeinsamen Achsen in laufende Passagen einzusetzen.
Damit können wir testen, ob die verbesserten Werte einen ganzen Absatz
konkreter machen, ohne die offenen Träger durch Fantasienamen zu ersetzen.

## Reproduktion und Grenze

Der vollständige Lauf umfasst 17 Ziele, 52 direkte Beziehungen, 782
Kalibrierungsvergleiche, 63 Formen und 1.523 Cachevorkommen auf 172 bereits
vorhandenen Seiten. Das GDT388-Paket ist strukturell lesbar, aber wegen fehlender
formaler Freigabe erwartungsgemäß `INVALID_PACKET` und nicht score-ready.
Der Validator besteht 18.725 Prüfungen und baut alle Ergebnisartefakte
byte-identisch neu.
GDT746 bestätigt null Lexeme, null Klartext, null Zeichen-/Komponentenwerte und
null konkrete historische Objektidentität.
