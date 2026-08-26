# GDT442 — vollständige Stop-Karte des Faktorlesers

Status: `COMPLETE_47_RULE_STOP_DECK__ALL_STOPS_STATE_SAFE`

Die Karte listet alle derzeit nicht lizenzierten Grundverbindungen: 44 direkte
Handlungspaare, zwei Kopf–Fokus-Kanten und den Kontextfall „Schluss ohne
aktiven Kopf“. „Stop“ bedeutet hier Lesergrenze, nicht historische
Unmöglichkeit.

Einen sichtbaren Kandidaten prüfen:

```bash
python3 experiments/yolo/gdt442_forbidden_factor_stop_deck/src/explain_stop.py \
  --recipe A_ADDR+T+S+OR
```

Siehe [REPORT.md](REPORT.md) und [METHOD.md](METHOD.md).
