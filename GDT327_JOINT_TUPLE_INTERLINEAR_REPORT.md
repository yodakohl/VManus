# GDT327 — executable joint-tuple interlinear

Status: **EXECUTABLE_JOINT_TUPLE_INTERLINEAR**.

The f84-free interlinear contains 8,448 physical source groups and 1,676 opaque joint tuples on 91 folios. The calibrated 126-cell lexicon covers 5,607 events (66.4%); 2,841 events remain explicitly `UNLICENSED_OR_UNKNOWN`.

```text
PAGE -> RECORD+ -> PHYSICAL_LINE+ -> FIELD+ -> GROUP+
GROUP -> JOINT_TUPLE(PAGE_HOST, FRAME, INNER_D, RIGHT, DY, B3)
      -> WRAPPER via exact-cell counts + s@LINE_START + q@PREV_DY
```

GDT325 prevents coordinate fallback on sparse cells. GDT326 prevents treating PAGE_HOST as an independently recombining payload. The emitted unit is therefore the joint tuple, with semantic and translation states left unassigned.

## Translation interface

Future grounding must align whole fields or records to external evidence and may then attach hypotheses to stable joint-tuple sequences. The interlinear itself does not attach a gloss to any tuple.

## Claim ceiling

Formal joint-tuple interlinear only; no word morpheme POS sound language meaning plaintext or translation. No f84 row was opened, parsed, retained, joined, or scored.
