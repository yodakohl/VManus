# GDT191 — context-keyed PAGE_HOST dictionaries do not rescue language

Status: **CONTEXT_KEYED_WORD_NOMENCLATOR_FALSIFIED**.

The global K=8 PAGE_HOST nomenclator was expanded into five fixed key scopes:
global, Currier, section, hand, and physical folio. Every stratum selected its
own top eight hosts (or fewer when necessary), paid its complete permutation
key, and was compared with an independently integrated source-identity KT
channel on the same mapped events.

The most flexible physical-folio model is also the closest result: `middle_high_german`
on 93 strata and 6333 mapped events, but it
still loses **240.070 bits**
(0.0379 bits/event), and the complete decoder is
not stable across three starts.

| key scope | best language | events | gap (bits) | gap/event | stable |
|---|---|---:|---:|---:|---|
| GLOBAL | `middle_high_german` | 5108 | 880.255 | 0.1723 | no |
| CURRIER | `middle_high_german` | 5337 | 875.380 | 0.1640 | no |
| SECTION | `middle_high_german` | 5524 | 774.687 | 0.1402 | no |
| HAND | `middle_high_german` | 5444 | 849.725 | 0.1561 | no |
| PHYSICAL_FOLIO | `middle_high_german` | 6333 | 240.070 | 0.0379 | no |

Context-specific dictionaries reduce the global mismatch, especially at folio
scale, but not enough to pay for themselves or identify one decoder. The fixed
frequent-host nomenclator therefore fails even when its key is allowed to vary
by known manuscript context. Remaining natural-language routes require
nonbijective/context-dependent expansion, phrase-level units, or an external
key—not another unpenalized page dictionary.

No target word is a reading; no language, sound, plaintext, meaning, or
translation is established. Every f84 row was rejected before parsing,
retention, joining, or scoring.
