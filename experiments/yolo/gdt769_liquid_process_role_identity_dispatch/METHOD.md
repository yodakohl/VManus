# GDT769 method — Stoff, Vorgang, Produkt, Recordfeld oder Verbinder?

## Frage

GDT769 verfolgt die fünf vollständigen Formen `ol`, `ckhy`, `pcheey`, `ols`
und `otar` durch alle bereits zugelassenen Cache-Zeilen. Der Pass fragt zuerst,
welche praktische Rolle jede Form wirklich spielt:

1. messbarer Stoff oder Zubereitungskopf;
2. gerichteter Vorgang;
3. Produkt oder Resultat;
4. gebundenes Recordfeld;
5. interner Folgen- oder Feldverbinder.

Erst nach dieser Rollenentscheidung konkurrieren konkrete Lesungen wie
Pflanzensaft, Auszug, Dekokt, Arzneiwasser, Öl, Wein, Essig, Pulver,
Einweichen, Trocknen und Filtrat. Die fünfte Rolle ist notwendig, weil GDT625
für `otar` bereits `dann/danach/bis` als nicht widerlegte Alternative fand.
Ohne sie würde der Pass ein häufiges Mittelwort künstlich zu einem Stoff oder
Vorgang zwingen.

## Eingaben

- der von GDT764 geerbte, seitenbeschränkte semantische Cache und seine
  Drei-Leser-Exaktheit;
- GDT759s 96 exakte Mengenpaare und drei exakte `ols + Wert`-Spans;
- GDT764s neun exakte `X daiin`-Spans;
- die vollständigen Zustandswörter `cheo`, `cheor`, `sheo`, `sheor` sowie
  `oly` ausschließlich als vollständige Kontrollformen;
- GDT754s 172 quellkomponierte Formen und GDT737s 80 ausdrücklich
  quarantänisierte Kopfableitungen als Bedeutungsgeber-Sperre;
- GDT768s portable Inhaltsklassen für `cthy`, `chor` und `shor`, ohne die
  Richtung Blüte gegen Frucht/Samen zu importieren;
- periodennahe historische Registerbeispiele ausschließlich als
  Architektur- und Kandidatenquelle, nie als Buchstaben- oder Lautgleichung.

Es werden keine neue Seite, kein neues Bild und keine neue Transkription
geöffnet. `f84` und `f84r` bleiben gesperrt.

## 1. Exakter Target-Atlas

`src/core_atlas.py` zählt zuerst rohe Ganzformtreffer und behält für die
Auswertung nur Positionen, an denen ZL3b, IT2a und RF1b dieselbe vollständige
Form lesen. Für jedes Vorkommen werden D1-, R2- und Ganzzeilenansichten,
Zeilen-/Absatzgeometrie sowie gerichtete Nachbarn ausgegeben.

Ein Nachbar darf semantische Evidenz liefern, wenn er:

- reader-exakt ist;
- keine der fünf Zielformen ist;
- nicht zu den 172 GDT754- oder 80 expliziten GDT737-Sperrformen gehört;
- mehr als zwei Editierschritte von **jeder** der fünf Zielformen entfernt ist;
- im aktuellen Ganzwortbestand nicht als unsauber markiert ist.

Die weniger strenge Sperre nur um das jeweils aktuelle Ziel wird als
Sensitivitätszählung behalten, liefert aber keinen Identitätskredit.

## 2. Fünf Rollen

Die 16 beobachtbaren Rahmensignaturen stehen vollständig in
`src/FRAME_SIGNATURE_SPECS.tsv`. Dazu gehören Mengen- und Wertbindung,
Trocken-/Feucht-, Hitze-/Kälte- und Inhaltsnähe, gerichtete Prozessposition,
Endgeometrie, H1-`X daiin`-Felder sowie zwei eigens für `otar` bewahrte
Alternativen:

- F14: wiederholte mediale Scharnierposition mit unabhängigen Feldern auf
  beiden Seiten, aber ohne eigene Mengen-/Wertbindung;
- F15: Position zwischen zwei unabhängigen Zustandsgruppen, wobei die Richtung
  trocken→feucht, feucht→trocken, heiß→kalt usw. sichtbar bleibt.
- F16: unmittelbarer gerichteter Anschluss an eine bereits lizenzierte
  Mengenformel. Dabei bleibt getrennt, ob `ol`/`otar` die Menge einleitet oder
  ihr folgt; bloße Wiederholung eines häufigen Wortes zählt nicht.

