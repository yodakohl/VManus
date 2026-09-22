# RAW370 V2: unabhängige Prüfung von Materialvertrag und vier Handverläufen

2026-09-22. Geprüft wurden ausschließlich die eingefrorenen
[V2-Handverläufe](../proposals/raw370_powder_partition_v2_material_contract_20260922.md),
das [V2-JSON](../proposals/raw370_powder_partition_v2_material_contract_20260922.json)
und seine bereits bekannten V1-Bindings. Kein ausgewählter f4r-Text, anderer
Absatz, neues Bild, Corpuslauf oder Simulator wurde geöffnet beziehungsweise
ausgeführt. Die Originaldateien wurden nicht verändert.

**Ergebnis:** Kein neuer zwingender Widerspruch der vollständigen CARRY-
Handfolge nachgewiesen. V2 ersetzt die beiden zuvor offenen Materialregeln
durch ausdrücklich neue globale Annahmen. REITERATED bleibt innerhalb dieses
Vertrags widersprüchlich; FRESH und TWO bleiben erhaltene Alternativen. Die
Eigenschaftsfortschreibung bei Wasserzugabe ist noch nicht vollständig
formalisiert. Dies ist eine begrenzte Vertragsprüfung, kein Bedeutungs-PASS
und kein Nachweis einer vollständigen chemisch-physikalischen Simulation.

## Identität der eingefrorenen Bestandteile

Die vorgegebenen Hashes stimmen:

- JSON: `7676250faf7adabc2fd240635a520852c65c2d7a2f8070fb82717351a8ab6d78`.
- Markdown: `c90de002dde795dc35502e7d32692515459859e49e323fc51865b7fcf4110a61`.

Die Bindings von V1-JSON, Autorenklarstellung und V2-Markdown stimmen ebenfalls.
Alle zehn `unchanged_inherited_blocks` sind strukturell exakt gleich den
entsprechenden V1-Blöcken; ihre kanonischen SHA256 stimmen. Das umfasst alle
65 Primäreinträge, 15 Alternativformannahmen, 238 Positionszuordnungen,
vollständigen ursprünglichen Lesungen, 18 Produktionen und drei Rivalenblöcke.
Die Gleichheit der sprachlichen Einträge bedeutet ausdrücklich **nicht**,
dass ihre gesamte operative Interpretation unverändert geblieben wäre.
V2 deklariert die Änderung der Materialeffekte und Kompatibilität selbst.

## Globale Regeln und konkrete Stellen

