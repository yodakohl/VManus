# GDT990: execution interrupted; necessary certificates recovered

The registered whole-Tabula fit did not complete. It ended with exit 143, before
individual solver outcomes were saved. The termination cause is unknown. No
complete writing witness is retained, but the lost outcomes cannot be counted
as contradictions, unknown solver returns, or evidence that no witness occurred.
The source, six meaning branches, four writers and original implementation remain
byte-identical to the public preregistration at commit `1735087bb`.

The separate [interruption recovery](INTERRUPTION_NOTE.md) makes no solver calls.
It reconstructs the complete candidate inventory and deterministic necessary
conditions, then checks them with the original independent implementation.

| Consequence | Cases |
|---|---:|
| Source transcription ineligible under the fixed rule | 19,080 |
| Too few characters for nonempty roots | 7,524 |
| Too few characters for distinct roots | 3,696 |
| More whole-word boundaries than source forms | 96 |
| Full equation unresolved; individual run outcome unretained | 1,980 |
| Total | 32,376 |

These are 24 cases for each of 1,349 paragraphs: 659 ZL3b and 690 IT2a; RF1b
has no complete-paragraph capacity in the fixed packet. The unchanged eligibility
flag admits 31 ZL3b and 523 IT2a paragraphs. The 11,316 necessary contradictions
are certified; they do not close the remaining equations. The three reported
progress checkpoints were 32, 64 and 96 completed jobs, each with only its latest
job labelled UNKNOWN_SOLVER. They do not identify the completed cases or all
statuses between checkpoints.

Every candidate's source branch, writer, paragraph, physical leaf, form count,
word count, observed consequence and independent confirmation capacity appears in
[INTERRUPTED_CANDIDATES.tsv](artifacts/INTERRUPTED_CANDIDATES.tsv). Exact necessary
certificates are in [INTERRUPTED_CASES.json.gz](artifacts/INTERRUPTED_CASES.json.gz).
The full prediction for a row is its variant's 21 content trees and named compiled
stream in [SOURCE.json](src/SOURCE.json), under the unchanged [METHOD](METHOD.md).
[INTERRUPTION_RESULT.json](artifacts/INTERRUPTION_RESULT.json) retains the complete
edition/branch/writer breakdown and explicitly separates unknown original outcomes
from the zero retained witnesses. [Recovery validation](artifacts/INTERRUPTION_VALIDATION.json)
is PASS for these reconstructed certificates and table coverage only; it does not
validate a completed solver run.

All six source branches and all four writer orders remain unresolved at full-code
level. Necessary length certificates do not distinguish writer orders; source
branches with equal root multiplicities have the same length predictions. Even a
future complete forward code would not by itself prove unique inverse decoding,
reference assignments, the source reading, or a manuscript word meaning. All
whole-paragraph target data were previously exposed; alternate transcriptions are
readings of the same manuscript. Independent meaning-confirmation capacity is
zero. No reserve, f84/f84r, f116v, or new image was opened; no significance or
confirmed translated word is claimed.

Decision: park the full equation search as incomplete, retaining all 1,980
unresolved cases. No automatic longer retry, decoder repair, source substitution,
or result-dependent frame change follows. A subsequent experiment requires a
separate substantive decision and registration; the original failure to retain
individual outcomes stays in this record.

Reproduce deterministic recovery only:

```
python experiments/yolo/gdt990_smaragdina_complete_role_frames/src/recover_interruption.py
```
