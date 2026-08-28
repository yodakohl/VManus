# GDT589 — vollständiger Carrier-Host-Replay

Status: `PASS_953_COMPLETE_HOST_REPLAY__910_AUTO_EXACT__41_MANUAL_VISIBLE__2_SOURCE_FALLTHROUGH_EXACT__117_REPEAT_HOST_OVERLAY`

GDT589 fährt den GDT588-Vollhostleser nicht nur an Beispielen, sondern über
alle 953 bekannten Carrier-Hosts. Die 910 automatischen Hosts reproduzieren
alle 1.186 Slots exakt. 41 manuelle Hosts und zwei alte source-ID-Brücken
erhalten einen sichtbaren eigenen Weg.

Der Vollbestand zeigt außerdem 117 statt nur 13 Hosts mit wiederholten
Carrier-Wurzeln. GDT589 hält deshalb drei Ebenen getrennt: geordnete
Schriftstellen, Packet-Komposition und flüssige Bedeutungshypothese. `×N`
bezeichnet Schriftpositionen, nicht automatisch N reale Gegenstände.

Ausführen:

```bash
python3 experiments/yolo/gdt589_full_host_carrier_intake_replay/src/run.py
python3 experiments/yolo/gdt589_full_host_carrier_intake_replay/src/validate.py
python3 experiments/yolo/gdt589_full_host_carrier_intake_replay/src/read_known_host.py ACTION:G407-E4166@3:CHD
```

Siehe [REPORT.md](REPORT.md), [METHOD.md](METHOD.md) und den kompakten
[Replay-Deck](artifacts/GDT589_FULL_HOST_REPLAY_DECK.md).
