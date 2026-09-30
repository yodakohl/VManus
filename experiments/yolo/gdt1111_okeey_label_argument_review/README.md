# GDT1111 — okeey label argument review

Decision: `NO_LABEL_OWNER_OR_WRITTEN_MEANING_DISCRIMINATOR`.

See [the report](REPORT.md), [all candidate occurrences](artifacts/CANDIDATE_TABLE.tsv)
and [the complete conditional reader](artifacts/FULL_READER.md).
This is exposed exploration, not a prospective or independent meaning test.

Reproduce with `python3 experiments/yolo/gdt1111_okeey_label_argument_review/src/run.py`
then `python3 experiments/yolo/gdt1111_okeey_label_argument_review/src/validate.py`.
The validator needs the GDT852 official Yale f75v image at its existing ignored
runtime path; its public URL and required hash are in GDT852 artifacts/SOURCES.json.
`prepare.py` reproduces the packet using the existing guarded admission-bound cache.
