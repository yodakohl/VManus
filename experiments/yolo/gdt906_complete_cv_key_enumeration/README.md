# GDT906: exhaustive completion of the GDT905 key search

The user removed the time and witness limits from the unresolved GDT905 search.
The same 49 paragraphs, alphabet, CV code, reference forms and grammar remain
fixed. [METHOD.md](METHOD.md) is the prospective decision rule;
[artifacts/BINDINGS.json](artifacts/BINDINGS.json) seals inputs and primary code.

The complete plan has 439,399 cases: 26,483 finished GDT905 cases are reused,
including its two grammar-rejected lexical keys, and 412,916 cases require full
enumeration. No completed research conclusion is asserted while cases remain.

Provide the hash-matching GDT892 reference cache and a fresh work directory using
`GDT906_CACHE` and `GDT906_WORK`, then run:

```sh
python3 experiments/yolo/gdt906_complete_cv_key_enumeration/src/reproduce.py --cache-dir "$GDT906_CACHE" --work-dir "$GDT906_WORK"
```

The primary pass uses up to 28 workers; the separate implementation verifies
all observed-key sets and grammar decisions with four workers during the primary
pass and up to 32 after the primary workers finish. Total concurrent workers
remain at most 32. This scheduling adjustment does not alter any case or
constraint. Receipts permit
resuming completed cases. Neither pass has a time or witness-count stopping rule.
A full-model candidate still requires independent evidence for its meanings.