| Regel / Stelle | Unabhängiger Befund | Einordnung |
|---|---|---|
| `nominal_compatibility.POWDER`, Default; f21r.12 RETRIEVE | POWDER verlangt nun ausdrücklich freie, eigenständige Fein-Pulverform; Grobgut/F/G/ganze Paste sind ausgeschlossen. Deshalb passt P und nicht der zuletzt gelagerte C. Das frühere Ziel ist kein Materialknoten. | V1-Lücke durch neue geschlossene Typannahme entschieden; kein aus Wortform oder Objektverschiedenheit gewonnener Bedeutungsbeleg. |
| `access_by_role`; f32v.8–10 | Die Bestandsliste darf Komponenten des noch ungetrennten B beschreiben; SEPARATE macht C/P zu freien Zweigen. C und später P sind nach SORT beziehungsweise KNEAD keine zusätzlich verfügbaren Elternvorräte. | Die getrennten Zugriffsrollen verhindern Doppelzählung und erneutes Ausgeben bereits verbrauchten Materials. |
| `KNEAD`, `WITH_MEDIUM`; f32v.10–11 | T enthält P/W/O; diese Komponenten sind nicht mehr frei. WITH_MEDIUM erreicht das enthaltene Wasser ausdrücklich, ohne es freizugeben. Derselbe Zugriff erlaubt keine beliebige erneute Pulverentnahme. | Kohärente Rollenunterscheidung, neu präzisiert und global formuliert. |
| `GRIND`, `FORM_UPDATE`; f32v.11 | GRIND wirkt auf den Feststoffanteil, erhält T sowie W/O. Bei c=0 folgt aus 0≤a≤c zwingend a=0; kein neuer Grobanteil entsteht. Die freie Endmenge bleibt F+G+T, nicht F+G+P+T. | Die frühere unqualifizierte Erzeugung beider Grade wurde substanziell zurückgenommen; kein ortsbenannter Ausnahmefall. |
| `CRUSH/GRIND`; f21r.8/.10 | Beide Größenanteile sind nicht automatisch positiv. Die später benannten C/P und die Zielmenge erfordern c1>0 und p1≥Q. M>Q folgt daraus und aus M=c1+p1. | Bedingte Anforderung an Ausgangsmaterial und Verarbeitung; kein zuvor geschriebenes oder gemessenes M. |
| `SIEVE`; f21r.12 | U=Q und V=p1−Q bleiben disjunkte Teile des früheren P. Beide dürfen bezüglich des älteren Grenzwerts fein sein; ein Nullrest erzeugt keinen Knoten. | Keine Kopie der vollen Eingangsmasse und keine erzwungene Herstellung grober Teilchen aus Feinmaterial. |
| `SORT`, `sieve_limit`; f32v.9 | Zwei positive grobe Produkte benötigen einen passenden weiteren Sortierparameter. Ein unveränderter perfekter Binärschnitt auf seinem eigenen Grobrückstand genügte nicht. Der Vertrag setzt diese gemeinsame Schnittidentität aber gerade nicht. | Offengelegte physische Beleglücke, keine aus dem Vertrag folgende Unmöglichkeit. Die passenden Parameter sind nicht unabhängig bestimmt. |
| `global_frame_and_water_accounting`; f21r.9 | RINSE kann h1>0 hinterlassen. Die allgemeine Regel erhält nicht ausdrücklich geänderte Eigenschaften, ohne DRY_STATE mit dem Wasserzustand formal zu verknüpfen oder das Flag ausdrücklich zu löschen. | Verbleibende Zustandsableitungslücke; genauer unten. |

Die Bezeichnungen A/B/C/P sind ausdrücklich Provenienz-/Zustandsnamen,
keine verborgenen Ortsselektoren. PREPARED_BULK kann als Vorbereitungsrolle
auch einen nur groben oder nur feinen Bestand treffen. In den beiden
vorliegenden CARRY-Verläufen erzwingen erst die späteren positiven
Teilbestände tatsächlich einen gemischten B. Das ist keine automatische
Wirkung von CRUSH. Künftige Kontexte könnten mehrere freie Pulverbestände
enthalten; die geschlossene Tabelle beweist für solche Kontexte keine
allgemeine Eindeutigkeit. In den hier geprüften Rücknahmen ist nur P passend.

## Vier vollständige Verläufe und minimale Abhängigkeiten

**f21r, alle vier Einstellungen:** Erwerb, Trocknen, Zerkleinern, prospektives
Ziel, Spülen, Ausbreiten, erneutes Trocknen, Mahlen, Trennen, zweimaliges
Aufbewahren, Abdecken, getrenntes Lagern, Wiederaufnahme und abschließendes
Sieben sind erfasst. Die Rivalen ändern hier keine vorkommende Konstruktion.
Die Handbilanz ist c1+Q+(p1−Q)=M mit c1>0 und p1≥Q. Wasser wird getrennt
geführt und nach Trocknen beziehungsweise Abfluss nicht zum freien Vorrat.
Das Ziel wird erst an U geprüft; es stellt nie selbst Pulver bereit.

**CARRY_ADD, f32v:** Die .8-Bestandsangabe verlangt C=2Q, P=Q und damit N=3Q.
N=3Q steht nicht schon in .7; `dain` bleibt THOROUGHLY. Die .9-Produkte F/G
haben je Q, P bleibt für die Paste. Nach .11 bestehen F=Q, G=Q und T-solid=Q;
W/O sind erhaltene andere Komponenten. Minimal benötigt dies die festen
Besitzer, erschöpfende disjunkte Teilungen, gemeinsame positive Einheit,
keine zusätzliche Pflanzenfeststoffzufuhr und Nullverlust im 3Q-Intervall.

