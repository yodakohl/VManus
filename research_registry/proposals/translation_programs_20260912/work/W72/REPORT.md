# W72: keine gebundene thermische Ergebnisprüfung im aktuellen Entwurf

**Keine der ausgeschriebenen Qualitätsangaben verbindet sich unter den festen W69-Bezügen mit einer vorherigen Wärmehandlung an derselben Materialnennung.** Damit liefert der aktuelle Absatzumfang keine eigenständige schriftliche Endzustandsprüfung für W71s Wärmezufuhr-/Endtemperaturfrage. Das schließt Wärmeanweisungen nicht aus, begründet sie aber auch nicht.

Alle sechs W63-Absatztranskriptionen wurden in beiden W69-Fassungen geprüft, nicht nur die günstige Wärmefolge. Sämtliche **18 Qualitätsereignisse** sind in [QUALITIES.tsv](QUALITIES.tsv) erhalten:

| Qualitätsklasse | Ereignisse | Befund |
|---|---:|---|
| shy, W03-Feuchtigkeitswert | 4 | keine thermische Aussage |
| dy | 8 | kein W03-STANDALONE-Feature; keine erfundene Temperatur oder Abschlussbedingung |
| oty/chy, W03-Temperaturwerte | 6 | Material zugewiesen, aber keine frühere positive Wärmehandlung an genau dieser Nennung |

Die sechs Temperaturfälle enthalten auch **keine folgende** positive Wärmehandlung am selben Nennungsschlüssel. Es ergibt sich somit unter diesem Vertrag weder eine Ergebnis- noch eine unmittelbare Eingangskontrolle derselben Bearbeitung. Eine andere Materialidentitätsregel wurde nicht ergänzt.

## Alle thermischen Aussagen konkret

| Fassung und Stelle | Hypothetische Aussage | Zugewiesene Nennung | Fehlender Anschluss |
|---|---|---|---|
| ZL NRC, f116r.43:10 oty | Zubereitung B kühl | shey .42:8 | keine thermische Aktion an dieser Nennung |
| ZL AMV, dieselbe Stelle | Zubereitung B kühl | shey .42:8 | ebenso |
| ZL NRC, f116r.45:5 chy | erwärmte Dosis P heiß | qokain .44:3 | kein vorheriger Heizbefehl an dieser Nennung |
| ZL AMV, dieselbe Stelle | Zubereitungsposten nicht heiß | ol .44:5 | kein vorheriger Heizbefehl an dieser Nennung |
| IT NRC, f116r.45:5 chy | Zubereitung B heiß | shey .45:2 | kein vorheriger Heizbefehl an dieser Nennung |
| IT AMV, dieselbe Stelle | Zubereitung B nicht heiß | shey .45:2 | ebenso |

Diese Aussagen sind vorhandene Wort- und Bindungshypothesen, keine beobachteten Stofftemperaturen. Die positive und negative chy-Fassung werden nicht vermischt. „Nicht heiß“ wird nicht als „kalt“ ausgegeben. Die nominale Glosse „erwärmte Dosis“ ist ebenfalls keine vorherige geschriebene Erwärmungshandlung.

Dass ein anderes shey zuvor erhitzt wurde, reicht in W69s ausdrücklich nennungsbezogenem Vertrag nicht für denselben Stoff. Das bedeutet nicht, dass das Manuskript verschiedene Portionen beweist. Eine Gleichsetzung wäre eine weitere Identitätshypothese, deren Folgen vollständig geprüft werden müssten. Sie wird hier nicht zur Herstellung eines gewünschten Treffers eingesetzt.

## Entscheidung für die Lesung

Der f75v.45-Entwurf bleibt eine **unbestätigte Prozesshypothese mit offenen Wörtern**. Seine Temperaturen und sein Abschluss sind nicht durch nachfolgende schriftliche Aussagen desselben Objekts abgesichert. Kein zusätzlicher Zustandsrechner kann diese fehlende Bindung ersetzen. W71s warm→heiß→heiß→warm-Projektion bleibt eine Folge gesetzter Effekte, keine beobachtete Bestätigung.

Die konkrete Aufgabe „Endzustand im aktuellen festen Entwurf finden“ ist damit abgeschlossen. Keine weitere Suche mit verbreitertem Abstand, neuer dy-Temperatur oder stiller shey-Identität folgt daraus. Für Fortschritt an einem zusammenhängenden Lesungskonzept muss der nächste Ansatz eine ausdrücklich andere Inhaltsfrage bearbeiten. Als möglicher Anschluss ist die funktionale Bedeutung der wiederholten Handlung qokeey qokeey zu prüfen: Wiederholung eines Arbeitsschritts, Aufzählung oder Textproduktion haben unterschiedliche Folgen für vollständige Handlungsabschnitte. Vor Auswahl muss der bestehende Wiederholungs-/Restitutionsversuch W15 primär geprüft werden; die Wiederholung darf nicht einfach als neuer Beweis für „erhitzen“ dienen.

## Vorgänger, Ausführung, Grenzen

W13 zeigt, dass eine andere Nominalrolle Qualitätsobjekte wechseln lässt. W14s exponierte f102v2.35-Konstruktion demonstriert den Unterschied von Eingangsattribut und Ergebnisbehauptung, identifiziert aber keine allgemeine Satzregel; sie wird hier nicht nachträglich auf freie Abstände übertragen. W31 erhält die Probleme negativer Qualitätsbezüge. Keine dieser alten Fassungen wird verändert oder neu gerechnet.

DECISION.md vor der Extraktion. W03 liefert ausdrücklich geschriebene STANDALONE-Werte; W09 liefert den unveränderten thermischen Aktionskatalog; W69 liefert Prädikate, Polarität und Materialnennungen. Gesucht wurden letzte vorausgehende und erste folgende positive thermische Aktion am identischen Patientenschlüssel innerhalb desselben Absatzes. Alle offenen Gruppen und ganzen Absätze bleiben in [READING.md](READING.md). „Eigenständig geschrieben“ bedeutet nicht „semantisch unabhängig bestätigt“: Auch oty/chy-Werte und ihre Bindungen sind frei angenommen.

`build.py` erzeugt alle Tabellen; `validate.py` prüft separat jeden Qualitätsfall und beide Suchrichtungen. Keine Gesamtzustandsausführung, keine neue Grammatik, kein Decoder und keine Bedeutungsprüfung. Alles bereits exponiert, keine neuen Bilder/Quellen/Kontakte oder Reserven, f84/f84r geschlossen. Keine Signifikanz, bestätigte Pflanzennamen oder Wortübersetzung; unabhängige Bestätigungskapazität null.

Registryprüfung PASS; globale Prüfung weiterhin sieben bekannte ungebundene GDT600-Dateien. Lokale Vollständigkeitsprüfung: VALIDATION.json.
