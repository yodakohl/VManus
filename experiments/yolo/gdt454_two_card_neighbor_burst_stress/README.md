# GDT454 — zwei veränderte Karten hintereinander

GDT454 greift den 57-Banken-Strom nicht mehr mit einer einzelnen Nachbarkarte,
sondern mit zwei unmittelbar aufeinanderfolgenden Mutationen an. Die Auswahl
ist fest: je Quellrezept, Mutationsfamilie und neutraler Klasse der
lexikographisch erste lesbare beziehungsweise gestoppte Nachbar.

```bash
python3 experiments/yolo/gdt454_two_card_neighbor_burst_stress/src/run.py
python3 experiments/yolo/gdt454_two_card_neighbor_burst_stress/src/validate.py
```

34.205 Zweierbursts bestehen den vollständigen sequenziellen Zustandslauf.
