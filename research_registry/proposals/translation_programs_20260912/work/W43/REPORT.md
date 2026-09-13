# W43 — Verbrauch und Termine wählen keine Behandlungslesung

**Die zusätzliche Verbrauchsprüfung trennt einen Behandlungsplan nicht von der Bearbeitung eines erhaltenen Ansatzes.** Beide lassen sich über den gespeicherten S04-Abläufen mit freien Ressourcen ausarbeiten. Die verbrauchende Fassung benötigt neue positive Teilmengen und zusätzliche Zeitpunkte, aber weder deren Größe noch vorhandene Vorräte oder Abstände sind gebunden. Der Nachweis betrifft nur dieses ergänzte Ressourcenmodell, keine vollständige richtige Lesung.

Die Ausführungszahlen 6/2/4 stammen bereits aus S04 und sind **kein neuer Manuskriptbefund**. Neu geprüft wurde, ob ihre zusätzlichen Ressourcen- und Terminanforderungen eine der beiden Bedeutungsfamilien ausschließen oder bevorzugen. Das tun sie nicht. Es wurde kein neues Wort übersetzt.

## Registrierung und Datenabgrenzung

IDEA000193; [DECISION.md](DECISION.md), [SPEC.json](SPEC.json). Alle sieben exponierten f83r-Records,51Zeilen,341Gruppen. Drei alte Ablaufvarianten N/PRE/POST vollständig übernommen; keine Änderung von P15s strengem, zuvor gescheitertem erneut-Vertrag. Die hier verwendete N-Fassung bedeutet einen Durchgang, nicht bestätigtes „erneut“. PRE/POST behalten ihre fehlenden Bedingungen.

R deutet den ausgeführten Körper als nichtverbrauchende Bearbeitung desselben Materials A/C mit Gerät B. C deutet ihn als verbrauchende Gabe aus dem Vorrat A/C an denselben hypothetischen Adressaten B im Record. Dies sind **explizite alternative Gesamtbedeutungen**, keine durch unveränderte Gefäßglossen bewiesene Therapie. Die drei Ergebnis-/Verlaufswörter erhalten entsprechend „Bearbeitung/Anwendung läuft/erfolgt“; Erwärmen bleibt auf Material/Vorrat bezogen. R ist nicht jede mögliche Herstellung: Reale Einfüllungen könnten ebenfalls neue Stoffmengen benötigen. C ist ebenfalls nicht jede Behandlung, sondern ausdrücklich eine verbrauchende Anwendung.

B ist keine identifizierte Person, Krankheit oder Art der Verabreichung. Gleiche B-Nennungen bezeichnen nur unter der übernommenen Identitätshypothese denselben Adressaten. Neue Portionen erfordern keine neue Patientennennung und keinen neu beschafften Vorrat: Ein vorhandener Vorrat kann mehrere Teilmengen liefern.

## Vollständige Kandidatentabelle

| Kandidat | Ausgeführte Körper im alten Modell | Neue Vorhersage für Ressourcen / Termine | Ergebnis der Zusatzprüfung | Verbleibende Probleme |
|---|---:|---|---|---|
| N/R | 6 | Material bleibt bei diesem Körper erhalten; keine neuen Gaben gefordert. | Freier positiver Bestand genügt. | Alte fehlende Teilnehmer bleiben. Kein Therapieadressat verlangt. |
| N/C | 6 | Sechs positive Teilmengen, sechs geordnete Anwendungstermine. | Freie Vorräte und Termine erfüllen den berechneten Teilbedarf. | Mengen, Intervalle und Patientendeutung unbestimmt. |
| PRE/R | 2 | Nur die zwei gebundenen Direktkörper bearbeiten Material. | Keine zusätzliche Ressourcenunvereinbarkeit. | Zwei Aufrufe ohne geschriebene Bedingung; ein Aufruf ohne Teilnehmer. |
| PRE/C | 2 | Zwei positive Teilmengen; die erfüllten Prüfungen erzeugen keine neue Gabe. | Freie Vorräte genügen. | Dieselben fehlenden Bedingungen/Teilnehmer; keine bestätigte Behandlung. |
| POST/R | 4 | Zwei Direktkörper plus zwei zusätzliche Bearbeitungen. | Erhaltener Bestand kann wieder benutzt werden. | Dieselben fehlenden Bedingungen/Teilnehmer. |
| POST/C | 4 | Vier positive Teilmengen mit offenen Anwendungsterminen. | Freie Vorräte genügen. | Mengen und Zeitabstände fehlen weiterhin. |

Alle haben unabhängige Bedeutungsbestätigungskapazität **0**. Niedrigerer Materialbedarf wählt keinen Textsinn. Fehlende oder unauflösbare Aufrufe zählen nicht als erfolgreich ausgelassene Anwendung. Diese Körperzahlen erfassen nur ausgeführte Kandidaten, nicht sämtliche möglichen realen Anwendungen, Mengen oder Vorgeschichten.

## Die motivierende Doppelung vollständig erhalten

| qoteedy | N | PRE | POST |
|---|---|---|---|
| f83r.2:7 | ein Körper | Bedingung fehlt | Bedingung fehlt |
| f83r.5:9 | ein Körper | Bedingung fehlt | Bedingung fehlt |
| f83r.7:9 | ein Körper | Ziel bereits erfüllt, null Körper | ein Körper |
| f83r.7:10 | ein Körper | Ziel bereits erfüllt, null Körper | ein Körper |
| f83r.20:2 | Teilnehmer fehlt | Teilnehmer fehlt | Teilnehmer fehlt |

