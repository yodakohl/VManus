# GDT813 — concrete f17r content-word transfer

Status: `C0_CONTENT_ROLE_PRIORITY_NO_TRANSLATION`.

Start with [the working theory](WORKING_THEORY.md) and [report](REPORT.md).
Two fixed five-word readings differ at okaiin: Pulver? or ist?. The standalone
f88v inscription favours investigating an independently meaningful term over
a pure copula, but establishes neither powder nor root. All other words and
the inherited four-whole scalar family keep their declared trial meanings.

54 complete selected loci / 324 literal alternate-reader/model displays;
the whole f17r page is included. No new page or dictionary admission.

Reproduce:

```sh
python3 experiments/yolo/gdt813_f17_content_word_transfer/src/run.py --check
python3 experiments/yolo/gdt813_f17_content_word_transfer/src/validate.py --check
./vmanus-exp check-edge-packet experiments/yolo/gdt813_f17_content_word_transfer/src/LABEL_CONTEXT_PACKET.tsv
```

The last command is expected to return an ineligible exploratory packet,
not a score-ready visual relation. See METHOD.md and PREREGISTRATION.md for
scope, observation timing and the difference between source checks and meaning.
