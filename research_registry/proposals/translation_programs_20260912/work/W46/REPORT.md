# W46 — ysheol: bedingte Arbeitslesung „feucht“

Die vorregistrierte lokale Prüfung bevorzugt **ysheol ≈ feucht** als Arbeitslesung unter den bestehenden Operations- und Objektannahmen. Sie übersetzt das Wort nicht unabhängig. „Warm“ bleibt möglich: seine Stütze hängt an der abweichenden Transkription ykeey/ykeea. W44 bleibt unverändert.

## Vollständiger Kandidatenvergleich

| Ganzwortkandidat | ZL3b | IT2a | RF1b |
|---|---|---|---|
| feucht | MATCH | MATCH | kein exaktes Zielwort |
| trocken | CONFLICT | CONFLICT | kein exaktes Zielwort |
| kalt | CONFLICT | UNKNOWN | kein exaktes Zielwort |
| warm | MATCH | UNKNOWN | kein exaktes Zielwort |
| heiß | DIFFERENT_NOT_OPPOSED | UNKNOWN | kein exaktes Zielwort |

MATCH bezeichnet Übereinstimmung mit einem **angenommenen** Zustand, keine beobachtete Wortbedeutung. UNKNOWN widerspricht keinem Kandidaten. Warm und heiß sind unterschiedliche, hier nicht gegensätzliche Werte.

Die tatsächlich beobachteten vollständigen Zielzeilen auf f21r.12:

- ZL3b: `ykeey chor sheey ysheol chor chol daiin chkaiin`
- IT2a: `ykeea chor sheey ysheol chor chol daiin chkaiin`
- RF1b: `ykee@222; chor sheey @222;sheol chor chol daiin chkaiin`

Die unveränderten W09-Annahmen setzen ykeey auf thermisch warm und sheey auf feucht; ykeea hat keinen gebundenen Effekt. Die lokale Patientenbindung an chor wird vorausgesetzt. Damit ist nur die Benetzungsoperation in beiden exakten Zielwortlesungen erhalten. Ein unbekannter Effekt von ykeea könnte ebenfalls Erwärmung sein. Seine Abwesenheit aus dem Modell bedeutet weder Wirkungslosigkeit noch Kälte. Eine Prüfung am Originalbild wurde hier nicht durchgeführt und könnte den Lesungsunterschied auflösen.

## Datenabgrenzung und Konsequenz

W45 hat alle 96.184 Gruppen der bereits exponierten 179 Selektoren in drei alternativen Lesungen durchsucht: zwei exakte Zielwortvorkommen an **derselben** physischen Stelle, keine zusätzliche Stelle. Das ist keine unabhängige Bestätigung. Die vollständigen beiden Absätze und alle drei Zielzeilen stehen in [W45/CONTEXTS.md](../W45/CONTEXTS.md) und dessen maschinenlesbarem JSON. W46 wertet vorregistriert nur die drei unmittelbar vorhergehenden Gruppen aus; es ist kein vollständiger IT2a-Decoder. Die übrige Absatzfortsetzung aus W44 wird nicht als neue Evidenz gezählt.

Alle fünf Kandidaten wurden in allen drei Lesungen dokumentiert, einschließlich fehlender exakter RF-Zielwortkapazität. Trocken widerspricht der angenommenen Benetzung, kalt der angenommenen ZL-Erwärmung; beides sind modellbedingte Widersprüche. Andere Wortarten oder Bedeutungen außerhalb der fünf Werte bleiben ungeprüft. Kein Präfix, „geworden“, Demonstrativum oder Pflanzenname wurde erschlossen.

**Entscheidung:** feucht als bedingte Arbeitsglosse priorisieren, warm nicht ausschließen. Der nächste sinnvolle Bedeutungsfortschritt muss die vorausgesetzte Benetzungsoperation oder eine davon unabhängige Konsequenz binden. Dieselbe Stelle erneut umzucodieren liefert das nicht. Bestätigungskapazität dieses Versuchs: null unabhängige Bedeutungsprüfungen und null zusätzliche physische Blätter. Keine Signifikanzbehauptung. Keine Reserveöffnung; f84/f84r geschlossen; keine externen Kontakte.

## Reproduktion

Vom Repository-Stamm:

```sh
python research_registry/proposals/translation_programs_20260912/work/W45/build.py
python research_registry/proposals/translation_programs_20260912/work/W45/validate.py
python research_registry/proposals/translation_programs_20260912/work/W46/build.py
python research_registry/proposals/translation_programs_20260912/work/W46/validate.py
```

DECISION.md und SPEC.json wurden vor der W46-Auswertung geschrieben, nach der ausdrücklich offengelegten W45-Quellenexposition. PREDICTIONS.tsv enthält alle 15 Fälle; RESULT.json die wörtlichen Ursachen und unbekannten Effekte. Beide Validatoren PASS; sie prüfen Berechnung und Quellenbindung, keine Bedeutung.

Die globale Repository-Prüfung meldet weiterhin acht bekannte Altlasten: sieben ungebundene GDT600-Dateien und einen veralteten Experimentindex. Diese wurden nicht verändert.
