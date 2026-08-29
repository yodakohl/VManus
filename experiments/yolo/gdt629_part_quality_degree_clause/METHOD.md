# GDT629 method

## Question

Sind `choldaiin` und `chol daiin` am selben physischen Manuskriptspan
alternative Wortgrenzen derselben technischen Phrase? Bildet ein unmittelbar
vorangehendes `chor` zusammen mit dieser Phrase die kleinste vollständige
Teil–Qualität–Grad-Klausel, und welche Gegenlesung bleibt übrig?

## Inputs

Der Lauf benutzt ausschließlich acht bereits in GDT628 zugelassene Seiten und
Loci: f2r.10, f17v.8, f21r.12, f27r.6, f32v.10, f49r.6, f58r.18 und f100r.22.
Die Kreuztranskription wird mit `vmanus-exp query-tsv`, einer expliziten
Seiten-Allowlist und projizierten Spalten gelesen. f1r ist ausgeschlossen;
f84 und f84r bleiben vor Materialisierung verboten. Es wird kein Bild und
keine neue Seite geöffnet.

GDT628 liefert alle 43 `chol`-Wertrealisierungen, die terminalen Kontexte, das
OL/OR-Modell und V5. GDT625 liefert die `cth`-Partfamilie, GDT623 die
Qualitätskerne und GDT627 sechs historische Syntaxvergleiche. ZL3b, IT2a und
RF1b werden als alternative Lesungen desselben Manuskripts ausgewiesen, nicht
als drei unabhängige Belege gezählt.

## Method

1. Suche an jedem der acht vorregistrierten Loci in jeder Leserfassung exakt
   eine der Formen `cholaiin`, `choldaiin`, `chol daiin`, `cholchaiin` oder
   `chol chaiin`.
2. Speichere sichtbare Segmentierung, normalisierte Oberfläche, linken und
   rechten Rest sowie einen unmittelbar vorangehenden bekannten Partanker.
3. Nenne einen Fusions-/Trennungsbridge nur dann exakt, wenn zwei Leser am
   selben physischen Span nach Entfernen genau dieser Wortgrenze dieselben
   Zeichen haben. f27r.6 wird deshalb separat als semantische Leservariante
   geführt: IT2a/RF1b enthalten ein zusätzliches `ch`.
4. Nenne eine vollständige Part–Qualität–Grad-Klausel nur, wenn `chor`
   unmittelbar vor dem registrierten Trocken-III-Ausdruck steht. Alle Tokens
   außerhalb dieser kleinsten Klammer bleiben sichtbar und `OPEN`.
5. Rückklassifiziere alle 43 GDT628-Kontexte als vollständige Partklausel,
   Qualitätsphrase mit nahem Part oder bloße Qualitätsphrase. Die
   ursprüngliche Stabilität wird unverändert übernommen.
6. Weise jedem der 65 Tokens der acht ZL3b-Zielzeilen einen Defaultstatus zu.
   Nur bereits kompositorisch belegte Formen erhalten eine konkrete Lesung;
   unbekannte Formen heißen ausdrücklich `OPEN` und bekommen keinen
   generischen Ersatz wie „Arbeitsgut“ oder „ausführen“.
7. Merge V5 byte- und feldgetreu als die ersten 28 Zeilen von V6 und ergänze
   vier Klausel-/Grenzeinträge.

## Decision rule and claim ceiling

Primäre Arbeitslesung:

```text
chor chol daiin = Pflanzen-/Reproduktionsteil: trocken, Grad III
```

Sie wird von zwei verschiedenen, dreifach exakt gelesenen Loci getragen. Die
getrennte Form behält die Gegenlesung „Pflanzenteil/Trockenmaterial: drei
Portionen“, weil `daiin` außerhalb eines OL-Qualitätskopfs auch einen
Mengenwert tragen kann. `choldaiin = chol daiin` wird nur als Wortgrenzen-
Äquivalenz beansprucht; daraus folgt noch kein fusionierter Partanker.

Der Lauf identifiziert weder Sprache noch Lautwerte und übersetzt keine
ganzen Zielzeilen. Er liefert eine konkrete, kompositionell vorhersagbare
Klausel und markiert jeden verbleibenden Slot offen.