**FRESH_INPUT_LISTS:** Die ersten vier Operationen erzeugen B:N, das später
unbenutzt bleibt. .8 führt E=3Q zu, .10 zusätzlich P′=Q. SEPARATE, LIFT_OUT,
SORT, KEEP, KNEAD und WITH_MEDIUM/GRIND erhalten dann insgesamt
B:N+P:Q+F:Q+G:Q+T-solid:Q=N+4Q. Keine Verdoppelung durch Enthaltensein;
P′ gehört zu T und wird nicht daneben gezählt. Die zusätzliche Zufuhr ist
die explizite Rivalenregel. Ohne weitere Vollverbrauchsbehauptung bleibt
dies eine kohärente, materiell andere Lesung.

**REITERATED_QUANTITY_ASSERTION:** Bis .8 entsteht C=Q, P=Q. Die erste
unvereinbare Nachbedingung ist die vollständige .9-SORT/KEEP-Konstruktion:
f+g≤Q aus unvermehrtem Eingang, aber f=g=Q und Q>0. Die Trennung von
SORT-Zwischenzustand und nachfolgender KEEP-Mengenbedingung im Handkonto
ändert diesen gemeinsamen Klauselwiderspruch nicht. Nach .9 gibt es keinen
erreichbaren vollständigen Erfolgszustand; spätere Wörter werden richtig
erhalten, ohne ihre Ausführung vorzutäuschen. Der Beweis benötigt weder die
finale Nassmahlregel noch einen gemessenen Anfangswert noch Nullverlust.

**TWO_EQUAL_PORTIONS:** C enthält zwei Portionen Q. Für 0≤a≤Q erhalten F
die Beiträge a und Q−a, G die komplementären Beiträge Q−a und a. Jede
Ursprungsportion trägt insgesamt Q bei; jedes Produkt wiegt Q. C wird beim
Sortieren nicht als zusätzlicher Bestand mitgezählt. Kein späterer Ausdruck
identifiziert eine Ursprungsportion einzeln. Die Gesamtbilanz und die
anschließende Paste stimmen deshalb mit ADD überein; V2 trennt die beiden
Hypothesen weiterhin nicht.

## Verbleibende Grenze der Eigenschaftsfortschreibung

Die f21r-Handfolge lässt nach RINSE 0≤h1≤w zu. Bei h1>0 und der zusätzlichen
Interpretation DRY_STATE iff kein zurückgehaltenes Wasser würde ein rein
mechanisch fortgeschriebenes altes DRY-Flag veraltet sein. Der Vertrag sagt
noch nicht ausdrücklich, ob DRY_STATE aus Komponenten berechnet oder als
eigenständiges Prädikat aktualisiert wird. Eine automatische Löschregel wurde
in dieser Prüfung nicht ergänzt. Dasselbe allgemeine Problem betrifft die
saubere Trennung von Komponenten-, Träger- und abgeleiteten Eigenschaften;
es rechtfertigt keinen Anspruch auf einen bereits vollständigen Simulator.

Dies erzwingt **keinen Gesamtwiderspruch der vorhandenen Handfolge**: h1=0
ist erlaubt, und vor dem trockenen Endziel folgt auf .10 ausdrücklich DRY.
Die f32v-Nassmahlung behauptet weder Wasserverlust noch trockene Gesamtpaste.
Die neue Trägerregel bleibt deshalb brauchbar, während eine spätere formale
Zustandsausführung die Attributableitung ausdrücklich festlegen müsste.
Keine ortsbezogene Reparatur oder Änderung anhand eines weiteren Absatzes
ist damit autorisiert oder durchgeführt.

Die beiden ursprünglichen Materiallücken sind in V2 als neue Hypothesen
adressiert. Die physische Eignung von Wurzelmaterial, Werkzeugen und Parametern,
die Wortwerte, die Klauselwahl und das konservative Stoffkonto bleiben
unbestätigt. Null bestätigte Wörter; kein unabhängiger Bedeutungsbeleg.