Ein allgemeines `dann/weiter` darf verschiedene Zustandsrichtungen verbinden.
Die Forderung nach einem konsistent rechten Zielzustand gilt nur für engere
Lesungen wie `bis` oder einen konkreten Trocknungsprozess. Ebenso dürfen
Mengen- und Ergebnisachsen für eine Produktrolle nicht von getrennten
Fundstellen zusammenaddiert werden: sie müssen am selben Targetvorkommen und
nach Locus-Ausschluss erneut auf einer zweiten Seite gemeinsam auftreten.
Für die Verbinderrolle zählen F14-Seiten nicht zur Replikation: mindestens drei
Seiten müssen F14 lokal mit F15 oder F16 verbinden, und zwei solche Seiten
müssen nach Entfernung des stärksten locus bleiben. So kann bloße häufige
Mittelstellung kein Verbinderwort erzeugen.

Jedes Rollenmodell erhält positive und widersprechende Signaturen. Ein Modell
wird nicht durch seine frühere Arbeitslesung bevorzugt. Bei gleichwertigen
Modellen bleibt die Rollenmehrdeutigkeit sichtbar; der Renderer verwendet dann
den praktischsten ersetzbaren Default und nennt den engsten Rivalen.

## 3. Konkrete Identitäten

`src/IDENTITY_CANDIDATE_SPECS.tsv` enthält pro Zielform einen portablen
Nullwert und konkrete Karten. Die Kandidatenbank wurde bewusst über die vier
einfachen Flüssigkeitsnamen hinaus erweitert:

- Pflanzensaft oder ausgepresster Saft;
- Auszug oder Arzneiwasser;
- Infusion, Dekokt oder Absud;
- fertige Flüssigzubereitung;
- Filtrat oder Colatur;
- Öl, Wasser, Wein und Essig;
- Pulver oder Trockendroge;
- Paste, Salben- oder Mischform als Rivalen eines feucht eingeleiteten
  Zubereitungsfeldes;
- Einweichen/Mazerieren, Abseihen/Filtrieren und Trocknen;
- `dann/danach`, `bis` und ein neutraler Feldverbinder.

Das entspricht dem spätmittelalterlichen Praxisregister besser: ein
Pflanzenauszug kann gemessen, gekocht, reduziert, abgeseiht und anschließend
als *water* bezeichnet werden. Daher trennt ein bloßer Feuchtkontakt Wasser,
Wein, Essig, Saft und Dekokt nicht.

## 4. Zweite Achse und stärkster-Locus-Ausschluss

Eine konkrete Karte braucht mindestens zwei verschiedene Evidenzachsen, etwa
Menge + Pflanzeninhalt, Pflanzeninhalt + Hitze oder Wert + Ergebnisgeometrie.
Dann wird der einzelne stärkste stützende locus entfernt. Dieselbe notwendige
Kombination muss auf mindestens einer weiteren Seite weiterbestehen.

Diese Regel soll keinen interessanten Kandidaten aus dem Arbeitsdeck löschen.
Sie entscheidet nur, ob er schon den ausgegebenen Default ersetzen darf.
Nicht ausgewählte Karten bleiben mit ihren erfüllten und fehlenden
Vorhersagen sichtbar.

## 5. Praktischer Leser

Der Pass gibt neben Zensus und Scoreboards vollständige Zielzeilen aus. Jedes
Token erhält entweder einen bereits vorhandenen konkreten Ganzwortdefault oder
einen neuen ausdrücklich ersetzbaren Default mit Rivalen. Strukturelle Tags
bleiben von englischen oder deutschen Wortübersetzungen getrennt. Unbekannte
Tokens werden nicht durch universelle Prosa wie „Arbeitsgut bearbeiten“
verdeckt.

## Entscheidungs- und Behauptungsgrenze

Ein ausgewählter Default ist die derzeit beste konkrete Arbeitstheorie, keine
bestätigte Übersetzung. GDT769 darf Rollen und konkrete Ganzwortkandidaten
verschieben, wenn deren vorhergesagte Rahmen außerhalb des stärksten locus
wiederkehren. Der Pass darf kein EVA-Zeichen als lateinischen Anfangsbuchstaben,
Laut oder Morphem lesen und keine Bedeutung von `ol` auf `ols`, von `p` auf
`pcheey` oder von irgendeinem sichtbaren Teilstring auf eine andere Ganzform
übertragen.

Bestätigte Lexeme, Klartext, Sprache, Chiffre, produktive Komponenten,
Pflanzenarten, Krankheiten und Heilbehauptungen bleiben außerhalb der
zulässigen Aussage.
