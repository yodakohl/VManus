# GDT455 — zustandsbehafteter Stream-Fault-Contract

GDT455 ersetzt in 513 von 514 mehrgliedrigen Aussagen gleichzeitig je zwei
benachbarte Karten durch nichtleere Ein-Schritt-Nachbarn. Der neue Treiber liest
den ganzen 4.576er Strom mit 57 getrennten Besitzerbanken, Satz-Scope,
Ein-Karten-Vorausblick und zustandserhaltenden Stopps.

```bash
python3 experiments/yolo/gdt455_stream_fault_contract/src/run.py
python3 experiments/yolo/gdt455_stream_fault_contract/src/validate.py
```

Der Treiber kann außerdem eine andere bereits sichtbare Ersatzliste einlesen:

```bash
python3 experiments/yolo/gdt455_stream_fault_contract/src/stream_fault_driver.py \
  --input INPUT.tsv --schedule SCHEDULE.tsv --output REPLAY.tsv
```
