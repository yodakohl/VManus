# GDT1140 — gemeinsame Statuslesung bleibt unvollständig

**PARTIAL_SCOPED_C0.** Der Versuch hat eine konkrete, aber fragmentarische Lesung der vier f85r2-Textblöcke hervorgebracht. Er liefert keine ausgewählte Fortune-Deutung und kein bestätigtes Wort. Alle108 primären ZL-Positionen wurden bearbeitet;44 Wörter bleiben ohne Bedeutung und68 Positionen ohne vollständigen syntaktischen/semantischen Anschluss. Die anderen Transkriptionen und149 äußeren Gruppen bleiben unverändert erhalten, nicht mitübersetzt.

|Block|Positionen|Hypothetisch zugewiesene Wörter|Unbekannte Wörter|Weitere Fälle|Unvollständiger Anschluss|
|---|---:|---:|---:|---|---:|
|Nord|19|11|8|–|9|
|Ost|27|9|17|1 Skopusfrage|26|
|Süd|26|16|9|1 strukturelles Zeichen|13|
|West|36|26|10|–|20|
|Gesamt|108|62|44|2|68|

Die vollständige Kandidaten-/Positionstabelle und alle vier Lesungen stehen in [AUTHOR_READING.md](AUTHOR_READING.md), maschinenlesbar in [AUTHOR_ACCOUNT.json](artifacts/AUTHOR_ACCOUNT.json). Die Tabelle unterscheidet eine zugewiesene Wortbedeutung ausdrücklich von einem vollständigen Satz.39 Wortpositionen und das eine strukturelle Zeichen haben einen bedingt vollständigen Anschluss; diese39 sind ebenfalls keine bestätigten Übersetzungen.

## Was die feste Konstruktion tatsächlich leistet

Im eingefrorenen Kern bedeutet aiin versuchsweise allgemeine Stellung/Fähigkeit, d deren Innehaben, qo ausdrückliche Negation. or und ol bezeichnen zwei verschiedene, nur innerhalb ihres jeweiligen Blocks gebundene Träger T und A. Zwei vollständige hypothetische Zusammenhänge sind:

|Exakte Folge|Arbeitslesung|Bezahlte Konstruktion|
|---|---|---|
|N.2 sain or or aiin opchdy|Was jenen Träger betrifft: Er hat jetzt Stellung/Fähigkeit.|Thema, wiederholte identische Referenz, Subjekt, unausgesprochenes HOLD, NOW.|
|N.4 dair sheo oraiin chol daiin|Früher hatte der andere Träger Stellung/Fähigkeit, in Bezug auf die Stellung jenes Trägers.|Vergangenheitsbezug, besitzanzeigende Nominalgruppe, verschiedener ausdrücklicher Satzträger.|

Der zweite Satz behauptet weder die Übertragung derselben Herrschaft noch heutigen Verlust. Solche zusätzlichen Aussagen dürfen nicht aus dem historischen Fortune-Bildprogramm ergänzt werden. Die spätere Erweiterung setzt dieselben d/qo-Funktionen auf die neu bezahlten Substantive ar=Ressourcen und ain=Bedarf an; qodain bleibt von qodaiin verschieden. orar bezeichnet Ressourcen von T, oldar bindet A als Inhaber. Diese Regeln erzeugen lokale zusammengesetzte Lesungen, statt jedem Vorkommen eine andere Episode zuzuweisen.

Der Preis ist erheblich:32 primitive Einträge,18 ausgewählte Zusammensetzungen und16 Regelkarten, mehrere Synonyme sowie frei angenommene Satzgrenzen und Referenzen. Alle zehn neu lizenzierten Gesamtformen kommen in diesem Ausschnitt nur einmal vor. Die wiederverwendeten Funktionen sind deshalb eine bedingte lokale Konstruktion, kein Nachweis produktiver Sprachmorphologie. GDT608 erlaubt formale Zusammensetzung und zugleich eigenständige Gesamtformeffekte; es bestätigt keine dieser Bedeutungen. Die d=HAS/qo=NOT-Architektur war bereits in IDEA554 vorgeschlagen und ist nicht neu entdeckt.