Daneben bleiben sämtliche sechs qokeedy-Stellen erhalten: .6:7 und .14:2 sind als Direktkörper gebunden; .22:3/.25:1/.27:3/.30:3 sind ungebunden. Diese Tatsachen wurden aus S04 übernommen, nicht als neue Treffer gezählt.

Die lokale C/POST-Lesung auf .7 lautet hypothetisch: „Anwendung von C bei B erfolgt; eine weitere Gabe C, anschließend prüfen; eine weitere Gabe C, anschließend prüfen.“ Dafür braucht sie zwei getrennte positive Teilmengen aus demselben C-Vorrat. Die angesetzten Termine müssen aufeinander folgen, aber **weder zwei Tage noch ein bestimmter Abstand** ergeben sich daraus. PRE verlangt an genau diesen beiden Stellen dagegen keine neue Gabe. Die spätere Erwärmung des Materials bestimmt keine verbliebene Vorratsmenge. Alle Zwischenwörter stehen in den vollständigen Lesungen.

## Was tatsächlich gerechnet wurde

[PORTIONS.tsv](PORTIONS.tsv) enthält jeden ausgeführten Körper mit Material, Adressatenhypothese, ursprünglicher Empfängernennung, Teilmengenvariable und offenem Termin. Für jeden Record/Material-Pool lautet C:

`Restbestand = S − (d₁ + … + dₙ), mit allen dᵢ > 0`

R verlangt durch diesen Körper keinen Abgang und behält S. Die Ausdrücke sind **Teilkonten ausschließlich der modellierten Körperwirkungen**. Ungelesene Wörter, ungebundene oder laufende Vorgänge sowie frühere Ergebnisbehauptungen können weitere Vorgeschichte und Verbrauch verlangen; sie wurden nicht zu null erklärt. Es gibt keine daraus bestätigte vollständige Massenbilanz.

Ein einfacher Existenzzeuge belegt die Freiheit: Wähle rein rechnerisch dᵢ=1 und S=n+1; C behält dann einen positiven Rest, R den unveränderten Bestand. Termine t₁=1,t₂=2,… erfüllen eine frei wählbare Reihenfolge. **Diese Zahlen sind ausschließlich dimensionslose Rechenzeugen, keine gelesenen Zahlen, gleichen Dosen oder tatsächlichen Termine.** Andere positive Größen und Abstände funktionieren ebenso.

[STOCKS.tsv](STOCKS.tsv) führt alle84Record-/Material-/Modellkonten, auch diejenigen ohne ausgeführten Körper. Eine Null in diesem Teilkonto bedeutet keinen bewiesenen Gesamtverbrauch null. Beide Familien bewahren bei jeder Ablaufvariante exakt dieselben ursprünglichen Referenz- und Zustandsprojektionen. Diese Gleichheit entsteht durch den registrierten Aufbau; sie ist kein neuer Texttreffer. Die zusätzliche Prüfung zeigt, dass die freien Ressourcen sie nicht widerlegen.

## Entscheidung

**Keine verbrauchende Behandlungslesung aus dieser Wiederholung auswählen.** Der angesetzte Patient kann bestehen bleiben, während Portionen wechseln; das ist ein konsistentes mögliches Konzept. Mangels gebundener Ressourcen und Termine bleibt es hier von der anderen Bedeutungsfamilie ununterscheidbar. Kein weiteres Raten von Tagesmarkern, Portionsgrößen oder Patienten zur Rettung angeschlossen. Der feste Teilansatz von IDEA000193 ist damit geprüft; andere Formen von Behandlung werden nicht allgemein ausgeschlossen.

[READING.md](READING.md) bewahrt alle341Gruppen in sechs vollständigen Bedeutungsentwürfen, [ALIGNMENT.tsv](ALIGNMENT.tsv) alle2046Positionen; 72 Positionen mit alten/alternativen Bedeutungsannahmen und269offen, kein Abdeckungsgewinn. [EVENTS.tsv](EVENTS.tsv) erhält alle252Ereignisprojektionen mit sämtlichen alten Leerstellen und Statuswerten.

[VALIDATION.json](VALIDATION.json): PASS. Getrennter Code prüft vollständige Quellerhaltung, alle unveränderten Ereignisprojektionen, sämtliche zwölf lesungsabhängigen Körperzeugen und84positive Bestandsbelegungen. Zwölf Quelldateien hashgebunden. Derselbe Bearbeiter, keine unabhängige Bedeutungsprüfung. Kein Erfolg der gesamten S04-Verträge behauptet.

Projektexposition vollständig; keine neuen Bilder/Seiten, Reservetests oder Kontakte. f84/f84r und alle Reserveseiten geschlossen. Keine Signifikanz, bestätigten Wörter/Pflanzennamen oder scorefähige Relationsevidenz.

```sh
python research_registry/proposals/translation_programs_20260912/work/W43/build.py
python research_registry/proposals/translation_programs_20260912/work/W43/validate.py
```

Repository-Prüfung: W43-Validator und Ideenregistry PASS. Globale Prüfung weiterhin mit acht bekannten Altfehlern (sieben ungebundene GDT600-Dateien, veralteter Experimentindex); keine dieser Dateien geändert. Der exakte Publikationsstand wird separat auf private Inhalte und nicht zum Versuch gehörende Dateien geprüft.
