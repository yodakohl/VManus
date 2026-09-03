# GDT770 — target-masked valency/orphan tournament

GDT770 masks every exact `ol`, `ckhy`, `ols`, and `otar` occurrence in fifteen
already admitted complete lines, then compares eighteen fixed whole-form
policies using only exact immediate-neighbour role edges. It uses no target
default, target role, German fluency, historical similarity, or EVA/Latin
resemblance as score evidence.

The raw working leads are:

- `ol`: contextual relator, 19 penalty points versus NULL 41;
- `ckhy`: invariant mixing operation, 13 versus 32;
- `ols`: finished preparation/result, 0 versus 23;
- `otar`: transition/preparation nominal, 16 versus sequence linker 18 and
  NULL 41.

All four formal decisions remain `OPAQUE_NULL`: `ol` lacks its declared
left-quantity branch, `ckhy` and `ols` fail one page holdout, and `otar` is too
close to the sequence rival and reverses under holdout. The practical defaults
are concrete but replaceable: `ol=[aus?]/mit/und` by context, `ckhy=mischen`,
`ols=fertige Zubereitung`, and `otar=Zwischenzubereitung` with `dann` retained
as the close rival. None is a confirmed lexeme or plaintext translation.

Read [REPORT.md](REPORT.md) first. [METHOD.md](METHOD.md) specifies the exact
role-edge binder and [PREREGISTRATION.md](PREREGISTRATION.md) records the fixed
cohort, decks, penalties, gates, and admitted outcomes. The artifact map is in
[artifacts/README.md](artifacts/README.md).

Reproduce with:

```bash
PYTHONDONTWRITEBYTECODE=1 python3 experiments/yolo/gdt770_target_masked_valency_orphan_tournament/src/run.py
PYTHONDONTWRITEBYTECODE=1 python3 experiments/yolo/gdt770_target_masked_valency_orphan_tournament/src/validate.py
```

No new page, image, OCR, or transcription is used. `f84` and `f84r` remain
forbidden.

Independent validation passes 34,744 assertions and a byte-identical replay of
all seventeen runner outputs.
