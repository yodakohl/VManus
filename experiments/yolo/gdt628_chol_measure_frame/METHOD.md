# GDT628 method

## Question

Ist `chol` ein gelerntes Stoffwort vor einer Menge, eine Maßeinheit oder die
komponierte `ch+ol`-Form eines produktiven Qualitätsparadigmas? Wenn die letzte
Lesung trägt: Drückt `chol d-WERT` einen Trockenheitsgrad I–IV aus, und wie
verhält sich diese getrennte Schreibung zu direkten und fusionierten Formen?

## Scope and inputs

Der Lauf benutzt die 179-seitige GDT627-Allowlist. `f1r` und jedes `f84*`
bleiben ausgeschlossen. Die zwei Transkriptionsquellen werden ausschließlich
über `vmanus-exp query-tsv` mit expliziter Seiten-Allowlist und projizierten
Spalten gelesen. Es wird kein Bild und keine neue Seite geöffnet.

Die Qualitätswerte `k=heiß`, `t=kalt`, `ch=trocken`, `sh=feucht` kommen aus
GDT623; die produktiven Qualitätshüllen aus GDT624; die `cth`-Pflanzenteil-
Familie einschließlich `cthar` aus GDT625; die I–IV-Wertarchitektur, historischen
Syntaxvergleiche und visuellen Notizen aus GDT627.

## Construction

1. Registriere die 54 exakten Oberflächen aus drei Wrappern (`bare/o/qo`),
   neun Kernen (leer sowie `k/t/ch/sh/kch/ksh/tch/tsh`) und den Endungen
   `ol/or`. Materialisiere jedes Vorkommen samt Leser-Stabilität.
2. Suche für jede vorgesehene Alternation dieselbe physische Zeile. Weise
   ausdrücklich aus, ob die Formen nur zeilengleich oder wirklich adjazent
   sind. „Lokal“ bedeutet deshalb nie automatisch „Nachbarwort“.
3. Zähle exaktes `chol`, alle Oberflächen mit `chol` als Substring und trenne
   exakte Form, linke/rechte Randerweiterung sowie interne Treffer.
4. Registriere für jede der 54 Basen und jeden Wert I–IV drei Schreibwege:

   ```text
   BASE+a+WERT       direkte Form
   BASE+d+a+WERT     fusionierte d-Form
   BASE | d+a+WERT   getrennte d-Form
   ```

5. Für Zweiwortphrasen gilt Stabilität nur, wenn die vollständige adjazente
   Folge mit ausreichender Häufigkeit in ZL3b, IT2a und RF1b vorkommt. Zwei
   einzeln stabile Wörter reichen nicht.
6. Trenne `ol`-Qualitätsköpfe von `or`-/Pflanzenteilköpfen. Nach einem
   kernhaltigen `ol`-Kopf wird `d-WERT` als Qualitätsgrad gelesen; bei `or`
   bleibt Menge/Portion oder Grad sichtbar offen.
7. Klassifiziere die dreizehn terminalen `chol d-WERT`-Zeilen nach ihrem
   lokalen Kontext als `QUALITY_ANCHORED`, `QUALITY_OR_DOSE` oder
   `MULTI_CLAUSE_REQUIRED`. Diese Klasse ändert nicht den Wörterbuchdefault,
   sondern zeigt, wie viel die einzelne Zeile selbst beiträgt.
8. Merge alle fünfzehn Einträge des GDT627-Wörterbuchs in V5 und ergänze die
   dreizehn neuen `ol/or/chol`-Einträge. V5 ist ein konsolidierter Leser, kein
   unmarkiertes Delta.

## Working decision

```text
QUALITY_CORE + ol       = Qualität/Zustand; ol meist flüssig null
ch + ol                 = trocken; nominal trockenes Gut
OL_QUALITY + d + WERT   = Qualität im Grad I–IV
OR/PART + d + WERT      = Teil/Stoff mit Menge oder Grad I–IV
```

Die primäre Lesung gewinnt wegen des kernhaltigen `ol`-Gitters, der parallelen
heiß/kalt/feucht-Formen und der direkten/fusionierten/getrennten Wertwege. Eine
Dosis aus Trockenmaterial bleibt als nominale Nebenlesung erhalten.

## Claim ceiling

GDT628 ist eine konkrete Arbeitsübersetzung für diese Familie, keine
Behauptung, das ganze Manuskript gelöst zu haben. Es identifiziert keine
Sprache, keinen Lautwert und keine absolute Maßeinheit. Die `or`-Endung ist
nicht generell übersetzt; `chor/shor` behalten ihre gelernten
Pflanzenteillesungen. Die historische Galenik zeigt, dass das Modell zeitlich
und fachlich plausibel ist, nicht dass eine Voynich-Oberfläche lateinisch ist.