## Grenzen und tatsächliche offene Folgen

- qotaiin ist als qo+t+aiin festgelegt. NOT(FUTURE(HOLD)) und die ebenfalls eingefrorene Formulierung FUTURE(NOT(HOLD)) sind ohne Festlegung des zukünftigen Zeitbezugs nicht allgemein gleich. Bei einem bestimmten zukünftigen Zeitpunkt können sie zusammenfallen; bei existenzieller Zukunft nicht. Das bleibt offene Semantik, kein nachträglich reparierter Treffer und keine automatische Widerlegung.
- S.16 erhält sein Subjekt nur unter der zusätzlich bezahlten Annahme, dass am die Referenz nicht ändert. Unbekannte andere Stellen werden als Referenzbarrieren behandelt. Gegensätzliche Aussagen in W.19–22 sind ohne gesicherten gleichen Träger kein nachgewiesener Widerspruch.
- AGAIN(FUTURE(RISE)) und die AGAIN/CONTINUE-Voraussetzungen sind ebenfalls nicht vollständig semantisch bestimmt. Ein vergangenes Ereignis wird dadurch nicht unabhängig beobachtet.
- Die Wortprofile zählen179 zugelassene Cache-Selektoren, nicht unabhängig gezählte physische Blätter. Die alte Überschrift count/leaves im eingefrorenen Profil-MD ist ungenau; das JSON und dieser Bericht stellen die Einheit richtig. Häufigkeit wählt weder Stellung noch Ressourcen als Bedeutung aus.

Die stärkste gleichwertige Alternative liest dieselbe Konstruktion als körperliche Fähigkeit, verfügbares Material und Zustandsänderung. Allgemeine Zustands-/Registerlesungen und semantische Umbenennungen bleiben ebenfalls möglich. Eine vollständige Geschichte lässt sich aus den unbekannten Stellen nicht legitim ergänzen. Entscheidung: Kandidat als partielle Konstruktion erhalten, keine weitere freie Glossarauffüllung auf derselben Grundlage. Für eine Fortsetzung wäre eine konkrete ganze noch offene Konstruktion erforderlich; die fehlende Bedeutung wird nicht durch einen neuen Decoder ersetzt.

## Prüfung und Reproduktion

Die unabhängige Prüfung bestätigt30/30 Erfassungs- und Vertragsprüfungen:473 originale Zwölf-Feld-Datensätze samt Reihenfolge,108 primäre Positionen, eingefrorener Kern, wiederholte Bedeutungen und sämtliche unbekannten Wörter. Sie findet keinen nachgewiesenen Widerspruch des festen Kerns, bestätigt aber weder vollständige Sprache noch Manuskriptbedeutung. Ein zweiter unabhängiger semantischer Bericht prüfte zusätzlich alle vier Absätze und die erweiterten Referenzen. Details: [VALIDATION.md](artifacts/VALIDATION.md) und [bestehendes Gutachten](../../../research_registry/proposals/laufenberg_f85r2_20260926/source_supply_20260929/GD_BIG_PICTURE_CONSTRAINT_ADVISORY_20261002.md).

`src/run.py` reproduziert das Inventar des manuell verfassten, eingefrorenen Kandidaten; `src/validate.py` prüft es unabhängig. Kein behaupteter semantischer Executor. Die Kernfixierung war10:41:21UTC, der Endentwurf11:03:06UTC am2.Oktober2026; die Belege stehen in den Receipts. Alle Daten waren Entwicklungsmaterial. Bestätigte Wörter0, unabhängige Bestätigungskapazität0. Keine Signifikanz, Pflanzenidentität, Reserveöffnung oder externe Kontaktaufnahme. Frühere Versuche bleiben unverändert.
