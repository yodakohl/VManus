# GDT932 — Durchführung und Reproduktion

[PREREGISTRATION](PREREGISTRATION.md) legt Aussageideen, neun konstante
Ganzwortwerte und die begrenzte Bindungsprobe fest. Quelle und Absatzrahmen
werden direkt aus dem bereits abgegrenzten GDT930-Artifact wiederverwendet.
Keine neue Roh-TSV-Abfrage oder Bildöffnung; f84/f84r bleiben geschlossen.

```sh
python experiments/yolo/gdt932_joint_flow_participant_reading/src/run.py
python experiments/yolo/gdt932_joint_flow_participant_reading/src/validate.py
```

Der Runner richtet beide unveränderten Lexika auf jede Rohgruppe aus. Innerhalb
zusammenhängend nominierter Wörter bindet er Material beziehungsweise Prädikat
mit fester Linkspräferenz, danach rechts. Die Kenntnisgrenze ist keine sprachliche
Satzgrenze. Jeder andere Fall bleibt offen. CLAUSES.tsv zeigt alle nominierten
Szenarien in allen Lesungen einschließlich RF-Lücken; die deutsche Formulierung
ist eine Interpretation aus dem Protokoll und keine Parserbestätigung.

Der separat implementierte Validator prüft Quellen, alle Gruppen und Werte,
jede der150Pflichten, alle60qokeedy-Vorkommen in beiden Lesungen, Dopplungen,
Szenarioquellen und bytegleichen Replay. Beide Programme stammen von root;
keine unabhängige semantische Begutachtung. PREREG_LOCK.json bindet die
vor der Auswertung festen Quellen/Hypothesen. DEVELOPMENT_DECISION.json kennzeichnet
die nachträgliche praktische Wahl M ausdrücklich. Der Experimentmanifest
bindet sämtliche endgültigen Reproduktionsdateien.
