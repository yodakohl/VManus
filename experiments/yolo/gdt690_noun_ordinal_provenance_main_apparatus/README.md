# GDT690 — noun ordinal provenance and main/apparatus reader

GDT690 converts the 51-line V62 edition into V63. Every German main-text noun is bound to one exact written ordinal; one concrete value is printed in the main text and rivals are retained in a compact apparatus.

Headline result: 725 noun spans at 459/479 token positions, 92 rewritten positions, 40 spoken meta-nouns reduced to zero, and 21 slash/or alternatives reduced to zero. The short productive heads are `p=Pulver`, `s=Samen`, `r=Wurzel`, `l=Holz`.

See [REPORT.md](REPORT.md) for the result, [METHOD.md](METHOD.md) for construction details, and [artifacts/GDT690_V63_CONCRETE_NOUN_READER.md](artifacts/GDT690_V63_CONCRETE_NOUN_READER.md) for the full reader.

Run:

```bash
python3 experiments/yolo/gdt690_noun_ordinal_provenance_main_apparatus/src/run.py
python3 experiments/yolo/gdt690_noun_ordinal_provenance_main_apparatus/src/validate.py
```
