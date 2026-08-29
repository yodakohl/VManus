# GDT635 — Methode

## Frage

Können die GDT634-Hypothesen für initiales `p/s/r/l` durch echte
Gleichrestreihen verbessert werden? Eine brauchbare Kopfbelegung muss aus
demselben Rest unter wechselndem Anfangszeichen kurze, vorhersehbare
Stoffbedeutungen bilden und in vollständigen Passagen praktisch lesbar bleiben.

## Materialgrenze

Der Versuch benutzt nur die von GDT634 geerbte Allowlist mit 179 Seiten. Es
werden keine neue Seite und kein Bild geöffnet. `f1r` bleibt ausgeschlossen;
`f84` und `f84r` sind verboten. Die beiden gemischten TSV-Quellen werden durch
den Guard projiziert, bevor andere Spalten materialisiert werden. Das Ergebnis
enthält 32.339 ZL3b-Token in 4.128 tokenführenden Loci sowie 4.137
Paralleltranskriptionszeilen.

ZL3b, IT2a und RF1b bleiben drei Lesungen desselben Manuskripts. Ihre
Übereinstimmung ist ein Oberflächenstabilitätsmerkmal, keine dreifache Probe.

## 1. Exakte Kopfdefinition

Für jedes Token gilt nur:

```text
head = erstes Zeichen aus {p,s,r,l}
body = sämtliche danach sichtbaren Zeichen, unverändert
```

Zusatzregeln:

- `sh...` ist ein eigener Feuchtigkeitskern und wird nicht als `s+h...`
  zerlegt;
- die Einzeichenformen `p/s/r/l` bleiben separat;
- innere und terminale Vorkommen derselben Zeichen bleiben separat;
- es gibt keine Allographnormalisierung, keine Editdistanz und keine
  Übernahme der GDT418-Workshopwerte.

So entstehen 2.860 initiale Kopf-Token, 985 Kopf-Körper-Typen und 760
verschiedene Körper.

## 2. Belegungsatlas

Für jeden Körper werden Kopfbelegung, Formen, Token-, Seiten-, Locus- und
Leserstabilitätszahlen gezählt. Körper mit mindestens zwei Köpfen bilden den
Tauschatlas. Zusätzlich werden erfasst:

- derselbe Körper mit zwei Köpfen in derselben physischen Zeile;
- derselbe Körper unter identischem linken und rechten Nachbartoken;
- derselbe Kontext zusätzlich in gleicher Sektion, Sprache und Hand;
- alle Körper, die unter sämtlichen vier Köpfen vorkommen.

Das ist ein Zeichenvergleich, keine Behauptung, dass die vier Köpfe dieselbe
syntaktische Funktion besitzen.

## 3. Konkrete Bedeutungsbelegung

Die Arbeitswerte werden nicht aus langen frei formulierten Sätzen gewonnen,
sondern aus einer kurzen Komposition:

```text
Kopfwert + Restwert

p pulvis/Pulver       aiin Typ/Charge III
s semen/Samen         chedy getrocknet
r radix/Wurzel        shedy angefeuchtet/eingeweicht
l lignum/Drogenholz   ol Stoff/Material
                      or Teil/Portion
```

Jeder dieser fünf Reste muss mit jedem der vier Köpfe tatsächlich belegt sein.
Die resultierenden 20 Ganzformen erhalten genau eine Primärbedeutung und ein
separates Rivalenfeld. Die erweiterte Trocken-/Feuchtreihe aus zehn Körpern
ergibt 40 mögliche Zellen; beobachtete und noch leere Formen werden getrennt
ausgegeben. Leere Zellen werden nicht ins Wörterbuch aufgenommen.

## 4. Zwei syntaktische Kopfklassen

Die Semantik wird nicht mit einer falschen Einheitssyntax erkauft. Für jeden
Kopf werden Zeilenanfang, -mitte und -ende gezählt. `p/s` sind häufig
zeileninitial; `r/l` fast immer intern oder final. Das Arbeitsmodell behandelt
sie daher als zwei Unterklassen:

```text
p/s  Stoff- oder Eintragsköpfe
r/l  interne Zutaten-/Pflanzenteilköpfe
```

Die vollständigen Viererraster sind semantische Austauschreihen, nicht die
Behauptung einer einzigen flachen Satzposition.

## 5. Zehn Übersetzungsspannen

Zehn benannte Spannen prüfen die praktische Folge an exakt erhaltenen
Tokenpositionen. Jede Zeile enthält Oberflächen, Tokenbedeutungen, eine
zusammengesetzte deutsche Arbeitslesung, alle drei Transkriptionen und eine
Leserdiagnose. Kein Token darf mit „Arbeitsgut“, „bearbeiten“, „ausführen“,
„weiterleiten“ oder ähnlich inhaltsleer paraphrasiert werden.

Die Doppelstellung `paiin/saiin + daiin` verlangt zwei Achsen:

```text
Kopf+aIII  = Stofftyp oder Charge III
d+aIII     = Dosis oder Maß III
```

Damit wird nicht zweimal dieselbe Menge wiederholt.

## 6. Historische Auswahl

Der historische Vergleich fragt nur, ob die vier Sachkategorien und ihre
Kombination mit Zustand/Grad um 1400 tatsächlich in technischen Handschriften
vorkommen. Salzburg UB M I 89 verbindet `pulvis` und `semen` im selben
zeitnahen Rezeptcodex. Wellcome MS.542 verbindet `lignum` und `radix`
ausdrücklich mit heiß/trocken und Gradangaben. Das macht das Bedeutungsmodell
historisch realistisch; es identifiziert kein Voynich-Zeichen als lateinische
Abkürzung.

## Ergebnisregel und Reichweite

Die Runde gilt als praktisch gewonnen, wenn:

1. die exakten Inventar- und Kontextzahlen reproduzierbar sind;
2. alle fünf Viererraster vollständig belegt sind;
3. alle zehn Spannen eine konkrete, nichtgenerische Lesung erhalten;
4. ein alter Kopfwert nur stehen bleibt, wenn die Komposition natürlich ist;
5. V11 unverändert vor den neuen, klar markierten V12-Zeilen bleibt;
6. Builder und unabhängiger Validator byteidentisch reproduzieren.

Der Versuch liefert eine konkrete, vorhersagbare Wortkopf-Arbeitstheorie. Er
liefert noch keine Phonetik, Sprache oder vollständige Manuskriptübersetzung.
