# GDT634 — Methode der konkreten Kern- und Endstellenlesung

## Frage

Kann die in GDT633 konsolidierte Qualitäts-, CTH-, E-Längen-, O- und
Mengenstruktur so mit konkreten pharmazeutischen Wortköpfen verbunden werden,
dass acht bereits ausgewählte Mikrozeilen ohne semantische Leerstellen lesbar
werden? Gesucht wird ausdrücklich keine generische Prozessparaphrase, sondern
für jede sichtbare Form eine kurze Bedeutung wie Pulver, Salz, Wurzel,
Flüssigkeit, Blattgut, Portion, heiß, kalt, trocken oder feucht.

## Material und Schutzgrenze

Verwendet werden ausschließlich acht schon in früheren Experimenten sichtbare
Zeilen von f20v, f22v, f29r, f80r, f80v, f82v, f85r1 und f114v. Es werden
keine neuen Seiten und keine neuen Bilder geöffnet. f1r ist ausgeschlossen;
f84 und f84r sind verboten.

Die beiden gemischten Transkriptionsquellen werden durch den in GDT633
veröffentlichten Guard mit expliziter Seiten-Allowlist projiziert. ZL3b, IT2a
und RF1b sind alternative Leser desselben Manuskripts, nicht drei unabhängige
Texte. Leserübereinstimmung wird als Stabilitätsmerkmal geführt und niemals
als dreifache Häufigkeit gezählt.

Das erlaubte Korpus enthält 179 Seiten, 32.339 ZL3b-Token und 4.137
leserübergreifende Zeilen. Der Builder verwirft alle nicht erlaubten sowie
alle verbotenen Selektoren vor der Materialisierung weiterer Spalten.

## Pass 1 — vollständige Zielpopulation

Die acht Zielzeilen werden wortgetreu als 69 Positionen und 58 verschiedene
Oberflächenformen ausgegeben. Für jede Position werden festgehalten:

```text
Oberfläche | strukturelle Zerlegung | deutscher Default | Evidenzbasis |
Konfidenz | lebender Rivale | Korpusfrequenz | Leserstabilität
```

Eine Zeile gilt nur dann als vollständig, wenn jede Position einen primären
Sach-, Zustands-, Qualitäts-, Teil- oder Mengenwert besitzt. „Arbeitsgut“,
„bearbeiten“, „ausführen“ und ähnliche bedeutungsleere Verben sind keine
zulässigen Defaults.

## Pass 2 — geerbte produktive Schicht

Die folgenden Werte werden aus dem publizierten Wörterbuch V10 übernommen:

```text
k          heiß
t          kalt
ch         trocken
sh         feucht
cth        Drogenmaterial; im Herbal Blatt-/Krautgut
äußeres e  attributive Bindung
e/ee/eee   sichtbare Bindungs- oder Formstufen
y          Grund-/Schlussform
aiin       Wert oder Menge III
o+cth      Zubereitung/Ansatz aus CTH-Material
ol         Material-/Substanzträger
or         Teil-/Portionsträger
```

Die große Endfamilie
`(∅|o|qo)+(k|t|ch|sh)+e{0..3}+d?+y` wird unabhängig neu gezählt. Sie umfasst
4.950 Token, 75 Typen und 176 Seiten; 3.612 Vorkommen sind in allen drei
Lesern exakt stabil. Die vier E-Längenstufen besitzen 907, 2.275, 1.663 und
105 Vorkommen. Damit werden Zielwerte wie `qokeedy`, `qokeeedy`, `otedy`,
`cheody` und `chedy` nicht jeweils als unabhängige Ganzwörter erfunden.

## Pass 3 — konkrete pharmazeutische Wortköpfe

Vier Anfangszeichen erhalten aggressive, aber kurze lateinische
Arbeitshypothesen. Ein finales `p` wird ausdrücklich separat behandelt:

```text
p- initial  = pulvis  → Pulver
-p terminal           → Pulverform (separate LOW-Hypothese)
s- initial  = sal     → Salz; semen/Samen bleibt Rivale
r- initial  = radix   → Wurzelstoff
l- initial  = liquor  → Flüssigkeit oder Flüssigpräparat
```

Diese Werte behaupten keine identischen historischen Siglen und keine
lateinische Lautentschlüsselung. Sie werden eingesetzt, weil sie im
Arzneiwortschatz um 1420 passende konkrete Kategorien liefern und weil die
Voynich-Formen produktiv weitere bekannte Slots aufnehmen. Das finale `p` in
`chep` wird nicht aus der Verteilung des initialen `p` hergeleitet. Ebenso ist
das `s` in `posaiin` kein belegter interner SAL-Kopf: `posa` bleibt dort ein
gelerntes Ganzwort mit Salzpulver-Default und Samenpulver-Rivale; IT2a liest
stattdessen `poraiin`.

Für jeden Kopf werden Wert-, L/R-Träger- und Träger-plus-Wert-Formen gezählt.
Zusätzlich wird geprüft, wie oft das Entfernen des Anfangskopfes eine
belegte Restform erzeugt. Bei `p` besitzen 395 von 503 präfigierten Vorkommen
einen belegten Rest ohne `p`; 360 dieser Vorkommen stehen zeileninitial. Das
stützt einen hinzufügbaren Produktkopf. Die entsprechende Statistik wird auch
für `s`, `r` und `l` ausgegeben, ohne gleiche Semantik daraus zu erzwingen.

