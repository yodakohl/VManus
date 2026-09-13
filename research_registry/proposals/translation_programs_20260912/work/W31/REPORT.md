# W31: Negation mit tatsächlich neu berechneten Materialbezügen

**Die vollständige Negationsfassung wurde gerechnet und bleibt unvollständig.** Ohne chey als Prüfvorgang verlieren auf f86v5 zwei Qualitätsangaben ihren Materialbezug. Zusätzlich wechselt auf f93r das Objekt des Zerkleinerungsbefehls. W28/W29 bleiben die redaktionelle Arbeitsfassung; chey≈nicht wird nicht übernommen. Das bestätigt chey≈prüfe nicht unabhängig.

## Die entscheidende Stelle: oty oty

Die exponierte Folge f86v5.19 enthält chey .19:3, zwei offene Gruppen und **oty .19:6, oty .19:7**. Beide oty heißen in der geerbten Arbeitshypothese „kühl“.

| Folge | C: chey≈prüfe | N: chey≈nicht, feste Vorwärtsregel |
|---|---|---|
| erstes oty .19:6 | kühl am angenommenen Endprodukt ody .18:8; INITIAL_CONSTRAINT | nicht kühl; **Materialobjekt fehlt**, MISSING_PATIENT |
| zweites oty .19:7 | nochmals kühl am selben Objekt; MATCH | positiv kühl; **Materialobjekt fehlt**, MISSING_PATIENT |

Die bestehende W13-Qualitätsregel gewinnt beide alten Bezüge aus dem chey-Prüfereignis. Nach dessen Entfernung gibt es keinen zulässigen lokalen Ersatzbezug. W31 wendet dieselbe Regel neu an und erhält den Fehler ausdrücklich. Das zweite oty wird weder gelöscht noch ebenfalls negiert: W30s festgehaltener Bereich betrifft nur das nächste Prädikat.

**Bedingte Konsequenz einer möglichen Reparatur:** Würde man beide Angaben zusätzlich an denselben Stoff binden, ergäbe sich „nicht kühl; kühl“, ohne dazwischenliegenden Zustandswechsel. Unter dem registrierten Negationsvertrag wäre das widersprüchlich. Dieser gemeinsame Bezug wurde nicht als neue Manuskriptlesung eingesetzt. Im tatsächlich gerechneten N liegt fehlende Bindung vor, kein beobachteter harter Zustandswiderspruch. „Nicht kühl“ wird niemals zu „warm“ umgedeutet.

## Weitere Änderung durch die neue Wortrolle

Auf f93r.10 bleibt ychos .10:1 positiv: es steht vor chey. Sein Patient wechselt jedoch unter allen B/J/M-Regeln von der Trockenmaterialdosis chodaiin .8:3 zur flüssigen Zubereitung cheol .10:4. Ohne chey als Aktionsgrenze greift die bestehende lokale Rechtsbindung. keol .10:3 bleibt ein ungelesenes Zwischenwort. Das ist eine materielle Änderung der Handlungsfolge, keine rückwirkende Negation von ychos.

Der spätere qokor .12:1 behält sal .11:7 als Objekt und wird gemäß dem schon in W30 festgelegten Bereich verboten. N lässt sich hier also hypothetisch als „zerkleinere die flüssige Zubereitung … erhitze das Arzneimaterial nicht“ formulieren. C hatte stattdessen die ältere Trockenmaterialdosis zerkleinert, die Flüssigkeit geprüft und sal erhitzt. Keine dieser Wortbedeutungen ist unabhängig bestätigt.

## Alle acht Ziele und ihre Auswertung

| chey | Negatives Ziel | Tatsächlicher N-Befund |
|---|---|---|
| f17v.19:2 | ykeey .20:1: Auszug nicht erneut erwärmen | Gebundenes Verbot, keine Wärmewirkung ausgeführt |
| f17v.22:3 | chkeey .23:1: warmen Auszug nicht vollständig zerreiben | Gebundenes Verbot; kein physischer Mahlgrad war modelliert |
| f24r.5:4 | qoky .6:5: kühles Ausgangsmaterial nicht mäßig erwärmen | Gebundenes Verbot, keine Wärmewirkung ausgeführt |
| f24r.13:4 | cheey .14:2: Blütenanteil nicht fein zerreiben | Gebundenes Verbot; kein physischer Mahlgrad war modelliert |
| f86v5.19:3 | oty .19:6: nicht kühl | Negative Aussage ohne Materialobjekt; Folge-oty ebenfalls ungebunden |
| f93r.10:2 | qokor .12:1: sal nicht erhitzen | Gebundenes Verbot, keine Wärmewirkung ausgeführt |
| f102v2.37:3 | qokeey .37:8: verarbeitetes Blütenmaterial nicht anhaltend erhitzen | Gebundenes Verbot, keine Wärmewirkung ausgeführt |
| f29v.2:6 | erstes chol .3:1: Kraut nicht erhitzen/trocknen | Nur erster Befehl verboten; zweiter chol .3:2 bleibt positiv |

