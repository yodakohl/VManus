# GDT782 — recurrent-six target-external field adjudication

Status: `PASS__20_CACHE_OCCURRENCES__14_READER_EXACT__6_TARGET_MASKED__8_TARGET_EXTERNAL__65_EXTERNAL_NEIGHBORS__5_REVISED__1_KEPT__270_CONTEXTUAL__106_FALLBACKS__230_CONSUMED__ZERO_COMPONENT_EXPORT`

Masking the six GDT781 target positions leaves eight reader-exact outside
fields. They revise five concrete whole-form defaults and retain one, while
preserving all 376 renderer rows, 270 contextual outputs and 230 consumed right
tokens. The strongest practical repair is `or aiin | chedor`: the field now
reads working “Menge: drei Portionen | Stoff: getrockneter Arzneistoff” instead
of repeating “Portion.”

The pass also prevents two stale context displays: source-built `okeol` prose
is replaced by GDT754's later open whole-form role, and `cthy` uses GDT768's
current `Blattgut` default. The eight outside displays are aggregate card
audits, not newly licensed translations.

All six defaults remain replaceable hypotheses with confidence and
counterevidence. See `PREREGISTRATION.md`, `METHOD.md`, `REPORT.md`,
`artifacts/GDT782_6_WORKING_REVISIONS.tsv` and `experiment.json`.

Reproduce with:

```bash
python3 -B experiments/yolo/gdt782_recurrent_six_target_external_field_adjudication/src/run.py
python3 -B experiments/yolo/gdt782_recurrent_six_target_external_field_adjudication/src/validate.py
./vmanus-exp check-edge-packet experiments/yolo/gdt782_recurrent_six_target_external_field_adjudication/artifacts/GDT782_GDT388_EXTERNAL_FIELD_PACKET.tsv
```
