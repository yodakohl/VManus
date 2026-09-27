# GDT1055 — exact running-text repeats across leaves

## Decision

The complete raw census finds two three-group sequences recurring at the same
physical loci in all three alternate transcriptions: `daiin chey lchedy`
(`f76r.42` → `f83r.3`) and `qol chedy qokeey` (`f81r.20` → `f82r.21`).
This is a positive **text-identity** result. It supplies inspectable repeated
constructions, but neither phrase has an independently bound image owner or
meaning. No translated word follows. The two examples were seen before this
registration; all counts below are a post-discovery descriptive audit, without
a significance claim.

## Complete result

Windows contain 3–6 exact raw groups separated by definite spaces on one P
line, and each pair lies on different physical leaves. An offset is one-based
within that transcription's line. `all` means the same raw triple and exact
locus/offset pair occurs in ZL3b, IT2a and RF1b. These are alternate readings
of **one** manuscript, not three confirmations.

| Reading | Raw groups | First locus, offset | Second locus, offset | All |
| --- | --- | --- | --- | --- |
| IT2a | `chey qol chedy` | f81v.25, 7 | f82r.21, 6 | no |
| IT2a | `daiin chey lchedy` | f76r.42, 4 | f83r.3, 5 | yes |
| IT2a | `ol sheedy qokeey` | f75r.5, 8 | f81r.12, 3 | no |
| IT2a | `qol chedy qokeey` | f81r.20, 2 | f82r.21, 7 | yes |
| IT2a | `shedy qokar shedy` | f75r.32, 7 | f76r.29, 3 | no |
| RF1b | `daiin chey lchedy` | f76r.42, 4 | f83r.3, 5 | yes |
| RF1b | `ol s aiin` | f55v.10, 2 | f82r.16, 7 | no |
| RF1b | `qol chedy qokeey` | f81r.20, 2 | f82r.21, 7 | yes |
| RF1b | `shedy qokar she@152;y` | f75r.32, 7 | f76r.29, 3 | no |
| ZL3b | `daiin chey lchedy` | f76r.42, 4 | f83r.3, 5 | yes |
| ZL3b | `qol chedy qokeey` | f81r.20, 2 | f82r.21, 7 | yes |
| ZL3b | `sar shedy qol` | f81r.25, 1 | f82r.6, 1 | no |
| ZL3b | `shedy qokain dar` | f75r.32, 3 | f76r.29, 5 | no |

There are 4 ZL3b, 5 IT2a and 4 RF1b cross-leaf pairs of length three;
none of length four, five or six. The respective eligible within-line
window counts for n=3/4/5/6 are ZL3b 2936/2236/1662/1202,
IT2a 3367/2737/2172/1681, and RF1b 3229/2580/2009/1517.
The machine-readable result retains every hit and the complete lines at the
two all-reader pairs.

The first pair spans an unillustrated f76r text line and f83r upper-spray
paragraph. The second spans f81r lower-pool and f82r bottom-communal
paragraphs under the prior GDT791 line-owner atlas. These broad visual
contexts do not assign any word to a particular object. The pairings might
reflect repeated discourse or formulae, ordinary common words, or copying;
this census cannot distinguish those explanations. GDT875's failed
local-label bridge is a different test and is not rescued by running-text
repetition.

## Validation and next decision

`src/validate.py` independently reconstructs the raw windows and checks the
complete reported inventory; it returned PASS. Source hash, rules and the
post-selection disclosure are in `METHOD.md` and `PREREGISTRATION.md`.
Retain both triples as exact repeat constraints in any whole-reading proposal.
Further recurrence scans of this roster alone will not give their meaning;
a later test needs a source-bound content or image relation that predicts a
different consequence for competing interpretations. f84/f84r and reserves
remain closed.