Die Beispiele zeigen die A/H/J-Anzeige; sämtliche Q/A, D/H, B/J/M und O/I-Fälle stehen in CANDIDATES.tsv. Ein Verbot betrifft nur den einzelnen geschriebenen Befehl, nicht jeden späteren gleichlautenden Vorgang. Alle offenen Bereichs- und Argumentgruppen bleiben sichtbar. Die vorgegebenen acht Negationsziele bleiben auch nach der Neuberechnung der Bindungen dieselben.

## Ganze Fortsetzungen und verbleibende Probleme

Alle17Absätze/169Zeilen/1045Gruppen wurden neu ausgewertet: **408 Absatzwelten, 10680 Ereignisse**. Acht entfernte Prüfbefehle je24Varianten erklären die192 gegenüber W28 entfallenen Ereignisse. Die Negationswörter selbst bleiben vollständig im Alignment und den Bereichstabellen erhalten.

192 Zielfälle umfassen168 gebundene Verbote und24 ungebundene negative Qualitätsfälle. Alle128 späteren Anforderungen an die jeweils alten oder neuen Zielobjekte wurden erfasst. Der einzige unterschiedliche spätere Qualitätsstatus ist oty .19:7: MATCH→MISSING_PATIENT in24abhängigen Varianten. Das ist der Verlust eines prüfbaren Bezugs, keine erfolgreiche Vorhersage eines anderen Temperaturwerts. Die späteren Aktionen und alle vollständigen Zustandsspuren bleiben in den Tabellen erhalten.

Pro Q/A-Modell ändern sich27 Argumentzeilen:24 entfernte chey-Zeilen und3 neue ychos-Bindungen. Sechs Qualitätszeilen ändern sich (zwei Stellen × drei Grammatiken);248 Ereigniszeilen einschließlich entfernter Checks und fortgeführter Zustände. TAKE-Bezüge bleiben gleich. ALL_CHANGES.tsv enthält sämtliche Änderungen gegenüber **W28**, nicht gegenüber der älteren sal-losen Fassung.

Keine neue harte Zustandsopposition entsteht. In der aktuellen A/H/I-Kombination steigen fehlende Qualitätsobjekte aber von15 auf21 (zwei Stellen × drei Grammatiken);0harte Oppositionen,3warm/heiß-Abweichungen und39technisch unvollständige positive Aktionen bleiben bestehen. Die übrigen Modellvarianten behalten ihre vorherigen Oppositionen. Weniger ausgeführte Aktionen oder unbekannte statt widersprüchliche Zustände beweisen keine Negationsbedeutung.

## Entscheidung und Reproduktion

**N ist als vollständige Lesung unter den festgelegten Regeln nicht tragfähig:** die negative Aussage und ihre Fortsetzung sind ungebunden. Der konkrete sal-Befehl kann als Gegenlesung verboten werden, trägt aber keine Auswahl der Wortbedeutung. Keine automatische neue Objektregel, zweite Negation oder Auswahl nur der sieben Verbotsstellen folgt daraus. Die positive Arbeitsfassung bleibt bestehen; allgemeine Negation im Manuskript ist damit nicht ausgeschlossen.

[READING.md](READING.md) erhält alle1045Gruppen mit markierten Negationszielen, dem geänderten ychos-Objekt und den beiden fehlenden Qualitätsobjekten. Die unannotierten Q/A-Alignments enthalten die Wortwerte; die Ereignisdateien die tatsächlich berechnete Polarität.

IDEA000228, DECISION.md/SPEC.json vor der Rechnung;569Vorgängerdateien hashgebunden und unverändert. W30s Nichtausführung bleibt unverändert dokumentiert. Der Validator rechnet alle Objektbindungen mit den eingefrorenen Funktionen und die tatsächlichen Zustände separat nach, kontrolliert die Bereiche,192Zielfälle,128Fortsetzungen und vollständige Wortfolge. Vier kleine künstliche Vertragsprüfungen prüfen zusätzlich Werteausschluss ohne Wärme-Erfindung, Widerspruch einer folgenden positiven Aussage, Zustandswechsel und Nichtausführung eines Verbots. Sie sind keine Manuskriptbelege. PASS.

Keine neuen Seiten, Bilder, Rohdaten, Quellen, alternativen Transkriptionen oder Kontakte; f84/f84r und Reserven geschlossen. Alles exponierte Hypothesenentwicklung. Keine unabhängige Bedeutungsbestätigung, Signifikanz, bestätigten Pflanzennamen oder GDT388-Zulassung.

```
python research_registry/proposals/translation_programs_20260912/work/W31/build.py
python research_registry/proposals/translation_programs_20260912/work/W31/compare.py
python research_registry/proposals/translation_programs_20260912/work/W31/consequences.py
python research_registry/proposals/translation_programs_20260912/work/W31/render.py
python research_registry/proposals/translation_programs_20260912/work/W31/validate.py
```
