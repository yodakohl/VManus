# GDT605 artifacts

- `gdt605_unit_result.json`: compact boundary-aware inventory result.
- `gdt605_unit_inventory.tsv`: all 98 training units with held frequencies.
- `gdt605_bpe_merges.tsv`: the 64 ordered training merges.
- `gdt605_separator_crossing.json`: all separator counts, per-folio signs,
  merge rules and crossed examples.
- `gdt605_boundary_latin.json`: three-start exact-letter Latin attack.
- `gdt605_boundary_old_italian.json`: three-start exact-letter Old Italian
  attack.

All target rows were obtained through the guarded query in `src/run.py`; the
raw mixed transcription is not parsed directly by an experiment script.
