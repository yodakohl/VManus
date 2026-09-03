# GDT772-Methode — erweiterter maskierter `ol`-Zweig

## Praktische Frage

GDT770 bevorzugte für `ol` roh einen Positionsdispatch: nach einer linken
Menge oder einem linken Wert `von/aus`, sonst zwischen zwei Feldern `und/mit`.
Der erste Zweig kam in der damaligen Kohorte jedoch keinmal vollständig vor.
GDT771 fand im bereits zugelassenen Vollzeilen-Cache sieben vollständige Fälle
auf sechs Seiten.  GDT772 fügt genau deren sieben Zeilen hinzu und lässt
ansonsten Kandidaten, Binder, Strafen und Gewinnerhürden unverändert.

## Kohorte und gleichzeitige Maske

Die fünfzehn GDT770-Zeilen bleiben unverändert. Hinzu kommen ausschließlich:

- `f112r.36`, `f30v.2`, `f75r.26`, `f81r.15`, `f81r.22`, `f82r.33` und
  `f85r1.21`;
- ihre 55 bereits gecachten Token;
- sieben von GDT771 vollständig typisierte `ol`-Brücken;
- drei weitere exakte `ol` derselben Zeilen als nicht handverlesene
  Gegenfälle.

Damit umfasst die erweiterte Kohorte 22 Zeilen und 27 Zielmasken:
`ol=15`, `ckhy=4`, `ols=3`, `otar=5`.  In jeder Zeile werden alle exakten
Vorkommen der vier Zielformen gleichzeitig maskiert. Die drei zusätzlichen
Gegenfälle sind:

- `f75r.26@5`: linker Wert, aber keine typisierte rechte Pflichtkante;
- `f81r.22@4`: rechter Wert, aber keine typisierte linke Kante;
- `f81r.22@6`: linker Wert und rechter Mengen-/Wertposten, aber keine für den
  linken Relatorzweig zulässige rechte Feld-/Stoff-/Prozesskante.

Die neue Tokengeometrie wird nicht aus einer ungeschützten Gesamttabelle
gelesen. Der Runner fragt den gemischten GDT734-Zellcache mit den sieben
expliziten Locus-Allow-Werten und genau den benötigten Spalten über
`./vmanus-exp query-tsv` ab. `f84` und `f84r` sind als Selektoren verboten.

## Rollen und praktischer Reader

`src/NEW_EDGE_ROLE_SPECS.tsv` enthält nur die sechzehn unmittelbaren
target-unabhängigen Nachbarrollen, die GDT771 bereits als Wert/Menge oder als
zulässige rechte Feld-, Zubereitungs- oder Prozesskante ausgewiesen hat. Eine
Qualitätsstufe wird dabei nicht still zu `FIELD`, und `KNOWN_OTHER` nicht zu
irgendeinem Inhaltswort. Alle übrigen neuen Zellen sind für den Scorer
untypisiert.

GDT734s alte Anzeigen mit Samen-, Saatgut-, Holz- oder pauschaler
Drogenstoff-Prosa werden in den sieben neuen Zeilen vor der Ausgabe durch
`src/RERENDER_OVERRIDE_SPECS.tsv` ersetzt. Diese Korrekturen beeinflussen den
Score nicht. Sie dienen nur einem lesbaren Arbeitsvergleich der drei
`ol`-Modelle.

## Unveränderter GDT770-Score

GDT772 importiert bytefest die GDT770-Dateien:

- `CANDIDATE_POLICY_SPECS.tsv`;
- `PENALTY_SPECS.tsv`;
- `WINNER_GATE_SPECS.tsv`;
- `model.py`, `scoring.py` und die aggregierenden Scorefunktionen aus
  `run.py`.

Die erwarteten Hashes stehen in `src/SCORE_CONTRACT_LOCK.tsv`. Abweichungen
brechen den Lauf ab. Es gibt weiterhin keinen Lesbarkeits-, Geschichts-,
Häufigkeits- oder Deutschscore. Gewertet werden nur unmittelbare exakte
Rollenbindungen, dieselben `+6/+5/+4/+3/+2/+1`-Strafen, dieselben
Seiten-Holdouts und dieselben acht Gewinnerhürden.

Neben dem Gesamtturnier wird der `ol`-Kontrast fallweise ausgegeben:
Positionsdispatch, invariantes `Ansatz/Basis`, invariantes messbares
`Produkt/Resultat` und `OPAQUE_NULL`. So bleibt sichtbar, ob ein Gesamtvorsprung
von den sieben Vollfällen oder von den drei automatisch mitgeführten
Gegenfällen stammt.

## Entscheidung und Grenze

Es gilt exakt die GDT770-Regel. Ein Nicht-NULL-Modell muss unter anderem jeden
Rivalen um mindestens vier Strafpunkte schlagen, beide Positionszweige auf je
zwei Seiten tragen und in jedem Leave-one-page-out-Fold allein vorne bleiben.
Ein Gleichstand geht an NULL.

Ein möglicher Sieg bezeichnet nur die nützlichste kohortenlokale
Ganzwort-Policy. `von/aus`, `Ansatz/Basis`, `Produkt/Resultat`, Öl, Wasser,
Wein oder irgendeine historische Substanz erhalten dadurch keinen Lexem- oder
Übersetzungskredit. Komponentenexport, EVA-zu-Latein-Kredit und bestätigter
Klartext bleiben null. Es wird keine neue Manuskriptseite, kein Bild, keine
OCR und keine neue Transkription geöffnet.
