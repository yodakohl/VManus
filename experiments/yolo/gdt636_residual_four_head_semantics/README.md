# GDT636 — die restlichen 19 Vierkopf-Körper

Status: `ALL_19_RESIDUAL_BODIES_HAVE_SCOPED_COMPOSITIONAL_DEFAULTS`

GDT636 vervollständigt das GDT635-Raster: 19 Restkörper ergeben unter
`p/s/r/l` 76 belegte Ganzformen mit 527 Token, davon 398 in ZL3b, IT2a und
RF1b oberflächenexakt. Die Bedeutungen werden aus 15 kurzen Fachslots
komponiert; kein Rest erhält eine lange freie Satzglosse.

Wichtigste neue Trennungen:

```text
ar / air / aiir = Fraktion I / II / III
or              = Portion
al              = Rohstoffform I
ol              = allgemeines oder zubereitetes Material
ody             = fertig aufbereitet, nicht kühlen
```

`WORKING_DICTIONARY_V13.tsv` enthält 251 Zeilen: alle 156 V12-Zeilen
unverändert, danach 19 streng begrenzte Restwerte und 76 konkrete Ganzformen.
Der Validator prüft Inventar, Kontexte, Lesergrenzen, Leitern, Kollisionen,
Passagen, Wörterbucherhalt, Hashes und byteidentischen Rebuild.

Ausführen:

```bash
python3 experiments/yolo/gdt636_residual_four_head_semantics/src/run.py
python3 experiments/yolo/gdt636_residual_four_head_semantics/src/validate.py
```

Der vollständige Befund steht in `REPORT.md`, die genaue Konstruktion in
`METHOD.md`.
