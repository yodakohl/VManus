# GDT515 — Methode

## Frage

Können alle 597 Karten der vier in GDT514 ausgewählten Seiten konkrete
Arbeitsbedeutungen erhalten, ohne einen der neunzehn portablen Werte zu ändern,
und trägt das Mischmodell aus Funktionskürzeln, Datensatzkarten und lokalen
Namen-/Zeichenresten auf diesen Seiten?

## Geschützte Eingabe und Besitzer

Der Builder lädt ausschließlich `f31r`, `f66r`, `f20v` und `f4r` über
`./vmanus-exp query-tsv`, mit expliziten Allow-Werten, ausgewählten Spalten und
dem verbotenen Präfix `f84`. Die Abfrage ergibt 122 Quellzeilen und 597 Token.

Die Bildkarte aus GDT514 bleibt unverändert. f31r, f20v und f4r besitzen je
eine abgebildete Ganzpflanze; sichtbare Absatzgrenzen begrenzen Aussagen, ohne
den Pflanzenbesitzer zu teilen. Auf f66r ist jeder der fünf Hauptprosablöcke
ein eigener Textbesitzer. 46 frühe Randtoken und fünf Token des separaten
späten Nachtrags werden als 51 lokale Karten gespeichert und niemals an einen
Hauptprosasatz angehängt.

## Rezeptreihenfolge

Für jede Oberfläche gilt diese Reihenfolge:

1. Ein Kontakt mit GDT405 übernimmt das dort gesperrte Rezept exakt.
2. Eine andere alte laufende Oberfläche übernimmt ihr eindeutiges
   GDT407-Rezept.
3. Nur eine im laufenden Deck fehlende Oberfläche erhält eine direkte sichtbare
   Zusammensetzung aus den 46 aktuellen Komponenten.
4. `axor` und `chxar` dürfen den undurchsichtigen lokalen Kern
   `LOCAL_NAME_CORE_X` behalten. Die alleinstehenden Randformen `x` und `c`
   bleiben `LOCAL_SIGN_X/C`. Diese drei Tags sind keine portablen Atome und
   keine Wortübersetzungen.

Die beste sichtbare Ein-Schritt-Nachbarzerlegung wird für jede der 169 im
laufenden Deck fehlenden Oberflächen protokolliert, aber nicht automatisch zur
ausgewählten Zerlegung gemacht. Eine Arbeitshypothese bleibt damit benutzbar,
bis eine sichtbar bessere Zerlegung sie ersetzt.

## Bedeutungen und Aussagen

Die neunzehn breiten Werte stammen bytegenau aus GDT413. Formale und lokale
Komponenten werden in der Lesung geklammert. Jede Karte erhält außerdem eine
Containerrolle: Anweisung, Adresse/Fortsetzung, Koordinate/Katalog, lokale
Kennung, Namenskern mit Funktionsrahmen, Randkennung, Randzeichen oder später
Nachtrag.

Nur die 546 Prosakarten werden an den GDT402/GDT404-Bereichsparser übergeben.
`DY` darf eine Aussage schließen, höchstens eine folgende Karte darf als
begrenzter Vorgriff dienen, und Besitzer- sowie Absatzgrenzen dürfen nicht
überschritten werden. Für das offene `ykady` wird zusätzlich eine Lesung ohne
Schlusswirkung berechnet.

## Auswertung

Die fünf vor dem Öffnen in GDT513 notierten Erwartungen werden direkt gegen
die vier Seiten gestellt. Aufnahme verlangt vollständige Defaults, exakte
Wiederholung aller GDT405-Kontakte, null neue portable Atome, null
Bereichsfehler und getrennte f66r-Randkarten. Der Anspruch bleibt eine
explorative Arbeitsausgabe, nicht identifizierter Klartext, Sprache oder
bestätigtes Lexikon.
