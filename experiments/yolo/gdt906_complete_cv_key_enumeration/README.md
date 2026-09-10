# GDT906: exhaustive completion of the GDT905 key search

**COMPLETE_NO_GRAMMAR_KEY.** All 439,399 primary and independent case enumerations
agree. Three lexical case assignments represent two previously known distinct
key/passages, all rejected by the fixed grammar. No translation or confirmed
meaning was found. [Final report](REPORT.md); [validation](artifacts/VALIDATION.json).

[METHOD.md](METHOD.md) is the prospective rule and
[BINDINGS.json](artifacts/BINDINGS.json) seals unchanged inputs and primary code.
The user removed elapsed-time and witness limits. The same 49 paragraph readings,
CV model, literal alphabet, reference forms and grammar were retained. 26,483
completed GDT905 cases were reused and 412,916 cases completely enumerated anew.
The independent checker re-established every exact key set and grammar decision.

Provide the hash-matching GDT892 reference cache and an external work directory
using `GDT906_CACHE` and `GDT906_WORK`, then run:

```sh
python3 experiments/yolo/gdt906_complete_cv_key_enumeration/src/reproduce.py --cache-dir "$GDT906_CACHE" --work-dir "$GDT906_WORK"
```

This runs the primary pass with 28 workers, then the independent pass with 32,
packs every independent receipt, and checks complete byte/provenance/key-set
agreement. Completed receipts permit restarting without dropping unknown cases.
Neither pass has a time or witness-count stop. Timings vary on fresh runs;
recorded exact key sets, decisions and coverage are the reproducible outcomes.

`validate_complete_v3.py` preserves the published earlier independent source.
The current version adds only a separately implemented necessary flow check;
all 180,257 valid earlier receipts remain bound to their original source hash.
The three-key provisional witness receipt also binds that preserved version.
The final checker validates the source map and all 439,399 individual receipts.
No grammar compatibility would by itself establish a word's meaning.
