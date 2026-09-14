# W77: otchy bleibt zwischen Stoff- und Eigenschaftsrolle offen

**Otchy lässt sich nicht allein aus den Eingabeplätzen von W76 als Stoffwort festlegen.** Die vollständigen erfassten Zeilen erlauben sowohl eine Gegenstandsnennung als auch eine Eigenschaft bei einem anderen Gegenstand. Der neue Vergleich erhält beide Rollen an sämtlichen117otchy-Lesepositionen; kein Stoffname oder Temperaturwert wird ergänzt.

GDT717 ist der wichtige Vorgänger: Dort war „kalt-trocken; Anfangsstufe“ ein hypothetischer portabler Kern, „Zubereitung“ nur eine ersetzbare lokale Ergänzung. Das ist kein bestätigtes Stoffwort und keine unabhängig bestätigte Temperatur. W77 übernimmt deshalb weder Kälte noch Trockenheit noch die Stufe als gesicherte Bedeutung.

## Konkrete Gegenlesungen

| Vollständiger Kontextanfang | N: Material T | Q: Eigenschaft T | Offene Entscheidung |
|---|---|---|---|
| f19v.3 otchy chol daiin … | Material T, trocken, Grad Γ | Eigenschaft T, trocken, Grad Γ; Träger fehlt unter der engen Nachbarregel | N ermöglicht ein Material-Eigenschaft-Feld, ohne das Material zu identifizieren |
| f2v.3 otchy chor … | Material T; Blüten | Eigenschaft T der Blüten | N braucht Beziehung zwischen zwei Nennungen; Q setzt vorangestellte Eigenschaft voraus |
| f18v.6 qotor chor otchy … | Blüten; Material T | Blüten mit Eigenschaft T | derselbe Unterschied bei umgekehrter Stellung |
| f13v.3 … chy otchy cthody | Wasser; Material T | Wasser mit Eigenschaft T | Wasser ist selbst nur die geerbte R1-Glosse |
| f22v.3 … otchy cthy … | Material T; Kraut | Eigenschaft T des Krauts | weder gemeinsame Sorte noch Prädikatsrichtung identifiziert |

Die Beispiele sind nur Erläuterungen der vollständigen Tabelle. [READING.md](READING.md) enthält **alle114verschiedenen Lesungszeilen**, zweimal ausgerichtet, insgesamt2068Wortpositionen. Drei Zeilen enthalten je zweiotchy und werden pro Fassung nur einmal vollständig ausgegeben; [ROLES.tsv](ROLES.tsv) behält beide Zielpositionen. Die117Positionen sind Alternativlesungen von40Loci, nicht117unabhängige Belege.

## Vollständiger lokaler Rollentest

Die vorab festgelegte Q-Regel prüft ausschließlich den unmittelbaren linken, sonst rechten Nachbarn auf die bestehende P09-R1-Materialrolle. **17Positionen haben einen solchen angenommenen Träger,100nicht.** Diese100sind keine100Gegenbeweise gegen Eigenschaften: Das kleine R1-Glossar lässt viele Wörter offen, ein Bezug könnte weiter entfernt oder elliptisch sein. Solche Bezüge wurden hier nicht hinzugefügt.

Für N wurde parallel jede unmittelbar folgende bereits angenommene R1-Qualität erfasst. Das gibt **zwei Lesepositionen an einer einzigen Stelle**, f19v.3 mit chol, ZL/IT. N trägt an den übrigen Stellen zunächst nur einen Materialplatzhalter ohne erklärte Anschlussbeziehung. Deshalb dürfen17gegen2 oder100fehlendeQ-Träger nicht zu einer Rangliste zwischen den Rollen werden: Die beiden Diagnosen haben verschiedene Anforderungen.

An den W76-Eingabeplätzen qotaiin otchy und qotchy otchy ist „Material T“ ebenfalls eine mögliche Rollenannahme. Der dortige Aktionswert ist aber selbst hypothetisch und wurde gerade zur Bildung des Eingabeplatzes benutzt. Diese Stellen unabhängig als Beweis für otchy=Nomen anzurechnen wäre zirkulär.

## Entscheidung für die weitere Lesung

**Otchy wird noch nicht global als Stoffwort in R1 eingesetzt.** Beide ganzen Rollenfassungen bleiben gespeichert. Das neue konkret formulierbare Feld ist „Material T, trocken, Grad Γ“ auf f19v.3; die Gegenkontexte vor und nach chor/cthy verlangen gleichzeitig eine Erklärung, die ein Stoffname allein nicht liefert. Kein Wort ist bestätigt übersetzt.

Der nächste sinnvolle inhaltliche Vergleich wäre eine einheitliche Lesung dieser drei Beziehungen: `otchy chol`, `otchy chor` und `chor otchy`. Eine Materialklasse mit Eigenschaften und eine Eigenschaft mit unterschiedlichen Trägern müssen an vollständigen Absätzen verschiedene Aussagen machen. Erst deren gemeinsame Ausarbeitung kann über den jetzigen lokalen Rollentest hinausgehen. Kein Wechsel der Wortart nur an störenden Stellen und keine automatische Übertragung der alten Anfangs-/Kälteskala.

## Umfang und Nachvollziehbarkeit

DECISION.md nach erklärter Projektexposition und vor der Rollenrechnung. Die Quelle ist ausschließlich W75s vollständiges Inventar; kein neuer Korpuszugriff. N/Q variieren nur otchy, alle übrigen R1-Werte bleiben unverändert. „Material T“ und „Eigenschaft T“ sind bewusst unbestimmte Inhaltsplätze, keine deutschen Wortübersetzungen. Ganze Zeilen, nicht neue vollständige Absätze, bilden hier den festgelegten Umfang.

`build.py` erzeugt alle Zeilen und Rollen, `validate.py` prüft vollständige Zuordnung und unveränderte andere Glossen. Keine Grammatik- oder Bedeutungsvalidierung, keine Physiksimulation, keine Signifikanz. Keine neuen Bilder/Quellen/Kontakte/Reserveseiten; f84/f84r geschlossen.

Registryprüfung PASS; globale Prüfung weiterhin sieben bekannte ungebundene GDT600-Dateien. Lokale Ausführungsprüfung: VALIDATION.json.
