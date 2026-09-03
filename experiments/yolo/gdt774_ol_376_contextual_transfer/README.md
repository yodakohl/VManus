# GDT774 — `ol` contextual transfer over 376 exact occurrences

Status: `PASS__PARTIAL_CONTEXT_TRANSFER__NO_PLAINTEXT`.

The independent validator passes 28,954 checks, verifies all fifteen source
locks, and byte-replays all 24 runner artifacts plus `REPORT.md`.

GDT774 applies the GDT773 working interpretation to every one of the 376
reader-exact cached `ol` occurrences without opening another page. It keeps two
outputs separate:

- an automatic renderer using only occurrence-ID-free cached conditions;
- a practical hybrid which preserves the fifteen fixed GDT773 calibration
  outputs, then uses the automatic rules elsewhere.

The automatic renderer finds 49 contextual outputs: ten `Ansatz:`, five
`Menge:`, four `und dann`, three `;`, and 27 `und`. The other 327 positions keep
the weak whole-form fallback `Ansatz-/Zubereitungsposten`. It reproduces only
9/15 GDT773 case outputs, exposing six local decisions that do not transfer.
The hybrid has 55 contextual outputs and 321 nominal fallbacks.

A companion 20,000-draw structural audit shows strong internal placement and
concentrated right followers, especially in section B/hand 2. Repetition and
seven adjacent `ol ol` pairs prevent a universal punctuation reading. Only 73
of 376 positions enter the broader inherited typed-evidence union; 303 remain
outside it.

Every German value is a replaceable renderer default. `ol` is treated only as
the complete EVA whole; no component, liquid, substance, operation, lexeme, or
plaintext is identified. GDT683 mixed-source rows are joined only through
`./vmanus-exp query-tsv` with the 98 safe GDT769 page selectors and explicit
columns.

Run:

```bash
PYTHONDONTWRITEBYTECODE=1 python3 experiments/yolo/gdt774_ol_376_contextual_transfer/src/run.py
PYTHONDONTWRITEBYTECODE=1 python3 experiments/yolo/gdt774_ol_376_contextual_transfer/src/validate.py
```

See `PREREGISTRATION.md`, `METHOD.md`, `REPORT.md`, and `experiment.json`.
