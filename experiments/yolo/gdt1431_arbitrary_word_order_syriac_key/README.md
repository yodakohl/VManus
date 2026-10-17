# GDT1431 — word-internal permutation envelope

CONTROL_STOP_NO_NATIVE_SEARCH. Both actual controls hit preparation caps; zero native searches. See REPORT.md. No model exclusion or word meanings.

Run in order after public lock:

```
python3 experiments/yolo/gdt1431_arbitrary_word_order_syriac_key/src/run.py --gate
python3 experiments/yolo/gdt1431_arbitrary_word_order_syriac_key/src/validate.py --gate
python3 experiments/yolo/gdt1431_arbitrary_word_order_syriac_key/src/run.py --native
python3 experiments/yolo/gdt1431_arbitrary_word_order_syriac_key/src/validate.py --native
python3 experiments/yolo/gdt1431_arbitrary_word_order_syriac_key/src/validate.py --validate
```
