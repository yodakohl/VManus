# GDT297 — exact-host renderer/surface alias audit

Status: **EXACT_HOST_RENDERER_IS_WITHIN_HOST_SURFACE_ALIAS**.

## Result

All 59/59 hosts have a bijection between their renderer tuples and complete raw source forms. Only 1/59 has exactly one raw surface; the other hosts express two or more whole-form alternants. Held renderer top-1 is therefore also the top-1 accuracy of the corresponding whole-form alternant for the same exact host.

The five GDT296 canonical candidates are:

| host | events | surfaces | dominant complete form | share | held top-1 |
|---|---:|---:|---|---:|---:|
| `lche` | 42 | 1 | `lchedy` | 1.000 | 1.000 |
| `cthol` | 30 | 2 | `cthol` | 0.967 | 0.967 |
| `cthor` | 20 | 2 | `cthor` | 0.950 | 0.950 |
| `okee` | 126 | 5 | `qokeedy` | 0.786 | 0.786 |
| `okeey` | 115 | 4 | `qokeey` | 0.783 | 0.783 |

## Consequence

GDT293 remains a strong exact-host completion result and GDT296 remains useful as a normalization atlas. But at exact-host resolution it does not separate a productive renderer from memorized whole-form alternants: every renderer choice corresponds one-to-one to a raw form. This agrees with the failed GDT289--290 cross-host and compact-class transfer tests. The current executable model should therefore treat the exact host+renderer table as a high-capacity surface lexicon unless a future cross-host rule predicts unseen alternants.

## Claim ceiling

This is a parser-defined formal alias audit. It identifies no word, morpheme, code value, sound, language, meaning, plaintext, translation, or f84 evidence.
