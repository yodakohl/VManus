# GDT453 — Synchronisation nach einem terminalen Stopp

GDT453 nimmt die 765 GDT452-Stopps am Aussageende und prüft die erste wirkliche
Karte danach. Gleicher Besitzer trägt den erhaltenen Zustand weiter; ein neuer
Besitzer oder eine neue Seite verwendet ausschließlich die eigene Zustandsbank.

```bash
python3 experiments/yolo/gdt453_terminal_stop_boundary_resynchronization/src/run.py
python3 experiments/yolo/gdt453_terminal_stop_boundary_resynchronization/src/validate.py
```

Alle 755 vorhandenen Grenzkarten lesen grün. Zehn Varianten liegen am Ende des
gesamten Stroms und besitzen keine spätere Karte.
