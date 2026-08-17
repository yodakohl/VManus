# GDT194 — consonantal homophony does not rescue PAGE_HOST

Status: **CONSONANTAL_HOMOPHONY_FALSIFIED**.

Allowing multiple PAGE_HOST signs to share a target consonant improves the best
GDT193 gap by 2,870.3 bits. The
best pack is `old_italian_tuscan`, using 17
distinct consonants for 20 source signs, but it still loses
**85,247.3 bits** to matched KT
(1.420 bits/event). The reverse ambiguity is paid
and the three retained mappings are not identical.

| pack | best gap (bits) | distinct consonants | stable |
|---|---:|---:|---|
| `latin` | 95,345.8 | 15 | no |
| `middle_high_german` | 97,013.6 | 18 | no |
| `middle_french` | 99,941.3 | 17 | no |
| `old_italian_tuscan` | 85,247.3 | 17 | no |
| `medieval_czech` | 91,476.1 | 18 | no |
| `old_hungarian` | 88,264.0 | 20 | no |

Fixed consonantal homophony is therefore another insufficient substrate. The
vowel-omission direction survives only as an architectural hint; it supplies no
consonant values or language identification.

No sign, sound, word, language, plaintext, meaning, or translation is
established. Every f84 row was rejected before parsing or scoring.
