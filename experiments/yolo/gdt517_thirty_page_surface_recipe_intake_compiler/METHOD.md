# GDT517 — Methode

## Frage

Kann aus den 26 älteren Seiten ein ausführbarer Oberflächen-zu-Rezept-Compiler
gebaut werden, der die 159 in GDT515 erstmals sichtbaren Formen selbständig
zerlegt, anstatt ihre dort bereits eingetragenen Rezepte nur zu wiederholen?
Und lässt sich daraus eine vollständige, rollenbewusste Aufnahmebasis für alle
30 gegenwärtig geöffneten Seiten herstellen?

## Eingaben

Der Pass öffnet keine weitere Manuskriptseite. Er verwendet:

- GDT407s 4.576 laufende Ereignisse und 693 lokale Gruppen der älteren 26
  Seiten;
- GDT413s Komponentenwerte für die wörtliche Arbeitswiedergabe;
- GDT451s ausführbaren, zustandsabhängigen Rezeptleser;
- GDT473s 183 vollständige lokale Adress-/Namenspakete;
- GDT513s 510 vollständige Arbeitslesarten der übrigen alten Lokalkarten;
- GDT516s 159 neue Oberflächen als Wiedergewinnungsziel sowie dessen 597- und
  5.866-Karten-Kontextausgaben.

## Lernen sichtbarer Stücke

Die ältere laufende Ausgabe enthält 1.558 verschiedene Oberflächen. Jede davon
hat genau ein beobachtetes Rezept. Der Builder lernt daraus in vier Stufen:

1. vollständige alte Oberfläche → vollständiges altes Rezept;
2. direkte Reststücke aus Paaren, bei denen die kleinere Oberfläche durch
   Entfernen eines zusammenhängenden Zeichenstücks und ihr Rezept durch
   Entfernen eines zusammenhängenden Atomstücks entsteht;
3. wiederholte Präfix-/Suffix-Abtrennung bereits hinreichend eindeutiger
   Stücke;
4. die endlichen f66r-Lokallesungen `x → LOCAL_X` und `c → LOCAL_C`.

Ein direkter Restkontakt erhält das Minimum der beiden alten
Ereignishäufigkeiten. In jeder Iteration werden die Gewichte zu Rundenbeginn
festgehalten; dadurch kann die Reihenfolge innerhalb der Runde ein Stück nicht
verstärken. Ein Topkandidat wird bei mindestens 0,75 Anteil weiterverwendet.
Für die spätere Zerlegung bleiben alle Kandidaten ab 0,05 Anteil erhalten.

`dy → DY` darf nach der ersten Reststückrunde keine zusätzliche rekursive
Selbstverstärkung erhalten. Die 30-Seiten-Ausgabe zeigt bereits, dass dasselbe
sichtbare `dy` auch `D_ADDR+Y` oder `Y` realisiert. Diese Alternativen bleiben
deshalb im Compiler. Die f66r-Tags sind ebenfalls bereichsgebunden: außerhalb
eines ausdrücklich gewählten f66r-Lokalkontexts bleibt etwa `c → CH` die
allgemeine Zerlegung.

## Zerlegung und Rangfolge

Ein dynamisches Programm kachelt die gesamte sichtbare Oberfläche lückenlos
mit gelernten Stücken. Kandidaten werden zuerst nach der kleinsten Zahl
sichtbarer Stücke und dann nach

`log(1 + Unterstützung) + 2·log(Anteil) − 0,1·Rezeptatome`

geordnet. Pro Oberfläche bleiben höchstens 2.000 verschiedene Rezepte. Sobald
eine Oberfläche kachelbar ist, wird immer ein Rang-1-Arbeitsdefault ausgegeben;
die nächsten Kandidaten bleiben sichtbar.

Die Wiedergewinnung verwendet nur das 26-Seiten-Modell. Erst danach wird
dasselbe Verfahren auf den aktuellen 5.122 laufenden Ereignissen der 30 Seiten
neu gebaut. Bekannte 30-Seiten-Formen werden nicht neu erraten: ihre exakte
Ereigniskarte hat Vorrang vor Oberflächenindex und Compilerdefault.

## Lokale Pakete und Rollen

Die 693 alten Lokalkarten werden nicht aus den alten Platzhaltern wie
`LOCAL_ADDRESS` rekonstruiert. Die 183 GDT473-Karten und 510 GDT513-Karten
decken sie disjunkt und vollständig ab. Gelernte Ganznamen bleiben benannte
lokale Pakete; ihre Funktionsschale wird getrennt gespeichert. Die 51 neu
ausgewählten Lokalkarten und die im laufenden Material erkannten Rand-/Namens-
rollen werden ebenfalls als `LOCAL_RECORD` geführt.

Der Oberflächenindex zählt Rezeptoptionen, nicht Besitzerformulierungen.
Unterschiedliche deutsche Besitzerergänzungen derselben Rezeptkarte bleiben
in der ereignisgenauen 5.866-Karten-Ausgabe und erzeugen kein falsches zweites
„Wort“.

## Ausführung

Die 546 ausgewählten laufenden Karten werden aussagenweise durch GDT451
geschickt. Nicht ausführbare Adressabschlüsse bleiben lesbare Rollencontainer,
lokale Namensschalen betreten den portablen Aktionsstrom nicht, und die einmal
direkt sichtbare Folge `SH>S` in `shso` erhält genau dort eine gelbe Leselizenz.
Solche Rollenkarten verändern den laufenden Handlungszustand nicht.

## Grenze

GDT517 liefert einen durchgängigen Arbeitscompiler, keine bestätigte Sprache
oder Klartextübersetzung. Seine Rang-1-Ausgabe ist der verpflichtende Default
des Sidequests; bekannte Ereigniskarten und endliche Rollenentscheidungen haben
Vorrang, und alternative Zerlegungen bleiben abrufbar.
