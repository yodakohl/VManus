# GDT452 — nach einem Stopp wirklich weiterlesen

GDT452 ersetzt jede GDT448-Quellkarte durch einen lokal gestoppten Nachbarn,
bewahrt den Zustand und gibt danach die tatsächlich folgende Quellkarte ein.
Es prüft damit reale Anschlussstellen statt eigens gewählter Recovery-Beispiele.

```bash
python3 experiments/yolo/gdt452_context_stop_actual_next_recovery/src/run.py
python3 experiments/yolo/gdt452_context_stop_actual_next_recovery/src/validate.py
```

Von 5.243 Fällen mit einer Folgekarte lesen 5.240 sofort weiter. Drei Varianten
am selben Ort lassen folgerichtig auch den abhängigen kopflosen Schluss stoppen;
alle drei lesen am Beginn der nächsten Aussage wieder weiter.
