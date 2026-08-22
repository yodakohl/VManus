# V65 — Vierrollen-Auswahl: Biological-Zweitausgabe

Status: vollständige kreative Arbeitsedition; keine Entzifferung.

## Auswahl

R2 wird als gemeinsame Biological-Fassung gewählt:

```text
illustriertes therapeutisches Bad-/Wascharbeitsblatt
+ eigenständige Becken-, Filter-, Leitungs- und Auslassbedienung
```

Das ist keine reine Frauenheilkunde und kein reines Wasserwerk. Der medizinische
Rahmen ist bei B2 am stärksten und bei B4 nur gattungsgestützt. B1 und B3
bleiben echte Mischfälle. B5 und B6 werden auch innerhalb der medizinischen
Handschrift primär als technische Hilfsnachträge gelesen.

## Vollständige Deckung

```text
Records:       6
Aussagen:     97
Felder:      115
Ereignisse:  281

Ereignisse: 90 lizenziert, 191 EXEMPLAR_ONLY
Felder:      14 UNIQUE, 41 AMBIGUOUS, 60 UNPARSED
Aussagen:    12 UNIQUE, 35 AMBIGUOUS, 50 UNPARSED
```

R1 bestätigt denselben Hybrid als für einen Lehrling ausführbare
103-Kanten-Fassung und lässt genau eine unsichere Kante sichtbar. R3 führt den
reinen Wasserwerksrivalen vollständig aus: Er gewinnt 13 von 97 Aussagen, die
iatromedizinische Fassung 25, 59 bleiben gleichwertig. Nach symmetrischen
Zusatzannahmen verliert die Technik nur knapp mit 597 gegen 587. R4 bestätigt
die sechs Prozessketten und hält alle konkreten Sachwörter außerhalb der
Kartenebene.

## Sechs ausgewählte Prozesse

1. **B1/f81v — Grundkreislauf:** Kräuter-/Badflotte beschicken, portionieren,
   verbinden, temperieren, ruhen und prüfen, nachfüllen, weiterleiten,
   Teilstrecken spülen oder entleeren. Medizin und Badehaus sind unentschieden.
2. **B2/f82r — Einzelbad:** temperierte Portion zwischen Zugängen führen,
   filtrieren und auffangen; örtliches Teilbad, Waschung oder warme Auflage als
   bevorzugte Exemplarfüllung; danach Varianten spülen/ablassen.
3. **B3/f83r — langer Rücklaufzyklus:** setzen, klare Fraktion abziehen, warm
   nachspeisen, mischen, verteilen, unten fangen, erneut klären und rückführen.
   Äußere Lavage und Wasserwerk bleiben gleich stark.
4. **B4/f83r — warmer Nachgang:** Anteil temperieren, durch Tuch führen,
   äußerlich waschen/auflegen, dann Gefäß und Lauf reinigen, ablassen und neu
   beschicken. Der Körperbesitzer kommt nur aus Bild und Gattung.
5. **B5/f83r — Übergabenachtrag:** Teilcharge abziehen, einmal erwärmen, halten,
   mit dem recordlokalen Vorposten verbinden und weitergeben. Technische Lesung
   gewinnt.
6. **B6/f83r — offener Kaltgang:** kalten Bestand recordlokal eröffnen,
   dosieren, einfach filtern und zum Zielslot übergeben. Kein Rückgriff auf B5
   und kein erfundener Schluss.

## Verbesserungen gegenüber V54

- Innere gynäkologische Anatomie und Diagnosen werden zurückgezogen.
- `VORIGES?` und alle anonymen Register resetten an jedem Record.
- f82r.3→f82r.4 bleibt eine Aussage über den physischen Zeilenwechsel hinweg.
- Die langen f83r-Folgen werden als Prozessphasen und Varianten gelesen, nicht
  als je ein Satz oder eine Krankheit pro Feld.
- `SPÜLEN?` und `ABLASSEN?` bleiben an allen 16 Vorkommen terminal-konfundiert.
- Apparatebetrieb ist ein positiver Bestandteil der bevorzugten Fassung, nicht
  bloß eine skeptische Nullhypothese.

## Bedeutungsgrenze

Wasser, Badende, Patient, Haut, Wunde, Tuch, Becken, Rohr, Temperatur und Dauer
sind Bild-, Gattungs- oder Exemplarwörter. Die gemeinsame sichtbare Ebene ist
nur eine anonyme Betriebsalgebra:

```text
OWNER/STATION -> ACTIVE CHARGE -> PARAMETER/LINK/TARGET
              -> STATE/CONTACT -> TRANSFER -> LOCAL CLOSE
```

V65 ändert keine der elf V60-Kartenbedeutungen und fügt keinen Stamm hinzu.
