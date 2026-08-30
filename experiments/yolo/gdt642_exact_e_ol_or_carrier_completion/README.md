# GDT642 — exact E+OL/OR carrier completion

GDT642 adds three concrete exact-whole working values to V19:

- `cheol = ch+e+ol = trockener Drogenstoff`;
- `cheor = ch+e+or = trockener Drogenteil`, with portion and lexicalized-part
  rivals retained;
- `tcheol = tch+e+ol = kalt-trockener Drogenstoff`.

The builder audits all 219 occurrences, preserves alternate-reader warnings,
and rebuilds every one of the 4,128 allowed line states. The three values add
219 known token positions and expose five new one-hole lines. They do not add
a multi-token complete line by themselves.

Run:

```bash
python3 experiments/yolo/gdt642_exact_e_ol_or_carrier_completion/src/run.py
python3 experiments/yolo/gdt642_exact_e_ol_or_carrier_completion/src/validate.py
```

The complete interpretation and five-line next frontier are in `REPORT.md`.
These are replaceable technical-codebook defaults, not a claimed plaintext,
phonetic reading, language identification or manuscript solution.