## Pass 4 — L/R-Träger und sichtbare Vokale

`al/ol` werden als L-Materialfamilie, `ar/or` als R-Teilfamilie behandelt.
Das `a/o` wird nicht gelöscht:

```text
qokal = qo + k + a + l   heiße Substanz
qokar = qo + k + a + r   heiße Portion / heißer Teil
qokol = qo + k + o + l   anderer O-L-Materialträger
qokor = qo + k + o + r   anderer O-R-Teilträger
```

Im erlaubten Korpus existieren 115 Körper sowohl mit `al` als auch `ol` und
131 Körper sowohl mit `ar` als auch `or`. Das erlaubt die gemeinsame
Material/Teil-Polarität, verlangt aber weiterhin einen eigenen Wert für den
vorangehenden Vokal. `oraiin` wird unmittelbar als Portion III gelesen;
`olor` als Materialportion oder Zutat.

## Pass 5 — Kompositionskontrollen

Zehn konkrete Lesungen werden auf das Vorkommen der vorab genannten
Formvarianten geprüft:

- `chep/shep/chepy/shepy`: ein terminaler P-Körper trägt trockene und feuchte
  Formen; dies belegt keine Identität mit initialem `p`;
- `dalkedy/daltedy`: derselbe AL-Körper trägt heiß/kalt;
- `dalchedy/dalshedy` und `dolchedy/dolshedy`: derselbe Träger trägt
  trocken/feucht;
- `qokeeo/qoteeo`: terminales O bleibt unter heiß/kalt erhalten;
- `olkam/oltam`: derselbe M-Schluss bleibt unter heiß/kalt erhalten;
- P- und S-Wert-/Trägerraster: Pulver und Salz bilden mehrere Komposita.

Acht der zehn Listen enthalten mindestens zwei der genannten Formen. Der
Status heißt deshalb `MULTIPLE_LISTED_FORMS_ATTESTED`, nicht „semantisch
bewiesene Gegenform“; identischer Kontext wird damit nicht behauptet. Nur
`rcheald/rsheald` und `lkealy/ltealy` sind einseitig belegt. Wurzel und
Flüssigkeit bleiben an diesen Stellen LOW.

## Pass 6 — Lesergrenzen statt erfundener Wörter

Alle acht Zielzeilen werden in ZL3b, IT2a und RF1b nebeneinandergestellt.
Vier Leserunterschiede ändern die konkrete Lesung:

- f29r: `posaiin` in ZL3b/RF1b gegen IT2a `poraiin`; die Ausgabe zeigt beide
  Bedeutungen statt eine Variante zu verstecken;
- f80v: ZL3b `qotainol` gegen IT2a/RF1b `qotain | ol`;
- f114v: `cheo | ctheey` gegen die Fusion `cheoctheey`;
- f85r1.21: ZL3b `daiir` gegen IT2a/RF1b `daiin`, daher nur an diesem
  Zielort Maß III; acht andere `daiir`-Loci sind dreileser-exakt und bleiben
  global offen.

Die automatische Zahl 53 ist enger als diese manuelle Liste: Sie zählt nur
ZL-Oberflächen, die in allen Lesern exakt oder durch Zusammenziehen einer
Spaltung in einem anderen Leser rekonstruierbar sind. Gegenüber 51 exakten
Zielpositionen gewinnen dabei nur `saiin` und `qotainol`. Inverse Fusionen
und Glyphgabeln werden in `CROSS_READER_READING_EVIDENCE.tsv` separat geführt.

## Pass 7 — finales m

Das bereits in GDT044 erkannte terminale M-Profil wird im aktuellen Korpus
neu gezählt. 591 von 838 m-finalen Token stehen am Zeilenende; bei `olkam`
sind es 8 von 11. Deshalb erhält `m` keinen erfundenen Stoffwert und wird auch
nicht gelöscht. Es bleibt als **[terminal-M, Funktion unbekannt]** sichtbar,
während `ol+k+a` als heißes Material gesprochen wird.

## Ergebnisregel und Reichweite

Der Versuch ist erfolgreich, wenn:

1. alle 69 Tokenpositionen eine nichtleere Primärglosse ohne verbotene
   generische Prozessphrase erhalten und Rivalen in einem eigenen Feld stehen;
2. die produktiven Familien aus dem erlaubten Korpus reproduzierbar sind;
3. Lesergrenzen explizit bleiben;
4. aggressive Wortköpfe getrennt von geerbten Strukturwerten markiert sind;
5. V10 mitsamt seinen Kontextregeln unverändert am Anfang von V11 bleibt;
6. der Builder und ein unabhängiger Validator byteidentische Artefakte
   reproduzieren.

Er identifiziert noch keine Sprache, Lautwerte, Pflanzenart oder universelle
Übersetzung des Manuskripts. Die acht Zeilen bilden eine konkrete
Vollglossierung, an der die vier Wortköpfe im nächsten Schritt durch
gleichkörperige Austauschreihen weiter verbessert oder ersetzt werden können.
