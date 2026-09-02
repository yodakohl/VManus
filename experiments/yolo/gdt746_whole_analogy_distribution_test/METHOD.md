# GDT746 method

## Question

Besetzen GDT745s 17 A3-Kandidaten tatsächlich dieselben Manuskriptumgebungen
wie ihre 52 bekannten Distanz-1-Ganzwortnachbarn, oder war die starke
Bedeutungsähnlichkeit nur eine attraktive Schreibanalogie?

## Inputs

Die Kandidaten, direkten Ganzwortbeziehungen, Arbeitswerte und Achsen stammen
aus GDT745. Vorkommen kommen ausschließlich aus dem bereits erlaubten
179-Seiten-Cache und dem GDT734-Zellregister. Der Guard materialisiert 32.339
erlaubte Token; `f84/f84r` bleiben vor der Materialisierung gesperrt. GDT739s
Achsenregeln beschreiben nur die bekannten linken/rechten Ganzwörter.

## Method

Die A3-Grenze liefert 17 Kandidaten, 52 direkte Beziehungen zu 46 verschiedenen
bekannten Ganzwörtern und zusammen 63 vollständige Oberflächen. Der Cache
enthält davon 1.523 Vorkommen auf 172 bereits vorhandenen Seiten; 1.228 sind in
ZL3b, IT2a und RF1b exakt gleich gelesen. Primär werden diese 1.228
reader-exakten Stellen verglichen, alle ZL3b-Stellen bilden die Sensitivität.

Jedes Vorkommen erhält fünf Verteilungsmerkmale:

- Manuskriptabschnitt;
- FIRST/MIDDLE/LAST/SINGLE-Zeilenposition;
- Achsen des unmittelbar linken bekannten Ganzworts;
- Achsen des unmittelbar rechten bekannten Ganzworts;
- Seite und Abstand der nächsten bekannten Abschlussform innerhalb fünf Token.

Zusätzlich bleiben die exakten linken und rechten Ganzwortoberflächen sichtbar.
Für jedes Merkmal wird die Jensen-Shannon-Ähnlichkeit berechnet. Der breite
Score gewichtet Abschnitt 0,25, Zeilenposition 0,20, beide Seitenkontexte je
0,20 und Abschlussnähe 0,15. Der Hybridscore besteht zu 0,80 aus diesem Wert und
zu je 0,10 aus den exakten linken/rechten Ganzwortverteilungen. Eine zweite
Wertung entfernt den Abschnitt vollständig; ein starkes Paar muss auch dort
über dem Vergleichsfeld liegen.

Für jeden Kandidaten wird jedes der 46 bekannten Wörter gleich behandelt. Der
echte Distanz-1-Nachbar erhält deshalb einen Rang innerhalb derselben 46-Wort-
Vergleichsmenge. Die vollständigen 17×46 = 782 Werte zeigen außerdem, welche
fünf Wörter allein nach Verteilung am nächsten liegen. Deren Achsenkonsens wird
mit dem unabhängigen Formfamilienkonsens aus GDT745 geschnitten.

Die Arbeitsstufen sind Durchsatzkarten, keine Wahrscheinlichkeiten:

- D3: beide Seiten mindestens drei reader-exakte Vorkommen, Hybrid ≥0,60,
  Gesamtrang ≥80. Perzentil, lokaler Rang ohne Abschnitt ≥65. Perzentil und
  mindestens drei von fünf breiten Merkmalen ≥0,50;
- D2: beide Seiten mindestens zwei Vorkommen, Hybrid ≥0,52, Gesamtrang ≥55.
  Perzentil, lokaler Rang ≥40. Perzentil und zwei breite Merkmale ≥0,50;
- D1: Singleton-/knappe oder gewöhnliche Vergleiche;
- D0: beidseitig mindestens drei Vorkommen, Hybrid <0,38 und Rang höchstens im
  unteren Fünftel.

Die 17 deutschen Folgekarten werden anschließend einzeln konsolidiert. Ein
Singleton darf keinen Bedeutungsbonus erhalten, auch wenn sein Einzelkontext
zufällig hoch rangiert.

## Decision rule and claim ceiling

Mehrere D3-Nachbarn verstärken eine Ganzwortfamilie; ein D2-Nachbar stützt sie
provisorisch. Das benennt weder ein historisches Wort noch einen Stoff. Nur
Achsen, die sich aus vollständigen bekannten Wörtern ergeben, dürfen in den
Arbeitswert einfließen. Exakte Flankenübereinstimmung, Abschnittseffekt und
reader-variant Sensitivität bleiben als Gegenbelege sichtbar.

GDT746 bestätigt null Lexeme, null Klartext, null Zeichen- oder Teilstringwert,
null konkrete Pflanze, Substanz, Flüssigkeit, Krankheit, Heilung, Person,
Gefäß oder Maßeinheit und null Vorhersage ungesehener Formen.
